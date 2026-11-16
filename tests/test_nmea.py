"""Your own receiver (backlog 344): NMEA decoding, sentinels, statics, multi-part
messages, the station figures, and the real UDP path on a free port.
Runs inside the HA container: python lts_boxtest_clone.py test_nmea.py
Sentences: three real ones (San Francisco Bay, from pyais's own examples) and the
rest built with pyais's encoder, so every field and sentinel can be chosen."""
import asyncio
import datetime as dt
import pathlib
import socket
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "custom_components"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from pyais.encode import encode_dict                        # noqa: E402
from saw_livetrack.ais import StaticCache                   # noqa: E402
from live_track_ships.sources import nmea                    # noqa: E402
from live_track_ships.sources.nmea import (                  # noqa: E402
    Decoder, NmeaUdpSource, StationStats)

passed = failed = 0
NOW = dt.datetime(2026, 11, 16, 5, 0, 0, tzinfo=dt.timezone.utc)


def check(label, got, want=True):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}"
          + ("" if ok else f"\n         got {got!r}\n         want {want!r}"))


def near(a, b, tol=0.001):
    return a is not None and b is not None and abs(a - b) <= tol


class Clock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


def enc(**fields):
    return [s.encode() for s in encode_dict(fields, talker_id="AI", radio_channel="A")]


def one(dec, lines):
    out = []
    for raw in lines:
        o = dec.line(raw, NOW)
        if o is not None:
            out.append(o)
    return out


# ---------------------------------------------------------------- real sentences
print("=== real sentences ===")
dec = Decoder(StaticCache())
o = dec.line(b"!AIVDM,1,1,,B,15M67FC000G?ufbE`FepT@3n00Sa,0*5C", NOW)
check("type 1 gives a vessel", o is not None and o.kind, "vessel")
check("MMSI as nine digits", o.identity, "366053209")
check("latitude", near(o.latitude, 37.802118))
check("longitude", near(o.longitude, -122.341618))
check("speed 0 kn is 0 km/h, not unavailable", o.speed_kmh, 0.0)
check("course 219.3", near(o.course_deg, 219.3))
check("navigational status 3", o.nav_status, 3)
check("rate of turn omitted (not verified, D0)", o.rate_of_turn_dps, None)
check("raw message type for object_kind", o.raw_message_type, "PositionReport")
check("source domain", o.source, "live_track_ships")
check("position time is the arrival time", o.observed_at, NOW)
check("max_extrapolation_s absent", o.max_extrapolation_s, None)

p1 = b"!AIVDM,2,1,4,A,55O0W7`00001L@gCWGA2uItLth@DqtL5@F22220j1h742t0Ht0000000,0*08"
p2 = b"!AIVDM,2,2,4,A,000000000000000,2*20"
check("first half of type 5 yields nothing", dec.line(p1, NOW), None)
check("second half yields nothing (statics only)", dec.line(p2, NOW), None)
rec = dec._static.lookup("368060190")
check("type 5 name into the statics", rec is not None and rec.name, "P/V_GOLDEN_GATE")
check("type 5 type 50 (pilot)", rec.type, 50)
check("type 5 call sign", rec.call_sign, "WDK4954")
check("type 5 length 14+7", rec.length_m, 21.0)
check("type 5 beam 4+2", rec.beam_m, 6.0)
check("imo 0 is not stored", rec.imo, None)
check("empty destination is None", rec.destination, None)

dec2 = Decoder(StaticCache())
check("halves in reverse order still join",
      (dec2.line(p2, NOW), dec2.line(p1, NOW), dec2._static.lookup("368060190") is not None),
      (None, None, True))

# ---------------------------------------------------------------- sentinels
print("=== unavailable values (B3) ===")
dec = Decoder(StaticCache())
o = one(dec, enc(msg_type=1, mmsi=244650000, lat=52.1, lon=4.3, speed=102.3,
                 course=360, heading=511, status=15))[0]
check("speed 102.3 -> None", o.speed_kmh, None)
check("course 360 -> None", o.course_deg, None)
check("heading 511 -> None", o.heading_deg, None)
check("status 15 -> None", o.nav_status, None)
check("a real heading kept", one(dec, enc(msg_type=1, mmsi=244650000, lat=52.1, lon=4.3,
                                          heading=87, speed=12.5, course=90.4))[0].heading_deg, 87)
o = one(dec, enc(msg_type=1, mmsi=244650000, lat=52.1, lon=4.3, speed=10, course=0))[0]
check("10 kn -> 18.52 km/h", near(o.speed_kmh, 18.52))
check("course 0 is north, not unavailable", o.course_deg, 0.0)
check("latitude 91 -> no observation", one(dec, enc(msg_type=1, mmsi=244650000, lat=91, lon=4.3)), [])
check("longitude 181 -> no observation", one(dec, enc(msg_type=1, mmsi=244650000, lat=52.1, lon=181)), [])

