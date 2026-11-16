"""Entry and exit events (backlog 342), with the real VesselStore.
Runs inside the HA container (the package imports homeassistant):
python lts_boxtest_clone.py test_events.py"""
import datetime as dt
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "custom_components"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from live_track_ships.events import (                       # noqa: E402
    AreaEvents, EVENT_ENTRY, EVENT_EXIT, EXIT_GRACE_S, WARMUP_S, bearing_deg)
from live_track_ships.geo import (                          # noqa: E402
    RadiusError, bounding_boxes, listen_margin_km)
from live_track_ships.store import VesselStore              # noqa: E402
from live_track_ships.sources.base import Observation       # noqa: E402
from live_track_ships.ship_types import label_for           # noqa: E402

passed = failed = 0
T0 = dt.datetime(2026, 11, 15, 22, 0, 0, tzinfo=dt.timezone.utc)
LAT, LON = 41.8995, -87.9403


def check(label, got, want=True):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}"
          + ("" if ok else f"\n         got {got!r}\n         want {want!r}"))


def obs(ident, dlat, secs=0, **kw):
    return Observation(identity=ident, source="live_track_ships",
                       observed_at=T0 + dt.timedelta(seconds=secs),
                       latitude=LAT + dlat, longitude=LON, **kw)


class Clock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


class Timers:
    def __init__(self):
        self.live = []

    def __call__(self, delay, cb):
        t = self

        class H:
            cancelled = False

            def cancel(self):
                self.cancelled = True
                if self in t.live:
                    t.live.remove(self)
        h = H()
        h.delay, h.cb = delay, cb
        self.live.append(h)
        return h


def make(radius=50, cap=1000, drawn=None):
    store = VesselStore(LAT, LON, radius, cap)
    fired = []
    clock, timers = Clock(), Timers()
    ev = AreaEvents(store, "entry1", "Ships near 41.900, -87.940", LAT, LON,
                    fire=lambda t, d: fired.append((t, d)),
                    call_later=timers, clock=clock, drawn=drawn)
    return store, ev, fired, clock, timers


print("=== the listening ring ===")
check("50 km asks 5 km more", listen_margin_km(50), 5.0)
check("1 km asks the 1 km floor", listen_margin_km(1), 1.0)
b0 = bounding_boxes(LAT, LON, 50)[0]
b1 = bounding_boxes(LAT, LON, 50, listen_margin_km(50))[0]
check("the box grows north", b1[0][0] > b0[0][0])
check("the box grows west", b1[0][1] < b0[0][1])
check("500 km plus the ring is accepted", len(bounding_boxes(LAT, LON, 500, 50)), 1)
try:
    bounding_boxes(LAT, LON, 501)
    check("501 km is still refused", False)
except RadiusError:
    check("501 km is still refused", True)
check("bearing east", round(bearing_deg(0, 0, 0, 1)), 90)
check("bearing north", bearing_deg(0, 0, 1, 0), 0.0)

print("\n=== warm-up: what is already there is announced to nobody ===")
store, ev, fired, clock, timers = make()
store.add(obs("367000001", 0.1, name="MOORED ONE", nav_status=5))
ev.run()
check("no entry during warm-up", fired, [])
check("but it is counted inside", "367000001" in ev._inside)
clock.t += WARMUP_S + 1
store.add(obs("367000001", 0.1, 30, name="MOORED ONE", nav_status=5))
ev.run()
check("still no entry for it after warm-up", fired, [])

print("\n=== a newcomer after warm-up: one entry, with the vessel's details ===")
store.add(obs("367000002", 0.2, 40, name=" FINNBREEZE  ", ship_type=70,
              length_m=217.0, speed_kmh=30.0, course_deg=180.0, imo=9543756))
ev.run()
check("one event", len(fired), 1)
t, d = fired[-1]
check("it is the entry", t, EVENT_ENTRY)
check("event name", EVENT_ENTRY, "live_track_ships_entry")
check("area id", d["area_id"], "entry1")
check("area name", d["area"], "Ships near 41.900, -87.940")
check("name stripped", d["name"], "FINNBREEZE")
check("type label, as the entity's", d.get("ship_type_label"), label_for(70))
check("length", d["length_m"], 217.0)
check("speed", d["speed_kmh"], 30.0)
check("imo as 7 digits", d["imo"], "9543756")
check("distance", round(d["distance_km"]), 22)
check("bearing from centre is north", d["bearing_from_centre_deg"], 0.0)
check("no reason on an entry", "reason" in d, False)
check("no entity_id when not drawn", "entity_id" in d, False)
check("no None values", None in d.values(), False)
store.add(obs("367000002", 0.19, 50, name="FINNBREEZE"))
ev.run()
check("a second fix inside is not a second entry", len(fired), 1)

