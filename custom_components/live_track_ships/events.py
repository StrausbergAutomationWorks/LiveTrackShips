"""Entry and exit events, one pair per area (backlog 342, 2026-11-15).

`live_track_ships_entry` when a vessel comes into an area's circle and
`live_track_ships_exit` when it leaves, the shape OpenSky and Flightradar24
use, so a user's own automation decides which ships matter (by name, type,
length, speed, course). The integration still filters nothing.

Counted on the store's `present()`: every vessel inside the circle, by its
newest fix. NOT on the entities: the per-entry cap, the instance quota and
which entry owns a vessel decide what is DRAWN, and none of them may make a
vessel enter or leave. Two areas over the same water each fire their own.

Three rules, each against a measured nuisance:

  1. WARM-UP. A restart or reload starts with an empty store and hears the
     vessels already there over several minutes (a moored vessel reports
     every 3 min, p95 539 s, measured 2026-09-08, store.py). For WARMUP_S
     after the area starts, a first sighting is taken as already inside and
     announced to nobody. A vessel that really arrives in that window is
     missed: a restart must not send one notification per moored boat.
  2. EXIT GRACE. An exit is announced only after the vessel has stayed out
     EXIT_GRACE_S. Back inside sooner (a vessel along the edge, a bad fix)
     and nothing is announced: one entry, one exit.
  3. TWO KINDS OF EXIT. `reason: left` when the vessel was HEARD outside
     (the listening ring, geo.listen_margin_km); `reason: silent` when it
     was not heard for the retention window (30 min, or 6 h moored). A
     silent vessel may still be there: no message is not no vessel.
"""

from __future__ import annotations

import logging
import math
import time

from .const_flow import DOMAIN
from .geo import distance_km
from .ship_types import label_for as ship_type_label
from .sources.base import valid_imo

_LOGGER = logging.getLogger(__name__)

EVENT_ENTRY = f"{DOMAIN}_entry"
EVENT_EXIT = f"{DOMAIN}_exit"

WARMUP_S = 600
EXIT_GRACE_S = 120

# Omitted for anything that is not a vessel (sources/base.py object_kind).
# ONE copy: geo_location.py imports it from here.
VESSEL_ONLY = ("ship_type", "ship_type_label", "call_sign", "destination",
               "imo", "length_m", "beam_m", "draught_m", "nav_status")
# Objects that do not move.
FIXED_KINDS = frozenset(("aton", "base_station"))
MOTION = ("course_deg", "heading_deg", "speed_kmh", "rate_of_turn_dps")