# ---------------------------------------------------------------- statics join
print("=== statics join onto positions ===")
cache = StaticCache()
dec = Decoder(cache)
one(dec, enc(msg_type=5, mmsi=219000123, shipname="TYCHO BRAHE", callsign="OXYZ",
             ship_type=60, to_bow=80, to_stern=31, to_port=14, to_starboard=14,
             destination="HELSINGBORG", draught=5.4, imo=9007116))
o = one(dec, enc(msg_type=1, mmsi=219000123, lat=56.04, lon=12.69, speed=11, course=80))[0]
check("name joined", o.name, "TYCHO BRAHE")
check("type joined", o.ship_type, 60)
check("length joined", o.length_m, 111.0)
check("destination joined", o.destination, "HELSINGBORG")
check("imo joined", o.imo, 9007116)
check("draught joined", near(o.draught_m, 5.4, 0.05))
check("one cache: another source sees it too", cache.lookup("219000123").name, "TYCHO BRAHE")
one(dec, enc(msg_type=5, mmsi=219000124, ship_type=0, to_bow=0, to_stern=0))
check("type 0 is unavailable, not a type", cache.lookup("219000124").type, None)
one(dec, enc(msg_type=5, mmsi=219000125, to_bow=400, to_stern=200))
check("600 m is a bad record: no length", getattr(cache.lookup("219000125"), "length_m", None), None)

print("=== Class B ===")
cache = StaticCache()
dec = Decoder(cache)
one(dec, enc(msg_type=24, mmsi=338123456, partno=1, ship_type=37, callsign="WDA1234",
             to_bow=8, to_stern=4, to_port=2, to_starboard=2))
one(dec, enc(msg_type=24, mmsi=338123456, partno=0, shipname="SEADOG IV"))
o = one(dec, enc(msg_type=18, mmsi=338123456, lat=41.89, lon=-87.6, speed=6.2, course=45, heading=44))[0]
check("type 18 a vessel", o.kind, "vessel")
check("type 18 raw type", o.raw_message_type, "StandardClassBPositionReport")
check("24B type joined (37 pleasure)", o.ship_type, 37)
check("24A name joined", o.name, "SEADOG IV")
check("24B length", o.length_m, 12.0)
check("24A alone never creates a record",
      (one(dec, enc(msg_type=24, mmsi=338999999, partno=0, shipname="LONELY")), cache.lookup("338999999")),
      ([], None))
o = one(dec, enc(msg_type=19, mmsi=338777777, lat=41.9, lon=-87.61, speed=3, course=10,
                 heading=12, shipname="ODYSSEY", ship_type=60, to_bow=30, to_stern=30))[0]
check("type 19 a vessel with its own name", o.name, "ODYSSEY")
check("type 19 type", o.ship_type, 60)
check("type 19 length", o.length_m, 60.0)
check("type 19 statics kept", cache.lookup("338777777").type, 60)

print("=== not vessels ===")
dec = Decoder(StaticCache())
o = one(dec, enc(msg_type=21, mmsi=993672001, aid_type=1, name="CHICAGO HARBOR LT", lat=41.89, lon=-87.59))[0]
check("type 21 an aid to navigation", o.kind, "aton")
check("type 21 name", o.name, "CHICAGO HARBOR LT")
o = one(dec, enc(msg_type=4, mmsi=3669999, lat=41.88, lon=-87.62))[0]
check("type 4 a base station", o.kind, "base_station")
check("type 4 MMSI padded to nine", o.identity, "003669999")
o = one(dec, enc(msg_type=9, mmsi=111232506, alt=300, speed=120, lat=57.6, lon=11.8, course=270))[0]
check("type 9 a SAR aircraft", o.kind, "sar_aircraft")
check("type 9 speed 120 kn", near(o.speed_kmh, 222.24))
o = one(dec, enc(msg_type=27, mmsi=257123000, lat=70.5, lon=19.2, speed=12, course=33, status=0))[0]
check("type 27 long range a vessel", (o.kind, o.raw_message_type), ("vessel", "LongRangeAisBroadcastMessage"))
check("type 7 (binary acknowledge) counted and ignored",
      (one(dec, enc(msg_type=7, mmsi=244650000, mmsi1=244660000)), dec.counts["ignored"]),
      ([], 1))

print("=== damaged input ===")
dec = Decoder(StaticCache())
check("garbage line ignored", dec.line(b"hello world", NOW), None)
check("bad checksum ignored", dec.line(b"!AIVDM,1,1,,B,15M67FC000G?ufbE`FepT@3n00Sa,0*00", NOW), None)
check("both counted invalid", dec.counts["invalid"], 2)
check("$GPRMC from a GPS is not AIS: ignored, no crash", dec.line(
    b"$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A", NOW), None)
