"""Fintraffic Digitraffic - open AIS for Finnish and Baltic waters.

⚠ MEASURED 2026-09-08. Open, no credentials, no registration. Digitraffic asks
callers to identify themselves with a Digitraffic-User header; send an honest
one. 1,149 vessels in 47 KB gzipped in 0.6 s.

⚠ THIS SOURCE IS REST-POLLED, NOT STREAMED. Two endpoints that must be joined
on MMSI:

    /api/ais/v1/locations   position, course, speed   GeoJSON FeatureCollection
    /api/ais/v1/vessels     name, type, destination   flat list

That is the same static-join problem as aisstream, made explicit by the API
rather than hidden inside one stream.

⚠ Server-side geographic filtering EXISTS: ?latitude=&longitude=&radius= .
Verified - a 50 km radius returned 83 features against 1,149 unfiltered.

⚠ DO NOT SEND ?from= . Measured: `from=1` returns 19,025 features and 7.9 MB.
That is the historical backlog, not the live set.

⚠ Digitraffic's roadmap says the current AIS integration is coming to end of
life and a new one will be needed, though it "should not affect end users".
Expect this adapter to need revisiting.
"""

from __future__ import annotations

import asyncio
import datetime as _dt
import logging

from .base import KNOTS_TO_KMH, Observation

_LOGGER = logging.getLogger(__name__)

BASE = "https://meri.digitraffic.fi"
LOCATIONS = "/api/ais/v1/locations"
VESSELS = "/api/ais/v1/vessels"

USER_AGENT = "StrausbergAutomationWorks/LiveTrackShips"

# ⚠ AIS sentinels as they arrive from THIS source. Each protocol encodes
# "unavailable" in band, and an unmapped sentinel is indistinguishable from a
# measurement downstream. See 05_SHARED_LESSONS.md B3.
COG_UNAVAILABLE = 360.0
HEADING_UNAVAILABLE = 511
SOG_UNAVAILABLE = 102.3
ROT_UNAVAILABLE = (-128, 128)
NAV_STATUS_UNDEFINED = 15
SHIP_TYPE_UNAVAILABLE = 0

# ⚠ The longest ship ever built was ~458 m (Seawise Giant). Anything beyond
# this is a bad record, not a big ship. Measured: VIRGINIABORG publishes
# A+B = 644 m alongside draught 0 and type 0.
MAX_PLAUSIBLE_LENGTH_M = 500.0

# Static data changes rarely; positions change constantly.
DEFAULT_POSITION_INTERVAL_S = 60
DEFAULT_STATIC_INTERVAL_S = 900


def _clean(value, unavailable):
    """Map a sentinel to None. Never let one reach a consumer."""
    if value is None:
        return None
    if isinstance(unavailable, tuple):
        return None if value in unavailable else value
    return None if value == unavailable else value


def _decimetres(value):
    """⚠ Digitraffic reports draught and reference points in DECIMETRES.
    draught: 80 is 8.0 m, not 80 m."""
    return None if value in (None, 0) else value / 10.0


