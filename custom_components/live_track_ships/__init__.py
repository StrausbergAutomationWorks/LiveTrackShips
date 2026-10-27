"""Live Track Ships — AIS vessel tracking for Home Assistant.

Part of Live Track: ships, aircraft and trains on one map.

⚠ NOT A NAVIGATION PRODUCT. Positions may be animated between two OBSERVED
fixes by a consumer, which costs display lag. That trade is only legitimate
because nobody is navigating by it. See 10_SEED/05_SHARED_LESSONS.md D3c.

⚠ THIS IS NOT A DataUpdateCoordinator. The primary source is a WEBSOCKET PUSH,
and that class is built around "call this function every N seconds". A
long-lived task owns the connection and pushes into the store.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_FINAL_WRITE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const_flow import (
    CONF_API_KEY, CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_INSTANCE_MAX,
    CONF_LATITUDE, INSTANCE_MAX_VESSELS, MIN_INSTANCE_MAX_VESSELS,
    CONF_LONGITUDE, CONF_MAX_VESSELS, CONF_RADIUS_KM, CONF_SOURCE,
    DEFAULT_MAX_VESSELS, DOMAIN, NOTIFY_WINDOW_S, PLATFORMS,
    SOURCE_BARENTSWATCH, SOURCE_DIGITRAFFIC,
)
from .const_flow import attribution_for
from .geo import DEFAULT_RADIUS_KM, bounding_boxes
from . import held as _held
from .sources import statics as _statics
from .quota import effective_ceiling
from .store import DEFAULT_PRUNE_INTERVAL_S, VesselStore
from .shared_map_card import async_offer_map_card, async_withdraw_map_card

_LOGGER = logging.getLogger(__name__)

HERE = Path(__file__).parent

def instance_ceiling(hass) -> int:
    """INSTANCE_MAX_VESSELS as lowered by the users' sliders (item 264): the
    lowest setting on any enabled Ships entry. Cheap enough to read per pass."""
    return effective_ceiling(
        (e.options.get(CONF_INSTANCE_MAX)
         for e in hass.config_entries.async_entries(DOMAIN)
         if e.disabled_by is None),
        INSTANCE_MAX_VESSELS, MIN_INSTANCE_MAX_VESSELS)


# ⚠ NOT under hass.data[DOMAIN], which maps entry ids to feeds.
STATICS_KEY = f"{DOMAIN}_statics"


class StaticsHolder:
    """The one vessel-statics cache for this Home Assistant (SSOT item 262):
    loaded once, shared by every aisstream entry, flushed to SQLite by each
    entry's prune pass, at unload, and at shutdown."""

    def __init__(self, hass):
        self.hass = hass
        self.path = hass.config.path(".storage", _statics.FILE_NAME)
        self.cache = _statics.StaticCache()
        self._loaded: asyncio.Future | None = None
        self._lock = asyncio.Lock()
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_FINAL_WRITE,
                                   self._final_write)

    async def async_load(self):
        if self._loaded is None:
            self._loaded = self.hass.loop.create_future()
            try:
                rows = await self.hass.async_add_executor_job(
                    _statics.load, self.path)
                taken = self.cache.load_rows(rows)
                _LOGGER.debug("Vessel statics: %d read back from disk", taken)
            except Exception as exc:                   # noqa: BLE001
                # ⚠ Never block setup on the cache: start empty.
                _LOGGER.warning("Vessel statics not read back: %s", exc)
            finally:
                self._loaded.set_result(True)
        await self._loaded

    async def async_flush(self):
        """Evict, then write what changed. A failed write is logged and its
        rows kept for the next flush - statics never stop positions."""
        async with self._lock:
            deleted = self.cache.evict()
            rows = self.cache.take_dirty()
            if not rows and not deleted:
                return
            try:
                await self.hass.async_add_executor_job(
                    _statics.save, self.path, rows, deleted)
            except Exception as exc:                   # noqa: BLE001
                self.cache.mark_dirty(r[0] for r in rows)
                _LOGGER.warning("Vessel statics not saved: %s", exc)
                return
            _LOGGER.debug("Vessel statics: %d written, %d dropped, %d held",
                          len(rows), len(deleted), len(self.cache))

    async def _final_write(self, _event):
        await self.async_flush()


# ⚠ NOT under hass.data[DOMAIN], which maps entry ids to feeds.
HELD_KEY = f"{DOMAIN}_held"


