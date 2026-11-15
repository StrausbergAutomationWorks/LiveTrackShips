"""Test the BarentsWatch adapter against the LIVE feed.

⚠ Centred on Tromsø, not Elmhurst - the feed covers Norwegian waters and a
Chicago centre would return nothing, which would look like a broken adapter.
"""
import asyncio
import datetime as dt
import pathlib
import sys
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]
                       / "custom_components" / "live_track_ships"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from _keys import key_or_skip                                       # noqa: E402
from sources.barentswatch import (                              # noqa: E402
    BarentsWatchSource, circle_geometry)
from sources.base import Observation                            # noqa: E402

passed = failed = 0
TROMSO = (69.6492, 18.9553)
SECONDS = 90


def check(label, got, want=True):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}"
          + ("" if ok else f"   got {got!r} want {want!r}"))


print("=== ⚠ the circle is sent as a POLYGON, not a bounding box ===")
g = circle_geometry(TROMSO[0], TROMSO[1], 100)
check("GeoJSON Polygon", g["type"], "Polygon")
ring = g["coordinates"][0]
check("ring is closed", ring[0], ring[-1])
check("65 points for a 64-segment ring", len(ring), 65)
lats = [p[1] for p in ring]
lons = [p[0] for p in ring]
span_lat = max(lats) - min(lats)
span_lon = max(lons) - min(lons)
print(f"   lat span {span_lat:.3f}°   lon span {span_lon:.3f}°")
# ⚠ At 69.6 N a degree of longitude is ~0.35 of a degree of latitude, so the
# longitude span MUST be much wider or the shape is an ellipse, not a circle.
check("⚠ longitude span widened for latitude", span_lon > span_lat * 2)


BW_ID, BW_SECRET = key_or_skip(
    "test_barentswatch_live",
    ["BARENTSWATCH_CLIENT_ID", "BARENTSWATCH_CLIENT_SECRET"],
    ["barentswatch_client_id", "barentswatch_client_secret"])


async def main():
    import aiohttp
    async with aiohttp.ClientSession() as session:
        src = BarentsWatchSource(
            session,
            BW_ID,
            BW_SECRET,
            TROMSO[0], TROMSO[1], radius_km=200)

        print("\n=== the token ===")
        tok = await src._access_token()
        check("token obtained", bool(tok))
        check("⚠ cached, not re-fetched", await src._access_token(), tok)

        print("\n=== the snapshot, server-side filtered ===")
        snap = await src._snapshot()
        check("vessels returned", len(snap) > 0)
        print(f"   {len(snap)} vessels inside a 200 km polygon")

        obs = list(snap)
        gen = src.observations()

        async def drain():
            async for o in gen:
                obs.append(o)
        try:
            await asyncio.wait_for(drain(), timeout=SECONDS)
        except asyncio.TimeoutError:
            pass
        await gen.aclose()
        await src.close()

    print(f"\n=== {len(obs)} observations total ===")
    check("all Observation", all(isinstance(o, Observation) for o in obs))
    check("source is the domain",
          all(o.source == "live_track_ships" for o in obs))
    check("all positioned", all(o.latitude is not None for o in obs))
    check("timezone aware",
          all(o.observed_at.tzinfo is not None for o in obs))

    print("\n=== ⚠ no static join needed ===")
    named = sum(1 for o in obs if o.name)
    typed = sum(1 for o in obs if o.ship_type is not None)
    print(f"   named {named}/{len(obs)} ({100*named/len(obs):.0f}%)   "
          f"real type {typed}/{len(obs)} ({100*typed/len(obs):.0f}%)")
    check("names arrive with positions", named > len(obs) * 0.8)

    print("\n=== ⚠ sentinels never reach a consumer ===")
    check("no course 360", any(o.course_deg == 360.0 for o in obs), False)
    check("no heading 511", any(o.heading_deg == 511 for o in obs), False)
    check("no nav_status 15", any(o.nav_status == 15 for o in obs), False)
    check("no ship_type 0", any(o.ship_type == 0 for o in obs), False)

    print("\n=== ⚠ provenance is STATED, not inferred ===")
    streams = Counter(o.extra.get("stream") for o in obs)
    print(f"   stream values: {dict(streams)}")
    sources = Counter(o.position_source for o in obs)
    print(f"   position_source: {dict(sources)}")
    check("every observation has a position_source",
          all(o.position_source for o in obs))
    sat = [o for o in obs if o.extra.get("stream") == "satellite"]
    if sat:
        check("⚠ satellite fixes are labelled as such",
              all(o.position_source == "satellite" for o in sat))
        print(f"   {len(sat)} satellite-sourced fixes")

    print("\n=== ⚠ ships must never be movable ===")
    check("max_extrapolation_s never set",
          all(o.max_extrapolation_s is None for o in obs))

    print("\n=== units ===")
    sp = [o.speed_kmh for o in obs if o.speed_kmh is not None]
    if sp:
        check(f"speed in km/h (max {max(sp):.1f})", max(sp) < 120)

    print("\n=== sample ===")
    for o in obs[:3]:
        print(f"   {o.identity}  {o.name!r}  "
              f"{o.latitude:.4f},{o.longitude:.4f}  "
              f"type={o.ship_type} stream={o.extra.get('stream')!r} "
              f"src={o.position_source}")

    print(f"\n{passed} passed, {failed} failed")

asyncio.run(main())
sys.exit(1 if failed else 0)
