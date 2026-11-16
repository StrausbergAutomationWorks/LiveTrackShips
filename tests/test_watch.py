"""Watched vessels (backlog 343): the list's text, and the events, with the real
VesselStore. Runs inside the HA container: python lts_boxtest_clone.py test_watch.py"""
import datetime as dt
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "custom_components"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from live_track_ships.watch import (                        # noqa: E402
    DWELL_S, EVENT_WATCHED, WORLD_RADIUS_KM, VesselListError, WatchEvents,
    format_vessels, parse_vessels)
from live_track_ships.const_flow import MAX_WATCHED         # noqa: E402
from live_track_ships.store import VesselStore              # noqa: E402
from live_track_ships.sources.base import Observation       # noqa: E402

passed = failed = 0
T0 = dt.datetime(2026, 11, 16, 4, 0, 0, tzinfo=dt.timezone.utc)
HOME = (41.8995, -87.9403)


def check(label, got, want=True):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}"
          + ("" if ok else f"\n         got {got!r}\n         want {want!r}"))


def code(text):
    try:
        parse_vessels(text)
        return None
    except VesselListError as exc:
        return exc.code


print("=== the list's text ===")
check("MMSI and label", parse_vessels("244650000 Dad's boat"),
      [{"mmsi": "244650000", "label": "Dad's boat"}])
check("comma and spaces", parse_vessels(" 244650000,  Dad's boat "),
      [{"mmsi": "244650000", "label": "Dad's boat"}])
check("tab, semicolon", parse_vessels("244650000\tA\n366999999;B"),
      [{"mmsi": "244650000", "label": "A"}, {"mmsi": "366999999", "label": "B"}])
check("MMSI alone has no label key", parse_vessels("366999999"), [{"mmsi": "366999999"}])
check("blank lines and # comments skipped",
      parse_vessels("\n# ferries\n366999999\n\n"), [{"mmsi": "366999999"}])
check("a repeat keeps its first line",
      parse_vessels("366999999 first\n366999999 second"),
      [{"mmsi": "366999999", "label": "first"}])
check("8 digits refused", code("36699999"), "vessels_invalid")
check("10 digits refused", code("3669999990"), "vessels_invalid")
check("a name first refused", code("Dad 244650000"), "vessels_invalid")
check("non-ASCII digits refused", code("٣٦٦٩٩٩٩٩٩"), "vessels_invalid")
check("empty refused", code("  \n# nothing\n"), "vessels_empty")
check("None refused", code(None), "vessels_empty")
check(f"{MAX_WATCHED} accepted",
      len(parse_vessels("\n".join(str(200000000 + i) for i in range(MAX_WATCHED)))), MAX_WATCHED)
check(f"{MAX_WATCHED + 1} refused",
      code("\n".join(str(200000000 + i) for i in range(MAX_WATCHED + 1))), "vessels_too_many")
check("round trip", parse_vessels(format_vessels(parse_vessels("244650000 Dad's boat\n366999999"))),
      parse_vessels("244650000 Dad's boat\n366999999"))


def obs(ident, secs, lat=48.0, lon=-123.0, **kw):
    return Observation(identity=ident, source="live_track_ships",
                       observed_at=T0 + dt.timedelta(seconds=secs),
                       latitude=lat, longitude=lon, **kw)


def make(labels=None, drawn=None):
    labels = labels or {"366999999": "Dad's boat", "244650000": ""}
    store = VesselStore(HOME[0], HOME[1], WORLD_RADIUS_KM, len(labels))
    fired = []
    ev = WatchEvents(store, "w1", "Watched vessels", HOME[0], HOME[1], labels,
                     fire=lambda t, d: fired.append((t, d)), drawn=drawn)
    return store, ev, fired


print("\n=== the world circle keeps a vessel anywhere ===")
store, ev, fired = make()
check("the antipode of home is kept", store.add(obs("366999999", 0, -41.9, 92.06)), True)

print("\n=== the first fix is the baseline: no event ===")
store, ev, fired = make()
store.add(obs("366999999", 0, nav_status=5, destination="SEATTLE"))
ev.run()
check("nothing fired", fired, [])

