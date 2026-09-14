"""Contract test for the geo_location entity, against REAL Home Assistant.

⚠ THE STUB IS GONE, DELETED 2026-09-08. It existed because Home Assistant was
not importable on the Windows box - but it was wrong in a way that mattered
(it did not map _attr_<x> to the property <x>, so it measured itself), and once
__init__.py imported homeassistant the stub SHADOWED the real module and broke
the package it was meant to test.

⚠ This suite runs INSIDE the Home Assistant container against 2026.9.1. That
is the only place the four platform facts in 05_SHARED_LESSONS.md A4 can be
confirmed rather than read off source.
"""
import datetime as dt
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent / "custom_components"))

from homeassistant.components.geo_location import GeolocationEvent  # noqa: E402
from homeassistant.util import slugify                              # noqa: E402

from live_track_ships.geo_location import ShipEvent                 # noqa: E402
from live_track_ships.sources.base import Observation               # noqa: E402

passed = failed = 0
T0 = dt.datetime(2026, 9, 8, 12, 0, 0, tzinfo=dt.timezone.utc)


def check(label, got, want=True):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}"
          + ("" if ok else f"   got {got!r} want {want!r}"))


FULL = Observation(
    identity="367148850", source="live_track_ships", observed_at=T0,
    latitude=41.9, longitude=-87.6, course_deg=130.6, heading_deg=204,
    speed_kmh=30.0, name="FINNBREEZE", ship_type=70, call_sign="OJKV",
    destination="USCHI", imo=9543756, length_m=217.0, beam_m=30.0,
    draught_m=6.6, nav_status=0,
    extra={"previous_latitude": 41.8, "previous_longitude": -87.5,
           "previous_observed_at": T0 - dt.timedelta(seconds=90),
           "segment_duration_s": 90.0})

SPARSE = Observation(identity="338999111", source="live_track_ships",
                     observed_at=T0, latitude=41.95, longitude=-87.7)

MANGLED = Observation(identity="367700010", source="live_track_ships",
                      observed_at=T0, latitude=41.9, longitude=-87.6,
                      name="ODYSSEY CHICAGO_IVER")

print("=== it really is a GeolocationEvent ===")
e = ShipEvent(FULL, 12.3)
check("subclass of the real base", isinstance(e, GeolocationEvent))

print("\n=== ⚠ the four platform facts, against real HA ===")
check("state IS the distance", e.state, 12.3)
check("state is @final on the base", "state" in GeolocationEvent.__dict__)
check("state_attributes is @final on the base",
      "state_attributes" in GeolocationEvent.__dict__)
check("state_attributes holds ONLY source/lat/lon",
      sorted(e.state_attributes), ["latitude", "longitude", "source"])
check("source is the domain", e.state_attributes["source"],
      "live_track_ships")
check("should_poll is False", e.should_poll, False)

print("\n=== ⚠ our attributes survive the @final wall ===")
a = e.extra_state_attributes
for k, v in (("identity", "367148850"), ("marker_label", "FINNBREEZE"),
             ("course_deg", 130.6), ("heading_deg", 204),
             ("speed_kmh", 30.0), ("ship_type", 70),
             ("position_source", "observed"), ("z_index_offset", 20)):
    check(k, a.get(k), v)
check("last_seen is ISO", a["last_seen"], T0.isoformat())

print("\n=== ⚠ distance is the STATE, never an attribute ===")
check("no distance attribute", "distance" in a, False)
check("no distance_km attribute", "distance_km" in a, False)

print("\n=== ⚠ absent values are OMITTED, never sentinels ===")
sp = ShipEvent(SPARSE, 5.0).extra_state_attributes
for k in ("course_deg", "heading_deg", "speed_kmh", "ship_type", "name",
          "destination", "imo", "draught_m", "nav_status"):
    check(f"{k} absent, not None", k in sp, False)
check("marker_label falls back to MMSI", sp["marker_label"], "338999111")

print("\n=== ⚠ ships must never be movable ===")
check("max_extrapolation_s absent when full", "max_extrapolation_s" in a,
      False)
check("max_extrapolation_s absent when sparse",
      "max_extrapolation_s" in sp, False)

print("\n=== the previous fix, for consumer-side animation ===")
check("previous_latitude", a["previous_latitude"], 41.8)
check("segment_duration_s", a["segment_duration_s"], 90.0)
check("previous_observed_at is ISO", a["previous_observed_at"],
      (T0 - dt.timedelta(seconds=90)).isoformat())
check("⚠ absent on a first sighting", "previous_latitude" in sp, False)

print("\n=== ⚠⚠ a MANGLED ShipName must not reach the entity_id ===")
m = ShipEvent(MANGLED, 3.0)
check("unique_id is namespaced on MMSI", m.unique_id,
      "live_track_ships:367700010")
# ⚠ THE SPLIT: the ID is keyed on MMSI, the NAME is not.
check("the readable name IS the mangled ShipName", m.name,
      "ODYSSEY CHICAGO_IVER")
check("⚠ but the entity id comes from the MMSI",
      m.suggested_object_id, "vessel_367700010")
eid = f"geo_location.{slugify(m.suggested_object_id)}"
print(f"   entity_id would be: {eid}")
check("⚠ no ShipName in the entity_id", "odyssey" in eid.lower(), False)
check("the mangled name IS still readable as an attribute",
      m.extra_state_attributes["name"], "ODYSSEY CHICAGO_IVER")
check("marker_label uses it", m.extra_state_attributes["marker_label"],
      "ODYSSEY CHICAGO_IVER")


print("\n=== the full-entity case ===")
check("⚠ entity id from MMSI", e.suggested_object_id, "vessel_367148850")
check("name is the ship, not the number", e.name, "FINNBREEZE")

print("\n=== a vessel with NO name falls back to the MMSI ===")
sp_e = ShipEvent(SPARSE, 5.0)
check("name falls back to the identity", sp_e.name, "338999111")
check("⚠ the id is unaffected by the fallback", sp_e.suggested_object_id,
      "vessel_338999111")

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
