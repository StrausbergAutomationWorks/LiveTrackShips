"""Item 246: the notify window and changed-only writes.

⚠ Runs INSIDE the Home Assistant container (the package imports
homeassistant), like test_geo_location.py. %USERPROFILE%\\bin\\lts_boxtest.py.

What it pins down:
  * many notifies inside one window -> ONE listener pass
  * nothing arrives -> nothing runs
  * the prune path still produces a pass, and a departed vessel is removed
  * stop() cancels a pending pass
  * one listener raising does not starve the next
  * a duplicate relay does not notify at all
  * a vessel whose observation did not change is not written
"""
import asyncio
import dataclasses
import datetime as dt
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent / "custom_components"))

from live_track_ships import ShipFeed                                # noqa: E402
from live_track_ships import geo_location as gl                      # noqa: E402
from live_track_ships.const_flow import (                            # noqa: E402
    CONF_LATITUDE, CONF_LONGITUDE, CONF_MAX_VESSELS, CONF_RADIUS_KM,
    CONF_SOURCE, DOMAIN, NOTIFY_WINDOW_S, SOURCE_DIGITRAFFIC)
from live_track_ships.geo_location import ShipEvent                  # noqa: E402
from live_track_ships.sources.base import Observation                # noqa: E402

passed = failed = 0
LAT, LON = 60.0, 23.0
T0 = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
W = 0.2          # shortened window for the test


def check(label, got, want=True):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}"
          + ("" if ok else f"   got {got!r} want {want!r}"))


def obs(ident, dlat, secs=0, **kw):
    return Observation(identity=ident, source=DOMAIN,
                       observed_at=T0 + dt.timedelta(seconds=secs),
                       latitude=LAT + dlat, longitude=LON, **kw)


class FakeEntry:
    def __init__(self, entry_id):
        self.entry_id = entry_id
        self.data = {CONF_SOURCE: SOURCE_DIGITRAFFIC, CONF_LATITUDE: LAT,
                     CONF_LONGITUDE: LON, CONF_RADIUS_KM: 50,
                     CONF_MAX_VESSELS: 1000}
        self.options = {}
        self.unloads = []

    def async_on_unload(self, cb):
        self.unloads.append(cb)


class FakeHass:
    def __init__(self, loop):
        self.loop = loop
        self.data = {}

    def async_create_task(self, coro):
        return self.loop.create_task(coro)


async def main():
    loop = asyncio.get_running_loop()
    hass = FakeHass(loop)

    print(f"=== the shipped window is {NOTIFY_WINDOW_S} s ===")
    check("NOTIFY_WINDOW_S is 5", NOTIFY_WINDOW_S, 5.0)

    print("\n=== many notifies, one pass ===")
    feed = ShipFeed(hass, FakeEntry("A"))
    feed.notify_window_s = W
    calls = []
    feed.add_listener(lambda: calls.append(1))
    for _ in range(200):
        feed._notify()
    await asyncio.sleep(W / 2)
    check("nothing runs inside the window", len(calls), 0)
    await asyncio.sleep(W)
    check("200 notifies -> ONE pass", len(calls), 1)
    await asyncio.sleep(W * 3)
    check("idle: nothing runs", len(calls), 1)
    feed._notify()
    await asyncio.sleep(W * 1.5)
    check("the next arrival opens a new window", len(calls), 2)

    print("\n=== stop() cancels a pending pass ===")
    feed._notify()
    await feed.stop()
    await asyncio.sleep(W * 1.5)
    check("no pass after stop", len(calls), 2)

    print("\n=== one listener raising does not starve the next ===")
    f2 = ShipFeed(hass, FakeEntry("B"))
    f2.notify_window_s = W
    after = []
    f2.add_listener(lambda: 1 / 0)
    f2.add_listener(lambda: after.append(1))
    f2._notify()
    await asyncio.sleep(W * 1.5)
    check("second listener still ran", len(after), 1)

    print("\n=== duplicates do not notify ===")
    s = f2.store
    check("new vessel kept", s.add(obs("d1", 0.01)), True)
    check("⚠ same fix again (duplicate relay) -> False",
          s.add(obs("d1", 0.01)), False)
    check("older fix -> False", s.add(obs("d1", 0.02, -10)), False)
    check("newer fix -> True", s.add(obs("d1", 0.02, 10)), True)

    print("\n=== a truncated store published exactly max_vessels ===")
    from live_track_ships.store import VesselStore
    st = VesselStore(LAT, LON, 50, 5)
    for i in range(9):
        st.add(obs(f"t{i}", 0.001 * (i + 1)))
    check("published() length is the cap", len(st.published()), 5)
    check("max_vessels is the cap", st.max_vessels, 5)
    check("truncated_from is the total", st.truncated_from, 9)

    print("\n=== changed-only writes, on the entity ===")
    e = ShipEvent(obs("u1", 0.01), 1.1)
    same = dataclasses.replace(obs("u1", 0.01))
    check("equal by value, new object -> not written",
          e.update_from(same, 1.1), False)
    check("distance changed -> written", e.update_from(same, 1.2), True)
    check("static data on its own (same fix time) -> written",
          e.update_from(obs("u1", 0.01, name="NEW NAME"), 1.2), True)

    print("\n=== through geo_location._sync: writes, departures ===")
    writes = []
    removed = []
    orig_write = ShipEvent.async_write_ha_state
    orig_remove = ShipEvent.async_remove
    ShipEvent.async_write_ha_state = lambda self: writes.append(
        self._obs.identity)

    async def fake_remove(self, *, force_remove=False):
        removed.append(self._obs.identity)
    ShipEvent.async_remove = fake_remove
    try:
        entry = FakeEntry("C")
        f3 = ShipFeed(hass, entry)
        f3.notify_window_s = W
        hass.data.setdefault(DOMAIN, {})["C"] = f3
        for i, name in enumerate(("v1", "v2", "v3")):
            f3.store.add(obs(name, 0.01 * (i + 1)))
        added = []

        def add_entities(ents):
            for ent in ents:
                ent.hass = hass
            added.extend(ents)
        await gl.async_setup_entry(hass, entry, add_entities)
        check("three vessels added on setup", len(added), 3)

        # One vessel moves; the pass must write that one and no other.
        if f3.store.add(obs("v2", 0.025, 30)):
            f3._notify()
        await asyncio.sleep(W * 1.5)
        check("⛔ one vessel changed -> ONE write, not three", writes, ["v2"])

        # A duplicate of v1 arrives: no notify, no pass, no write.
        n = f3.passes
        if f3.store.add(obs("v1", 0.01)):
            f3._notify()
        await asyncio.sleep(W * 1.5)
        check("duplicate -> no pass", f3.passes, n)

        # Departure through the PRUNE path: age v3 out, prune, notify.
        f3.store._tracks["v3"]._latest = obs("v3", 0.03, -100000)
        if f3.store.prune():
            f3._notify()
        await asyncio.sleep(W * 1.5)
        await asyncio.sleep(0)          # let _remove_vessel run
        check("⚠ prune still produces a pass and removes the vessel",
              removed, ["v3"])
        owners = hass.data[gl.OWNERS_KEY]
        check("its MMSI is released for another entry", "v3" in owners,
              False)
        check("the others are still owned", sorted(
            k for k, v in owners.items() if v == "C"), ["v1", "v2"])
        for cb in entry.unloads:
            cb()
        await f3.stop()
    finally:
        ShipEvent.async_write_ha_state = orig_write
        ShipEvent.async_remove = orig_remove

    print(f"\n{passed} passed, {failed} failed")
    return failed


sys.exit(1 if asyncio.run(main()) else 0)
