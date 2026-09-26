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

from homeassistant.components.sensor import SensorEntity, SensorStateClass

from . import instance_ceiling
from .const_flow import DOMAIN
from .geo_location import OWNERS_KEY

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    feed = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([VesselCountSensor(entry, feed)])


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
