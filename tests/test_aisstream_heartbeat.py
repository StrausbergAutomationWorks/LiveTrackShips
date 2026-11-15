"""SSOT item 23: an aisstream socket that dies without closing.

⚠ Since 2026-10-30 (backlog 315) the connection is saw_livetrack.aisstream's
and this drives it through Ships' adapter, `sources` loaded BY PATH, so it
runs anywhere with aiohttp and saw-livetrack 0.2.19 (and still in the box).

A local WebSocket server stands in for aisstream. What it pins down:
  * a QUIET but live server (answers pings, sends no data) is NOT dropped -
    quiet water must never look like a dead socket
  * a DEAD server (never answers a ping) is dropped and reconnected, and a
    WARNING is logged
  * an {"error": ...} frame is logged as a WARNING, with the key masked
  * data still flows as Observations with the heartbeat on
  * MUTATION: with heartbeat off (the pre-2026-10-20 code) the dead server is
    never noticed - proves the dead-server check can fail
"""
import asyncio
import importlib
import json
import logging
import pathlib
import sys
import types

import aiohttp                                                       # noqa: E402
from aiohttp import web                                              # noqa: E402

from saw_livetrack import aisstream as A                             # noqa: E402

_pkg = types.ModuleType("lts_src")
_pkg.__path__ = [str(pathlib.Path(__file__).resolve().parents[1] / "custom_components"
                     / "live_track_ships" / "sources")]
sys.modules["lts_src"] = _pkg
S = importlib.import_module("lts_src.aisstream")                   # Ships' adapter

passed = failed = 0
KEY = "test-key-0123456789abcdef"
HB = 0.5          # shortened heartbeat: a dead socket is noticed in 0.75 s


def check(label, got, want=True):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}"
          + ("" if ok else f"   got {got!r} want {want!r}"))


class Capture(logging.Handler):
    def __init__(self):
        super().__init__(logging.DEBUG)
        self.records = []

    def emit(self, record):
        self.records.append(record)

    def warnings(self, needle):
        return [r.getMessage() for r in self.records
                if r.levelno >= logging.WARNING and needle in r.getMessage()]


CONFIRM = json.dumps({"Message": {"CompressionEnabled": True},
                      "MessageType": "SubscriptionConfirmation"}).encode()


def position(mmsi):
    return json.dumps({
        "MessageType": "PositionReport",
        "MetaData": {"MMSI": mmsi, "ShipName": "TEST", "latitude": 40.0,
                     "longitude": -3.0,
                     "time_utc": "2026-10-20 22:05:43.933000000 +0000 UTC"},
        "Message": {"PositionReport": {"Sog": 5.0, "Cog": 90.0,
                                       "TrueHeading": 90}},
    }).encode()


async def run_case(mode, seconds, heartbeat):
    """Serve `mode`, run the source for `seconds`, return (connections, obs, log)."""
    state = {"connections": 0}

    async def handler(request):
        state["connections"] += 1
        # autoping=False on the DEAD server: it never answers a ping.
        ws = web.WebSocketResponse(autoping=(mode != "dead"))
        await ws.prepare(request)
        await ws.receive()                      # the subscription
        await ws.send_bytes(CONFIRM)
        if mode == "error":
            await ws.send_bytes(json.dumps(
                {"error": f"Api Key Is Not Valid: {KEY}"}).encode())
            await ws.close()
            return ws
        if mode == "data":
            for i in range(int(seconds / 0.1)):
                await ws.send_bytes(position(200000000 + i % 3))
                await asyncio.sleep(0.1)
        if mode == "dead":
            await asyncio.sleep(3600)           # never reads, never pongs
            return ws
        # quiet: keep reading so autoping answers pings, send nothing
        async for _ in ws:
            pass
        return ws

    app = web.Application()
    app.router.add_get("/", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]

    A.URL = f"ws://127.0.0.1:{port}/"
    A.HEARTBEAT_S = heartbeat
    A.BACKOFF_START_S = 0.05
    cap = Capture()
    A._LOGGER.addHandler(cap)
    A._LOGGER.setLevel(logging.DEBUG)
    got = []
    async with aiohttp.ClientSession() as session:
        src = S.AisStreamSource(session, KEY, [[[39, -4], [41, -2]]])

        async def consume():
            async for o in src.observations():
                got.append(o)

        task = asyncio.create_task(consume())
        await asyncio.sleep(seconds)
        await src.close()
        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, Exception):
            pass
    A._LOGGER.removeHandler(cap)
    await runner.cleanup()
    return state["connections"], got, cap


async def main():
    print("quiet but alive server, heartbeat on")
    n, got, cap = await run_case("quiet", 3.0, HB)
    check("one connection held for 3 s (6 heartbeats)", n, 1)
    check("no 'connection lost' warning", cap.warnings("connection lost"), [])

    print("dead server (never pongs), heartbeat on")
    n, got, cap = await run_case("dead", 3.0, HB)
    check("reconnected at least once", n >= 2)
    check("a 'connection lost' WARNING was logged",
          len(cap.warnings("connection lost")) >= 1)

    print("error frame")
    n, got, cap = await run_case("error", 1.0, HB)
    w = cap.warnings("refused the subscription")
    check("the refusal is logged as a WARNING", len(w) >= 1)
    check("the key is masked in the log", any("<api key>" in m for m in w))
    check("the key itself never appears", any(KEY in m for m in w), False)
    check("no observation from an error frame", got, [])

    print("data flows with the heartbeat on")
    n, got, cap = await run_case("data", 2.0, HB)
    check("observations arrive", len(got) >= 10)
    check("still one connection", n, 1)
    check("identity is the MMSI string", got[0].identity if got else None,
          "200000000")

    print("MUTATION: heartbeat off, dead server (the pre-fix code)")
    n, got, cap = await run_case("dead", 3.0, None)
    check("the dead socket is NEVER noticed without a heartbeat", n, 1)

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


asyncio.run(main())