class DigitrafficSource:
    """Polls Digitraffic and yields normalised Observations."""

    domain = "live_track_ships"

    def __init__(self, session, latitude, longitude, radius_km,
                 position_interval_s=DEFAULT_POSITION_INTERVAL_S,
                 static_interval_s=DEFAULT_STATIC_INTERVAL_S):
        self._session = session
        self._lat = latitude
        self._lon = longitude
        self._radius = radius_km
        self._position_interval = position_interval_s
        self._static_interval = static_interval_s
        self._static: dict[str, dict] = {}
        self._static_fetched_at: _dt.datetime | None = None

    # -- HTTP -------------------------------------------------------------
    async def _get(self, path, params=None):
        headers = {"Digitraffic-User": USER_AGENT,
                   "Accept-Encoding": "gzip"}
        async with self._session.get(BASE + path, params=params,
                                     headers=headers,
                                     timeout=60) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def _refresh_static(self):
        """⚠ Bounded by time, not by success. A failed static refresh must not
        stop positions - names are a nicety, positions are the product."""
        try:
            rows = await self._get(VESSELS)
        except Exception as exc:                      # noqa: BLE001
            _LOGGER.warning("Digitraffic static refresh failed: %s", exc)
            return
        self._static = {str(r["mmsi"]): r for r in rows if r.get("mmsi")}
        self._static_fetched_at = _dt.datetime.now(_dt.timezone.utc)
        _LOGGER.debug("Digitraffic static: %d vessels", len(self._static))

    # -- normalisation ----------------------------------------------------
    def _to_observation(self, feature):
        props = feature.get("properties") or {}
        geom = feature.get("geometry") or {}
        coords = geom.get("coordinates") or [None, None]
        mmsi = props.get("mmsi")
        if mmsi is None:
            return None

        # ⚠ `timestamp` here is the AIS SECOND-OF-MINUTE (0-59), NOT a time.
        # The real instant is timestampExternal, in MILLISECONDS. Digitraffic's
        # own docs warn that location and metadata use different units.
        ms = props.get("timestampExternal")
        observed = (_dt.datetime.fromtimestamp(ms / 1000, _dt.timezone.utc)
                    if ms else _dt.datetime.now(_dt.timezone.utc))

        static = self._static.get(str(mmsi), {})
        ship_type = _clean(static.get("shipType"), SHIP_TYPE_UNAVAILABLE)

        a = static.get("referencePointA") or 0
        b = static.get("referencePointB") or 0
        c = static.get("referencePointC") or 0
        d = static.get("referencePointD") or 0
        # ⚠⚠ UNITS DIFFER WITHIN THE SAME OBJECT. Measured 2026-09-08 across
        # 1,018 vessels:
        #   draught          is DECIMETRES  - 163 -> 16.3 m, a real deep draught
        #   referencePointA-D are METRES    - MEIN SCHIFF RELAX A+B = 333, a
        #                                     real cruise ship. As decimetres
        #                                     that would be 33 m, absurd next
        #                                     to a 9.7 m draught.
        # An earlier version divided BOTH by 10 and produced a 29 m cargo
        # fleet. Do not assume one unit governs a whole payload.
        length = float(a + b) if (a + b) else None
        beam = float(c + d) if (c + d) else None
        # ⚠ Bad records exist. VIRGINIABORG reports A+B = 644 m with draught 0
        # and type 0 - over twice the longest ship ever built. Clamp rather
        # than publish a nonsense dimension.
        if length and length > MAX_PLAUSIBLE_LENGTH_M:
            _LOGGER.debug("implausible length %s m for MMSI %s, dropped",
                          length, mmsi)
            length = beam = None
        # ⚠ A+B is the length of the whole UNIT. For an articulated tug-barge
        # that is the pair, not the hull. See 05_SHARED_LESSONS.md B2.

        sog = _clean(props.get("sog"), SOG_UNAVAILABLE)
        rot = _clean(props.get("rot"), ROT_UNAVAILABLE)

        return Observation(
            identity=str(mmsi),
            source=self.domain,
            observed_at=observed,
            latitude=coords[1],
            longitude=coords[0],
            course_deg=_clean(props.get("cog"), COG_UNAVAILABLE),
            heading_deg=_clean(props.get("heading"), HEADING_UNAVAILABLE),
            speed_kmh=None if sog is None else sog * KNOTS_TO_KMH,
            rate_of_turn_dps=rot,
            name=(static.get("name") or "").strip() or None,
            ship_type=ship_type,
            call_sign=(static.get("callSign") or "").strip() or None,
            destination=(static.get("destination") or "").strip() or None,
            imo=static.get("imo") or None,
            length_m=length,
            beam_m=beam,
            draught_m=_decimetres(static.get("draught")),
            nav_status=_clean(props.get("navStat"), NAV_STATUS_UNDEFINED),
            position_source="observed",
            # ⚠ NOT SET. A REST poll at 60 s is far coarser than the gaps that
            # already made ships ineligible for extrapolation. No field, no
            # motion. See 05_SHARED_LESSONS.md D3a.
            max_extrapolation_s=None,
            raw_message_type="DigitrafficLocation",
            extra={"pos_acc": props.get("posAcc"),
                   "raim": props.get("raim")},
        )

    # -- the loop ---------------------------------------------------------
    async def observations(self):
        while True:
            now = _dt.datetime.now(_dt.timezone.utc)
            stale = (self._static_fetched_at is None
                     or (now - self._static_fetched_at).total_seconds()
                     >= self._static_interval)
            if stale:
                await self._refresh_static()

            params = {"latitude": self._lat, "longitude": self._lon,
                      "radius": self._radius}
            try:
                data = await self._get(LOCATIONS, params)
            except Exception as exc:                  # noqa: BLE001
                _LOGGER.warning("Digitraffic poll failed: %s", exc)
                await asyncio.sleep(self._position_interval)
                continue

            for feature in data.get("features", []):
                obs = self._to_observation(feature)
                if obs is not None:
                    yield obs

            await asyncio.sleep(self._position_interval)

    async def close(self):
        return None
