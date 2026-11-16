"""Sensor platform: how many vessels are on the map.

⚠ WHY THIS EXISTS. The map's control card carries a count for every other
source - "Aircraft in range", "UP-W trains running", "South Shore running" -
and a geo_location integration has no equivalent, because its entities are
transient and cannot be counted by a template that names them.

⚠ IT COUNTS WHAT IS PUBLISHED, NOT WHAT IS HELD. The store keeps vessels for a
retention window and caps what it publishes; the number a user sees on the map
is the published one. Reporting the held count would overstate the map.

⚠ AND IT SURFACES TRUNCATION. `05_SHARED_LESSONS.md` and the Ships SSOT both
record that a quietly clipped list looks exactly like missing coverage, so
`truncated_from` is an attribute here rather than a debug log line.
"""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity, SensorStateClass

from . import instance_ceiling
from .const_flow import CONF_SOURCE, DOMAIN, KIND_AREA, KIND_WATCH, SOURCE_LOCAL
from .geo_location import OWNERS_KEY

_LOGGER = logging.getLogger(__name__)

# Only the station sensor polls (the others push); 30 s is Home Assistant's own default.
SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(hass, entry, async_add_entities):
    feed = hass.data[DOMAIN][entry.entry_id]
    if getattr(feed, "kind", KIND_AREA) == KIND_WATCH:
        async_add_entities([WatchedVesselsSensor(entry, feed)])
    else:
        sensors = [VesselCountSensor(entry, feed)]
        # Your own receiver (backlog 344): how the station itself is doing.
        if getattr(feed, "_cfg", {}).get(CONF_SOURCE) == SOURCE_LOCAL:
            sensors.append(StationSensor(entry, feed))
        async_add_entities(sensors)


class StationSensor(SensorEntity):
    """Your own receiver (backlog 344, Lee 2026-11-15): messages per minute,
    and as attributes the vessels heard in the last ten minutes, the farthest
    one from the area's centre, the last message, and the port's state.

    ⚠ POLLED, every 30 s, unlike the others: a dead receiver sends nothing, so
    nothing would ever push a 0 and the rate would freeze at its last value."""

    _attr_should_poll = True
    _attr_icon = "mdi:radio-tower"
    # Change with nearly every poll; kept out of the recorder.
    _unrecorded_attributes = frozenset({"last_message", "farthest_mmsi",
                                        "invalid_sentences", "dropped_datagrams"})
    _attr_native_unit_of_measurement = "messages/min"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = False

    def __init__(self, entry, feed):
        self._feed = feed
        self._attr_unique_id = f"{DOMAIN}:{entry.entry_id}:station"
        self._attr_name = "AIS station"
        self._attr_attribution = feed.attribution

    def _source(self):
        return getattr(self._feed, "_source", None)

    @property
    def native_value(self):
        src = self._source()
        return None if src is None else src.stats.snapshot()["messages_per_minute"]

    @property
    def extra_state_attributes(self) -> dict:
        src = self._source()
        if src is None:
            return {}
        s = src.stats.snapshot()
        attrs = {
            "udp_port": src.port,
            "listening": src._transport is not None,
            "vessels_heard": s["vessels_heard"],
            "farthest_km": s["farthest_km"],
            "farthest_mmsi": s["farthest_mmsi"],
            "last_message": s["last_message"].isoformat() if s["last_message"] else None,
            "invalid_sentences": src.decoder.counts["invalid"],
        }
        if src.stats.dropped:
            attrs["dropped_datagrams"] = src.stats.dropped
        if src.bind_error:
            attrs["port_error"] = src.bind_error
        return attrs


class WatchedVesselsSensor(SensorEntity):
    """The watch entry (backlog 343): how many listed vessels are heard now,
    and every listed vessel's label and last known state as an attribute
    (at most MAX_WATCHED rows), for a dashboard card."""

    _attr_should_poll = False
    _attr_icon = "mdi:binoculars"
    # Up to 100 rows rewritten with every pass: kept out of the recorder.
    _unrecorded_attributes = frozenset({"vessels"})
    _attr_native_unit_of_measurement = "vessels"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = False

    def __init__(self, entry, feed):
        self._feed = feed
        self._attr_unique_id = f"{DOMAIN}:{entry.entry_id}:watched"
        self._attr_name = "Watched vessels"
        self._attr_attribution = feed.attribution

    async def async_added_to_hass(self):
        self.async_on_remove(self._feed.add_listener(self._changed))

    def _changed(self):
        if self.hass is not None:
            self.async_write_ha_state()

    @property
    def native_value(self) -> int:
        return len(self._feed.store.present())

    @property
    def extra_state_attributes(self) -> dict:
        events = getattr(self._feed, "events", None)
        rows = events.snapshot() if events is not None else [
            {"mmsi": m, **({"label": l} if l else {}), "heard": False}
            for m, l in self._feed.labels.items()]
        return {"listed": len(self._feed.labels), "vessels": rows}


class VesselCountSensor(SensorEntity):
    """Vessels currently shown on the map."""

    _attr_should_poll = False
    _attr_icon = "mdi:ferry"
    _attr_native_unit_of_measurement = "vessels"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = False

    def __init__(self, entry, feed):
        self._feed = feed
        self._entry_id = entry.entry_id
        # ⚠ Namespaced and tied to the config entry, so a second area gets its
        # own sensor rather than colliding.
        self._attr_unique_id = f"{DOMAIN}:{entry.entry_id}:vessel_count"
        self._attr_name = "Ships in range"
        self._attr_attribution = feed.attribution

    async def async_added_to_hass(self):
        self.async_on_remove(self._feed.add_listener(self._changed))

    def _changed(self):
        if self.hass is not None:
            self.async_write_ha_state()

    @property
    def native_value(self) -> int:
        # ⚠ published() MUST still be called here: it is what sets
        # store.truncated_from, which extra_state_attributes reads next
        # (SSOT item 14, the latent ordering dependency).
        published = self._feed.store.published()
        # ⚠ COUNT ONLY WHAT THIS ENTRY OWNS (Lee, 2026-09-23). Two entries
        # over the same water both hear a vessel; geo_location gives it to one
        # of them. Counting published() would put it on both integration
        # cards. Owners are keyed MMSI -> entry_id by geo_location._sync.
        owners = self.hass.data.get(OWNERS_KEY, {}) if self.hass else {}
        me = self._entry_id
        return sum(1 for o in published if owners.get(o.identity) == me)

    @property
    def extra_state_attributes(self) -> dict:
        store = self._feed.store
        attrs = {
            "tracked": len(store),
            "radius_km": self._feed.radius,
        }
        # ⚠ Only present when the cap actually bit. A quietly clipped list
        # looks like missing coverage - say so rather than hide it.
        if store.truncated_from:
            attrs["truncated_from"] = store.truncated_from
            # ⚠ When truncated, published() returned exactly the cap. Do not
            # call it a second time to count it: measured 57 ms median on
            # 3,000 tracks in the HA container, and native_value already
            # called it once this write (item 246).
            attrs["showing_nearest"] = store.max_vessels
        # ⛔ Item 246: new vessels this entry could not add because the map
        # already holds INSTANCE_MAX_VESSELS across every entry.
        held = getattr(self._feed, "held_by_instance_cap", 0)
        if held:
            attrs["held_by_instance_cap"] = held
        # Item 264: the ceiling in force, after the users' sliders, so a held
        # count can be read against it.
        attrs["instance_ceiling"] = instance_ceiling(self.hass)
        return attrs
