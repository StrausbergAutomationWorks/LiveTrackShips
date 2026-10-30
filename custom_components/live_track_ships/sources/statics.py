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
import sqlite3
import time

_LOGGER = logging.getLogger(__name__)

FILE_NAME = "saw_vessel_statics.sqlite"
SCHEMA_VERSION = "1"

# ⚠ MOVED TO saw-livetrack 0.2.19 (backlog 315, 2026-10-30), VERBATIM from
# this file at ccebaee: the in-memory join table (PERSISTED, HULL, VOYAGE, the
# retention and ceiling, name_key, StaticRecord, StaticCache). The instance's
# one cache is the shared aisstream client's `statics`; Ships keeps what is
# below, the SQLite file it is loaded from and saved to. Do not define any of
# the imported names again here.
from saw_livetrack.ais import (  # noqa: F401
    HULL,
    MAX_ENTRIES,
    PERSISTED,
    RETENTION_DAYS,
    VOYAGE,
    StaticCache,
    StaticRecord,
    _NAME_KEY,
    name_key,
)


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
