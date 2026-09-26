"""Vessel statics learned from the air, kept across restarts. SSOT item 262.

WHY. aisstream sends a vessel's type, call sign, IMO and size only in its
static messages - Msg 5 for Class A about every 6 minutes, Msg 24 Part B for
Class B, which most Class B units rarely send with a payload (SSOT section 6).
The adapter joins them onto positions by MMSI. Until 2026-09-26 that join was
a dict LOST ON EVERY RESTART and CLEARED WHOLESALE past 5,000 MMSIs, so a
Class B type that took days to arrive was gone at the next restart, and on
busy water every learned type vanished whenever the dict filled.

WHAT IS KEPT. Only what describes the HULL: type, call sign, IMO, length and
beam, with the name that came with them. Destination and draught are VOYAGE
data: they stay in memory and are never written. A destination read back
after a restart could be a finished voyage, a confident wrong answer (D0),
and Class A resends both within minutes.

ONE CACHE PER HOME ASSISTANT, shared by every aisstream entry and keyed by
MMSI: a vessel's type is a fact about the vessel, not about a circle.

⚠ MMSIs ARE REASSIGNED. A record read back from disk is used only while
nothing contradicts it: if its name and the name the vessel broadcasts now
both exist and differ, it is ignored until the vessel sends its own static
again. A record heard since this start is always used, as before.

⚠ EVICTION IS BY LAST HEARD, NEVER WHOLESALE. Records not refreshed for
RETENTION_DAYS go; past MAX_ENTRIES the least recently heard go first.

STORAGE. SQLite at .storage/saw_vessel_statics.sqlite - the shared-file
naming rule: saw_*, never named after an integration. A flush upserts the
changed rows in one transaction; nothing rewrites the whole table.
⚠ NO HOME ASSISTANT IMPORT HERE, so the tests run anywhere.
"""

from __future__ import annotations

import logging
import os
import re
import sqlite3
import time

_LOGGER = logging.getLogger(__name__)

FILE_NAME = "saw_vessel_statics.sqlite"
SCHEMA_VERSION = "1"

# Written to disk, in column order. `name` is kept for the reassignment guard.
PERSISTED = ("name", "type", "call_sign", "imo", "length_m", "beam_m")
HULL = PERSISTED[1:]
VOYAGE = ("destination", "draught_m")

RETENTION_DAYS = 90
MAX_ENTRIES = 50_000

_NAME_KEY = re.compile(r"[^A-Z0-9]")


def name_key(name) -> str | None:
    """A name compared on letters and digits only, so padding, spacing and
    punctuation are not a difference. Both names come from the same
    transponder, mangling included, so nothing is repaired (SSOT section 6)."""
    if not name:
        return None
    key = _NAME_KEY.sub("", str(name).upper())
    return key or None


class StaticRecord:
    """One vessel's statics. Slots, because a busy entry holds tens of
    thousands of these."""

    __slots__ = PERSISTED + VOYAGE + ("first_seen", "last_seen")

    def __init__(self, first_seen: int, last_seen: int):
        for k in PERSISTED + VOYAGE:
            setattr(self, k, None)
        self.first_seen = first_seen
        self.last_seen = last_seen

    def has_hull(self) -> bool:
        return any(getattr(self, k) is not None for k in HULL)