print("\n=== heard OUTSIDE: it leaves the store at once, exits after the grace ===")
check("an older fix outside does nothing",
      store.add(obs("367000002", 0.47, 45)), False)
check("still in the store", "367000002" in store.present())
check("a newer fix outside removes it",
      store.add(obs("367000002", 0.47, 60, speed_kmh=28.0, course_deg=0.0)), True)
check("gone from the store", "367000002" in store.present(), False)
ev.run()
check("no exit yet: the grace", len(fired), 1)
check("a timer waits for the grace", len(timers.live), 1)
check("timer delay covers the grace", timers.live[0].delay >= EXIT_GRACE_S)
check("a late relay from inside cannot revive it",
      store.add(obs("367000002", 0.2, 55)), False)
clock.t += EXIT_GRACE_S + 1
timers.live.pop(0).cb()       # the loop drops a handle once it has run
check("now the exit", fired[-1][0], EVENT_EXIT)
t, d = fired[-1]
check("event name", EVENT_EXIT, "live_track_ships_exit")
check("reason left", d["reason"], "left")
check("position is the fix outside", round(d["distance_km"]), 52)
check("motion is the fix outside", d["speed_kmh"], 28.0)
check("details from inside survive", d["name"], "FINNBREEZE")
check("no entity_id on an exit", "entity_id" in d, False)

print("\n=== back inside within the grace: nothing announced ===")
store.add(obs("367000003", 0.3, 70, name="EDGE RUNNER"))
ev.run()
n = len(fired)
check("entry for the edge runner", fired[-1][1]["name"], "EDGE RUNNER")
store.add(obs("367000003", 0.47, 80))
ev.run()
clock.t += 30
store.add(obs("367000003", 0.44, 90))
ev.run()
clock.t += EXIT_GRACE_S + 1
ev.run()
check("no exit, no second entry", len(fired), n)
check("no timer left", len(timers.live), 0)

print("\n=== silent: pruned by the retention window ===")
store2, ev2, fired2, clock2, timers2 = make()
clock2.t += WARMUP_S + 1
store2.add(obs("367000004", 0.1, -4000, name="QUIET"))
ev2.run()
check("entry", fired2[-1][0], EVENT_ENTRY)
store2.prune(T0)
ev2.run()
clock2.t += EXIT_GRACE_S + 1
ev2.run()
check("exit", fired2[-1][0], EVENT_EXIT)
check("reason silent", fired2[-1][1]["reason"], "silent")
check("its last position inside", round(fired2[-1][1]["distance_km"]), 11)

print("\n=== the cap and the quota never make a vessel enter or leave ===")
store3, ev3, fired3, clock3, _t3 = make(cap=1)
clock3.t += WARMUP_S + 1
store3.add(obs("367000005", 0.1, 0))
store3.add(obs("367000006", 0.2, 0))
check("the cap shows one", len(store3.published()), 1)
ev3.run()
check("both entered", sorted(d["identity"] for _t, d in fired3),
      ["367000005", "367000006"])

print("\n=== entity_id while drawn ===")
store4, ev4, fired4, clock4, _t4 = make(drawn=lambda i: i == "367000007")
clock4.t += WARMUP_S + 1
store4.add(obs("367000007", 0.1, 0))
ev4.run()
check("entity_id", fired4[-1][1]["entity_id"], "geo_location.vessel_367000007")

print("\n=== not a vessel: no vessel fields ===")
store5, ev5, fired5, clock5, _t5 = make()
clock5.t += WARMUP_S + 1
aton = obs("993661234", 0.1, 0, ship_type=70, length_m=5.0, speed_kmh=0.0)
check("the kind is aton", aton.kind, "aton")
store5.add(aton)
ev5.run()
d = fired5[-1][1]
check("object_kind", d["object_kind"], "aton")
check("no ship_type", "ship_type" in d, False)
check("no length", "length_m" in d, False)
check("no speed on a fixed object", "speed_kmh" in d, False)

print("\n=== close cancels the timer ===")
store6, ev6, _f6, clock6, timers6 = make()
store6.add(obs("367000008", 0.1, 0))
ev6.run()
store6.add(obs("367000008", 0.47, 10))
ev6.run()
check("a timer", len(timers6.live), 1)
ev6.close()
check("cancelled", len(timers6.live), 0)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
