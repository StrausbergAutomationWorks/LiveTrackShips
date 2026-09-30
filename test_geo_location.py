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
             ("position_source", "observed")):
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
check("⚠ nameless, no type: marker_label is '?', never the MMSI",
      sp["marker_label"], "?")
typed = Observation(identity="338999112", source="live_track_ships",
                    observed_at=T0, latitude=41.95, longitude=-87.7,
                    ship_type=37)
check("nameless with a type: marker_label is the type label",
      ShipEvent(typed, 5.0).extra_state_attributes["marker_label"],
      "Pleasure craft")
check("an all-blank name counts as no name",
      ShipEvent(Observation(identity="338999113", source="live_track_ships",
                            observed_at=T0, latitude=41.95, longitude=-87.7,
                            name="                    ", ship_type=52),
                5.0).marker_label, "Tug")

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
check("⚠ NO unique_id - no registry row per vessel (2026-09-23)",
      m.unique_id, None)
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

print("\n=== a vessel with NO name and NO type is shown as '?' (2026-09-23) ===")
sp_e = ShipEvent(SPARSE, 5.0)
check("name is '?', never the MMSI", sp_e.name, "?")
check("⚠ the id is unaffected by the fallback", sp_e.suggested_object_id,
      "vessel_338999111")

print("\n=== backlog 258: map_layer and object_ids (D10, D11) ===")
check("z_index_offset attribute retired", "z_index_offset" in a, False)
check("vessel map_layer water", a.get("map_layer"), "water")
check("imo attribute is the validated string", a.get("imo"), "9543756")
check("object_ids, exact form", a.get("object_ids"),
      {"mmsi": "367148850", "imo": "9543756"})
check("sparse: mmsi only", sp.get("object_ids"), {"mmsi": "338999111"})
check("sparse: water", sp.get("map_layer"), "water")


def attrs_of(ident, **kw):
    ob = Observation(identity=ident, source="live_track_ships", observed_at=T0,
                     latitude=59.4, longitude=10.7, **kw)
    ev = ShipEvent(ob, 1.0)
    return ev.extra_state_attributes, ev.entity_picture


x, _ = attrs_of("367148851", imo=101210706)
check("nine-digit IMO kept out of object_ids", x.get("object_ids"),
      {"mmsi": "367148851"})
check("nine-digit IMO dropped from the imo attribute", "imo" in x, False)
x, _ = attrs_of("367148852", imo=9074728)
check("bad check digit kept out of object_ids", x.get("object_ids"),
      {"mmsi": "367148852"})
check("bad check digit dropped from the imo attribute", "imo" in x, False)
x, _ = attrs_of("367148853", imo=9074729)
check("valid IMO attribute is the 7-digit string", x.get("imo"), "9074729")
x, _ = attrs_of("367148854", imo=0)
check("IMO 0 dropped from the attribute", "imo" in x, False)
x, _ = attrs_of("586707076", name="FISHING BOUY")
check("net buoy fixed", x.get("map_layer"), "fixed")
x, p = attrs_of("111257001", name="NOR-002", speed_kmh=0.0)
check("SAR helicopter air_low", x.get("map_layer"), "air_low")
check("SAR helicopter icon", x.get("icon_category"), "sarheli")
check("SAR helicopter picture", "/sarheli/" in (p or ""), True)
check("SAR helicopter ids", x.get("object_ids"), {"mmsi": "111257001"})
x, p = attrs_of("111265103", name="SAR PLANE")
check("SAR plane air", x.get("map_layer"), "air")
check("SAR plane icon", x.get("icon_category"), "sarplane")
x, _ = attrs_of("257123450", name="RS 161", ship_type=51, length_m=16.0)
check("SAR BOAT is a vessel", x.get("object_kind"), "vessel")
check("SAR BOAT stays on the water", x.get("map_layer"), "water")

print("\n=== ONE icon form for every entry, no options (Lee 2026-09-25) ===")
import live_track_ships.const_flow as cf                            # noqa: E402
check("no card_rotation option exists", hasattr(cf, "CONF_CARD_ROTATION"), False)
check("no silhouette_only option exists", hasattr(cf, "CONF_SILHOUETTE_ONLY"), False)
x, p = attrs_of("367148860", heading_deg=90, course_deg=90, speed_kmh=20.0,
                ship_type=70, length_m=180.0)
check("vessel picture has no disc (b=0)", "b=0" in (p or ""), True)
check("vessel picture is UNROTATED", (p or "").split("?")[0].endswith("/fixed.svg"), True)
check("the card is told the angle", x.get("icon_rotation_deg"), 90)
x, p = attrs_of("111257001", name="NOR-002", heading_deg=45, speed_kmh=150.0)
check("SAR heli picture unrotated, no disc",
      ("/sarheli/fixed.svg" in (p or ""), "b=0" in (p or "")), (True, True))
