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
    "philippines", "saudi", "uae", "bahrain", "morocco", "russia",
    "turkmenistan", "croatia",
    "islandtime", "shorelinetaxi", "cwttaxi", "wendella", "odyssey",
    "elite", "seadogry", "seadogyr",
    "cityview", "shorelinetour", "firstlady", "classiclady", "emeraldlady",
    "fairlady", "littlelady", "anitadee2", "anitadee", "innisfree", "ftdearborn",
    "marquette",
    "capstreeter", "starofchicago", "skyview", "fireboat", "fireinflatable", "versluis", "summerofgeorge", "ouilmette", "lakeexpress", "viking", "vikingtender", "paddlewheel", "victory", "windy", "detroitprincess",
    # Batch 4, 2026-10-20 (Lee)
    "nauticaqueen", "paddlewheelgreen", "ladycaroline"))

# ! NOT A VESSEL: a fishing-gear buoy (sources/base.py object_kind). A salmon
# seen from the side, mouth north, drawn IN ITS OWN COLOURS - salmon body,
# black scales, white head outlined black - so the renderer keeps its paint
# instead of filling it with a tone. Sized as the smallest aircraft draws:
# Live Track Aircraft's light-aircraft icons at weight 0.62 span 31 px of a
# 64 px image (bin\ship_icons\make_fish.txt, 2026-09-24), and so does this.
# The state-vessel icons below are painted too: their colours ARE the icon.
PAINTED = frozenset(("netbuoy", "dannebrog", "norge", "savarona", "oman",
                     "qatar", "indonesia", "philippines", "saudi", "uae",
                     "bahrain", "morocco", "russia", "turkmenistan",
                     "croatia"))
# ! THE VESSEL PALETTE (Lee, 2026-09-28): soft colours, never primaries,
# the real-world colours where a type has them (red tanker decks, yellow
# dredgers, white cruise ships), and no colour shared with another icon
# apart from the outline (test_icons.py checks). These draw their own
# paint; the tint vocabulary (TONES) stays for generic, military, medical
# and sar, whose colour carries meaning. Drafts and the check:
# bin\ship_icons\draft_palette\, SSOT item 254.
VESSEL_PAINTED = frozenset((
    "tanker", "atb", "tug", "dredger", "offshore", "fishing", "cargo",
    "bulk", "container", "carcarrier", "cruise", "ferry", "passenger",
    "highspeed", "workboat", "pleasure", "police", "sailing"))
# ! NAMED BOATS (Lee, 2026-09-29/30): one boat, or one fleet, drawn in its
# own colours from photographs - Chicago's party boat, water taxis, tour
# boats and City Cruises. Which boat gets which: NAMED_BY_MMSI below.
NAMED_KEYS = frozenset((
    "islandtime", "shorelinetaxi", "cwttaxi", "wendella", "odyssey",
    "elite", "seadogry", "seadogyr",
    "cityview", "shorelinetour", "firstlady", "classiclady", "emeraldlady",
    "fairlady", "littlelady", "anitadee2", "anitadee", "innisfree", "ftdearborn",
    "marquette",
    # Batch 3, 2026-10-03 (Lee, Ships 20_Research/MMSI.docx)
    "capstreeter", "starofchicago", "skyview", "fireboat", "fireinflatable", "versluis", "summerofgeorge", "ouilmette", "lakeexpress", "viking", "vikingtender", "paddlewheel", "victory", "windy", "detroitprincess",
    # Batch 4, 2026-10-20 (Lee)
    "nauticaqueen", "paddlewheelgreen", "ladycaroline"))
PAINTED = PAINTED | VESSEL_PAINTED | NAMED_KEYS
# ! "Same company, same color" (Lee, 2026-09-30): the no-shared-colour rule
# (test_icons.py) holds only BETWEEN companies. A key not listed is its own
# company. Seadog is City Cruises; Wendella runs Chicago Water Taxi.
COMPANY_FOR = {
    "odyssey": "citycruises", "elite": "citycruises",
    "seadogry": "citycruises", "seadogyr": "citycruises",
    "wendella": "wendella", "cwttaxi": "wendella",
    "shorelinetaxi": "shoreline", "cityview": "shoreline", "shorelinetour": "shoreline",
    "firstlady": "firstlady", "classiclady": "firstlady", "emeraldlady": "firstlady",
    "fairlady": "firstlady", "littlelady": "firstlady",
    "anitadee": "anitadee", "anitadee2": "anitadee",
    "innisfree": "chicagoline", "ftdearborn": "chicagoline", "marquette": "chicagoline",
    # Batch 3 (2026-10-03). "fire": Lee's scheme for any US fireboat; "chicago": the City.
    "capstreeter": "shoreline",
    "starofchicago": "shoreline",
    "skyview": "shoreline",
    "fireboat": "fire",
    "fireinflatable": "fire",
    "versluis": "chicago",
    "summerofgeorge": "lakefront",
    "ouilmette": "wendella",
    "lakeexpress": "lakeexpress",
    "viking": "viking",
    "vikingtender": "viking",
    "paddlewheel": "paddlewheel",
    "victory": "victory",
    "windy": "windy",
    "detroitprincess": "detroitprincess",
    # Batch 4 (2026-10-20). 367107610's operator is not known: its own company,
    # so its copy of STAR OF SAUGATUCK's art carries colours nudged one step.
    "nauticaqueen": "nauticaqueen",
    "paddlewheelgreen": "paddlewheelgreen",
    "ladycaroline": "ladycaroline",
}
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
    "9445435": "turkmenistan",  # GALKYNYSH ex WIND, presidential; IMO only (MMSI
                                # 434113600 last update 2025-08-23)
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
    "238122040": "croatia",    # UCKA ex PODGORKA, Croatian Navy state yacht; no IMO
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

