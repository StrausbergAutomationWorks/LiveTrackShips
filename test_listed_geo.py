"""Backlog 315 task 5: the listed vessel as an ENTITY, against REAL Home Assistant (runs in the HA container, as
test_geo_location.py does). What it pins down:
  * a listed, sourced vessel: label "USCG", friendly name and `name` the list's, `operator_short`, the list's
    attributes, the picture in the list's tone with the glow (t=mil, l=g), the source's credit then the list's
  * a vessel the list does not hold, a cleared one, and a non-vessel are drawn exactly as before
  * the claims: every vessel the entry draws, released at unload (source wiring)
  * web.py: l=g only on a listed picture; the view reads it
Run: python test_listed_geo.py   (in the container; saw-livetrack 0.2.20 on the path)
"""
import datetime as dt
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).parent / "custom_components"))

from saw_livetrack import enforcement_vessels as ev                 # noqa: E402
from live_track_ships import enforcement as enf                      # noqa: E402
from live_track_ships.geo_location import ShipEvent                  # noqa: E402
from live_track_ships.sources.base import Observation                # noqa: E402
from live_track_ships.web import picture_url                         # noqa: E402

passed = failed = 0
T0 = dt.datetime(2026, 10, 30, 22, 0, 0, tzinfo=dt.timezone.utc)
CREDIT = "Data: aisstream.io (https://aisstream.io)"


def check(label, got, want=True):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}" + ("" if ok else f"   got {got!r} want {want!r}"))


DOC = {"name": "EnforcementVessels", "schema": 1, "built": "b", "license": "ODbL-1.0", "theatres": [],
       "entries": [{"id": "uscg-wpc", "short": "USCG"}],
       "vessels": [{"mmsi": "338926432", "name": "USCGC Benjamin Bottoms (WPC 1132)", "agency": "US Coast Guard",
                    "hull": "WPC 1132", "entry": "uscg-wpc", "status": "sourced"},
                   {"mmsi": "366999999", "name": "Gone", "agency": "US Coast Guard", "status": "cleared"}]}
reader = ev.VesselList(str(pathlib.Path(tempfile.mkdtemp()) / ev.CACHE_NAME))
reader._install(json.dumps(DOC).encode())


def obs(mmsi, name="CG BOTTOMS", ship_type=35, raw="PositionReport"):
    return Observation(identity=mmsi, source="live_track_ships", observed_at=T0, latitude=41.9, longitude=-87.6,
                       course_deg=90.0, heading_deg=91, speed_kmh=20.0, name=name, ship_type=ship_type,
                       length_m=47.0, raw_message_type=raw)


print("=== a listed, sourced vessel: the list's look ===")
e = ShipEvent(obs("338926432"), 3.2, CREDIT, reader)
a = e.extra_state_attributes
check("label", a["marker_label"], "USCG")
check("friendly name is the list's name", e.name, "USCGC Benjamin Bottoms (WPC 1132)")
check("`name` the same text (D4b rule 14)", a["name"], e.name)
check("operator_short", a["operator_short"], "USCG")
check("status, agency, entry, hull", (a["enforcement_status"], a["enforcement_agency"], a["enforcement_entry"],
                                      a["hull"]), ("sourced", "US Coast Guard", "uscg-wpc", "WPC 1132"))
check("list_name", a["list_name"], "USCGC Benjamin Bottoms (WPC 1132)")
check("picture in the list's tone, exactly", "t=mil&" in e.entity_picture)
check("picture with the glow", "l=g" in e.entity_picture)
check("Ships' own silhouette for its type", "/military/" in e.entity_picture)
check("credit: the source, then the list", e.attribution, CREDIT + "; " + enf.LIST_ATTRIBUTION)
check("identity and id unchanged", (a["identity"], e.suggested_object_id), ("338926432", "vessel_338926432"))
check("still rotated by heading", a.get("icon_rotation_basis"), "heading")

print("\n=== everything else is drawn as before ===")
for label, o in (("an unlisted vessel", obs("367000099", "TUG ONE", 52)),
                 ("a cleared vessel", obs("366999999", "GONE", 35))):
    plain = ShipEvent(o, 1.0, CREDIT)
    seen = ShipEvent(o, 1.0, CREDIT, reader)
    check(f"{label}: same attributes with or without the list",
          seen.extra_state_attributes, plain.extra_state_attributes)
    check(f"{label}: same picture", seen.entity_picture, plain.entity_picture)
    check(f"{label}: same credit", seen.attribution, CREDIT)
    check(f"{label}: no glow", "l=g" in seen.entity_picture, False)
buoy = ShipEvent(obs("338926432", "NET 1", None, raw="StaticDataReport"), 1.0, CREDIT, reader)
check("the listing is for vessels only (a non-vessel kind is never listed)",
      buoy._listed is None or buoy._obs.kind == "vessel")
check("an entity with no reader is not listed", ShipEvent(obs("338926432"), 1.0, CREDIT)._listed, None)

print("\n=== the claims (backlog 315 task 5) ===")
src = (pathlib.Path(__file__).parent / "custom_components/live_track_ships/geo_location.py").read_text(encoding="utf-8")
sync = src[src.index("    def _sync():"):src.index("    def _release_all()")]
check("every drawn vessel claimed, each pass", "client.claim(consumer, seen)" in sync)
check("each entity is given the instance's reader",
      "ShipEvent(obs, distance, feed.attribution, feed.vessel_reader)" in sync)
check("claimed after the pass decides what it draws", sync.index("owners[identity] = me") < sync.index("client.claim("))
check("released at unload", "client.release(consumer)" in src[src.index("    def _release_all()"):])
check("named as the entry's aisstream consumer", 'consumer = f"{DOMAIN}:{me}"' in src)
init = (pathlib.Path(__file__).parent / "custom_components/live_track_ships/__init__.py").read_text(encoding="utf-8")
check("one reader per instance, the library's",
      '_ev.shared_list(hass.data, hass.config.path(".storage", _ev.CACHE_NAME))' in init)
check("the cache loaded only by the first", "first = _ev.STORE_KEY not in hass.data" in init)
check("refreshed hourly and at start", "async_track_time_interval(hass, _check_list, LIST_TICK)" in init
      and 'hass.async_create_background_task(_check_list(), f"{DOMAIN}_vessel_list")' in init)

print("\n=== web.py ===")
check("l=g only with the glow", "l=g" in picture_url("military", None, "mil", 0.72, False, lights="glow"))
check("no l= otherwise", "l=" in picture_url("military", None, "mil", 0.72, False), False)
web = (pathlib.Path(__file__).parent / "custom_components/live_track_ships/web.py").read_text(encoding="utf-8")
check("the view reads l=g", 'lights = icons.LIGHTS_GLOW if q.get("l") == "g" else None' in web)
check("and passes it to render", "counter, tow, moving, lights)" in web)

print(f"\nchecks: {passed + failed}  passed: {passed}  failed: {failed}")
sys.exit(1 if failed else 0)