print("\n=== departed: needs DWELL_S on the vessel's own clock ===")
store.add(obs("366999999", 60, nav_status=0, speed_kmh=18.0))
ev.run()
check("the first fix under way is not yet a departure", fired, [])
store.add(obs("366999999", 60 + DWELL_S - 1, nav_status=0, speed_kmh=18.0))
ev.run()
check("still not, one second short", fired, [])
store.add(obs("366999999", 60 + DWELL_S, nav_status=0, speed_kmh=18.0))
ev.run()
check("departed", [(t, d["change"]) for t, d in fired], [(EVENT_WATCHED, "departed")])
d = fired[-1][1]
check("event name", EVENT_WATCHED, "live_track_ships_watched")
check("watch id and name", (d["watch_id"], d["watch"]), ("w1", "Watched vessels"))
check("the user's label", d["label"], "Dad's boat")
check("identity", d["identity"], "366999999")
check("speed", d["speed_kmh"], 18.0)
check("distance from home", round(d["distance_km"]) > 2000)
check("no entity_id when not drawn", "entity_id" in d, False)

print("\n=== a flicker back does not count ===")
n = len(fired)
store.add(obs("366999999", 400, nav_status=5))
ev.run()
store.add(obs("366999999", 420, nav_status=0, speed_kmh=18.0))
ev.run()
store.add(obs("366999999", 420 + DWELL_S + 10, nav_status=0, speed_kmh=18.0))
ev.run()
check("no arrival, no second departure", len(fired), n)

print("\n=== arrived: moored, held DWELL_S ===")
store.add(obs("366999999", 2000, nav_status=5))
ev.run()                      # each pass sees the newest fix only
store.add(obs("366999999", 2000 + DWELL_S, nav_status=5))
ev.run()
check("arrived", fired[-1][1]["change"], "arrived")

print("\n=== with no status, speed decides (under 2 kn is berthed) ===")
store2, ev2, fired2 = make()
store2.add(obs("244650000", 0, speed_kmh=12.0))
ev2.run()
store2.add(obs("244650000", 100, speed_kmh=1.0))
ev2.run()
store2.add(obs("244650000", 100 + DWELL_S, speed_kmh=0.5))
ev2.run()
check("arrived by speed", [d["change"] for _t, d in fired2], ["arrived"])
check("no label key when the user gave none", "label" in fired2[-1][1], False)

print("\n=== destination ===")
store3, ev3, fired3 = make()
store3.add(obs("366999999", 0, nav_status=0, destination=""))
ev3.run()
store3.add(obs("366999999", 10, nav_status=0, destination="SEATTLE"))
ev3.run()
check("first destination is the baseline", fired3, [])
store3.add(obs("366999999", 20, nav_status=0, destination=" SEATTLE "))
ev3.run()
check("the same, padded, is no change", fired3, [])
store3.add(obs("366999999", 30, nav_status=0, destination="VICTORIA"))
ev3.run()
check("changed", (fired3[-1][1]["change"], fired3[-1][1]["destination"],
                  fired3[-1][1]["destination_previous"]), ("destination", "VICTORIA", "SEATTLE"))
store3.add(obs("366999999", 40, nav_status=0, destination=""))
ev3.run()
check("a blank is no change", len(fired3), 1)

print("\n=== silent, then heard ===")
store4, ev4, fired4 = make(drawn=lambda i: True)
store4.add(obs("366999999", -4000, nav_status=0, speed_kmh=20.0, name="SEA SPRITE"))
ev4.run()
store4.prune(T0)
ev4.run()
check("silent", fired4[-1][1]["change"], "silent")
check("no entity_id on silent", "entity_id" in fired4[-1][1], False)
check("its last name", fired4[-1][1]["name"], "SEA SPRITE")
store4.add(obs("366999999", 10, nav_status=0, speed_kmh=20.0))
ev4.run()
check("heard", fired4[-1][1]["change"], "heard")
check("entity_id while drawn", fired4[-1][1]["entity_id"], "geo_location.vessel_366999999")
check("exactly two events", [d["change"] for _t, d in fired4], ["silent", "heard"])

print("\n=== the sensor's rows ===")
store5, ev5, _f5 = make(drawn=lambda i: i == "366999999")
store5.add(obs("366999999", 0, nav_status=5, name="SEA SPRITE", destination="SEATTLE"))
ev5.run()
rows = {r["mmsi"]: r for r in ev5.snapshot()}
check("every listed vessel has a row", sorted(rows), ["244650000", "366999999"])
check("heard one", (rows["366999999"]["heard"], rows["366999999"]["berthed"],
                    rows["366999999"]["name"], rows["366999999"]["label"]),
      (True, True, "SEA SPRITE", "Dad's boat"))
check("its entity", rows["366999999"]["entity_id"], "geo_location.vessel_366999999")
check("the unheard one", rows["244650000"], {"mmsi": "244650000", "heard": False})

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
