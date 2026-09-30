"""The held angle of vessels with no heading, kept across restarts. SSOT item 270.

WHY. Below 2 kn a vessel's course over ground is noise, so a vessel with no
heading is drawn at an angle HELD from how it last moved (icons.resolve). Until
2026-09-29 that angle lived only for the Home Assistant run: after a restart a
moored boat had nothing to go on until it moved again. Lee, 2026-09-29: keep
the saved angles, and keep them extremely small.

WHAT IS KEPT IN MEMORY. Every held angle for the run, per vessel, with whether
it is STRONG (from a course at 2 kn or more, or from a move of 30 m or more)
or WEAK (seeded from a slow course, replaced by each newer non-zero one).
Insertion-ordered; the oldest go past MAX_MEMORY.

WHAT IS WRITTEN. One row per vessel: MMSI, the angle in 5-degree steps and the
UTC day it was last held. Only STRONG angles - a weak one is the vessel's own
slow course and comes back with its next report - held in the last 24 h (to
the day), at most MAX_SAVED rows (the instance ceiling), the most recently
held first. Written by the prune pass as a diff: rows that changed are
upserted, rows no longer wanted are deleted.

STORAGE. SQLite at .storage/saw_vessel_held.sqlite - the shared-file naming
rule: saw_*, never named after an integration. MMSI is the INTEGER PRIMARY KEY
(the rowid, so no separate index); 1 KB pages and auto_vacuum FULL, so the
file shrinks with its rows. The schema version is PRAGMA user_version: a meta
table would cost two more pages than the data.
⚠ NO HOME ASSISTANT IMPORT HERE, so the tests run anywhere.
"""

from __future__ import annotations

import logging
import os
import sqlite3
import time

_LOGGER = logging.getLogger(__name__)

FILE_NAME = "saw_vessel_held.sqlite"
SCHEMA_VERSION = 1
STEP = 5                  # degrees per stored step; icons.ROTATION_STEP
KEEP_S = 24 * 3600        # a row is kept while held in the last 24 h
MAX_SAVED = 2500          # the instance ceiling, INSTANCE_MAX_VESSELS
MAX_MEMORY = 50_000
_DAY = 86400


def mmsi_key(identity) -> int | None:
    """The stored key: a 9-digit MMSI not starting 0 (a vessel's), else
    None and the angle is kept for the run only."""
    s = str(identity or "")
    if len(s) == 9 and s.isdigit() and s[0] != "0":
        return int(s)
    return None


