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

import re
from typing import Protocol

# ⚠ MOVED TO saw-livetrack 0.2.19 (backlog 315, 2026-10-30), VERBATIM from
# this file at ccebaee: KNOTS_TO_KMH, the rate-of-turn decode (rot_to_dps and
# its constants, SSOT items 18 and 20), Observation, and what a transmitter is
# (object_kind, OBJECT_KINDS, the net-buoy name rule; item 257). Imported, so
# every name above this seam still resolves here and there is ONE copy: do
# not define any of them again in this file. What stays here is Ships' own:
# sar_airframe, map_layer, valid_imo, object_ids and the Source protocol.
from saw_livetrack.ais import (  # noqa: F401
    KNOTS_TO_KMH,
    NON_VESSEL_MESSAGES,
    OBJECT_KINDS,
    ROT_SATURATED,
    ROT_SCALE,
    ROT_UNAVAILABLE,
    Observation,
    _GEAR_NAME,
    object_kind,
    rot_to_dps,
)


# ---------------------------------------------------------------------------
# A SAR aircraft's airframe, from its MMSI. ITU-R M.585-8 Annex 1 section 3
# lets an administration mark the SEVENTH digit, 1 fixed-wing and 5
# helicopter. Optional: Sweden marks, Norway's NOR-002 (111257001) does not and
# is a helicopter. So 1 is fixed-wing and everything else a rotorcraft.
# ⚠ DECIDED HERE AND NOWHERE ELSE (backlog 258). The icon (icons.pick_sar) and
# the map layer (map_layer below) both take it from this function.
def sar_airframe(identity) -> str:
    """fixed_wing or rotorcraft, for an object whose kind is sar_aircraft."""
    mmsi = str(identity or "")
    return "fixed_wing" if len(mmsi) == 9 and mmsi[6] == "1" else "rotorcraft"


# 10_SEED/06_MAP_CONTRACT.md D10: the integration names the layer, the CARD
# owns the numbers. The layer follows WHAT the object is: a SAR BOAT has a
# ship MMSI and kind vessel, so it is water; only a SAR AIRCRAFT (111 MMSI or
# the SAR aircraft message) is in the air.
def map_layer(kind, identity) -> str:
    """water, fixed, air_low or air."""
    if kind == "vessel":
        return "water"
    if kind == "sar_aircraft":
        return "air" if sar_airframe(identity) == "fixed_wing" else "air_low"
    return "fixed"      # net_buoy, aton, base_station, distress_beacon


# 06_MAP_CONTRACT.md D11: object_ids. Only values the source states AS that
# identifier, in the card's normalised form; never repaired, never derived.
# The card drops anything else SILENTLY (rule 7), so a malformed value here
# would do nothing and look as if it worked. [0-9], not \d: \d also matches
# non-ASCII digits.
_MMSI_RE = re.compile(r"[0-9]{9}")
_IMO_RE = re.compile(r"[0-9]{7}")


def valid_imo(value) -> str | None:
    """The IMO number as a 7-digit string, or None. The seventh digit is a
    check digit: the first six weighted 7, 6, 5, 4, 3, 2, summed, mod 10.
    Measured 2026-09-24: a live entity carried imo '101210706', nine digits."""
    if value is None or isinstance(value, bool):
        return None
    s = str(value)
    if not _IMO_RE.fullmatch(s) or s == "0000000":
        return None
    total = sum(int(d) * w for d, w in zip(s[:6], (7, 6, 5, 4, 3, 2)))
    return s if total % 10 == int(s[6]) else None


def object_ids(identity, imo=None) -> dict:
    """{"mmsi": 9-digit string} when the identity is one, plus "imo" only when
    valid_imo accepts it. ⚠ NEVER "registration": an AIS call sign is not a
    registration (D11), even where a Swedish SAR helicopter's was one."""
    ids = {}
    mmsi = str(identity) if identity is not None else ""
    if _MMSI_RE.fullmatch(mmsi):
        ids["mmsi"] = mmsi
    imo_s = valid_imo(imo)
    if imo_s:
        ids["imo"] = imo_s
    return ids


class Source(Protocol):
    """Every backend implements this; nothing above it knows the difference."""

    domain: str

    async def observations(self):
        """Yield Observation objects until cancelled."""
        ...

    async def close(self) -> None:
        ...
