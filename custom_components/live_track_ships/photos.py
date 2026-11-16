"""A photo of the vessel, and a link out to it (backlog 346; 06_MAP_CONTRACT.md D4g).

DECIDED by Lee 2026-11-16 01:1x-01:2x CST: photos from Wikidata now (ShipSpotting thumbnails later, preferred
where both exist, if ShipSpotting agrees: a request was sent the same night); the photo in the map's hover box
and, with the link, in a popup on click; the link to VesselFinder.

HOW (measured 2026-11-16 00:5x-01:3x from the PC, bin\\lts346_probe.py):
  * Wikidata's QUERY SERVICE answered 429 "Aggressively rate-limiting to 1 req / min" (an outage rule), so it is
    NOT used. The Action API is: `list=search` with `haswbstatement:P458=<imo>|P458=<imo>...` finds several ships
    in one request (0.6 s); `wbgetentities` gives their IMO (P458) and image (P18), 50 a request.
  * Of 521 IMO numbers on the box's map, 322 matched a Wikidata item and 49 of those carry an image. So most
    vessels get the link and no photo; that is expected, not a fault.
  * Commons `imageinfo` gives a 320 px thumbnail, the file's page, the author (HTML: stripped here) and the
    licence (CC BY-SA 4.0, Public domain, ...), ten files in one request (0.27 s).
  * VesselFinder's page is https://www.vesselfinder.com/vessels/details/<number>: an IMO opened EMMA MAERSK, and
    so did her MMSI (measured both). A link only: nothing is fetched from VesselFinder.

⚠ Each install looks up the vessels on ITS OWN map, for its own user; nothing passes through SAW.
⚠ Wikimedia asks every client for a User-Agent naming it and a way to reach its maintainer: USER_AGENT.
⚠ The cache is SAW-neutral (`.storage/saw_vessel_photos.json`), keyed by IMO: a photo found stays 30 days, a
  ship with none is asked again after 14.
"""

from __future__ import annotations

import asyncio
import html
import json
import logging
import re
import time

_LOGGER = logging.getLogger(__name__)

STORE_KEY = "saw_vessel_photos"
CACHE_NAME = "saw_vessel_photos.json"
USER_AGENT = ("StrausbergAutomationWorks-LiveTrackShips/0.1 "
              "(https://github.com/StrausbergAutomationWorks; Home Assistant integration)")
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
FOUND_TTL_S = 30 * 86400
NONE_TTL_S = 14 * 86400
BATCH = 20                 # IMO numbers per search request
PAUSE_S = 10.0             # between batches: at most 6 lookups a minute per install
THUMB_PX = 320
CREDIT_MAX = 120
CACHE_MAX = 20000

VESSELFINDER = "https://www.vesselfinder.com/vessels/details/{}"


# -- pure helpers (tested without Home Assistant) ---------------------------------------------------------------
def vessel_links(imo: str | None, mmsi: str | None) -> list:
    """The link out (D4g `marker_links`): VesselFinder by IMO, else by MMSI. Empty when there is neither."""
    number = imo or mmsi
    if not number or not str(number).isdigit():
        return []
    return [{"label": "VesselFinder", "url": VESSELFINDER.format(number)}]


def search_query(imos) -> str:
    return "haswbstatement:" + "|".join(f"P458={i}" for i in imos)


def files_by_imo(entities: dict, wanted) -> dict:
    """wbgetentities' entities -> {imo: Commons file name}, only for an item whose own IMO is one we asked for
    (the search matches on a statement, but the item is read back to be sure)."""
    wanted = set(wanted)
    out = {}
    for ent in (entities or {}).values():
        claims = ent.get("claims") or {}
        imos = {str(c.get("mainsnak", {}).get("datavalue", {}).get("value", "")) for c in claims.get("P458", [])}
        files = [c.get("mainsnak", {}).get("datavalue", {}).get("value") for c in claims.get("P18", [])
                 if c.get("rank") != "deprecated"]
        files = [f for f in files if isinstance(f, str) and f]
        for imo in imos & wanted:
            if files and imo not in out:
                out[imo] = files[0]
    return out