class HeldAngles:
    """identity -> [degrees, strong, last held (epoch s)]."""

    def __init__(self, clock=time.time, keep_s: float = KEEP_S,
                 max_saved: int = MAX_SAVED, max_memory: int = MAX_MEMORY):
        self._d: dict[str, list] = {}
        self._disk: dict[int, tuple[int, int]] = {}   # what the file holds
        self._clock = clock
        self._keep = keep_s
        self._max_saved = max_saved
        self._max_memory = max_memory

    def __len__(self) -> int:
        return len(self._d)

    def clear(self) -> None:
        self._d.clear()
        self._disk.clear()

    def get(self, identity) -> tuple[float, bool] | None:
        v = self._d.get(identity)
        return None if v is None else (v[0], v[1])

    def put(self, identity, deg: float, strong: bool) -> None:
        """Hold `deg` for this vessel now; the newest goes last."""
        self._d.pop(identity, None)
        self._d[identity] = [float(deg) % 360, bool(strong), self._clock()]
        while len(self._d) > self._max_memory:
            self._d.pop(next(iter(self._d)))

    def touch(self, identity) -> None:
        """The held angle was drawn again: it is still being held."""
        v = self._d.get(identity)
        if v is not None:
            self.put(identity, v[0], v[1])

    # -- to and from disk ----------------------------------------------------
    def load_rows(self, rows) -> int:
        """Rows (mmsi, step, day) as read by load(). Every row is noted as on
        disk; only those held in the last 24 h (to the day) and not already
        held since this start are taken, as STRONG. Returns how many."""
        now = self._clock()
        taken = 0
        for mmsi, step, day in rows:
            self._disk[int(mmsi)] = (int(step), int(day))
            identity = str(mmsi)
            if identity in self._d:
                continue
            at = min(now, (int(day) + 1) * _DAY - 1)   # the end of its day
            if now - at > self._keep:
                continue
            self._d[identity] = [(int(step) % (360 // STEP)) * STEP, True, at]
            taken += 1
        # Loaded rows are older than anything held since the start.
        self._d = dict(sorted(self._d.items(), key=lambda kv: kv[1][2]))
        return taken

    def wanted(self) -> dict[int, tuple[int, int]]:
        """mmsi -> (step, day) for every row the file should hold."""
        now = self._clock()
        rows = []
        for identity, (deg, strong, at) in self._d.items():
            key = mmsi_key(identity)
            if strong and key is not None and now - at <= self._keep:
                rows.append((at, key, int(round(deg / STEP)) % (360 // STEP),
                             int(at // _DAY)))
        rows.sort(reverse=True)
        return {key: (step, day) for _at, key, step, day in rows[:self._max_saved]}

    def changes(self) -> tuple[list[tuple[int, int, int]], list[int]]:
        """(rows to upsert, MMSIs to delete) against what the file holds."""
        want = self.wanted()
        # ⚠ In MMSI order: SQLite fills a page it appends to, and splits one
        # it inserts into half-empty. Measured on 2,500 rows written newest
        # first (MMSIs falling): 75,776 b unsorted.
        upserts = sorted((k, s, d) for k, (s, d) in want.items()
                         if self._disk.get(k) != (s, d))
        deletes = sorted(k for k in self._disk if k not in want)
        return upserts, deletes

    def committed(self, upserts, deletes) -> None:
        """The write succeeded: the file now holds this."""
        for k, s, d in upserts:
            self._disk[k] = (s, d)
        for k in deletes:
            self._disk.pop(k, None)


# ---------------------------------------------------------------------------
# SQLite. Blocking: Home Assistant calls these in its executor.
def _connect(path: str) -> sqlite3.Connection:
    con = sqlite3.connect(path, timeout=30)
    try:
        # ⚠ page_size and auto_vacuum take effect only before the first
        # table exists; on an existing file they are no-ops.
        con.execute("PRAGMA page_size = 1024")
        con.execute("PRAGMA auto_vacuum = FULL")
        con.execute("CREATE TABLE IF NOT EXISTS held ("
                    "mmsi INTEGER PRIMARY KEY, "
                    "step INTEGER NOT NULL, "
                    "day INTEGER NOT NULL)")
        con.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        con.commit()
    except BaseException:
        con.close()          # release the file, so an unreadable one can move
        raise
    return con


def load(path: str) -> list[tuple]:
    """Every row, as (mmsi, step, day).

    ⚠ A file that cannot be read is MOVED ASIDE, not deleted and not fatal:
    a held angle is a convenience, positions are the product."""
    try:
        con = _connect(path)
        try:
            return con.execute("SELECT mmsi, step, day FROM held").fetchall()
        finally:
            con.close()
    except sqlite3.DatabaseError as exc:
        aside = f"{path}.unreadable-{int(time.time())}"
        try:
            os.replace(path, aside)
        except OSError:
            aside = None
        _LOGGER.warning("Held angles unreadable (%s); moved to %s and "
                        "starting empty", exc, aside)
        return []


def save(path: str, upserts: list[tuple], deletes: list[int]) -> None:
    """Upsert `upserts` and delete `deletes`, in one transaction."""
    con = _connect(path)
    try:
        with con:
            if upserts:
                con.executemany(
                    "INSERT INTO held (mmsi, step, day) VALUES (?, ?, ?) "
                    "ON CONFLICT(mmsi) DO UPDATE SET step = excluded.step, "
                    "day = excluded.day", upserts)
            if deletes:
                con.executemany("DELETE FROM held WHERE mmsi = ?",
                                [(k,) for k in deletes])
    finally:
        con.close()


# ONE per Home Assistant: a vessel's held angle is a fact about the vessel,
# not about a circle. geo_location reads and writes it; __init__ loads it and
# the prune pass writes it.
HELD = HeldAngles()
