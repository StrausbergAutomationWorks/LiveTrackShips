"""The saved held angle (SSOT item 270, Lee 2026-09-29): held.py.

Loads held.py by FILE PATH, so it runs anywhere with no Home Assistant
installed (SSOT item 22). Run: python test_held.py
"""
import importlib.util
import os
import pathlib
import sqlite3
import sys
import tempfile

_PKG = pathlib.Path(__file__).parent / "custom_components" / "live_track_ships"
spec = importlib.util.spec_from_file_location("lts_held", _PKG / "held.py")
held = importlib.util.module_from_spec(spec)
sys.modules["lts_held"] = held
spec.loader.exec_module(held)

passed = failed = 0


def check(label, got, want):
    global passed, failed
    if got == want:
        passed += 1
    else:
        failed += 1
        print("FAIL %s: got %r want %r" % (label, got, want))


class Clock:
    def __init__(self, t=1_790_000_000.0):
        self.t = t

    def __call__(self):
        return self.t


DAY = 86400
clk = Clock()
h = held.HeldAngles(clock=clk, max_saved=3, max_memory=6)

# --- memory ---
h.put("367000001", 123.4, True)
check("get", h.get("367000001"), (123.4, True))
check("absent", h.get("nope"), None)
h.put("367000002", 40.0, False)
check("weak kept in memory", h.get("367000002"), (40.0, False))
for i in range(3, 9):
    h.put("36700000%d" % i, 10.0 * i, True)
check("memory capped", len(h), 6)
check("the oldest went first", h.get("367000001"), None)

# --- what is written: strong only, 9-digit vessel MMSIs, capped, newest first ---
h = held.HeldAngles(clock=clk, max_saved=3)
h.put("367000001", 90.0, True); clk.t += 1
h.put("367000002", 40.0, False); clk.t += 1          # weak: never written
h.put("002570000", 10.0, True); clk.t += 1           # base station form
h.put("12345", 10.0, True); clk.t += 1               # not an MMSI
h.put("367000003", 181.0, True); clk.t += 1
h.put("367000004", 357.6, True); clk.t += 1
h.put("367000005", 12.0, True); clk.t += 1
w = h.wanted()
check("only strong 9-digit MMSIs, capped at max_saved, newest",
      sorted(w), [367000003, 367000004, 367000005])
check("angle in 5-degree steps", w[367000003][0], 36)
check("357.6 wraps to step 0", w[367000004][0], 0)
check("day is the UTC day", w[367000005][1], int(clk.t // DAY))
check("mmsi_key rejects a leading zero", held.mmsi_key("002570000"), None)
check("mmsi_key takes an int", held.mmsi_key(367000001), 367000001)

# --- the diff ---
up, de = h.changes()
check("first diff: all three upserted", sorted(r[0] for r in up), [367000003, 367000004, 367000005])
check("first diff: nothing to delete", de, [])
h.committed(up, de)
check("nothing changed: no writes", h.changes(), ([], []))
h.touch("367000003")
check("touched on the same day: still no write", h.changes(), ([], []))
h.put("367000001", 95.0, True)         # newest now: pushes the oldest saved out
up, de = h.changes()
check("a newer hold displaces the oldest past the cap",
      (sorted(r[0] for r in up), de), ([367000001], [367000004]))
h.committed(up, de)

# --- 24 h ---
clk.t += DAY + 10
up, de = h.changes()
check("past 24 h every row is deleted", (up, sorted(de)), ([], [367000001, 367000003, 367000005]))
check("memory keeps them for the run", h.get("367000001"), (95.0, True))

# --- SQLite round trip, size, and the restart ---
d = tempfile.mkdtemp()
path = os.path.join(d, held.FILE_NAME)
clk.t = 1_790_000_000.0
h = held.HeldAngles(clock=clk)
for i in range(2500):
    h.put(str(367000000 + i), (i * 7) % 360, True)
up, de = h.changes()
held.save(path, up, de)
h.committed(up, de)
size = os.path.getsize(path)
print("2,500 rows: %d bytes" % size)
# Measured 2026-09-29: 41,984 b written in MMSI order, 75,776 b newest-first.
check("2,500 rows stay under 48 KB (written in MMSI order)", size < 48_000, True)
con = sqlite3.connect(path)
check("page size 1 KB", con.execute("PRAGMA page_size").fetchone()[0], 1024)
check("auto_vacuum FULL", con.execute("PRAGMA auto_vacuum").fetchone()[0], 1)
check("schema version", con.execute("PRAGMA user_version").fetchone()[0], held.SCHEMA_VERSION)
check("three columns only",
      [r[1] for r in con.execute("PRAGMA table_info(held)")], ["mmsi", "step", "day"])
check("no other table", [r[0] for r in con.execute(
    "SELECT name FROM sqlite_master WHERE type='table'")], ["held"])
con.close()

# a restart the next morning: yesterday's rows are read back as strong
rows = held.load(path)
check("all rows read", len(rows), 2500)
clk.t += 12 * 3600
r = held.HeldAngles(clock=clk)
r.put("367000007", 200.0, False)       # heard since this start: not overwritten
taken = r.load_rows(rows)
check("taken", taken, 2499)
check("read back as STRONG, quantised", r.get("367000001"), (5.0, True))
check("a hold since this start wins", r.get("367000007"), (200.0, False))
check("read back: nothing to write", r.changes()[0], [])

# a restart two days later: nothing is taken, and the file is emptied
clk.t += 2 * DAY
r = held.HeldAngles(clock=clk)
check("two days later nothing is taken", r.load_rows(rows), 0)
up, de = r.changes()
check("two days later every row is deleted", (up, len(de)), ([], 2500))
held.save(path, up, de)
r.committed(up, de)
check("the file is emptied", held.load(path), [])
check("the file shrinks (auto_vacuum)", os.path.getsize(path) < 8_000, True)

# an unreadable file is moved aside, not fatal
bad = os.path.join(d, "bad_" + held.FILE_NAME)
with open(bad, "wb") as fh:
    fh.write(b"this is not a database" * 100)
check("unreadable -> empty", held.load(bad), [])
check("unreadable -> moved aside", os.path.exists(bad), False)

print("%d passed, %d failed" % (passed, failed))
sys.exit(1 if failed else 0)
