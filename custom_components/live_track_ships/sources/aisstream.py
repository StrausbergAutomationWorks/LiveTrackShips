"""aisstream.io - the primary source. Global, free, websocket push.

⚠ EVERY CONSTANT AND EVERY TRAP BELOW WAS MEASURED, NOT READ FROM DOCS.
See 30_Integrations/Live_Track_Ships/SSOT.md sections 5, 6 and 14.

THE SERVICE
  * 3 subscribed connections per account, and 3 open connections per
    ORIGINATING IP applied BEFORE authentication. ⚠ A dev machine and the HA
    host behind one NAT share that budget. A config-entry reload that does not
    tear down cleanly leaks against it.
  * The subscription must arrive within 3 s of connect or the socket closes.
  * Subscription updates REPLACE, never merge, and are capped at 1/second;
    faster CLOSES THE CONNECTION. An options flow re-subscribing per keystroke
    is a self-inflicted disconnect.
  * From September 2026 uncompressed connections face per-user bandwidth
    limits, so permessage-deflate is not optional.
  * ⚠ NO SLA AND NO DURABLE REPLAY. A vessel that stops appearing has not
    necessarily left.

⚠ EVERY FRAME IS BINARY. 133 of 133 across every capture, zero TEXT. Code
written against WSMsgType.TEXT sees an EMPTY STREAM WITH NO ERROR - the same
silent-failure signature as a BOM'd manifest.

⚠ NO FilterMessageTypes IS SENT. Filtering would BLOCK a type the day the
service started publishing it. Only five of twenty-five types have ever
arrived; the other twenty are handled by ignoring what we cannot interpret.
"""

from __future__ import annotations

import asyncio
import datetime as _dt
import json
import logging
import random

from .base import KNOTS_TO_KMH, Observation, rot_to_dps

_LOGGER = logging.getLogger(__name__)

URL = "wss://stream.aisstream.io/v0/stream"

# ⚠ aiohttp compress=15 negotiates permessage-deflate. Verified two ways: the
# handshake returned permessage-deflate;server_no_context_takeover;
# client_no_context_takeover AND the server reported CompressionEnabled: true.
COMPRESS_WBITS = 15

SUBSCRIBE_WITHIN_S = 3
MIN_SECONDS_BETWEEN_SUBSCRIBES = 1.0

# ⚠ Reconnect with backoff AND JITTER. Without jitter, every instance that
# lost the same upstream returns in lockstep.
BACKOFF_START_S = 2.0
BACKOFF_MAX_S = 300.0

POSITION_TYPES = frozenset({
    "PositionReport", "StandardClassBPositionReport",
    "ExtendedClassBPositionReport", "LongRangeAisBroadcastMessage",
})
STATIC_TYPES = frozenset({"ShipStaticData", "StaticDataReport"})

# ⚠ AIS encodes "unavailable" IN BAND. An unmapped sentinel is
# indistinguishable from a measurement downstream. B3 in 05_SHARED_LESSONS.md.
COG_UNAVAILABLE = 360.0
HEADING_UNAVAILABLE = 511
SOG_UNAVAILABLE = 102.3
# ⚠ Rate of turn is decoded by `rot_to_dps` in base.py and has NO sentinel
# constant here, deliberately. Four private copies of that list held three
# different values - SSOT.md items 18 and 20. Do not add one back.
NAV_STATUS_UNDEFINED = 15
SHIP_TYPE_UNAVAILABLE = 0

# ⚠ A record longer than any ship ever built is a bad record, not a big ship.
MAX_PLAUSIBLE_LENGTH_M = 500.0

# Static data is broadcast every ~6 minutes and arrives for a small minority of
# vessels at any moment - 13 of 114 in three minutes. Cache it generously.
STATIC_CACHE_MAX = 5000


def _clean(value, unavailable):
    if value is None:
        return None
    if isinstance(unavailable, tuple):
        return None if value in unavailable else value
    return None if value == unavailable else value


def _parse_time(raw):
    """⚠ time_utc is a Go timestamp with NANOSECOND precision, e.g.
    '2026-09-02 22:05:43.933000000 +0000 UTC'. Python's %f accepts at most SIX
    fractional digits, so strptime FAILS on it unmodified. Truncate first.
    This cost a broken analysis script before it was caught."""
    if not raw:
        return None
    try:
        s = raw.split(" +")[0].strip()
        if "." in s:
            head, frac = s.split(".", 1)
            s = f"{head}.{frac[:6]}"
        return _dt.datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f").replace(
            tzinfo=_dt.timezone.utc)
    except (ValueError, AttributeError):
        return None


