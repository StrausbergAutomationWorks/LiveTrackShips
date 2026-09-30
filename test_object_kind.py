"""object_kind() / is_vessel and the net-buoy icon.

Loads sources/base.py and icons.py by FILE PATH, so it runs anywhere with no
Home Assistant installed (SSOT item 22). Run: python test_object_kind.py
"""
import datetime as dt
import importlib.util
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
# In the clone and in /config on the box alike, the component sits here.
COMP = os.path.join(HERE, "custom_components", "live_track_ships")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


base = load("lts_base", os.path.join(COMP, "sources", "base.py"))
icons = load("lts_icons", os.path.join(COMP, "icons.py"))

passed = failed = 0


def check(label, got, want):
    global passed, failed
    if got == want:
        passed += 1
    else:
        failed += 1
        print("FAIL %s: got %r want %r" % (label, got, want))


k = base.object_kind
# the buoys on the map 2026-09-24, south of Vestbygd
check("FISHING BOUY", k("586707076", "FISHING BOUY"), "net_buoy")
check("padded name", k("586707076", "FISHING BOUY        "), "net_buoy")
check("NET MARK", k("412000001", "NET MARK 12"), "net_buoy")
check("BUOY", k("412000002", "BUOY 7"), "net_buoy")
check("lower case", k("412000003", "fishing net"), "net_buoy")
check("979 prefix, no name", k("979123456"), "net_buoy")
# a real vessel with the word in its name broadcasts a length
check("BUOY TENDER with length", k("366000001", "BUOY TENDER", 49.0), "vessel")
# names that merely contain the letters
check("FYRHOLM", k("257817500", "FYRHOLM", 21.0), "vessel")
check("BOUYGUES word boundary", k("227000001", "BOUYGUES"), "vessel")
check("ordinary ship", k("257047800", "FYRGLIMT"), "vessel")
check("no name", k("338123456"), "vessel")
# ITU-R M.585 formats
check("99 AtoN", k("992571234", "SOME LIGHT"), "aton")
check("00 base station", k("002570000"), "base_station")
check("111 SAR aircraft", k("111257001", "NOR-002"), "sar_aircraft")
check("970 SART", k("970123456"), "distress_beacon")
check("972 MOB", k("972123456"), "distress_beacon")
check("974 EPIRB", k("974123456"), "distress_beacon")
# message type wins
check("AtoN message", k("257000000", "X", None, "AidsToNavigationReport"), "aton")
check("base message", k("257000000", None, None, "BaseStationReport"), "base_station")
check("SAR message", k("257000000", None, None,
                       "StandardSearchAndRescueAircraftReport"), "sar_aircraft")

now = dt.datetime.now(dt.timezone.utc)
o = base.Observation(identity="586707076", source="live_track_ships",
                     observed_at=now, name="FISHING BOUY")
check("Observation.kind", o.kind, "net_buoy")
check("Observation.is_vessel buoy", o.is_vessel, False)
v = base.Observation(identity="257047800", source="live_track_ships",
                     observed_at=now, name="FYRGLIMT")
check("Observation.is_vessel ship", v.is_vessel, True)
check("OBJECT_KINDS covers the answers", set(base.OBJECT_KINDS) >= {
    "vessel", "net_buoy", "aton", "base_station", "sar_aircraft",
    "distress_beacon"}, True)

# the icon
check("netbuoy is a key", icons.valid_key("netbuoy"), True)
p = icons.icon_path("netbuoy")
check("netbuoy file exists", p is not None, True)
check("netbuoy weight", icons.weight_for("netbuoy", 300), icons.NETBUOY_WEIGHT)
for deg in (None, 0, 45, 185):
    for badge in (True, False):
        svg = icons.render(p, "netbuoy", deg, 64, "police", 0.47, badge)
        ET.fromstring(svg)
        check("paint kept deg=%s badge=%s" % (deg, badge), "#FA8072" in svg, True)
        check("no tone fill deg=%s badge=%s" % (deg, badge),
              icons.TONES["police"] in svg, False)
# a vessel icon that is not painted is still filled with its tone and
# decoloured (2026-09-28: cargo and the rest of the vessel palette now paint
# their own colours - icons.VESSEL_PAINTED - so this uses generic)
svg = icons.render(icons.icon_path("generic"), "generic", 30, 64, "police", 0.9, True)
check("unpainted vessel still toned", icons.TONES["police"] in svg, True)
check("generic is not painted", "generic" in icons.PAINTED, False)

# SAR aircraft: ITU-R M.585-8 seventh digit, 1 fixed-wing, 5 helicopter, optional
# the airframe is decided ONCE, in base.sar_airframe; the icon maps it (backlog 258)
check("111265103 fixed-wing", icons.pick_sar(base.sar_airframe("111265103")), "sarplane")
check("111265583 helicopter", icons.pick_sar(base.sar_airframe("111265583")), "sarheli")
check("111257001 unmarked -> helicopter (NOR-002 is one)", icons.pick_sar(base.sar_airframe("111257001")), "sarheli")
check("sar tone", icons.tone_for_kind("sar_aircraft"), "sar")
check("net buoy tone", icons.tone_for_kind("net_buoy"), "default")
check("sar weight", icons.weight_for("sarheli", None), icons.SMALLEST_AIRCRAFT_WEIGHT)
for deg in (None, 90):
    for badge in (True, False):
        h = icons.render(icons.icon_path("sarheli"), "sarheli", deg, 64, "sar", 0.47, badge)
        ET.fromstring(h)
        check("rotor animation survives render deg=%s badge=%s" % (deg, badge),
              '<animateTransform attributeName="transform" type="rotate" from="0 100 100"' in h, True)
        check("heli drawn orange deg=%s badge=%s" % (deg, badge), icons.TONES["sar"] in h, True)
        p = icons.render(icons.icon_path("sarplane"), "sarplane", deg, 64, "sar", 0.47, badge)
        ET.fromstring(p)
        check("plane has no animation deg=%s badge=%s" % (deg, badge), "animate" in p, False)

