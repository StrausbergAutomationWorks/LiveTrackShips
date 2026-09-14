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

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const_flow import (
    CONF_API_KEY, CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_LATITUDE,
    CONF_LONGITUDE, CONF_MAX_VESSELS, CONF_RADIUS_KM, CONF_SOURCE,
    DEFAULT_MAX_VESSELS, DOMAIN, PLATFORMS, SOURCE_BARENTSWATCH,
    SOURCE_DIGITRAFFIC,
)
from .geo import DEFAULT_RADIUS_KM, bounding_boxes
from .store import DEFAULT_PRUNE_INTERVAL_S, VesselStore

_LOGGER = logging.getLogger(__name__)


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
        self._task: asyncio.Task | None = None
        self._prune: asyncio.Task | None = None
        self._source = None
        self._listeners: list = []

    def add_listener(self, cb):
        self._listeners.append(cb)
        return lambda: self._listeners.remove(cb)

    def _notify(self):
        for cb in list(self._listeners):
            cb()

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
                               bounding_boxes(self.lat, self.lon, self.radius))

    async def start(self):
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

    async def stop(self):
        """⚠ TEAR DOWN CLEANLY. Only THREE connections exist per account and
        per originating IP, applied before authentication. A reload that leaks
        one burns a third of the budget until Home Assistant restarts."""
        for task in (self._task, self._prune):
            if task is not None:
                task.cancel()
        if self._source is not None:
            await self._source.close()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    feed = ShipFeed(hass, entry)
    await feed.start()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = feed
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_reload))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS)
    feed = hass.data[DOMAIN].pop(entry.entry_id, None)
    if feed is not None:
        await feed.stop()
    return unloaded


async def _reload(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """⚠ Options are applied by RELOADING, not by re-subscribing in place.
    aisstream caps subscription updates at one per second and a faster one
    closes the connection."""
    await hass.config_entries.async_reload(entry.entry_id)
