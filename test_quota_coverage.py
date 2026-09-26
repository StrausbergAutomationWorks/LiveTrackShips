"""Tests for the instance quota (item 253) and the coverage share (item 249).

Run: python test_quota_coverage.py   (here, or in the container via lts_boxtest.py)
Both modules are pure standard library and load by file path.
"""
import importlib.util
import json
import os
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
_PKG = pathlib.Path(__file__).parent / "custom_components" / "live_track_ships"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


allocate = _load("lts_quota", _PKG / "quota.py").allocate
cov = _load("lts_coverage", _PKG / "coverage.py")
passed = failed = 0


def check(label, got, want):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}"
          + ("" if ok else f"\n         got {got!r}\n         want {want!r}"))


print("=== quota: a quiet entry takes what it needs, the rest is shared ===")
# The 2026-09-24 shape: Chicagoland 30, BarentsWatch 620, Digitraffic 1,036.
check("30 / 620 / 1036 of 1500", allocate({"chi": 30, "bw": 620, "fi": 1036}, 1500),
      {"chi": 30, "bw": 620, "fi": 850})
check("two full entries split evenly", allocate({"a": 1000, "b": 1000}, 1500), {"a": 750, "b": 750})
check("remainder goes in entry_id order", allocate({"c": 1000, "a": 1000, "b": 1000}, 1000),
      {"a": 334, "b": 333, "c": 333})
check("everyone fits: each gets its demand", allocate({"a": 10, "b": 20}, 1500), {"a": 10, "b": 20})
check("one entry is capped at the total", allocate({"a": 3000}, 1500), {"a": 1500})
check("no entries", allocate({}, 1500), {})
check("zero demand gets zero", allocate({"a": 0, "b": 2000}, 1500), {"a": 0, "b": 1500})
check("negative demand treated as zero", allocate({"a": -5, "b": 10}, 1500), {"a": 0, "b": 10})
check("same demands, same answer", allocate({"x": 900, "y": 900, "z": 5}, 1500),
      allocate({"z": 5, "y": 900, "x": 900}, 1500))
worst = max(sum(allocate({str(i): d for i, d in enumerate(ds)}, 1500).values())
            for ds in ([1] * 7, [1500] * 7, [3, 1600, 17, 800], [0, 0], [499, 501, 500, 2]))
check("sum never exceeds the ceiling", worst <= 1500, True)
check("equal share guaranteed to a busy entry", allocate({"a": 5, "b": 2000, "c": 2000}, 1500)["b"], 748)

print("\n=== coverage: share of a circle outside an area ===")
square = {"type": "Polygon", "coordinates": [[[0, 50], [20, 50], [20, 70], [0, 70], [0, 50]]]}
check("circle well inside -> 0.0", cov.outside_share(60, 10, 50, square), 0.0)
edge = cov.outside_share(60, 20, 100, square)
check("circle centred on the east edge -> about half", 0.4 < edge < 0.6, True)
check("circle entirely outside -> 1.0", cov.outside_share(40, 10, 50, square), 1.0)
holed = {"type": "Polygon", "coordinates": [square["coordinates"][0],
                                            [[8, 58], [12, 58], [12, 62], [8, 62], [8, 58]]]}
check("a point in a hole is outside", cov.in_area(60, 10, holed), False)
check("unknown area -> None, never a gap", cov.outside_share(60, 10, 50, None), None)
check("wrong geometry type -> None", cov.outside_share(60, 10, 50, {"type": "Point"}), None)
multi = {"type": "MultiPolygon", "coordinates": [square["coordinates"],
         [[[30, 50], [40, 50], [40, 60], [30, 60], [30, 50]]]]}
check("second polygon of a multipolygon counts", cov.in_area(55, 35, multi), True)

real = r"%USERPROFILE%\bin\bw_openaisarea.json"
if os.path.exists(real):
    print("\n=== coverage against BarentsWatch's real published area (saved 2026-09-23) ===")
    area = json.load(open(real, encoding="utf-8"))
    osl = cov.outside_share(59.5, 10.5, 30, area)
    check("Oslofjord, 30 km -> fully covered", osl, 0.0)
    oh = cov.outside_share(56.7325, 10.3729, 380, area)
    print(f"  info Oslo-Hamburg entry, 380 km -> {oh:.0%} outside")
    check("Oslo-Hamburg entry warns (>= 5%)", oh >= 0.05, True)
    sk = cov.outside_share(57.72, 10.58, 20, area)
    check("Skagen, 20 km -> mostly outside", sk > 0.5, True)
else:
    print("  skip real BarentsWatch area not on this machine")

# -- item 264: the user's slider can only LOWER the instance ceiling ---------
eff = _load("lts_quota_eff", _PKG / "quota.py").effective_ceiling
check("264: nobody set it -> the constant", eff([], 2500, 100), 2500)
check("264: None ignored", eff([None, None], 2500, 100), 2500)
check("264: the LOWEST setting wins", eff([1200, 300, 2500], 2500, 100), 300)
check("264: never above the constant", eff([9999], 2500, 100), 2500)
check("264: never below the floor", eff([5], 2500, 100), 100)
check("264: a slider float is taken as int", eff([700.0], 2500, 100), 700)
check("264: junk ignored, not read as zero", eff(["abc", 800], 2500, 100), 800)
check("264: a bool is not a number here", eff([True, 900], 2500, 100), 900)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
