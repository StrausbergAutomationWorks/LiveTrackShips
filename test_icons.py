"""Tests for the vessel icons (SSOT item 254).

Run: python test_icons.py   (here, or in the HA container via lts_boxtest.py)

Loaded by file path, like test_rot_and_types.py: icons.py imports only the
standard library. The raster checks need resvg_py and are skipped where it is
absent (the HA container); the XML checks run everywhere.
"""
import importlib.util
import math
import pathlib
import sys
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
_PKG = pathlib.Path(__file__).parent / "custom_components" / "live_track_ships"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


icons = _load("lts_icons", _PKG / "icons.py")
passed = failed = 0


def check(label, got, want):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}"
          + ("" if ok else f"\n         got {got!r}\n         want {want!r}"))


print("=== pick: USCG specifics, decade fallbacks, hazard digits select nothing ===")
for code, length, want in (
        (0, None, "generic"), (None, None, "generic"), ("x", None, "generic"),
        (100, None, "generic"), (8, None, "generic"), (10, None, "generic"),
        (15, None, "generic"), (16, None, "generic"), (90, None, "generic"),
        (99, None, "generic"), (1, None, "workboat"), (3, None, "generic"),
        (6, None, "offshore"), (11, None, "offshore"), (12, None, "fishing"),
        (14, None, "offshore"), (18, None, "workboat"),
        (20, None, "highspeed"), (25, None, "highspeed"), (29, None, "highspeed"),
        (30, None, "fishing"), (33, None, "dredger"), (35, None, "military"),
        (36, None, "sailing"), (37, None, "pleasure"), (38, None, "fishing"),
        (39, None, "military"), (40, None, "highspeed"), (45, None, "highspeed"),
        (51, None, "sar"), (55, None, "police"), (58, None, "medical"),
        (60, None, "passenger"), (61, None, "passenger"), (64, None, "passenger"),
        (65, None, "cruise"), (66, None, "ferry"), (67, None, "passenger"),
        (69, None, "passenger"), (70, None, "cargo"), (71, None, "cargo"),
        (74, None, "cargo"), (75, None, "bulk"), (76, None, "container"),
        (77, None, "carcarrier"), (78, None, "cargo"), (79, None, "cargo"),
        (80, None, "tanker"), (81, None, "tanker"), (84, None, "tanker"),
        (85, None, "tanker"), (86, None, "tug"), (89, None, "tanker"),
        ("70", None, "cargo")):
    check(f"type {code!r} -> {want}", icons.pick(code, length), want)

print("\n=== towing vessels: tug under 60 m; at 60 m+ atb or the tug pushing a barge (Lee 2026-09-30) ===")
check("52 at 164 m, no beam (SEA EAGLE II) -> atb", icons.pick(52, 164), "atb")
check("52 at 30 m -> tug", icons.pick(52, 30), "tug")
check("52 at exactly 60 m, no beam -> atb (60 m OR MORE)", icons.pick(52, 60), "atb")
check("52 at 59 m -> tug", icons.pick(52, 59), "tug")
check("31 at 90 m -> atb", icons.pick(31, 90), "atb")
check("32 at 61 m -> atb", icons.pick(32, 61), "atb")
check("57 at 120 m -> atb", icons.pick(57, 120), "atb")
check("57 at 20 m -> tug (was generic)", icons.pick(57, 20), "tug")
check("86 at 20 m -> tug (was atb)", icons.pick(86, 20), "tug")
check("86 with no length -> tug", icons.pick(86, None), "tug")
check("52 with no length -> tug", icons.pick(52, None), "tug")
check("70 at 300 m is not an atb", icons.pick(70, 300), "cargo")
check("70 at 300 m x 40 m is no tow", icons.tow_form(70, 300, 40), None)
for _t in (31, 32, 52, 57, 86):
    check(f"{_t} at 215 x 33 (PAT VOSS shape) -> tug", icons.pick(_t, 215, 33), "tug")
    check(f"{_t} at 215 x 33 -> barge", icons.tow_form(_t, 215, 33), "barge")
check("UNDAUNTED 150 x 18 -> atb", icons.pick(31, 150, 18), "atb")
check("OLIVE L. MOORE 222 x 22 -> atb", icons.pick(52, 222, 22), "atb")
check("beam exactly 15 -> atb", icons.tow_form(52, 100, 15), "atb")
check("beam 14.9 -> barge", icons.tow_form(52, 100, 14.9), "barge")
check("beam 24.9 -> atb", icons.tow_form(52, 100, 24.9), "atb")
check("beam exactly 25 -> barge", icons.tow_form(52, 100, 25), "barge")
check("towing astern (11) at 215 x 33 -> atb", icons.pick(57, 215, 33, 11), "atb")
check("towing astern as a string '11' -> atb", icons.tow_form(57, 215, 33, "11"), "atb")
check("pushing ahead (12) at 215 x 33 -> barge", icons.tow_form(57, 215, 33, 12), "barge")
check("t31 at 59 m x 33 -> plain tug, no barge", (icons.pick(31, 59, 33), icons.tow_for(31, 59, 33)), ("tug", None))
check("tow_for PAT VOSS", icons.tow_for(57, 215, 33), (215, 33))
check("tow_for clamps length", icons.tow_for(57, 900, 33), (400, 33))
check("tow_for clamps beam", icons.tow_for(57, 215, 500), (215, 70))
check("tow_for rounds", icons.tow_for(57, 215.4, 32.6), (215, 33))
check("tow_for: atb gets no barge", icons.tow_for(52, 222, 22), None)
check("tow_for: astern gets no barge", icons.tow_for(52, 215, 33, 11), None)
check("tow_for: garbage", (icons.tow_for(None, 215, 33), icons.tow_for(52, "x", 33), icons.tow_for(52, 215, "x")),
      (None, None, None))
check("choose passes beam and status", icons.choose("999999991", None, 57, 215, 33, 11), ("atb", icons.weight_for("atb", 215)))
check("choose: PAT VOSS is the tug at its length", icons.choose("999999992", None, 57, 215, 33),
      ("tug", icons.weight_for("tug", 215)))
