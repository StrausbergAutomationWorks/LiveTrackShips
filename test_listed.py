"""Backlog 315 task 5: a vessel on the EnforcementVessels list, drawn by this integration with the list's look.

Runs anywhere with saw-livetrack 0.2.20 (no Home Assistant): enforcement.py and icons.py are loaded by path.
  * enforcement.py: listed or not, the glow, the label, the hover's name and agency, the attributes, the credit
  * the list's tone is saw_livetrack.aircraft_icons' "mil", here and in icons.TONES
  * icons.render with the glow: red then blue under the art, cut out of the closed silhouette, police flash replaced,
    a painted hull decoloured into the list's fill; and EVERY unlisted picture byte-identical to HEAD's renderer
    (why ARTWORK_VERSION is not bumped)
Run: python test_listed.py
"""
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile

from saw_livetrack import aircraft_icons as AI
from saw_livetrack import enforcement_vessels as ev

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = pathlib.Path(__file__).parent
_PKG = HERE / "custom_components" / "live_track_ships"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


enf = _load("lts_enforcement", _PKG / "enforcement.py")
icons = _load("lts_icons_listed", _PKG / "icons.py")
passed = failed = 0


def check(label, got, want=True):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}" + ("" if ok else f"\n         got {got!r}\n         want {want!r}"))


DOC = {"name": "EnforcementVessels", "schema": 1, "built": "b", "license": "ODbL-1.0",
       "theatres": [{"id": "s", "name": "Southern California", "box": [34.5, -121.0, 32.0, -117.0]}],
       "entries": [{"id": "uscg-wpc", "short": "USCG"}],
       "vessels": [{"mmsi": "338926432", "name": "USCGC Benjamin Bottoms (WPC 1132)", "agency": "US Coast Guard",
                    "hull": "WPC 1132", "entry": "uscg-wpc", "status": "sourced"},
                   {"mmsi": "366999662", "name": "USCGC Halibut", "agency": "US Coast Guard", "entry": "uscg-x",
                    "status": "newstatus"},
                   {"mmsi": "366999999", "name": "Gone", "agency": "US Coast Guard", "status": "cleared"},
                   {"mmsi": "367000001", "status": "sourced"}]}
reader = ev.VesselList(str(pathlib.Path(tempfile.mkdtemp()) / ev.CACHE_NAME))
reader._install(json.dumps(DOC).encode())

print("=== listed or not ===")
bb = enf.listed(reader, "338926432")
check("a sourced row is listed", bb is not None and bb.mmsi == "338926432")
check("a cleared row is not", enf.listed(reader, "366999999"), None)
check("an unlisted MMSI is not", enf.listed(reader, "211000000"), None)
check("no reader, no listing", enf.listed(None, "338926432"), None)
hal = enf.listed(reader, "366999662")
check("a status the reader does not know is listed", hal is not None)

print("\n=== the glow on a sourced row only (SALT's rule) ===")
check("sourced glows", enf.lights(bb), "glow")
check("another status does not", enf.lights(hal), None)

print("\n=== label, hover name and agency (06_MAP_CONTRACT.md D4b rules 12, 14) ===")
check("label is the entry's short form", enf.label(bb), "USCG")
check("label falls back to the agency", enf.label(hal), "US Coast Guard")
bare = enf.listed(reader, "367000001")
check("label with neither", enf.label(bare), "Listed vessel")
check("the hover name is the list's", enf.name(bb, "CG BOTTOMS"), "USCGC Benjamin Bottoms (WPC 1132)")
check("else the AIS name, stripped", enf.name(bare, "  CG NONAME "), "CG NONAME")
check("else none", enf.name(bare, "  "), None)
check("the hover agency", enf.operator_short(bb), "USCG")
check("none when unknown", enf.operator_short(bare), None)
long_v = ev.Vessel("367000002", "sourced", "X", "Customs and Border Protection Air and Marine")
check("agency cut to 22 with an ellipsis", enf.operator_short(long_v), "Customs and Border Pr…")
check("label cut the same way", enf.label(long_v), "Customs and Border Pr…")

print("\n=== attributes and credit ===")
a = enf.attributes(bb, "CG BOTTOMS")
check("attributes", a, {"enforcement_status": "sourced", "enforcement_agency": "US Coast Guard",
                        "enforcement_entry": "uscg-wpc", "hull": "WPC 1132",
                        "list_name": "USCGC Benjamin Bottoms (WPC 1132)",
                        "name": "USCGC Benjamin Bottoms (WPC 1132)", "operator_short": "USCG"})
