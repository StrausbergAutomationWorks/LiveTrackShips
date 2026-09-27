"""Vessel marker icons: which silhouette, what colour, what size, which way.

The artwork is OURS (MIT, drawn for this integration 2026-09-24), top-down,
bow NORTH, in a 200 x 200 viewBox. Every point sits within r <= 94 of the
centre, so ANY rotation fits the box without the 1/sqrt(2) shrink Live Track
Aircraft needs for its square artwork. Record: SSOT item 254.

! THE ICON FOLLOWS THE DECLARED AIS TYPE. Type is the vessel's own broadcast
declaration; its accuracy is the transmitter's liability, not ours (Lee,
2026-09-24). That includes 58's red cross and 51's Star of Life.

! THE HAZARD DIGIT SELECTS NOTHING. In the 20s, 40s, 60s, 70s, 80s and 90s a
unit digit of 1-4 is a dangerous-goods category whose letters were redefined
between ITU-R M.1371-4 and -5 (ship_types.py). It picks the DECADE's icon and
nothing more. The specific icons come only from codes ITU leaves RESERVED and
the USCG AIS Encoding Guide (26-07-01) defines: 01-19, and unit digits 5-8 in
the 40s, 60s, 70s and 80s. The two never collide.

! Two icons carry a SYMBOL that must stay UPRIGHT at any heading - a tilted
red cross reads as an X. decolour() strips every paint attribute from the
artwork, so the symbol cannot live in the icon file; the renderer adds it as
a second layer. When the CARD does the rotating (it always does, since 2026-09-25), the symbol
is counter-rotated inside the served image so the card's turn stands it up.
"""

from __future__ import annotations

import math
import os
import re

# --- which silhouette ------------------------------------------------------
ICON_KEYS = frozenset((
    "generic", "cargo", "tanker", "passenger", "fishing", "tug", "sailing",
    "pleasure", "highspeed", "workboat", "military", "container", "bulk",
    "carcarrier", "cruise", "ferry", "dredger", "offshore", "police",
    "medical", "atb", "sar", "netbuoy", "sarheli", "sarplane",
    "dannebrog", "norge", "savarona", "oman", "qatar", "indonesia",
    "philippines", "saudi", "uae", "bahrain", "morocco", "russia"))

# ! NOT A VESSEL: a fishing-gear buoy (sources/base.py object_kind). A salmon
# seen from the side, mouth north, drawn IN ITS OWN COLOURS - salmon body,
# black scales, white head outlined black - so the renderer keeps its paint
# instead of filling it with a tone. Sized as the smallest aircraft draws:
# Live Track Aircraft's light-aircraft icons at weight 0.62 span 31 px of a
# 64 px image (bin\ship_icons\make_fish.txt, 2026-09-24), and so does this.
# The state-vessel icons below are painted too: their colours ARE the icon.
PAINTED = frozenset(("netbuoy", "dannebrog", "norge", "savarona", "oman",
                     "qatar", "indonesia", "philippines", "saudi", "uae",
                     "bahrain", "morocco", "russia"))
SMALLEST_AIRCRAFT_WEIGHT = 0.47
NETBUOY_WEIGHT = SMALLEST_AIRCRAFT_WEIGHT

# ! NOT A VESSEL: an aircraft in search and rescue, 111MIDxxx. AIS carries no
# aircraft type; ITU-R M.585-8 Annex 1 section 3 lets an administration mark
# the SEVENTH digit, 1 fixed-wing and 5 helicopter. Optional: Sweden marks,
# Norway's NOR-002 (111257001) does not and is a helicopter. So 1 is a plane
# and everything else a helicopter. The helicopter's rotor spins: its own
# group, hub at the image centre, SMIL in the artwork. SAR orange, the same
# orange as the Star of Life on SAR boats.
SAR_ICON_KEYS = frozenset(("sarheli", "sarplane"))


# ⚠ The airframe is decided in sources/base.py sar_airframe() and NOWHERE
# else (backlog 258); the map layer takes it from there too, so the icon and
# the layer cannot disagree. This only maps it to artwork.
SAR_KEY_FOR = {"fixed_wing": "sarplane", "rotorcraft": "sarheli"}


