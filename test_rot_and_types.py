"""Tests for the rate-of-turn decode and the ITU type table.

Run: python test_rot_and_types.py

⚠ WHY THIS FILE EXISTS. Both things under test are one-line lookups that were
wrong in shipped code for days, silently, because nothing exercised the edges.
The ROT sentinel list lived in four places in three different states and
published +127 as "degrees per second"; the type table did not exist and type 0
was being counted as a real type. Edges, not the happy path, are the point.
"""
import importlib.util
import sys
import pathlib

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ⚠ LOADED BY FILE PATH, NOT AS A PACKAGE, DELIBERATELY. Importing
# `live_track_ships.anything` executes the package __init__, which imports
# homeassistant at module level - and homeassistant is NOT installed on this
# machine, under any interpreter (measured 2026-09-17: four venvs in bin\, none
# has it). So every other test file in this repo currently fails at the import
# line before running a single check. Both modules under test import nothing
# but the standard library, so they load standalone.
_PKG = pathlib.Path(__file__).parent / "custom_components" / "live_track_ships"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    # ⚠ REGISTER BEFORE EXECUTING. @dataclass looks its own class up in
    # sys.modules while the module body is still running, and an unregistered
    # module makes it fail with an opaque AttributeError on NoneType.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


rot_to_dps = _load("lts_base", _PKG / "sources" / "base.py").rot_to_dps
label_for = _load("lts_ship_types", _PKG / "ship_types.py").label_for

passed = failed = 0


def check(label, got, want):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}"
          + ("" if ok else f"\n         got {got!r}\n         want {want!r}"))


print("=== rate of turn: the three sentinels, SYMMETRICALLY ===")
check("-128 no information -> None", rot_to_dps(-128), None)
check("-127 saturated port -> None", rot_to_dps(-127), None)
# ⚠ THIS IS THE ONE THAT SHIPPED WRONG. +127 was published as a reading, and
# it is the COMMONER of the two: 18 at +127 against 12 at -127 in one pull of
# 1,063 vessels. 127 "degrees per second" is 21 revolutions a minute.
check("+127 saturated starboard -> None", rot_to_dps(127), None)
check("None -> None", rot_to_dps(None), None)

print("\n=== the decode is not a pass-through ===")
# raw = 4.733 * sqrt(deg/min), so raw 11 is ~5.4 deg/min, not 11 of anything.
check("raw 11 -> 0.09 deg/s", round(rot_to_dps(11), 2), 0.09)
check("raw -11 -> -0.09 deg/s", round(rot_to_dps(-11), 2), -0.09)
check("raw 0 -> 0.0", rot_to_dps(0), 0.0)
check("sign is symmetric", rot_to_dps(50), -rot_to_dps(-50))
check("monotonic in magnitude", rot_to_dps(20) > rot_to_dps(10), True)
# ⚠ The encoding's ceiling. 126 is the largest non-sentinel value and must
# still land somewhere physically sane rather than in the hundreds.
check("raw 126 stays under 12 deg/s", 11.0 < rot_to_dps(126) < 12.0, True)

print("\n=== junk in, None out ===")
check("out of range high", rot_to_dps(200), None)
check("out of range low", rot_to_dps(-200), None)
check("not a number", rot_to_dps("abc"), None)
check("float arrives from JSON", rot_to_dps(11.0), rot_to_dps(11))


print("\n=== ITU type: the sentinel and the reserved ranges are UNLABELLED ===")
# ⚠ 147 of 255 reported types are 0. A label here would be a placeholder
# indistinguishable from a reading.
check("0 unavailable -> None", label_for(0), None)
# ⚠ 2026-09-24: 5, 19, 38 and 39 were "reserved -> None" here. The USCG AIS
# Encoding Guide (26-07-01) defines them; codes it leaves out stay unlabelled.
check("5 USCG -> Buoy tender", label_for(5), "Buoy tender")
check("19 USCG -> Support vessel", label_for(19), "Support vessel")
check("38 USCG -> Trawler", label_for(38), "Trawler")
check("39 USCG -> Patrol vessel", label_for(39), "Patrol vessel")
check("86 USCG -> ATB", label_for(86), "Articulated tug and barge")
check("8 undefined -> None", label_for(8), None)
check("10 undefined -> None", label_for(10), None)
check("15 undefined -> None", label_for(15), None)
check("16 undefined -> None", label_for(16), None)
check("81 hazard digit -> decade only", label_for(81), "Tanker")
check("None -> None", label_for(None), None)
check("100 out of range -> None", label_for(100), None)
check("-1 out of range -> None", label_for(-1), None)

print("\n=== ITU type: the standalone codes 30-59 ===")
for code, want in ((30, "Fishing"), (31, "Towing"), (36, "Sailing"),
                   (37, "Pleasure craft"), (50, "Pilot vessel"),
                   (51, "Search and rescue"), (52, "Tug"),
                   (55, "Law enforcement")):
    check(f"{code} -> {want}", label_for(code), want)

print("\n=== ITU type: the decade rule, unit digit NOT decoded ===")
for code, want in ((20, "Wing in ground effect"), (49, "High speed craft"),
                   (60, "Passenger"), (69, "Passenger"), (70, "Cargo"),
                   (74, "Cargo"), (80, "Tanker"), (99, "Other")):
    check(f"{code} -> {want}", label_for(code), want)
check("a string code still resolves", label_for("70"), "Cargo")

print("\n=== every type MEASURED on real traffic resolves ===")
# The ten real types seen over five days, 291 vessels. If any of these come
# back None the table has a hole where the traffic actually is.
measured = [60, 36, 37, 70, 99, 69, 31, 52, 50, 51]
check("all ten measured types labelled",
      [c for c in measured if label_for(c) is None], [])

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