check("unknown values omitted", sorted(enf.attributes(bare, None)), ["enforcement_status"])
check("credit: the source, then the list",
      enf.attribution("Data: aisstream.io"), "Data: aisstream.io; " + enf.LIST_ATTRIBUTION)
check("credit with no source", enf.attribution(None), enf.LIST_ATTRIBUTION)
check("the list's ODbL line", "Open Database License (ODbL) v1.0" in enf.LIST_ATTRIBUTION)

print("\n=== the list's tone is the library's Coast Guard green ===")
check("enforcement.LIST_TONE", enf.LIST_TONE, "mil")
check("icons.TONES['mil'] = aircraft_icons' 'mil'", icons.TONES["mil"], AI._TONES["mil"])
check("not Ships' own military olive", icons.TONES["mil"] != icons.TONES["military"])

print("\n=== the glow in the picture ===")


def pic(key, tone="default", lights=None, badge=False, weight=0.72):
    return icons.render(icons.icon_path(key), key, None, 64, tone, weight, badge, None, None, False, lights)


g = pic("military", "mil", "glow")
check("red and blue halos", '<filter id="lr"' in g and '<filter id="lb"' in g)
check("they alternate", 'values="1;0"' in g and 'values="0;1"' in g)
check("drawn from the art, defined once", g.count('id="art"'), 1)
check("UNDER the outlined art", g.index('filter="url(#lr)"') < g.index('<g filter="url(#e)">'))
check("cut out of the closed silhouette", g.count('operator="out"'), 2)
check("in the list's fill", 'fill="%s"' % icons.TONES["mil"] in g)
check("a badge ignores the glow", '<filter id="lr"' in pic("military", "mil", "glow", badge=True), False)
check("... and changes nothing on it: a police badge keeps its flash",
      'values="0;1;1;0;0"' in pic("police", "mil", "glow", badge=True))
check("... nor names its art", 'id="art"' in pic("military", "mil", "glow", badge=True), False)
check("no lights, no glow", '<filter id="lr"' in pic("military", "mil"), False)
pol = pic("police", "mil", "glow")
check("a listed police hull: no police flash", 'values="0;1;1;0;0"' in pol, False)
check("unlisted police keeps its flash", 'values="0;1;1;0;0"' in pic("police", "police"))
_src = pathlib.Path(icons.icon_path("police")).read_text(encoding="utf-8")
_body = _src[icons._SVG_OPEN.search(_src).end():_src.rfind("</svg>")]
check("a painted hull takes the list's fill", 'fill="%s"' % icons.TONES["mil"] in pol)
check("... decoloured: Ships' own shape, the list's colour", icons.decolour(_body) in pol)
check("unlisted police stays painted", _body in pic("police", "police"))

print("\n=== every unlisted picture is unchanged (no ARTWORK_VERSION bump) ===")
head_src = subprocess.run(["git", "show", "HEAD:custom_components/live_track_ships/icons.py"], cwd=HERE,
                          capture_output=True, text=True, encoding="utf-8").stdout
import types  # noqa: E402
old = types.ModuleType("lts_icons_head")
old.__file__ = str(_PKG / "icons.py")      # HEAD's code, reading the art beside the real module
exec(compile(head_src, old.__file__, "exec"), old.__dict__)
diff = n = 0
if "def render(" not in head_src:
    print("  SKIPPED: no git checkout here (the HA container); this comparison runs from the clone")
for key in (sorted(icons.ICON_KEYS) if "def render(" in head_src else ()):
    path = icons.icon_path(key)
    if path is None:
        continue
    for tone in ("default", "police", "gov", "military", "white", "sar"):
        for badge in (False, True):
            for deg in (None, 90):
                n += 1
                a1 = old.render(path, key, deg, 64, tone, 0.72, badge, None, None, False)
                b1 = icons.render(path, key, deg, 64, tone, 0.72, badge, None, None, False)
                diff += a1 != b1
if "def render(" in head_src:
    check(f"{n} pictures in every old tone, badge and angle, identical", diff, 0)
    check("every key compared", n > 1000)

print(f"\nchecks: {passed + failed}  passed: {passed}  failed: {failed}")
sys.exit(1 if failed else 0)