def pick_sar(airframe) -> str:
    return SAR_KEY_FOR.get(airframe, "sarheli")


# --- one named ship, one icon ----------------------------------------------
# ! ROYAL AND PRESIDENTIAL SHIPS (Lee, 2026-09-26). Each draws its own
# PAINTED icon in its national colours, whatever type it broadcasts: the
# ship is the point, not its declared class. Only objects of kind `vessel`
# reach this. Never keyed by name - a name is padded, mangled and editable.
#
# ! IMO FIRST, MMSI SECOND (Lee, 2026-09-26). An IMO number stays with the
# hull for life; an MMSI changes with flag or operator - SAVARONA went from
# 271000250 to 271035111 when she became TCG SAVARONA, and a table keyed by
# MMSI alone would have gone dark on her. The caller passes the IMO only
# when sources/base.py valid_imo() accepts it. The MMSI row covers a ship
# whose IMO has not arrived yet (static data lags position, SSOT section 6);
# list only the MMSI she broadcasts NOW - an old one can be reissued.
# Each value must be in ICON_KEYS and PAINTED (test_icons.py checks).
# ! RULE (Lee, 2026-09-26): a royal or presidential ship gets an icon when
# its MMSI OR its IMO can be found - including a reigning monarch's own
# yacht and a warship that doubles as the presidential ship. No
# identifier, no ship. Icons named for a SHIP are that ship's; icons named
# for a COUNTRY are its flag and serve every state vessel of that country.
# ! RULES (Lee, 2026-09-27): no FORMER ruler's yacht - it is private. A
# country icon carries the OWNER's country, not the flag state (TATOOSH
# and AL RAYA fly Cayman). Royal fleet SUPPORT ships count (AL NOORES).
# A published IMO that fails its check digit is no identifier.
# An MMSI not heard for years is left out and the ship listed by IMO only:
# a dead MMSI can be reissued to another ship (OLYMPIA, CHAYKA).
STATE_BY_IMO = {
    "4537661": "dannebrog",   # Kongeskibet DANNEBROG, Denmark, 78.43 m
    "4603343": "norge",       # KS NORGE, Norway, 80.6 m (IMO measured live)
    "5314810": "savarona",    # SAVARONA, Turkey, 136 m
    "9463774": "oman",        # AL SAID, Oman Royal Yacht Squadron, 155 m
    "9714460": "oman",        # FULK AL SALAMAH, Oman, 164 m
    "1004572": "oman",        # ZINAT AL BIHAAR, Oman, royal sailing dhow
    "9772929": "qatar",       # AL LUSAIL, the reigning Emir of Qatar, 123 m
    "4772326": "indonesia",   # KRI BUNG KARNO (369), presidential corvette
    "4608410": "philippines", # BRP ANG PANGULO (AT-25); no MMSI published
    "1007043": "saudi",       # AL SALAMAH, Saudi Arabia Govt Finance, 139 m
    "9234240": "oman",        # AL NOORES, Royal Yachts Squadron tug
    "9803601": "morocco",     # BADIS 1, King Mohammed VI
    "6915946": "morocco",     # EL BOUGHAZ I, King Mohammed VI
    "1006324": "uae",         # DUBAI, the Ruler of Dubai, 162 m
    "1006336": "uae",         # TATOOSH, UAE President; Cayman flag
    "9693367": "uae",         # AZZAM, Dept of the President's Affairs, 180 m
    "9526758": "bahrain",     # AL RAYA, Royal Family of Bahrain; Cayman flag
    "1011551": "russia",      # GRACEFUL (KOSATKA), US Treasury: Putin's, 82 m
    "1006960": "russia",      # OLYMPIA, US Treasury: Putin's; Cayman flag
    "9544619": "russia",      # CHAYKA ex SIRIUS, bought for the President 2011
    "1009663": "russia",      # VICTORIA, 71 m, linked to Putin (Maritime Executive)
}
STATE_BY_MMSI = {
    "219517000": "dannebrog",  # call sign OUDA
    "257001000": "norge",      # call sign LAMA; measured live 2026-09-26
    "271035111": "savarona",   # as TCG SAVARONA since the 2024 refit
    "461001000": "oman",       # AL SAID
    "461002000": "oman",       # FULK AL SALAMAH
    "461003000": "oman",       # ZINAT AL BIHAAR
    "466443000": "qatar",      # AL LUSAIL
    "525114116": "indonesia",  # KRI BUNG KARNO
    "403003000": "saudi",      # AL SALAMAH (NOT 403007000: resolves to nothing)
    "461006000": "oman",       # AL NOORES
    "242822300": "morocco",    # BADIS 1
    "242890000": "morocco",    # EL BOUGHAZ I
    "470886000": "uae",        # DUBAI
    "319801000": "uae",        # TATOOSH
    "470992000": "uae",        # AZZAM
    "319150300": "bahrain",    # AL RAYA (NOT 319526000: her MMSI as DILBAR)
    "273294110": "russia",     # GRACEFUL (NOT 378374000: her BVI MMSI to 2021)
    "273216780": "russia",     # VICTORIA, call sign UBZU3
}