class HeldHolder:
    """The saved held angles (SSOT item 270, Lee 2026-09-29): read into
    held.HELD once per Home Assistant, before any entity is made, and written
    as a diff by every entry's prune pass, at unload and at shutdown. Every
    source: a vessel with no heading can come from any of them."""

    def __init__(self, hass):
        self.hass = hass
        self.path = hass.config.path(".storage", _held.FILE_NAME)
        self._loaded: asyncio.Future | None = None
        self._lock = asyncio.Lock()
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_FINAL_WRITE,
                                   self._final_write)

    async def async_load(self):
        if self._loaded is None:
            self._loaded = self.hass.loop.create_future()
            try:
                rows = await self.hass.async_add_executor_job(
                    _held.load, self.path)
                taken = _held.HELD.load_rows(rows)
                _LOGGER.debug("Held angles: %d of %d read back", taken,
                              len(rows))
            except Exception as exc:                   # noqa: BLE001
                # ⚠ Never block setup on a convenience: start empty.
                _LOGGER.warning("Held angles not read back: %s", exc)
            finally:
                self._loaded.set_result(True)
        await self._loaded

    async def async_flush(self):
        """Write what changed. A failed write is logged; the next flush
        computes the diff again, so nothing is lost but time."""
        async with self._lock:
            upserts, deletes = _held.HELD.changes()
            if not upserts and not deletes:
                return
            try:
                await self.hass.async_add_executor_job(
                    _held.save, self.path, upserts, deletes)
            except Exception as exc:                   # noqa: BLE001
                _LOGGER.warning("Held angles not saved: %s", exc)
                return
            _held.HELD.committed(upserts, deletes)
            _LOGGER.debug("Held angles: %d written, %d dropped",
                          len(upserts), len(deletes))

    async def _final_write(self, _event):
        await self.async_flush()


async def _held_holder(hass) -> HeldHolder:
    holder = hass.data.get(HELD_KEY)
    if holder is None:
        holder = hass.data[HELD_KEY] = HeldHolder(hass)
    await holder.async_load()
    return holder


async def _statics_holder(hass) -> StaticsHolder:
    holder = hass.data.get(STATICS_KEY)
    if holder is None:
        holder = hass.data[STATICS_KEY] = StaticsHolder(hass)
    await holder.async_load()
    return holder