_g = icons.tow_layout(215, 33)
check("PAT VOSS grid 3 x 3", (_g["across"], _g["long"]), (3, 3))
check("61 x 10 grid 1 x 1", (icons.tow_layout(61, 10)["across"], icons.tow_layout(61, 10)["long"]), (1, 1))
_narrow = [(L, B) for L in range(60, 401, 10) for B in (1, 5, 10, 14)
           if icons.tow_layout(L, B)["bw"] + 1e-9 < icons.tow_layout(L, B)["tug_w"]]
check("the barge is never narrower than the tug", _narrow, [])
_wide = [(L, B) for L in range(60, 401, 10) for B in range(1, 71, 3)
         if icons.tow_layout(L, B)["bw"] / 2 > icons.TOW_HALF_MAX + 1e-9]
check("the barge never wider than the reach allows", _wide, [])
check("the bow corners sit inside REACH_LIMIT", math.hypot(icons.TOW_HALF_MAX, 90) <= icons.REACH_LIMIT, True)
_sv = icons.render(icons.icon_path("tug"), "tug", None, 64, "default", 0.95, False, None, (215, 33))
ET.fromstring(_sv)
check("composite carries the barge colours", all(c in _sv for c in (icons.BARGE, icons.BARGE_HATCH, icons.BARGE_COAMING)), True)
check("composite: ONE outline filter", _sv.count('filter="url(#e)"'), 1)
check("composite keeps the tug's own paint", "#E0A273" in _sv, True)
check("composite: 9 barges", _sv.count(icons.BARGE_COAMING), 9)
_plain = icons.render(icons.icon_path("tug"), "tug", None, 64, "default", 0.65, False, None, None)
check("no tow: no barge", icons.BARGE in _plain, False)
check("tow ignored for any other key", icons.BARGE in icons.render(
    icons.icon_path("atb"), "atb", None, 64, "default", 0.9, False, None, (215, 33)), False)

print("\n=== every icon exists; nothing else is servable ===")
files = {p.stem for p in (_PKG / "icons").glob("*.svg")}
check("78 keys (22 vessels + netbuoy + sarheli + sarplane + 14 state + 39 named)",
      len(icons.ICON_KEYS), 78)
check("every key has a file", sorted(k for k in icons.ICON_KEYS if k not in files), [])
check("lng dropped", "lng" in icons.ICON_KEYS, False)
every_pick = {icons.pick(c, L) for c in range(0, 100) for L in (None, 20, 200)}
check("every pick() result is a key", sorted(every_pick - icons.ICON_KEYS), [])
for bad in ("_star_of_life", "../icons/tug", "lng", "", "Tug", "tug.svg"):
    check(f"valid_key({bad!r}) is False", icons.valid_key(bad), False)
check("icon_path('tug') exists", icons.icon_path("tug") is not None, True)

print("\n=== state vessels: one ship, one painted icon, by MMSI ===")
check("219517000 -> dannebrog", icons.special_for("219517000"), "dannebrog")
check("int MMSI -> dannebrog", icons.special_for(219517000), "dannebrog")
check("padded MMSI -> dannebrog", icons.special_for(" 219517000 "), "dannebrog")
check("a neighbour MMSI -> None", icons.special_for("219517001"), None)
check("None -> None", icons.special_for(None), None)
_state = set(icons.STATE_BY_IMO.values()) | set(icons.STATE_BY_MMSI.values())
check("every state icon is a key", sorted(_state - icons.ICON_KEYS), [])
check("every state icon is PAINTED", sorted(_state - icons.PAINTED), [])
check("IMO wins: Savarona under her OLD MMSI",
      icons.special_for("271000250", "5314810"), "savarona")
check("IMO wins over a mismatching MMSI",
      icons.special_for("219517000", "4603343"), "norge")
check("unknown IMO falls back to MMSI",
      icons.special_for("257001000", "9074729"), "norge")
check("no IMO: MMSI 271035111 -> savarona",
      icons.special_for(271035111, None), "savarona")
check("old Savarona MMSI alone is NOT listed",
      icons.special_for("271000250", None), None)
check("unknown both -> None", icons.special_for("1", "9074729"), None)
nge = icons.render(icons.icon_path("norge"), "norge", None, 64, "default", 0.8, False)
check("norge: red, white and blue", all(c in nge for c in
      ("#BA0C2F", "#FFFFFF", "#00205B")), True)
svr = icons.render(icons.icon_path("savarona"), "savarona", None, 64, "default", 0.95, False)
check("savarona: red and white", all(c in svr for c in ("#E30A17", "#FFFFFF")), True)
check("136 m -> weight 0.88", icons.weight_for("savarona", 136), 0.88)
for imo, mmsi, want in (("9463774", "461001000", "oman"),
                        ("9714460", "461002000", "oman"),
                        ("1004572", "461003000", "oman"),
                        ("9772929", "466443000", "qatar"),
                        ("4772326", "525114116", "indonesia")):
    check(f"IMO {imo} -> {want}", icons.special_for(None, imo), want)
    check(f"MMSI {mmsi} -> {want}", icons.special_for(mmsi, None), want)
check("Ang Pangulo by IMO alone", icons.special_for("548000000", "4608410"), "philippines")
_u = icons.render(icons.icon_path("uae"), "uae", None, 64, "default", 0.9, False)
check("uae: outline grey, not EDGE", "#9AA0A6" in _u and 'flood-color="#1F2327"' not in _u, True)
_q = icons.render(icons.icon_path("qatar"), "qatar", None, 64, "default", 0.9, False)
check("qatar: outline EDGE", 'flood-color="#1F2327"' in _q and "#9AA0A6" not in _q, True)
check("every EDGE_FOR key is PAINTED", sorted(set(icons.EDGE_FOR) - icons.PAINTED), [])
check("GRACEFUL by IMO", icons.special_for(None, "1011551"), "russia")
check("GRACEFUL by MMSI", icons.special_for("273294110", None), "russia")
check("VICTORIA by IMO", icons.special_for(None, "1009663"), "russia")
check("VICTORIA by MMSI", icons.special_for("273216780", None), "russia")
check("GALKYNYSH by IMO", icons.special_for(None, "9445435"), "turkmenistan")
check("MMSI 434113600 is NOT listed", icons.special_for("434113600", None), None)
check("UCKA by MMSI", icons.special_for("238122040", None), "croatia")
_t = icons.render(icons.icon_path("turkmenistan"), "turkmenistan", None, 64, "military", 0.9, False)
check("turkmenistan: green and red, not olive", all(c in _t for c in
      ("#00853A", "#D22630")) and "#8C9A4B" not in _t, True)
