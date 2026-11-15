"""Vessel statics kept across restarts (SSOT item 262): sources/statics.py and
the aisstream adapter's use of it.

Loads the `sources` package by FILE PATH, so it runs anywhere with no Home
Assistant installed (SSOT item 22). Run: python test_statics.py
"""
import importlib
import json
import os
import sqlite3
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMP = os.path.join(HERE, "custom_components", "live_track_ships")
pkg = types.ModuleType("lts_src")
pkg.__path__ = [os.path.join(COMP, "sources")]
sys.modules["lts_src"] = pkg
st = importlib.import_module("lts_src.statics")
ais = importlib.import_module("lts_src.aisstream")

passed = failed = 0


def check(label, got, want):
    global passed, failed
    if got == want:
        passed += 1
    else:
        failed += 1
        print("FAIL %s: got %r want %r" % (label, got, want))


class Clock:
    def __init__(self, t=1_790_000_000):
        self.t = t

    def __call__(self):
        return self.t


def msg5(mmsi, name, typ, cs="WDA1234", imo=9876543, a=20, b=10, c=4, d=4,
         dest="CHICAGO", draught=3.2):
    return {"MessageType": "ShipStaticData",
            "MetaData": {"MMSI": int(mmsi), "ShipName": name},
            "Message": {"ShipStaticData": {
                "Name": name, "Type": typ, "CallSign": cs, "ImoNumber": imo,
                "Destination": dest, "MaximumStaticDraught": draught,
                "Dimension": {"A": a, "B": b, "C": c, "D": d}}}}


def msg24b(mmsi, typ, valid=True, cs="", a=6, b=4):
    return {"MessageType": "StaticDataReport",
            "MetaData": {"MMSI": int(mmsi), "ShipName": ""},
            "Message": {"StaticDataReport": {
                "PartNumber": True,
                "ReportA": {"Valid": False, "Name": ""},
                "ReportB": {"Valid": valid, "ShipType": typ, "CallSign": cs,
                            "Dimension": {"A": a, "B": b, "C": 1, "D": 2}}}}}


def msg24a(mmsi, name):
    return {"MessageType": "StaticDataReport",
            "MetaData": {"MMSI": int(mmsi), "ShipName": name},
            "Message": {"StaticDataReport": {
                "PartNumber": False,
                "ReportA": {"Valid": True, "Name": name},
                "ReportB": {"Valid": False}}}}


def pos(mmsi, name, cls="A"):
    mt = "PositionReport" if cls == "A" else "StandardClassBPositionReport"
    return {"MessageType": mt,
            "MetaData": {"MMSI": int(mmsi), "ShipName": name,
                         "latitude": 41.9, "longitude": -87.6,
                         "time_utc": "2026-09-26 16:00:00.123456789 +0000 UTC"},
            "Message": {mt: {"Sog": 5.0, "Cog": 90.0, "TrueHeading": 511}}}


def source(cache):
    return ais.AisStreamSource(None, "k", [], statics=cache)


tmp = tempfile.mkdtemp()
path = os.path.join(tmp, st.FILE_NAME)

# -- 1. the join within one run, unchanged -----------------------------------
c1 = st.StaticCache()
s1 = source(c1)
check("static returns no observation", s1._to_observation(msg5("367000001", "ODYSSEY CHICAGO_IVER", 60)), None)
o = s1._to_observation(pos("367000001", "ODYSSEY CHICAGO_IVER"))
check("run: type", o.ship_type, 60)
check("run: length", o.length_m, 30.0)
check("run: beam", o.beam_m, 8.0)
check("run: call sign", o.call_sign, "WDA1234")
check("run: imo", o.imo, 9876543)
check("run: destination (voyage, in memory)", o.destination, "CHICAGO")
check("run: draught (voyage, in memory)", o.draught_m, 3.2)
check("run: name from the position", o.name, "ODYSSEY CHICAGO_IVER")

# -- 2. a restart: written, read back, joined with no static message -------
rows = c1.take_dirty()
check("one row to write", len(rows), 1)
st.save(path, rows, [])
c2 = st.StaticCache()
check("rows read back", c2.load_rows(st.load(path)), 1)
s2 = source(c2)
o = s2._to_observation(pos("367000001", "ODYSSEY CHICAGO_IVER"))
check("restart: type", o.ship_type, 60)
check("restart: length", o.length_m, 30.0)
check("restart: call sign", o.call_sign, "WDA1234")
check("restart: imo", o.imo, 9876543)
check("restart: destination NOT persisted", o.destination, None)
check("restart: draught NOT persisted", o.draught_m, None)

# -- 3. the reassignment guard ----------------------------------------------
o = s2._to_observation(pos("367000001", "SOMEONE ELSE"))
check("guard: other name refused", o.ship_type, None)
check("guard: other name, no size either", o.length_m, None)
o = s2._to_observation(pos("367000001", "  odyssey chicago-iver "))
check("guard: spacing/case/punctuation are not a difference", o.ship_type, 60)
o = s2._to_observation(pos("367000001", ""))
check("guard: no name now, record used", o.ship_type, 60)
s2._to_observation(msg5("367000001", "SOMEONE ELSE", 52))
o = s2._to_observation(pos("367000001", "SOMEONE ELSE"))
check("guard lifted by a fresh static", o.ship_type, 52)
o = s2._to_observation(pos("367000001", "ODYSSEY CHICAGO_IVER"))
check("fresh record used whatever the name", o.ship_type, 52)

