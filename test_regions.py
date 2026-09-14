"""Tests for the region registry. Run: python test_regions.py"""
import sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent
                       / "custom_components" / "live_track_ships"))
import regions as R

passed = failed = 0


def check(label, got, want):
    global passed, failed
    if got == want:
        passed += 1
        print(f"  ok   {label}")
    else:
        failed += 1
        print(f"  FAIL {label}\n         got  {got!r}\n         want {want!r}")


print("=== registry ===")
check("chicagoland is the default", R.DEFAULT_REGION, "chicagoland")
check("world is registered", "world" in R.REGIONS, True)
check("chicagoland has one box", len(R.REGIONS["chicagoland"].boxes), 1)

print("\n=== boxes_for ===")
check("single region -> one box",
      R.boxes_for(["chicagoland"]), [[[42.60, -88.40], [41.30, -86.20]]])
check("two regions -> two boxes",
      len(R.boxes_for(["chicagoland", "great_lakes"])), 2)
check("duplicate ids collapse",
      len(R.boxes_for(["chicagoland", "chicagoland"])), 1)

try:
    R.boxes_for(["atlantis"])
    check("unknown id raises", False, True)
except KeyError:
    check("unknown id raises", True, True)

print("\n=== antimeridian ===")
# ⚠ Nothing in Chicagoland exercises this. That is the point of testing it.
bering = ((66.0, 170.0), (60.0, -168.0))
split = R.split_antimeridian(bering)
check("crossing box splits in two", len(split), 2)
check("first piece ends at +180", split[0][1][1], 180.0)
check("second piece starts at -180", split[1][0][1], -180.0)
check("normal box is untouched",
      len(R.split_antimeridian(((42.6, -88.4), (41.3, -86.2)))), 1)
check("a box ending exactly at 180 does not split",
      len(R.split_antimeridian(((10.0, 170.0), (-10.0, 180.0)))), 1)

print("\n=== rates ===")
check("measured region returns a number",
      R.estimated_rate(["great_lakes"]), 1.0)
check("sum of two measured regions",
      round(R.estimated_rate(["chicagoland", "great_lakes"]), 2), 1.2)

R.register(R.Region(id="_unmeasured", name="x",
                    boxes=(((1.0, 1.0), (0.0, 2.0)),)))
check("any unmeasured region -> None",
      R.estimated_rate(["great_lakes", "_unmeasured"]), None)

print("\n=== validation ===")
for bad, why in [
    ((((91.0, 0.0), (0.0, 1.0)),), "latitude over 90"),
    ((((10.0, -181.0), (0.0, 1.0)),), "longitude under -180"),
]:
    try:
        R.register(R.Region(id="_bad" + why, name="x", boxes=bad))
        check(why + " rejected", False, True)
    except ValueError:
        check(why + " rejected", True, True)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
