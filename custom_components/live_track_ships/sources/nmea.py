"""Your own AIS receiver: NMEA sentences over UDP (backlog 344, 2026-11-15).

DECIDED by Lee 2026-11-15 22:4x CST: NMEA over UDP only (the setting every
receiver and decoder already offers: AIS-catcher, rtl-ais, dAISy, OpenCPN,
Signal K); decoded by the pyais library (MIT; measured in the HA container
the same night: pyais 3.3.1, pure Python, its one dependency attrs, installed
from wheels); a station sensor. No receiver was available to test against:
the tests use real sentences and a replay sent over UDP from the PC.

The receiver sends `!AIVDM` / `!AIVDO` sentences to a UDP port on Home
Assistant. A datagram may hold several lines; a message may span several
sentences (multi-part, joined by sequence id and channel). What a decoded
message carries becomes the same Observation every other source yields:

  * 1, 2, 3 (Class A position), 18 (Class B position), 27 (long range): a
    position, joined to the vessel's statics;
  * 19 (Class B extended): a position, and its name, type and size into the
    statics;
  * 5 (Class A static and voyage), 24 (Class B static, parts A and B): the
    statics only, into the instance's shared StaticCache (the one aisstream
    fills and Ships saves), so a vessel heard by both is joined either way;
  * 21 (aid to navigation), 4 (base station), 9 (SAR aircraft): a fixed
    object or an aircraft, with the raw message type that object_kind reads.
  Anything else is counted and ignored, never fatal.

⚠ AIS ENCODES "UNAVAILABLE" IN BAND (05_SHARED_LESSONS B3): latitude 91,
longitude 181, speed 102.3 kn, course 360, heading 511, navigational status
15, ship type 0. pyais returns them as they are (measured: a heading of 1 and
course 219.3 came through raw), so they are mapped to None here.
⚠ RATE OF TURN IS OMITTED for this source: pyais converts the wire byte
itself, and its form was not verified tonight, so it is not passed as a
decoded rate (D0: absent beats wrong). Not measured: what pyais returns there.
⚠ THE POSITION TIME IS THE ARRIVAL TIME. A UDP sentence carries no date, and
the message's own UTC second (0-59) is not enough to place it.
"""

from __future__ import annotations

import asyncio
import collections
import datetime as _dt
import logging
import time

from .base import KNOTS_TO_KMH, Observation

_LOGGER = logging.getLogger(__name__)

# The port itself is const_flow.DEFAULT_UDP_PORT (10110, the one OpenCPN and most guides use).
FRAGMENT_TTL_S = 10.0             # parts of one message arrive together; older halves are dropped
RATE_WINDOW_S = 60.0
HEARD_WINDOW_S = 600.0

LAT_UNAVAILABLE = 91.0
LON_UNAVAILABLE = 181.0
SOG_UNAVAILABLE = 102.3
COG_UNAVAILABLE = 360.0
HEADING_UNAVAILABLE = 511
NAV_STATUS_UNDEFINED = 15
SHIP_TYPE_UNAVAILABLE = 0
SAR_SPEED_UNAVAILABLE = 1023
MAX_PLAUSIBLE_LENGTH_M = 500.0

POSITION_TYPES = {1: "PositionReport", 2: "PositionReport", 3: "PositionReport",
                  18: "StandardClassBPositionReport",
                  19: "ExtendedClassBPositionReport",
                  27: "LongRangeAisBroadcastMessage"}
OBJECT_TYPES = {21: "AidsToNavigationReport", 4: "BaseStationReport",
                9: "StandardSearchAndRescueAircraftReport"}


def _clean(value, unavailable):
    if value is None:
        return None
    try:
        return None if float(value) == float(unavailable) else value
    except (TypeError, ValueError):
        return None