def bearing_deg(lat1, lon1, lat2, lon2) -> float:
    """Initial great-circle bearing from point 1 to point 2, 0-360, true."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    x = math.sin(dl) * math.cos(p2)
    y = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return round((math.degrees(math.atan2(x, y)) + 360.0) % 360.0, 1)


class AreaEvents:
    """Who is inside one area, and the events when that changes.

    `fire(event_type, data)` and `call_later(delay_s, callback) -> handle with
    .cancel()` are passed in, so the logic runs without Home Assistant in a
    test; `clock` is monotonic seconds."""

    def __init__(self, store, area_id, area_name, lat, lon, fire, call_later,
                 clock=time.monotonic, drawn=None):
        self._store = store
        self._area_id = area_id
        self._area_name = area_name
        self._lat, self._lon = lat, lon
        self._fire = fire
        self._call_later = call_later
        self._clock = clock
        self._drawn = drawn or (lambda _identity: False)
        self._started = clock()
        # identity -> newest fix while inside (or within its exit grace)
        self._inside: dict = {}
        # identity -> (deadline, reason, last fix inside, fix outside or None)
        self._leaving: dict = {}
        self._timer = None
        self.fired = {EVENT_ENTRY: 0, EVENT_EXIT: 0}   # for tests and logs

    @property
    def warming(self) -> bool:
        return self._clock() - self._started < WARMUP_S

    def run(self) -> None:
        """One pass: called after every store change (the feed's coalesced
        listener) and when an exit grace runs out."""
        now = self._clock()
        warming = now - self._started < WARMUP_S
        present = self._store.present()
        gone = self._store.take_gone()
        for identity, obs in present.items():
            self._leaving.pop(identity, None)          # back inside: no exit
            if identity not in self._inside and not warming:
                self._announce(EVENT_ENTRY, obs)
            self._inside[identity] = obs
        for identity in [k for k in self._inside
                         if k not in present and k not in self._leaving]:
            reason, last, outside = gone.get(
                identity, ("silent", self._inside[identity], None))
            self._leaving[identity] = (now + EXIT_GRACE_S, reason,
                                       last or self._inside[identity], outside)
        for identity, (due, reason, last, outside) in list(self._leaving.items()):
            if due <= now:
                del self._leaving[identity]
                self._inside.pop(identity, None)
                self._announce(EVENT_EXIT, last, outside, reason)
        self._schedule(now)

    def _schedule(self, now) -> None:
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        if self._leaving:
            due = min(v[0] for v in self._leaving.values())
            self._timer = self._call_later(max(0.0, due - now) + 0.5,
                                           self._tick)

    def _tick(self, *_args) -> None:
        self._timer = None
        self.run()

    def close(self) -> None:
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    def _announce(self, event_type, obs, outside=None, reason=None) -> None:
        try:
            data = self.payload(obs, outside, reason)
        except Exception:                          # noqa: BLE001
            _LOGGER.exception("Live Track Ships: event for %s not built",
                              getattr(obs, "identity", "?"))
            return
        self.fired[event_type] += 1
        self._fire(event_type, data)

    def payload(self, obs, outside=None, reason=None) -> dict:
        """The event's data. Names and units as the vessel entity's
        attributes (05_SHARED_LESSONS.md D); an unknown value is OMITTED,
        never a placeholder. For an exit HEARD outside, the position and
        motion are the fix outside, the identity and details the last fix
        inside (a fix outside may come before the details are relayed)."""
        pos = outside if outside is not None else obs
        kind = obs.kind
        name = (obs.name or "").strip() or None
        data: dict = {"area_id": self._area_id, "area": self._area_name,
                      "identity": obs.identity}
        if reason is not None:
            data["reason"] = reason
        # Only while some entry DRAWS it (geo_location's OWNERS map): the cap
        # or the quota can leave a vessel inside the circle and off the map.
        # Never on an exit: the entity is being removed in the same pass.
        if reason is None and self._drawn(obs.identity):
            data["entity_id"] = f"geo_location.vessel_{obs.identity}"
        for key, value in (
            ("name", name),
            ("object_kind", kind),
            ("ship_type", obs.ship_type),
            ("ship_type_label", ship_type_label(obs.ship_type)),
            ("call_sign", obs.call_sign),
            ("imo", valid_imo(obs.imo)),
            ("length_m", obs.length_m),
            ("beam_m", obs.beam_m),
            ("draught_m", obs.draught_m),
            ("destination", obs.destination),
            ("nav_status", _first(pos.nav_status, obs.nav_status)),
            ("speed_kmh", pos.speed_kmh),
            ("course_deg", pos.course_deg),
            ("heading_deg", pos.heading_deg),
            ("latitude", pos.latitude),
            ("longitude", pos.longitude),
        ):
            if value is not None:
                data[key] = value
        if pos.latitude is not None and pos.longitude is not None:
            data["distance_km"] = round(distance_km(
                self._lat, self._lon, pos.latitude, pos.longitude), 2)
            data["bearing_from_centre_deg"] = bearing_deg(
                self._lat, self._lon, pos.latitude, pos.longitude)
        if pos.observed_at is not None:
            data["last_seen"] = pos.observed_at.isoformat()
        if kind != "vessel":
            for key in VESSEL_ONLY:
                data.pop(key, None)
            if kind in FIXED_KINDS:
                for key in MOTION:
                    data.pop(key, None)
        return data


def _first(*values):
    for v in values:
        if v is not None:
            return v
    return None


def attach(hass, entry, feed) -> AreaEvents:
    """Wire one area's events to Home Assistant: the bus, the loop's timer,
    and the feed's coalesced listener; unload registered on the entry.

    ⚠ Call AFTER the platforms are set up: listeners run in the order they
    were added, so geo_location's pass has claimed this pass's vessels in
    OWNERS before an entry event asks whether the vessel is drawn."""
    owners_key = f"{DOMAIN}_owners"      # geo_location.OWNERS_KEY

    def _fire(event_type, data):
        hass.bus.async_fire(event_type, data)

    events = AreaEvents(
        feed.store, entry.entry_id, entry.title, feed.lat, feed.lon,
        fire=_fire, call_later=hass.loop.call_later,
        drawn=lambda identity: identity in hass.data.get(owners_key, {}))
    entry.async_on_unload(feed.add_listener(events.run))
    entry.async_on_unload(events.close)
    return events
