"""Segment tracking: publish the NEWEST fix, and expose the previous one so a
consumer can animate between two OBSERVED points.

⚠ CORRECTED 2026-09-08. This module first held the newest fix BACK, so the
integration always knew both ends of a segment. That was wrong, and it
conflated two independent mechanisms:

    publishing a delayed fix    -> integration -> A FULL UPDATE INTERVAL OF LAG
    animating between two fixes -> consumer    -> only the animation's duration

⚠ On a card that cannot animate, delaying is STRICTLY WORSE than publishing the
newest fix - the same jump, to a staler position, for nothing. And an
integration that hard-codes a delay throws away the benefit of a faster source:
129 s median on the aisstream aggregate, 47 s on Digitraffic, 2-10 s on a local
receiver. The lag should shrink with the feed, not be fixed upstream.

So: the newest observed position is published, and `previous_*` carries the
other end. The consumer picks its own policy - a short fixed slide stays
near-live; duration = the observed gap gives continuous motion and accepts one
interval of lag AS ITS OWN CHOICE.

⚠ STILL INTERPOLATION, NEVER EXTRAPOLATION. Both endpoints are measured. See
10_SEED/05_SHARED_LESSONS.md D3a and D3c.

⚠ WHAT LICENSES ANY LAG AT ALL is that this is NOT A NAVIGATION PRODUCT.
"""

from __future__ import annotations

import dataclasses
import datetime as _dt
from dataclasses import dataclass

from .sources.base import Observation


@dataclass(frozen=True)
class Segment:
    """Two consecutive OBSERVED fixes for one object, and the gap between."""

    identity: str
    start: Observation
    end: Observation

    @property
    def duration_s(self) -> float:
        return max(
            0.0,
            (self.end.observed_at - self.start.observed_at).total_seconds())

    @property
    def is_stationary(self) -> bool:
        return (self.start.latitude == self.end.latitude
                and self.start.longitude == self.end.longitude)

    def position_at(self, when: _dt.datetime):
        """Position along the segment. NEVER outside it.

        ⚠ CLAMPED AT BOTH ENDS ON PURPOSE. Letting the fraction exceed 1.0
        would turn this into extrapolation - silently, with no code change and
        no name change. Provided for consumers that cannot animate but can
        poll; the card-side case does not use it.
        """
        if self.start.latitude is None or self.end.latitude is None:
            return None
        d = self.duration_s
        if d <= 0:
            return self.end.latitude, self.end.longitude
        frac = (when - self.start.observed_at).total_seconds() / d
        frac = min(1.0, max(0.0, frac))
        return (
            self.start.latitude
            + (self.end.latitude - self.start.latitude) * frac,
            self.start.longitude
            + (self.end.longitude - self.start.longitude) * frac,
        )


class Track:
    """Remembers the previous fix so the published one can carry both ends.

    ⚠ `current` is the NEWEST observation. Nothing is held back.
    """

    __slots__ = ("identity", "_previous", "_latest")

    def __init__(self, identity: str):
        self.identity = identity
        self._previous: Observation | None = None
        self._latest: Observation | None = None

    def add(self, obs: Observation) -> bool:
        """⚠ Ignores duplicates and out-of-order fixes. Sources re-send the
        same fix - measured on aisstream, where sub-second gaps were the same
        broadcast relayed by two receivers. Treating those as a segment would
        produce a zero-duration jump.

        Returns False when the fix was ignored, so the store does not wake
        the entities for a message that changed nothing (SSOT item 246)."""
        if self._latest is not None:
            if obs.observed_at < self._latest.observed_at:
                return False
            if obs.observed_at == self._latest.observed_at:
                return False
        self._previous, self._latest = self._latest, obs
        return True

    @property
    def current(self) -> Observation | None:
        """The NEWEST observation. This is what gets published."""
        return self._latest

    @property
    def segment(self) -> Segment | None:
        """Previous fix to newest, or None until two exist."""
        if self._previous is None or self._latest is None:
            return None
        return Segment(self.identity, self._previous, self._latest)

    def publish(self) -> Observation | None:
        """The newest fix, carrying the previous one for a consumer to
        animate from.

        ⚠ On a FIRST SIGHTING the previous fields are absent, and a consumer
        must read that as "place it and do not move it". There is no second
        endpoint, so any motion would be invented.
        """
        if self._latest is None:
            return None
        seg = self.segment
        if seg is None or seg.start.latitude is None:
            return self._latest
        extra = dict(self._latest.extra)
        extra.update({
            "previous_latitude": seg.start.latitude,
            "previous_longitude": seg.start.longitude,
            "previous_observed_at": seg.start.observed_at,
            "segment_duration_s": seg.duration_s,
        })
        return dataclasses.replace(self._latest, extra=extra)