_h = icons.render(icons.icon_path("croatia"), "croatia", None, 64, "military", 0.9, False)
check("croatia: red, white and blue, not olive", all(c in _h for c in
      ("#FF0000", "#FFFFFF", "#171796")) and "#8C9A4B" not in _h, True)
for imo in ("1006960", "9544619"):
    check(f"IMO {imo} -> russia", icons.special_for(None, imo), "russia")
for gone in ("378374000", "319766000", "273352710"):
    check(f"MMSI {gone} is NOT listed", icons.special_for(gone, None), None)
_r = icons.render(icons.icon_path("russia"), "russia", None, 64, "military", 0.9, False)
check("russia: its own colours, not olive", all(c in _r for c in
      ("#FFFFFF", "#0039A6", "#D52B1E")) and "#8C9A4B" not in _r, True)
for imo, mmsi, want in (("1007043", "403003000", "saudi"),
                        ("9234240", "461006000", "oman"),
                        ("9803601", "242822300", "morocco"),
                        ("6915946", "242890000", "morocco"),
                        ("1006324", "470886000", "uae"),
                        ("1006336", "319801000", "uae"),
                        ("9693367", "470992000", "uae"),
                        ("9526758", "319150300", "bahrain"),
                        ):
    check(f"IMO {imo} -> {want}", icons.special_for(None, imo), want)
    check(f"MMSI {mmsi} -> {want}", icons.special_for(mmsi, None), want)
for gone in ("403007000", "319526000", "403001000", "466066000", "319650000"):
    check(f"MMSI {gone} is NOT listed", icons.special_for(gone, None), None)
for gone in ("9562805", "1003308", "1004704", "5617475", "1009120"):
    check(f"IMO {gone} is NOT listed", icons.special_for(None, gone), None)
for key, colours in (("oman", ("#DB161B", "#008000", "#FFFFFF")),
                     ("qatar", ("#8A1538", "#FFFFFF")),
                     ("indonesia", ("#CE1126", "#FFFFFF")),
                     ("philippines", ("#0038A8", "#CE1126", "#FFFFFF", "#FCD116")),
                     ("saudi", ("#006C35", "#FFFFFF")),
                     ("uae", ("#00732F", "#FFFFFF", "#000000", "#FF0000")),
                     ("bahrain", ("#CE1126", "#FFFFFF")),
                     ("morocco", ("#C1272D", "#006233"))):
    s = icons.render(icons.icon_path(key), key, None, 64, "military", 0.9, False)
    check(f"{key}: its own colours, not olive",
          all(c in s for c in colours) and "#8C9A4B" not in s, True)
dnb = icons.render(icons.icon_path("dannebrog"), "dannebrog", None, 64,
                   "military", 0.8, False, 90)
check("dannebrog keeps its red", "#C60C30" in dnb, True)
check("dannebrog keeps its white cross", dnb.count('fill="#FFFFFF"'), 1)
check("the military tone does not recolour it", "#8C9A4B" in dnb, False)
check("78.43 m -> weight 0.8", icons.weight_for("dannebrog", 78.43), 0.8)

print("\n=== tone ===")
for code, want in ((55, "police"), (3, "gov"), (35, "military"), (39, "military"),
                   (58, "white"), (51, "default"), (70, "default"), (None, "default")):
    check(f"type {code!r} -> {want}", icons.tone_for(code), want)
check("police blue", icons.TONES["police"], "#3D8BFF")
check("olive", icons.TONES["military"], "#8C9A4B")

print("\n=== length ramp (approved 2026-09-24) ===")
for L, want in ((12, 0.51), (60, 0.76), (190, 0.93), (300, 1.0), (500, 1.0),
                (4, 0.45), (8, 0.45)):
    check(f"{L} m -> {want}", icons.weight_for("cargo", L), want)
check("no length, pleasure -> 0.50", icons.weight_for("pleasure", None), 0.50)
check("no length, cargo -> 0.90", icons.weight_for("cargo", 0), 0.90)
check("junk length -> default", icons.weight_for("tug", "x"), 0.60)

print("\n=== bearing: heading, else course when moving, else HELD ===")
SLOW = icons.SLOW_KMH
check("heading wins, even at rest", icons.bearing(90, 180, 0.0, 10.0), (90.0, "heading"))
check("course when moving", icons.bearing(None, 180, SLOW, None), (180.0, "course"))
check("course just below 2 kn -> held", icons.bearing(None, 180, SLOW - 0.01, 45.0), (45.0, "held"))
check("slow, nothing held -> its course, as held", icons.bearing(None, 180, 0.5, None), (180.0, "held"))
check("slow, nothing held, no course -> none", icons.bearing(None, None, 0.5, None), (None, None))
check("slow, a move of 30 m+ beats the held angle", icons.bearing(None, 180, 0.5, 45.0, 300.0), (300.0, "held"))
check("slow, a move of 30 m+ beats a slow course", icons.bearing(None, 180, 0.5, None, 300.0), (300.0, "held"))
check("moving at 2 kn: course beats the move", icons.bearing(None, 180, SLOW, 45.0, 300.0), (180.0, "course"))
check("heading beats the move", icons.bearing(90, 180, 0.0, 10.0, 300.0), (90.0, "heading"))
check("held beats a slow course", icons.bearing(None, 180, 0.5, 45.0), (45.0, "held"))
check("arrival floor is 30 m", icons.ARRIVAL_MIN_M, 30.0)
_M = 1 / 111195.0   # degrees of latitude per metre, near enough
check("a move of 100 m north bears 0", round(icons.arrival_bearing(41.88, -87.63, 41.88 + 100 * _M, -87.63)), 0)
check("a move of 100 m east bears 90", round(icons.arrival_bearing(41.88, -87.63, 41.88, -87.63 + 100 * _M / math.cos(math.radians(41.88)))), 90)
check("a move of 100 m south-west bears 225", round(icons.arrival_bearing(41.88, -87.63, 41.88 - 70.71 * _M, -87.63 - 70.71 * _M / math.cos(math.radians(41.88)))), 225)
check("29 m is jitter: no bearing", icons.arrival_bearing(41.88, -87.63, 41.88 + 29 * _M, -87.63), None)
check("31 m is a move", icons.arrival_bearing(41.88, -87.63, 41.88 + 31 * _M, -87.63) is not None, True)
check("no previous fix: no bearing", icons.arrival_bearing(None, None, 41.88, -87.63), None)
check("no speed -> held, not course", icons.bearing(None, 180, None, 30.0), (30.0, "held"))
check("moving, no course -> held", icons.bearing(None, None, 20.0, 30.0), (30.0, "held"))
check("heading 360 wraps", icons.bearing(360, None, None, None), (0.0, "heading"))
check("slow, course 0 at speed 0 is NO course", icons.bearing(None, 0, 0.0, None), (None, None))
check("slow, course 360 with no speed is NO course", icons.bearing(None, 360, None, None), (None, None))
check("course 0 at speed 0 does not replace a held angle", icons.bearing(None, 0, 0.0, 45.0), (45.0, "held"))
check("course 0 while MOVING is north", icons.bearing(None, 0, 20.0, None), (0.0, "course"))
check("course 0 at a real slow speed is kept", icons.bearing(None, 0, 0.5, None), (0.0, "held"))
check("usable_course 0 at 0", icons.usable_course(0, 0), None)
check("usable_course 0.0 at None", icons.usable_course(0.0, None), None)
check("usable_course 49.4 at 0", icons.usable_course(49.4, 0), 49.4)

