"""Test the aisstream source against the LIVE feed.

⚠ The parsing traps this guards against only exist on the wire: binary frames,
nanosecond timestamps, in-band sentinels, mangled ShipNames, inconsistent
padding. A fixture would test my understanding of them, not the feed.

⚠ Holds ONE of the three connections for the duration. Do not run alongside
another probe.
"""
import asyncio
import datetime as dt
import pathlib
import sys
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]
                       / "custom_components" / "live_track_ships"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from _keys import key_or_skip                                     # noqa: E402
from sources.aisstream import AisStreamSource                 # noqa: E402
from sources.base import Observation                          # noqa: E402

passed = failed = 0
SECONDS = 120
# The Chicagoland rectangle - the box every measurement in the SSOT used.
BOXES = [[[42.4953, -88.7504], [41.2917, -86.00]]]


def check(label, got, want=True):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}"
          + ("" if ok else f"   got {got!r} want {want!r}"))


(AIS_KEY,) = key_or_skip("test_aisstream_live", ["AISSTREAM_API_KEY"], ["aisstream"])


async def main():
    import aiohttp
    obs = []
    async with aiohttp.ClientSession() as session:
        src = AisStreamSource(session, AIS_KEY, BOXES)

        async def drain():
            async for o in src.observations():
                obs.append(o)
        try:
            await asyncio.wait_for(drain(), timeout=SECONDS)
        except asyncio.TimeoutError:
            pass
        await src.close()

    print(f"\n{len(obs)} observations in {SECONDS} s   "
          f"static cached: {len(src._static)}\n")

    print("=== ⚠ the connection itself ===")
    check("compression negotiated", src.compression_enabled, True)
    check("observations arrived at all", len(obs) > 0)
    if not obs:
        print("⚠ nothing received - cannot test parsing")
        return

    print("\n=== shape ===")
    check("all Observation", all(isinstance(o, Observation) for o in obs))
    check("identity is a str", all(isinstance(o.identity, str) for o in obs))
    check("source is the domain",
          all(o.source == "live_track_ships" for o in obs))
    check("all positioned", all(o.latitude is not None for o in obs))

    print("\n=== ⚠ nanosecond timestamps parsed, not defaulted ===")
    now = dt.datetime.now(dt.timezone.utc)
    check("timezone aware", all(o.observed_at.tzinfo is not None for o in obs))
    ages = [(now - o.observed_at).total_seconds() for o in obs]
    print(f"   fix age: min {min(ages):.0f}s  max {max(ages):.0f}s")
    check("no fix from the future", min(ages) > -60)
    # If _parse_time silently failed, every observed_at would be ~now.
    check("⚠ timestamps are the FEED's, not a fallback to now()",
          max(ages) > 5)

    print("\n=== ⚠ sentinels never reach a consumer ===")
    check("no course of 360", any(o.course_deg == 360.0 for o in obs), False)
    check("no heading of 511", any(o.heading_deg == 511 for o in obs), False)
    check("no nav_status 15", any(o.nav_status == 15 for o in obs), False)
    check("no ship_type 0", any(o.ship_type == 0 for o in obs), False)
    # ⚠ THIS ASSERTION USED TO ENCODE THE BUG IT WAS MEANT TO CATCH. It tested
    # `in (-128, -127)` - the same asymmetric list the adapter carried - so it
    # passed while +127 was published as a reading. Rate of turn is now DECODED
    # to degrees per second, so no raw byte should survive at all: the decoded
    # value is bounded by the encoding's ceiling of ~11.8 deg/s.
    check("no raw RoT byte survives the decode",
          any(o.rate_of_turn_dps is not None and abs(o.rate_of_turn_dps) > 12
              for o in obs), False)

    print("\n=== ⚠ units and plausibility ===")
    sp = [o.speed_kmh for o in obs if o.speed_kmh is not None]
    if sp:
        check(f"speed in km/h (max {max(sp):.1f})", max(sp) < 120)
    ln = [o.length_m for o in obs if o.length_m]
    if ln:
        check(f"length plausible (max {max(ln):.0f} m)", max(ln) <= 500)

    print("\n=== ⚠ names are stripped, never repaired ===")
    named = [o.name for o in obs if o.name]
    check("no leading/trailing space survives",
          all(n == n.strip() for n in named))
    mangled = [n for n in named if "_" in n]
    print(f"   names seen: {len(named)}   containing an underscore: "
          f"{len(mangled)}  {mangled[:3]}")

    print("\n=== ⚠ ships must never be movable ===")
    check("max_extrapolation_s never set",
          all(o.max_extrapolation_s is None for o in obs))
    check("position_source always observed",
          all(o.position_source == "observed" for o in obs))

    print("\n=== message mix ===")
    print(f"   {dict(Counter(o.raw_message_type for o in obs))}")
    ids = {o.identity for o in obs}
    typed = sum(1 for o in obs if o.ship_type is not None)
    print(f"   distinct vessels {len(ids)}   with a real ITU type {typed}")

    print(f"\n{passed} passed, {failed} failed")

asyncio.run(main())
sys.exit(1 if failed else 0)
