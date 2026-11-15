"""Tests for VesselStore. Run: python test_store.py"""
import datetime as dt
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "custom_components"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from live_track_ships.store import (                        # noqa: E402
    VesselStore, DEFAULT_BERTHED_STALE_AFTER_S, DEFAULT_STALE_AFTER_S)
from live_track_ships.sources.base import Observation       # noqa: E402

passed = failed = 0
T0 = dt.datetime(2026, 9, 8, 12, 0, 0, tzinfo=dt.timezone.utc)
LAT, LON = 41.8995, -87.9403          # Elmhurst


def check(label, got, want):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}"
          + ("" if ok else f"\n         got {got!r}\n         want {want!r}"))


def obs(ident, lat, lon, secs=0, nav=None, kmh=None):
    return Observation(identity=ident, source="live_track_ships",
                       observed_at=T0 + dt.timedelta(seconds=secs),
                       latitude=lat, longitude=lon,
                       nav_status=nav, speed_kmh=kmh)


print("=== ⚠ the CIRCLE is enforced, not the box ===")
s = VesselStore(LAT, LON, radius_km=50, max_vessels=100)
check("inside is kept", s.add(obs("a", LAT + 0.1, LON)), True)
# A box corner is radius*sqrt(2) out. 50 km box -> ~0.45 deg lat and lon.
check("box CORNER is rejected",
      s.add(obs("corner", LAT + 0.44, LON + 0.59)), False)
check("far away is rejected", s.add(obs("far", 0.0, 0.0)), False)
check("positionless is rejected",
      s.add(Observation(identity="np", source="s", observed_at=T0)), False)
check("only the inside vessel is stored", len(s), 1)

print("\n=== ⚠ eviction is by TIME, never by count ===")
s2 = VesselStore(LAT, LON, 50, 100, stale_after_s=600)
s2.add(obs("fresh", LAT + 0.01, LON, 0))
s2.add(obs("quiet", LAT + 0.02, LON, -1200))
check("both stored", len(s2), 2)
check("one pruned", s2.prune(T0), 1)
check("the quiet one is gone", len(s2), 1)
check("the fresh one survives", s2.published()[0].identity, "fresh")

print("\n=== ⚠ a vessel silent for 20 minutes is NOT gone ===")
# Measured: 10 of 48 vessels appeared ONCE in 20 minutes.
s3 = VesselStore(LAT, LON, 50, 100)          # default 1800 s
s3.add(obs("once", LAT + 0.01, LON, -1200))
check("still held at 20 minutes", s3.prune(T0), 0)

print("\n=== ⚠ the cap keeps the NEAREST, deterministically ===")
s4 = VesselStore(LAT, LON, 50, max_vessels=3)
for i in range(8):
    s4.add(obs(f"v{i}", LAT + 0.01 * (i + 1), LON))
out = s4.published()
check("capped to max_vessels", len(out), 3)
check("nearest first", [o.identity for o in out], ["v0", "v1", "v2"])
check("truncation is REPORTED", s4.truncated_from, 8)
check("same input, same output", [o.identity for o in s4.published()],
      ["v0", "v1", "v2"])

print("\n=== truncated_from is None when nothing was dropped ===")
s5 = VesselStore(LAT, LON, 50, max_vessels=10)
s5.add(obs("only", LAT + 0.01, LON))
s5.published()
check("no truncation reported", s5.truncated_from, None)

print("\n=== the previous fix rides along ===")
s6 = VesselStore(LAT, LON, 50, 100)
s6.add(obs("m", LAT + 0.01, LON, 0))
s6.add(obs("m", LAT + 0.02, LON, 60))
p = s6.published()[0]
check("published is the NEWEST", round(p.latitude, 4), round(LAT + 0.02, 4))
check("previous rides along", round(p.extra["previous_latitude"], 4),
      round(LAT + 0.01, 4))
check("measured gap", p.extra["segment_duration_s"], 60.0)

print("\n=== a first sighting publishes with no previous ===")
s7 = VesselStore(LAT, LON, 50, 100)
s7.add(obs("new", LAT + 0.01, LON))
check("published", len(s7.published()), 1)
check("⚠ no previous fields", "previous_latitude" in s7.published()[0].extra,
      False)


