"""geo_location platform - the shared-map surface.

⚠ MEASURED AGAINST HA 2026.9.0 AND AGAINST 155 LIVE geo_location ENTITIES.
Four platform facts that are easy to get wrong and produce silent failures:

  1. `state` is @final AND IS THE DISTANCE - round(self.distance, 1).
     Do NOT add a distance attribute. Do NOT try to override state.
  2. `state_attributes` is @final and returns ONLY source, latitude,
     longitude. EVERY custom value must go in `extra_state_attributes` or it
     is silently discarded. This is the _FLIGHT_ATTRS trap in a new costume.
  3. `_attr_source` is MANDATORY - declared with no default. It is the
     discriminator the shared map filters on.
  4. `_attr_should_poll = False`, or the component polls on a 60 s
     SCAN_INTERVAL against a push source.

⚠⚠ VESSEL ENTITIES CARRY NO unique_id - since 2026-09-23 (Lee's decision).
Measured that day: 3,684 live and 2,807 deleted registry rows belonged to this
integration, about 5.7 MB of a 7.0 MB core.entity_registry - 78% of every
entity on the instance. Removing a row on departure did not shrink anything:
Home Assistant moves it to deleted_entities and keeps it for 30 days. Live
Track Aircraft and Brightline already emit no per-object unique_id.

With no unique_id there is no registry row, so there is nothing to drift: HA
2026.9.3 (helpers/entity_platform.py, the `unique_id is None` branch) takes the
id from `suggested_object_id` and appends a suffix only if that id is held by
a live state or a registered entity. Hence two rules:
  - the old registry rows MUST be purged in the same restart that loads this
    code, or every vessel with a leftover row comes up as vessel_<MMSI>_2;
  - two config entries must never publish the same vessel at once, or the
    second copy becomes vessel_<MMSI>_2 - a second marker for one ship. The
    OWNERS map below prevents that (SSOT item 247b).

⚠ The entity_id is still keyed on MMSI through `suggested_object_id`; the
friendly name and the map label are the ship's name. AIS ShipName is a hard
20-character field operators MANGLE to fit - `ODYSSEY CHICAGO_IVER` is real
data and must never become an entity id.

See 10_SEED/06_MAP_CONTRACT.md D1, D6a-0b and D6b.
"""

from __future__ import annotations

import logging

from homeassistant.components.geo_location import GeolocationEvent
from homeassistant.const import UnitOfLength
from homeassistant.core import callback

from .const_flow import DOMAIN, INSTANCE_MAX_VESSELS
from .ship_types import label_for as ship_type_label
from .sources.base import Observation

_LOGGER = logging.getLogger(__name__)

# MMSI -> entry_id of the config entry currently publishing that vessel.
# ⚠ Kept OUTSIDE hass.data[DOMAIN], which maps entry_id -> feed and is read by
# key elsewhere.
OWNERS_KEY = f"{DOMAIN}_owners"


async def async_setup_entry(hass, entry, async_add_entities):
    """Create and retire entities as vessels arrive and depart."""
    feed = hass.data[DOMAIN][entry.entry_id]
    owners: dict[str, str] = hass.data.setdefault(OWNERS_KEY, {})
    me = entry.entry_id
    known: dict[str, ShipEvent] = {}

    def _releaser(identity: str):
        @callback
        def _release() -> None:
            if owners.get(identity) == me:
                del owners[identity]
        return _release

    @callback
    def _sync():
        published = feed.store.published()
        seen = set()
        new = []
        held = 0
        written = 0
        for obs in published:
            identity = obs.identity
            # ⚠ ONE vessel, ONE entity, across ALL config entries. Two entries
            # over the same water both hear it; the first to publish owns it
            # until it departs from that entry. See the module docstring.
            owner = owners.get(identity)
            if owner is not None and owner != me:
                continue
            # ⛔ THE INSTANCE CEILING (item 246): a NEW vessel is not added
            # while the map already holds INSTANCE_MAX_VESSELS across every
            # entry. Vessels already shown keep their place.
            if owner is None and len(owners) >= INSTANCE_MAX_VESSELS:
                held += 1
                continue
            owners[identity] = me
            seen.add(identity)
            distance = feed.store.distance_to(obs)
            existing = known.get(identity)
            if existing is None:
                entity = ShipEvent(obs, distance)
                known[identity] = entity
                new.append(entity)
            elif existing.update_from(obs, distance):
                written += 1

        # ⚠ A vessel that fell out of the published set must be REMOVED, not
        # left stale. It has either departed, gone quiet past the retention
        # window, or been pushed out by the cap.
        gone = [k for k in known if k not in seen]
        for identity in gone:
            entity = known.pop(identity)
            hass.async_create_task(
                _remove_vessel(entity, _releaser(identity)))

        if new:
            async_add_entities(new)

        # Read by sensor.ships_in_range: a ceiling that bites silently looks
        # exactly like missing coverage.
        feed.held_by_instance_cap = held

        # Item 246: one line per pass, at debug, so the pass rate and the
        # write count can be read off the log without a code change.
        _LOGGER.debug("pass: %d published, %d new, %d written, %d removed, "
                      "%d held", len(published), len(new), written,
                      len(gone), held)

        # ⚠ SAY SO when the cap bites. A quietly clipped list looks exactly
        # like missing coverage - measured: 50 truncated 36% of samples on
        # ordinary water, peak 106.
        if feed.store.truncated_from:
            _LOGGER.debug("showing the nearest %d of %d vessels",
                          len(published), feed.store.truncated_from)

    @callback
    def _release_all() -> None:
        """On unload the platform removes the entities; give up ownership so
        another entry can take the vessels over.

        ⚠ Known race, accepted: if another entry claims a vessel before this
        entry's state for it is gone, the newcomer is vessel_<MMSI>_2 until it
        departs. Only at unload or disable, never in normal running."""
        for identity in list(known):
            _releaser(identity)()
        known.clear()

    entry.async_on_unload(feed.add_listener(_sync))
    entry.async_on_unload(_release_all)
    _sync()