class ShipFeed:
    """Owns the source task and the store."""

    def __init__(self, hass, entry):
        self.hass = hass
        self.entry = entry
        cfg = {**entry.data, **entry.options}
        self.lat = cfg[CONF_LATITUDE]
        self.lon = cfg[CONF_LONGITUDE]
        self.radius = cfg.get(CONF_RADIUS_KM, DEFAULT_RADIUS_KM)
        self.store = VesselStore(
            self.lat, self.lon, self.radius,
            cfg.get(CONF_MAX_VESSELS, DEFAULT_MAX_VESSELS))
        self._cfg = cfg
        # Credit line for everything this entry shows (const_flow.ATTRIBUTION).
        self.attribution = attribution_for(cfg.get(CONF_SOURCE))
        self._task: asyncio.Task | None = None
        self._prune: asyncio.Task | None = None
        self._source = None
        self._statics: StaticsHolder | None = None   # aisstream only
        self._held: HeldHolder | None = None
        self._listeners: list = []
        self.held_by_instance_cap = 0   # set by geo_location._sync (item 246)
        # ⛔ Item 246: at most one listener pass per window. Instance
        # attribute so a test can shorten it.
        self.notify_window_s = NOTIFY_WINDOW_S
        self._pending: asyncio.TimerHandle | None = None
        self.passes = 0                 # listener passes run; for tests

    def add_listener(self, cb):
        self._listeners.append(cb)
        return lambda: self._listeners.remove(cb)

    def _notify(self):
        """⛔ COALESCED (item 246). The first change after a pass schedules one
        pass `notify_window_s` later; later changes fold into it. This used to
        run every listener on every message, and each run wrote state for
        every vessel the entry showed.

        ⚠ EVERY caller goes through here, the prune loop included, so
        departures, expiries, the instance ceiling and ownership handoff all
        still happen - at most one window late."""
        if self._pending is not None:
            return
        self._pending = self.hass.loop.call_later(
            self.notify_window_s, self._flush)

    def _flush(self):
        self._pending = None
        self.passes += 1
        for cb in list(self._listeners):
            # ⚠ One listener raising must not starve the others. Before the
            # window this propagated into _run and killed the feed.
            try:
                cb()
            except Exception:                      # noqa: BLE001
                _LOGGER.exception("Live Track Ships listener failed")

    def _build_source(self):
        session = async_get_clientsession(self.hass)
        if self._cfg[CONF_SOURCE] == SOURCE_DIGITRAFFIC:
            from .sources.digitraffic import DigitrafficSource
            return DigitrafficSource(session, self.lat, self.lon, self.radius)
        if self._cfg[CONF_SOURCE] == SOURCE_BARENTSWATCH:
            from .sources.barentswatch import BarentsWatchSource
            # ⚠ Sends the CIRCLE as a GeoJSON polygon - the only source that
            # can take the shape the user actually asked for, rather than a
            # circumscribing box filtered again locally.
            return BarentsWatchSource(
                session, self._cfg[CONF_CLIENT_ID],
                self._cfg[CONF_CLIENT_SECRET],
                self.lat, self.lon, self.radius)
        from .sources.aisstream import AisStreamSource
        # ⚠ The service takes BOXES; the user asked for a CIRCLE. We request
        # the circumscribing box and the store enforces the circle - a corner
        # is 1.41x the radius out.
        return AisStreamSource(session, self._cfg[CONF_API_KEY],
                               bounding_boxes(self.lat, self.lon, self.radius),
                               statics=(self._statics.cache
                                        if self._statics else None))

    async def start(self):
        # ⚠ Only aisstream learns statics from the air. BarentsWatch sends
        # them with every position and Digitraffic's server keeps them, so a
        # restart costs those two nothing (SSOT item 262, read 2026-09-26).
        if self._cfg[CONF_SOURCE] not in (SOURCE_DIGITRAFFIC,
                                          SOURCE_BARENTSWATCH):
            self._statics = await _statics_holder(self.hass)
        # Before the platforms make any entity (item 270).
        self._held = await _held_holder(self.hass)
        self._source = self._build_source()
        self._task = self.entry.async_create_background_task(
            self.hass, self._run(), f"{DOMAIN}_feed")
        self._prune = self.entry.async_create_background_task(
            self.hass, self._prune_loop(), f"{DOMAIN}_prune")

    async def _run(self):
        try:
            async for obs in self._source.observations():
                if self.store.add(obs):
                    self._notify()
        except asyncio.CancelledError:
            raise
        except Exception:                          # noqa: BLE001
            _LOGGER.exception("Live Track Ships feed stopped unexpectedly")

    async def _prune_loop(self):
        """⚠ Eviction is by RETENTION WINDOW, never by total count. The union
        of distinct vessels does NOT converge - 30-37 new per day, still
        climbing at 291 after five days."""
        while True:
            await asyncio.sleep(DEFAULT_PRUNE_INTERVAL_S)
            if self.store.prune():
                self._notify()
            if self._statics is not None:
                await self._statics.async_flush()
            if self._held is not None:
                await self._held.async_flush()

    async def stop(self):
        """⚠ TEAR DOWN CLEANLY. Only THREE connections exist per account and
        per originating IP, applied before authentication. A reload that leaks
        one burns a third of the budget until Home Assistant restarts."""
        for task in (self._task, self._prune):
            if task is not None:
                task.cancel()
        # A pass scheduled after the platforms unloaded has nothing to run.
        if self._pending is not None:
            self._pending.cancel()
            self._pending = None
        if self._source is not None:
            await self._source.close()
        # What this entry learned since the last prune pass (item 262).
        if self._statics is not None:
            await self._statics.async_flush()
        if self._held is not None:
            await self._held.async_flush()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # The vessel icons (SSOT item 254). Registered once per HA run.
    from .web import register as register_views
    register_views(hass)
    # LiveTrackMapCard, shipped in frontend/: served once per run, offered, and
    # the one dashboard resource row reconciled (backlog 291). Never raises.
    await async_offer_map_card(hass, DOMAIN, HERE / "frontend")
    feed = ShipFeed(hass, entry)
    await feed.start()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = feed
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_reload))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload one area. The map card is NOT withdrawn here: every restart
    and reload unloads, and that is not an uninstall (card SSOT 67.6);
    async_remove_entry does it."""
    unloaded = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS)
    feed = hass.data[DOMAIN].pop(entry.entry_id, None)
    if feed is not None:
        await feed.stop()
    return unloaded


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """An area was deleted. The domain's LAST one withdraws the map card."""
    if not [e for e in hass.config_entries.async_entries(DOMAIN)
            if e.entry_id != entry.entry_id]:
        await async_withdraw_map_card(hass, DOMAIN)


async def _reload(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """⚠ Options are applied by RELOADING, not by re-subscribing in place.
    aisstream caps subscription updates at one per second and a faster one
    closes the connection."""
    await hass.config_entries.async_reload(entry.entry_id)