print("\n=== ⚠ a vessel that DECLARES it is moored is kept far longer ===")
# Measured: declared anchored/moored gaps run to 714 s worst case with a 180 s
# median - the ITU-R M.1371 3-minute interval. A single window would delete a
# tug tied up overnight and re-create it all night.
check("moored is berthed", VesselStore.is_berthed(obs("x", 0, 0, nav=5)), True)
check("at anchor is berthed", VesselStore.is_berthed(obs("x", 0, 0, nav=1)),
      True)
check("under way is NOT berthed",
      VesselStore.is_berthed(obs("x", 0, 0, nav=0)), False)
check("⚠ a declared status is BELIEVED over slow speed",
      VesselStore.is_berthed(obs("x", 0, 0, nav=0, kmh=0.1)), False)
check("no status falls back to speed",
      VesselStore.is_berthed(obs("x", 0, 0, kmh=0.1)), True)
check("no status, moving",
      VesselStore.is_berthed(obs("x", 0, 0, kmh=20.0)), False)
check("⚠ nothing to go on is NOT berthed",
      VesselStore.is_berthed(obs("x", 0, 0)), False)

s8 = VesselStore(LAT, LON, 50, 1000)
s8.add(obs("moored", LAT + 0.01, LON, -7200, nav=5))     # 2 h old
s8.add(obs("underway", LAT + 0.02, LON, -7200, nav=0))   # 2 h old
check("both stored", len(s8), 2)
check("⚠ only the under-way one is evicted", s8.prune(T0), 1)
check("the moored vessel survives",
      [o.identity for o in s8.published()], ["moored"])

s9 = VesselStore(LAT, LON, 50, 1000)
s9.add(obs("moored", LAT + 0.01, LON, -DEFAULT_BERTHED_STALE_AFTER_S - 60,
           nav=5))
check("⚠ even a moored vessel goes eventually", s9.prune(T0), 1)

print("\n=== ⚠ 15 is the UNDEFINED sentinel, never 'not moored' ===")
# It is mapped to None upstream, so it reaches the store as no status at all.
check("None status + slow = berthed",
      VesselStore.is_berthed(obs("x", 0, 0, nav=None, kmh=0.0)), True)

print("\n=== the cap is a CEILING, not a display limit ===")
s10 = VesselStore(LAT, LON, 50, max_vessels=1000)
for i in range(200):
    s10.add(obs(f"n{i}", LAT + 0.0001 * i, LON))
check("200 vessels are all published", len(s10.published()), 200)
check("no truncation reported", s10.truncated_from, None)

print("\n=== item 267: the edge hold at the max_vessels cut ===")
KM = 1 / 111.195
s11 = VesselStore(LAT, LON, 50, max_vessels=2)   # hold = 2.5 km
check("hold_km is 5% of the radius", s11.hold_km, 2.5)
s11.add(obs("a", LAT + 5 * KM, LON))
s11.add(obs("b", LAT + 20 * KM, LON))
check("first pass: a, b", [o.identity for o in s11.published()], ["a", "b"])
s11.add(obs("c", LAT + 19 * KM, LON))          # 1 km nearer than b
check("c 1 km nearer than b: b KEEPS its place",
      [o.identity for o in s11.published()], ["a", "b"])
check("a second call gives the same list (the sensor calls it too)",
      [o.identity for o in s11.published()], ["a", "b"])
check("truncation still reported", s11.truncated_from, 3)
s11.add(obs("d", LAT + 16 * KM, LON))          # 4 km nearer than b
check("d 4 km nearer: b goes, d comes in",
      [o.identity for o in s11.published()], ["a", "d"])
s11.add(obs("b", LAT + 20 * KM, LON, 30))      # b heard again, same place
check("b, no longer shown, gets no hold back: c and b stay out",
      [o.identity for o in s11.published()], ["a", "d"])
s12 = VesselStore(LAT, LON, 50, max_vessels=2)
s12.add(obs("a", LAT + 5 * KM, LON))
s12.add(obs("b", LAT + 20 * KM, LON))
s12.add(obs("c", LAT + 19 * KM, LON))
check("⚠ a FRESH store holds nothing: nearest two",
      [o.identity for o in s12.published()], ["a", "c"])

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
