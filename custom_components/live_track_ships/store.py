"""Coordinator: owns the source, the per-vessel tracks, and the cap.

⚠ THIS IS NOT A DataUpdateCoordinator. That class is built around "call this
function every N seconds", and the primary source is a WEBSOCKET PUSH. The
right shape is a long-lived background task owning the connection and calling
async_set_updated_data when state changes. See
10_SEED/05_SHARED_LESSONS.md section D and the Live Track Ships SSOT section 3.

⚠ NO FilterMessageTypes IS SENT to any source. Filtering would BLOCK a message
type the day a source started publishing it, and unblocking would need a code
change, a release and a user upgrade. Handle anything; assume nothing.
"""

from __future__ import annotations

import asyncio
import datetime as _dt
import logging

from .geo import distance_km, nearest, within_radius
from .playback import Track
from .sources.base import Observation

_LOGGER = logging.getLogger(__name__)

# ⚠⚠ TWO RETENTION WINDOWS, CHOSEN BY WHAT THE VESSEL DECLARES.
#
# Measured 2026-09-08 across every capture - stationary vessels report LESS
# often, so a single window quietly deletes the ones that are demonstrably
# still there:
#
#     group                      p50    p90    p95    max
#     moving   (>2 kn)            63    190    249    602
#     stationary (<2 kn)         120    357    365   1080
#     DECLARED anchored/moored   180    360    539    714
#
# The declared group sits at a 180 s median - exactly the 3-minute interval
# ITU-R M.1371 specifies for Class A at anchor and Class B under 2 kn. So a
# 1800 s window leaves a moored tug barely two missed relays from eviction,
# and it would be deleted and re-created all night.
#
# ⚠ NavigationalStatus is POPULATED on real traffic: 66% under way, 15% MOORED,
# 2.3% AT ANCHOR - 17% of messages carry an explicit declaration that the
# vessel is not going anywhere. That is far stronger than inferring from speed,
# which may be stale or merely drifting.
#
# ⚠ THE GHOST RISK IS SMALL AND SELF-CORRECTING. A moored vessel that departs
# starts transmitting every 2-10 s and reappears at a new position, updating
# the same entity. It only ghosts if it leaves the radius entirely without
# being heard once. Weigh that against deleting a vessel still tied to a dock -
# "absence of a message is not absence of the thing", B1.
DEFAULT_STALE_AFTER_S = 1800            # moving, or status unknown
DEFAULT_BERTHED_STALE_AFTER_S = 21600   # 6 h, for a vessel that DECLARED it

# ITU-R M.1371 navigational status. ⚠ 15 is the UNDEFINED SENTINEL and is
# already mapped to None upstream - it must NEVER be read as "not moored".
NAV_AT_ANCHOR = 1
NAV_MOORED = 5
BERTHED_STATUSES = frozenset({NAV_AT_ANCHOR, NAV_MOORED})

# ⚠ Below this a vessel is not really moving. 2 kn is the Class B reporting-rate
# boundary in ITU-R M.1371 - below it a unit reports every 3 minutes, which is
# the protocol itself saying the object is stationary.
STATIONARY_KMH = 2 * 1.852

# ⚠ The union of distinct vessels does NOT converge - measured 30-37 new per
# day over five days, still climbing at 291. So the cache is bounded by a
# RETENTION WINDOW, never by "vessels ever seen". Live Track Ships SSOT §13.
DEFAULT_PRUNE_INTERVAL_S = 300


class VesselStore:
    """Tracks per MMSI, pruned by a retention window."""

    def __init__(self, centre_lat, centre_lon, radius_km,
                 max_vessels, stale_after_s=DEFAULT_STALE_AFTER_S,
                 berthed_stale_after_s=DEFAULT_BERTHED_STALE_AFTER_S):
        self._lat = centre_lat
        self._lon = centre_lon
        self._radius = radius_km
        self._max = max_vessels
        self._stale_after = stale_after_s
        self._berthed_stale_after = berthed_stale_after_s
        self._tracks: dict[str, Track] = {}
        self.truncated_from: int | None = None

    @staticmethod
    def is_berthed(obs) -> bool:
        """⚠ Prefers what the vessel DECLARES over what we infer.

        A vessel reporting status 1 or 5 is stating it is anchored or tied up.
        Speed is the fallback only - it may be stale, and a drifting vessel
        also reads near zero.
        """
        if obs.nav_status in BERTHED_STATUSES:
            return True
        if obs.nav_status is not None:
            return False          # it declared something else; believe it
        return (obs.speed_kmh is not None
                and obs.speed_kmh < STATIONARY_KMH)

    def _window_for(self, obs) -> int:
        return (self._berthed_stale_after if self.is_berthed(obs)
                else self._stale_after)

    # -- ingest ------------------------------------------------------------
    def add(self, obs: Observation) -> bool:
        """Accept an observation. Returns True if it was kept AND changed the
        track - a duplicate relay or an out-of-order fix returns False, so it
        does not wake the entities (SSOT item 246).

        ⚠ The service filters by BOUNDING BOX; we asked for a CIRCLE. A box
        corner is 1.41x the radius away, so without this check the integration
        silently shows vessels up to 41% further out than configured.
        """
        if obs.latitude is None or obs.longitude is None:
            return False
        if not within_radius(self._lat, self._lon, self._radius,
                             obs.latitude, obs.longitude):
            return False
        track = self._tracks.get(obs.identity)
        if track is None:
            track = self._tracks[obs.identity] = Track(obs.identity)
        return track.add(obs)

    # -- eviction ----------------------------------------------------------
    def prune(self, now: _dt.datetime | None = None) -> int:
        """⚠ Evict on last_seen, never on a total count. Removed count is
        returned so a caller can log it."""
        now = now or _dt.datetime.now(_dt.timezone.utc)
        dead = []
        for k, track in self._tracks.items():
            obs = track.current
            if obs is None:
                continue
            age = (now - obs.observed_at).total_seconds()
            if age > self._window_for(obs):
                dead.append(k)
        for k in dead:
            del self._tracks[k]
        return len(dead)

    # -- publish -----------------------------------------------------------
    def published(self) -> list[Observation]:
        """The observations to expose, nearest first, capped.

        ⚠ When the cap bites, WHICH vessels are dropped must be deterministic
        and must match what the user asked for. Nearest-first does both;
        dropping arbitrarily would make the entity set flap between updates for
        no visible reason.

        ⚠ 50 truncated 36% of samples on ordinary suburban water and the peak
        was 106. `truncated_from` is recorded so the integration can SAY it is
        showing a subset - a quietly clipped list looks like missing coverage.
        """
        rows = []
        for track in self._tracks.values():
            obs = track.publish()
            if obs is None or obs.latitude is None:
                continue
            rows.append((obs.identity, obs.latitude, obs.longitude, obs))
        total = len(rows)
        picked = nearest(self._lat, self._lon, rows, self._max)
        self.truncated_from = total if total > self._max else None
        return [payload for _d, _k, _la, _lo, payload in picked]

    def distance_to(self, obs: Observation) -> float:
        return distance_km(self._lat, self._lon, obs.latitude, obs.longitude)

    @property
    def max_vessels(self) -> int:
        """The per-entry cap. When `truncated_from` is set, published()
        returned exactly this many."""
        return self._max

    def __len__(self) -> int:
        return len(self._tracks)
