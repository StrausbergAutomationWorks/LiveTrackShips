"""Tests for centre-and-radius geometry. Run: python test_geo.py

⚠ Tests ALL the cases, not a sample: equator, mid-latitude, high latitude,
pole, both antimeridian directions, and the box-vs-circle corner gap.
"""
import math, sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent
                       / "custom_components" / "live_track_ships"))
import geo as G

passed = failed = 0


def check(label, got, want):
    global passed, failed
    if got == want:
        passed += 1
        print(f"  ok   {label}")
    else:
        failed += 1
        print(f"  FAIL {label}\n         got  {got!r}\n         want {want!r}")


HOME_LAT, HOME_LON = 41.8995, -87.9403      # Elmhurst

print("=== distance ===")
# Measured earlier in the session: Elmhurst to the Chicago River is 24-27 km.
d = G.distance_km(HOME_LAT, HOME_LON, 41.8885, -87.6340)
check("Elmhurst -> Chicago River is 25-26 km", 25 <= d <= 26, True)
check("zero distance to self",
      round(G.distance_km(HOME_LAT, HOME_LON, HOME_LAT, HOME_LON), 6), 0.0)

print("\n=== validation ===")
for bad in (0.0, 0.9, 500.1, 10000):
    try:
        G.validate_radius(bad)
        check(f"radius {bad} rejected", False, True)
    except G.RadiusError:
        check(f"radius {bad} rejected", True, True)
check("radius 50 accepted", G.validate_radius(50), 50.0)
check("default is inside the range",
      G.MIN_RADIUS_KM <= G.DEFAULT_RADIUS_KM <= G.MAX_RADIUS_KM, True)

print("\n=== box covers the circle ===")
boxes = G.bounding_boxes(HOME_LAT, HOME_LON, 50)
check("one box for a normal circle", len(boxes), 1)
(n, w), (s, e) = boxes[0]
# ⚠ every point exactly `radius` away, in all directions, must be inside
edge_ok = True
for bearing in range(0, 360, 15):
    br = math.radians(bearing)
    dlat = (50.0 / G.KM_PER_DEGREE_LAT) * math.cos(br)
    dlon = (50.0 / (G.KM_PER_DEGREE_LAT
                    * math.cos(math.radians(HOME_LAT)))) * math.sin(br)
    plat, plon = HOME_LAT + dlat, HOME_LON + dlon
    if not (s <= plat <= n and w <= plon <= e):
        edge_ok = False
check("all 24 compass edge points fall inside the box", edge_ok, True)

print("\n=== box is BIGGER than the circle ===")
# a corner of the box is radius*sqrt(2) away and must NOT count as in-radius
check("box corner is outside the radius",
      G.within_radius(HOME_LAT, HOME_LON, 50, n, w), False)
check("centre is inside the radius",
      G.within_radius(HOME_LAT, HOME_LON, 50, HOME_LAT, HOME_LON), True)
check("a point at 49 km is inside",
      G.within_radius(HOME_LAT, HOME_LON, 50, HOME_LAT + 0.44, HOME_LON), True)
check("a point at 60 km is outside",
      G.within_radius(HOME_LAT, HOME_LON, 50, HOME_LAT + 0.54, HOME_LON), False)

print("\n=== longitude span grows towards the poles ===")
spans = {}
for lat in (0.0, 41.9, 60.0, 80.0):
    (bn, bw), (bs, be) = G.bounding_boxes(lat, 0.0, 500)[0]
    spans[lat] = round(be - bw, 2)
    print(f"  lat {lat:>5}: longitude span {spans[lat]:>7} degrees")
check("span at the equator is ~9 degrees", 8.9 <= spans[0.0] <= 9.1, True)
check("span grows with latitude",
      spans[0.0] < spans[41.9] < spans[60.0] < spans[80.0], True)

print("\n=== poles ===")
polar = G.bounding_boxes(89.9, 12.0, 100)
check("near-pole circle returns ONE box", len(polar), 1)
check("near-pole box spans all longitudes",
      [polar[0][0][1], polar[0][1][1]], [-180.0, 180.0])
