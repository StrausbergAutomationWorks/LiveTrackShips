"""A photo of the vessel, and a link out to it (backlog 346; 06_MAP_CONTRACT.md D4g).

DECIDED by Lee 2026-11-16 01:1x-01:2x CST: photos from Wikidata now (ShipSpotting thumbnails later, preferred
where both exist, if ShipSpotting agrees: a request was sent the same night); the photo in the map's hover box
and, with the link, in a popup on click; the link to VesselFinder.

! THE LOOKUP IS THE LIBRARY'S since saw-livetrack 0.2.43 (2026-11-21): saw_livetrack.vessel_photos, hoisted from
this file when Live Track SALT became its second consumer (05_SHARED_LESSONS.md rule 2), and widened on 2026-11-21
to fall back to MMSI: by IMO (P458), and by MMSI (P587) when the IMO finds nothing or the vessel sends
none. One book per Home Assistant under the library's SAW-neutral key, cache `.storage/saw_vessel_photo_book.json`;
its first start reads this integration's old `saw_vessel_photos.json` once (IMO answers), and never writes it. The
lookup's measurements, rules and tests are the library's.

VesselFinder's page is https://www.vesselfinder.com/vessels/details/<number>: an IMO opened EMMA MAERSK, and so did
her MMSI (measured both, 2026-11-16). A link only: nothing is fetched from VesselFinder.

! Each install looks up the vessels on ITS OWN map, for its own user; nothing passes through SAW.
"""

from __future__ import annotations

from saw_livetrack import vessel_photos as _lib

STORE_KEY = _lib.STORE_KEY

VESSELFINDER = "https://www.vesselfinder.com/vessels/details/{}"


def vessel_links(imo: str | None, mmsi: str | None) -> list:
    """The link out (D4g `marker_links`): VesselFinder by IMO, else by MMSI. Empty when there is neither."""
    number = imo or mmsi
    if not number or not str(number).isdigit():
        return []
    return [{"label": "VesselFinder", "url": VESSELFINDER.format(number)}]


async def shared(hass):
    """The instance's book (saw_livetrack.vessel_photos), started on first use: cache read in the executor, worker
    running for the rest of the run. Shared with every other consumer on the same library."""
    from homeassistant.helpers.aiohttp_client import async_get_clientsession  # noqa: PLC0415

    return await _lib.shared(hass.data, hass.config.path(".storage"), hass.async_add_executor_job,
                             lambda coro: hass.async_create_background_task(coro, "saw_vessel_photo_book"),
                             async_get_clientsession(hass))