print("\n=== resolve: STRONG holds stick, WEAK seeds follow the newest slow course ===")
R = icons.resolve
check("moving: course, held strong", R(None, 120, 20.0, None), (120.0, "course", (120.0, True)))
check("a move of 30 m+: held strong", R(None, 10, 0.5, None, 300.0), (300.0, "held", (300.0, True)))
check("nothing held, slow course: seeded WEAK", R(None, 250, 0.3, None), (250.0, "held", (250.0, False)))
check("a WEAK seed follows a newer non-zero slow course", R(None, 40, 0.3, (250.0, False)), (40.0, "held", (40.0, False)))
check("a WEAK seed is not replaced by course 0 at rest", R(None, 0, 0.0, (250.0, False)), (250.0, "held", (250.0, False)))
check("a WEAK seed is not replaced by course 0 even when slow", R(None, 0, 0.5, (250.0, False)), (250.0, "held", (250.0, False)))
check("a STRONG hold sticks against a slow course", R(None, 40, 0.3, (120.0, True)), (120.0, "held", (120.0, True)))
check("a move replaces a STRONG hold", R(None, 40, 0.3, (120.0, True), 200.0), (200.0, "held", (200.0, True)))
check("heading: the hold is left as it is", R(90, 40, 0.0, (250.0, False)), (90.0, "heading", (250.0, False)))
check("nothing at all: nothing, hold unchanged", R(None, None, None, None), (None, None, None))
check("ODYSSEY: course 0 at 0, nothing held -> nothing", R(None, 0, 0.0, None), (None, None, None))
check("ODYSSEY: then 49.4 at 0 -> held weak 49.4", R(None, 49.4, 0.0, None), (49.4, "held", (49.4, False)))
check("rotated at rest: buoy WEST, sailboat EAST", icons.REST_DEG_FOR, {"netbuoy": 270, "sailing": 90})
check("only those two", sorted(icons.REST_DEG_FOR), ["netbuoy", "sailing"])
sv = icons.render(icons.icon_path("sailing"), "sailing", icons.SAIL_REST_DEG, 64, "default", 0.5, False, None)
ET.fromstring(sv)
check("an east sailboat turns its hull", "rotate(90 100 100)" in sv, True)
check("an east sailboat's rig is not turned", 'rotate(-' in sv or 'rotate(270' in sv, False)
check("quantise 357.6 -> 0", icons.quantise(357.6), 0)
check("quantise 2.4 -> 0", icons.quantise(2.4), 0)
check("quantise 47.6 -> 50", icons.quantise(47.6), 50)
check("quantise None", icons.quantise(None), None)

print("\n=== vessel palette: painted, and no colour shared between icons ===")
check("every palette key is a key", sorted(icons.VESSEL_PAINTED - icons.ICON_KEYS), [])
check("every palette key is PAINTED", sorted(icons.VESSEL_PAINTED - icons.PAINTED), [])
# named outright: a key dropped from VESSEL_PAINTED would also drop out of the
# check above and be decoloured to cream without any test noticing
check("the painted vessel set", sorted(icons.VESSEL_PAINTED - {"police", "sailing"}), sorted((
    "atb", "bulk", "carcarrier", "cargo", "container", "cruise", "dredger", "ferry",
    "fishing", "highspeed", "offshore", "passenger", "pleasure", "tanker", "tug", "workboat")))
check("tinted vessels stay tinted", sorted({"generic", "military", "medical", "sar"} & icons.PAINTED), [])
import re as _re
import os
_hex = _re.compile(r"#[0-9A-Fa-f]{6}")
_uses = {}
for _k in sorted(icons.PAINTED):
    for _c in set(h.upper() for h in _hex.findall(open(icons.icon_path(_k), encoding="utf-8").read())):
        _uses.setdefault(_c, set()).add(_k)
_state = set(icons.STATE_BY_IMO.values()) | set(icons.STATE_BY_MMSI.values()) | {"netbuoy"}
# "Same company, same color" (Lee, 2026-09-30): a colour may be shared only
# WITHIN a company (icons.COMPANY_FOR; an unlisted key is its own company).
_company = lambda k: icons.COMPANY_FOR.get(k, k)
_clash = sorted((c, sorted(u)) for c, u in _uses.items()
                if c != icons.EDGE.upper() and len({_company(k) for k in u}) > 1
                and u - _state)
