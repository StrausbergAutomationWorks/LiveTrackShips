"""Test the Digitraffic adapter against the LIVE feed.

⚠ Not a mock. The point of choosing a reachable open source was to be able to
test normalisation against real data, including the sentinels and unit traps
that only appear on the wire.
"""
import asyncio
import datetime as dt
import sys
import pathlib
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]
                       / "custom_components" / "live_track_ships"))

from sources.digitraffic import DigitrafficSource               # noqa: E402
from sources.base import Observation                            # noqa: E402

HELSINKI = (60.1699, 24.9384)
passed = failed = 0


def check(label, got, want=True):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}"
          + ("" if ok else f"   got {got!r} want {want!r}"))


async def main():
    import aiohttp
    async with aiohttp.ClientSession() as session:
        src = DigitrafficSource(session, HELSINKI[0], HELSINKI[1],
                                radius_km=80, position_interval_s=9999)
        obs = []
        gen = src.observations()

        # ⚠ The generator sleeps for position_interval_s after draining a
        # poll. Asking for a fixed number of observations HANGS whenever the
        # area holds fewer than that. Bound by TIME, not by count.
        async def drain():
            async for o in gen:
                obs.append(o)
                if len(obs) >= 2000:
                    return
        try:
            await asyncio.wait_for(drain(), timeout=45)
        except asyncio.TimeoutError:
            pass
        await gen.aclose()

    print(f"\nobservations: {len(obs)}   static cached: {len(src._static)}\n")
    if not obs:
        print("⚠ no observations - cannot test")
        return

    print("=== shape ===")
    check("all are Observation", all(isinstance(o, Observation) for o in obs))
    check("all carry the domain as source",
          all(o.source == "live_track_ships" for o in obs))
    check("identity is a str", all(isinstance(o.identity, str) for o in obs))
    check("observed_at is timezone-aware",
          all(o.observed_at.tzinfo is not None for o in obs))
    check("positions present", all(o.latitude is not None for o in obs))

    print("\n=== ⚠ sentinels must never reach a consumer ===")
    check("no course of exactly 360", any(o.course_deg == 360.0 for o in obs), False)
    check("no heading of 511", any(o.heading_deg == 511 for o in obs), False)
    check("no nav_status 15", any(o.nav_status == 15 for o in obs), False)
    check("no ship_type 0", any(o.ship_type == 0 for o in obs), False)
    check("no speed from SOG 102.3",
          any(o.speed_kmh and abs(o.speed_kmh - 102.3 * 1.852) < 0.01
              for o in obs), False)

    print("\n=== ⚠ units ===")
    draughts = [o.draught_m for o in obs if o.draught_m]
    if draughts:
        check(f"draught looks like metres (max {max(draughts):.1f})",
              max(draughts) < 30)
    lengths = [o.length_m for o in obs if o.length_m]
    if lengths:
        # ⚠ referencePointA-D are METRES while draught is DECIMETRES, in the
        # same object. A cargo fleet whose longest ship is 29 m means the
        # divide-by-10 was applied to the wrong field.
        check(f"length looks like metres (max {max(lengths):.0f})",
              60 < max(lengths) <= 500)
        big = [o for o in obs if o.length_m and o.length_m > 100]
        check(f"some vessels exceed 100 m ({len(big)} of {len(lengths)})",
              len(big) > 0)
    speeds = [o.speed_kmh for o in obs if o.speed_kmh]
    if speeds:
        check(f"speed looks like km/h (max {max(speeds):.1f})",
              max(speeds) < 120)

    print("\n=== ⚠ timestamps ===")
    now = dt.datetime.now(dt.timezone.utc)
    ages = [(now - o.observed_at).total_seconds() for o in obs]
    print(f"  age of fixes: min {min(ages):.0f}s  median "
          f"{sorted(ages)[len(ages)//2]:.0f}s  max {max(ages):.0f}s")
    check("no fix claims to be from the future", min(ages) > -60)
    check("timestampExternal used, not second-of-minute",
          max(ages) > 120 or min(ages) > 0)

    print("\n=== ⚠ extrapolation must be refused ===")
    check("max_extrapolation_s never set",
          all(o.max_extrapolation_s is None for o in obs))
    check("position_source always stated",
          all(o.position_source for o in obs))

    print("\n=== coverage of the static join ===")
    named = sum(1 for o in obs if o.name)
    typed = sum(1 for o in obs if o.ship_type is not None)
    print(f"  named {named}/{len(obs)} ({100*named/len(obs):.0f}%)   "
          f"real ITU type {typed}/{len(obs)} ({100*typed/len(obs):.0f}%)")
    print(f"  types: {dict(Counter(o.ship_type for o in obs if o.ship_type).most_common(8))}")
    moving = sum(1 for o in obs if (o.speed_kmh or 0) > 2 * 1.852)
    print(f"  moving faster than 2 kn: {moving}/{len(obs)} "
          f"({100*moving/len(obs):.0f}%)")

    print(f"\n=== sample ===")
    for o in obs[:3]:
        print(f"  {o.identity}  {o.name!r}  {o.latitude:.4f},{o.longitude:.4f}  "
              f"cog={o.course_deg} hdg={o.heading_deg} "
              f"kmh={None if o.speed_kmh is None else round(o.speed_kmh,1)} "
              f"type={o.ship_type} draught={o.draught_m}")

    print(f"\n{passed} passed, {failed} failed")

asyncio.run(main())
sys.exit(1 if failed else 0)
