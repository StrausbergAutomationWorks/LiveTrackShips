# Live Track Ships

**AIS ship, boat and vessel tracking for Home Assistant.** Part of Live Track —
ships, aircraft and trains on one map.

Live marine AIS data from [aisstream.io](https://aisstream.io),
[Fintraffic Digitraffic](https://www.digitraffic.fi/en/marine-traffic/) or
[BarentsWatch](https://www.barentswatch.no/en/), shown as Home Assistant
entities and map markers.

**Status: pre-release.**

## What AIS is

AIS — Automatic Identification System — is a VHF broadcast that vessels use to
announce their position, identity and voyage to each other and to shore. It is
the marine equivalent of ADS-B. Commercial vessels are required to carry it;
many recreational boats carry it voluntarily, usually as a lower-powered
Class B unit.

AIS is broadcast in the clear. Anyone with a receiver can hear it, and public
aggregators republish it.

## What this shows

**Everything the source sends.** Nothing is filtered out, and there is no
setting to hide a category.

| In the feed | Shown |
|---|---|
| Cargo ships, tankers, tugs, ferries, passenger vessels | yes |
| Fishing, pilot, law-enforcement and other working craft | yes |
| **Private pleasure craft and sailboats** | **yes — with name and position** |
| **Fishing-gear buoys** that transmit AIS | **yes — drawn as a fish** |
| Search-and-rescue (SAR) aircraft | when the source sends them |
| Aids to navigation — buoys, beacons, lighthouses | when the source sends them |
| AIS shore base stations | when the source sends them |

### Private boats are shown, and you should know what that means

A recreational vessel that transmits AIS appears on your map exactly like a
cargo ship. Depending on what the boat broadcasts, its entity can carry:

- its **name**, which is also the label drawn on the map
- its **MMSI** and **radio call sign**, both permanent and publicly searchable
- its **position** to about a metre, its previous position, and when each was
  heard
- its speed, course and heading, when sent
- its length, beam and vessel type, when sent

A boat that keeps its transponder on at the dock stays on the map at its berth
for as long as it keeps transmitting.

There is no opt-out list for AIS, as there is for aircraft, and this
integration does not invent one. If you want fewer private boats on your map,
reduce the radius.

### Vessel type is often missing, especially for small boats

Position and name arrive with nearly every message. Vessel type and size arrive
in a separate, slower message, and many small-boat (Class B) units rarely send
the part that carries them. Expect a large share of vessels — most small craft
among them — to show no type or dimensions, and expect all vessels to be
sparse for several minutes after Home Assistant restarts. That is the data,
not a fault.

### Not everything on AIS is a ship

Each entity carries `object_kind`: `vessel`, `net_buoy`, `aton` (aid to
navigation), `base_station`, `sar_aircraft` or `distress_beacon`. Most are
told apart by the identity format the ITU assigns them. Fishing-gear buoys
are not: they transmit with ship-style identities, so they are recognised by
their factory names (FISHING BOUY, NET MARK, BUOY) together with the absence
of a broadcast length.

Anything that is not a vessel is shown without a vessel type, size or
navigational status. Fishing-gear buoys drift with their lines, so they keep
their speed and course and are drawn as a salmon pointing the way they drift.

Which of these appear depends on the source. Measured on one evening:

| Source | Fishing-gear buoys | SAR aircraft | Aids to navigation, base stations |
|---|---|---|---|
| BarentsWatch | yes | yes | none seen |
| Digitraffic | none seen | yes | none seen |
| aisstream.io | none seen | none seen | none seen |

aisstream.io delivered only vessel position and vessel detail messages, both
over the Great Lakes and over the same Norwegian and Danish waters where
BarentsWatch shows the buoys.

## Sources

You choose one source per configured area.

| Source | Coverage | Needs |
|---|---|---|
| aisstream.io | worldwide, where volunteers run receivers | a free API key |
| Fintraffic Digitraffic | Finnish and Baltic waters | nothing |
| BarentsWatch AIS Live | Norwegian waters | a free client ID and secret |

Which categories appear, how fresh positions are and how complete vessel
details are all depend on the source you choose.

### Attribution

Every vessel entity, and each area's `ships_in_range` sensor, carries an
`attribution` naming the source that supplied it; Home Assistant shows it in
the entity's details. Two of the sources license their data with an
attribution requirement, and Live Track Ships changes the data it receives
(units converted, only vessels inside your circle), so their lines say so. If
you show this data to others, for example on a public dashboard, read the
source's own terms:

- **aisstream.io**: no published terms. <https://aisstream.io>
- **Fintraffic Digitraffic**: CC BY 4.0.
  <https://www.digitraffic.fi/en/terms-of-service/>
- **BarentsWatch**: Norwegian Licence for Open Government Data (NLOD).
  <https://www.barentswatch.no/en/articles/api-terms-and-conditions/>

## Map card

Vessels are drawn by [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)
(`custom:live-track-map-card`), the one map every Live Track integration
renders on. It draws each vessel's own picture, turns it to the vessel's
heading, and slides it between real fixes along the water rather than straight
across the land.

**The card is installed with the integration.** This integration carries a
released copy of the card, serves it, and registers it as a dashboard resource
when Home Assistant starts; there is nothing to download or copy into `www`.
Every Live Track integration does the same, and they keep exactly one resource
row between them: the highest card version any of them carries, never a
downgrade. A card you installed through HACS is left alone. Removing the last
area of this integration hands the row to another Live Track integration, or
removes it if none is left. See the card's README, section
[Live Track](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).

If your dashboards' resources are set in YAML (`lovelace: resource_mode: yaml`),
nothing can be registered for you. A Repairs issue then gives the exact line to
add; it looks like this, with the integration's own address in place of the
placeholders:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_ships/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

If the integration's files are removed (through HACS, say) while its areas are
still set up, and no other Live Track integration is installed, nothing is left
to tidy the row: remove it in Settings > Dashboards > Resources. To install the
card by hand instead, follow the card's README; the resource row of a
hand-installed copy under `/local/` is pointed at an integration's copy only
when that copy is a newer release.

Give it the vessels with
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities),
filtering on `domain: geo_location` and
`attributes: {source: live_track_ships}`. With other Live Track integrations
installed, add one filter for each of their sources.

Any other map card that shows `geo_location` entities shows the vessels too,
without the card's pictures and slides.

## Where it looks

You give it a **latitude, a longitude and a radius**. The centre can be
anywhere in the world; the radius can be 1 to 500 km. The default is **50 km**.
Each vessel's state is its distance from your centre point.

How many vessels a circle contains depends far more on *which water* than on
*how big*. In testing, a 50 km circle held about 4 vessels over Chicago and
about 340 over the Solent in southern England — the same radius, roughly 80×
the traffic. So the integration keeps at most a set number of vessels (1,000 by
default, adjustable up to 5,000), keeps the nearest when there are more, and
says so on its `ships_in_range` sensor.

All your areas **together** show at most 2,500 vessels, whatever their
sources. Each area's settings have a slider, *Maximum vessels on the map, all
Live Track Ships entries together*, that can only lower that ceiling; the
lowest setting on any enabled area applies. Lower it on slower hardware.

## Coverage, measured rather than promised

Coverage is good where receivers are and absent where they are not, and **no
configuration can create coverage that does not exist**.

Measured on 2026-09-02 around Chicago, on aisstream.io:

- **Great Lakes** — 100 distinct vessels in 120 seconds, all five lakes plus
  the connecting waters.
- **Chicago River, downtown** — busy and reliable.
- **Chicago Sanitary and Ship Canal, Cal-Sag Channel, Calumet River** — one
  hour of listening, **zero vessels**. The canal is not empty: its tows are
  visible on commercial services via satellite AIS, which free aggregators do
  not carry. The traffic is real; the terrestrial coverage is not.

No vessels in your area may mean no receivers rather than no boats. Check that
your source covers your water before assuming the integration is broken.

A vessel that stops appearing has not necessarily left. None of these sources
guarantees delivery, so the integration shows when each vessel was last heard
and removes it only after a period of silence.

## Requirements

- Home Assistant with outbound internet access
- For aisstream.io: a free API key from
  [aisstream.io](https://aisstream.io/account). aisstream allows **three
  connections per account and three per public IP**; if you run other tools
  against the same key, budget for it.
- For BarentsWatch: a free client ID and secret, self-registered at
  BarentsWatch. Enter the client ID exactly as issued.

## Not affiliated

Not affiliated with aisstream.io, Fintraffic, BarentsWatch, MarineTraffic,
VesselFinder, or any maritime authority. AIS is a safety-of-navigation system;
**this integration is for interest and is not for navigation, collision
avoidance, or any operational purpose.**

## Licence

MIT.
