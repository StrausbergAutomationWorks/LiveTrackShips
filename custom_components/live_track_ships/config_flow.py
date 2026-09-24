"""Config flow.

⚠ Requiring a free API key is NOT disqualifying (00_START_HERE.md). HA
integrations do this constantly. Prefer zero setup; accept a free account when
nothing better exists - and for worldwide AIS, nothing does.

⚠ THE OPTIONS FLOW MUST NOT RE-SUBSCRIBE PER KEYSTROKE. aisstream caps
subscription updates at one per second and a faster update CLOSES THE
CONNECTION. Options are applied on submit, by reloading the entry.
"""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .const_flow import (
    CONF_API_KEY, CONF_CARD_ROTATION, CONF_CLIENT_ID, CONF_CLIENT_SECRET,
    CONF_LATITUDE, CONF_LONGITUDE, CONF_MAX_VESSELS, CONF_RADIUS_KM,
    CONF_SILHOUETTE_ONLY, CONF_SOURCE, DEFAULT_CARD_ROTATION,
    DEFAULT_MAX_VESSELS, DEFAULT_SILHOUETTE_ONLY, DOMAIN, SOURCE_AISSTREAM,
    SOURCE_BARENTSWATCH, SOURCES,
)
from .geo import (
    DEFAULT_RADIUS_KM, MAX_RADIUS_KM, MAX_VESSELS, MIN_RADIUS_KM,
    RadiusError, validate_centre, validate_radius,
)


class LiveTrackShipsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """⚠ VERSION IS PERMANENT ONCE SHIPPED. Bumping it requires a migration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}

        if user_input is not None:
            source = user_input[CONF_SOURCE]
            try:
                validate_centre(user_input[CONF_LATITUDE],
                                user_input[CONF_LONGITUDE])
                validate_radius(user_input[CONF_RADIUS_KM])
            except RadiusError:
                errors[CONF_RADIUS_KM] = "radius_out_of_range"
            except ValueError:
                errors["base"] = "invalid_location"

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
                return self.async_create_entry(
                    title=f"Ships near {user_input[CONF_LATITUDE]:.3f}, "
                          f"{user_input[CONF_LONGITUDE]:.3f}",
                    data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=self._schema(user_input),
            errors=errors,
            description_placeholders={
                "radius_min": str(int(MIN_RADIUS_KM)),
                "radius_max": str(int(MAX_RADIUS_KM)),
            },
        )

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
            vol.Required(
                CONF_LATITUDE,
                default=prior.get(CONF_LATITUDE,
                                  self.hass.config.latitude)): cv.latitude,
            vol.Required(
                CONF_LONGITUDE,
                default=prior.get(CONF_LONGITUDE,
                                  self.hass.config.longitude)): cv.longitude,
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
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
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
                # ⚠ Icon options (SSOT item 254). Both default OFF, which
                # works on any card; see const_flow.py.
                vol.Required(
                    CONF_CARD_ROTATION,
                    default=current.get(CONF_CARD_ROTATION,
                                        DEFAULT_CARD_ROTATION)): bool,
                vol.Required(
                    CONF_SILHOUETTE_ONLY,
                    default=current.get(CONF_SILHOUETTE_ONLY,
                                        DEFAULT_SILHOUETTE_ONLY)): bool,
            }),
        )