# -- 4. Class B: Part B type, Part A name, across a restart ----------------
path_b = os.path.join(tmp, "b.sqlite")
cb = st.StaticCache()
sb = source(cb)
sb._to_observation(msg24b("338123456", 37))
sb._to_observation(msg24a("338123456", "SEADOG IV"))
o = sb._to_observation(pos("338123456", "SEADOG IV", "B"))
check("B: type from Part B", o.ship_type, 37)
check("B: length from Part B", o.length_m, 10.0)
st.save(path_b, cb.take_dirty(), [])
cb2 = st.StaticCache()
cb2.load_rows(st.load(path_b))
sb2 = source(cb2)
check("B: restart type", sb2._to_observation(pos("338123456", "SEADOG IV", "B")).ship_type, 37)
check("B: restart, Part A name kept for the guard",
      sb2._to_observation(pos("338123456", "SEA DOG", "B")).ship_type, None)
n0 = len(cb2)
sb2._to_observation(msg24b("338999999", 37, valid=False))
check("B: invalid Part B creates nothing", len(cb2), n0)
sb2._to_observation(msg24a("338999998", "NAME ONLY"))
check("B: Part A alone creates nothing", len(cb2), n0)

# -- 5. past the old 5,000: nothing is wiped --------------------------------
cw = st.StaticCache()
sw = source(cw)
for i in range(5002):
    sw._to_observation(msg5(str(211000000 + i), f"V{i}", 70))
check("5,002 vessels held", len(cw), 5002)
check("the first still typed", sw._to_observation(pos("211000000", "V0")).ship_type, 70)
check("the last typed", sw._to_observation(pos("211005001", "V5001")).ship_type, 70)

# -- 6. eviction by last heard ----------------------------------------------
clk = Clock()
ce = st.StaticCache(retention_s=100, max_entries=10, clock=clk)
ce.update("100000001", {"type": 30})
clk.t += 50
ce.update("100000002", {"type": 31})
clk.t += 60
check("retention: the one not heard for 110 s goes", ce.evict(), ["100000001"])
check("retention: the other stays", "100000002" in ce, True)

clk = Clock()
cm = st.StaticCache(retention_s=10_000, max_entries=3, clock=clk)
for i in range(5):
    cm.update(f"20000000{i}", {"type": 70})
    clk.t += 1
cm.update("200000000", {"type": 70})          # heard again: now the newest
gone = sorted(cm.evict())
check("ceiling: least recently heard go first", gone, ["200000001", "200000002"])
check("ceiling: re-heard one kept", "200000000" in cm, True)
check("ceiling: size", len(cm), 3)

# -- 7. what reaches the disk ------------------------------------------------
path_d = os.path.join(tmp, "d.sqlite")
clk = Clock(1000)
cd = st.StaticCache(clock=clk)
cd.update("300000001", {"type": 60, "destination": "X"})
cd.update("300000002", {"destination": "VOYAGE ONLY", "draught_m": 5.0})
rows = cd.take_dirty()
check("voyage-only record not written", [r[0] for r in rows], ["300000001"])
check("take_dirty empties the queue", cd.take_dirty(), [])
st.save(path_d, rows, [])
clk.t = 2000
cd.update("300000001", {"type": 61})
st.save(path_d, cd.take_dirty(), [])
con = sqlite3.connect(path_d)
r = con.execute("SELECT type, first_seen, last_seen FROM vessel_static WHERE mmsi='300000001'").fetchone()
check("upsert: new type, first_seen kept, last_seen advanced", r, (61, 1000, 2000))
check("meta schema_version", con.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone(), ("1",))
con.close()
cx = st.StaticCache(clock=Clock(5000))      # a later run that did not read back
cx.update("300000001", {"type": 62})
st.save(path_d, cx.take_dirty(), [])
con = sqlite3.connect(path_d)
r = con.execute("SELECT type, first_seen, last_seen FROM vessel_static WHERE mmsi='300000001'").fetchone()
con.close()
check("upsert: the older first_seen on disk survives", r, (62, 1000, 5000))
st.save(path_d, [], ["300000001"])
check("an eviction deletes the row", st.load(path_d), [])
cd.update("300000003", {"type": 30})
rows = cd.take_dirty()
cd.mark_dirty(r[0] for r in rows)
check("mark_dirty puts a failed write back", [r[0] for r in cd.take_dirty()], ["300000003"])

# -- 8. read-back never overwrites what was heard this run ------------------
cl = st.StaticCache()
cl.update("367000001", {"type": 99})
cl.load_rows(st.load(path))
check("load_rows keeps the fresh record", cl.lookup("367000001").type, 99)

# -- 9. an unreadable file is moved aside, not fatal ------------------------
path_bad = os.path.join(tmp, "bad.sqlite")
with open(path_bad, "wb") as f:
    f.write(b"this is not a database" * 50)
check("unreadable: starts empty", st.load(path_bad), [])
aside = [n for n in os.listdir(tmp) if n.startswith("bad.sqlite.unreadable-")]
check("unreadable: moved aside", len(aside), 1)
check("unreadable: a fresh file works", st.load(path_bad), [])

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