_TAG = re.compile(r"<[^>]+>")


def plain(value, limit=CREDIT_MAX) -> str:
    """Commons' Artist is HTML (a user link, sometimes a whole table): text only, one line, cut."""
    text = html.unescape(_TAG.sub(" ", str(value or "")))
    text = " ".join(text.split())
    return text[:limit].rstrip()


def _https(url) -> str | None:
    if not isinstance(url, str) or not url:
        return None
    if url.startswith("//"):
        url = "https:" + url
    if url.startswith("http://"):
        url = "https://" + url[7:]
    return url if url.startswith("https://") else None


def photo_from_imageinfo(page: dict) -> dict | None:
    """One Commons page with imageinfo -> D4g `marker_photo`, or None when it lacks a thumbnail or a page."""
    info = (page.get("imageinfo") or [{}])[0]
    meta = info.get("extmetadata") or {}
    thumb = _https(info.get("thumburl"))
    link = _https(info.get("descriptionurl"))
    if not thumb or not link:
        return None
    thumb = thumb.split("?", 1)[0]          # Commons appends utm_* tracking parameters
    credit = plain(meta.get("Artist", {}).get("value")) or plain(meta.get("Credit", {}).get("value"))
    photo = {
        "url": thumb,
        "page": link,
        "credit": credit or "Wikimedia Commons contributor",
        "licence": plain(meta.get("LicenseShortName", {}).get("value"), 60) or "see the photo's page",
        "source": "Wikimedia Commons",
    }
    lic = _https(meta.get("LicenseUrl", {}).get("value"))
    if lic:
        photo["licence_url"] = lic
    for key in ("thumbwidth", "thumbheight"):
        if isinstance(info.get(key), int):
            photo["width" if key == "thumbwidth" else "height"] = info[key]
    return photo


