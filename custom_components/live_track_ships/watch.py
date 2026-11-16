"""Watched vessels: a list of MMSIs followed anywhere (backlog 343, 2026-11-15).

DECIDED by Lee 2026-11-15 22:0x CST: the list is its OWN config entry (at most
one, "Watched vessels"); aisstream only, on the shared client's VESSELS
connection (worldwide, MMSI filter); each vessel is an MMSI with an optional
label of the user's own; events for arrived / departed, heard / gone silent,
and destination changed.

One event type, `live_track_ships_watched`, with `change` saying which, so an
automation triggers on one event and filters on its data:

  * `arrived`  the vessel now reports itself moored or at anchor, or (with no
               status) sits under 2 kn: store.VesselStore.is_berthed, the same
               rule the retention windows use;
  * `departed` it is under way again by the same rule;
  * `heard`    a fix after it went silent;
  * `silent`   not heard for the retention window (30 min, or 6 h berthed),
               so it leaves the map; it may still be there;
  * `destination` the crew-entered destination changed (`destination` and
               `destination_previous`).

Rules against nuisance, each decided here, none measured yet:
  1. NO EVENT FROM THE FIRST FIX after a load: it sets the baseline. A restart
     must not announce every watched vessel's state.
  2. ARRIVED AND DEPARTED NEED DWELL_S. The new state must still hold on a fix
     at least DWELL_S after the first fix that showed it, by the vessels' own
     timestamps: a vessel drifting at 2 kn, or a status keyed wrong for one
     report, does not flap.
  3. A destination change counts only between two non-empty destinations, as
     the crew typed them (trimmed, case kept); a destination appearing for
     the first time is the baseline, not a change.
"""

from __future__ import annotations

import logging
import re

from .const_flow import DOMAIN, MAX_WATCHED
from .events import vessel_data
from .store import VesselStore

_LOGGER = logging.getLogger(__name__)

EVENT_WATCHED = f"{DOMAIN}_watched"
DWELL_S = 300

# A circle that holds the whole Earth (half its circumference is 20,015 km):
# the watch entry's store keeps every fix of a listed vessel, wherever it is.
WORLD_RADIUS_KM = 20100.0

_MMSI = re.compile(r"[0-9]{9}")
_SPLIT = re.compile(r"[\s,;]+", re.UNICODE)


class VesselListError(ValueError):
    """`code` is the dialog's error key."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def parse_vessels(text) -> list[dict]:
    """The dialog's text, one vessel per line: a 9-digit MMSI, then an
    optional label (`244650000 Dad's boat`, `244650000, Dad's boat`). Blank
    lines and lines starting with # are skipped; a repeated MMSI keeps its
    first line. Raises VesselListError: vessels_invalid, vessels_empty,
    vessels_too_many."""
    out: list[dict] = []
    seen: set = set()
    for raw in str(text or "").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = _SPLIT.split(line, maxsplit=1)
        mmsi = parts[0]
        if not _MMSI.fullmatch(mmsi):
            raise VesselListError("vessels_invalid")
        if mmsi in seen:
            continue
        seen.add(mmsi)
        label = parts[1].strip(" ,;\t") if len(parts) > 1 else ""
        out.append({"mmsi": mmsi, "label": label} if label else {"mmsi": mmsi})
    if not out:
        raise VesselListError("vessels_empty")
    if len(out) > MAX_WATCHED:
        raise VesselListError("vessels_too_many")
    return out


def format_vessels(vessels) -> str:
    """The stored list back as the dialog's text."""
    return "\n".join(
        f"{v['mmsi']} {v['label']}" if v.get("label") else v["mmsi"]
        for v in vessels or [])


class _State:
    __slots__ = ("berthed", "pending", "since", "destination", "heard")

    def __init__(self, obs):
        self.berthed = VesselStore.is_berthed(obs)
        self.pending = None          # the berthed value waiting out DWELL_S
        self.since = None            # timestamp of the first fix showing it
        self.destination = _dest(obs.destination)
        self.heard = True


def _dest(value):
    value = (value or "").strip()
    return value or None


