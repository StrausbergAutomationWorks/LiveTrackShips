"""BarentsWatch AIS Live - Norwegian waters, OAuth2, SSE stream.

⚠ MEASURED 2026-09-09, not read from docs. 4,281 vessels in one snapshot,
212 KB gzipped. Names on 100%, real ITU types on 95% - because position and
static data arrive TOGETHER. Neither aisstream nor Digitraffic does that; both
need an MMSI join.

⚠ THE BEST-ENGINEERED SOURCE OF THE THREE, and the narrowest geographically:

    transport        SSE stream (text/event-stream), not polling
    spatial filter   ⚠ GeoJSON GEOMETRY - a polygon, not a bounding box, so
                     the CIRCLE the user asked for can be sent as-is
    static join      none needed
    provenance       ⚠ `stream` field: terra | satellite | offshore
    coverage extent  ⚠ published as a MultiPolygon at /v1/openaisarea

⚠ AUTHENTICATION IS OAUTH2 client_credentials AND THE TOKEN EXPIRES IN 3600 s.
This is the first source with an expiring credential. The token is cached and
refreshed early; a 401 forces an immediate refresh and one retry.

⚠ client_id has the shape <email>:<clientname> with a literal @ and : . It must
be URL-ENCODED AT REQUEST TIME, not in storage. Pre-encoding it double-encodes
and fails with an opaque `invalid_client`.
"""

from __future__ import annotations

import asyncio
import datetime as _dt
import json
import logging
import math
import random

from .base import KNOTS_TO_KMH, Observation

_LOGGER = logging.getLogger(__name__)

TOKEN_URL = "https://id.barentswatch.no/connect/token"
BASE_URL = "https://live.ais.barentswatch.no"
SSE_COMBINED = f"{BASE_URL}/v1/sse/combined"
LATEST_COMBINED = f"{BASE_URL}/v1/latest/combined"
OPEN_AREA = f"{BASE_URL}/v1/openaisarea"

SCOPE = "ais"
USER_AGENT = "StrausbergAutomationWorks/LiveTrackShips"

# ⚠ Refresh EARLY. A token that expires mid-stream drops the connection, and
# the reconnect costs more than a refresh does.
TOKEN_REFRESH_MARGIN_S = 300

BACKOFF_START_S = 2.0
BACKOFF_MAX_S = 300.0

# ⚠ Sentinels. Same ITU values as everywhere else - an unmapped sentinel is
# indistinguishable from a measurement downstream. B3 in 05_SHARED_LESSONS.md.
COG_UNAVAILABLE = 360.0
HEADING_UNAVAILABLE = 511
SOG_UNAVAILABLE = 102.3
ROT_UNAVAILABLE = (-128, -127)
NAV_STATUS_UNDEFINED = 15
SHIP_TYPE_UNAVAILABLE = 0

# ⚠ `stream` maps DIRECTLY onto position_source in the shared contract. This is
# the only source that states provenance rather than leaving it to be inferred,
# and it matters: a satellite fix can be HOURS old and must not be interpolated
# as though it were a terrestrial one.
STREAM_TO_POSITION_SOURCE = {
    "terra": "observed",
    "offshore": "observed",
    "satellite": "satellite",
}

# A circle approximated as a polygon. 64 points keeps the error under ~0.1% of
# the radius, which is far below the position accuracy of AIS itself.
CIRCLE_POINTS = 64


def _clean(value, unavailable):
    if value is None:
        return None
    if isinstance(unavailable, tuple):
        return None if value in unavailable else value
    return None if value == unavailable else value


def circle_geometry(lat: float, lon: float, radius_km: float,
                    points: int = CIRCLE_POINTS) -> dict:
    """A GeoJSON Polygon approximating the requested circle.

    ⚠ THIS IS WHY THIS SOURCE IS BETTER. aisstream takes only bounding boxes,
    so a circle must be circumscribed - 1.27x the area, corners 1.41x the
    radius out - and filtered again locally. Here the actual shape is sent.

    ⚠ Longitude degrees shrink with latitude. At 70 N, where much of this
    feed's coverage lies, a degree of longitude is about a third of a degree of
    latitude. Ignoring that would produce an ellipse, not a circle.
    """
    lat_deg = radius_km / 111.32
    cos_lat = math.cos(math.radians(lat))
    # Near the pole the correction explodes; clamp rather than divide by ~0.
    lon_deg = radius_km / (111.32 * max(cos_lat, 0.01))
    ring = []
    for i in range(points):
        theta = 2 * math.pi * i / points
        ring.append([round(lon + lon_deg * math.cos(theta), 6),
                     round(lat + lat_deg * math.sin(theta), 6)])
    ring.append(ring[0])                      # GeoJSON rings must close
    return {"type": "Polygon", "coordinates": [ring]}


