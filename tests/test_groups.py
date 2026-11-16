"""Marker groups for the map's filter card (backlog 345, 06_MAP_CONTRACT.md D4f).
Runs anywhere with Python: python tests/test_groups.py"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "custom_components" / "live_track_ships"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from ship_types import GROUPS, group_for, label_for   # noqa: E402

passed = failed = 0


def check(label, got, want=True):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}" + ("" if ok else f"\n         got {got!r}\n         want {want!r}"))


print("=== the thirteen groups ===")
check("thirteen", len(GROUPS), 13)
check("orders 1-13, each once", sorted(o for _l, o in GROUPS.values()), list(range(1, 14)))
check("keys are lowercase words", all(k.replace("_", "").isalpha() and k == k.lower() for k in GROUPS), True)

print("=== every vessel has a group, from every code ===")
codes = [None, "x", -1, 100, 255] + list(range(0, 100))
groups = {c: group_for("vessel", c) for c in codes}
check("every code lands in a group", all(g in GROUPS for g in groups.values()), True)
check("no vessel lands in a non-vessel group",
      {g for g in groups.values()} & {"fishing_gear", "aton", "base_station", "sar_aircraft"}, set())
check("0 (unavailable) -> type not sent", group_for("vessel", 0), "type_unknown")
check("None -> type not sent", group_for("vessel", None), "type_unknown")
check("reserved 10 -> type not sent", group_for("vessel", 10), "type_unknown")
check("out of range 120 -> type not sent", group_for("vessel", 120), "type_unknown")
check("a labelled code is never 'type not sent'",
      [c for c in range(100) if label_for(c) and group_for("vessel", c) == "type_unknown"], [])
for code, want in [(70, "cargo"), (76, "cargo"), (79, "cargo"), (80, "tanker"), (85, "tanker"), (86, "tanker"),
                   (60, "passenger"), (65, "passenger"), (66, "passenger"), (69, "passenger"),
                   (30, "fishing"), (38, "fishing"), (12, "fishing"), (13, "fishing"),
                   (36, "pleasure"), (37, "pleasure"),
                   (52, "service"), (50, "service"), (31, "service"), (32, "service"), (53, "service"),
                   (33, "service"), (14, "service"), (5, "service"), (18, "service"),
                   (55, "government"), (51, "government"), (35, "government"), (39, "government"),
                   (3, "government"), (4, "government"),
                   (40, "other"), (45, "other"), (20, "other"), (90, "other"), (1, "other"), (56, "other")]:
    check(f"type {code} ({label_for(code)}) -> {want}", group_for("vessel", code), want)
check("a numeric string reads as its code", group_for("vessel", "52"), "service")

print("=== not vessels ===")
check("fishing-gear buoy", group_for("net_buoy", 0), "fishing_gear")
check("aid to navigation", group_for("aton", None), "aton")
check("base station", group_for("base_station", None), "base_station")
check("SAR aircraft", group_for("sar_aircraft", None), "sar_aircraft")
check("a distress beacon has NO group: it cannot be hidden by class", group_for("distress_beacon", 0), None)
check("an unknown kind has none", group_for("spaceship", 70), None)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