def special_for(identity, imo=None) -> str | None:
    """The icon of a named state vessel, or None for every other ship.
    `imo` must already be validated (valid_imo); `identity` is the MMSI."""
    if imo is not None:
        key = STATE_BY_IMO.get(str(imo).strip())
        if key:
            return key
    if identity is None:
        return None
    return STATE_BY_MMSI.get(str(identity).strip())

# Codes that name ONE thing. 01-19 and x5-x8 are the USCG extension (reserved
# in ITU); 30-59 are ITU's own standalone block.
_EXACT = {
    1: "workboat",      # science / research vessel
    2: "generic",       # training vessel
    3: "generic",       # government-owned or operated - drawn in amber
    4: "generic",       # ice breaker
    5: "workboat",      # buoy (AtoN) tender
    6: "offshore",      # cable layer
    7: "offshore",      # pipe layer
    9: "generic",       # special purpose, no additional information
    11: "offshore",     # FPSO
    12: "fishing",      # fish factory ship
    13: "workboat",     # fish farm support vessel
    14: "offshore",     # offshore support vessel
    17: "offshore",     # construction vessel
    18: "workboat",     # crew boat
    19: "workboat",     # support vessel, no additional information
    30: "fishing",
    31: "tug",          # towing
    32: "tug",          # towing, tow > 200 m or > 25 m wide
    33: "dredger",      # dredging or underwater operations
    34: "workboat",     # diving operations
    35: "military",     # warship or naval auxiliary
    36: "sailing",
    37: "pleasure",
    38: "fishing",      # trawler (USCG)
    39: "military",     # patrol vessel (USCG) - drawn in olive
    45: "highspeed",    # HSC carrying passengers (USCG)
    46: "highspeed",    # HSC ro-ro (USCG)
    50: "workboat",     # pilot vessel
    51: "sar",          # search and rescue
    52: "tug",
    53: "workboat",     # port or fish tender
    54: "workboat",     # anti-pollution or firefighting
    55: "police",       # law enforcement
    56: "generic",      # spare, local vessels
    57: "generic",      # spare, local vessels - see _ATB_BY_LENGTH
    58: "medical",      # medical transport, 1949 Geneva Conventions
    59: "generic",      # ships of states not party to an armed conflict
    65: "cruise",       # passenger (cruise) ship (USCG)
    66: "ferry",        # passenger (ferry) ship (USCG)
    67: "passenger",    # passenger (excursion) ship (USCG)
    75: "bulk",         # bulk carrier (USCG)
    76: "container",    # container ship (USCG)
    77: "carcarrier",   # roll-on roll-off carrier (USCG)
    78: "cargo",        # landing craft (USCG)
    85: "tanker",       # non-hazardous tanker (USCG)
    86: "atb",          # integrated / articulated tug and barge (USCG)
}

# Everything else in a decade takes the decade's icon, hazard digits included.
_DECADE = {2: "highspeed",      # WIG: nearest shape we have (Lee, 2026-09-24)
           4: "highspeed", 6: "passenger", 7: "cargo", 8: "tanker"}

