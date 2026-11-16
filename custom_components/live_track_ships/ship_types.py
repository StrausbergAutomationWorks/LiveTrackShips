"""ITU-R M.1371 vessel type codes -> a human label.

⚠ A STATIC TABLE, never a runtime dependency. It resolves an integer the
source already sent; it fetches nothing and it cannot fail.

⚠⚠ TYPE 0 IS THE UNAVAILABLE SENTINEL AND IT IS THE COMMON CASE. Measured
over 291 distinct vessels in five days: 255 reported a type value and 147 of
those were 0 - so the real coverage is 108 of 291, 37%, not 88%. An earlier
pass counted 0 as populated and reported 88%, which is B3's sentinel trap made
by the author of B3. The adapters map 0 to None before it reaches here;
`label_for` refuses it a second time on purpose.

⚠ Class B is worse, and inverted from what a recreational user wants. Message
24 is split - Part A is the name, Part B is the type - and units transmit Part
A far more reliably. Measured: Class B sent static MORE often than Class A
(42% vs 18%) and yielded a usable type LESS often (8% vs 18%). Any feature
built on type must treat "unknown" as a first-class state, not an error.

⚠ THE SECOND DIGIT IS NOT DECODED, DELIBERATELY. For the 20s, 40s, 60s, 70s,
80s and 90s the second digit encodes a dangerous-goods or pollutant category,
and the category letters were REDEFINED between ITU-R M.1371-4 and -5. A
transmitter's revision is not in the message, so decoding it would produce a
confident wrong answer for an unknown share of traffic. The decade is
reliable; the unit digit is not. Do not "improve" this without evidence.
"""

from __future__ import annotations

# ⚠ THE USCG EXTENSION (added 2026-09-24, SSOT item 254). USCG AIS Encoding
# Guide 26-07-01, navcen.uscg.gov: codes 01-19, 38-39, and unit digits 5-8 in
# the 40s, 60s, 70s and 80s. Every one sits in digits ITU marks RESERVED - never
# in the hazard digits 1-4 - so labelling them decodes nothing the note above
# forbids. Older sets may show them as reserved or not at all. Codes the guide
# leaves out (08, 10, 15, 16) stay unlabelled.
_USCG = {
    1: "Research vessel",
    2: "Training vessel",
    3: "Government vessel",
    4: "Icebreaker",
    5: "Buoy tender",
    6: "Cable layer",
    7: "Pipe layer",
    9: "Special purpose ship",
    11: "FPSO",
    12: "Fish factory ship",
    13: "Fish farm support vessel",
    14: "Offshore support vessel",
    17: "Construction vessel",
    18: "Crew boat",
    19: "Support vessel",
    38: "Trawler",
    39: "Patrol vessel",
    45: "High speed passenger craft",
    46: "High speed ro-ro craft",
    65: "Cruise ship",
    66: "Ferry",
    67: "Excursion vessel",
    75: "Bulk carrier",
    76: "Container ship",
    77: "Ro-ro cargo ship",
    78: "Landing craft",
    85: "Tanker, non-hazardous cargo",
    86: "Articulated tug and barge",
}

# Codes 30-59 stand alone - each number means one thing, with no decade rule.
_EXACT = {
    30: "Fishing",
    31: "Towing",
    32: "Towing (long or wide tow)",
    33: "Dredging or underwater operations",
    34: "Diving operations",
    35: "Military operations",
    36: "Sailing",
    37: "Pleasure craft",
    50: "Pilot vessel",
    51: "Search and rescue",
    52: "Tug",
    53: "Port tender",
    54: "Anti-pollution equipment",
    55: "Law enforcement",
    56: "Local vessel",
    57: "Local vessel",
    58: "Medical transport",
    59: "Non-combatant",
}

# Codes with a decade rule. The unit digit is not decoded - see the note above.
_DECADE = {
    2: "Wing in ground effect",
    4: "High speed craft",
    6: "Passenger",
    7: "Cargo",
    8: "Tanker",
    9: "Other",
}


