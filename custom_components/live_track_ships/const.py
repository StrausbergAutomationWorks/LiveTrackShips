"""Constants for Live Track Ships.

⚠ Values here are SCAFFOLDING with one exception: the message-type names and
the service limits are MEASURED against the live aisstream.io feed on
2026-09-02 and should not be edited from memory. See
30_Integrations/Live_Track_Ships/SSOT.md.
"""

DOMAIN = "live_track_ships"

# --------------------------------------------------------------------------
# Service — measured, not assumed
STREAM_URL = "wss://stream.aisstream.io/v0/stream"

# ⚠ The server sends BINARY frames containing UTF-8 JSON. 133 of 133 frames
# across every probe run were BINARY, zero TEXT. Code written against
# WSMsgType.TEXT sees an empty stream WITH NO ERROR.
SUBSCRIBE_WITHIN_SECONDS = 3        # connection closes without a subscription
MIN_SECONDS_BETWEEN_SUBSCRIBES = 1  # faster closes the connection
MAX_MMSI_FILTERS = 200              # nine-character strings
COMPRESS_WBITS = 15                 # aiohttp compress= ; deflate is required
                                    # from Sept 2026 or bandwidth is capped

# ⚠ Subscriptions REPLACE, never merge. An options flow that re-subscribes per
# field change is a self-inflicted disconnect.

# --------------------------------------------------------------------------
# Message types (25, measured from the service documentation)
POSITION_TYPES = (
    "PositionReport",
    "StandardClassBPositionReport",
    "ExtendedClassBPositionReport",
    "LongRangeAisBroadcastMessage",
    "StandardSearchAndRescueAircraftReport",
)
STATIC_TYPES = ("ShipStaticData", "StaticDataReport")
INFRASTRUCTURE_TYPES = ("AidsToNavigationReport", "BaseStationReport")

# ⚠ NO FilterMessageTypes IS SENT. These groupings describe the PROTOCOL and
# are used for interpreting what arrives, not for restricting what is asked
# for. Filtering would BLOCK a type the day the source started sending it, and
# unblocking it would need a code change, a release and a user upgrade. Not
# filtering means it appears on its own.
#
# ⚠ MEASURED 2026-09-08, 11 unfiltered captures incl. 15 minutes over the whole
# Great Lakes: only FIVE types ever arrive from the cloud feed - PositionReport,
# StandardClassBPositionReport, ExtendedClassBPositionReport, ShipStaticData,
# StaticDataReport. AidsToNavigationReport, BaseStationReport and
# StandardSearchAndRescueAircraftReport were NEVER seen.
#
# ⚠ An earlier version of this comment claimed buoys, shore stations and SAR
# aircraft "are all in the feed". That was read off the documented list of 25
# types, not off the wire, and it is FALSE for this source. A local or national
# receiver DOES hear them - see SSOT.md sections 14 and 15.
OBSERVED_TYPES = (
    "PositionReport",
    "StandardClassBPositionReport",
    "ExtendedClassBPositionReport",
    "ShipStaticData",
    "StaticDataReport",
)

# What is and is not a vessel - message types, MMSI formats and net buoys -
# is decided in ONE place: object_kind() in sources/base.py.

# --------------------------------------------------------------------------
# ⚠ AIS sentinel values. NONE of these are real readings. Map to None; never
# display. Same principle as "Unknown" being the correct label for a TIS-B
# radar track - do not fill a gap with a sentinel.
HEADING_UNAVAILABLE = 511
# ⚠⚠ ROT_UNAVAILABLE WAS HERE AND NOTHING EVER IMPORTED IT. It read
# (-128, -127) while the adapters carried their own copies - one of which read
# (-128, 128) - so the corpus held four copies of one constant in three
# different states, and the drift was invisible because this copy was dead.
# Rate of turn is now decoded once, by `rot_to_dps` in sources/base.py, which
# is also the only place that knows +127 is a SATURATION sentinel and not a
# reading. SSOT.md items 18 and 20.
COG_UNAVAILABLE = 360.0
NAV_STATUS_UNDEFINED = 15
SOG_UNAVAILABLE = 102.3