check("no colour shared between icons of different companies (outline excepted)", _clash, [])
check("the companies", icons.COMPANY_FOR, {
    "odyssey": "citycruises", "elite": "citycruises",
    "seadogyr": "citycruises", "wendella": "wendella", "cwttaxi": "wendella",
    "shorelinetaxi": "shoreline", "cityview": "shoreline", "shorelinetour": "shoreline",
    "firstlady": "firstlady", "classiclady": "firstlady", "emeraldlady": "firstlady",
    "fairlady": "firstlady", "littlelady": "firstlady", "anitadee": "anitadee",
    "anitadee2": "anitadee", "innisfree": "chicagoline", "ftdearborn": "chicagoline",
    "marquette": "chicagoline",
    "capstreeter": "shoreline",    "starofchicago": "shoreline",    "skyview": "shoreline",    "fireboat": "fire",    "fireinflatable": "fire",    "versluis": "chicago",    "summerofgeorge": "lakefront",    "ouilmette": "wendella",    "lakeexpress": "lakeexpress",    "viking": "viking",    "vikingtender": "viking",    "paddlewheel": "paddlewheel",    "victory": "victory",    "windy": "windy",    "detroitprincess": "detroitprincess",
    "nauticaqueen": "nauticaqueen", "paddlewheelgreen": "paddlewheelgreen",
    "ladycaroline": "ladycaroline",
    "drummond46": "drummond", "drummond30": "drummond",})
check("the barge colours are in no icon file", sorted(c for c in (icons.BARGE, icons.BARGE_HATCH, icons.BARGE_COAMING)
      if c.upper() in _uses), [])
check("City Cruises share their blue #124A60", {"odyssey", "elite"} <= _uses.get("#124A60", set()), True)
_same = sorted((c, sorted(u)) for c, u in _uses.items()
               if c != icons.EDGE.upper() and len(u) > 1 and u - _state)
check("the exception is exercised: a shared colour exists within a company", bool(_same), True)
check("every shared colour stays inside one company",
      [c for c, u in _same if len({_company(k) for k in u}) > 1], [])

print("\n=== named boats: by MMSI alone, painted, a FIXED size (Lee 2026-09-30) ===")
_NAMED = {
    "367776910": ("islandtime", 0.59), "367496450": ("shorelinetaxi", 0.70),
    "367531970": ("shorelinetaxi", 0.70), "367576980": ("shorelinetaxi", 0.70),
    "367307630": ("shorelinetaxi", 0.70), "367454470": ("shorelinetaxi", 0.70),
    "367364840": ("shorelinetaxi", 0.70), "367023080": ("shorelinetaxi", 0.70),
    "366825870": ("cwttaxi", 0.70), "367170850": ("cwttaxi", 0.70),
    "367152790": ("cwttaxi", 0.70), "367162320": ("wendella", 0.75),
    "367648960": ("wendella", 0.75), "367442380": ("wendella", 0.75),
    "367521420": ("wendella", 0.75), "367360260": ("odyssey", 0.90),
    "368039870": ("odyssey", 0.85), "367409940": ("elite", 0.85),
    "367148850": ("elite", 0.90), "367350360": ("elite", 0.85),
    "366848350": ("seadogyr", 0.70), "367350620": ("seadogyr", 0.70),
    "367401440": ("seadogyr", 0.70)}   # Lee 2026-10-20: SEADOG III, IV, V all the yellow-deck Seadog
_NAMED.update({
    "367627830": ("cityview", 0.8),
    "366897080": ("shorelinetour", 0.78),
    "366853070": ("shorelinetour", 0.78),
    "367107750": ("firstlady", 0.78),
    "367608260": ("classiclady", 0.78),
    "367495590": ("classiclady", 0.78),
    "368156510": ("emeraldlady", 0.78),
    "367116070": ("fairlady", 0.74),
    "367398450": ("littlelady", 0.74),
    "367688370": ("anitadee2", 0.82),
    "367060580": ("anitadee", 0.75),
    "366912650": ("innisfree", 0.72),
    "367197480": ("ftdearborn", 0.7),
    "366982270": ("marquette", 0.68),
    "368088860": ("cwttaxi", 0.7),
    "338503254": ("sailing", 0.45)})
_NAMED.update({
    "367164050": ("capstreeter", 0.75),
    "366936590": ("capstreeter", 0.75),
    "367396720": ("starofchicago", 0.75),
    "367745090": ("skyview", 0.8),
    "367575550": ("fireboat", 0.8),
    "338237135": ("fireboat", 0.8),
    "338173767": ("fireinflatable", 0.45),
    "338173771": ("fireinflatable", 0.45),
    "367073840": ("versluis", 0.8),
    "366951920": ("summerofgeorge", 0.85),
    "366877570": ("ouilmette", 0.75),
    "366941210": ("lakeexpress", 0.9),
    "259070000": ("viking", 1.0),
    "982570174": ("vikingtender", 0.5),
    "982570175": ("vikingtender", 0.5),
    "368081650": ("paddlewheel", 0.75),
    "311050400": ("victory", 0.95),
    "311050300": ("victory", 0.95),
    "367505190": ("windy", 0.9),
    "366964380": ("detroitprincess", 0.9),
    "338236842": ("tug", 0.45),
})
_NAMED.update({   # batch 4, 2026-10-20
    "367164090": ("nauticaqueen", 0.80),
    "367578130": ("cityview", 0.8),
    "367107610": ("paddlewheelgreen", 0.80),
    "368285150": ("ladycaroline", 0.80),
    "367349450": ("drummond46", 0.88),
    "367065250": ("drummond30", 0.80),
})
check("66 boats", len(_NAMED), 66)
check("the table is exactly the named boats", icons.NAMED_BY_MMSI, _NAMED)
for _m, _want in _NAMED.items():
    check(f"MMSI {_m} -> {_want}", icons.named_for(_m), _want)