def label_for(code) -> str | None:
    """ITU vessel type code -> label, or None when there is nothing to say.

    ⚠ None is returned for 0 (unavailable), for the codes neither ITU nor the
    USCG extension defines (08, 10, 15, 16), for anything outside 0-99, and
    for anything that is not an integer. OMIT the attribute rather than
    publishing "Unknown" - D0: a placeholder is indistinguishable from a
    reading. Until 2026-09-24 all of 1-19 and 38-39 returned None here.
    """
    try:
        value = int(code)
    except (TypeError, ValueError):
        return None
    if not 0 <= value <= 99:
        return None
    if value in _USCG:
        return _USCG[value]
    if value in _EXACT:
        return _EXACT[value]
    decade = _DECADE.get(value // 10)
    if decade is None:
        # 0 unavailable, 1-19 and 38-39 reserved. Nothing to report.
        return None
    return decade


def is_reportable(code) -> bool:
    """True when this code resolves to something worth showing a user."""
    return label_for(code) is not None


# ---------------------------------------------------------------------------
# MARKER GROUPS (06_MAP_CONTRACT.md D4f, backlog 345; Lee 2026-11-15: thirteen
# groups). What the map's filter card offers to hide, one group per object.
# The integration still shows everything; hiding is the viewer's, in the card.
# (key, label, order). Keys are permanent: a viewer's browser stores them.
GROUPS = {
    "cargo": ("Cargo", 1),
    "tanker": ("Tanker", 2),
    "passenger": ("Passenger and ferry", 3),
    "fishing": ("Fishing", 4),
    "pleasure": ("Pleasure and sailing", 5),
    "service": ("Tug, pilot and port service", 6),
    "government": ("Government, SAR and law enforcement", 7),
    "other": ("High speed and other", 8),
    "type_unknown": ("Type not sent", 9),
    "fishing_gear": ("Fishing-gear buoys", 10),
    "aton": ("Aids to navigation", 11),
    "base_station": ("Base stations", 12),
    "sar_aircraft": ("SAR aircraft", 13),
}
_KIND_GROUP = {"net_buoy": "fishing_gear", "aton": "aton",
               "base_station": "base_station", "sar_aircraft": "sar_aircraft"}
_CODE_GROUP = {
    # fishing
    30: "fishing", 38: "fishing", 12: "fishing", 13: "fishing",
    # pleasure
    36: "pleasure", 37: "pleasure",
    # tugs, pilots, port and offshore service: working craft
    31: "service", 32: "service", 33: "service", 34: "service", 50: "service",
    52: "service", 53: "service", 54: "service", 5: "service", 6: "service",
    7: "service", 14: "service", 17: "service", 18: "service", 19: "service",
    # government, search and rescue, law enforcement
    3: "government", 4: "government", 35: "government", 39: "government",
    51: "government", 55: "government", 58: "government", 59: "government",
}
_DECADE_GROUP = {6: "passenger", 7: "cargo", 8: "tanker", 2: "other", 4: "other", 9: "other"}


def group_for(kind, code):
    """The marker group key for an object, or None.

    ⚠ A DISTRESS BEACON (AIS-SART, MOB, EPIRB) HAS NO GROUP, deliberately: no
    viewer can hide one by hiding a class. Every vessel has a group; one whose
    type is 0, reserved or not sent is "type_unknown"."""
    if kind == "distress_beacon":
        return None
    if kind != "vessel":
        return _KIND_GROUP.get(kind)
    try:
        value = int(code)
    except (TypeError, ValueError):
        return "type_unknown"
    if value in _CODE_GROUP:
        return _CODE_GROUP[value]
    group = _DECADE_GROUP.get(value // 10) if 0 <= value <= 99 else None
    if group:
        return group
    # 1 research, 2 training, 9 special purpose, 11 FPSO, 56/57 local vessel:
    # labelled types that fit no class above.
    return "other" if label_for(value) else "type_unknown"
