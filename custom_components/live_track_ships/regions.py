"""Named regions — PRESETS AND CALIBRATION DATA, not the primary model.

⚠ SUPERSEDED AS THE MAIN MECHANISM, 2026-09-02. The integration is configured
with a CENTRE LATITUDE, LONGITUDE AND RADIUS - see geo.py. That is what the
user enters and what builds the subscription.

This module survives for two reasons, both real:

  * the measured_rate figures here are the CALIBRATION DATA behind the radius
    and vessel caps in geo.py, and deleting them would delete the evidence
  * named presets remain useful for anyone who wants a whole lake or seaway
    rather than a circle round their house

Everything below still applies where it is used. The registry is data: adding
a region means adding a Region and nothing else.

⚠ Region ids NEVER appear in a unique_id. Entities are keyed on MMSI, which is
the vessel's identity and independent of where it was seen. Regions can be
renamed, re-cut, merged or split at any time without orphaning entities.

⚠ A subscription REPLACES, it does not merge. boxes_for() therefore always
returns the whole set, never a delta.

⚠ Boxes crossing the antimeridian MUST be split. See split_antimeridian - and
note geo.py handles the same problem independently for circles.
"""

from __future__ import annotations

from dataclasses import dataclass, field

Corner = tuple[float, float]      # (latitude, longitude)
Box = tuple[Corner, Corner]       # two opposite corners


@dataclass(frozen=True)
class Region:
    """A named area, expressed as one or more bounding boxes."""

    id: str
    name: str
    boxes: tuple[Box, ...]
    notes: str = ""
    # Measured messages/second, where we have measured it. None means unknown -
    # do not guess, and do not present a guess to the user as a figure.
    measured_rate: float | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)


# --------------------------------------------------------------------------
# The registry
#
# ⚠ Rates below are MEASURED unless marked otherwise. An unmeasured region
# carries measured_rate=None rather than an estimate.

REGIONS: dict[str, Region] = {}


def register(region: Region) -> Region:
    if region.id in REGIONS:
        raise ValueError(f"duplicate region id: {region.id}")
    for (lat1, lon1), (lat2, lon2) in region.boxes:
        for lat in (lat1, lat2):
            if not -90.0 <= lat <= 90.0:
                raise ValueError(f"{region.id}: latitude {lat} out of range")
        for lon in (lon1, lon2):
            if not -180.0 <= lon <= 180.0:
                raise ValueError(f"{region.id}: longitude {lon} out of range")
    REGIONS[region.id] = region
    return region


# -- the starting region ----------------------------------------------------
CHICAGOLAND = register(Region(
    id="chicagoland",
    name="Chicagoland and southern Lake Michigan",
    boxes=((( 42.60, -88.40), (41.30, -86.20)),),
    measured_rate=0.2,
    tags=("great_lakes", "usa"),
    notes=(
        "Waukegan south through Chicago, Gary, Burns Harbor and Michigan City, "
        "round to St Joseph on the Michigan shore, and inland to Joliet. "
        "⚠ MEASURED: the Chicago River downtown is well covered. The Chicago "
        "Sanitary and Ship Canal, the Cal-Sag Channel and the Calumet River "
        "are NOT - one hour of listening over that corridor returned zero "
        "vessels. Do not promise inland waterway coverage."
    ),
))

GREAT_LAKES = register(Region(
    id="great_lakes",
    name="Great Lakes and St Lawrence Seaway",
    boxes=((( 49.10, -92.30), (41.20, -76.00)),),
    measured_rate=1.0,
    tags=("great_lakes", "usa", "canada"),
    notes=(
        "All five lakes plus the connecting waters. MEASURED: 100 distinct "
        "vessels in 120 s, every position inside a lake - the box does not "
        "drag in ocean or inland noise."
    ),
))

# -- worldwide: supported, deliberately not the default ---------------------
WORLD = register(Region(
    id="world",
    name="Worldwide",
    boxes=(((85.0, -180.0), (-85.0, 180.0)),),
    measured_rate=100.3,
    tags=("global",),
    notes=(
        "⚠ MEASURED 2026-09-02: 100.3 messages/second, 6,017/minute, and "
        "3,846 DISTINCT VESSELS IN 40 SECONDS - and that is a floor, since "
        "vessel count grows with the observation window. About 100x the "
        "Great Lakes rate. The bandwidth is manageable; the ENTITY COUNT is "
        "not. Worldwide scope means 'any region you choose', not 'everything "
        "at once'. Offer this only behind a clear warning."
    ),
))


# --------------------------------------------------------------------------
# Geometry


def split_antimeridian(box: Box) -> list[Box]:
    """Split a box that crosses 180 degrees into two that do not.

    ⚠ A box written as lon 170 -> -170 means "20 degrees across the Pacific",
    but read literally as min/max it means "340 degrees the other way round" -
    almost the whole planet. Nothing in Chicagoland can trigger this, which is
    exactly why it will not be noticed until someone adds the Bering Strait,
    Fiji or the Russian Far East. Handle it now, in one place.

    A box is treated as crossing when its western longitude is greater than
    its eastern one.
    """
    (lat1, lon1), (lat2, lon2) = box
    north, south = max(lat1, lat2), min(lat1, lat2)
    west, east = lon1, lon2
    if west <= east:
        return [((north, west), (south, east))]
    return [
        ((north, west), (south, 180.0)),
        ((north, -180.0), (south, east)),
    ]


def boxes_for(region_ids) -> list[list[list[float]]]:
    """The complete BoundingBoxes payload for the selected regions.

    ⚠ Returns the WHOLE set every time. Subscriptions replace rather than
    merge, so a partial list silently drops coverage instead of adding to it.

    Unknown ids raise rather than being skipped: quietly ignoring a region the
    user asked for means showing them less water than they configured, with no
    error to explain it.
    """
    out: list[list[list[float]]] = []
    seen: set[tuple] = set()
    for rid in region_ids:
        try:
            region = REGIONS[rid]
        except KeyError:
            raise KeyError(
                f"unknown region {rid!r}; known: {sorted(REGIONS)}") from None
        for box in region.boxes:
            for (n, w), (s, e) in split_antimeridian(box):
                key = (n, w, s, e)
                if key in seen:      # regions may legitimately overlap
                    continue
                seen.add(key)
                out.append([[n, w], [s, e]])
    return out


def estimated_rate(region_ids) -> float | None:
    """Summed measured rate, or None if any selected region is unmeasured.

    ⚠ Deliberately returns None rather than a partial total. A number that
    silently omits an unmeasured region is worse than no number - it looks
    authoritative and is not. Overlapping regions also double-count, so treat
    the result as an upper bound.
    """
    total = 0.0
    for rid in region_ids:
        rate = REGIONS[rid].measured_rate
        if rate is None:
            return None
        total += rate
    return total


DEFAULT_REGION = CHICAGOLAND.id
