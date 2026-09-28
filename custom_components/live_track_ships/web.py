"""Serves the vessel marker icons: coloured, sized, rotated.

The pattern is Live Track Aircraft's (SSOT item 254): the icons ship INSIDE
the component, so a user installs the integration and gets them, with nothing
to copy into www/; and the picture reaches the map as `entity_picture`, which
the shared map's card draws.
"""

from __future__ import annotations

import logging

from aiohttp import web

from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant

from . import icons

_LOGGER = logging.getLogger(__name__)

URL_BASE = "/api/live_track_ships/icon"

# ! Bumped whenever the ARTWORK or the renderer changes. Responses are cached
# for a day as immutable, so without this a browser keeps yesterday's picture
# and a fix looks like it did nothing (06_MAP_CONTRACT.md D6a-0a, one level down).
ARTWORK_VERSION = "12"


def picture_url(key: str, degrees: int | None, tone: str = "default",
                weight: float | None = None, badge: bool = True,
                counter: int | None = None) -> str:
    """The entity_picture for one icon.

    ! Tone, weight, badge and the symbol's counter-rotation ride as QUERY
    parameters and only when not the default, so the query is part of the
    cache key and a plain vessel's URL stays short."""
    url = "%s/%s/%s.svg" % (URL_BASE, key,
                            "fixed" if degrees is None else degrees)
    extra = ["v=%s" % ARTWORK_VERSION]
    if tone and tone != "default":
        extra.append("t=%s" % tone)
    if weight is not None:
        extra.append("w=%.2f" % weight)
    if not badge:
        extra.append("b=0")
    if counter:
        extra.append("s=%d" % counter)
    return url + "?" + "&".join(extra)


class ShipIconView(HomeAssistantView):
    """Return one vessel silhouette."""

    url = URL_BASE + "/{key}/{angle}.svg"
    name = "api:live_track_ships:icon"

    # ! An <img> cannot send an Authorization header, so a picture URL must
    # be reachable without one. The response is our own artwork with no user
    # data in it; the URL says only that a vessel of some type exists.
    requires_auth = False

    async def get(self, request: web.Request, key: str,
                  angle: str) -> web.Response:
        path = icons.icon_path(key)
        if path is None:
            # valid_key() admits only the named icons.
            return web.Response(status=404, text="unknown icon")
        if angle == "fixed":
            degrees: int | None = None
        else:
            try:
                degrees = int(angle) % 360
            except ValueError:
                return web.Response(status=400, text="bad angle")

        # ! UNTRUSTED input off a URL: tone falls back through a lookup,
        # weight is clamped in render(), counter is reduced mod 360.
        q = request.query
        tone = q.get("t", "default")
        try:
            weight = float(q.get("w", 0.70))
        except (TypeError, ValueError):
            weight = 0.70
        badge = q.get("b") != "0"
        try:
            counter = int(q.get("s", 0)) % 360 or None
        except (TypeError, ValueError):
            counter = None

        try:
            svg = await request.app["hass"].async_add_executor_job(
                icons.render, path, key, degrees, 64, tone, weight, badge,
                counter)
        except Exception:  # noqa: BLE001
            _LOGGER.exception("Could not render %s at %s", key, angle)
            return web.Response(status=500, text="render failed")

        return web.Response(
            body=svg.encode("utf-8"),
            content_type="image/svg+xml",
            headers={"Cache-Control": "public, max-age=86400, immutable"},
        )


def register(hass: HomeAssistant) -> None:
    """Once per Home Assistant run; a second config entry must not register
    the route again."""
    key = f"{URL_BASE}_registered"
    if hass.data.get(key):
        return
    hass.http.register_view(ShipIconView())
    hass.data[key] = True