check("north edge is clamped to 90", polar[0][0][0], 90.0)
south = G.bounding_boxes(-89.95, 0.0, 100)
check("south pole also spans all longitudes",
      [south[0][0][1], south[0][1][1]], [-180.0, 180.0])

print("\n=== antimeridian ===")
# ⚠ Nothing in Chicagoland exercises this. That is exactly why it is tested.
east_side = G.bounding_boxes(0.0, 178.0, 500)
check("circle crossing +180 splits in two", len(east_side), 2)
check("first piece ends at +180", east_side[0][1][1], 180.0)
check("second piece starts at -180", east_side[1][0][1], -180.0)

west_side = G.bounding_boxes(0.0, -178.0, 500)
check("circle crossing -180 splits in two", len(west_side), 2)
check("a piece ends at +180", west_side[0][1][1], 180.0)

check("far from the antimeridian stays one box",
      len(G.bounding_boxes(0.0, 0.0, 500)), 1)

print("\n=== nearest, and the vessel ceiling ===")
vessels = [
    ("far",    HOME_LAT + 0.30, HOME_LON, None),
    ("near",   HOME_LAT + 0.01, HOME_LON, None),
    ("middle", HOME_LAT + 0.10, HOME_LON, None),
]
got = [v[1] for v in G.nearest(HOME_LAT, HOME_LON, vessels, 3)]
check("sorted nearest first", got, ["near", "middle", "far"])
check("limit truncates",
      [v[1] for v in G.nearest(HOME_LAT, HOME_LON, vessels, 2)],
      ["near", "middle"])
check("limit larger than input is safe",
      len(G.nearest(HOME_LAT, HOME_LON, vessels, 99)), 3)
check("empty input is safe", G.nearest(HOME_LAT, HOME_LON, [], 5), [])

print("\n=== item 267: the edge hold ===")
KM = 1 / 111.195                       # degrees of latitude per km
inc = ("inc", HOME_LAT + 10.0 * KM, HOME_LON, None)
close = ("close", HOME_LAT + 9.5 * KM, HOME_LON, None)
clear = ("clear", HOME_LAT + 8.5 * KM, HOME_LON, None)
check("HOLD_FRACTION is 5%", G.HOLD_FRACTION, 0.05)
check("no hold: the nearer newcomer wins",
      [v[1] for v in G.nearest(HOME_LAT, HOME_LON, [inc, close], 1)], ["close"])
check("hold 1 km: a newcomer 0.5 km nearer does NOT displace",
      [v[1] for v in G.nearest(HOME_LAT, HOME_LON, [inc, close], 1,
                               held={"inc"}, hold_km=1.0)], ["inc"])
check("hold 1 km: a newcomer 1.5 km nearer DOES",
      [v[1] for v in G.nearest(HOME_LAT, HOME_LON, [inc, clear], 1,
                               held={"inc"}, hold_km=1.0)], ["clear"])
got = G.nearest(HOME_LAT, HOME_LON, [inc, close], 1, held={"inc"}, hold_km=1.0)
check("the returned distance is the TRUE one", round(got[0][0], 2), 10.0)
check("hold never changes the count",
      len(G.nearest(HOME_LAT, HOME_LON, [inc, close, clear], 2,
                    held={"inc"}, hold_km=5.0)), 2)
check("hold 0 is the old ordering",
      [v[1] for v in G.nearest(HOME_LAT, HOME_LON, [inc, close, clear], 3,
                               held={"inc"}, hold_km=0.0)],
      ["clear", "close", "inc"])
check("hold_rank: held", G.hold_rank(10.0, "a", {"a"}, 2.0), 8.0)
check("hold_rank: not held", G.hold_rank(10.0, "b", {"a"}, 2.0), 10.0)

print("\n=== ceiling is not a count ===")
check("MAX_VESSELS is a ceiling above the default",
      G.MAX_VESSELS > G.DEFAULT_MAX_VESSELS, True)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