class StaticCache:
    """The MMSI join table: in memory, loaded from and flushed to SQLite."""

    def __init__(self, retention_s: float = RETENTION_DAYS * 86400,
                 max_entries: int = MAX_ENTRIES, clock=time.time):
        self._d: dict[str, StaticRecord] = {}
        self._fresh: set[str] = set()      # heard since this start
        self._dirty: set[str] = set()      # to write at the next flush
        self._retention = retention_s
        self._max = max_entries
        self._clock = clock

    def __len__(self) -> int:
        return len(self._d)

    def __contains__(self, mmsi) -> bool:
        return mmsi in self._d

    # -- from the air ------------------------------------------------------
    def update(self, mmsi: str, fields: dict) -> StaticRecord:
        """Record what one static message carried. Fields it did not carry
        keep their values; a field it carried as None is cleared, exactly as
        the vessel declared it."""
        now = int(self._clock())
        rec = self._d.get(mmsi)
        if rec is None:
            rec = self._d[mmsi] = StaticRecord(now, now)
        for k, v in fields.items():
            if k in PERSISTED or k in VOYAGE:
                setattr(rec, k, v)
        rec.last_seen = now
        self._fresh.add(mmsi)
        self._dirty.add(mmsi)
        return rec

    def set_name(self, mmsi: str, name) -> None:
        """A Class B Part A carries only the name. It never creates a record
        (a name alone is not worth a row), but it gives an existing one the
        name the reassignment guard compares."""
        rec = self._d.get(mmsi)
        if rec is not None and name:
            rec.name = name
            self._dirty.add(mmsi)

    def lookup(self, mmsi: str, current_name=None) -> StaticRecord | None:
        """The record to join onto a position, or None.

        ⚠ A record read back from disk and not yet re-heard is refused when
        its name and the name broadcast now both exist and differ."""
        rec = self._d.get(mmsi)
        if rec is None:
            return None
        if mmsi not in self._fresh:
            old, new = name_key(rec.name), name_key(current_name)
            if old and new and old != new:
                return None
        return rec

    # -- eviction ----------------------------------------------------------
    def evict(self) -> list[str]:
        """Drop records not heard for the retention window, then the least
        recently heard past the ceiling. Returns the MMSIs dropped."""
        cutoff = self._clock() - self._retention
        dead = [m for m, r in self._d.items() if r.last_seen < cutoff]
        over = len(self._d) - len(dead) - self._max
        if over > 0:
            gone = set(dead)
            alive = sorted((r.last_seen, m) for m, r in self._d.items()
                           if m not in gone)
            dead.extend(m for _ls, m in alive[:over])
        for m in dead:
            del self._d[m]
            self._fresh.discard(m)
            self._dirty.discard(m)
        return dead

    # -- to and from disk ----------------------------------------------------
    def load_rows(self, rows) -> int:
        """Rows as returned by load(). Never overwrites a record already heard
        since this start. Returns how many were taken."""
        taken = 0
        for row in rows:
            mmsi = row[0]
            if mmsi in self._d:
                continue
            *values, first_seen, last_seen = row[1:]
            rec = StaticRecord(int(first_seen), int(last_seen))
            for k, v in zip(PERSISTED, values):
                setattr(rec, k, v)
            self._d[mmsi] = rec
            taken += 1
        return taken

    def take_dirty(self) -> list[tuple]:
        """Rows to upsert, and forget them. Only records with a hull field
        are written."""
        rows = []
        for m in self._dirty:
            rec = self._d.get(m)
            if rec is not None and rec.has_hull():
                rows.append((m, *(getattr(rec, k) for k in PERSISTED),
                             rec.first_seen, rec.last_seen))
        self._dirty.clear()
        return rows

    def mark_dirty(self, mmsis) -> None:
        """Put rows back after a failed write."""
        self._dirty.update(m for m in mmsis if m in self._d)


# ---------------------------------------------------------------------------
# SQLite. Blocking: Home Assistant calls these in its executor.
_CREATE = """
CREATE TABLE IF NOT EXISTS vessel_static (
    mmsi       TEXT PRIMARY KEY,
    name       TEXT,
    type       INTEGER,
    call_sign  TEXT,
    imo        INTEGER,
    length_m   REAL,
    beam_m     REAL,
    first_seen INTEGER NOT NULL,
    last_seen  INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
"""
_META = {
    "schema_version": SCHEMA_VERSION,
    "content": "AIS static data as broadcast by the vessels themselves, "
               "learned from the air. Hull fields only; no voyage data.",
    "written_by": "Live Track Ships (StrausbergAutomationWorks)",
}
_UPSERT = f"""
INSERT INTO vessel_static (mmsi, {", ".join(PERSISTED)}, first_seen, last_seen)
VALUES ({", ".join("?" * (len(PERSISTED) + 3))})
ON CONFLICT(mmsi) DO UPDATE SET
    {", ".join(f"{k} = excluded.{k}" for k in PERSISTED)},
    first_seen = MIN(vessel_static.first_seen, excluded.first_seen),
    last_seen = MAX(vessel_static.last_seen, excluded.last_seen)
"""


def _connect(path: str) -> sqlite3.Connection:
    con = sqlite3.connect(path, timeout=30)
    try:
        con.executescript(_CREATE)
        con.executemany("INSERT OR IGNORE INTO meta (key, value) VALUES (?, ?)",
                        list(_META.items()))
        con.commit()
    except BaseException:
        con.close()          # release the file, so an unreadable one can move
        raise
    return con


def load(path: str) -> list[tuple]:
    """Every row, as (mmsi, *PERSISTED, first_seen, last_seen).

    ⚠ A file that cannot be read is MOVED ASIDE, not deleted and not fatal:
    the statics are a convenience, positions are the product."""
    try:
        con = _connect(path)
        try:
            return con.execute(
                f"SELECT mmsi, {', '.join(PERSISTED)}, first_seen, last_seen "
                "FROM vessel_static").fetchall()
        finally:
            con.close()
    except sqlite3.DatabaseError as exc:
        aside = f"{path}.unreadable-{int(time.time())}"
        try:
            os.replace(path, aside)
        except OSError:
            aside = None
        _LOGGER.warning("Vessel statics unreadable (%s); moved to %s and "
                        "starting empty", exc, aside)
        return []


def save(path: str, rows: list[tuple], deleted: list[str]) -> None:
    """Upsert `rows` and delete `deleted`, in one transaction."""
    con = _connect(path)
    try:
        with con:
            if rows:
                con.executemany(_UPSERT, rows)
            if deleted:
                con.executemany("DELETE FROM vessel_static WHERE mmsi = ?",
                                [(m,) for m in deleted])
    finally:
        con.close()