check("int MMSI", icons.named_for(367360260), ("odyssey", 0.90))
check("padded MMSI", icons.named_for(" 367360260 "), ("odyssey", 0.90))
check("a neighbour MMSI -> None", icons.named_for("367360261"), None)
check("None -> None", icons.named_for(None), None)
_nk = {k for k, _ in icons.NAMED_BY_MMSI.values()}
check("NAMED_KEYS is the table's keys less the type icons a row may name", sorted(icons.NAMED_KEYS), sorted(_nk - every_pick))
check("every named key is a key", sorted(_nk - icons.ICON_KEYS), [])
check("every named key is PAINTED", sorted(icons.NAMED_KEYS - icons.PAINTED), [])
check("no named key is reachable by type", sorted(every_pick & icons.NAMED_KEYS), [])
check("ISLAND TIME's 0.59 is the ramp at 20 m", icons.weight_for("generic", 20), 0.59)
print("  choose: state vessel, then named boat, then declared type")
check("named: broadcast 99 at 512 m ignored", icons.choose("367776910", None, 99, 512.0), ("islandtime", 0.59))
check("named: broadcast type 6 ignored", icons.choose("367531970", None, 6, 19.0), ("shorelinetaxi", 0.70))
check("named: no type, no length", icons.choose("367576980", None, None, None), ("shorelinetaxi", 0.70))
check("named: a freighter's type and length ignored", icons.choose("367148850", None, 70, 217.0), ("elite", 0.90))
check("a valid state IMO beats the named MMSI", icons.choose("367360260", "4537661", 60, 61.0),
      ("dannebrog", icons.weight_for("dannebrog", 61.0)))
check("a state MMSI keeps its length ramp", icons.choose("219517000", None, None, 78.43), ("dannebrog", 0.8))
check("unnamed: type and length ramp", icons.choose("367360261", None, 60, 61.0),
      ("passenger", icons.weight_for("passenger", 61.0)))
import inspect as _inspect
check("no name is taken, so none is compared", "name" in _inspect.signature(icons.choose).parameters, False)
for _k in sorted(icons.NAMED_KEYS):
    _src = open(icons.icon_path(_k), encoding="utf-8").read()
    _cols = set(h.upper() for h in _re.findall(r"#[0-9A-Fa-f]{6}", _src))
    _out = icons.render(icons.icon_path(_k), _k, None, 64, "military", 0.8, False).upper()
    check(f"{_k}: every own colour served", sorted(c for c in _cols if c not in _out), [])
    check(f"{_k}: the military tone does not tint it", "#8C9A4B" in _out, "#8C9A4B" in _cols)
check("islandtime animates", "<animate" in open(icons.icon_path("islandtime"), encoding="utf-8").read(), True)
print("  batch 2 (Lee 2026-09-30 evening)")
check("Shoreline outlines brand blue, First Lady gold, uae grey", icons.EDGE_FOR, {'uae': '#9AA0A6', 'shorelinetaxi': '#00559C', 'cityview': '#00559C', 'shorelinetour': '#00559C', 'firstlady': '#BB8833', 'classiclady': '#BB8833', 'emeraldlady': '#BB8833', 'fairlady': '#BB8833', 'littlelady': '#BB8833', 'capstreeter': '#00559C', 'starofchicago': '#00559C', 'skyview': '#00559C', 'fireboat': '#FF002F', 'fireinflatable': '#FF002F', 'versluis': '#41B6E6', 'summerofgeorge': '#21C3F9', 'lakeexpress': '#425E8C', 'vikingtender': '#B10A32', 'paddlewheel': '#013CA3', 'victory': '#08264B', 'nauticaqueen': '#FDFDFC', 'paddlewheelgreen': '#00B669', 'ladycaroline': '#103831', 'drummond46': '#004684', 'drummond30': '#004684'})
for _k, _c in icons.EDGE_FOR.items():
    check(f"{_k}: its outline colour is served", _c in icons.render(icons.icon_path(_k), _k, None, 64, "default", 0.8, False), True)
check("338503254 sails at the 8 m ramp", icons.named_for("338503254"), ("sailing", icons.weight_for("sailing", 8)))
check("sailing is still UPRIGHT (held sail)", "sailing" in icons.UPRIGHT, True)
check("CARMALEE ROSE has no row (Lee 20:07: all tugs look the same)", icons.named_for("367325460"), None)
check("LADY GREBE is not shipped (no MMSI heard)", "ladygrebe" in icons.ICON_KEYS, False)
check("EVENING STAR and BRIGHT STAR share the Shoreline tour boat", (icons.named_for("366853070"), icons.named_for("366897080")),
      (("shorelinetour", 0.78), ("shorelinetour", 0.78)))

print("\n=== police: light bar, flash outside the outline, capped at 94 ===")
check("police is PAINTED", "police" in icons.PAINTED, True)
check("light bar blue", icons.POLICE_BLUE in open(icons.icon_path("police"), encoding="utf-8").read(), True)
check("no side rays left", "M138.43" in open(icons.icon_path("police"), encoding="utf-8").read(), False)
_over = []
for _w in [x / 100 for x in range(10, 101)]:
    _r = icons.police_flash_r(_w)
    if _w * icons._flash_reach(_r) > icons.REACH_LIMIT + 1e-9 or _r > icons.POLICE_FLASH_R:
        _over.append((_w, _r))
check("flash within 94 at every weight 0.10-1.00", _over, [])
check("small boat (0.55) gets the full 108", icons.police_flash_r(0.55), 108.0)
check("largest (1.0) is capped", icons.police_flash_r(1.0) < 108.0, True)
_p = icons.render(icons.icon_path("police"), "police", None, 64, "police", 0.68, False)
check("two flashes", _p.count("<ellipse"), 2)
check("flashes after the filtered group", _p.rfind("<ellipse") > _p.rfind('filter="url(#e)"'), True)
_fb = _re.findall(r'<ellipse[^>]*>\s*<animate[^>]*begin="([^"]+)"', _p)
check("the two flashes alternate", sorted(_fb), ["-0.4s", "0s"])
check("no overlay on cargo", "<ellipse" in icons.render(icons.icon_path("cargo"), "cargo", None, 64, "default", 0.9, False), False)