# --- backlog 258: map_layer (D10), object_ids (D11), one airframe decision ---
af = base.sar_airframe
check("airframe 111265103 fixed_wing", af("111265103"), "fixed_wing")
check("airframe 111265583 rotorcraft", af("111265583"), "rotorcraft")
check("airframe 111257001 unmarked rotorcraft", af("111257001"), "rotorcraft")
ml = base.map_layer
check("layer vessel water", ml("vessel", "257047800"), "water")
# a SAR BOAT has a ship MMSI: kind vessel, so it stays on the water (Lee)
check("SAR boat is a vessel", k("257123450", "RS 161 SAR"), "vessel")
check("SAR boat layer water", ml(k("257123450", "RS 161 SAR"), "257123450"), "water")
for kd in ("net_buoy", "aton", "base_station", "distress_beacon"):
    check("layer %s fixed" % kd, ml(kd, "979123456"), "fixed")
check("layer unknown kind fixed", ml("something_new", "1"), "fixed")
check("layer SAR heli air_low", ml("sar_aircraft", "111257001"), "air_low")
check("layer SAR plane air", ml("sar_aircraft", "111265103"), "air")
check("layer SAR message, ship MMSI -> heli", ml(k("257000000", None, None,
      "StandardSearchAndRescueAircraftReport"), "257000000"), "air_low")
for m in ("111265103", "111265583", "111257001", "111000000", "11126510", None):
    pair = (icons.pick_sar(af(m)), ml("sar_aircraft", m))
    check("icon and layer agree for %s" % m, pair in
          (("sarplane", "air"), ("sarheli", "air_low")), True)
# the rotor survives the new path
h = icons.render(icons.icon_path(icons.pick_sar(af("111257001"))), "sarheli",
                 None, 64, "sar", 0.47, False)
check("NOR-002 still gets the spinning rotor", "animateTransform" in h, True)

vi = base.valid_imo
check("imo valid int", vi(9543756), "9543756")
check("imo valid str", vi("9074729"), "9074729")
check("imo check digit fails", vi("9074728"), None)
check("imo nine digits (seen live 2026-09-24)", vi("101210706"), None)
check("imo six digits", vi(123456), None)
check("imo 0", vi(0), None)
check("imo 0000000", vi("0000000"), None)
check("imo None", vi(None), None)
check("imo bool", vi(True), None)
check("imo float", vi(9074729.0), None)
check("imo prefixed", vi("IMO9074729"), None)
check("imo padded", vi(" 9074729"), None)
check("imo non-ASCII digits", vi("\u0669\u0660\u0667\u0664\u0667\u0662\u0669"), None)

oi = base.object_ids
check("ids mmsi only", oi("257047800"), {"mmsi": "257047800"})
check("ids mmsi and imo", oi("257047800", 9074729),
      {"mmsi": "257047800", "imo": "9074729"})
check("ids bad imo dropped", oi("257047800", "101210706"), {"mmsi": "257047800"})
check("ids mmsi is a str", type(oi("257047800")["mmsi"]), str)
check("ids imo is a str", type(oi("257047800", 9074729)["imo"]), str)
check("ids int identity", oi(257047800), {"mmsi": "257047800"})
check("ids base station keeps its zeros", oi("002570000"), {"mmsi": "002570000"})
check("ids 8 digits dropped", oi("25704780"), {})
check("ids no identity", oi(None), {})
check("ids never registration", "registration" in oi("111265583", 9074729), False)

# --- net buoys point where they are going, at ANY speed; else EAST (Lee 2026-09-25) ---
bb = icons.buoy_bearing
check("buoy heading wins", bb(33, 200), (33.0, "heading"))
check("buoy course at any speed", bb(None, 200), (200.0, "course"))
check("buoy course 0 while drifting is north", bb(None, 0, 0.4), (0.0, "course"))
check("buoy course 0 at speed 0 is NO course (Lee 2026-09-29)", bb(None, 0, 0.0), (None, None))
check("buoy course 360 with no speed is NO course", bb(None, 360), (None, None))
check("buoy course 200 at speed 0 is used", bb(None, 200, 0.0), (200.0, "course"))
check("buoy nothing", bb(None, None), (None, None))
check("buoy rest direction is east", icons.BUOY_REST_DEG, 90)
check("vessels keep the 2 kn rule: below it a course is held, never basis course",
      icons.bearing(None, 200, 1.0, None), (200.0, "held"))
svg = icons.render(icons.icon_path("netbuoy"), "netbuoy", 90, 64, "default", 0.47, False)
ET.fromstring(svg)
check("an east-drawn fish keeps its paint", "#FA8072" in svg, True)

print("%d passed, %d failed" % (passed, failed))
sys.exit(1 if failed else 0)
