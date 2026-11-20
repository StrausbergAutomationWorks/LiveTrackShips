"""ShipIconView does no disk work on the event loop (hacs/default#14499, review item 2).

Runs inside the Home Assistant container (lts_boxtest.py): web.py imports homeassistant."""
import ast, inspect, sys
sys.path.insert(0, "/config")
from custom_components.live_track_ships import icons, web  # noqa: E402

fails = 0


def check(name, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(("ok   " if ok else "FAIL ") + name + ("" if ok else "  got %r want %r" % (got, want)))


args = (None, "default", 0.8, False, None, None, False, None)
have = [k for k in sorted(icons.ICON_KEYS) if icons.icon_path(k)]
same = [k for k in have if web._render_key(k, *args) == icons.render(icons.icon_path(k), k, None, 64, "default", 0.8,
                                                                      False, None, None, False, None)]
check("every icon key with a file renders as before (%d)" % len(have), len(same), len(have))
check("tug with a barge renders as before",
      web._render_key("tug", 90, "default", 0.9, False, None, (215, 33), True, None),
      icons.render(icons.icon_path("tug"), "tug", 90, 64, "default", 0.9, False, None, (215, 33), True, None))
check("an unknown key is None", web._render_key("nope", *args), None)
check("a path is refused", web._render_key("../manifest", *args), None)

tree = ast.parse(inspect.cleandoc("\n" + inspect.getsource(web.ShipIconView.get)))
calls = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        f = node.func
        calls.add(f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "?"))
check("get calls no icon_path / render / open / os.*",
      sorted(calls & {"icon_path", "render", "open", "exists", "stat", "isfile", "listdir", "read_text", "read_bytes"}), [])
check("get uses valid_key", "valid_key" in calls, True)
check("get hands _render_key to the executor", "_render_key" in inspect.getsource(web.ShipIconView.get), True)
print("FAILURES", fails)
sys.exit(1 if fails else 0)