# ! NAMED BOATS, BY MMSI ALONE (Lee, 2026-09-30 04:21: "Just match on mmsi").
# No name check, no IMO: a boat on this list draws its icon whatever it
# broadcasts as name, type or length, and at a FIXED size, because the
# broadcast length is often wrong on these boats (ISLAND TIME says 512 x 64 m)
# and the sizes were chosen against each other: taxis 0.70 < Wendella 0.75
# < City Cruises 0.85-0.90. A state vessel (special_for) still wins.
# ! An MMSI can be reissued: when one of these boats is sold or renamed out
# of the fleet, take its row out. Names below are as BROADCAST (the two
# ODYSSEYs arrive mangled); they are comments, never compared.
# Research and sources: 20_Research/WATER_TAXIS_20260930.md; decisions in
# bin\ship_icons\draft_*\CHOSEN.md; SSOT item 254.
NAMED_BY_MMSI = {
    "367776910": ("islandtime", 0.59),     # ISLAND TIME; the ramp at 20 m
    "367496450": ("shorelinetaxi", 0.70),  # ASAP
    "367531970": ("shorelinetaxi", 0.70),  # GOTTA GO NOW
    "367576980": ("shorelinetaxi", 0.70),  # SKEDADDLE
    "367307630": ("shorelinetaxi", 0.70),  # GIDDY UP
    "367454470": ("shorelinetaxi", 0.70),  # LICKETY SPLIT
    "367364840": ("shorelinetaxi", 0.70),  # SHAKE A LEG (not yet heard by us)
    "367023080": ("shorelinetaxi", 0.70),  # BLUE DOG (not yet heard by us)
    "366825870": ("cwttaxi", 0.70),        # BRAVO
    "367170850": ("cwttaxi", 0.70),        # SUNLINER
    "367152790": ("cwttaxi", 0.70),        # WENDELLA LTD (not yet heard by us)
    "367162320": ("wendella", 0.75),       # WENDELLA
    "367648960": ("wendella", 0.75),       # LUCIA
    "367442380": ("wendella", 0.75),       # LINNEA
    "367521420": ("wendella", 0.75),       # LILA
    "367360260": ("odyssey", 0.90),        # ODYSSEY LAKE MI_IGAN
    "368039870": ("odyssey", 0.85),        # ODYSSEY CHICAGO_IVER
    "367409940": ("elite", 0.85),          # CHICAGO ELITE
    "367148850": ("elite", 0.90),          # SPIRIT OF CHICAGO
    "367350360": ("elite", 0.85),          # SPIRIT OF NAVY PIER
    "366848350": ("seadogry", 0.70),       # SEADOG IV (not yet heard by us)
    "367350620": ("seadogyr", 0.70),       # SEADOG V (SEADOG EXTREME)
    # Batch 2, 2026-09-30 evening (Lee): Shoreline's tour boats, the First Lady fleet,
    # Anita Dee, Chicago Line Cruises, one more water taxi, and a sailboat that broadcasts
    # no statics. A row may name a TYPE icon (sailing): it then keeps that icon's behaviour.
    "367627830": ("cityview", 0.8),           # CITYVIEW (tug and barge)
    "366897080": ("shorelinetour", 0.78),     # BRIGHT STAR
    "366853070": ("shorelinetour", 0.78),     # EVENING STAR
    "367107750": ("firstlady", 0.78),         # CHICAGO'S FIRST LADY
    "367608260": ("classiclady", 0.78),       # CLASSIC LADY
    "367495590": ("classiclady", 0.78),       # LEADING LADY (one design with CLASSIC LADY)
    "368156510": ("emeraldlady", 0.78),       # EMERALD LADY
    "367116070": ("fairlady", 0.74),          # FAIR LADY
    "367398450": ("littlelady", 0.74),        # LITTLE LADY
    "367688370": ("anitadee2", 0.82),         # THE ANITA DEE II
    "367060580": ("anitadee", 0.75),          # ANITA DEE
    "366912650": ("innisfree", 0.72),         # INNISFREE
    "367197480": ("ftdearborn", 0.7),         # FT DEARBORN
    "366982270": ("marquette", 0.68),         # MARQUETTE; trackers list this MMSI as the tug CASPIAN DAWN
    "368088860": ("cwttaxi", 0.7),            # ROBERT H (Lee 2026-09-30: a Chicago Water Taxi)
    "338503254": ("sailing", 0.45),           # no statics broadcast; an 8 x 3 m sailboat (Lee), the 8 m ramp
    # Batch 3, 2026-10-03 (Lee, Ships 20_Research/MMSI.docx; drafts bin\ship_icons\draft_mmsi\).
    "367164050": ("capstreeter", 0.75),     # CAP STREETER
    "366936590": ("capstreeter", 0.75),     # MARLYN
    "367396720": ("starofchicago", 0.75),   # STAR OF CHICAGO
    "367745090": ("skyview", 0.8),          # SKYVIEW
    "367575550": ("fireboat", 0.8),         # FRED A BUSSE
    "338237135": ("fireboat", 0.8),         # CFD Boat 3 (Chicago Fire Department; several fireboats use it)
    "338173767": ("fireinflatable", 0.45),  # CFD Zodiac 17
    "338173771": ("fireinflatable", 0.45),  # CFD Zodiac 9
    "367073840": ("versluis", 0.8),         # JAMES J. VERSLUIS (City of Chicago)
    "366951920": ("summerofgeorge", 0.85),  # SUMMER OF GEORGE (Chicago Lakefront Cruises)
    "366877570": ("ouilmette", 0.75),       # OUILMETTE (Wendella)
    "366941210": ("lakeexpress", 0.9),      # LAKE EXPRESS
    "259070000": ("viking", 1.0),           # VIKING OCTANTIS, IMO 9863194
    "982570174": ("vikingtender", 0.5),     # OCTANTIS TENDER 1
    "982570175": ("vikingtender", 0.5),     # OCTANTIS TENDER 2
    "368081650": ("paddlewheel", 0.75),     # STAR OF SAUGATUCK, a sternwheeler, 80 ft (name from our statics, 2026-10-20)
    "311050400": ("victory", 0.95),         # Victory Cruise Lines, IMO 9213129
    "311050300": ("victory", 0.95),         # Victory Cruise Lines, IMO 9213131
    "367505190": ("windy", 0.9),            # WINDY (side view, mirrors)
    "366964380": ("detroitprincess", 0.9),
    # Batch 4, 2026-10-20 (Lee; drafts bin\ship_icons\draft_nautica\).
    "367164090": ("nauticaqueen", 0.80),    # NAUTICA QUEEN, 32 x 9 m, Cleveland (draft b)
    "367578130": ("cityview", 0.8),         # RIVER VIEW (Lee: same icon as CITYVIEW; broadcasts 7 x 5 m)
    "367107610": ("paddlewheelgreen", 0.80),  # 26 x 8 m passenger, not yet heard by us
    "368285150": ("ladycaroline", 0.80),    # LADY CAROLINE, 29 x 10 m, Cleveland (Lee's picture, no letters)
    "338236842": ("tug", 0.45),           # a 7 x 4 m towing vessel that rarely broadcasts its type (Lee); the 7 m ramp  # DETROIT PRINCESS
}


