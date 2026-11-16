"""A short track behind each vessel, kept by Ships and fetched by the map card on click (backlog 348;
06_MAP_CONTRACT.md D4h `marker_track`).

DECIDED by Lee 2026-11-16 03:01-03:40 CST: Ships keeps the track and the card asks for it on click (not drawn
for every vessel, so a busy port is never swamped: the D6 complaint); 24 hours by default, changed with the
action `live_track_ships.set_track_hours` (1 to 168); watched vessels are click-only like the rest.

WHAT IS KEPT:
  * REAL FIXES ONLY - what a source reported, never an estimate or an interpolated frame (06_MAP_CONTRACT.md
    D3c-ii: a history of positions the object was never observed at is worse than none).
  * Thinned: a fix is kept when the vessel moved at least MIN_MOVE_M since the last kept fix, or MAX_QUIET_S
    passed; never two within MIN_GAP_S. A moored vessel's jitter then costs a point every ten minutes, and a
    local receiver's fix every 2-10 s cannot fill memory: at most 2,880 points a vessel a day.
  * Measured 2026-11-16 03:05 (bin\\lts348_rate.py, 5 min): vessels heard sent 3-5 new fixes an hour on average,
    36 at most; at this box's traffic a week is about half a million points.
  * The window: points older than `hours` are dropped; a vessel not heard for the whole window is dropped.

WHERE: in memory, one book per Home Assistant, shared by every Ships entry (a vessel two areas hear is one
track); saved to `.storage/saw_vessel_tracks.json` (SAW-neutral) every SAVE_INTERVAL_S and at Home Assistant's
final write, so a restart keeps the track. Served at GET /api/live_track_ships/track/<MMSI>, signed in only:
the card asks for one vessel when the viewer clicks it.
"""

from __future__ import annotations

import asyncio
import json
import logging
import math
import os
import re
import time

_LOGGER = logging.getLogger(__name__)

STORE_KEY = "saw_vessel_tracks"
CACHE_NAME = "saw_vessel_tracks.json"
URL_BASE = "/api/live_track_ships/track"
DEFAULT_HOURS = 24
MIN_HOURS = 1
MAX_HOURS = 168
MIN_MOVE_M = 25.0
MAX_QUIET_S = 600
MIN_GAP_S = 30
SAVE_INTERVAL_S = 300
FUTURE_SLACK_S = 300        # a fix stamped further ahead than this is a bad clock, not kept
_IDENTITY = re.compile(r"^\d{1,9}$")


def track_url(identity) -> str | None:
    """D4h `marker_track`: the address the card fetches, or None for an identity that is not an MMSI."""
    ident = str(identity or "")
    return f"{URL_BASE}/{ident}" if _IDENTITY.match(ident) else None


def distance_m(lat1, lon1, lat2, lon2) -> float:
    r = 6371008.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


def valid_hours(value) -> int:
    """1-168 whole hours, or ValueError."""
    if isinstance(value, bool):
        raise ValueError("hours must be a number")
    try:
        h = float(value)
    except (TypeError, ValueError):
        raise ValueError("hours must be a number") from None
    if h != int(h) or not MIN_HOURS <= h <= MAX_HOURS:
        raise ValueError(f"hours must be a whole number from {MIN_HOURS} to {MAX_HOURS}")
    return int(h)


