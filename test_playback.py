"""Tests for segment tracking. Run: python test_playback.py

⚠ The test that matters most is that a time PAST the end of a segment does not
extrapolate. That is the failure this module exists to prevent and it would be
invisible in normal operation.

⚠ The SECOND most important is that the published fix is the NEWEST one. An
earlier version published a delayed fix, which on a card that cannot animate is
strictly worse than publishing nothing special.
"""
import datetime as dt
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent / "custom_components"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from live_track_ships.playback import Track, Segment        # noqa: E402
from live_track_ships.sources.base import Observation       # noqa: E402

passed = failed = 0
T0 = dt.datetime(2026, 9, 8, 12, 0, 0, tzinfo=dt.timezone.utc)


def check(label, got, want):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}"
          + ("" if ok else f"\n         got {got!r}\n         want {want!r}"))


def obs(secs, lat, lon):
    return Observation(identity="123456789", source="live_track_ships",
                       observed_at=T0 + dt.timedelta(seconds=secs),
                       latitude=lat, longitude=lon)


print("=== ⚠ the NEWEST fix is published, nothing is held back ===")
t = Track("123456789")
t.add(obs(0, 41.0, -87.0))
check("first sighting is the newest fix", t.current.latitude, 41.0)
check("no segment yet", t.segment, None)
p = t.publish()
check("published at its real position", (p.latitude, p.longitude),
      (41.0, -87.0))
check("⚠ no previous fields on a first sighting",
      "previous_latitude" in p.extra, False)

t.add(obs(100, 41.0, -86.0))
p = t.publish()
check("published is the NEWEST, not the previous",
      (p.latitude, p.longitude), (41.0, -86.0))
check("observed_at is the newest fix's time",
      p.observed_at, T0 + dt.timedelta(seconds=100))
check("position_source stays observed", p.position_source, "observed")

print("\n=== the previous fix rides along for the consumer ===")
check("previous_latitude", p.extra["previous_latitude"], 41.0)
check("previous_longitude", p.extra["previous_longitude"], -87.0)
check("previous_observed_at", p.extra["previous_observed_at"], T0)
check("segment_duration_s is the MEASURED gap",
      p.extra["segment_duration_s"], 100.0)

print("\n=== ⚠⚠ IT MUST NOT EXTRAPOLATE ===")
seg = t.segment
check("midpoint", seg.position_at(T0 + dt.timedelta(seconds=50)),
      (41.0, -86.5))
check("far past the end stays AT the end",
      seg.position_at(T0 + dt.timedelta(seconds=100000)), (41.0, -86.0))
check("before the start stays AT the start",
      seg.position_at(T0 - dt.timedelta(seconds=5000)), (41.0, -87.0))

print("\n=== ⚠ duplicates and out-of-order fixes ===")
t2 = Track("999")
t2.add(obs(0, 10.0, 10.0))
t2.add(obs(60, 10.0, 11.0))
t2.add(obs(60, 99.0, 99.0))
check("same-instant duplicate ignored", t2.current.latitude, 10.0)
t2.add(obs(30, 50.0, 50.0))
check("older fix ignored", t2.current.longitude, 11.0)

print("\n=== stationary vessels ===")
t3 = Track("555")
t3.add(obs(0, 5.0, 5.0))
t3.add(obs(180, 5.0, 5.0))
check("recognised as stationary", t3.segment.is_stationary, True)
check("still publishes the newest fix", t3.publish().latitude, 5.0)
check("previous fields still present",
      t3.publish().extra["previous_latitude"], 5.0)

print("\n=== degenerate cases ===")
t4 = Track("777")
t4.add(obs(0, 1.0, 1.0))
t4.add(obs(0, 2.0, 2.0))
check("duplicate instant leaves one fix", t4.segment, None)
t5 = Track("888")
t5.add(Observation(identity="888", source="s", observed_at=T0))
t5.add(obs(60, 3.0, 3.0))
check("positionless previous -> no previous fields",
      "previous_latitude" in t5.publish().extra, False)
check("but the newest fix is still published", t5.publish().latitude, 3.0)
check("empty track publishes nothing", Track("0").publish(), None)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
