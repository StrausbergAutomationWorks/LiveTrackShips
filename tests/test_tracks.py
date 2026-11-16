"""Vessel tracks (backlog 348): thinning, the window, the cap, the file, the hours rule, the address and the
attribute. Runs inside the HA container: python lts_boxtest_clone.py test_tracks.py"""
import asyncio
import datetime as dt
import json
import os
import pathlib
import sys
import tempfile
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "custom_components"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from live_track_ships.tracks import (                       # noqa: E402
    DEFAULT_HOURS, MAX_HOURS, MAX_QUIET_S, MIN_GAP_S, TrackBook, _make_view, distance_m, track_url, valid_hours)

passed = failed = 0


def check(label, got, want=True):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}" + ("" if ok else f"\n         got {got!r}\n         want {want!r}"))


class Clock:
    def __init__(self, t=1_800_000_000.0):
        self.t = t

    def __call__(self):
        return self.t


def book(clock=None, path=None):
    return TrackBook(path or os.path.join(tempfile.mkdtemp(), "t.json"), clock=clock or Clock())


M = "366053209"
LAT, LON = 41.88, -87.60
DLAT_100M = 100 / 111_195          # about 100 m north
DLAT_5M = 5 / 111_195

print("=== the address ===")
check("an MMSI", track_url(M), "/api/live_track_ships/track/366053209")
check("a number given as int", track_url(366053209), "/api/live_track_ships/track/366053209")
check("letters: none", track_url("abc"), None)
check("ten digits: none", track_url("1234567890"), None)
check("nothing: none", track_url(None), None)
check("a path in it: none", track_url("1/../2"), None)

print("=== distance ===")
check("100 m north is about 100 m", round(distance_m(LAT, LON, LAT + DLAT_100M, LON)), 100)
check("same point is 0", distance_m(LAT, LON, LAT, LON), 0.0)

print("=== hours ===")
for v, w in ((1, 1), (24, 24), (168, 168), ("72", 72), (72.0, 72)):
    check(f"{v!r} accepted", valid_hours(v), w)
for v in (0, 169, 1.5, "x", None, True, -5):
    try:
        valid_hours(v)
        check(f"{v!r} refused", False)
    except ValueError:
        check(f"{v!r} refused", True)
check("default is 24", DEFAULT_HOURS, 24)
check("cap is 168", MAX_HOURS, 168)

print("=== thinning ===")
c = Clock()
b = book(c)
t0 = c.t - 3600
check("first fix kept", b.add(M, LAT, LON, t0))
check("10 s later, moved 100 m: refused (gap)", b.add(M, LAT + DLAT_100M, LON, t0 + 10), False)
check("the same fix again (a relay): refused", b.add(M, LAT, LON, t0), False)
check("an earlier fix (out of order): refused", b.add(M, LAT, LON, t0 - 100), False)
check("40 s later, moved 5 m: refused (no move, not quiet)", b.add(M, LAT + DLAT_5M, LON, t0 + 40), False)
check("40 s later, moved 100 m: kept", b.add(M, LAT + DLAT_100M, LON, t0 + 40))
check(f"{MAX_QUIET_S + 1} s later, not moved: kept (quiet)", b.add(M, LAT + DLAT_100M, LON, t0 + 40 + MAX_QUIET_S + 1))
check("three points kept", len(b.points(M)), 3)
check("points are [lat, lon, t], oldest first", b.points(M)[0], [round(LAT, 5), round(LON, 5), int(t0)])
check("newest last", b.points(M)[-1][2], int(t0 + 40 + MAX_QUIET_S + 1))

print("=== refused input ===")
check("not an MMSI", b.add("ABC", LAT, LON, t0), False)
check("latitude out of range", b.add("1", 95, LON, t0), False)
check("longitude out of range", b.add("1", LAT, 200, t0), False)
check("0,0 (no fix)", b.add("1", 0, 0, t0), False)
check("not numbers", b.add("1", "x", LON, t0), False)
check("from the future past the slack", b.add("2", LAT, LON, c.t + 3600), False)
check("older than the window", b.add("3", LAT, LON, c.t - DEFAULT_HOURS * 3600 - 10), False)
check("refused vessels left no track", b.counts()[0], 1)

