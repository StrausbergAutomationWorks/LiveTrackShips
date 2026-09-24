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
# a vessel icon is still filled with its tone and decoloured
svg = icons.render(icons.icon_path("cargo"), "cargo", 30, 64, "police", 0.9, True)
check("vessel still toned", icons.TONES["police"] in svg, True)

# SAR aircraft: ITU-R M.585-8 seventh digit, 1 fixed-wing, 5 helicopter, optional
check("111265103 fixed-wing", icons.pick_sar("111265103"), "sarplane")
check("111265583 helicopter", icons.pick_sar("111265583"), "sarheli")
check("111257001 unmarked -> helicopter (NOR-002 is one)", icons.pick_sar("111257001"), "sarheli")
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

print("%d passed, %d failed" % (passed, failed))
sys.exit(1 if failed else 0)
