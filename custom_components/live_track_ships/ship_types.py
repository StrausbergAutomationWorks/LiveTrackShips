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

    ⚠ None is returned for 0 (unavailable), for 1-19 and 38-39 (reserved, so
    the code carries no meaning to report), for anything outside 0-99, and for
    anything that is not an integer. OMIT the attribute rather than publishing
    "Unknown" - D0: a placeholder is indistinguishable from a reading.
    """
    try:
        value = int(code)
    except (TypeError, ValueError):
        return None
    if not 0 <= value <= 99:
        return None
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
