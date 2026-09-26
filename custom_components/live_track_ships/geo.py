"""Centre-and-radius geometry for Live Track Ships.

The user gives a latitude, a longitude and a radius. The service only accepts
BOUNDING BOXES, so we request the box that circumscribes the circle and filter
to the true circle locally.

⚠ THE BOX IS BIGGER THAN THE CIRCLE. A circumscribing square has 4/pi ~ 1.27x
the area, and its corners sit radius*sqrt(2) ~ 1.41x away from the centre. A
vessel in a corner is INSIDE the box and OUTSIDE the radius. Without the local
distance filter the integration silently shows vessels up to 41% further away
than the user asked for.

⚠ WHY A RADIUS CAP IS NOT ENOUGH - measured 2026-09-02.

Observed vessel density varies by a factor of 5,729 across the four captures:

    Solent            43.4 vessels per 1000 km2
    Chicagoland        0.53
    Great Lakes        0.089
    worldwide          0.0076

A 50 km radius yields about 4 vessels over Chicagoland and about 341 over the
Solent. AREA IS A USELESS PREDICTOR OF LOAD. Therefore two independent limits:

  * MAX_RADIUS_KM bounds what we ASK FOR - bandwidth and parsing.
  * MAX_VESSELS bounds what we KEEP - entities, which is the real ceiling.

⚠ MAX_VESSELS is a VALIDATION CEILING, not a vessel count. This is the same
distinction that MAX_COUNT carries in flights_above, where conflating the
ceiling with the configured value has been a recurring error. Guard it here.
"""

from __future__ import annotations

import math

EARTH_RADIUS_KM = 6371.0
KM_PER_DEGREE_LAT = 111.32

# -- what the user may ask for ---------------------------------------------
MIN_RADIUS_KM = 1.0
DEFAULT_RADIUS_KM = 50.0     # Elmhurst to the Chicago River is 24-32 km
MAX_RADIUS_KM = 500.0        # a 500 km circle is ~785,000 km2; at Solent
                             # density that is ~34,000 vessels of INGEST, which
                             # is why the vessel ceiling below also exists

# -- what we are willing to keep -------------------------------------------
# ⚠ REVISED 2026-09-08. These bound the STATE MACHINE and the RECORDER, not
# the map. ha-map-card renders 154 markers comfortably and clustering is a
# runtime toggle, so display needs no cap at all.
DEFAULT_MAX_VESSELS = 1000
MAX_VESSELS = 5000           # ⚠ CEILING for validation. NOT a default, NOT a
                             # count. Nothing may treat this as "how many
                             # vessels there are". A 500 km circle at the
                             # measured Solent density holds ~34,000, so this
                             # is the backstop against a pathological radius.


class RadiusError(ValueError):
    """The requested radius is outside what the integration will accept."""


def validate_radius(radius_km: float) -> float:
    if not MIN_RADIUS_KM <= radius_km <= MAX_RADIUS_KM:
        raise RadiusError(
            f"radius {radius_km} km is outside {MIN_RADIUS_KM}-{MAX_RADIUS_KM}")
    return float(radius_km)


def validate_centre(lat: float, lon: float) -> tuple[float, float]:
    if not -90.0 <= lat <= 90.0:
        raise ValueError(f"latitude {lat} out of range")
    if not -180.0 <= lon <= 180.0:
        raise ValueError(f"longitude {lon} out of range")
    return float(lat), float(lon)


def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance. Used for the local filter AND for the
    'distance from home' attribute, so it is worth having exactly once."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = (math.sin(dp / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2)
    return EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(a))


def bounding_boxes(lat: float, lon: float, radius_km: float
                   ) -> list[list[list[float]]]:
    """Boxes covering the circle, ready for the BoundingBoxes payload.

    Returns one box normally, two when the circle crosses the antimeridian.

    ⚠ Longitude degrees SHRINK towards the poles by cos(latitude). A 500 km
    circle spans 4.5 degrees of longitude at the equator and 51 degrees at
    85 N. Near enough to a pole the circle wraps all the way round, and the
    box must become the FULL longitude range - otherwise the maths produces a
    nonsense box that silently excludes most of the requested area.
    """
    lat, lon = validate_centre(lat, lon)
    radius_km = validate_radius(radius_km)

    dlat = radius_km / KM_PER_DEGREE_LAT
    north = min(90.0, lat + dlat)
    south = max(-90.0, lat - dlat)

    cos_lat = math.cos(math.radians(lat))
    if cos_lat <= 1e-9:
        dlon = 180.0
    else:
        dlon = radius_km / (KM_PER_DEGREE_LAT * cos_lat)

    # ⚠ The circle also wraps if it reaches over a pole, where every longitude
    # is within the radius regardless of what cos(lat) suggests.
    if dlon >= 180.0 or north >= 90.0 or south <= -90.0:
        return [[[north, -180.0], [south, 180.0]]]

    west, east = lon - dlon, lon + dlon
    if west < -180.0:
        return [[[north, west + 360.0], [south, 180.0]],
                [[north, -180.0], [south, east]]]
    if east > 180.0:
        return [[[north, west], [south, 180.0]],
                [[north, -180.0], [south, east - 360.0]]]
    return [[[north, west], [south, east]]]


def within_radius(centre_lat: float, centre_lon: float, radius_km: float,
                  lat: float, lon: float) -> bool:
    """True if a position is inside the circle, not merely inside the box."""
    return distance_km(centre_lat, centre_lon, lat, lon) <= radius_km


# ⚠ THE EDGE HOLD (Ships item 267, Lee 2026-09-26: "fix it in code"). A vessel
# already on the map keeps its place until a newcomer is CLEARLY nearer: its
# distance counts as HOLD_FRACTION x radius less when ranking. Without it the
# ring at the cap traded places whenever a vessel a few hundred metres nearer
# was heard, and some came straight back (6 in 10 min on the Denmark entry,
# 2026-09-26). A FRACTION of the radius, not kilometres: radius runs 1-500 km
# worldwide. Chosen, not measured. The count is unchanged - only which vessels.
HOLD_FRACTION = 0.05


def hold_rank(distance: float, key, held, hold_km: float) -> float:
    """Distance as used for ranking: less by hold_km for a vessel in `held`.
    The ONE place the rule lives; nearest() and geo_location._sync use it."""
    return distance - hold_km if key in held else distance


def nearest(centre_lat: float, centre_lon: float, vessels, limit: int,
            held=(), hold_km: float = 0.0):
    """The `limit` nearest vessels, closest first.

    ⚠ When more vessels are in range than the cap allows, WHICH ones we drop
    must be deterministic and must match what the user asked for. Nearest-first
    does both. Dropping arbitrarily would make the entity set flap between
    updates for no visible reason.

    `vessels` is an iterable of (key, lat, lon, payload). Keys in `held` rank
    as if hold_km nearer (item 267); the distance RETURNED is always the true
    one. Ties break on key, so the same input gives the same output.
    """
    scored = [
        (distance_km(centre_lat, centre_lon, lat, lon), key, lat, lon, payload)
        for key, lat, lon, payload in vessels
    ]
    scored.sort(key=lambda t: (hold_rank(t[0], t[1], held, hold_km), t[1]))
    return scored[:limit]