x, p = attrs_of("258028670", name="KV MOB 2259", ship_type=51, heading_deg=200,
                speed_kmh=30.0)
check("SAR boat picture unrotated, no disc",
      ((p or "").split("?")[0].endswith("/fixed.svg"), "b=0" in (p or "")), (True, True))
ev = ShipEvent(Observation(identity="367148861", source="live_track_ships", observed_at=T0,
                           latitude=59.4, longitude=10.7, heading_deg=30), 1.0)
check("ShipEvent takes no icon options", ev.entity_picture is not None, True)

print("\n=== sailboat: the rig stands up, so the picture carries the angle (2026-09-28) ===")
x, p = attrs_of("367148870", ship_type=36, heading_deg=200, length_m=12.0)
check("sailboat picture unrotated", (p or "").split("?")[0].endswith("/sailing/fixed.svg"), True)
check("sailboat picture carries the counter angle", "s=200" in (p or ""), True)
check("the card is told the same angle", x.get("icon_rotation_deg"), 200)
x, p = attrs_of("367148871", ship_type=70, heading_deg=200, length_m=120.0)
check("cargo carries no counter angle", "s=" in (p or ""), False)

print("\n=== net buoys: any heading or course, at any speed; else WEST (Lee 2026-09-29) ===")
x, p = attrs_of("586707080", name="FISHING BOUY")
check("buoy, nothing to go on: no rotation attribute", "icon_rotation_deg" in x, False)
check("buoy, nothing to go on: drawn WEST in the image", "/netbuoy/270.svg" in (p or ""), True)
check("buoy, nothing to go on: still no disc", "b=0" in (p or ""), True)
x, p = attrs_of("586707081", name="FISHING BOUY", course_deg=200.0, speed_kmh=0.4)
check("buoy course at 0.4 km/h is used", (x.get("icon_rotation_deg"), x.get("icon_rotation_basis")), (200, "course"))
check("buoy with a course: image unrotated", "/netbuoy/fixed.svg" in (p or ""), True)
x, p = attrs_of("586707083", name="FISHING BOUY", course_deg=0.0, speed_kmh=0.0)
check("buoy course 0 at speed 0: no rotation attribute", "icon_rotation_deg" in x, False)
check("buoy course 0 at speed 0: drawn WEST in the image", "/netbuoy/270.svg" in (p or ""), True)
x, p = attrs_of("586707084", name="FISHING BOUY", course_deg=0.0, speed_kmh=0.4)
check("buoy course 0 while drifting: north, published",
      (x.get("icon_rotation_deg"), "/netbuoy/fixed.svg" in (p or "")), (0, True))
x, p = attrs_of("586707082", name="FISHING BOUY", heading_deg=10, course_deg=200.0, speed_kmh=0.4)
check("buoy heading wins over course", (x.get("icon_rotation_deg"), x.get("icon_rotation_basis")), (10, "heading"))
x, p = attrs_of("367148870", course_deg=200.0, speed_kmh=1.0, ship_type=70)
check("a VESSEL below 2 kn: its course is HELD, never basis course (Lee 2026-09-29)",
      (x.get("icon_rotation_deg"), x.get("icon_rotation_basis")), (200, "held"))
check("a VESSEL is never drawn east in the image", "/fixed.svg" in (p or ""), True)
x, p = attrs_of("367148875", speed_kmh=0.0, ship_type=70)
check("a VESSEL with nothing to go on: no rotation", "icon_rotation_deg" in x, False)

print("\n=== held: the right way, never north (Lee 2026-09-29) ===")
x, _ = attrs_of("367148871", speed_kmh=0.5, ship_type=60,
                extra={"previous_latitude": 59.4, "previous_longitude": 10.698})
check("slow, moved 113 m east, no course: held at 90",
      (x.get("icon_rotation_deg"), x.get("icon_rotation_basis")), (90, "held"))
x, _ = attrs_of("367148872", speed_kmh=0.5, ship_type=60, course_deg=10.0,
                extra={"previous_latitude": 59.399, "previous_longitude": 10.7})
check("slow, moved 111 m north: the move beats the slow course",
      (x.get("icon_rotation_deg"), x.get("icon_rotation_basis")), (0, "held"))
x, _ = attrs_of("367148873", speed_kmh=0.5, ship_type=60,
                extra={"previous_latitude": 59.4, "previous_longitude": 10.6997})