print("\n=== sailboat: upright rig, counter-rotated, not scaled ===")
check("sailing is PAINTED", "sailing" in icons.PAINTED, True)
check("UPRIGHT = symbols + sailing + windy", sorted(icons.UPRIGHT), sorted(set(icons.SYMBOL_FOR) | {"sailing", "windy"}))
_s0 = icons.render(icons.icon_path("sailing"), "sailing", None, 64, "default", 0.53, False)
_s9 = icons.render(icons.icon_path("sailing"), "sailing", None, 64, "default", 0.53, False, 90)
check("rig present", _s0.count("url(#rgm)") == 1 and _s0.count("url(#rgj)") == 1, True)
check("no counter -> rig upright, unrotated", "rotate(" in _s0, False)
check("counter 90 -> rig turned back by -90", '<g transform="rotate(270 100 100)">' in _s9, True)
check("counter 90 -> hull NOT rotated", "rotate(90 100 100)" in _s9, False)
check("rig after the filtered group", _s0.rfind("url(#rgm)") > _s0.rfind('filter="url(#e)"'), True)
_rig = lambda s: s[s.index('<g><defs><linearGradient id="rgm"'):]
_o5, _o10 = icons._overlay("sailing", 0.53, None), icons._overlay("sailing", 1.0, None)
check("rig identical at weight 0.53 and 1.0", _o5 == _o10, True)
check("rig carries no scale", "scale(" in _o5, False)
check("the rig is served as built", _o5 in _s0, True)
check("no rig on pleasure", "rgm" in icons.render(icons.icon_path("pleasure"), "pleasure", None, 64, "default", 0.5, False), False)

print("\n=== batch 3 (Lee 2026-10-03, MMSI.docx): fx layer, fire flash, WINDY ===")
for _k in sorted(icons.FX_KEYS):
    _fp = os.path.join(icons.icon_dir(), _k + "_fx.svg")
    check(f"{_k}: fx file exists", os.path.exists(_fp), True)
    check(f"{_k}_fx is not servable", icons.valid_key(_k + "_fx"), False)
    _r = icons.render(icons.icon_path(_k), _k, None, 64, "default", 0.9, False, None, None, True)
    _fxb = open(_fp, encoding="utf-8").read()
    _fxb = _fxb[_fxb.index(">") + 1:_fxb.rfind("</svg>")]
    check(f"{_k}: fx served", _fxb in _r, True)
    check(f"{_k}: fx after the filtered group", _r.rfind(_fxb) > _r.rfind('filter="url(#e)"'), True)
    check(f"{_k}: fx at the art's scale", '<g transform="translate(10.0000 10.0000) scale(0.900000)">' + _fxb in _r, True)
_rest = lambda k, **kw: icons.render(icons.icon_path(k), k, None, 64, "default", 0.9, False, **kw)
check("wake keys", sorted(icons.WAKE_KEYS), ["lakeexpress", "paddlewheel", "paddlewheelgreen"])
check("lakeexpress at rest: no wake", "lewk" in _rest("lakeexpress"), False)
check("lakeexpress moving: wake", "lewk" in _rest("lakeexpress", moving=True), True)
check("paddlewheel at rest: no wake", "type=\"scale\"" in _rest("paddlewheel"), False)
check("paddlewheel moving: the wake spreads (scale)", "type=\"scale\"" in _rest("paddlewheel", moving=True), True)
check("paddlewheel at rest: paddles still turn, 12 a cycle", "to=\"0 12\"" in _rest("paddlewheel"), True)
check("detroitprincess at rest: glow stays", "dpg" in _rest("detroitprincess"), True)
check("is_moving", [icons.is_moving(v) for v in (None, 0, 3.7, icons.SLOW_KMH, 20, "x")], [False, False, False, True, True, False])
check("338236842 is the stock tug at the 7 m ramp", icons.named_for("338236842"), ("tug", icons.weight_for("tug", 7)))
check("fx keys are exactly the four", sorted(icons.FX_KEYS), ["detroitprincess", "lakeexpress", "paddlewheel", "paddlewheelgreen"])
check("every _fx file belongs to an FX key", sorted(f[:-7] for f in os.listdir(icons.icon_dir()) if f.endswith("_fx.svg")),
      sorted(icons.FX_KEYS))
_f = icons.render(icons.icon_path("fireboat"), "fireboat", None, 64, "default", 0.8, False)
check("fireboat: two flashes", _f.count("<ellipse"), 2)
check("fireboat: flashes red, not police blue", (icons.FIRE_RED in _f, icons.POLICE_BLUE in _f), (True, False))
check("fireboat: flashes after the filtered group", _f.rfind("<ellipse") > _f.rfind('filter="url(#e)"'), True)
check("fireboat: its own gradient ids", ('id="ffa"' in _f, 'id="ffb"' in _f, 'id="pfa"' in _f), (True, True, False))
check("fireboat: alternate", sorted(_re.findall(r'<ellipse[^>]*>\s*<animate[^>]*begin="([^"]+)"', _f)), ["-0.4s", "0s"])
check("fireinflatable has no flash", "<ellipse" in icons.render(icons.icon_path("fireinflatable"), "fireinflatable", None, 64, "default", 0.45, False), False)
check("police still blue", icons.POLICE_BLUE in icons.render(icons.icon_path("police"), "police", None, 64, "police", 0.6, False), True)
_MIR = "matrix(-1 0 0 1 200 0)"
_w = lambda c: icons.render(icons.icon_path("windy"), "windy", None, 64, "default", 0.9, False, c)
check("windy: no angle -> mirrored (west), not turned", (_MIR in _w(None), "rotate(" in _w(None)), (True, False))
check("windy: 90 -> turned back, east", ("rotate(270 100 100)" in _w(90), _MIR in _w(90)), (True, False))
check("windy: 179 -> east", _MIR in _w(179), False)
check("windy: 180 -> west", ("rotate(180 100 100)" in _w(180), _MIR in _w(180)), (True, True))
check("windy: 200 -> turned back 160, west", ("rotate(160 100 100)" in _w(200), _MIR in _w(200)), (True, True))
check("windy: mirror applied to the art first", _w(200).index("rotate(160") < _w(200).index(_MIR), True)
check("windy is UPRIGHT, so the URL carries s=", "windy" in icons.UPRIGHT, True)
check("only windy is side view", sorted(icons.SIDEVIEW), ["windy"])
check("cargo never mirrored", _MIR in icons.render(icons.icon_path("cargo"), "cargo", None, 64, "default", 0.9, False, 200), False)
check("paddlewheel paddles animate", "<animateTransform" in open(icons.icon_path("paddlewheel"), encoding="utf-8").read(), True)
print("  batch 4 (Lee 2026-10-20)")
_pg = open(icons.icon_path("paddlewheelgreen"), encoding="utf-8").read()
check("paddlewheelgreen: Lee's green, no Saugatuck blue", ("#00B669" in _pg, "#013CA3" in _pg.upper()), (True, False))
check("paddlewheelgreen: paddles animate", "<animateTransform" in _pg, True)
check("paddlewheelgreen: its own gradient and clip ids", ("pgw" in _pg, "pww" in _pg, "pgc" in _pg, "pwc" in _pg), (True, False, True, False))
check("paddlewheelgreen at rest: no wake", "type=\"scale\"" in _rest("paddlewheelgreen"), False)
check("paddlewheelgreen moving: the wake spreads (scale)", "type=\"scale\"" in _rest("paddlewheelgreen", moving=True), True)
# Lee 2026-10-20 21:55: the gaps between the paddles are the water (OSM standard tiles,
# measured #AAD3DF); the green boat one step off, being another company.
check("paddlewheel: gaps the water blue", "#AAD3DF" in open(icons.icon_path("paddlewheel"), encoding="utf-8").read(), True)
check("paddlewheelgreen: gaps the water blue, one step off", "#AAD3E0" in open(icons.icon_path("paddlewheelgreen"), encoding="utf-8").read(), True)
check("paddles twice as tall (6.8)", all('height="6.8"' in open(icons.icon_path(k), encoding="utf-8").read() for k in ("paddlewheel", "paddlewheelgreen")), True)
check("RIVER VIEW draws CITYVIEW", icons.named_for("367578130"), icons.named_for("367627830"))
_lc = open(icons.icon_path("ladycaroline"), encoding="utf-8").read()
check("seadogry is retired: no key, no file", ("seadogry" in icons.ICON_KEYS, os.path.exists(os.path.join(icons.icon_dir(), "seadogry.svg"))), (False, False))
check("SEADOG III, IV, V draw the same icon", {icons.named_for(m)[0] for m in ("367401440", "366848350", "367350620")}, {"seadogyr"})
for _k in ("drummond46", "drummond30"):
    _d = open(icons.icon_path(_k), encoding="utf-8").read()
    check(f"{_k}: Lee's #004684 fill", "#004684" in _d, True)
    check(f"{_k}: its own gradient id", f'id="{_k}g"' in _d, True)
