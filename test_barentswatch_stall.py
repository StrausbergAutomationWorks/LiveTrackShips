"""SSOT item 23, BarentsWatch: an SSE stream that dies without closing.

⚠ Runs INSIDE the Home Assistant container (the package imports
homeassistant), like test_aisstream_heartbeat.py. %USERPROFILE%\\bin\\lts_boxtest.py.

A local server stands in for BarentsWatch (token, snapshot and SSE). It pins:
  * a QUIET stream that keeps sending `: keep-alive` is NOT dropped - empty
    water must never look like a dead stream
  * a DEAD stream (`: start`, then silence) is dropped and reconnected, and a
    WARNING is logged
  * data still flows as Observations with the read timeout on
  * MUTATION: with no read timeout (the pre-2026-10-20 code) the dead stream
    is never noticed - proves the dead-stream check can fail
"""
import asyncio
import json
import logging
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent / "custom_components"))

import aiohttp                                                       # noqa: E402
from aiohttp import web                                              # noqa: E402

from live_track_ships.sources import barentswatch as B               # noqa: E402

passed = failed = 0
READ_TIMEOUT = 0.6     # shortened; the shipped value is 150 s
KEEPALIVE = 0.2        # shortened; the measured interval is 50 s


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


def row(mmsi):
    return {"mmsi": mmsi, "latitude": 60.0, "longitude": 5.0, "name": "TEST",
            "shipType": 70, "speedOverGround": 5.0, "courseOverGround": 90.0,
            "trueHeading": 90, "msgtime": "2026-10-20T22:05:43+00:00",
            "stream": "terra"}


async def run_case(mode, seconds, read_timeout):
    state = {"streams": 0}

    async def token(request):
        return web.json_response({"access_token": "t", "expires_in": 3600})

    async def latest(request):
        return web.json_response([])

    async def sse(request):
        state["streams"] += 1
        resp = web.StreamResponse(headers={"Content-Type": "text/event-stream"})
        await resp.prepare(request)
        await resp.write(b": start\n\n")
        end = asyncio.get_running_loop().time() + seconds + 5
        i = 0
        while asyncio.get_running_loop().time() < end:
            if mode == "dead":
                await asyncio.sleep(3600)   # never speaks again
            elif mode == "quiet":
                await asyncio.sleep(KEEPALIVE)
                await resp.write(b": keep-alive\n\n")
            elif mode == "data":
                await asyncio.sleep(0.1)
                await resp.write(
                    f"data: {json.dumps(row(257000000 + i % 3))}\n\n".encode())
                i += 1
        return resp

    app = web.Application()
    app.router.add_post("/token", token)
    app.router.add_post("/latest", latest)
    app.router.add_post("/sse", sse)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    base = f"http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}"

    B.TOKEN_URL = f"{base}/token"
    B.LATEST_COMBINED = f"{base}/latest"
    B.SSE_COMBINED = f"{base}/sse"
    B.SSE_READ_TIMEOUT_S = read_timeout
    B.BACKOFF_START_S = 0.05
    cap = Capture()
    B._LOGGER.addHandler(cap)
    B._LOGGER.setLevel(logging.DEBUG)
    got = []
    async with aiohttp.ClientSession() as session:
        src = B.BarentsWatchSource(session, "id@x:c", "secret", 60.0, 5.0, 10.0)

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
    B._LOGGER.removeHandler(cap)
    await runner.shutdown()
    await runner.cleanup()
    return state["streams"], got, cap


async def main():
    print("the shipped values")
    check("keepalive interval is the measured 50 s", B.KEEPALIVE_INTERVAL_S, 50)
    check("read timeout is three intervals (150 s)", B.SSE_READ_TIMEOUT_S, 150)

    print("quiet stream, keepalives only, read timeout on")
    n, got, cap = await run_case("quiet", 3.0, READ_TIMEOUT)
    check("one stream held for 3 s (5 read timeouts' worth)", n, 1)
    check("no 'silent' warning", cap.warnings("silent"), [])

    print("dead stream, read timeout on")
    n, got, cap = await run_case("dead", 3.0, READ_TIMEOUT)
    check("reconnected at least once", n >= 2)
    check("a 'silent ... reconnecting' WARNING was logged",
          len(cap.warnings("silent")) >= 1)

    print("data flows with the read timeout on")
    n, got, cap = await run_case("data", 2.0, READ_TIMEOUT)
    check("observations arrive", len(got) >= 10)
    check("still one stream", n, 1)
    check("identity is the MMSI string", got[0].identity if got else None,
          "257000000")

    print("MUTATION: no read timeout, dead stream (the pre-fix code)")
    n, got, cap = await run_case("dead", 3.0, None)
    check("the dead stream is NEVER noticed without a read timeout", n, 1)

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


asyncio.run(main())