def named_for(identity) -> tuple[str, float] | None:
    """(icon key, fixed weight) of a named boat, by MMSI alone, or None."""
    if identity is None:
        return None
    return NAMED_BY_MMSI.get(str(identity).strip())


def choose(identity, imo, ship_type, length_m, beam_m=None,
           nav_status=None) -> tuple[str, float]:
    """(icon key, weight) for an object of kind `vessel`: a state vessel
    (sized by its length), else a named boat (its fixed size), else the
    declared type (sized by its length). `imo` must already be validated.
    Beam and navigational status decide only a towing vessel (tow_form)."""
    key = special_for(identity, imo)
    if key:
        return key, weight_for(key, length_m)
    named = named_for(identity)
    if named:
        return named
    key = pick(ship_type, length_m, beam_m, nav_status)
    return key, weight_for(key, length_m)


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
    57: "tug",          # a push vessel whose dimensions include its tow (USCG) - tow_form
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
    86: "tug",          # integrated / articulated tug and barge (USCG) - tow_form
}

# Everything else in a decade takes the decade's icon, hazard digits included.
_DECADE = {2: "highspeed",      # WIG: nearest shape we have (Lee, 2026-09-24)
           4: "highspeed", 6: "passenger", 7: "cargo", 8: "tanker"}

