# Live Track Ships

**English** · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Kalaallisut](README.kl.md) · [All languages](#languages)

**AIS ship, boat and vessel tracking for Home Assistant.** Ships near you, or
anywhere in the world you choose, as live markers on your map. Part of Live
Track: ships, aircraft and trains on one map.

Live marine AIS data from [aisstream.io](https://aisstream.io),
[Fintraffic Digitraffic](https://www.digitraffic.fi/en/marine-traffic/) or
[BarentsWatch](https://www.barentswatch.no/en/), shown as Home Assistant
`geo_location` entities and drawn on the shared Live Track map.

**Status: 0.1.0, the first release.** Added to the Marketplace by link (below);
it is not in the Marketplace's catalog yet.

## What AIS is

AIS (Automatic Identification System) is a VHF broadcast that vessels use to
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
| **Private pleasure craft and sailboats** | **yes, with name and position** |
| **Fishing-gear buoys** that transmit AIS | **yes, drawn as a fish** |
| Search-and-rescue (SAR) aircraft | when the source sends them |
| Aids to navigation: buoys, beacons, lighthouses | when the source sends them |
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
the part that carries them. Expect a large share of vessels, most small craft
among them, to show no type or dimensions, and expect all vessels to be sparse
for several minutes after Home Assistant restarts. That is the data, not a
fault. Types and sizes once heard are kept across restarts.

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

You choose one source per area you set up.

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
you show this data to others, for example on a public dashboard, keep the
credit with it and read the source's own terms:

- **aisstream.io**: no published terms. <https://aisstream.io>
- **Fintraffic Digitraffic**: CC BY 4.0.
  <https://www.digitraffic.fi/en/terms-of-service/>
- **BarentsWatch**: Norwegian Licence for Open Government Data (NLOD).
  <https://www.barentswatch.no/en/articles/api-terms-and-conditions/>
- **EnforcementVessels** (the list behind the Coast Guard look, below): ODbL
  v1.0. <https://github.com/StrausbergAutomationWorks/EnforcementVessels>

The exact credit lines are in [ATTRIBUTION.md](ATTRIBUTION.md).

## Requirements

- Home Assistant 2026.11 or later, with outbound internet access.
- For aisstream.io: a free API key from
  [aisstream.io](https://aisstream.io/account). aisstream allows **three
  connections per account and three per public IP**; if you run other tools
  against the same key, budget for it. Live Track SALT, if installed, uses a
  second connection on the same key.
- For BarentsWatch: a free client ID and secret, self-registered at
  BarentsWatch. Enter the client ID exactly as issued.
- Home Assistant installs the Python package this needs (`saw-livetrack`) the
  first time it loads the integration.

## Installation

### From the Marketplace

Live Track Ships is not in the Marketplace's catalog yet. Add it by link:

1. **Settings > Marketplace**, then **Add from link**.
2. Enter `StrausbergAutomationWorks/LiveTrackShips`. If it asks for the type,
   choose **Integration**.
3. Install **Live Track Ships**.
4. Restart Home Assistant. The Marketplace offers the restart as a repair in
   **Settings > System > Repairs**.

### By hand

1. Download the source code of the
   [latest release](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest).
2. Copy its `custom_components/live_track_ships` folder into the
   `custom_components` folder of your Home Assistant configuration directory.
3. Restart Home Assistant.

## Setup

**Settings > Devices & services > Add integration > Live Track Ships.** Each
area you add is one entry, titled *Ships near <latitude>, <longitude>*.

| Field | What it takes | Default |
|---|---|---|
| Data source | aisstream.io, Fintraffic Digitraffic or BarentsWatch AIS Live | aisstream.io |
| API key | aisstream.io only. Filled in from an area you already set up; you can change it | empty |
| Client ID, Client secret | BarentsWatch only. Filled in from an area you already set up | empty |
| Centre | a marker on a map; drag it to the water you want to watch | your home |
| Radius (km) | 1 to 500 | 50 |
| Maximum vessels to track | 1 to 5,000; a safety limit for this area, nearest kept | 1,000 |

The same source cannot watch the same centre twice. When at least 5% of a
BarentsWatch circle lies outside the waters BarentsWatch publishes, the dialog
says how much before the area is created; submit to keep that circle anyway.

**Settings of an area** (Configure on its entry): the centre, on the same map
marker; the radius; the maximum vessels to track; and *Maximum vessels on the
map, all Live Track Ships entries together*, a slider from 100 to 2,500 in
steps of 100 (default 2,500). Moving the centre renames the area to its new
position and reloads it. The same source still cannot watch one centre from
two areas.

## What it creates

- **One `geo_location` entity per vessel**, `geo_location.vessel_<MMSI>`, whose
  state is its distance from the area's centre in kilometres. Attributes
  include the name, MMSI, call sign, speed, course, heading, length, beam,
  vessel type, destination, `object_kind`, `last_seen` and `attribution`, each
  only when the source sent it. A vessel seen by two areas is one entity.
- **One sensor per area**, `sensor.ships_in_range`, counting the vessels shown,
  and saying so when the area's or the instance's ceiling clips the list.

A vessel heard outside your circle leaves the map at once. To hear that, each
source is asked for a ring a little wider than your circle (10%, at least
1 km); only vessels inside your circle are kept. A vessel that is not heard
again leaves after a period of silence, and a vessel that stops appearing has
not necessarily left (below).

## Events: a ship comes into your area, or leaves it

Each area fires two Home Assistant events, so an automation can tell you when
a ship you care about arrives:

- `live_track_ships_entry` when a vessel comes into the area's circle
- `live_track_ships_exit` when it leaves

The integration announces every vessel; your automation picks the ones that
matter. The event data uses the same names and units as the vessel's
attributes, and leaves out whatever the source did not send:

| Field | What it holds |
|---|---|
| `area_id`, `area` | the area's config entry ID and its title |
| `identity` | the MMSI |
| `name`, `call_sign`, `imo` | when sent |
| `object_kind` | `vessel`, `net_buoy`, `aton`, `base_station`, `sar_aircraft` or `distress_beacon` |
| `ship_type`, `ship_type_label`, `length_m`, `beam_m`, `draught_m`, `destination`, `nav_status` | vessels only, when sent |
| `speed_kmh`, `course_deg`, `heading_deg` | when sent |
| `latitude`, `longitude`, `distance_km`, `bearing_from_centre_deg`, `last_seen` | where it was heard, from the area's centre |
| `entity_id` | entry only: `geo_location.vessel_<MMSI>`, when the vessel is on the map |
| `reason` | exit only: `left` (heard outside the circle) or `silent` (not heard for the retention window, so it may still be there) |

Four things to know:

- **An arrival is announced only if the vessel was heard outside the circle
  first**, in the ring around it. A vessel first heard inside may have been
  there all along: after a restart the receivers keep delivering vessels that
  never moved for many minutes. So a vessel the receivers missed on its way
  in, or one that switches its transponder on inside, is not announced.
- **A departure heard outside is always announced**, even for a vessel that
  was there before Home Assistant started. A vessel that goes silent is
  announced as leaving (`reason: silent`) only if its arrival was.
- **An exit waits 2 minutes.** A vessel that comes back inside sooner, along
  the edge of the circle, is not announced as leaving and arriving again.
- **Details may be missing on arrival.** Name, type and size travel in a
  slower message than position (above). A vessel heard for the first time can
  arrive with a position and nothing else; one heard before usually carries
  its type and size.

Two areas over the same water each fire their own events. The map's limits on
how many vessels are drawn never make a vessel enter or leave.

An automation that tells you when a ship over 150 m comes into an area:

```yaml
triggers:
  - trigger: event
    event_type: live_track_ships_entry
conditions:
  - condition: template
    value_template: "{{ trigger.event.data.length_m | default(0) > 150 }}"
actions:
  - action: notify.notify
    data:
      title: "{{ trigger.event.data.name | default('A ship') }}"
      message: >-
        {{ trigger.event.data.ship_type_label | default('Vessel') }},
        {{ trigger.event.data.length_m }} m,
        {{ trigger.event.data.distance_km }} km away, entering
        {{ trigger.event.data.area }}.
```

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
downgrade. A card you installed through the Marketplace is left alone. Removing
the last area of this integration hands the row to another Live Track
integration, or removes it if none is left. See the card's README, section
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

If the integration's files are removed (through the Marketplace, say) while its
areas are still set up, and no other Live Track integration is installed,
nothing is left to tidy the row: remove it in Settings > Dashboards >
Resources. To install the card by hand instead, follow the card's README; the
resource row of a hand-installed copy under `/local/` is pointed at an
integration's copy only when that copy is a newer release.

Give it the vessels with
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities),
filtering on `domain: geo_location` and
`attributes: {source: live_track_ships}`. With other Live Track integrations
installed, add one filter for each of their sources.

Any other map card that shows `geo_location` entities shows the vessels too,
without the card's pictures and slides.

A vessel on the public [EnforcementVessels](https://github.com/StrausbergAutomationWorks/EnforcementVessels)
list (Coast Guard vessels used in immigration work) is drawn in the Coast
Guard's colours with the list's name and agency, wherever it is.

## Where it looks

You put a **centre and a radius** on the map. The centre can be anywhere in
the world; the radius can be 1 to 500 km. The default is **50 km**. Each
vessel's state is its distance from your centre.

How many vessels a circle contains depends far more on *which water* than on
*how big*. In testing, a 50 km circle held about 4 vessels over Chicago and
about 340 over the Solent in southern England: the same radius, roughly 80
times the traffic. So the integration keeps at most a set number of vessels
(1,000 by default, adjustable up to 5,000), keeps the nearest when there are
more, and says so on its `ships_in_range` sensor.

All your areas **together** show at most 2,500 vessels, whatever their
sources. Each area's settings have the slider above, which can only lower that
ceiling; the lowest setting on any enabled area applies. Lower it on slower
hardware.

## Coverage, measured rather than promised

Coverage is good where receivers are and absent where they are not, and **no
configuration can create coverage that does not exist**.

Measured on 2026-09-02 around Chicago, on aisstream.io:

- **Great Lakes**: 100 distinct vessels in 120 seconds, all five lakes plus
  the connecting waters.
- **Chicago River, downtown**: busy and reliable.
- **Chicago Sanitary and Ship Canal, Cal-Sag Channel, Calumet River**: one
  hour of listening, **zero vessels**. The canal is not empty: its tows are
  visible on commercial services via satellite AIS, which free aggregators do
  not carry. The traffic is real; the terrestrial coverage is not.

No vessels in your area may mean no receivers rather than no boats. Check that
your source covers your water before assuming the integration is broken.

A vessel that stops appearing has not necessarily left. None of these sources
guarantees delivery, so the integration shows when each vessel was last heard
and removes it only after a period of silence.

## Ships worth their own picture

Most vessels are drawn by type. Some get their own picture: royal and state
yachts, and well-known boats such as Chicago's tour boats, water taxis and
fireboats. Know a ship that deserves one, anywhere in the world? Open an issue
at <https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues> with
its name and MMSI or IMO number, and a photo or a link if you have one.

## Languages

This README: **English**, [Deutsch](README.de.md), [Français](README.fr.md),
[Nederlands](README.nl.md), [简体中文](README.zh-Hans.md),
[Español](README.es.md), [Italiano](README.it.md), [Dansk](README.da.md) and
[Kalaallisut](README.kl.md) (a draft, sent to Oqaasileriffik, Greenland's
language secretariat, for review; until then the Danish page is the reliable
one). The README is translated into a short list of languages: the ones most
Home Assistant users read, and a few more where there is a solid reason. The
English one is the full reference.

The setup dialog and the area's settings appear in your Home Assistant
language when it is one of these: English, Dansk, Deutsch, Español, Français,
Gaeilge, Íslenska, Italiano, Nederlands, Norsk Bokmål, Polski, Português,
Português (BR), Suomi, Svenska and 简体中文. Any other language shows the
English dialog. Kalaallisut is not a Home Assistant language yet; we have
asked Home Assistant to add it, and the dialog will follow once it can be
shown.

Found a mistake in a translation that changes the meaning or reads badly?
Please tell us at <https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues>.
The translations were written for this project and not all of them have been
read by a native speaker yet.

**Struggling to follow this in any of these languages?** Ask for another one at
the same address, and we will try to accommodate you.

## Part of Live Track

Live Track is a set of Home Assistant integrations, one per kind of moving
thing, all drawing on the same map. They share a Python library
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore))
and the map card, so installing another one adds no requests to a shared
source. Released:
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft),
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
[Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail),
[Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail)
and Live Track Ships. Each works on its own.

## Not affiliated

Not affiliated with aisstream.io, Fintraffic, BarentsWatch, MarineTraffic,
VesselFinder, any vessel operator, or any maritime authority. AIS is a
safety-of-navigation system; **this integration is for interest and is not for
navigation, collision avoidance, or any operational purpose.**

## Licence

Code: MIT, in [LICENSE](LICENSE). Data and artwork credits:
[ATTRIBUTION.md](ATTRIBUTION.md).

## Keywords

Home Assistant AIS · ship tracking · vessel tracker · boat tracker · marine
traffic map · AIS map card · aisstream.io · Digitraffic · BarentsWatch ·
geo_location · HACS integration
