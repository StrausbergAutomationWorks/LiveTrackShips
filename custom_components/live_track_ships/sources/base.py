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
import re
from dataclasses import dataclass, field
from typing import Protocol

KNOTS_TO_KMH = 1.852

# ---------------------------------------------------------------------------
# ⚠ RATE OF TURN — one decode, here, for all three sources.
#
# The AIS wire value is NOT an angular rate. ITU-R M.1371 encodes it as
#     raw = 4.733 * sqrt(ROT in degrees per MINUTE), signed
# so raw 11 is about 5.4 deg/min - 0.09 deg/s - and publishing 11 under a key
# named `_dps` is D0's wrong-value-worse-than-absent case: the consumer cannot
# tell. DECODE, never pass through.
#
# ⚠ THREE values are special and they are NOT all negative:
#     -128  no turn information available
#     -127  turning LEFT  faster than 5 deg/30 s, magnitude unknown
#     +127  turning RIGHT faster than 5 deg/30 s, magnitude unknown
#
# ⚠⚠ THIS CONSTANT LIVED IN FOUR PLACES AND HELD THREE DIFFERENT VALUES -
# (-128, -127) in two adapters, (-128, 128) in a third, and a fourth copy in
# const.py that nothing imported. Every list enumerated the NEGATIVE specials
# rather than the SATURATED ones, so +127 was published as a reading: 127
# "degrees per second" is 21 revolutions a minute. Measured in one Digitraffic
# pull of 1,063 vessels: 12 at -127 and 18 at +127, so the COMMONER of the two
# was the one let through. SSOT.md items 18 and 20.
#
# ±127 is SATURATED, not unavailable - direction is known, magnitude is not.
# No contract field carries that honestly, so under D0 it is OMITTED, by the
# same rule for both signs on every source. Do not reintroduce a per-adapter
# sentinel list for this field; that is what drifted.
ROT_UNAVAILABLE = -128
ROT_SATURATED = (-127, 127)
ROT_SCALE = 4.733


def rot_to_dps(raw) -> float | None:
    """AIS rate-of-turn byte -> degrees per second, signed, or None."""
    if raw is None:
        return None
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return None
    if value == ROT_UNAVAILABLE or value in ROT_SATURATED:
        return None
    # ⚠ Outside the signed byte it is not an AIS rate of turn at all.
    if not -128 <= value <= 127:
        return None
    dps = ((abs(value) / ROT_SCALE) ** 2) / 60.0
    return round(dps if value >= 0 else -dps, 4)



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
    rate_of_turn_dps: float | None = None   # DECODED. See rot_to_dps above

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
    def kind(self) -> str:
        """What the object is: one of OBJECT_KINDS. See object_kind()."""
        return object_kind(self.identity, self.name, self.length_m,
                           self.raw_message_type)

    @property
    def is_vessel(self) -> bool:
        """Not every AIS transmitter is on a ship. An aid to navigation is a
        fixed object, a base station is a building, and a net buoy is a float
        on a fishing line; none has a vessel type, a size or a voyage."""
        return self.kind == "vessel"


# ---------------------------------------------------------------------------
# What an AIS transmitter is, from what it sends. ITU-R M.585 fixes the MMSI
# formats for everything that is not a ship station; the net buoys are the
# exception below.
OBJECT_KINDS = ("vessel", "net_buoy", "aton", "base_station", "sar_aircraft",
                "distress_beacon")

NON_VESSEL_MESSAGES = {
    "AidsToNavigationReport": "aton",
    "BaseStationReport": "base_station",
    "StandardSearchAndRescueAircraftReport": "sar_aircraft",
}

# ⚠ A NET BUOY IS KNOWN BY ITS NAME. ITU gives fishing-gear devices 979xxxxxx
# on channel 2006 only, never the AIS channels; the ones on the AIS channels
# carry ship-shaped MMSIs (5867xxxxx off southern Norway), no type, no size
# and no call sign. The factory name is the tell - FISHING BOUY, NET
# MARK, BUOY - and it is also how Global Fishing Watch flags "likely gear".
# A real vessel with such a word in its name (a BUOY TENDER) broadcasts its
# length, so a broadcast length rules the name out.
_GEAR_NAME = re.compile(
    r"\b(BUOY|BOUY|BOYA|BOUE|NET\s*MARK(ER)?|NET\s*BUOY|FISHING\s*NET|"
    r"FISH(ING)?\s*GEAR)\b", re.I)


def object_kind(identity, name=None, length_m=None,
                raw_message_type=None) -> str:
    """vessel, net_buoy, aton, base_station, sar_aircraft or distress_beacon."""
    kind = NON_VESSEL_MESSAGES.get(raw_message_type or "")
    if kind:
        return kind
    mmsi = str(identity or "")
    if len(mmsi) == 9 and mmsi.isdigit():
        if mmsi.startswith("979"):
            return "net_buoy"
        if mmsi.startswith(("970", "972", "974")):
            return "distress_beacon"
        if mmsi.startswith("99"):
            return "aton"
        if mmsi.startswith("00"):
            return "base_station"
        if mmsi.startswith("111"):
            return "sar_aircraft"
    if name and not length_m and _GEAR_NAME.search(name):
        return "net_buoy"
    return "vessel"


class Source(Protocol):
    """Every backend implements this; nothing above it knows the difference."""

    domain: str

    async def observations(self):
        """Yield Observation objects until cancelled."""
        ...

    async def close(self) -> None:
        ...
