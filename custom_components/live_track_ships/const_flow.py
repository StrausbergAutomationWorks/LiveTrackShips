"""Constants for the config flow and setup wiring."""

DOMAIN = "live_track_ships"
# ⚠ geo_location is the map surface; sensor carries the count the dashboard's
# control card needs. A geo_location integration cannot be counted by a
# template, because its entities are transient and unnamed in advance.
PLATFORMS = ["geo_location", "sensor"]

CONF_SOURCE = "source"
CONF_API_KEY = "api_key"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_RADIUS_KM = "radius_km"
CONF_MAX_VESSELS = "max_vessels"
# ⚠ BarentsWatch is the only source needing TWO credentials - OAuth2
# client_credentials. The client_id has the shape <email>:<clientname>
# and must be stored EXACTLY as issued; URL-encoding happens at request
# time, and pre-encoding it fails with an opaque `invalid_client`.
CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"

# ⚠ NO ICON OPTIONS (Lee, 2026-09-25). card_rotation and silhouette_only were
# per-entry options, both default OFF, so an entry created without them drew
# every vessel pre-rotated on a dark disc. Deleted: every entry draws the same
# icon - UNROTATED, no disc, the card turns it by icon_rotation_deg (never both,
# or the rotation doubles: 06_MAP_CONTRACT.md D4). Strangers get LiveTrackMapCard
# too, so there is no "card that cannot rotate" to serve.

SOURCE_AISSTREAM = "aisstream"
SOURCE_DIGITRAFFIC = "digitraffic"
SOURCE_BARENTSWATCH = "barentswatch"

# ⚠ aisstream is the ONLY free, live, GLOBAL source that needs no receiver.
# Digitraffic is open and needs no credentials but covers Finnish and Baltic
# waters only. AISHub requires contributing your own receiver feed. Kystverket
# is unreachable without a registration form and was measured DEAD from here -
# all ports timed out. There is NO free live public AIS feed for US waters.
# See Live Track Ships SSOT section 15.
SOURCES = {
    SOURCE_AISSTREAM: "aisstream.io — worldwide, free API key required",
    SOURCE_DIGITRAFFIC: "Fintraffic Digitraffic — Finnish and Baltic waters, "
                        "no key",
    SOURCE_BARENTSWATCH: "BarentsWatch AIS Live — Norwegian waters, "
                         "free client registration required",
}

# ⚠⚠ THIS IS A SAFETY CEILING, NOT A DISPLAY LIMIT. Revised 2026-09-08.
#
# It was 50, then 100, both chosen to keep a map readable. That reasoning is
# GONE: ha-map-card renders 154 markers comfortably and `cluster_markers` is a
# RUNTIME TOGGLE the user controls, so nothing about the display needs a cap.
#
# What still needs one is the Home Assistant state machine and the recorder.
# ⚠ MAX_RADIUS_KM is 500, and a 500 km circle at the measured Solent density
# of 43.4 vessels per 1000 km2 holds roughly 34,000 vessels. That is not a map
# problem; it is an instance-destroying problem.
#
# So the default is high enough to be invisible on ordinary water - the peak
# measured over five days on the Chicagoland rectangle was 106 - and the
# ceiling exists only to stop a pathological radius over a busy sea.
#
# ⚠ When it DOES bite, say so. A quietly clipped list looks exactly like
# missing coverage.
DEFAULT_MAX_VESSELS = 1000

# ⛔ THE PER-ENTRY CAP ABOVE DOES NOT BOUND THE INSTANCE (SSOT item 246).
# 2026-09-23: four entries, ~1,830 Ships entities rebuilding at once, two
# watchdog restarts of Home Assistant. This ceiling applies across ALL entries.
# ⚠ HOW IT IS SHARED changed 2026-09-24 (SSOT item 253, Lee): no longer
# first-come. quota.allocate() gives each loaded entry an equal share, passing
# what a quiet entry leaves to the others, and an entry over its share drops its
# FARTHEST vessels. Measured the same day with three entries at the ceiling:
# Digitraffic Finland gave back 857 -> 852 and Chicagoland rose 8 -> 13.
#
# ✅ MEASURED SAFE, KEPT (Lee, 2026-09-23). After the throttle fix below, all
# four entries ran at this ceiling with /api/ at 0.00-0.04 s, including through
# a full restart. That shows 1,500 is safe on the development VM (4 GB). It does
# NOT show that anything higher is, and it is not a limit found by pushing
# until something broke. Raise it only on a new measurement, re-run the same
# way (SSOT item 246).
# ✅ RAISED TO 2,500 ON 2026-09-26 (Lee; SSOT item 264), MEASURED on the
# development VM (3 vCPU, 4 GB): five entries wanted about 2,235 and Denmark
# showed its nearest ~455 of 1,600, its outer ring flickering. At 2,500, steady
# at 2,440 Ships entities: /api/ 0.02 s median, 0.04 s max; HA CPU median 15%
# (10% at 1,500); 1.04 GiB. A full restart spikes /api/ to 7.5 s in its first
# minute, and so does a control restart at ~1,450 (6.5 s): HA's own startup,
# not this ceiling. ⚠ ONE MACHINE. What a Pi or an HA Green tolerates is NOT
# measured, and this constant ships to every user.
INSTANCE_MAX_VESSELS = 2500

# ⛔ ONE PASS PER WINDOW, PER ENTRY (SSOT item 246, Lee 2026-09-23).
# Every message used to rebuild the published set and write state for every
# vessel the entry showed. At 1,500 vessels, with aisstream over Danish water,
# that stalled Home Assistant at a FLAT entity count. Now the first change
# after a pass schedules ONE pass this many seconds later; everything arriving
# in between folds into it. Nothing arrives, nothing runs.
# ⚠ A WINDOW, NOT A CLOCK, and the delay is FIXED from the first arrival - so a
# Digitraffic poll (~1,000 fixes at once) always lands in a single pass.
NOTIFY_WINDOW_S = 5.0