# ! A TOWING VESSEL (Lee, 2026-09-30; Ships 30_Correspondence/
# BRIEF_tug_barge_20260930.md). The towing codes are 31 and 32 (towing), 52
# (tug), and 57 and 86, which the USCG AIS Encoding Guide gives a push vessel
# whose broadcast dimensions include its tow (USCG Safety Alert 04-20: 57, not
# 31, when towing ahead or alongside). ALL TUGS LOOK THE SAME (Lee): under
# TOW_MIN_LENGTH_M every one is the stock `tug`. At or above it the broadcast
# describes the boat AND its tow (SEA EAGLE II sends 52 at 164 m, SSOT section
# 6), and tow_form() is the ONE rule for how it is drawn:
#   - towing ASTERN (nav_status 11): `atb`. A hawser tow trails on its own
#     track; a rigid picture would point it wrong on every turn.
#   - no beam, or a beam of 15 to 25 m: `atb`, one barge with the tug in its
#     notch. ATB barges run about 18-26 m wide (UNDAUNTED 18, OLIVE L. MOORE 22).
#   - otherwise: the stock `tug` with a barge composed ahead of it by the
#     renderer (tow_for, render's `tow`), hopper barges in a grid sized from the
#     broadcast - one wide under 15 m, three wide at 33 m (PAT VOSS, 3 x 3).
# ! KNOWN MISS: a tow two hoppers wide (~21 m) draws `atb`; beam alone cannot
# tell it from an ATB (Lee 22:17, the lifelike choice of the two offered).
TOWING_TYPES = frozenset((31, 32, 52, 57, 86))
TOW_MIN_LENGTH_M = 60.0
ATB_BEAM_M = (15.0, 25.0)        # [low, high): an ATB's one wide barge
NAV_TOWING_ASTERN = 11
# What the picture URL may carry (web.py clamps to these as well).
TOW_LENGTH_LIMITS = (60, 400)
TOW_BEAM_LIMITS = (1, 70)


def _positive(v) -> float:
    try:
        f = float(v) if v else 0.0
    except (TypeError, ValueError):
        return 0.0
    return f if f > 0 and math.isfinite(f) else 0.0


def tow_form(ship_type, length_m=None, beam_m=None, nav_status=None):
    """None (not a towing code, or no length under TOW_MIN_LENGTH_M), "atb",
    or "barge": the stock tug with a barge composed ahead of it."""
    try:
        code = int(ship_type)
    except (TypeError, ValueError):
        return None
    if code not in TOWING_TYPES or _positive(length_m) < TOW_MIN_LENGTH_M:
        return None
    try:
        astern = int(nav_status) == NAV_TOWING_ASTERN
    except (TypeError, ValueError):
        astern = False
    beam = _positive(beam_m)
    if astern or not beam or ATB_BEAM_M[0] <= beam < ATB_BEAM_M[1]:
        return "atb"
    return "barge"


def tow_for(ship_type, length_m=None, beam_m=None, nav_status=None):
    """(length, beam) in whole metres, clamped, for the renderer's barge;
    None unless tow_form() says "barge"."""
    if tow_form(ship_type, length_m, beam_m, nav_status) != "barge":
        return None
    lo, hi = TOW_LENGTH_LIMITS
    blo, bhi = TOW_BEAM_LIMITS
    return (max(lo, min(hi, int(round(_positive(length_m))))),
            max(blo, min(bhi, int(round(_positive(beam_m))))))


def pick(ship_type, length_m=None, beam_m=None, nav_status=None) -> str:
    """Which silhouette. Never None; an unknown or absent type is generic."""
    try:
        code = int(ship_type)
    except (TypeError, ValueError):
        return "generic"
    if tow_form(code, length_m, beam_m, nav_status) == "atb":
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
    "turkmenistan": 0.80, "croatia": 0.75,
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


# A move at least this long by a vessel not making 2 kn is a boat easing into
# or out of its slip, not mooring jitter (the card's 30 m floor, card SSOT 40;
# on the river capture 920 at-rest moves were under 30 m and 148 over, 85 of
# them 100-965 m). Lee, 2026-09-29.
ARRIVAL_MIN_M = 30.0
_EARTH_M = 6371008.8


