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

from saw_livetrack import aisstream as _aisstream

from . import enforcement as _enf
from . import icons
from . import instance_ceiling
from .held import HELD
from .const_flow import DOMAIN
from .geo import hold_rank
from .quota import allocate
from .ship_types import label_for as ship_type_label
from .sources.base import (Observation, map_layer, object_ids, sar_airframe,
                           valid_imo)
from .web import picture_url

_LOGGER = logging.getLogger(__name__)

# MMSI -> entry_id of the config entry currently publishing that vessel.
# ⚠ Kept OUTSIDE hass.data[DOMAIN], which maps entry_id -> feed and is read by
# key elsewhere.
OWNERS_KEY = f"{DOMAIN}_owners"
# entry_id -> how many vessels that entry could show, for the quota (item 253).
DEMANDS_KEY = f"{DOMAIN}_demands"

# Omitted for anything that is not a vessel (sources/base.py object_kind).
_VESSEL_ONLY = ("ship_type", "ship_type_label", "call_sign", "destination",
                "imo", "length_m", "beam_m", "draught_m", "nav_status")
# Objects that do not move: no course, speed or turn, and no rotation.
_FIXED_KINDS = frozenset(("aton", "base_station"))
_MOTION = ("course_deg", "heading_deg", "speed_kmh", "rate_of_turn_dps")


async def async_setup_entry(hass, entry, async_add_entities):
    """Create and retire entities as vessels arrive and depart."""
    feed = hass.data[DOMAIN][entry.entry_id]
    owners: dict[str, str] = hass.data.setdefault(OWNERS_KEY, {})
    demands: dict[str, int] = hass.data.setdefault(DEMANDS_KEY, {})
    me = entry.entry_id
    known: dict[str, ShipEvent] = {}
    # ! CLAIMS (backlog 315 task 5): every vessel this entry draws, on the shared aisstream client, whatever the
    # source; Live Track SALT skips them. Same name as this entry's aisstream consumer, whose remove() drops them too.
    client = _aisstream.shared(hass.data)
    consumer = f"{DOMAIN}:{me}"

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
        # ⚠ ONE vessel, ONE entity, across ALL config entries. Two entries
        # over the same water both hear it; the first to publish owns it
        # until it departs from that entry. See the module docstring.
        candidates = [o for o in published
                      if owners.get(o.identity) in (None, me)]
        # ⛔ THE INSTANCE CEILING IS SHARED BY QUOTA (item 253, Lee
        # 2026-09-24), no longer first-come (item 246). Each entry reports
        # how many it could show; quota.allocate() gives each an equal share,
        # and what a quiet entry leaves goes to the others.
        # ⚠ REVERSES 246's "vessels already shown are never evicted": an
        # entry over its quota drops its FARTHEST vessels, because a quota
        # nobody gives back is first-come again. They leave through the
        # normal departure path below.
        # ⚠ Item 267: ranked with the EDGE HOLD - a vessel this entry already
        # shows counts as store.hold_km nearer - so a quota that moves by a
        # few does not trade the ring back and forth. Same rule as the
        # store's max_vessels cut (geo.hold_rank).
        hold = feed.store.hold_km
        ranked = sorted(
            ((feed.store.distance_to(o), o) for o in candidates),
            key=lambda t: (hold_rank(t[0], t[1].identity, known, hold),
                           t[1].identity))
        demands[me] = len(candidates)
        # The users' slider can only LOWER the constant (item 264).
        ceiling = instance_ceiling(hass)
        quota = allocate(demands, ceiling).get(me, 0)
        for rank, (distance, obs) in enumerate(ranked):
            identity = obs.identity
            owner = owners.get(identity)
            if rank >= quota:
                held += 1
                continue
            # Safety net, not the policy: another entry may not have shed
            # its surplus yet, so never let the instance exceed the ceiling.
            if owner is None and len(owners) >= ceiling:
                held += 1
                continue
            owners[identity] = me
            seen.add(identity)
            existing = known.get(identity)
            if existing is None:
                entity = ShipEvent(obs, distance, feed.attribution, feed.vessel_reader)
                known[identity] = entity
                new.append(entity)
            elif existing.update_from(obs, distance):
                written += 1

        # ⚠ A vessel that fell out of the published set must be REMOVED, not
        # left stale. It has either departed, gone quiet past the retention
        # window, or been pushed out by the cap.
        client.claim(consumer, seen)
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
        # An unloaded entry claims no share of the ceiling (item 253).
        demands.pop(me, None)
        # Nor any vessel: SALT may draw a listed one again (backlog 315 task 5).
        client.release(consumer)

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