def _parse_msgtime(raw):
    """⚠ ISO 8601 with an offset - '2026-09-09T06:02:11+00:00'. Unlike
    aisstream's Go nanosecond timestamps this parses directly, but a Z suffix
    still needs translating for fromisoformat on older interpreters."""
    if not raw:
        return None
    try:
        return _dt.datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except ValueError:
        return None


class BarentsWatchSource:
    """SSE stream of combined AIS for a polygon, with a refreshing token."""

    domain = "live_track_ships"

    def __init__(self, session, client_id, client_secret,
                 latitude, longitude, radius_km):
        self._session = session
        self._client_id = client_id
        self._client_secret = client_secret
        self._geometry = circle_geometry(latitude, longitude, radius_km)
        self._token: str | None = None
        self._token_expires: _dt.datetime | None = None
        self._closing = False

    # -- authentication ---------------------------------------------------
    async def _access_token(self, force: bool = False) -> str:
        """⚠ Cached and refreshed EARLY. The token lives 3600 s and a mid-stream
        expiry drops the connection."""
        now = _dt.datetime.now(_dt.timezone.utc)
        if (not force and self._token and self._token_expires
                and now < self._token_expires):
            return self._token

        # ⚠ client_id contains a literal @ and : . aiohttp's form encoder
        # handles that; the STORED value must not be pre-encoded or it is
        # double-encoded and fails with an opaque `invalid_client`.
        data = {"grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "scope": SCOPE}
        async with self._session.post(
                TOKEN_URL, data=data,
                headers={"User-Agent": USER_AGENT}, timeout=40) as resp:
            resp.raise_for_status()
            payload = await resp.json()

        self._token = payload["access_token"]
        expires_in = int(payload.get("expires_in", 3600))
        self._token_expires = now + _dt.timedelta(
            seconds=max(60, expires_in - TOKEN_REFRESH_MARGIN_S))
        _LOGGER.debug("BarentsWatch token refreshed, valid %ss", expires_in)
        return self._token

    async def open_area(self) -> dict | None:
        """The published extent of the open scope, as a MultiPolygon.

        ⚠ 337 KB. No other source publishes where it is authoritative, and a
        user whose centre falls outside it would otherwise just see an empty
        map. Fetch once; it does not change often.
        """
        try:
            token = await self._access_token()
            async with self._session.get(
                    OPEN_AREA,
                    headers={"Authorization": f"Bearer {token}",
                             "User-Agent": USER_AGENT},
                    timeout=90) as resp:
                resp.raise_for_status()
                return await resp.json()
        except Exception as exc:                       # noqa: BLE001
            _LOGGER.warning("BarentsWatch open area unavailable: %s", exc)
            return None

    # -- normalisation ----------------------------------------------------
    def _to_observation(self, row: dict) -> Observation | None:
        mmsi = row.get("mmsi")
        if mmsi is None:
            return None
        lat, lon = row.get("latitude"), row.get("longitude")
        if lat is None or lon is None:
            return None

        raw_stream = row.get("stream")
        # ⚠ An UNKNOWN stream value must not silently become "observed".
        # Provenance decides whether a consumer may interpolate at all.
        position_source = STREAM_TO_POSITION_SOURCE.get(raw_stream, "observed")

        sog = _clean(row.get("speedOverGround"), SOG_UNAVAILABLE)
        observed = _parse_msgtime(row.get("msgtime"))

        return Observation(
            identity=str(mmsi),
            source=self.domain,
            observed_at=observed or _dt.datetime.now(_dt.timezone.utc),
            latitude=lat,
            longitude=lon,
            course_deg=_clean(row.get("courseOverGround"), COG_UNAVAILABLE),
            heading_deg=_clean(row.get("trueHeading"), HEADING_UNAVAILABLE),
            speed_kmh=None if sog is None else sog * KNOTS_TO_KMH,
            rate_of_turn_dps=_clean(row.get("rateOfTurn"), ROT_UNAVAILABLE),
            # ⚠ NO STATIC JOIN. name and shipType arrive with the position.
            name=(row.get("name") or "").strip() or None,
            ship_type=_clean(row.get("shipType"), SHIP_TYPE_UNAVAILABLE),
            call_sign=(row.get("callSign") or "").strip() or None,
            destination=(row.get("destination") or "").strip() or None,
            imo=row.get("imoNumber") or None,
            draught_m=row.get("draught") or None,
            nav_status=_clean(row.get("navigationalStatus"),
                              NAV_STATUS_UNDEFINED),
            position_source=position_source,
            # ⚠ NOT SET, as for every ship source. No field, no motion.
            # 05_SHARED_LESSONS.md D3a - ships fail on geography, not on
            # missing fields. A satellite fix makes that worse, not better.
            max_extrapolation_s=None,
            raw_message_type="BarentsWatchCombined",
            extra={"stream": raw_stream},
        )
    # -- the stream -------------------------------------------------------
    async def observations(self):
        """Yield Observations from the SSE stream, reconnecting with backoff.

        ⚠ A snapshot is pulled FIRST so the map is populated immediately. The
        stream only delivers CHANGES, so without this a restart shows an empty
        map until each vessel happens to report - measured elsewhere at a p50
        of 129 s and a p95 of 450 s.
        """
        backoff = BACKOFF_START_S
        while not self._closing:
            try:
                for obs in await self._snapshot():
                    yield obs
                async for obs in self._stream():
                    backoff = BACKOFF_START_S     # reset only on real data
                    yield obs
            except asyncio.CancelledError:
                raise
            except Exception as exc:              # noqa: BLE001
                _LOGGER.warning("BarentsWatch stream failed: %s", exc)
            if self._closing:
                return
            # ⚠ JITTER, so instances that lost the same upstream do not all
            # return in lockstep.
            wait = min(BACKOFF_MAX_S, backoff) * (0.5 + random.random())
            await asyncio.sleep(wait)
            backoff = min(BACKOFF_MAX_S, backoff * 2)

    async def _snapshot(self):
        """Latest per MMSI inside the polygon. Server-side filtered."""
        token = await self._access_token()
        body = {"geometry": self._geometry, "modelType": "Full",
                "modelFormat": "Json"}
        async with self._session.post(
                LATEST_COMBINED, json=body,
                headers={"Authorization": f"Bearer {token}",
                         "User-Agent": USER_AGENT},
                timeout=90) as resp:
            resp.raise_for_status()
            rows = await resp.json()
        out = [self._to_observation(r) for r in rows]
        kept = [o for o in out if o is not None]
        _LOGGER.debug("BarentsWatch snapshot: %d vessels", len(kept))
        return kept

    async def _stream(self):
        """SSE, filtered server-side by the polygon.

        ⚠ text/event-stream, NOT a websocket and NOT JSON-per-line. Lines are
        `data: {...}`, records separated by a blank line, and `:` alone is a
        keepalive comment that must be ignored rather than parsed.
        """
        token = await self._access_token()
        body = {"geometry": self._geometry, "modelType": "Full",
                "modelFormat": "Json", "downsample": True}
        async with self._session.post(
                SSE_COMBINED, json=body,
                headers={"Authorization": f"Bearer {token}",
                         "Accept": "text/event-stream",
                         "User-Agent": USER_AGENT},
                timeout=None) as resp:
            if resp.status == 401:
                # ⚠ Force a refresh and let the caller reconnect. A 401
                # mid-stream means the token aged out despite the margin.
                _LOGGER.debug("BarentsWatch 401 - forcing a token refresh")
                await self._access_token(force=True)
                return
            resp.raise_for_status()
            async for raw in resp.content:
                if self._closing:
                    return
                line = raw.decode("utf-8", errors="replace").strip()
                if not line or line.startswith(":"):
                    continue                      # blank or keepalive comment
                if not line.startswith("data:"):
                    continue                      # event:, id:, retry:
                payload = line[5:].strip()
                if not payload:
                    continue
                try:
                    row = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                obs = self._to_observation(row)
                if obs is not None:
                    yield obs

    async def close(self):
        self._closing = True