def arrival_bearing(prev_lat, prev_lon, lat, lon):
    """Initial great-circle bearing of the move from the previous fix to this
    one, degrees 0..360, or None: no previous fix, or a move under
    ARRIVAL_MIN_M (jitter has no direction)."""
    try:
        p1, l1, p2, l2 = (math.radians(float(v)) for v in (prev_lat, prev_lon, lat, lon))
    except (TypeError, ValueError):
        return None
    h = (math.sin((p2 - p1) / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin((l2 - l1) / 2) ** 2)
    if 2 * _EARTH_M * math.asin(min(1.0, math.sqrt(h))) < ARRIVAL_MIN_M:
        return None
    y = math.sin(l2 - l1) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(l2 - l1)
    return math.degrees(math.atan2(y, x)) % 360


def usable_course(course_deg, speed_kmh):
    """The course in degrees 0..360, or None. A course of exactly 0 (or 360)
    at speed 0 or with no speed is what a transponder sends when it has
    nothing: it is NO course, never north (ODYSSEY, 367360260, 2026-09-29)."""
    if course_deg is None:
        return None
    c = float(course_deg) % 360
    if c == 0.0 and not speed_kmh:
        return None
    return c


def resolve(heading_deg, course_deg, speed_kmh, held, arrival=None):
    """(bearing, basis, held) - `held` in and out is (degrees, strong) or None.
    06_MAP_CONTRACT.md D4.

    1. True heading when broadcast; the held angle is left as it is.
    2. Course over ground at 2 kn or more; held STRONG.
    3. Below that, the bearing of a move of ARRIVAL_MIN_M or more; held STRONG.
    4. The angle already held - but a WEAK one (seeded from a slow course) is
       replaced by each newer non-zero slow course (Lee, 2026-09-29).
    5. Nothing held: the slow course, held WEAK.
    Only a course at 2 kn or more, or a move of 30 m or more, sticks against
    later slow courses. A course of 0 at rest is no course (usable_course)."""
    if heading_deg is not None:
        return float(heading_deg) % 360, "heading", held
    course = usable_course(course_deg, speed_kmh)
    if course is not None and speed_kmh is not None and speed_kmh >= SLOW_KMH:
        return course, "course", (course, True)
    if arrival is not None:
        a = float(arrival) % 360
        return a, "held", (a, True)
    if held is not None:
        deg, strong = held
        if not strong and course:
            return course, "held", (course, False)
        return deg, "held", held
    if course is not None:
        return course, "held", (course, False)
    return None, None, held


def bearing(heading_deg, course_deg, speed_kmh, held, arrival=None):
    """(bearing, basis) or (None, None). 06_MAP_CONTRACT.md D4. A bare
    `held` angle counts as STRONG; the full ladder is resolve().

    True heading when broadcast - it is where the hull points, meaningful at
    rest. Else course over ground while moving at 2 kn or more. Below that a
    moored vessel's course is noise (Lee, 2026-09-24), so the angle is HELD:
    the bearing of the move it just made if that was ARRIVAL_MIN_M or more -
    it points the way it came into its slip; else the angle already held;
    else, with nothing held yet (first seen slow: after a restart, or back in
    range), its reported course, which the caller then holds. A held boat
    must point the right way, never snap north (Lee, 2026-09-29).
    With none of these there is nothing to show."""
    b, basis, _held = resolve(heading_deg, course_deg, speed_kmh,
                              None if held is None else (held, True), arrival)
    return b, basis


# A FISHING-GEAR BUOY (object_kind net_buoy, SSOT item 257) is not a vessel
# and the 2 kn rule is not for it (Lee, 2026-09-25): a buoy drifts slowly on
# its line and whatever heading or course it sends is the only direction it
# has. Heading first, then course at ANY speed, never held - but a course of 0
# at speed 0 or with no speed is no course (usable_course; Lee, 2026-09-29).
# With neither it is drawn pointing WEST - into the IMAGE, with no icon_rotation_deg, because D4
# allows only heading, course or held as a basis and "west" is none of them. West, not east
# (Lee, 2026-09-29: "West makes the fish look the most recognizable"); it was east from
# 2026-09-25 to 2026-09-29.
BUOY_REST_DEG = 270
SAIL_REST_DEG = 90
# The pictures drawn ROTATED in the image, with no icon_rotation_deg,
# when nothing gives them a direction: the net buoy, and the sailboat, whose
# rig stays upright (the renderer never turns the rig with `degrees`), so
# a harbour of idle sailboats still reads as sailboats (Lee, 2026-09-29).
REST_DEG_FOR = {"netbuoy": BUOY_REST_DEG, "sailing": SAIL_REST_DEG}


def buoy_bearing(heading_deg, course_deg, speed_kmh=None):
    """(bearing, basis) or (None, None) for a net buoy."""
    if heading_deg is not None:
        return float(heading_deg) % 360, "heading"
    course = usable_course(course_deg, speed_kmh)
    if course is not None:
        return course, "course"
    return None, None


# Quantised so the browser can cache: 72 variants per icon.
ROTATION_STEP = 5


def quantise(deg) -> int | None:
    if deg is None:
        return None
    return int(round((deg % 360) / ROTATION_STEP) * ROTATION_STEP) % 360


# --- the upright symbol ----------------------------------------------------
SYMBOL_FOR = {"medical": "cross", "sar": "sol"}
# Keys whose image carries something that must stand upright, so the
# picture URL carries the card's angle (s=) to counter-rotate it.
# ! SIDE VIEW (Lee, 2026-10-03): WINDY is drawn from the side, bow EAST. The
# whole picture is counter-rotated by the card's angle so she always stands
# up, and mirrored (bow WEST) for an angle of 180-359 or none: the sails stay
# with the hull and she never sails upside down. 0 rides as "no angle" (s= is
# dropped at 0), so due north draws her west - a flip at the line, as asked.
SIDEVIEW = frozenset({"windy"})
UPRIGHT = frozenset(SYMBOL_FOR) | {"sailing"} | SIDEVIEW
# ! EFFECTS LAYER (Lee, 2026-10-03): <key>_fx.svg - wakes, glow - drawn at the
# art's scale but OUTSIDE the outline filter, so it stays soft, as the police
# flash does. Not servable on its own: "_fx" fails valid_key().
FX_KEYS = frozenset({"lakeexpress", "paddlewheel", "detroitprincess", "paddlewheelgreen"})
# ! A WAKE shows only while the boat is moving (Lee, 2026-10-03 03:18): at or
# above SLOW_KMH, the line below which course is noise. The URL carries m=1.
# Detroit Princess's glow is not a wake: it shows at rest too.
WAKE_KEYS = frozenset({"lakeexpress", "paddlewheel", "paddlewheelgreen"})


def is_moving(speed_kmh) -> bool:
    try:
        return speed_kmh is not None and float(speed_kmh) >= SLOW_KMH
    except (TypeError, ValueError):
        return False
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


# --- overlays drawn OUTSIDE the outline filter ----------------------------
# ! POLICE (Lee, 2026-09-28): white hull, blue light bar, two lamps in
# wig-wag; each flash is a blue burst that reaches past the hull on its
# side. Nominal radius 108, CAPPED per weight so the burst - fading tail
# included - never reaches past 94 from the image centre: nothing clips
# at any heading. Outside the filter, so the glow stays soft.
POLICE_FLASH_R = 108.0
REACH_LIMIT = 94.0
_LY = 101
POLICE_BLUE, POLICE_HOT = "#3D8BFF", "#EEF6FF"


def _flash_reach(r: float) -> float:
    """Farthest point of one flash ellipse from the centre, art units."""
    cx = 85 - 0.25 * r
    return max(math.hypot(cx + r * math.cos(a) - 100,
                          _LY + 0.72 * r * math.sin(a) - 100)
               for a in (i * math.pi / 360 for i in range(720)))


_FLASH_CACHE: dict[float, float] = {}


def police_flash_r(k: float) -> float:
    """Largest radius <= POLICE_FLASH_R whose flash, scaled by k, stays
    within REACH_LIMIT. Rounded DOWN so the limit holds exactly."""
    k = round(max(0.1, min(1.0, k)), 2)
    if k not in _FLASH_CACHE:
        if k * _flash_reach(POLICE_FLASH_R) <= REACH_LIMIT:
            _FLASH_CACHE[k] = POLICE_FLASH_R
        else:
            lo, hi = 0.0, POLICE_FLASH_R
            for _ in range(40):
                mid = (lo + hi) / 2
                lo, hi = (mid, hi) if k * _flash_reach(mid) <= REACH_LIMIT else (lo, mid)
            _FLASH_CACHE[k] = math.floor(lo * 10) / 10
    return _FLASH_CACHE[k]


FIRE_RED, FIRE_HOT = "#FF002F", "#FFE9EC"   # Lee 2026-10-03: any US fireboat


def _police_flash(k: float, colour: str = POLICE_BLUE, hot: str = POLICE_HOT,
                  ids: tuple = ("pfa", "pfb")) -> str:
    r = police_flash_r(k)
    kt = 'keyTimes="0;0.06;0.38;0.48;1"'
    out = []
    for x, begin, g in ((85, "0s", ids[0]), (115, "-0.4s", ids[1])):
        cx = x + (-1 if x < 100 else 1) * r * 0.25
        out.append(
            '<defs><radialGradient id="%s"><stop offset="0" stop-color="%s"/>'
            '<stop offset="0.22" stop-color="%s" stop-opacity="0.95"/>'
            '<stop offset="0.6" stop-color="%s" stop-opacity="0.55"/>'
            '<stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient></defs>'
            '<ellipse cx="%.1f" cy="%d" rx="%.1f" ry="%.1f" fill="url(#%s)" opacity="0">'
            '<animate attributeName="opacity" values="0;1;1;0;0" %s dur="0.8s" '
            'begin="%s" repeatCount="indefinite"/></ellipse>'
            % (g, hot, colour, colour, colour,
               cx, _LY, r, 0.72 * r, g, kt, begin))
    return ('<g transform="translate(%.4f %.4f) scale(%.6f)">%s</g>'
            % (100 - 100 * k, 100 - 100 * k, k, "".join(out)))


# ! SAILBOAT (Lee, 2026-09-28): seen from shore - a tall mast, a white
# main and a slightly greyer jib with water between them, shaded, with a
# soft shadow and no outline. The hull turns with the heading; the RIG is
# counter-rotated so it always stands up, and it is NOT scaled by length
# (it would vanish at 13 m). The mast stands on the image centre, so hull
# and rig stay joined at any heading; reach 94 at the masthead.
RIG_MAIN = ("#F7F8FA", "#CBD3DB")
RIG_JIB = ("#E3E8ED", "#B3BDC7")
RIG_SPAR = "#8A7B6A"


def _rig(counter: int | None) -> str:
    top, boom, tack, foot, gap, drop = 8, 142, 56, 88, 6, 10
    jh, clew = top + 10 + drop, 99 - gap
    rot = ' transform="rotate(%d 100 100)"' % (-counter % 360) if counter else ""
    return (
        '<g%s><defs>'
        '<linearGradient id="rgm" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="%s"/>'
        '<stop offset="0.35" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>'
        '<linearGradient id="rgj" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="%s"/>'
        '<stop offset="0.55" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>'
        '<filter id="rgs" x="-20%%" y="-20%%" width="140%%" height="140%%">'
        '<feDropShadow dx="2.5" dy="3" stdDeviation="2.2" flood-color="%s" flood-opacity="0.38"/>'
        '</filter></defs><g filter="url(#rgs)">'
        '<path fill="url(#rgm)" d="M103 %d Q%d %d %d %d L103 %d Z"/>'
        '<path fill="url(#rgj)" d="M%d %d Q%d %d %d %d L%d %d Z"/>'
        '<rect x="99.5" y="%d" width="3" height="%d" rx="1.2" fill="%s"/>'
        '<rect x="102" y="%d" width="%d" height="2.4" rx="1" fill="%s"/>'
        '</g></g>'
        % (rot, RIG_MAIN[1], RIG_MAIN[0], RIG_MAIN[0], RIG_JIB[1], RIG_JIB[0], RIG_JIB[0], EDGE,
           top, boom - 6, (top + foot) // 2 + 8, boom, foot, foot + 2,
           clew - 1, jh, tack + 12, (jh + foot) // 2 + 10, tack, foot - 2, clew, foot - 2,
           top - 2, 104 - top, RIG_SPAR, foot - 1, boom - 101, RIG_SPAR))


def _overlay(key: str, k: float, counter: int | None) -> str:
    if key == "police":
        return _police_flash(k)
    if key == "fireboat":
        return _police_flash(k, FIRE_RED, FIRE_HOT, ("ffa", "ffb"))
    if key == "sailing":
        return _rig(counter)
    return ""


# --- rendering: Live Track Aircraft's pipeline, rotation fit 1.0 -----------
_SVG_OPEN = re.compile(r"<svg\b[^>]*>", re.I)
_PAINT_ATTR = re.compile(r'\s(?:fill|stroke)\s*=\s*"(?!none\s*")[^"]*"', re.I)
_PAINT_STYLE = re.compile(r"(?:fill|stroke)\s*:\s*[^;\"']*;?", re.I)
EDGE = "#1F2327"
# A painted icon whose flag carries black loses its edge in EDGE on dark
# tiles; it gets its own outline colour (Lee, 2026-09-27: uae grey).
EDGE_FOR = {
    "uae": "#9AA0A6",
    # Lee 2026-09-30: every Shoreline boat outlined in its brand blue, the First Lady
    # fleet in its gold.
    "shorelinetaxi": "#00559C",
    "cityview": "#00559C",
    "shorelinetour": "#00559C",
    "firstlady": "#BB8833",
    "classiclady": "#BB8833",
    "emeraldlady": "#BB8833",
    "fairlady": "#BB8833",
    "littlelady": "#BB8833",
    # Batch 3 (Lee, 2026-10-03, MMSI.docx)
    "capstreeter": "#00559C",
    "starofchicago": "#00559C",
    "skyview": "#00559C",
    "fireboat": "#FF002F",
    "fireinflatable": "#FF002F",
    "versluis": "#41B6E6",
    "summerofgeorge": "#21C3F9",
    "lakeexpress": "#425E8C",
    "vikingtender": "#B10A32",
    "paddlewheel": "#013CA3",
    "victory": "#08264B",
    # Batch 4 (Lee, 2026-10-20): Nautica Queen white, the green sternwheeler #00B669.
    "nauticaqueen": "#FDFDFC",
    "paddlewheelgreen": "#00B669",
    # Lady Caroline: the dark green of Lee's picture.
    "ladycaroline": "#103831",
}
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


# --- the barge ahead of a pushing tug (tow_form "barge") --------------------
# Colours of company `barge`, checked against every shipped icon (look_tow.py's
# settle, 2026-09-30; test_icons.py keeps them out of every icon file).
BARGE, BARGE_HATCH, BARGE_COAMING = "#7F868C", "#5F666C", "#A3A9AE"
HOPPER_L_M, HOPPER_B_M = 59.5, 10.7     # a 195 x 35 ft jumbo hopper barge
TUG_LEN_M = 30.0                        # the pushing boat's assumed length
TUG_MIN_UNITS = 30.0                    # never drawn shorter than this
TUG_ART = (64.0, 38.0, 136.0, 166.0)    # tug.svg's hull, x0 y0 x1 y1
# Half-width that keeps the barge's bow corners (y 10) within REACH_LIMIT.
TOW_HALF_MAX = math.floor(math.sqrt(REACH_LIMIT ** 2 - 90.0 ** 2))


def tow_layout(length_m: float, beam_m: float) -> dict:
    """Where the barge and the tug go in the 200-unit box, before the weight
    scale: the broadcast length spans y 10..190, the tug's stern at 190 and its
    bow against the barge. The barge is never narrower than the tug (a 61 x 10 m
    tow) and never wider than TOW_HALF_MAX each side."""
    L = max(TOW_LENGTH_LIMITS[0], min(TOW_LENGTH_LIMITS[1], float(length_m)))
    B = max(TOW_BEAM_LIMITS[0], min(TOW_BEAM_LIMITS[1], float(beam_m)))
    s = 180.0 / L
    tug_u = max(TUG_MIN_UNITS, TUG_LEN_M * s)
    f = tug_u / (TUG_ART[3] - TUG_ART[1])
    tug_w = (TUG_ART[2] - TUG_ART[0]) * f
    bw = min(2 * TOW_HALF_MAX, max(B * s, tug_w))
    return {"f": f, "tug_w": tug_w, "bow": 190.0 - tug_u,
            "tx": 100.0 - 100.0 * f, "ty": 190.0 - TUG_ART[3] * f,
            "bw": bw, "across": max(1, round(B / HOPPER_B_M)),
            "long": max(1, round((L - TUG_LEN_M) / HOPPER_L_M))}


def _tow_body(tug_body: str, length_m: float, beam_m: float) -> str:
    """The barge grid, then the tug's own body scaled into the stern."""
    g = tow_layout(length_m, beam_m)
    x0, top, end = 100.0 - g["bw"] / 2, 10.0, g["bow"] - 1.5
    cw, cl = g["bw"] / g["across"], (end - top) / g["long"]
    out = []
    for i in range(g["across"]):
        for j in range(g["long"]):
            x, y = x0 + i * cw, top + j * cl
            out.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="1.2" '
                       'fill="%s" stroke="%s" stroke-width="0.8"/>'
                       % (x + 0.5, y + 0.5, cw - 1, cl - 1, BARGE, BARGE_COAMING))
            nh = max(2, int(cl / 7))
            for h in range(nh):
                out.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="0.6" fill="%s"/>'
                           % (x + 2.5, y + 3 + h * (cl - 6) / nh, max(0.5, cw - 5),
                              (cl - 6) / nh - 1.2, BARGE_HATCH))
    out.append('<g transform="translate(%.3f %.3f) scale(%.5f)">%s</g>'
               % (g["tx"], g["ty"], g["f"], tug_body))
    return "".join(out)