class AisStreamSource:
    """Long-lived websocket, yielding normalised Observations."""

    domain = "live_track_ships"

    def __init__(self, session, api_key, boxes):
        self._session = session
        self._key = api_key
        self._boxes = boxes
        self._static: dict[str, dict] = {}
        self._closing = False
        self.compression_enabled: bool | None = None

    # -- normalisation -----------------------------------------------------
    @staticmethod
    def _meta(obj):
        """⚠ THE PUBLISHED DOCS ARE WRONG ABOUT CASING. The example shows
        Latitude/Longitude in MetaData; the live API sends `latitude`,
        `longitude`, `time_utc` LOWERCASE beside `MMSI` and `ShipName`
        UPPERCASE. Inside `Message` it is Latitude/Longitude capitalised.
        Mixed casing in one payload."""
        return obj.get("MetaData") or {}

    def _remember_static(self, mt, body, mmsi):
        """⚠ TWO different static messages, and Class B splits into parts.
        Class A sends ShipStaticData (Msg 5) every ~6 min and it is reliable.
        Class B sends StaticDataReport (Msg 24) where Part A is the NAME and
        Part B is the TYPE - and units transmit Part A far more reliably.
        Measured: 42% of Class B sent static, only 1 in 5 of those carried a
        usable type. Type-driven features must degrade to unknown."""
        if len(self._static) > STATIC_CACHE_MAX:
            self._static.clear()          # bounded; cheapest correct eviction
        entry = self._static.setdefault(mmsi, {})
        if mt == "ShipStaticData":
            entry.update({
                "type": _clean(body.get("Type"), SHIP_TYPE_UNAVAILABLE),
                "call_sign": (body.get("CallSign") or "").strip() or None,
                "destination": (body.get("Destination") or "").strip() or None,
                "imo": body.get("ImoNumber") or None,
                "draught_m": body.get("MaximumStaticDraught") or None,
            })
            dim = body.get("Dimension") or {}
            entry.update(self._dimensions(dim))
        elif mt == "StaticDataReport":
            rb = body.get("ReportB") or {}
            # ⚠ ReportB.Valid is false with all-zero dimensions on real
            # traffic. PRESENCE OF A MESSAGE IS NOT PRESENCE OF ITS PAYLOAD.
            if rb.get("Valid"):
                t = _clean(rb.get("ShipType", rb.get("Type")),
                           SHIP_TYPE_UNAVAILABLE)
                if t is not None:
                    entry["type"] = t
                entry.update(self._dimensions(rb.get("Dimension") or {}))
                cs = (rb.get("CallSign") or "").strip()
                if cs:
                    entry["call_sign"] = cs

    @staticmethod
    def _dimensions(dim):
        a = dim.get("A") or 0
        b = dim.get("B") or 0
        c = dim.get("C") or 0
        d = dim.get("D") or 0
        length = float(a + b) if (a + b) else None
        beam = float(c + d) if (c + d) else None
        # ⚠ A+B is the length of the whole UNIT. SEA EAGLE II reports type 52
        # (tug) at 164 m - an articulated tug-barge broadcasting the pair, not
        # a 164 m tug. Deriving a size class from this misclassifies ATBs.
        if length and length > MAX_PLAUSIBLE_LENGTH_M:
            return {}
        return {"length_m": length, "beam_m": beam}

    def _to_observation(self, obj):
        mt = obj.get("MessageType")
        meta = self._meta(obj)
        mmsi = meta.get("MMSI")
        if mmsi is None:
            return None
        # ⚠ MMSI_String is a JSON NUMBER, not a string. The field name lies.
        mmsi = str(mmsi)
        body = (obj.get("Message") or {}).get(mt) or {}

        if mt in STATIC_TYPES:
            self._remember_static(mt, body, mmsi)
            return None
        if mt not in POSITION_TYPES:
            # ⚠ Anything else is IGNORED, never fatal. AtoN and base stations
            # have never arrived from this source, but if they start they must
            # not be treated as vessels - a buoy is a fixed object.
            return None

        lat, lon = meta.get("latitude"), meta.get("longitude")
        if lat is None or lon is None:
            return None

        sog = _clean(body.get("Sog"), SOG_UNAVAILABLE)
        static = self._static.get(mmsi, {})
        # ⚠ ShipName is space-padded INCONSISTENTLY - 'SEADOG IV           '
        # padded to 20, plain 'ODYSSEY' at length 7. And operators MANGLE names
        # to fit: 'ODYSSEY CHICAGO_IVER' is real data with a literal 0x5F, not
        # corruption. Strip it; NEVER try to repair it.
        name = (meta.get("ShipName") or "").strip() or None

        return Observation(
            identity=mmsi,
            source=self.domain,
            observed_at=_parse_time(meta.get("time_utc"))
            or _dt.datetime.now(_dt.timezone.utc),
            latitude=lat,
            longitude=lon,
            course_deg=_clean(body.get("Cog"), COG_UNAVAILABLE),
            heading_deg=_clean(body.get("TrueHeading"), HEADING_UNAVAILABLE),
            speed_kmh=None if sog is None else sog * KNOTS_TO_KMH,
            rate_of_turn_dps=rot_to_dps(body.get("RateOfTurn")),
            name=name,
            ship_type=static.get("type"),
            call_sign=static.get("call_sign"),
            # ⚠ Destination is UNCONSTRAINED FREE TEXT - 'USCHI><USCHI',
            # 'TWO HARBORS CH 74', 'TORONTO@ON'. Operator-typed, no code table.
            # DO NOT build a resolver; the airport pipeline has nothing to bite
            # on here.
            destination=static.get("destination"),
            imo=static.get("imo"),
            length_m=static.get("length_m"),
            beam_m=static.get("beam_m"),
            draught_m=static.get("draught_m"),
            nav_status=_clean(body.get("NavigationalStatus"),
                              NAV_STATUS_UNDEFINED),
            position_source="observed",
            # ⚠ max_extrapolation_s IS DELIBERATELY ABSENT. No field, no
            # motion. D3a in 05_SHARED_LESSONS.md.
            max_extrapolation_s=None,
            raw_message_type=mt,
        )


    # -- the connection ----------------------------------------------------
    async def observations(self):
        """Yield Observations forever, reconnecting with backoff and jitter."""
        import aiohttp

        backoff = BACKOFF_START_S
        while not self._closing:
            try:
                async for obs in self._one_connection(aiohttp):
                    backoff = BACKOFF_START_S      # reset only on real data
                    yield obs
            except asyncio.CancelledError:
                raise
            except Exception as exc:               # noqa: BLE001
                _LOGGER.warning("aisstream connection failed: %s", exc)
            if self._closing:
                return
            # ⚠ JITTER. Without it every instance that lost the same upstream
            # returns in lockstep and the service sees a thundering herd.
            wait = min(BACKOFF_MAX_S, backoff) * (0.5 + random.random())
            _LOGGER.debug("aisstream reconnecting in %.1f s", wait)
            await asyncio.sleep(wait)
            backoff = min(BACKOFF_MAX_S, backoff * 2)

    async def _one_connection(self, aiohttp):
        async with self._session.ws_connect(
                URL, compress=COMPRESS_WBITS, max_msg_size=0,
                heartbeat=None) as ws:

            # ⚠ WITHIN 3 SECONDS or the socket closes. Send it first, before
            # any other work.
            await ws.send_str(json.dumps({
                "APIKey": self._key,
                "BoundingBoxes": self._boxes,
            }))

            async for msg in ws:
                # ⚠ BINARY, ALWAYS. 133 of 133 frames measured, zero TEXT.
                # Reading msg.json() or expecting WSMsgType.TEXT yields an
                # empty stream with NO ERROR.
                if msg.type is aiohttp.WSMsgType.BINARY:
                    payload = msg.data.decode("utf-8", errors="replace")
                elif msg.type is aiohttp.WSMsgType.TEXT:
                    payload = msg.data          # tolerated, never observed
                elif msg.type in (aiohttp.WSMsgType.CLOSED,
                                  aiohttp.WSMsgType.CLOSING,
                                  aiohttp.WSMsgType.ERROR):
                    _LOGGER.info("aisstream closed the connection: %s",
                                 ws.close_code)
                    return
                else:
                    continue

                try:
                    obj = json.loads(payload)
                except json.JSONDecodeError:
                    continue

                if obj.get("MessageType") == "SubscriptionConfirmation":
                    inner = obj.get("Message") or {}
                    self.compression_enabled = inner.get("CompressionEnabled")
                    _LOGGER.debug("aisstream subscribed, compression=%s",
                                  self.compression_enabled)
                    continue

                obs = self._to_observation(obj)
                if obs is not None:
                    yield obs

    async def close(self):
        self._closing = True
