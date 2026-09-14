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

⚠ TWO removal mechanisms exist in the shipped code. GDACS removes the registry
row in async_will_remove_from_hass; geo_json_events calls
async_remove(force_remove=True). Either works. Neither is automatic - omit both
and every departed vessel lingers forever as an unavailable entity.

⚠⚠ THE ENTITY_ID IS BUILT FROM THE NAME, and a correct unique_id does NOT
prevent it. Measured: geo_location.m_1_1_10_km_n_of_big_bear_city_ca. AIS
ShipName is a hard 20-character field operators MANGLE to fit - `ODYSSEY
CHICAGO_IVER` is real data, not corruption. Left alone that becomes
geo_location.odyssey_chicago_iver, PERMANENTLY. So _attr_name is built from the
MMSI, which is stable, and the readable name is an attribute.

See 10_SEED/05_SHARED_LESSONS.md sections A3, A4, D1, D6b.
"""

from __future__ import annotations

import logging

from homeassistant.components.geo_location import GeolocationEvent
from homeassistant.const import UnitOfLength
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er

from .const_flow import DOMAIN
from .sources.base import Observation

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Create and retire entities as vessels arrive and depart."""
    feed = hass.data[DOMAIN][entry.entry_id]
    known: dict[str, ShipEvent] = {}

    @callback
    def _sync():
        published = feed.store.published()
        seen = set()
        new = []
        for obs in published:
            seen.add(obs.identity)
            distance = feed.store.distance_to(obs)
            existing = known.get(obs.identity)
            if existing is None:
                entity = ShipEvent(obs, distance)
                known[obs.identity] = entity
                new.append(entity)
            else:
                existing.update_from(obs, distance)

        # ⚠ A vessel that fell out of the published set must be REMOVED, not
        # left stale. It has either departed, gone quiet past the retention
        # window, or been pushed out by the cap.
        for identity in [k for k in known if k not in seen]:
            entity = known.pop(identity)
            # ⚠⚠ THE REGISTRY ROW IS REMOVED *HERE*, ON DEPARTURE - never in
            # async_will_remove_from_hass.
            #
            # `async_remove(force_remove=True)` removes the STATE, NOT the
            # registry row. Its own docstring says so, and it was measured:
            # registry rows rose monotonically 46 -> 49 while live vessels
            # oscillated 38-46, a gap climbing 0 -> 11 in 65 minutes. That is
            # a leak, and the union of distinct vessels does not converge.
            #
            # ⚠ Removing it in async_will_remove_from_hass instead is what
            # caused `vessel_367152790_4`: that hook fires on SHUTDOWN too, so
            # the row was deleted every restart and re-registration collided
            # with the id still in the state machine.
            #
            # ⚠ Only this call site can tell a DEPARTURE from a SHUTDOWN.
            hass.async_create_task(_remove_vessel(hass, entity))

        if new:
            async_add_entities(new)

        # ⚠ SAY SO when the cap bites. A quietly clipped list looks exactly
        # like missing coverage - measured: 50 truncated 36% of samples on
        # ordinary water, peak 106.
        if feed.store.truncated_from:
            _LOGGER.debug("showing the nearest %d of %d vessels",
                          len(published), feed.store.truncated_from)

    entry.async_on_unload(feed.add_listener(_sync))
    _sync()


async def _remove_vessel(hass, entity) -> None:
    """Remove a departed vessel's state AND its registry row.

    ⚠ Order matters: the state goes first, then the row. Removing the row
    while the state is still present leaves the id occupied, which is what
    produces a `_2` suffix on the next registration.
    """
    entity_id = entity.entity_id
    await entity.async_remove(force_remove=True)
    registry = er.async_get(hass)
    if entity_id and entity_id in registry.entities:
        registry.async_remove(entity_id)


class ShipEvent(GeolocationEvent):
    """One vessel on the shared map."""

    _attr_should_poll = False
    _attr_source = DOMAIN
    _attr_unit_of_measurement = UnitOfLength.KILOMETERS
    _attr_icon = "mdi:ferry"

    def __init__(self, obs: Observation, distance_km: float):
        # ⚠ NAMESPACED, and built from MMSI - never from a name.
        self._attr_unique_id = f"{DOMAIN}:{obs.identity}"
        self._obs = obs
        self._attr_distance = distance_km

    @property
    def suggested_object_id(self) -> str:
        """⚠ THE ENTITY_ID COMES FROM HERE, NOT FROM THE NAME.

        Home Assistant derives the object id from `suggested_object_id` when it
        is set, falling back to the name otherwise
        (helpers/entity_platform.py:1311). That separation is what lets the
        friendly name be the ship's name while the id stays keyed on MMSI.

        ⚠ WITHOUT THIS the id would come from `name`, and AIS ShipName is a
        hard 20-character field operators MANGLE to fit - `ODYSSEY
        CHICAGO_IVER` is real data. That string would become a PERMANENT
        entity id.

        ⚠ Only consulted at FIRST registration. Existing entities keep the ids
        they already have.
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
        repair it, and fall back to the MMSI rather than to an empty string."""
        name = (self._obs.name or "").strip()
        return name or self._obs.identity

    # -- lifecycle ---------------------------------------------------------
    @callback
    def update_from(self, obs: Observation, distance_km: float) -> None:
        self._obs = obs
        self._attr_distance = distance_km
        if self.hass is not None:
            self.async_write_ha_state()

    async def async_will_remove_from_hass(self) -> None:
        """⚠⚠ NOTHING HAPPENS HERE, DELIBERATELY. Read before changing.

        This hook fires on DEPARTURE **and on SHUTDOWN**, and cannot tell them
        apart. Removing the registry row here deleted it on every restart, and
        re-registration then collided with the id still in the state machine -
        producing `vessel_367152790_4`, drifting upward forever.

        ⚠ The row IS removed on departure, in `_remove_vessel` at the `_sync`
        call site, which knows the difference.

        The original reasoning, kept because it is still true of the mechanism:

        An earlier version removed it here, copying GDACS. **That is wrong for
        this integration**, and it was measured going wrong: entity ids came
        back as `vessel_367152790_4`.

        GDACS reports EARTHQUAKES - one-shot events that never recur. A vessel
        recurs constantly: every reload, every expiry of the retention window,
        every flicker at the edge of the radius. Deleting the row and then
        re-registering the same `unique_id` makes Home Assistant find the base
        id still occupied and append a number, so ids drift upward forever -
        `_2`, `_3`, `_4` - breaking automations, history and dashboards.

        ⚠ THE COST OF KEEPING IT: registry rows accumulate. The distinct-vessel
        union does NOT converge - 30-37 new per day, 291 over five days - so a
        busy location will collect rows for every vessel ever seen. They are
        harmless, and Home Assistant offers a UI for deleting unavailable
        entities.

        ⚠ STABLE IDENTITY BEATS A TIDY REGISTRY. `05_SHARED_LESSONS.md` D6b
        records that two removal mechanisms exist in the shipped code; this is
        the choice between them, and it turns on whether the object RECURS.
        """
        return None