check("LADY CAROLINE: no letters (Lee)", "<text" in _lc, False)
check("LADY CAROLINE: the empty circle is there", 'r="12" fill="#123730"' in _lc, True)
check("NAUTICA QUEEN: white outline, white pilot house", "#FDFDFC" in open(icons.icon_path("nauticaqueen"), encoding="utf-8").read(), True)

print("\n=== render: strict XML for every icon, angle, tone and mode ===")
bad = []
n = 0
for key in sorted(icons.ICON_KEYS):
    path = icons.icon_path(key)
    for deg in (None, 0, 45, 200):
        for tone in icons.TONES:
            for badge in (True, False):
                for counter in (None, 90):
                    s = icons.render(path, key, deg, 64, tone, 0.8, badge, counter)
                    n += 1
                    try:
                        ET.fromstring(s)
                    except ET.ParseError as ex:
                        bad.append((key, deg, tone, badge, str(ex)))
check(f"{n} renders parse", bad, [])
med = icons.render(icons.icon_path("medical"), "medical", 45, 64, "white", 0.8, False)
check("medical carries the red cross", icons.CROSS_RED in med, True)
check("the cross is NOT rotated with the hull",
      med.count("rotate(45 100 100)"), 1)
sar = icons.render(icons.icon_path("sar"), "sar", 45, 64, "default", 0.8, False)
check("sar carries the orange star", icons.SOL_ORANGE in sar, True)
check("sar carries rod and snake", sar.count('fill="#FFFFFF"') >= 2, True)
turned = icons.render(icons.icon_path("sar"), "sar", None, 64, "default", 0.8, False, 90)
check("card rotation: symbol counter-rotated by -90", "rotate(270 100 100)" in turned, True)
check("card rotation: hull NOT rotated", "rotate(90 100 100)" in turned, False)
plain = icons.render(icons.icon_path("cargo"), "cargo", 45, 64, "default", 0.8, False, 90)
check("no symbol on cargo, counter ignored", "rotate(270" in plain, False)
check("police drawn blue", 'fill="#3D8BFF"' in icons.render(
    icons.icon_path("police"), "police", 0, 64, "police", 0.8, False), True)

print("\n=== raster: no rotation clips, badge-free has no disc ===")
try:
    import io
    import resvg_py
    from PIL import Image
except ImportError:
    print("  skip resvg_py/PIL not installed here")
else:
    clipped = []
    for key in sorted(icons.ICON_KEYS):
        for deg in range(0, 360, 15):
            s = icons.render(icons.icon_path(key), key, deg, 128, "default", 1.0, False)
            im = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(
                svg_string=s, width=128, height=128)))).convert("RGBA")
            a = im.getchannel("A")
            w, h = im.size
            edge = [a.getpixel((x, 0)) for x in range(w)] + \
                   [a.getpixel((x, h - 1)) for x in range(w)] + \
                   [a.getpixel((0, y)) for y in range(h)] + \
                   [a.getpixel((w - 1, y)) for y in range(h)]
            if max(edge) > 0:
                clipped.append((key, deg))
    check("every icon x 24 angles at full weight touches no edge", clipped, [])
    tclip = []
    for tow in ((60, 1), (60, 60), (61, 10), (215, 33), (300, 64), (400, 70), (400, 1)):
        for deg in range(0, 360, 15):
            s = icons.render(icons.icon_path("tug"), "tug", deg, 128, "default", 1.0, False, None, tow)
            im = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(
                svg_string=s, width=128, height=128)))).convert("RGBA")
            a = im.getchannel("A")
            w, h = im.size
            edge = [a.getpixel((x, 0)) for x in range(w)] + \
                   [a.getpixel((x, h - 1)) for x in range(w)] + \
                   [a.getpixel((0, y)) for y in range(h)] + \
                   [a.getpixel((w - 1, y)) for y in range(h)]
            if max(edge) > 0:
                tclip.append((tow, deg))
    check("the tug pushing a barge x 7 shapes x 24 angles at full weight touches no edge", tclip, [])

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
