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
! THE RULES ARE THE LIBRARY'S since saw-livetrack 0.2.21: saw_livetrack.enforcement_vessels, moved there from this
file by span (rule 2: Live Track SALT draws listed vessels by the same rules). The names below are re-exports, so
geo_location.py and the tests read them here as before. Change a rule in the library, not here.
! The READER is saw_livetrack.enforcement_vessels (saw-livetrack 0.2.20), one per instance, shared with SALT.
! No Home Assistant import.
"""

from __future__ import annotations

from saw_livetrack.enforcement_vessels import (  # noqa: F401  (re-exports)
    LIST_ATTRIBUTION, LIST_LIGHTS, LIST_TONE, MAX_LABEL_CHARS, OPERATOR_SHORT_MAX, attribution, attributes,
    label, lights, listed, name, operator_short,
)