class TrackBook:
    """identity -> [[epoch_s, lat, lon], ...], oldest first."""

    def __init__(self, path: str, clock=time.time):
        self.path = path
        self._clock = clock
        self.hours = DEFAULT_HOURS
        self._tracks: dict[str, list] = {}
        self._dirty = False
        self._task = None

    # -- adding ----------------------------------------------------------------------------------------------
    def add(self, identity, lat, lon, t) -> bool:
        """One reported fix. True when it was kept."""
        ident = str(identity or "")
        if not _IDENTITY.match(ident):
            return False
        try:
            lat, lon, t = float(lat), float(lon), float(t)
        except (TypeError, ValueError):
            return False
        if not (-90 <= lat <= 90 and -180 <= lon <= 180) or (lat == 0 and lon == 0):
            return False
        now = self._clock()
        if t > now + FUTURE_SLACK_S or t < now - self.hours * 3600:
            return False
        pts = self._tracks.get(ident)
        if pts:
            lt, llat, llon = pts[-1]
            gap = t - lt
            if gap < MIN_GAP_S:            # also drops a duplicate relay and an out-of-order fix
                return False
            if gap < MAX_QUIET_S and distance_m(llat, llon, lat, lon) < MIN_MOVE_M:
                return False
        else:
            pts = self._tracks[ident] = []
        pts.append([int(t), round(lat, 5), round(lon, 5)])
        self._dirty = True
        return True

    def add_obs(self, obs) -> bool:
        """An Observation (saw_livetrack.ais): real fixes only."""
        if getattr(obs, "position_source", None) == "estimated":
            return False
        at = getattr(obs, "observed_at", None)
        if at is None:
            return False
        return self.add(obs.identity, obs.latitude, obs.longitude, at.timestamp())

    # -- reading ---------------------------------------------------------------------------------------------
    def points(self, identity) -> list:
        """[[lat, lon, epoch_s], ...] inside the window, oldest first (the order the card draws)."""
        horizon = self._clock() - self.hours * 3600
        return [[la, lo, t] for t, la, lo in self._tracks.get(str(identity), ()) if t >= horizon]

    def answer(self, identity) -> dict:
        return {"identity": str(identity), "hours": self.hours, "points": self.points(identity)}

    def counts(self) -> tuple[int, int]:
        return len(self._tracks), sum(len(p) for p in self._tracks.values())

    # -- the window ------------------------------------------------------------------------------------------
    def set_hours(self, value) -> int:
        self.hours = valid_hours(value)
        self.prune()
        self._dirty = True
        return self.hours

    def prune(self) -> int:
        """Drop points older than the window and vessels left with none. Returns points dropped."""
        horizon = self._clock() - self.hours * 3600
        dropped = 0
        for ident in list(self._tracks):
            pts = self._tracks[ident]
            keep = next((i for i, p in enumerate(pts) if p[0] >= horizon), len(pts))
            if keep:
                dropped += keep
                del pts[:keep]
            if not pts:
                del self._tracks[ident]
        if dropped:
            self._dirty = True
        return dropped

    # -- disk ------------------------------------------------------------------------------------------------
    def load(self) -> None:
        try:
            with open(self.path, encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            return
        except Exception as exc:                      # noqa: BLE001 - a bad file is started over, never fatal
            _LOGGER.warning("Vessel track file not read, starting empty: %s", exc)
            return
        try:
            self.hours = valid_hours(data.get("hours", DEFAULT_HOURS))
        except (ValueError, AttributeError):
            self.hours = DEFAULT_HOURS
        tracks = data.get("tracks") if isinstance(data, dict) else None
        for ident, pts in (tracks or {}).items():
            if not _IDENTITY.match(str(ident)) or not isinstance(pts, list):
                continue
            good = [p for p in pts if isinstance(p, list) and len(p) == 3
                    and all(isinstance(x, (int, float)) for x in p)]
            good.sort(key=lambda p: p[0])
            if good:
                self._tracks[str(ident)] = [[int(t), la, lo] for t, la, lo in good]
        self.prune()
        self._dirty = False

    def save(self) -> None:
        if not self._dirty:
            return
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"v": 1, "hours": self.hours, "tracks": self._tracks}, f, separators=(",", ":"))
        os.replace(tmp, self.path)
        self._dirty = False

    async def run(self, hass) -> None:
        """Prune and save every SAVE_INTERVAL_S."""
        while True:
            await asyncio.sleep(SAVE_INTERVAL_S)
            self.prune()
            try:
                await hass.async_add_executor_job(self.save)
            except Exception as exc:                  # noqa: BLE001
                _LOGGER.warning("Vessel track file not saved: %s", exc)


def _make_view(book):
    """The address, built here so the module imports without Home Assistant (tests)."""
    from aiohttp import web
    from homeassistant.components.http import HomeAssistantView

    class VesselTrackView(HomeAssistantView):
        """One vessel's track. Signed in only: the card asks with the viewer's own login."""

        url = URL_BASE + "/{identity}"
        name = "api:live_track_ships:track"
        requires_auth = True

        async def get(self, request: web.Request, identity: str) -> web.Response:
            if not _IDENTITY.match(identity):
                return self.json_message("not an MMSI", status_code=400)
            return self.json(book.answer(identity))

    return VesselTrackView()


async def shared(hass):
    """The instance's TrackBook, started on first use: file read, address registered, the save loop running,
    and a last save at Home Assistant's final write."""
    book = hass.data.get(STORE_KEY)
    if book is None:
        from homeassistant.const import EVENT_HOMEASSISTANT_FINAL_WRITE
        book = hass.data[STORE_KEY] = TrackBook(hass.config.path(".storage", CACHE_NAME))
        await hass.async_add_executor_job(book.load)
        hass.http.register_view(_make_view(book))
        book._task = hass.async_create_background_task(book.run(hass), "saw_vessel_tracks")

        async def _final(_event):
            book.prune()
            await hass.async_add_executor_job(book.save)

        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_FINAL_WRITE, _final)
    return book
