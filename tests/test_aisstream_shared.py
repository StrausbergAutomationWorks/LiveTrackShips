"""Backlog 315: Ships' aisstream entries on the instance's SHARED client (saw-livetrack 0.2.19).

Loads `sources` BY PATH, so it runs anywhere with saw-livetrack 0.2.19 (no Home Assistant, no network: the
connection's task is captured and never run). What it pins down:
  * two entries on one key share ONE connection; another key gets its own
  * each entry receives only what falls inside its own boxes, labelled live_track_ships
  * closing one entry keeps the connection for the other; closing the last closes it
  * an adapter with no consumer name still gets a unique one (two entries never collide)
  * the adapter's statics ARE the client's, and __init__.py loads and saves that same cache
Run: python test_aisstream_shared.py
"""
import asyncio
import datetime as dt
import importlib
import pathlib
import sys
import types

from saw_livetrack import aisstream as L
from saw_livetrack.ais import Observation

HERE = pathlib.Path(__file__).resolve().parents[1]
_pkg = types.ModuleType("lts_src")
_pkg.__path__ = [str(HERE / "custom_components" / "live_track_ships" / "sources")]
sys.modules["lts_src"] = _pkg
S = importlib.import_module("lts_src.aisstream")

passed = failed = 0
CHICAGO = [[[44.0, -89.0], [41.0, -86.0]]]
HELSINKI = [[[61.0, 23.0], [59.0, 26.0]]]


def check(label, got, want=True):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}" + ("" if ok else f"   got {got!r} want {want!r}"))


def obs(lat, lon, mmsi="367000001"):
    return Observation(identity=mmsi, source="aisstream", observed_at=dt.datetime(2026, 10, 30, tzinfo=dt.timezone.utc),
                       latitude=lat, longitude=lon)


async def main():
    loop = asyncio.get_running_loop()
    started = []

    def create_task(coro, name):
        started.append(name)
        coro.close()                       # never connects
        f = loop.create_future()
        f.cancel()
        return f

    store = {}
    a = S.AisStreamSource(None, "key-1", CHICAGO, store=store, consumer="live_track_ships:a", create_task=create_task)
    b = S.AisStreamSource(None, "key-1", HELSINKI, store=store, consumer="live_track_ships:b", create_task=create_task)
    c = S.AisStreamSource(None, "key-2", CHICAGO, store=store, consumer="live_track_ships:c", create_task=create_task)
    client = L.shared(store)
    ga, gb, gc = a.observations(), b.observations(), c.observations()
    ta = asyncio.ensure_future(ga.__anext__())
    tb = asyncio.ensure_future(gb.__anext__())
    await asyncio.sleep(0)
    check("two entries on one key: one connection", len(client._conns), 1)
    check("one task started for it", started, ["saw_aisstream_area"])
    tc = asyncio.ensure_future(gc.__anext__())
    await asyncio.sleep(0)
    check("another key: its own connection", len(client._conns), 2)
    conn = client._conns[("key-1", L.AREA)]
    check("the area subscription carries both entries' boxes",
          client._payload("key-1", L.AREA)["BoundingBoxes"], CHICAGO + HELSINKI)
    client._dispatch(conn, obs(42.0, -87.5))
    await asyncio.sleep(0)
    check("a fix in Chicago reaches the Chicago entry", ta.done() and ta.result().latitude, 42.0)
    check("labelled live_track_ships", ta.result().source if ta.done() else None, "live_track_ships")
    check("and not the Helsinki entry", tb.done(), False)
    check("nor the other key's entry", tc.done(), False)
    check("statics are the client's", a.statics is client.statics and b._parser._static is client.statics)

    await a.close()
    check("closing one entry keeps the connection", ("key-1", L.AREA) in client._conns)
    check("its consumer is gone", sorted(client._consumers), ["live_track_ships:b", "live_track_ships:c"])
    tb.cancel()
    try:
        await tb
    except asyncio.CancelledError:
        pass
    await gb.aclose()
    check("the last entry on a key closes its connection", ("key-1", L.AREA) in client._conns, False)
    await c.close()
    tc.cancel()
    check("all closed", (client._conns, client._consumers), ({}, {}))

    d1 = S.AisStreamSource(None, "key-3", CHICAGO, store=store, create_task=create_task)
    d2 = S.AisStreamSource(None, "key-3", HELSINKI, store=store, create_task=create_task)
    t1 = asyncio.ensure_future(d1.observations().__anext__())
    t2 = asyncio.ensure_future(d2.observations().__anext__())
    await asyncio.sleep(0)
    check("no consumer name: still unique, both added", len(client._consumers), 2)
    for t in (t1, t2):
        t.cancel()
    await d1.close()
    await d2.close()

    init = (HERE / "custom_components" / "live_track_ships" / "__init__.py").read_text(encoding="utf-8")
    check("__init__: the holder's cache is the shared client's",
          "self.cache = _aisstream.shared(hass.data).statics" in init)
    check("__init__: the source joins the shared client",
          "store=self.hass.data," in init and 'consumer=f"{DOMAIN}:{self.entry.entry_id}"' in init)
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


asyncio.run(main())