def decolour(body: str) -> str:
    body = _PAINT_ATTR.sub(" ", body)
    return _PAINT_STYLE.sub("", body)


def render(path: str, key: str, degrees: int | None, size: int = 64,
           tone: str = "default", weight: float = 0.70, badge: bool = True,
           counter: int | None = None, tow=None, moving: bool = False) -> str:
    """One icon: coloured, sized, rotated, and its symbol upright.

    `tow` = (length, beam) in metres draws the stock tug pushing a barge
    (tow_for); honoured for key `tug` only.

    `degrees` rotates the hull (integration-rotated mode). `counter` is set
    only when the CARD rotates: the hull stays north and the symbol is turned
    back by the angle the card is about to apply."""
    with open(path, "r", encoding="utf-8") as fh:
        src = fh.read()
    m = _SVG_OPEN.search(src)
    if not m:
        raise ValueError("no <svg> element")
    body = src[m.end():src.rfind("</svg>")]
    if tow and key == "tug":
        body = _tow_body(body, *tow)
    k = max(0.1, min(1.0, weight))
    parts = ["translate(%.4f %.4f)" % (100 - 100 * k, 100 - 100 * k),
             "scale(%.6f)" % k]
    if degrees:
        parts.append("rotate(%d 100 100)" % degrees)
    if key in SIDEVIEW:
        if counter:
            parts.append("rotate(%d 100 100)" % (-counter % 360))
        if not counter or counter % 360 >= 180:
            parts.append("matrix(-1 0 0 1 200 0)")
    head = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
            'viewBox="0 0 200 200">' % (size, size))
    if key in PAINTED:
        art = '<g transform="%s">%s</g>' % (" ".join(parts), body)
    else:
        fill = TONES.get(tone, TONES["default"])
        art = '<g transform="%s" fill="%s">%s</g>' % (
            " ".join(parts), fill, decolour(body))
    fx = ""
    if key in FX_KEYS and (moving or key not in WAKE_KEYS):
        fp = os.path.join(os.path.dirname(path), key + "_fx.svg")
        if os.path.exists(fp):
            with open(fp, "r", encoding="utf-8") as fh:
                fsrc = fh.read()
            fm = _SVG_OPEN.search(fsrc)
            if fm:
                fx = '<g transform="%s">%s</g>' % (
                    " ".join(parts), fsrc[fm.end():fsrc.rfind("</svg>")])
    sym = fx + _symbol(SYMBOL_FOR.get(key, ""), k, counter) + _overlay(key, k, counter)
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