# -- the shared book: cache, queue, worker --------------------------------------------------------------------
class PhotoBook:
    """One per Home Assistant: every Ships entry asks it; it asks Wikidata at most once a PAUSE_S."""

    def __init__(self, path: str, clock=time.time):
        self.path = path
        self._clock = clock
        self._cache: dict[str, dict] = {}        # imo -> {"t": epoch, "photo": dict|None}
        self._queue: list[str] = []
        self._queued: set[str] = set()
        self._waiters: dict[str, set] = {}
        self._dirty = False
        self._task = None
        self.lookups = 0

    # disk
    def load(self) -> None:
        try:
            with open(self.path, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                self._cache = {k: v for k, v in data.items() if isinstance(v, dict) and "t" in v}
        except FileNotFoundError:
            pass
        except Exception as exc:                      # noqa: BLE001 - a bad cache is started over, never fatal
            _LOGGER.warning("Vessel photo cache not read, starting empty: %s", exc)

    def save(self) -> None:
        if not self._dirty:
            return
        if len(self._cache) > CACHE_MAX:
            for imo, _ in sorted(self._cache.items(), key=lambda kv: kv[1]["t"])[:len(self._cache) - CACHE_MAX]:
                del self._cache[imo]
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._cache, f, ensure_ascii=False, separators=(",", ":"))
        import os
        os.replace(tmp, self.path)
        self._dirty = False

    # asking
    def photo(self, imo: str | None, waiter=None) -> dict | None:
        """The photo known for this IMO, or None. An unknown or stale one is queued; `waiter` is called once
        when its answer arrives (the entity writes its state then)."""
        if not imo:
            return None
        rec = self._cache.get(imo)
        now = self._clock()
        fresh = rec is not None and now - rec["t"] < (FOUND_TTL_S if rec.get("photo") else NONE_TTL_S)
        if not fresh and imo not in self._queued:
            self._queue.append(imo)
            self._queued.add(imo)
        if not fresh and waiter is not None:
            self._waiters.setdefault(imo, set()).add(waiter)
        return rec.get("photo") if rec else None

    def forget_waiter(self, imo, waiter) -> None:
        s = self._waiters.get(imo)
        if s:
            s.discard(waiter)
            if not s:
                del self._waiters[imo]

    def take_batch(self) -> list:
        batch, self._queue = self._queue[:BATCH], self._queue[BATCH:]
        for imo in batch:
            self._queued.discard(imo)
        return batch

    def settle(self, asked, found: dict) -> list:
        """Record the answers for `asked` (found: imo -> photo). Returns the waiters to call."""
        now = self._clock()
        call = []
        for imo in asked:
            self._cache[imo] = {"t": now, "photo": found.get(imo)}
            call.extend(self._waiters.pop(imo, ()))
        self._dirty = True
        return call

    # the network
    async def lookup(self, session, imos) -> dict:
        """imo -> photo for those of `imos` Wikidata has a photo of. Raises on a network failure."""
        import aiohttp
        headers = {"User-Agent": USER_AGENT}
        timeout = aiohttp.ClientTimeout(total=30)
        params = {"action": "query", "list": "search", "srsearch": search_query(imos), "srlimit": 50,
                  "srprop": "", "format": "json"}
        async with session.get(WIKIDATA_API, params=params, headers=headers, timeout=timeout) as r:
            r.raise_for_status()
            hits = [h["title"] for h in (await r.json()).get("query", {}).get("search", [])]
        if not hits:
            return {}
        params = {"action": "wbgetentities", "ids": "|".join(hits[:50]), "props": "claims", "format": "json"}
        async with session.get(WIKIDATA_API, params=params, headers=headers, timeout=timeout) as r:
            r.raise_for_status()
            files = files_by_imo((await r.json()).get("entities"), imos)
        if not files:
            return {}
        titles = {f"File:{f}": imo for imo, f in files.items()}
        params = {"action": "query", "titles": "|".join(titles), "prop": "imageinfo",
                  "iiprop": "url|extmetadata", "iiurlwidth": THUMB_PX, "format": "json",
                  "iiextmetadatafilter": "Artist|Credit|LicenseShortName|LicenseUrl"}
        async with session.get(COMMONS_API, params=params, headers=headers, timeout=timeout) as r:
            r.raise_for_status()
            data = await r.json()
        # Commons normalises titles (underscores, capitals): map back through its own table.
        norm = {n["to"]: n["from"] for n in data.get("query", {}).get("normalized", [])}
        out = {}
        for page in data.get("query", {}).get("pages", {}).values():
            title = norm.get(page.get("title"), page.get("title"))
            imo = titles.get(title) or titles.get(page.get("title"))
            photo = photo_from_imageinfo(page) if imo else None
            if photo:
                out[imo] = photo
        return out

    async def run(self, hass, session) -> None:
        """The worker: one batch every PAUSE_S while there is anything to ask; saves after each answer."""
        while True:
            await asyncio.sleep(PAUSE_S)
            batch = self.take_batch()
            if not batch:
                continue
            try:
                found = await self.lookup(session, batch)
            except asyncio.CancelledError:
                raise
            except Exception as exc:                  # noqa: BLE001 - asked again later, never fatal
                _LOGGER.debug("Vessel photo lookup failed (%s); asked again later", exc)
                for imo in batch:
                    if imo not in self._queued:
                        self._queue.append(imo)
                        self._queued.add(imo)
                await asyncio.sleep(60)
                continue
            self.lookups += 1
            for cb in self.settle(batch, found):
                try:
                    cb()
                except Exception:                     # noqa: BLE001
                    _LOGGER.debug("photo waiter failed", exc_info=True)
            try:
                await hass.async_add_executor_job(self.save)
            except Exception as exc:                  # noqa: BLE001
                _LOGGER.warning("Vessel photo cache not saved: %s", exc)


async def shared(hass):
    """The instance's PhotoBook, started on first use: cache read, worker running for the rest of the run."""
    book = hass.data.get(STORE_KEY)
    if book is None:
        from homeassistant.helpers.aiohttp_client import async_get_clientsession
        book = hass.data[STORE_KEY] = PhotoBook(hass.config.path(".storage", CACHE_NAME))
        await hass.async_add_executor_job(book.load)
        book._task = hass.async_create_background_task(
            book.run(hass, async_get_clientsession(hass)), "saw_vessel_photos")
    return book
