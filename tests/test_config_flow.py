"""Test the config flow's key pre-fill and validation. Runs inside HA.

⚠ Home Assistant's ConfigFlow needs hass and a flow manager to run properly,
so this tests the pieces we own - the schema builder, the pre-fill lookup and
the validation - with the flow's own machinery stubbed at the seam.
"""
import sys
import pathlib
import types

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "custom_components"))

from live_track_ships.config_flow import (                        # noqa: E402
    LiveTrackShipsConfigFlow)
from live_track_ships.const_flow import (                         # noqa: E402
    CONF_API_KEY, CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_LATITUDE,
    CONF_LOCATION, CONF_LONGITUDE, CONF_MAX_VESSELS, CONF_RADIUS_KM, CONF_SOURCE,
    SOURCE_AISSTREAM, SOURCE_BARENTSWATCH, SOURCE_DIGITRAFFIC)
from live_track_ships.geo import (                                # noqa: E402
    MAX_RADIUS_KM, MAX_VESSELS, MIN_RADIUS_KM, RadiusError,
    validate_centre, validate_radius)

passed = failed = 0


def check(label, got, want=True):
    global passed, failed
    ok = got == want
    passed, failed = passed + ok, failed + (not ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {label}"
          + ("" if ok else f"   got {got!r} want {want!r}"))


def make_flow(existing=()):
    """A flow with hass and current-entries stubbed at the seam."""
    flow = LiveTrackShipsConfigFlow()
    flow.hass = types.SimpleNamespace(
        config=types.SimpleNamespace(latitude=41.8995, longitude=-87.9403))
    flow._async_current_entries = lambda include_ignore=None: list(existing)
    return flow


def entry(**data):
    return types.SimpleNamespace(data=data)


print("=== ⚠ the key pre-fills from an EXISTING ENTRY, not from disk ===")
f = make_flow()
check("no entries -> empty", f._existing(CONF_API_KEY), "")

f = make_flow([entry(**{CONF_API_KEY: "abc123"})])
check("one entry -> its key", f._existing(CONF_API_KEY), "abc123")

f = make_flow([entry(**{CONF_API_KEY: ""}), entry(**{CONF_API_KEY: "second"})])
check("skips an entry with no key", f._existing(CONF_API_KEY), "second")

f = make_flow([entry(**{CONF_API_KEY: "first"}), entry(**{CONF_API_KEY: "second"})])
check("takes the first that has one", f._existing(CONF_API_KEY), "first")

print("\n=== the schema pre-fills but stays editable ===")
f = make_flow([entry(**{CONF_API_KEY: "prefilled"})])
schema = f._schema(None)
defaults = {str(k): k.default() for k in schema.schema
            if hasattr(k, "default") and k.default is not None}
check("api_key default is the existing key",
      defaults.get(CONF_API_KEY), "prefilled")
check("⚠ api_key is Optional, so it can be cleared",
      any(str(k) == CONF_API_KEY and k.__class__.__name__ == "Optional"
          for k in schema.schema))
check("the map marker defaults to the HA location",
      defaults.get(CONF_LOCATION), {"latitude": 41.8995, "longitude": -87.9403})
check("no latitude or longitude field: one marker instead (item 268)",
      {CONF_LATITUDE, CONF_LONGITUDE} & {str(k) for k in schema.schema}, set())
check("a re-render keeps the marker where it was put",
      {str(k): k.default() for k in f._schema(
          {CONF_LOCATION: {"latitude": 33.73, "longitude": -118.27}}).schema
       if hasattr(k, "default") and k.default is not None}.get(CONF_LOCATION),
      {"latitude": 33.73, "longitude": -118.27})

print("\n=== ⚠ prior input beats the pre-fill ===")
f = make_flow([entry(**{CONF_API_KEY: "prefilled"})])
schema = f._schema({CONF_API_KEY: "typed-by-user"})
defaults = {str(k): k.default() for k in schema.schema
            if hasattr(k, "default") and k.default is not None}
check("a typed key survives a re-render",
      defaults.get(CONF_API_KEY), "typed-by-user")