check("slow, moved 17 m, no course: jitter, no rotation", "icon_rotation_deg" in x, False)
mv = Observation(identity="367148874", source="live_track_ships", observed_at=T0,
                 latitude=59.4, longitude=10.7, speed_kmh=12.0, course_deg=120.0, ship_type=60)
ShipEvent(mv, 1.0)
back = Observation(identity="367148874", source="live_track_ships", observed_at=T0,
                   latitude=59.4, longitude=10.7, speed_kmh=0.0, ship_type=60)
x = ShipEvent(back, 1.0).extra_state_attributes
check("a NEW entity for the same vessel keeps its held angle",
      (x.get("icon_rotation_deg"), x.get("icon_rotation_basis")), (120, "held"))
ev = ShipEvent(Observation(identity="367148876", source="live_track_ships", observed_at=T0,
               latitude=59.4, longitude=10.7, speed_kmh=0.3, course_deg=250.0, ship_type=60), 1.0)
ev.update_from(Observation(identity="367148876", source="live_track_ships", observed_at=T0,
               latitude=59.4, longitude=10.7, speed_kmh=0.3, course_deg=40.0, ship_type=60), 1.0)
check("a slow-course seed is WEAK: a newer non-zero slow course replaces it (2026-09-29)",
      ev.extra_state_attributes.get("icon_rotation_deg"), 40)
ev.update_from(Observation(identity="367148876", source="live_track_ships", observed_at=T0,
               latitude=59.4, longitude=10.7, speed_kmh=0.0, course_deg=0.0, ship_type=60), 1.0)
check("course 0 at speed 0 does not replace it",
      ev.extra_state_attributes.get("icon_rotation_deg"), 40)
ev = ShipEvent(Observation(identity="367148877", source="live_track_ships", observed_at=T0,
               latitude=59.4, longitude=10.7, speed_kmh=12.0, course_deg=120.0, ship_type=60), 1.0)
ev.update_from(Observation(identity="367148877", source="live_track_ships", observed_at=T0,
               latitude=59.4, longitude=10.7, speed_kmh=0.3, course_deg=40.0, ship_type=60), 1.0)
check("a hold from a course at 2 kn STICKS against a slow course",
      (ev.extra_state_attributes.get("icon_rotation_deg"),
       ev.extra_state_attributes.get("icon_rotation_basis")), (120, "held"))

from live_track_ships.held import HELD                               # noqa: E402
ta = ShipEvent(Observation(identity="367148878", source="live_track_ships", observed_at=T0,
               latitude=59.4, longitude=10.7, speed_kmh=12.0, course_deg=80.0, ship_type=60), 1.0)
ShipEvent(Observation(identity="367148879", source="live_track_ships", observed_at=T0,
          latitude=59.4, longitude=10.7, speed_kmh=12.0, course_deg=81.0, ship_type=60), 1.0)
ta.update_from(Observation(identity="367148878", source="live_track_ships", observed_at=T0,
               latitude=59.4, longitude=10.7, speed_kmh=0.2, ship_type=60), 1.0)
check("the held angle is shared per vessel", HELD.get("367148878"), (80.0, True))
check("drawing a held angle again marks it held NOW (newest last)",
      list(HELD._d)[-1], "367148878")

print("\n=== ODYSSEY (367360260): course 0 at 0 km/h is no course (2026-09-29) ===")
od = ShipEvent(Observation(identity="367360261", source="live_track_ships", observed_at=T0,
               latitude=41.89, longitude=-87.61, speed_kmh=0.0, course_deg=0.0,
               nav_status=5, ship_type=60), 1.0)
x = od.extra_state_attributes
check("course 0 at 0 with no heading: no rotation, never north", "icon_rotation_deg" in x, False)
od.update_from(Observation(identity="367360261", source="live_track_ships", observed_at=T0,
               latitude=41.89, longitude=-87.61, speed_kmh=0.0, course_deg=49.4,
               nav_status=5, ship_type=60), 1.0)
x = od.extra_state_attributes
check("then course 49.4 at 0: drawn at 50, held",
      (x.get("icon_rotation_deg"), x.get("icon_rotation_basis")), (50, "held"))