class WatchEvents:
    """The watched vessels' changes, and the events for them.

    `fire(event_type, data)` is passed in so the logic runs without Home
    Assistant in a test. Distances and bearings are from Home Assistant's
    home location."""

    def __init__(self, store, watch_id, watch_name, home_lat, home_lon,
                 labels, fire, drawn=None):
        self._store = store
        self._watch_id = watch_id
        self._watch_name = watch_name
        self._lat, self._lon = home_lat, home_lon
        self._labels = labels             # mmsi -> label
        self._fire = fire
        self._drawn = drawn or (lambda _identity: False)
        self._state: dict[str, _State] = {}
        self.fired: dict[str, int] = {}

    def run(self) -> None:
        """One pass, after every store change (the feed's listener)."""
        present = self._store.present()
        gone = self._store.take_gone()
        self._store.take_arrivals()       # meaningless for a world circle
        for identity, obs in present.items():
            s = self._state.get(identity)
            if s is None:                 # rule 1: the baseline
                self._state[identity] = _State(obs)
                continue
            if not s.heard:
                s.heard = True
                self._announce("heard", obs)
            self._berthing(identity, s, obs)
            dest = _dest(obs.destination)
            if dest is not None:
                if s.destination is not None and dest != s.destination:
                    previous, s.destination = s.destination, dest
                    self._announce("destination", obs,
                                   destination_previous=previous)
                else:
                    s.destination = dest
        for identity, (reason, last, _outside) in gone.items():
            s = self._state.get(identity)
            if s is not None and s.heard and identity not in present:
                s.heard = False
                s.pending = s.since = None
                if last is not None:
                    self._announce("silent", last)

    def _berthing(self, identity, s: _State, obs) -> None:
        now = VesselStore.is_berthed(obs)
        if now == s.berthed:
            s.pending = s.since = None
            return
        if s.pending != now:
            s.pending, s.since = now, obs.observed_at
            return
        if (obs.observed_at - s.since).total_seconds() >= DWELL_S:
            s.berthed = now
            s.pending = s.since = None
            self._announce("arrived" if now else "departed", obs)

    def payload(self, change, obs, **extra) -> dict:
        identity = obs.identity
        data: dict = {"watch_id": self._watch_id, "watch": self._watch_name,
                      "change": change, "identity": identity}
        label = self._labels.get(identity)
        if label:
            data["label"] = label
        if change != "silent" and self._drawn(identity):
            data["entity_id"] = f"geo_location.vessel_{identity}"
        data.update(vessel_data(obs, None, self._lat, self._lon))
        data.update({k: v for k, v in extra.items() if v is not None})
        return data

    def _announce(self, change, obs, **extra) -> None:
        try:
            data = self.payload(change, obs, **extra)
        except Exception:                          # noqa: BLE001
            _LOGGER.exception("Live Track Ships: watched event for %s not built",
                              getattr(obs, "identity", "?"))
            return
        self.fired[change] = self.fired.get(change, 0) + 1
        self._fire(EVENT_WATCHED, data)

    def snapshot(self) -> list[dict]:
        """Every listed vessel for the watch sensor: label, whether it is
        heard, and its last known state. Small: at most MAX_WATCHED rows."""
        present = self._store.present()
        rows = []
        for mmsi, label in self._labels.items():
            row = {"mmsi": mmsi}
            if label:
                row["label"] = label
            obs = present.get(mmsi)
            row["heard"] = obs is not None
            if obs is not None:
                name = (obs.name or "").strip()
                if name:
                    row["name"] = name
                row["berthed"] = VesselStore.is_berthed(obs)
                dest = _dest(obs.destination)
                if dest:
                    row["destination"] = dest
                row["last_seen"] = obs.observed_at.isoformat()
                if self._drawn(mmsi):
                    row["entity_id"] = f"geo_location.vessel_{mmsi}"
            rows.append(row)
        return rows


def attach(hass, entry, feed) -> WatchEvents:
    """Wire the watch entry's events to Home Assistant. AFTER the platforms,
    as events.attach, so geo_location has claimed this pass's vessels."""
    owners_key = f"{DOMAIN}_owners"      # geo_location.OWNERS_KEY

    def _fire(event_type, data):
        hass.bus.async_fire(event_type, data)

    events = WatchEvents(
        feed.store, entry.entry_id, entry.title,
        hass.config.latitude, hass.config.longitude, feed.labels, fire=_fire,
        drawn=lambda identity: identity in hass.data.get(owners_key, {}))
    entry.async_on_unload(feed.add_listener(events.run))
    return events
