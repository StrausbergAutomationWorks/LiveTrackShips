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
        (85, None, "tanker"), (86, None, "atb"), (89, None, "tanker"),
        ("70", None, "cargo")):
    check(f"type {code!r} -> {want}", icons.pick(code, length), want)

print("\n=== pick: a tug broadcasting the combined unit is an ATB ===")
check("52 at 164 m (SEA EAGLE II) -> atb", icons.pick(52, 164), "atb")
check("52 at 30 m -> tug", icons.pick(52, 30), "tug")
check("52 at exactly 60 m -> tug", icons.pick(52, 60), "tug")
check("31 at 90 m -> atb", icons.pick(31, 90), "atb")
check("32 at 61 m -> atb", icons.pick(32, 61), "atb")
check("57 at 120 m -> atb (USCG: 57 where 86 is unsupported)", icons.pick(57, 120), "atb")
check("57 at 20 m -> generic", icons.pick(57, 20), "generic")
check("52 with no length -> tug", icons.pick(52, None), "tug")
check("70 at 300 m is not an atb", icons.pick(70, 300), "cargo")

print("\n=== every icon exists; nothing else is servable ===")
files = {p.stem for p in (_PKG / "icons").glob("*.svg")}
check("39 keys (22 vessels + netbuoy + sarheli + sarplane + 14 state)",
      len(icons.ICON_KEYS), 39)
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
_hex = _re.compile(r"#[0-9A-Fa-f]{6}")
_uses = {}
for _k in sorted(icons.PAINTED):
    for _c in set(h.upper() for h in _hex.findall(open(icons.icon_path(_k), encoding="utf-8").read())):
        _uses.setdefault(_c, set()).add(_k)
_state = set(icons.STATE_BY_IMO.values()) | set(icons.STATE_BY_MMSI.values()) | {"netbuoy"}
_clash = sorted((c, sorted(u)) for c, u in _uses.items()
                if c != icons.EDGE.upper() and len(u) > 1 and u - _state)
check("no palette colour appears in two icons (outline excepted)", _clash, [])

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
check("UPRIGHT = symbols + sailing", sorted(icons.UPRIGHT), sorted(set(icons.SYMBOL_FOR) | {"sailing"}))
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

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