print("\n=== validation the flow relies on ===")
for bad in (0.0, 0.9, 500.1):
    try:
        validate_radius(bad)
        check(f"radius {bad} rejected", False)
    except RadiusError:
        check(f"radius {bad} rejected", True)
check("radius 50 accepted", validate_radius(50), 50.0)
check("centre accepted", validate_centre(41.9, -87.9), (41.9, -87.9))
for lat, lon in ((91.0, 0.0), (0.0, -181.0)):
    try:
        validate_centre(lat, lon)
        check(f"centre {lat},{lon} rejected", False)
    except ValueError:
        check(f"centre {lat},{lon} rejected", True)

print("\n=== ⚠ the ceiling is not the default ===")
from live_track_ships.const_flow import DEFAULT_MAX_VESSELS      # noqa: E402
check("default is below the ceiling", DEFAULT_MAX_VESSELS < MAX_VESSELS)
check("both sources offered",
      {SOURCE_AISSTREAM, SOURCE_DIGITRAFFIC} <=
      set(f._schema(None).schema[
          [k for k in f._schema(None).schema
           if str(k) == CONF_SOURCE][0]].container))


print("\n=== ⚠ BarentsWatch needs TWO credentials ===")
f = make_flow()
schema = f._schema(None)
keys = {str(k) for k in schema.schema}
check("client_id offered", CONF_CLIENT_ID in keys)
check("client_secret offered", CONF_CLIENT_SECRET in keys)
check("api_key still offered", CONF_API_KEY in keys)
check("BarentsWatch is a source option",
      SOURCE_BARENTSWATCH in set(f._schema(None).schema[
          [k for k in f._schema(None).schema
           if str(k) == CONF_SOURCE][0]].container))

print("\n=== the pre-fill generalised to ANY credential ===")
f = make_flow([entry(**{CONF_CLIENT_ID: "you@example.com:live_track_ships",
                        CONF_CLIENT_SECRET: "sekret"})])
check("client_id pre-fills", f._existing(CONF_CLIENT_ID),
      "you@example.com:live_track_ships")
check("client_secret pre-fills", f._existing(CONF_CLIENT_SECRET), "sekret")
check("⚠ an absent credential returns empty, not None",
      f._existing(CONF_API_KEY), "")

print("\n=== an area's settings can move its centre (Lee 2026-11-15) ===")
from live_track_ships.config_flow import LiveTrackShipsOptionsFlow   # noqa: E402


class _Opts(LiveTrackShipsOptionsFlow):
    config_entry = None   # HA's property, replaced by a plain attribute here


def make_opts(source, others=()):
    o = _Opts()
    o.config_entry = types.SimpleNamespace(
        entry_id="me", unique_id=f"{source}:60.0000:25.0000",
        data={CONF_SOURCE: source, CONF_LATITUDE: 60.0, CONF_LONGITUDE: 25.0}, options={})
    o.hass = types.SimpleNamespace(config_entries=types.SimpleNamespace(
        async_entries=lambda domain: [o.config_entry, *others]))
    return o


o = make_opts(SOURCE_DIGITRAFFIC)
check("the moved centre's id has the setup flow's shape",
      o._uid({CONF_LATITUDE: 59.5, CONF_LONGITUDE: 24.75}), "digitraffic:59.5000:24.7500")
other = types.SimpleNamespace(entry_id="other", unique_id="digitraffic:59.5000:24.7500")
o = make_opts(SOURCE_DIGITRAFFIC, [other])
check("another entry of the same source already there -> taken",
      o._uid_taken({CONF_LATITUDE: 59.5, CONF_LONGITUDE: 24.75}), True)
o = make_opts(SOURCE_AISSTREAM, [other])
check("the same centre on ANOTHER source is free",
      o._uid_taken({CONF_LATITUDE: 59.5, CONF_LONGITUDE: 24.75}), False)
me = types.SimpleNamespace(entry_id="me", unique_id="digitraffic:59.5000:24.7500")
o = make_opts(SOURCE_DIGITRAFFIC)
o.hass.config_entries.async_entries = lambda domain: [me]
check("the entry's own id never blocks it",
      o._uid_taken({CONF_LATITUDE: 59.5, CONF_LONGITUDE: 24.75}), False)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