def _int(value):
    """An IntEnum or int from pyais as a plain int; anything else None."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _text(value):
    """AIS 6-bit text: '@' pads it; spaces too. Stripped, never repaired."""
    s = str(value or "").replace("@", " ").strip()
    return s or None


def _dimensions(d) -> dict:
    a, b = d.get("to_bow") or 0, d.get("to_stern") or 0
    c, e = d.get("to_port") or 0, d.get("to_starboard") or 0
    length = float(a + b) if (a + b) else None
    beam = float(c + e) if (c + e) else None
    # ⚠ A record longer than any ship ever built is a bad record, not a big
    # ship (the same rule as the aisstream parser).
    if length and length > MAX_PLAUSIBLE_LENGTH_M:
        return {}
    return {"length_m": length, "beam_m": beam}


def _position(d):
    lat = _clean(d.get("lat"), LAT_UNAVAILABLE)
    lon = _clean(d.get("lon"), LON_UNAVAILABLE)
    if lat is None or lon is None or not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None, None
    return float(lat), float(lon)


class Decoder:
    """Lines of NMEA -> Observations. Joins multi-part messages, feeds the
    statics into the shared StaticCache, and counts what it saw."""

    def __init__(self, statics, domain="live_track_ships", clock=time.monotonic):
        from pyais import NMEAMessage     # imported here: the requirement installs on first load
        self._nmea = NMEAMessage
        self._static = statics
        self.domain = domain
        self._clock = clock
        self._parts: dict = {}            # (seq_id, channel, count) -> (first_seen, {frag_num: msg})
        self.counts = collections.Counter()

    def feed(self, data: bytes, now=None) -> list:
        """One datagram (one or more lines). Returns the Observations in it."""
        out = []
        for raw in data.splitlines():
            raw = raw.strip()
            if not raw:
                continue
            obs = self.line(raw, now)
            if obs is not None:
                out.append(obs)
        return out

    def line(self, raw: bytes, now=None):
        mono = self._clock()
        try:
            msg = self._nmea(raw)
        except Exception:                          # noqa: BLE001 - malformed is counted, never fatal
            self.counts["invalid"] += 1
            return None
        if not getattr(msg, "is_valid", True):
            self.counts["invalid"] += 1            # checksum failed
            return None
        self.counts["sentences"] += 1
        if self._parts:
            self._expire(mono)          # a half whose other half never came
        if not msg.is_single:
            key = (msg.seq_id, msg.channel, msg.frag_cnt)
            first, parts = self._parts.get(key, (mono, {}))
            if mono - first > FRAGMENT_TTL_S:
                first, parts = mono, {}
            parts[msg.frag_num] = msg
            self._parts[key] = (first, parts)
            if len(parts) < msg.frag_cnt:
                return None
            del self._parts[key]
            try:
                msg = self._nmea.assemble_from_iterable(
                    [parts[i] for i in sorted(parts)])
            except Exception:                      # noqa: BLE001
                self.counts["invalid"] += 1
                return None
        try:
            d = msg.decode().asdict()
        except Exception:                          # noqa: BLE001
            self.counts["undecodable"] += 1
            return None
        self.counts["messages"] += 1
        return self.message(d, now)

    def _expire(self, mono) -> None:
        for key in [k for k, (first, _p) in self._parts.items()
                    if mono - first > FRAGMENT_TTL_S]:
            del self._parts[key]
            self.counts["fragments_dropped"] += 1

    def message(self, d: dict, now=None):
        """One decoded message (pyais asdict) -> Observation or None."""
        mt = _int(d.get("msg_type"))
        mmsi = d.get("mmsi")
        if mt is None or mmsi is None:
            return None
        mmsi = f"{int(mmsi):09d}"
        now = now or _dt.datetime.now(_dt.timezone.utc)
        if mt == 5:
            fields = {"name": _text(d.get("shipname")),
                      "type": _clean(_int(d.get("ship_type")), SHIP_TYPE_UNAVAILABLE),
                      "call_sign": _text(d.get("callsign")),
                      "destination": _text(d.get("destination")),
                      "imo": _int(d.get("imo")) or None,
                      "draught_m": d.get("draught") or None}
            fields.update(_dimensions(d))
            self._static.update(mmsi, fields)
            return None
        if mt == 24:
            if _int(d.get("partno")) == 0:
                self._static.set_name(mmsi, _text(d.get("shipname")))
            else:
                fields = {}
                t = _clean(_int(d.get("ship_type")), SHIP_TYPE_UNAVAILABLE)
                if t is not None:
                    fields["type"] = t
                fields.update(_dimensions(d))
                cs = _text(d.get("callsign"))
                if cs:
                    fields["call_sign"] = cs
                if fields:
                    self._static.update(mmsi, fields)
            return None
        if mt in POSITION_TYPES:
            return self._vessel(mt, d, mmsi, now)
        if mt in OBJECT_TYPES:
            return self._object(mt, d, mmsi, now)
        self.counts["ignored"] += 1
        return None

    def _vessel(self, mt, d, mmsi, now):
        lat, lon = _position(d)
        if lat is None:
            return None
        name = _text(d.get("shipname")) if mt == 19 else None
        if mt == 19:
            fields = {"type": _clean(_int(d.get("ship_type")), SHIP_TYPE_UNAVAILABLE)}
            fields.update(_dimensions(d))
            if name:
                fields["name"] = name
            self._static.update(mmsi, {k: v for k, v in fields.items() if v is not None})
        rec = self._static.lookup(mmsi, name)
        st = ({k: getattr(rec, k) for k in rec.__slots__} if rec is not None else {})
        sog = _clean(d.get("speed"), SOG_UNAVAILABLE)
        return Observation(
            identity=mmsi, source=self.domain, observed_at=now,
            latitude=lat, longitude=lon,
            course_deg=_clean(d.get("course"), COG_UNAVAILABLE),
            heading_deg=_clean(_int(d.get("heading")), HEADING_UNAVAILABLE),
            speed_kmh=None if sog is None else float(sog) * KNOTS_TO_KMH,
            rate_of_turn_dps=None,
            name=name or st.get("name"),
            ship_type=st.get("type"), call_sign=st.get("call_sign"),
            destination=st.get("destination"), imo=st.get("imo"),
            length_m=st.get("length_m"), beam_m=st.get("beam_m"),
            draught_m=st.get("draught_m"),
            nav_status=_clean(_int(d.get("status")), NAV_STATUS_UNDEFINED),
            position_source="observed", max_extrapolation_s=None,
            raw_message_type=POSITION_TYPES[mt])

    def _object(self, mt, d, mmsi, now):
        lat, lon = _position(d)
        if lat is None:
            return None
        speed = course = None
        if mt == 9:
            s = _clean(_int(d.get("speed")), SAR_SPEED_UNAVAILABLE)
            speed = None if s is None else float(s) * KNOTS_TO_KMH
            course = _clean(d.get("course"), COG_UNAVAILABLE)
        return Observation(
            identity=mmsi, source=self.domain, observed_at=now,
            latitude=lat, longitude=lon, speed_kmh=speed, course_deg=course,
            name=_text(d.get("name")) if mt == 21 else None,
            position_source="observed", max_extrapolation_s=None,
            raw_message_type=OBJECT_TYPES[mt])


# ---------------------------------------------------------------------------
# The station: how the receiver itself is doing (Lee 2026-11-15: a station
# sensor). Everything the receiver sent counts, inside the circle or not: a
# receiver that hears 80 km is worth knowing about even with a 10 km circle.
class StationStats:
    """Messages per minute, vessels heard, the farthest one, the last arrival."""

    def __init__(self, centre_lat, centre_lon, clock=time.monotonic):
        from ..geo import distance_km
        self._distance = distance_km
        self._lat, self._lon = centre_lat, centre_lon
        self._clock = clock
        self._arrivals = collections.deque()          # monotonic times of decoded messages
        self._heard: dict[str, tuple] = {}            # mmsi -> (monotonic, distance_km)
        self.last_message = None                      # UTC datetime
        self.datagrams = 0
        self.dropped = 0

    def saw_messages(self, n, now_utc=None):
        if n <= 0:
            return
        t = self._clock()
        self._arrivals.extend([t] * n)
        self.last_message = now_utc or _dt.datetime.now(_dt.timezone.utc)

    def saw(self, obs):
        if obs.kind != "vessel":
            return
        self._heard[obs.identity] = (self._clock(), self._distance(
            self._lat, self._lon, obs.latitude, obs.longitude))

    def _trim(self):
        t = self._clock()
        while self._arrivals and t - self._arrivals[0] > RATE_WINDOW_S:
            self._arrivals.popleft()
        for m in [m for m, (seen, _d) in self._heard.items() if t - seen > HEARD_WINDOW_S]:
            del self._heard[m]

    def snapshot(self) -> dict:
        self._trim()
        far = max(self._heard.items(), key=lambda kv: kv[1][1], default=None)
        return {
            "messages_per_minute": len(self._arrivals),
            "vessels_heard": len(self._heard),
            "farthest_km": round(far[1][1], 1) if far else None,
            "farthest_mmsi": far[0] if far else None,
            "last_message": self.last_message,
        }


class _Protocol(asyncio.DatagramProtocol):
    def __init__(self, queue, stats):
        self._queue = queue
        self._stats = stats

    def datagram_received(self, data, addr):
        self._stats.datagrams += 1
        try:
            self._queue.put_nowait(data)
        except asyncio.QueueFull:
            # ⚠ Never block the event loop on a flood: drop and count it.
            self._stats.dropped += 1


QUEUE_MAX = 5000
BIND_RETRY_S = 30.0


class NmeaUdpSource:
    """Listens on a UDP port for the receiver's NMEA; yields Observations."""

    domain = "live_track_ships"

    def __init__(self, port, centre_lat, centre_lon, statics, host="0.0.0.0"):
        self.port = int(port)
        self.host = host
        if statics is None:
            from saw_livetrack.ais import StaticCache
            statics = StaticCache()
        self.decoder = Decoder(statics, self.domain)
        self.stats = StationStats(centre_lat, centre_lon)
        self.bind_error = None        # the last failure to open the port, for the sensor
        self._transport = None

    async def _open(self, queue):
        loop = asyncio.get_running_loop()
        warned = False
        while True:
            try:
                transport, _p = await loop.create_datagram_endpoint(
                    lambda: _Protocol(queue, self.stats),
                    local_addr=(self.host, self.port))
            except OSError as exc:
                # ⚠ Another program (or another entry) holds the port. Keep
                # trying: the other one may let go. Logged once, not every try.
                self.bind_error = str(exc)
                if not warned:
                    _LOGGER.error("Live Track Ships cannot listen on UDP port %s: %s; "
                                  "retrying every %ds", self.port, exc, BIND_RETRY_S)
                    warned = True
                await asyncio.sleep(BIND_RETRY_S)
                continue
            self.bind_error = None
            _LOGGER.info("Live Track Ships listening for AIS on UDP port %s", self.port)
            return transport

    async def observations(self):
        queue: asyncio.Queue = asyncio.Queue(maxsize=QUEUE_MAX)
        self._transport = await self._open(queue)
        try:
            while True:
                data = await queue.get()
                before = self.decoder.counts["messages"]
                found = self.decoder.feed(data)
                self.stats.saw_messages(self.decoder.counts["messages"] - before)
                for obs in found:
                    self.stats.saw(obs)
                    yield obs
        finally:
            await self.close()

    async def close(self) -> None:
        if self._transport is not None:
            self._transport.close()
            self._transport = None
