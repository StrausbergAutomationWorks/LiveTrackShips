"""The EnforcementVessels list on this integration's vessels (backlog 315 task 5, Lee 2026-10-30 22:15).

Where a vessel this integration draws is on the list, it is drawn with the LIST'S LOOK and Live Track SALT does not
draw it: one vessel, one marker.
  (A) ANYWHERE this integration draws it, not only inside the list's theatres (Lee: option 2, as Live Track Aircraft
      treats a listed aircraft anywhere in its circle).
  (B) This integration's OWN silhouette for the vessel's type, in the Coast Guard's army-green fill (LIST_TONE) with
      the sourced red/blue glow; the label the entry's short form ("USCG"); `name` the list's name and
      `operator_short` the agency, for the hover (06_MAP_CONTRACT.md D4b rule 14: "USCGC Benjamin Bottoms (WPC 1132)
      · USCG"); the list's ODbL credit beside the source's.
  (C) Every vessel this integration draws is CLAIMED on the shared aisstream client (geo_location.py); SALT skips
      what others claim.
! THE RULES BELOW ARE LIVE TRACK SALT'S (its vessels.py VesselTracker.record), copied: label, hover name and agency,
the attributes and the credit. Two consumers now hold the same rule, so by rule 2 it belongs in saw-livetrack; until
it moves, change both or neither.
! The READER is saw_livetrack.enforcement_vessels (saw-livetrack 0.2.20), one per instance, shared with SALT.
! No Home Assistant import.
"""

from __future__ import annotations

from saw_livetrack import enforcement_vessels as ev

# saw_livetrack.aircraft_icons' "mil": army green, the military and the Coast Guard (tests pin the two equal).
LIST_TONE = "mil"
LIST_LIGHTS = "glow"            # the sourced red/blue glow (saw_livetrack.aircraft_icons LIGHTS_GLOW)
MAX_LABEL_CHARS = 22            # SALT's tracker.MAX_LABEL_CHARS: one label rule for aircraft and vessels
OPERATOR_SHORT_MAX = 22         # 06_MAP_CONTRACT.md D4b rule 12
LIST_ATTRIBUTION = ("Contains information from EnforcementVessels "
                    "(https://github.com/StrausbergAutomationWorks/EnforcementVessels), "
                    "which is made available under the Open Database License (ODbL) v1.0")


def listed(reader, identity) -> ev.Vessel | None:
    """The list's row for this MMSI when it is listed and not cleared, else None. No reader, no listing."""
    if reader is None:
        return None
    v = reader.vessel(identity)
    return v if v is not None and v.status != ev.CLEARED else None


def lights(v: ev.Vessel) -> str | None:
    """The glow on a SOURCED entry only, as SALT draws it."""
    return LIST_LIGHTS if v.status == ev.SOURCED else None


def _text(value) -> str:
    return value.strip() if isinstance(value, str) else ""


def _cut(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def label(v: ev.Vessel) -> str:
    """The marker's label: the entry's short form, else the agency, else "Listed vessel"."""
    return _cut(_text(v.short) or _text(v.agency) or "Listed vessel", MAX_LABEL_CHARS)


def name(v: ev.Vessel, ais_name) -> str | None:
    """The hover's name: the list's, else what the vessel broadcasts; None when neither."""
    return _text(v.name) or _text(ais_name) or None


def operator_short(v: ev.Vessel) -> str | None:
    """The hover's agency: the entry's short form, else the agency, at most 22 characters; None when neither."""
    op = _text(v.short) or _text(v.agency)
    return _cut(op, OPERATOR_SHORT_MAX) if op else None


def attributes(v: ev.Vessel, ais_name) -> dict:
    """What a listed vessel adds to its entity, as SALT publishes it. Unknown values omitted (D0)."""
    out = {"enforcement_status": v.status}
    for key, value in (("enforcement_agency", v.agency), ("enforcement_entry", v.entry), ("hull", v.hull),
                       ("list_name", _text(v.name) or None), ("name", name(v, ais_name)),
                       ("operator_short", operator_short(v))):
        if value:
            out[key] = value
    return out


def attribution(base: str | None) -> str:
    """The source's credit, then the list's."""
    return (base + "; " + LIST_ATTRIBUTION) if base else LIST_ATTRIBUTION