async def _remove_vessel(entity: "ShipEvent", release) -> None:
    """Remove a departed vessel's state, THEN release its MMSI.

    ⚠ Release comes after the state is gone. Releasing first lets another
    entry claim the vessel while vessel_<MMSI> is still in the state machine,
    and the newcomer becomes vessel_<MMSI>_2.

    ⚠ `entity.hass is None` means Home Assistant never added it, or has not
    YET. Calling async_remove then raises AttributeError 'NoneType' has no
    attribute 'loop' (SSOT item 247a, measured 2026-09-23). Mark it retired
    instead; async_added_to_hass removes it if the add lands later.
    """
    try:
        if entity.hass is None:
            entity.retired = True
            return
        await entity.async_remove(force_remove=True)
    finally:
        release()


class ShipEvent(GeolocationEvent):
    """One vessel on the shared map."""

    _attr_should_poll = False
    _attr_source = DOMAIN
    _attr_unit_of_measurement = UnitOfLength.KILOMETERS
    _attr_icon = "mdi:ferry"

    def __init__(self, obs: Observation, distance_km: float):
        # ⚠ NO unique_id - see the module docstring. Identity lives in the
        # entity_id (suggested_object_id) and in the `identity` attribute.
        self._obs = obs
        self._attr_distance = distance_km
        self.retired = False

    @property
    def suggested_object_id(self) -> str:
        """⚠ THE ENTITY_ID COMES FROM HERE, NOT FROM THE NAME.

        Home Assistant derives the object id from `suggested_object_id` when it
        is set, falling back to the name otherwise. With no unique_id this is
        consulted on EVERY add, so the id is vessel_<MMSI> each time the vessel
        appears - provided nothing else holds that id (module docstring).

        ⚠ WITHOUT THIS the id would come from `name`, and AIS ShipName is a
        hard 20-character field operators MANGLE to fit - `ODYSSEY
        CHICAGO_IVER` is real data.
        """
        return f"vessel_{self._obs.identity}"

    @property
    def name(self) -> str:
        """What the user sees. ⚠ Safe to be the ship's name BECAUSE
        suggested_object_id owns the entity id. An earlier version returned
        "Vessel <MMSI>" here purely to protect the id, and the MMSI showed up
        in the UI as a result."""
        return self.marker_label

    # -- platform-mandated ------------------------------------------------
    @property
    def latitude(self) -> float | None:
        return self._obs.latitude

    @property
    def longitude(self) -> float | None:
        return self._obs.longitude

    @property
    def distance(self) -> float | None:
        """⚠ This becomes the entity STATE. Never also an attribute."""
        return self._attr_distance

    # -- the contract -----------------------------------------------------
    @property
    def extra_state_attributes(self) -> dict:
        """⚠ EVERYTHING custom goes here. `state_attributes` is @final and
        anything put there is silently discarded.

        Field names follow 05_SHARED_LESSONS.md section D: units live in the
        NAME, and an unavailable value is OMITTED - never a sentinel, never a
        placeholder. A wrong heading_deg is worse than an absent one, because
        the consumer cannot tell.
        """
        o = self._obs
        attrs: dict = {
            "identity": o.identity,
            "marker_label": self.marker_label,
            "last_seen": o.observed_at.isoformat(),
            "position_source": o.position_source,
        }

        # ⚠ heading_deg and course_deg are DIFFERENT FIELDS. Rotate the icon by
        # heading; extrapolate by course ONLY. Measured: TrueHeading was the
        # 511 sentinel on six of nine position reports, so heading is
        # frequently absent while course is present.
        for key, value in (
            ("course_deg", o.course_deg),
            ("heading_deg", o.heading_deg),
            ("speed_kmh", o.speed_kmh),
            ("altitude_m", None),
            ("rate_of_turn_dps", o.rate_of_turn_dps),
            ("name", o.name),
            ("ship_type", o.ship_type),
            # ⚠ The label is OMITTED, not "Unknown", when the code is the 0
            # sentinel or a reserved range - measured, 147 of 255 reported
            # types are 0. A placeholder cannot be told from a reading. D0.
            ("ship_type_label", ship_type_label(o.ship_type)),
            ("call_sign", o.call_sign),
            ("destination", o.destination),
            ("imo", o.imo),
            ("length_m", o.length_m),
            ("beam_m", o.beam_m),
            ("draught_m", o.draught_m),
            ("nav_status", o.nav_status),
        ):
            if value is not None:
                attrs[key] = value

        # ⚠ max_extrapolation_s is DELIBERATELY ABSENT for ships. No field, no
        # motion. Vessels have course and speed on 76% of messages and still
        # fail the eligibility test on geography: at a p95 gap of 450 s at
        # 10 kn a projected vessel is drawn 2.3 km across a 60 m wide river.
        # See 05_SHARED_LESSONS.md D3a.

        # The previous fix, so a consumer can animate between two OBSERVED
        # points. Absent on a first sighting - a consumer must read that as
        # "place it and do not move it".
        for key in ("previous_latitude", "previous_longitude",
                    "segment_duration_s"):
            if key in o.extra:
                attrs[key] = o.extra[key]
        prev_at = o.extra.get("previous_observed_at")
        if prev_at is not None:
            attrs["previous_observed_at"] = prev_at.isoformat()

        # ⚠ Display helpers: an integration MAY emit them, a consumer MUST NOT
        # require them. They exist only because ha-map-card cannot compute on
        # attributes. z_index puts vessels below aircraft on the shared map.
        attrs["z_index_offset"] = 20
        attrs["icon_category"] = "vessel"
        return attrs

    @property
    def marker_label(self) -> str:
        """⚠ ShipName is space-padded inconsistently and MANGLED to fit 20
        characters - `ODYSSEY CHICAGO_IVER` is real data. Strip it, never
        repair it.

        With no name, the type label ("Pleasure craft", "Tug"); with neither,
        "?". Never the MMSI - nine digits on a dot tell a user nothing (Lee,
        2026-09-23). The MMSI stays in `identity` and the entity id."""
        name = (self._obs.name or "").strip()
        return name or ship_type_label(self._obs.ship_type) or "?"

    # -- lifecycle ---------------------------------------------------------
    @callback
    def update_from(self, obs: Observation, distance_km: float) -> bool:
        """Write state only if the observation changed. Returns whether it did.

        ⛔ Item 246: every pass used to write EVERY vessel. HA drops an
        identical write without a state_changed event - read on the box,
        core.py async_set_internal - but still builds the attributes, compares
        them and fires state_reported, for each vessel, each pass. Compared by
        VALUE, not by fix time, so static data arriving on its own (name,
        type, size) still reaches the entity."""
        if obs == self._obs and distance_km == self._attr_distance:
            return False
        self._obs = obs
        self._attr_distance = distance_km
        if self.hass is not None:
            self.async_write_ha_state()
        return True

    async def async_added_to_hass(self) -> None:
        """⚠ The vessel may have departed between async_add_entities and this
        call; _remove_vessel then found hass None and marked it retired."""
        if self.retired:
            self.hass.async_create_task(self.async_remove(force_remove=True))

    async def async_will_remove_from_hass(self) -> None:
        """Nothing to do: with no unique_id there is no registry row to keep
        or delete. The history of why the row was once kept on departure and
        shutdown (vessel_367152790_4) is in 06_MAP_CONTRACT.md D6a-0b."""
        return None
