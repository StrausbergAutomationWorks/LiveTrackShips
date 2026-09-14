"""Normalised observation shape, and the Source protocol every backend meets.

⚠ THIS IS THE SEAM. Sources differ in transport, in field names, in units and
in sentinels. Everything above this module sees Observations and never learns
which source produced them.

Contract fields follow 10_SEED/05_SHARED_LESSONS.md section D:
  * units live in the NAME - _deg true north, _kmh, _km, _m, _s
  * an unavailable value is None. NEVER a sentinel, never a placeholder
  * heading_deg and course_deg are DIFFERENT FIELDS. Rotate by heading;
    extrapolate by course only
  * position_source is required before anything may be extrapolated
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from typing import Protocol

KNOTS_TO_KMH = 1.852


@dataclass(frozen=True)
class Observation:
    """One sighting of one object, from any source.

    ⚠ `identity` is the natural key (MMSI here) and is what unique_id is built
    from. NEVER build identity from a name - AIS ShipName is a 20-character
    field operators mangle to fit, and entity ids are permanent.
    """

    identity: str                      # MMSI as a string
    source: str                        # the integration domain
    observed_at: _dt.datetime          # when the POSITION was true

    latitude: float | None = None
    longitude: float | None = None

    course_deg: float | None = None    # direction of TRAVEL
    heading_deg: float | None = None   # direction the hull POINTS
    speed_kmh: float | None = None
    rate_of_turn_dps: float | None = None

    name: str | None = None
    ship_type: int | None = None       # ITU. 0 is "unavailable", not a type
    call_sign: str | None = None
    destination: str | None = None
    imo: int | None = None
    length_m: float | None = None
    beam_m: float | None = None
    draught_m: float | None = None
    nav_status: int | None = None

    # Required before any consumer may dead-reckon. See D3.
    position_source: str = "observed"
    max_extrapolation_s: int | None = None

    raw_message_type: str | None = None
    extra: dict = field(default_factory=dict)

    @property
    def is_vessel(self) -> bool:
        """Not every AIS message describes a ship. An aid to navigation is a
        fixed object and a base station is a building; neither has speed,
        course or a vessel type."""
        return self.raw_message_type not in (
            "AidsToNavigationReport", "BaseStationReport")


class Source(Protocol):
    """Every backend implements this; nothing above it knows the difference."""

    domain: str

    async def observations(self):
        """Yield Observation objects until cancelled."""
        ...

    async def close(self) -> None:
        ...