obs = dec.feed(b"!AIVDM,1,1,,B,15M67FC000G?ufbE`FepT@3n00Sa,0*5C\r\n\r\n" + enc(
    msg_type=1, mmsi=244650000, lat=52.1, lon=4.3)[0] + b"\n", NOW)
check("one datagram, two lines, two vessels", [o.identity for o in obs], ["366053209", "244650000"])
clock = Clock()
dec = Decoder(StaticCache(), clock=clock)
dec.line(p1, NOW)
clock.t += nmea.FRAGMENT_TTL_S + 1
dec.line(b"!AIVDM,1,1,,B,15M67FC000G?ufbE`FepT@3n00Sa,0*5C", NOW)
check("an orphaned half is dropped after the TTL", dec.counts["fragments_dropped"], 1)
check("and a late second half no longer completes it", dec.line(p2, NOW), None)
check("no record from a half message", dec._static.lookup("368060190"), None)

# ---------------------------------------------------------------- station figures
print("=== station figures ===")
clock = Clock()
st = StationStats(41.8995, -87.9403, clock=clock)
dec = Decoder(StaticCache())
near_v = one(dec, enc(msg_type=1, mmsi=366000001, lat=41.95, lon=-87.94))[0]
far_v = one(dec, enc(msg_type=1, mmsi=366000002, lat=42.40, lon=-87.94))[0]
aton = one(dec, enc(msg_type=21, mmsi=993672002, lat=43.0, lon=-87.9, name="FAR LIGHT"))[0]
st.saw_messages(3, NOW)
for o in (near_v, far_v, aton):
    st.saw(o)
s = st.snapshot()
check("messages per minute", s["messages_per_minute"], 3)
check("vessels heard (an aid to navigation is not one)", s["vessels_heard"], 2)
check("farthest is the far vessel", s["farthest_mmsi"], "366000002")
check("farthest about 55.7 km", near(s["farthest_km"], 55.7, 0.3))
check("last message time", s["last_message"], NOW)
clock.t += 61
check("a minute later the rate is 0", st.snapshot()["messages_per_minute"], 0)
check("but the vessels still count", st.snapshot()["vessels_heard"], 2)
clock.t += 600
s = st.snapshot()
check("ten minutes later nobody is heard", (s["vessels_heard"], s["farthest_km"]), (0, None))
check("the last message time stays", s["last_message"], NOW)


# ---------------------------------------------------------------- the UDP path
print("=== over UDP ===")


async def udp():
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    probe.bind(("127.0.0.1", 0))
    port = probe.getsockname()[1]
    probe.close()
    src = NmeaUdpSource(port, 41.8995, -87.9403, StaticCache(), host="127.0.0.1")
    got = []

    async def read():
        async for o in src.observations():
            got.append(o)
            if len(got) == 3:
                return

    task = asyncio.create_task(read())
    await asyncio.sleep(0.2)
    tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    tx.sendto(p1, ("127.0.0.1", port))
    tx.sendto(p2, ("127.0.0.1", port))
    tx.sendto(b"!AIVDM,1,1,,B,15M67FC000G?ufbE`FepT@3n00Sa,0*5C\r\n", ("127.0.0.1", port))
    for line in enc(msg_type=1, mmsi=368060190, lat=37.81, lon=-122.47, speed=8, course=200):
        tx.sendto(line + b"\r\n", ("127.0.0.1", port))
    tx.sendto(enc(msg_type=21, mmsi=993669001, lat=37.8, lon=-122.4, name="ALCATRAZ")[0], ("127.0.0.1", port))
    await asyncio.wait_for(task, 5)
    check("three objects arrived over UDP", [o.identity for o in got],
          ["366053209", "368060190", "993669001"])
    check("the pilot boat joined to its type 5 sent before it", got[1].name, "P/V_GOLDEN_GATE")
    s = src.stats.snapshot()
    check("station counted 4 messages", s["messages_per_minute"], 4)
    check("station heard 2 vessels", s["vessels_heard"], 2)
    check("datagrams counted", src.stats.datagrams, 5)
    # a second source on the same port cannot open it, and says so
    src2 = NmeaUdpSource(port, 0, 0, StaticCache(), host="127.0.0.1")
    t2 = asyncio.create_task(src2.observations().__anext__())
    await asyncio.sleep(0.3)
    check("a busy port is reported, not fatal", bool(src2.bind_error) and not t2.done())
    t2.cancel()
    await src.close()
    check("closed: the port is free again", src._transport, None)
    s3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s3.bind(("127.0.0.1", port))
        check("the port can be bound after close", True)
    finally:
        s3.close()

asyncio.run(udp())

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