# The held angle per vessel lives in held.HELD, not on the entity, so a
# vessel that leaves the entry's cut and comes back still points the way it
# did (Lee, 2026-09-29), and a STRONG one survives a restart
# (.storage/saw_vessel_held.sqlite, written by the prune pass).


class ShipEvent(GeolocationEvent):
    """One vessel on the shared map."""

    _attr_should_poll = False
    _attr_source = DOMAIN
    _attr_unit_of_measurement = UnitOfLength.KILOMETERS
    _attr_icon = "mdi:ferry"

    def __init__(self, obs: Observation, distance_km: float,
                 attribution: str | None = None, reader=None):
        # ⚠ NO unique_id - see the module docstring. Identity lives in the
        # entity_id (suggested_object_id) and in the `identity` attribute.
        self._obs = obs
        # The owning entry's source credit (const_flow.ATTRIBUTION). Fixed for
        # the entity's life: an entity belongs to the entry that created it.
        self._attr_attribution = attribution
        self._attr_distance = distance_km
        self.retired = False
        # The instance's EnforcementVessels reader (backlog 315 task 5, enforcement.py); the row is looked up with
        # each observation, in _refresh_icon, so the picture and the attributes always agree.
        self._reader = reader
        self._listed = None
        # The angle held while the vessel is at rest (icons.resolve) is kept
        # per vessel in held.HELD, never on this object. Never a heading:
        # heading stays meaningful at rest and is published as it is
        # (06_MAP_CONTRACT.md D4).
        self._icon: dict = {}
        self._refresh_icon()

    @callback
    def _refresh_icon(self) -> None:
        """Silhouette, colour, size and rotation for the current observation.

        ⚠ ONE FORM FOR EVERY ENTRY (Lee, 2026-09-25): the image is
        UNROTATED and has no disc; LiveTrackMapCard turns the marker by
        icon_rotation_deg (the angle goes into the attribute, never also into
        the image, or it doubles). The upright symbol of medical and SAR is
        counter-rotated inside the image so the card's turn stands it up
        again. The rotor of a SAR helicopter spins inside the image either
        way."""
        o = self._obs
        kind = o.kind
        weight = None
        if kind == "net_buoy":
            key = "netbuoy"
        elif kind == "sar_aircraft":
            key = icons.pick_sar(sar_airframe(o.identity))
        elif kind != "vessel":
            key = "generic"
        else:
            # A royal or presidential ship, then a named boat (by MMSI
            # alone, at its fixed size), draw their own icon (icons.choose).
            key, weight = icons.choose(o.identity, valid_imo(o.imo),
                                       o.ship_type, o.length_m, o.beam_m,
                                       o.nav_status)
        if kind in _FIXED_KINDS:
            bearing, basis = None, None
        elif kind == "net_buoy":
            # Any heading or course, at any speed; none -> west (icons.py).
            # A course of 0 at rest is none (Lee, 2026-09-29).
            bearing, basis = icons.buoy_bearing(o.heading_deg, o.course_deg,
                                                o.speed_kmh)
        else:
            prev = o.extra or {}
            arrival = icons.arrival_bearing(prev.get("previous_latitude"),
                                            prev.get("previous_longitude"),
                                            o.latitude, o.longitude)
            was = HELD.get(o.identity)
            bearing, basis, now = icons.resolve(o.heading_deg, o.course_deg,
                                                o.speed_kmh, was, arrival)
            if now != was:
                HELD.put(o.identity, *now)
            elif basis == "held":
                HELD.touch(o.identity)
        angle = icons.quantise(bearing)
        # ! THE LIST'S LOOK, ANYWHERE THIS ENTRY DRAWS IT (backlog 315 task 5): this integration's own silhouette in
        # the Coast Guard's fill, with the glow while sourced (enforcement.py).
        listed = _enf.listed(self._reader, o.identity) if kind == "vessel" else None
        self._listed = listed
        out: dict = {"icon_key": key}
        if angle is not None:
            out["icon_rotation_deg"] = angle
            out["icon_rotation_basis"] = basis
        symbol = key in icons.UPRIGHT
        # The card turns the picture by the angle and the symbol inside it is
        # turned back by the same angle: it must stay at the REPORTED angle
        # while the card slides it facing its travel (06_MAP_CONTRACT D3c-iv).
        # Omitted otherwise, never False (D0).
        if symbol and angle is not None:
            out["icon_counter_rotated"] = True
        # The pictures drawn rotated: a net buoy (WEST) or a sailboat (EAST)
        # with nothing to go on is turned in the image and publishes no
        # icon_rotation_deg, so the card leaves it as drawn and nothing
        # doubles. The sailboat's rig stays upright (Lee, 2026-09-29).
        baked = icons.REST_DEG_FOR.get(key) if angle is None else None
        out["entity_picture"] = picture_url(
            key,
            baked,
            _enf.LIST_TONE if listed else icons.tone_for(o.ship_type) if kind == "vessel"
            else icons.tone_for_kind(kind),
            icons.weight_for(key, o.length_m) if weight is None else weight,
            badge=False,
            counter=angle if symbol else None,
            # A wake only while moving (icons.WAKE_KEYS, Lee 2026-10-03).
            moving=key in icons.WAKE_KEYS and icons.is_moving(o.speed_kmh),
            # A pushing tug at 60 m or more: the barge ahead of it (icons.tow_form).
            tow=icons.tow_for(o.ship_type, o.length_m, o.beam_m, o.nav_status)
            if kind == "vessel" and key == "tug" else None,
            lights=_enf.lights(listed) if listed else None)
        self._icon = out

    @property
    def entity_picture(self) -> str | None:
        """The rendered silhouette; LiveTrackMapCard draws it as the marker."""
        return self._icon.get("entity_picture")

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
        in the UI as a result. A listed vessel is the list's name (D4b rule 14:
        `name` is the same text as the friendly name), never its label."""
        if self._listed is not None:
            return _enf.name(self._listed, self._obs.name) or self.marker_label
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
            # Only a valid IMO, as its 7-digit string (Lee 2026-09-25): a live
            # entity carried a nine-digit one. Same test as object_ids.
            ("imo", valid_imo(o.imo)),
            ("length_m", o.length_m),
            ("beam_m", o.beam_m),
            ("draught_m", o.draught_m),
            ("nav_status", o.nav_status),
        ):
            if value is not None:
                attrs[key] = value

        # ⚠ NOT A VESSEL (sources/base.py object_kind): no vessel type, size,
        # voyage or navigational status - a net buoy sends nav_status 0,
        # "under way using engine", as a default. A fixed object has no motion
        # either; a net buoy drifts with its line, so its course and speed are
        # real and it keeps them.
        kind = o.kind
        attrs["object_kind"] = kind
        if kind != "vessel":
            for key in _VESSEL_ONLY:
                attrs.pop(key, None)
            if kind in _FIXED_KINDS:
                for key in _MOTION:
                    attrs.pop(key, None)

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
        # attributes.
        # 06_MAP_CONTRACT.md D10/D11 (backlog 258): the layer NAME, which the
        # card maps to its stacking, and the identifiers the card merges
        # duplicates on. The numeric z_index_offset attribute is retired: the
        # card never read it (measured 2026-09-24). A non-vessel publishes no
        # imo attribute, so it offers none here either.
        attrs["map_layer"] = map_layer(kind, o.identity)
        ids = object_ids(o.identity, o.imo if kind == "vessel" else None)
        if ids:
            attrs["object_ids"] = ids
        # ⚠ icon_category was "vessel" on every entity until 2026-09-24; it is
        # now the silhouette drawn (SSOT item 254). Nothing on the dashboard
        # filtered on it (read that day, lts_dash_read.txt).
        attrs["icon_category"] = self._icon["icon_key"]
        for key in ("icon_rotation_deg", "icon_rotation_basis",
                    "icon_counter_rotated"):
            if key in self._icon:
                attrs[key] = self._icon[key]
        # A listed vessel: the list's status, agency, entry and hull, and the hover's name and agency (D4b
        # rule 14), as Live Track SALT publishes them; `name` becomes the list's.
        if self._listed is not None:
            attrs.update(_enf.attributes(self._listed, o.name))
        return attrs

    @property
    def attribution(self) -> str | None:
        """The source's credit; a listed vessel adds the list's ODbL line."""
        if self._listed is not None:
            return _enf.attribution(self._attr_attribution)
        return self._attr_attribution

    @property
    def marker_label(self) -> str:
        """⚠ ShipName is space-padded inconsistently and MANGLED to fit 20
        characters - `ODYSSEY CHICAGO_IVER` is real data. Strip it, never
        repair it.

        With no name, the type label ("Pleasure craft", "Tug"); with neither,
        "?". Never the MMSI - nine digits on a dot tell a user nothing (Lee,
        2026-09-23). The MMSI stays in `identity` and the entity id.

        A listed vessel: the list's label, "USCG" (backlog 315 task 5)."""
        if self._listed is not None:
            return _enf.label(self._listed)
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
        self._refresh_icon()
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