# ! A TUG BROADCASTING THE COMBINED UNIT. SEA EAGLE II sends type 52 at 164 m:
# an articulated tug-barge, not a 164 m tug (SSOT section 6). The USCG guide
# tells push tugs to send 86, or 57 where their set lacks 86 - so 57 joins the
# tug codes here, and only above the length no lone tug reaches.
_ATB_BY_LENGTH = frozenset((31, 32, 52, 57))
ATB_MIN_LENGTH_M = 60.0


def pick(ship_type, length_m=None) -> str:
    """Which silhouette. Never None; an unknown or absent type is generic."""
    try:
        code = int(ship_type)
    except (TypeError, ValueError):
        return "generic"
    if code in _ATB_BY_LENGTH and length_m and length_m > ATB_MIN_LENGTH_M:
        return "atb"
    if code in _EXACT:
        return _EXACT[code]
    if 20 <= code <= 89:
        return _DECADE.get(code // 10, "generic")
    return "generic"


# --- what colour -----------------------------------------------------------
# ! COLOUR CARRIES MEANING, NEVER IDENTITY. Identity is marker_label's job.
TONES = {
    "default": "#EDEAE2",   # cream
    "police": "#3D8BFF",    # blue: police across Europe and most of the world
    "gov": "#EF9F27",       # amber: Live Track Aircraft's government tone
    "military": "#8C9A4B",  # olive; haze grey read as "disabled" on a map
    "white": "#FFFFFF",     # the medical hull, under the red cross
    "sar": "#F26A1B",       # SAR orange: SAR aircraft, and 51's Star of Life
}


def tone_for_kind(kind: str) -> str:
    """Tone for an object that is not a vessel."""
    return "sar" if kind == "sar_aircraft" else "default"


def tone_for(ship_type) -> str:
    try:
        code = int(ship_type)
    except (TypeError, ValueError):
        return "default"
    if code == 55:
        return "police"
    if code == 3:
        return "gov"
    if code in (35, 39):
        return "military"
    if code == 58:
        return "white"
    return "default"


# --- what size -------------------------------------------------------------
# ! SIZE FROM THE BROADCAST LENGTH, on a log ramp, so a 12 m boat is still a
# readable shape and a 300 m ship is the whole icon. Approved 2026-09-24.
RAMP_MIN_W, RAMP_MIN_L, RAMP_MAX_L = 0.45, 8.0, 300.0

# Where no length is broadcast - Class B Part B goes missing far more often
# than Part A (SSOT section 6), so this is the common case for small craft.
_DEFAULT_WEIGHT = {
    "pleasure": 0.50, "sailing": 0.50, "workboat": 0.55, "police": 0.55,
    "medical": 0.55, "sar": 0.55, "highspeed": 0.60, "tug": 0.60,
    "fishing": 0.60, "generic": 0.70, "dredger": 0.75, "offshore": 0.75,
    "military": 0.80, "ferry": 0.85, "passenger": 0.85, "atb": 0.85,
    "cargo": 0.90, "tanker": 0.90, "container": 0.92, "bulk": 0.92,
    "carcarrier": 0.92, "cruise": 0.95, "dannebrog": 0.80,
    "norge": 0.80, "savarona": 0.95, "oman": 0.95, "qatar": 0.90,
    "indonesia": 0.80, "philippines": 0.80, "saudi": 0.95, "uae": 0.95,
    "bahrain": 0.90, "morocco": 0.80, "russia": 0.85,
}


def weight_for(key: str, length_m=None) -> float:
    if key == "netbuoy" or key in SAR_ICON_KEYS:
        return SMALLEST_AIRCRAFT_WEIGHT
    try:
        L = float(length_m) if length_m else 0.0
    except (TypeError, ValueError):
        L = 0.0
    if L > 0:
        L = max(RAMP_MIN_L, min(RAMP_MAX_L, L))
        t = math.log(L / RAMP_MIN_L) / math.log(RAMP_MAX_L / RAMP_MIN_L)
        return round(RAMP_MIN_W + (1.0 - RAMP_MIN_W) * t, 2)
    return _DEFAULT_WEIGHT.get(key, 0.70)


# --- which way -------------------------------------------------------------
# Below this a vessel is not going anywhere, and course over ground is noise.
# 2 kn is also AIS's own Class B reporting-rate boundary (store.STATIONARY_KMH).
SLOW_KMH = 2 * 1.852


def bearing(heading_deg, course_deg, speed_kmh, held):
    """(bearing, basis) or (None, None). 06_MAP_CONTRACT.md D4.

    True heading when broadcast - it is where the hull points, meaningful at
    rest. Else course over ground while moving at 2 kn or more. Else the last
    course-derived bearing, HELD (Lee, 2026-09-24): a moored vessel's course
    is noise, and dropping the rotation would snap every one of them north.
    A vessel first seen at rest with no heading has nothing to hold."""
    if heading_deg is not None:
        return float(heading_deg) % 360, "heading"
    if (course_deg is not None and speed_kmh is not None
            and speed_kmh >= SLOW_KMH):
        return float(course_deg) % 360, "course"
    if held is not None:
        return held, "held"
    return None, None


# A FISHING-GEAR BUOY (object_kind net_buoy, SSOT item 257) is not a vessel
# and the 2 kn rule is not for it (Lee, 2026-09-25): a buoy drifts slowly on
# its line and whatever heading or course it sends is the only direction it
# has. Heading first, then course at ANY speed, never held. With neither it is
# drawn pointing EAST - into the IMAGE, with no icon_rotation_deg, because D4
# allows only heading, course or held as a basis and "east" is none of them.
BUOY_REST_DEG = 90


def buoy_bearing(heading_deg, course_deg):
    """(bearing, basis) or (None, None) for a net buoy."""
    if heading_deg is not None:
        return float(heading_deg) % 360, "heading"
    if course_deg is not None:
        return float(course_deg) % 360, "course"
    return None, None


# Quantised so the browser can cache: 72 variants per icon.
ROTATION_STEP = 5


def quantise(deg) -> int | None:
    if deg is None:
        return None
    return int(round((deg % 360) / ROTATION_STEP) * ROTATION_STEP) % 360


# --- the upright symbol ----------------------------------------------------
SYMBOL_FOR = {"medical": "cross", "sar": "sol"}
CROSS_RED = "#D7263D"
SOL_ORANGE = "#F26A1B"   # the SAR variant; blue now means police


def _cross(cx, cy, arm, half) -> str:
    """ONE polygon. Two crossing rectangles fill back in where they overlap
    under evenodd."""
    p = [(-half, -arm), (half, -arm), (half, -half), (arm, -half),
         (arm, half), (half, half), (half, arm), (-half, arm), (-half, half),
         (-arm, half), (-arm, -half), (-half, -half)]
    return "M" + " L".join("%g %g" % (cx + x, cy + y) for x, y in p) + " Z"


_SOL_CACHE: dict[str, str] = {}


def _sol_paths() -> dict[str, str]:
    """Star, rod and snake from _star_of_life.svg - public-domain artwork
    (Wikimedia Commons File:Star_of_life2.svg), a trademarked mark; licence
    facts in SSOT item 254. The leading underscore keeps valid_key() from
    ever serving it as an icon."""
    if not _SOL_CACHE:
        with open(os.path.join(icon_dir(), "_star_of_life.svg"),
                  encoding="utf-8") as fh:
            src = fh.read()
        for pid in ("star", "rod", "snake"):
            m = re.search(r'id="%s"\s+d="([^"]+)"' % pid, src)
            _SOL_CACHE[pid] = m.group(1) if m else ""
    return _SOL_CACHE


def _symbol(kind: str, k: float, counter: int | None) -> str:
    """The symbol layer, scaled with the hull and centred, never rotated with
    it. `counter` turns it back by the card's rotation (the card does the rotating)."""
    rot = " rotate(%d 100 100)" % (-counter % 360) if counter else ""
    if kind == "cross":
        t = "translate(%.4f %.4f) scale(%.6f)%s" % (100 - 100 * k, 100 - 100 * k, k, rot)
        return '<g transform="%s" fill="%s"><path d="%s"/></g>' % (
            t, CROSS_RED, _cross(100, 100, 17, 6))
    if kind == "sol":
        p = _sol_paths()
        s = 0.36 * k   # the source is a 192-unit box
        t = "%s translate(%.4f %.4f) scale(%.5f)" % (
            rot.strip(), 100 - 96 * s, 100 - 96 * s, s)
        return ('<g transform="%s"><path d="%s" fill="%s" stroke="#FFFFFF" '
                'stroke-width="8"/><path d="%s" fill="#FFFFFF"/>'
                '<path d="%s" fill="#FFFFFF"/></g>'
                % (t.strip(), p["star"], SOL_ORANGE, p["rod"], p["snake"]))
    return ""


# --- rendering: Live Track Aircraft's pipeline, rotation fit 1.0 -----------
_SVG_OPEN = re.compile(r"<svg\b[^>]*>", re.I)
_PAINT_ATTR = re.compile(r'\s(?:fill|stroke)\s*=\s*"(?!none\s*")[^"]*"', re.I)
_PAINT_STYLE = re.compile(r"(?:fill|stroke)\s*:\s*[^;\"']*;?", re.I)
EDGE = "#1F2327"
# A painted icon whose flag carries black loses its edge in EDGE on dark
# tiles; it gets its own outline colour (Lee, 2026-09-27: uae grey).
EDGE_FOR = {"uae": "#9AA0A6"}
BADGE = "#1F2327"
OUTLINE_PX = 2.0
_SAFE = re.compile(r"^[a-z0-9]+$")

_OUTLINE_FILTER = (
    '<defs><filter id="e" filterUnits="userSpaceOnUse" x="0" y="0" '
    'width="200" height="200" color-interpolation-filters="sRGB">'
    '<feMorphology in="SourceAlpha" operator="dilate" radius="%.4f" result="d"/>'
    '<feFlood flood-color="%s" result="c"/>'
    '<feComposite in="c" in2="d" operator="in" result="edge"/>'
    '<feMerge><feMergeNode in="edge"/><feMergeNode in="SourceGraphic"/></feMerge>'
    '</filter></defs>')


def decolour(body: str) -> str:
    body = _PAINT_ATTR.sub(" ", body)
    return _PAINT_STYLE.sub("", body)


def render(path: str, key: str, degrees: int | None, size: int = 64,
           tone: str = "default", weight: float = 0.70, badge: bool = True,
           counter: int | None = None) -> str:
    """One icon: coloured, sized, rotated, and its symbol upright.

    `degrees` rotates the hull (integration-rotated mode). `counter` is set
    only when the CARD rotates: the hull stays north and the symbol is turned
    back by the angle the card is about to apply."""
    with open(path, "r", encoding="utf-8") as fh:
        src = fh.read()
    m = _SVG_OPEN.search(src)
    if not m:
        raise ValueError("no <svg> element")
    body = src[m.end():src.rfind("</svg>")]
    k = max(0.1, min(1.0, weight))
    parts = ["translate(%.4f %.4f)" % (100 - 100 * k, 100 - 100 * k),
             "scale(%.6f)" % k]
    if degrees:
        parts.append("rotate(%d 100 100)" % degrees)
    head = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
            'viewBox="0 0 200 200">' % (size, size))
    if key in PAINTED:
        art = '<g transform="%s">%s</g>' % (" ".join(parts), body)
    else:
        fill = TONES.get(tone, TONES["default"])
        art = '<g transform="%s" fill="%s">%s</g>' % (
            " ".join(parts), fill, decolour(body))
    sym = _symbol(SYMBOL_FOR.get(key, ""), k, counter)
    if badge:
        return (head + '<circle cx="100" cy="100" r="100" fill="%s"/>' % BADGE
                + art + sym + '</svg>')
    radius = OUTLINE_PX * 200.0 / size
    return (head + _OUTLINE_FILTER % (radius, EDGE_FOR.get(key, EDGE))
            + '<g filter="url(#e)">' + art + '</g>' + sym + '</svg>')


def icon_dir() -> str:
    return os.path.join(os.path.dirname(__file__), "icons")


def valid_key(key: str) -> bool:
    """Guard for the HTTP view: only the named icons, never a path."""
    return bool(_SAFE.match(key or "")) and key in ICON_KEYS


def icon_path(key: str) -> str | None:
    if not valid_key(key):
        return None
    p = os.path.join(icon_dir(), key + ".svg")
    return p if os.path.exists(p) else None
