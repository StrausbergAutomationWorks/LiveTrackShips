"""Config flow.

⚠ Requiring a free API key is NOT disqualifying (00_START_HERE.md). HA
integrations do this constantly. Prefer zero setup; accept a free account when
nothing better exists - and for worldwide AIS, nothing does.

⚠ THE OPTIONS FLOW MUST NOT RE-SUBSCRIBE PER KEYSTROKE. aisstream caps
subscription updates at one per second and a faster update CLOSES THE
CONNECTION. Options are applied on submit, by reloading the entry.
"""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import selector

from .centre import from_form, to_form
from .const_flow import (
    CONF_API_KEY, CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_INSTANCE_MAX,
    CONF_LATITUDE, CONF_LOCATION, CONF_LONGITUDE, CONF_MAX_VESSELS,
    CONF_RADIUS_KM,
    INSTANCE_MAX_STEP, INSTANCE_MAX_VESSELS, MIN_INSTANCE_MAX_VESSELS,
    CONF_SOURCE, DEFAULT_MAX_VESSELS, DOMAIN, SOURCE_AISSTREAM,
    SOURCE_BARENTSWATCH, SOURCES,
)
from .geo import (
    DEFAULT_RADIUS_KM, MAX_RADIUS_KM, MAX_VESSELS, MIN_RADIUS_KM,
    RadiusError, validate_centre, validate_radius,
)

_LOGGER = logging.getLogger(__name__)

# Where a user gets a free aisstream key; a placeholder in the dialog's texts.
AISSTREAM_ACCOUNT_URL = "https://aisstream.io/account"
ISSUES_URL = "https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues"

# Warn when at least this share of the circle is outside what the source can
# show. Below it the gap is an edge sliver, not a surprise.
COVERAGE_WARN_SHARE = 0.05


async def outside_share_for(hass, cfg) -> float | None:
    """Share of the configured circle outside the source's published area, or
    None when there is nothing to say (item 249).

    ⚠ ONLY BarentsWatch publishes its area, so only it is checked. Any failure
    - bad credentials, no network, a changed response - is None, never a
    warning: an unknown area is not a gap, and the flow must not be blocked by
    a check that is advice. The credentials the user just typed are used
    once, for one token and one request, and are not logged."""
    if cfg.get(CONF_SOURCE) != SOURCE_BARENTSWATCH:
        return None
    try:
        from homeassistant.helpers.aiohttp_client import async_get_clientsession
        from .coverage import outside_share
        from .sources.barentswatch import BarentsWatchSource
        src = BarentsWatchSource(
            async_get_clientsession(hass), cfg[CONF_CLIENT_ID],
            cfg[CONF_CLIENT_SECRET], cfg[CONF_LATITUDE], cfg[CONF_LONGITUDE],
            cfg[CONF_RADIUS_KM])
        area = await src.open_area()
        if not area:
            return None
        return await hass.async_add_executor_job(
            outside_share, cfg[CONF_LATITUDE], cfg[CONF_LONGITUDE],
            cfg[CONF_RADIUS_KM], area)
    except Exception:                              # noqa: BLE001
        _LOGGER.debug("coverage check skipped", exc_info=True)
        return None


class LiveTrackShipsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """⚠ VERSION IS PERMANENT ONCE SHIPPED. Bumping it requires a migration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}

        if user_input is not None:
            # The map marker arrives as one CONF_LOCATION; the entry stores
            # CONF_LATITUDE and CONF_LONGITUDE (centre.py). The raw input is
            # kept for a re-render, so the marker stays where it was put.
            shown = user_input
            values, loc_error = from_form(user_input)
            if loc_error:
                errors[CONF_LOCATION] = loc_error
                user_input = {k: v for k, v in user_input.items()
                              if k != CONF_LOCATION}
            else:
                user_input = values
            source = user_input[CONF_SOURCE]
            try:
                if not loc_error:
                    validate_centre(user_input[CONF_LATITUDE],
                                    user_input[CONF_LONGITUDE])
                validate_radius(user_input[CONF_RADIUS_KM])
            except RadiusError:
                errors[CONF_RADIUS_KM] = "radius_out_of_range"
            except ValueError:
                errors[CONF_LOCATION] = "invalid_location"

            if source == SOURCE_AISSTREAM and not user_input.get(CONF_API_KEY):
                errors[CONF_API_KEY] = "key_required"
            # ⚠ BarentsWatch needs BOTH. Half a credential pair fails at the
            # token endpoint with `invalid_client`, which says nothing useful
            # about which half is missing - so check here.
            if source == SOURCE_BARENTSWATCH:
                if not user_input.get(CONF_CLIENT_ID):
                    errors[CONF_CLIENT_ID] = "client_id_required"
                if not user_input.get(CONF_CLIENT_SECRET):
                    errors[CONF_CLIENT_SECRET] = "client_secret_required"

            if not errors:
                # ⚠ unique_id is the CENTRE and SOURCE, not the title. Two
                # entries on the same water from the same source would double
                # every entity and burn one of only THREE connections per IP.
                uid = (f"{source}:{user_input[CONF_LATITUDE]:.4f}:"
                       f"{user_input[CONF_LONGITUDE]:.4f}")
                await self.async_set_unique_id(uid)
                self._abort_if_unique_id_configured()
                self._pending = user_input
                # ⚠ Item 249: say so BEFORE creating the entry when part of
                # the circle lies outside what the source can ever show.
                share = await outside_share_for(self.hass, user_input)
                if share is not None and share >= COVERAGE_WARN_SHARE:
                    self._share = share
                    return await self.async_step_coverage()
                return self._create()

        return self.async_show_form(
            step_id="user",
            data_schema=self._schema(shown if user_input is not None else None),
            errors=errors,
            description_placeholders={
                "radius_min": str(int(MIN_RADIUS_KM)),
                "radius_max": str(int(MAX_RADIUS_KM)),
                # hassfest refuses a URL inside strings.json; the account page
                # is passed in, for the field description and the error alike.
                "aisstream_url": AISSTREAM_ACCOUNT_URL,
                # Where to ask for a ship's own picture, or report a mistake
                # in a translation (the dialog's description says both).
                "issues_url": ISSUES_URL,
            },
        )

    def _create(self):
        data = self._pending
        return self.async_create_entry(
            title=f"Ships near {data[CONF_LATITUDE]:.3f}, "
                  f"{data[CONF_LONGITUDE]:.3f}",
            data=data)

    async def async_step_coverage(self, user_input=None):
        """A warning, not an error: the user may want exactly that circle.
        Submitting creates the entry as entered; closing the dialog creates
        nothing."""
        if user_input is not None:
            return self._create()
        return self.async_show_form(
            step_id="coverage", data_schema=vol.Schema({}),
            description_placeholders={"percent": str(round(self._share * 100))})

    def _existing(self, key: str) -> str:
        """The key from an entry the user already configured, if any.

        ⚠ Someone adding a SECOND area should not retype a 40-character key.
        This is the only legitimate way to pre-fill it.

        ⚠ WHAT THIS DELIBERATELY DOES NOT DO: read a key from disk. An
        integration that scavenges the filesystem for credentials is a
        security smell and would be flagged in review - and a path that exists
        on the maintainer's machine is exactly the "works only for me" failure
        `00_START_HERE.md` names. A stranger installing from HACS has no such
        file, and the integration must behave identically for them.
        """
        for entry in self._async_current_entries():
            value = entry.data.get(key)
            if value:
                return value
        return ""

    def _schema(self, prior):
        prior = prior or {}
        return vol.Schema({
            vol.Required(CONF_SOURCE,
                         default=prior.get(CONF_SOURCE, SOURCE_AISSTREAM)):
                vol.In(SOURCES),
            vol.Optional(
                CONF_CLIENT_ID,
                default=prior.get(CONF_CLIENT_ID) or
                self._existing(CONF_CLIENT_ID)): cv.string,
            vol.Optional(
                CONF_CLIENT_SECRET,
                default=prior.get(CONF_CLIENT_SECRET) or
                self._existing(CONF_CLIENT_SECRET)): cv.string,
            vol.Optional(
                CONF_API_KEY,
                # ⚠ Pre-filled but still EDITABLE - a user may hold separate
                # keys, and aisstream allows only three connections per
                # account, so splitting areas across keys is a real reason to
                # change it.
                default=prior.get(CONF_API_KEY) or self._existing(CONF_API_KEY)):
                cv.string,
            # ONE map marker, not two number fields (backlog 317, item 268).
            # A re-render after an error shows the marker where it was put.
            vol.Required(
                CONF_LOCATION,
                default=(prior.get(CONF_LOCATION)
                         if isinstance(prior.get(CONF_LOCATION), dict)
                         else to_form(prior, self.hass.config.latitude,
                                      self.hass.config.longitude))):
                selector.LocationSelector(selector.LocationSelectorConfig(
                    radius=False, icon="mdi:ferry")),
            vol.Required(
                CONF_RADIUS_KM,
                default=prior.get(CONF_RADIUS_KM, DEFAULT_RADIUS_KM)):
                vol.All(vol.Coerce(float),
                        vol.Range(min=MIN_RADIUS_KM, max=MAX_RADIUS_KM)),
            vol.Required(
                CONF_MAX_VESSELS,
                default=prior.get(CONF_MAX_VESSELS, DEFAULT_MAX_VESSELS)):
                # ⚠ MAX_VESSELS is a VALIDATION CEILING, not a count and not a
                # default. Conflating the two is a recurring error - see
                # 05_SHARED_LESSONS.md A2.
                vol.All(vol.Coerce(int), vol.Range(min=1, max=MAX_VESSELS)),
        })

    @staticmethod
    @callback
    def async_get_options_flow(entry):
        return LiveTrackShipsOptionsFlow()


class LiveTrackShipsOptionsFlow(config_entries.OptionsFlow):
    """⚠ Applied on SUBMIT, never per field. A re-subscribe faster than once a
    second closes the aisstream connection."""

    async def async_step_init(self, user_input=None):
        errors: dict[str, str] = {}
        current = {**self.config_entry.data, **self.config_entry.options}
        if user_input is not None:
            # The centre can move (Lee 2026-11-15). It is stored in options as
            # CONF_LATITUDE and CONF_LONGITUDE, which override data everywhere
            # the entry is read ({**data, **options}).
            values, loc_error = from_form(user_input)
            if loc_error:
                errors[CONF_LOCATION] = loc_error
            else:
                moved = (values[CONF_LATITUDE] != current.get(CONF_LATITUDE)
                         or values[CONF_LONGITUDE] != current.get(CONF_LONGITUDE))
                if moved and self._uid_taken(values):
                    # The same source already watches that centre in another
                    # entry: two would double every vessel and spend a connection.
                    errors[CONF_LOCATION] = "already_watched"
            if not errors:
                # ⚠ Item 249: a larger radius or a moved centre can push the
                # circle past what BarentsWatch shows.
                if (moved or values.get(CONF_RADIUS_KM)
                        != current.get(CONF_RADIUS_KM)):
                    share = await outside_share_for(
                        self.hass, {**current, **values})
                    if share is not None and share >= COVERAGE_WARN_SHARE:
                        self._pending, self._share = values, share
                        return await self.async_step_coverage()
                return self._save(values)

        return self.async_show_form(
            step_id="init",
            errors=errors,
            description_placeholders={"issues_url": ISSUES_URL},
            data_schema=vol.Schema({
                # The same map marker as at setup (centre.py); it starts at
                # the area's centre, or where it was put if a re-render.
                vol.Required(
                    CONF_LOCATION,
                    default=(user_input.get(CONF_LOCATION)
                             if user_input and isinstance(
                                 user_input.get(CONF_LOCATION), dict)
                             else to_form(current, self.hass.config.latitude,
                                          self.hass.config.longitude))):
                    selector.LocationSelector(selector.LocationSelectorConfig(
                        radius=False, icon="mdi:ferry")),
                vol.Required(
                    CONF_RADIUS_KM,
                    default=current.get(CONF_RADIUS_KM, DEFAULT_RADIUS_KM)):
                    vol.All(vol.Coerce(float),
                            vol.Range(min=MIN_RADIUS_KM, max=MAX_RADIUS_KM)),
                vol.Required(
                    CONF_MAX_VESSELS,
                    default=current.get(CONF_MAX_VESSELS,
                                        DEFAULT_MAX_VESSELS)):
                    vol.All(vol.Coerce(int), vol.Range(min=1, max=MAX_VESSELS)),
                # ⚠ Item 264: ALL Ships entries together, and it can only
                # LOWER INSTANCE_MAX_VESSELS; the lowest enabled setting wins.
                vol.Required(
                    CONF_INSTANCE_MAX,
                    default=current.get(CONF_INSTANCE_MAX,
                                        INSTANCE_MAX_VESSELS)):
                    selector.NumberSelector(selector.NumberSelectorConfig(
                        min=MIN_INSTANCE_MAX_VESSELS, max=INSTANCE_MAX_VESSELS,
                        step=INSTANCE_MAX_STEP,
                        mode=selector.NumberSelectorMode.SLIDER)),
                # No icon options: one icon form for every entry (const_flow.py).
            }),
        )

    def _uid_taken(self, values) -> bool:
        """Another entry of this source already has the moved centre's id."""
        uid = self._uid(values)
        return any(e.unique_id == uid and e.entry_id != self.config_entry.entry_id
                   for e in self.hass.config_entries.async_entries(DOMAIN))

    def _uid(self, values) -> str:
        """The setup flow's unique_id shape: source and centre to 4 places."""
        source = self.config_entry.data.get(CONF_SOURCE, SOURCE_AISSTREAM)
        return (f"{source}:{values[CONF_LATITUDE]:.4f}:"
                f"{values[CONF_LONGITUDE]:.4f}")

    def _save(self, values):
        """Save the options; a moved centre also moves the entry's title and
        unique_id, in the SAME update, so the entry reloads once.

        ⚠ ONE update, not two: async_create_entry then writes the same options
        again, which changes nothing and so does not reload a second time. Two
        reloads within a second would re-subscribe aisstream faster than it
        allows. The vessel entities are keyed by MMSI, not by the centre, so
        none is renamed."""
        current = {**self.config_entry.data, **self.config_entry.options}
        if (values[CONF_LATITUDE] != current.get(CONF_LATITUDE)
                or values[CONF_LONGITUDE] != current.get(CONF_LONGITUDE)):
            self.hass.config_entries.async_update_entry(
                self.config_entry, options=values, unique_id=self._uid(values),
                title=f"Ships near {values[CONF_LATITUDE]:.3f}, "
                      f"{values[CONF_LONGITUDE]:.3f}")
        return self.async_create_entry(data=values)

    async def async_step_coverage(self, user_input=None):
        """The same warning as at setup; submitting saves the options as
        entered."""
        if user_input is not None:
            return self._save(self._pending)
        return self.async_show_form(
            step_id="coverage", data_schema=vol.Schema({}),
            description_placeholders={"percent": str(round(self._share * 100))})
