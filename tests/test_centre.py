"""The setup dialog's map marker (centre.py): converted to the two numbers the
entry stores, range-checked, and refused when it is not on the globe.

Backlog 317 and Ships item 268. Home Assistant is not needed: the package is
stubbed so its __init__ is not run, and centre.py imports only const_flow.
"""
import pathlib
import sys
import types

_COMP = pathlib.Path(__file__).resolve().parents[1] / "custom_components" / "live_track_ships"
_pkg = types.ModuleType("live_track_ships")
_pkg.__path__ = [str(_COMP)]
sys.modules["live_track_ships"] = _pkg

from live_track_ships.centre import (                                   # noqa: E402
    ERROR_INVALID_LOCATION, from_form, to_form)
from live_track_ships.const_flow import (                               # noqa: E402
    CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE, CONF_RADIUS_KM)

passed = failed = 0


def check(label, got, want=True):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}"
          + ("" if ok else f"   got {got!r} want {want!r}"))


print("=== the marker starts at home, or at a centre already given ===")
check("no centre -> home", to_form({}, 52.37, 4.90), {"latitude": 52.37, "longitude": 4.90})
check("a centre -> that centre", to_form({CONF_LATITUDE: -33.86, CONF_LONGITUDE: 151.2}, 52.37, 4.90),
      {"latitude": -33.86, "longitude": 151.2})

print("\n=== the marker becomes the two stored keys ===")
v, err = from_form({CONF_LOCATION: {"latitude": 60.17, "longitude": 24.95}, CONF_RADIUS_KM: 50})
check("no error", err, None)
check("latitude stored", v[CONF_LATITUDE], 60.17)
check("longitude stored", v[CONF_LONGITUDE], 24.95)
check("location not stored", CONF_LOCATION in v, False)
check("other fields pass through", v[CONF_RADIUS_KM], 50)

print("\n=== item 268: a western or southern centre keeps its sign ===")
v, err = from_form({CONF_LOCATION: {"latitude": 33.73, "longitude": -118.27}})
check("Port of Los Angeles stays at -118.27", v[CONF_LONGITUDE], -118.27)
v, err = from_form({CONF_LOCATION: {"latitude": -34.6, "longitude": -58.37}})
check("Buenos Aires stays south and west", (v[CONF_LATITUDE], v[CONF_LONGITUDE]), (-34.6, -58.37))

print("\n=== a marker on a second copy of the world folds back ===")
v, err = from_form({CONF_LOCATION: {"latitude": 10.0, "longitude": 190.0}})
check("190 -> -170", round(v[CONF_LONGITUDE], 6), -170.0)
v, err = from_form({CONF_LOCATION: {"latitude": 10.0, "longitude": -200.0}})
check("-200 -> 160", round(v[CONF_LONGITUDE], 6), 160.0)
check("180 is kept", from_form({CONF_LOCATION: {"latitude": 0, "longitude": 180.0}})[0][CONF_LONGITUDE], 180.0)

print("\n=== refused: not on the globe, or not a point ===")
for label, ui in (
        ("latitude 141.9 (the selector passed it on HA 2026.10.2)", {CONF_LOCATION: {"latitude": 141.9, "longitude": 0}}),
        ("latitude -90.5", {CONF_LOCATION: {"latitude": -90.5, "longitude": 0}}),
        ("NaN", {CONF_LOCATION: {"latitude": float("nan"), "longitude": 0}}),
        ("absurd longitude", {CONF_LOCATION: {"latitude": 0, "longitude": 1e9}}),
        ("missing longitude", {CONF_LOCATION: {"latitude": 1.0}}),
        ("text", {CONF_LOCATION: {"latitude": "north", "longitude": 0}}),
        ("no location at all", {CONF_RADIUS_KM: 50}),
        ("location not a dict", {CONF_LOCATION: "41.9,-87.9"})):
    check(label, from_form(ui), (None, ERROR_INVALID_LOCATION))

print("\n=== a radius inside the location is ignored ===")
v, err = from_form({CONF_LOCATION: {"latitude": 1.0, "longitude": 2.0, "radius": 999}, CONF_RADIUS_KM: 20})
check("radius_km kept, location radius dropped", (v[CONF_RADIUS_KM], "radius" in v), (20, False))

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
