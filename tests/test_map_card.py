"""Backlog 291: LiveTrackMapCard ships with this integration (card SSOT 67.7).

What it pins down:
  * the card is offered ONCE in async_setup_entry, before the feed starts and
    before the platforms are set up
  * async_unload_entry never touches the card (every restart unloads)
  * async_remove_entry withdraws only when no OTHER entry of the domain is left
  * the shipped files: the released bundle and nothing precompressed beside
    it, shared_map_card.py verbatim, the manifest, the two Repairs
    translations, the .gitattributes rule

__init__.py imports Home Assistant, so setup and unload are read from its
syntax tree and async_remove_entry is compiled on its own against fakes. No
homeassistant import: runs locally and inside the container alike.
"""
import ast
import asyncio
import hashlib
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
COMP = REPO / "custom_components" / "live_track_ships"
INIT = COMP / "__init__.py"
FRONTEND = COMP / "frontend"
CARD = FRONTEND / "live-track-map-card.js"
DOMAIN = "live_track_ships"
# LiveTrackCore reference/shared_map_card.py, SHA-256 of its LF text (bin\lt_reference_drift.py)
REFERENCE_SHA12 = "15251d6fcc54"
# LiveTrackMapCard release v0.1.8 (tools/vendor_card.py checks the asset's .sha256)
RELEASE_SHA12, RELEASE_VERSION, RELEASE_SIZE = "7760014d5dda", "0.1.8+2bcbc9a", 1292750

passed = failed = 0


def check(label, got, want=True):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}"
          + ("" if ok else f"   got {got!r} want {want!r}"))


TREE = ast.parse(INIT.read_text(encoding="utf-8"))


def func(name):
    for node in TREE.body:
        if isinstance(node, ast.AsyncFunctionDef) and node.name == name:
            return node
    return None


def names(node):
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            out.add(n.id)
        elif isinstance(n, ast.Attribute):
            out.add(n.attr)
    return out


def awaited(node, name):
    return [n for n in ast.walk(node)
            if isinstance(n, ast.Await) and isinstance(n.value, ast.Call)
            and getattr(n.value.func, "id", getattr(n.value.func, "attr", None)) == name]


print("=== setup offers the card once, first ===")
setup = func("async_setup_entry")
offers = awaited(setup, "async_offer_map_card")
check("one awaited offer in async_setup_entry", len(offers), 1)
if offers:
    check("offered as (hass, DOMAIN, HERE / 'frontend')",
          [ast.unparse(a) for a in offers[0].value.args], ["hass", "DOMAIN", "HERE / 'frontend'"])
    starts = awaited(setup, "start")
    forwards = awaited(setup, "async_forward_entry_setups")
    check("before the feed starts", bool(starts) and offers[0].lineno < starts[0].lineno)
    check("before the platforms are set up",
          bool(forwards) and offers[0].lineno < forwards[0].lineno)
src = ast.unparse(TREE)
check("HERE is the component folder", "HERE = Path(__file__).parent" in src)
check("imports both calls from .shared_map_card",
      "from .shared_map_card import async_offer_map_card, async_withdraw_map_card" in src)

print("\n=== unload never touches the card ===")
used = names(func("async_unload_entry"))
for n in ("async_offer_map_card", "async_withdraw_map_card", "async_reconcile"):
    check(f"async_unload_entry does not name {n}", n in used, False)


print("\n=== only the domain's LAST entry withdraws ===")
remove = func("async_remove_entry")
check("async_remove_entry exists", remove is not None)


def run_remove(entry_ids, removed):
    mod = ast.Module(body=[remove], type_ignores=[])
    calls = []

    async def withdraw(hass, domain):
        calls.append(domain)

    ns = {"DOMAIN": DOMAIN, "async_withdraw_map_card": withdraw,
          "HomeAssistant": object, "ConfigEntry": object}
    exec(compile(ast.fix_missing_locations(mod), str(INIT), "exec"), ns)

    class E:
        def __init__(self, i):
            self.entry_id = i

    class CE:
        def async_entries(self, domain):
            assert domain == DOMAIN
            return [E(i) for i in entry_ids]

    class H:
        config_entries = CE()

    asyncio.run(ns["async_remove_entry"](H(), E(removed)))
    return calls


if remove is not None:
    check("the last entry withdraws", run_remove(["a"], "a"), [DOMAIN])
    check("another entry left: no withdrawal", run_remove(["a", "b"], "a"), [])
    check("several left: no withdrawal", run_remove(["a", "b", "c"], "b"), [])
    check("entry already gone from the list: still withdraws", run_remove([], "a"), [DOMAIN])

print("\n=== what ships ===")
data = CARD.read_bytes()
check("bundle size is the release's", len(data), RELEASE_SIZE)
check("bundle SHA-256 is the release's", hashlib.sha256(data).hexdigest()[:12], RELEASE_SHA12)
m = re.match(r"^/\*! live-track-map-card (\S+) \*/", data.split(b"\n", 1)[0].decode("utf-8"))
check("line 1 carries the release version", m and m.group(1), RELEASE_VERSION)
# Home Assistant would serve a stale .gz or .br in preference (card SSOT 67.5).
check("nothing beside it in frontend/", sorted(p.name for p in FRONTEND.iterdir()),
      ["live-track-map-card.js"])
lf = (COMP / "shared_map_card.py").read_bytes().replace(b"\r\n", b"\n")
check("shared_map_card.py is the reference verbatim", hashlib.sha256(lf).hexdigest()[:12],
      REFERENCE_SHA12)
man = json.loads((COMP / "manifest.json").read_text(encoding="utf-8"))
check("manifest: http in dependencies", "http" in man.get("dependencies", []))
check("manifest: lovelace in after_dependencies", "lovelace" in man.get("after_dependencies", []))
# 0.2.42 since 2026-11-20: Live Track writes only its own map-card resource rows (hacs/default#14499).
# 0.2.43 since 2026-11-21: the vessel photos are the library's (saw_livetrack.vessel_photos), IMO then MMSI.
check("manifest: the saw-livetrack requirement",
      [r for r in man.get("requirements", []) if r.startswith("saw-livetrack")],
      ["saw-livetrack>=0.2.43,<0.3"])
for rel in ("strings.json", "translations/en.json"):
    issues = json.loads((COMP / rel).read_text(encoding="utf-8")).get("issues", {})
    yml = issues.get("map_card_yaml_resource", {})
    dup = issues.get("map_card_duplicate_resources", {})
    check(f"{rel}: yaml issue has a title and {{url}}", bool(yml.get("title")) and "{url}" in yml.get("description", ""))
    check(f"{rel}: duplicate issue has a title and {{urls}}", bool(dup.get("title")) and "{urls}" in dup.get("description", ""))
rules = [l.strip() for l in (REPO / ".gitattributes").read_text(encoding="utf-8").splitlines()
         if l.strip() and not l.startswith("#")]
check(".gitattributes keeps the bundle byte for byte", "custom_components/*/frontend/** -text -diff" in rules)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