print("=== observations ===")
at = dt.datetime.fromtimestamp(c.t - 60, dt.timezone.utc)
obs = SimpleNamespace(identity="219000001", latitude=55.0, longitude=12.0, observed_at=at, position_source="observed")
check("an observed fix", b.add_obs(obs))
est = SimpleNamespace(identity="219000002", latitude=55.0, longitude=12.0, observed_at=at, position_source="estimated")
check("an estimate is never kept", b.add_obs(est), False)
sat = SimpleNamespace(identity="219000003", latitude=55.0, longitude=12.0, observed_at=at, position_source="satellite")
check("a satellite fix is a real fix", b.add_obs(sat))
none_at = SimpleNamespace(identity="219000004", latitude=55.0, longitude=12.0, observed_at=None, position_source=None)
check("no time: not kept", b.add_obs(none_at), False)
check("two areas hearing one fix: the second is refused", b.add_obs(obs), False)

print("=== the cap ===")
c2 = Clock()
b2 = book(c2)
start = c2.t - 3600
kept = sum(b2.add(M, LAT + i * DLAT_100M, LON, start + i * 2) for i in range(1800))   # a fix every 2 s, moving
check(f"a fix every 2 s for an hour keeps at most 3600/{MIN_GAP_S}", kept <= 3600 // MIN_GAP_S, True)
check("and close to it", kept >= 3600 // MIN_GAP_S - 2, True)

print("=== the window ===")
c3 = Clock()
b3 = book(c3)
b3.add(M, LAT, LON, c3.t - 23 * 3600)
b3.add(M, LAT + DLAT_100M, LON, c3.t - 3600)
b3.add("219000009", LAT, LON, c3.t - 22.5 * 3600)
c3.t += 2 * 3600                       # M's points 25 h and 3 h old now; the other vessel's 24.5 h
check("points() hides what fell out", len(b3.points(M)), 1)
check("prune drops two points", b3.prune(), 2)
check("a vessel with nothing left is dropped", b3.counts(), (1, 1))
check("set_hours 1 drops older at once", (b3.set_hours(1), b3.counts()), (1, (0, 0)))
try:
    b3.set_hours(500)
    check("set_hours 500 refused", False)
except ValueError:
    check("set_hours 500 refused, hours unchanged", b3.hours, 1)
check("set_hours 168", b3.set_hours(168), 168)

print("=== the file ===")
d = tempfile.mkdtemp()
p = os.path.join(d, "saw_vessel_tracks.json")
c4 = Clock()
b4 = book(c4, p)
b4.add(M, LAT, LON, c4.t - 600)
b4.add(M, LAT + DLAT_100M, LON, c4.t - 300)
b4.set_hours(72)
b4.save()
check("saved", os.path.exists(p))
check("no temp file left", os.path.exists(p + ".tmp"), False)
raw = json.load(open(p, encoding="utf-8"))
check("version and hours in the file", (raw["v"], raw["hours"]), (1, 72))
b5 = book(c4, p)
b5.load()
check("read back: hours", b5.hours, 72)
check("read back: points", b5.points(M), b4.points(M))
check("nothing to save after reading", b5._dirty, False)
json.dump({"hours": 999, "tracks": {"abc": [[1, 2, 3]], M: [[int(c4.t - 60), LAT, LON], "junk", [1, 2]],
                                     "1": "notalist"}}, open(p, "w", encoding="utf-8"))
b6 = book(c4, p)
b6.load()
check("a bad hours value falls back to 24", b6.hours, 24)
check("junk entries are skipped", b6.counts(), (1, 1))
json.dump({"hours": 24, "tracks": {M: [[int(c4.t - 60), LAT + DLAT_100M, LON], [int(c4.t - 600), LAT, LON]]}},
          open(p, "w", encoding="utf-8"))
b9 = book(c4, p)
b9.load()
check("points out of order in the file are read oldest first", [x[2] for x in b9.points(M)],
      [int(c4.t - 600), int(c4.t - 60)])
open(p, "w", encoding="utf-8").write("{not json")
b7 = book(c4, p)
b7.load()
check("an unreadable file starts empty, no raise", b7.counts(), (0, 0))
b8 = book(c4, os.path.join(d, "absent.json"))
b8.load()
check("no file: empty", b8.counts(), (0, 0))

print("=== the answer and the address ===")
check("answer", b5.answer(M), {"identity": M, "hours": 72, "points": b5.points(M)})
check("answer for an unknown vessel is empty, not an error", b5.answer("219000077")["points"], [])
view = _make_view(b5)
check("signed in only", view.requires_auth, True)
check("url", view.url, "/api/live_track_ships/track/{identity}")
resp = asyncio.run(view.get(None, M))
check("200 with the points", (resp.status, json.loads(resp.body)["points"]), (200, b5.points(M)))
resp = asyncio.run(view.get(None, "x/y"))
check("not an MMSI: 400", resp.status, 400)

print("=== the entity ===")
from live_track_ships.geo_location import ShipEvent   # noqa: E402
check("marker_track is not recorded", "marker_track" in ShipEvent._unrecorded_attributes)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