print("\n=== sailboats with nothing to go on: hull EAST, rig upright (Lee 2026-09-29) ===")
x, p = attrs_of("367148880", ship_type=36, speed_kmh=0.0, length_m=10.0)
check("idle sailboat: no rotation attribute", "icon_rotation_deg" in x, False)
check("idle sailboat: drawn EAST in the image", "/sailing/90.svg" in (p or ""), True)
check("idle sailboat: no counter angle (the rig stays upright)", "s=" in (p or ""), False)
check("idle sailboat: not counter-rotated", "icon_counter_rotated" in x, False)
check("idle sailboat: no disc", "b=0" in (p or ""), True)
x, p = attrs_of("367148881", ship_type=36, speed_kmh=0.0, course_deg=0.0, length_m=10.0)
check("sailboat, course 0 at 0: still east", "/sailing/90.svg" in (p or ""), True)
x, p = attrs_of("367148882", ship_type=36, speed_kmh=0.3, course_deg=210.0, length_m=10.0)
check("sailboat with a slow course: held, unrotated image",
      (x.get("icon_rotation_deg"), "/sailing/fixed.svg" in (p or "")), (210, True))
x, p = attrs_of("367148883", ship_type=70, speed_kmh=0.0, length_m=100.0)
check("a cargo ship with nothing is NOT drawn east", "/fixed.svg" in (p or ""), True)
x, p = attrs_of("367148884", ship_type=37, speed_kmh=0.0, length_m=10.0)
check("a pleasure craft with nothing is NOT drawn east (sailboats only)", "/fixed.svg" in (p or ""), True)

print("\n=== icon_counter_rotated for UPRIGHT pictures (brief 2026-09-28) ===")
x, p = attrs_of("367148885", ship_type=36, heading_deg=200, length_m=12.0)
check("sailboat with an angle: True", x.get("icon_counter_rotated"), True)
x, p = attrs_of("367148886", ship_type=58, heading_deg=30, length_m=20.0)
check("medical with an angle: True", x.get("icon_counter_rotated"), True)
x, p = attrs_of("367148887", ship_type=70, heading_deg=30, length_m=120.0)
check("cargo with an angle: no key", "icon_counter_rotated" in x, False)
x, p = attrs_of("367148888", ship_type=58, speed_kmh=0.0, length_m=20.0)
check("medical with no angle: no key", "icon_counter_rotated" in x, False)
ch = ShipEvent(Observation(identity="367148889", source="live_track_ships", observed_at=T0,
               latitude=59.4, longitude=10.7, heading_deg=30, ship_type=36), 1.0)
check("before: sailing, key present", ch.extra_state_attributes.get("icon_counter_rotated"), True)
ch.update_from(Observation(identity="367148889", source="live_track_ships", observed_at=T0,
               latitude=59.4, longitude=10.7, heading_deg=30, ship_type=70), 1.0)
check("the key goes when the icon changes to a non-UPRIGHT one",
      "icon_counter_rotated" in ch.extra_state_attributes, False)
x, p = attrs_of("111257001", name="NOR-002", heading_deg=45, speed_kmh=150.0)
check("a SAR helicopter is not UPRIGHT: no key", "icon_counter_rotated" in x, False)

print("\n=== attribution: the entry's source credit (Lee 2026-09-26) ===")
import live_track_ships.const_flow as cfa                            # noqa: E402
check("no attribution given -> none", ShipEvent(FULL, 1.0).attribution, None)
check("attribution given -> carried",
      ShipEvent(FULL, 1.0, "Credit X").attribution, "Credit X")
dt_line = cfa.ATTRIBUTION[cfa.SOURCE_DIGITRAFFIC]
bw_line = cfa.ATTRIBUTION[cfa.SOURCE_BARENTSWATCH]
check("Digitraffic: Fintraffic's own credit wording",
      "Source: Fintraffic / digitraffic.fi" in dt_line and "license CC 4.0 BY" in dt_line)
check("Digitraffic: links the licence",
      "https://creativecommons.org/licenses/by/4.0/" in dt_line)
check("Digitraffic: links the original", "digitraffic.fi/en/marine-traffic" in dt_line)
check("Digitraffic: says it was changed", "Changed by Live Track Ships" in dt_line)
check("BarentsWatch: NLOD default credit, licensor named",
      "Contains data under the Norwegian licence for Open Government data (NLOD)" in bw_line
      and "distributed by BarentsWatch" in bw_line)
check("BarentsWatch: links NLOD", "https://data.norge.no/nlod/en/2.0" in bw_line)
check("BarentsWatch: says it was changed", "Changed by Live Track Ships" in bw_line)
check("aisstream credited", "aisstream.io" in cfa.ATTRIBUTION[cfa.SOURCE_AISSTREAM])
check("every source has a line", set(cfa.ATTRIBUTION), set(cfa.SOURCES))
check("no stored source -> aisstream's line",
      cfa.attribution_for(None), cfa.ATTRIBUTION[cfa.SOURCE_AISSTREAM])
check("an unknown source -> none", cfa.attribution_for("nope"), None)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
