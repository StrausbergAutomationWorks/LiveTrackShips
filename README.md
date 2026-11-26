# Live Track Ships

**English** · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Kalaallisut](README.kl.md) · [All languages](#languages)

**Ships and boats for Home Assistant, on one map.** Live Track Ships puts
ships, boats and everything else that broadcasts AIS (the radio signal vessels
use to say where they are) on your Home Assistant map, near you or anywhere in
the world you choose. It also follows chosen vessels wherever they go, and
tells your automations when a ship comes into your area or leaves it.

> **Live Track Ships is one module of Live Track**, a family of Home Assistant
> integrations that draw everything that moves, and the weather it moves
> through, on one shared map: aircraft, ships, trains and weather. Install it
> on its own, or beside the other modules
> ([list below](#part-of-live-track-the-other-modules)).

> **Growing, and open to ideas.** Live Track Ships covers the whole world where
> volunteers run receivers, Finland and Norway in more detail, and your own
> receiver, today, and we are adding more data sources and countries. Is yours
> missing? [Suggest it](#help-it-grow), or add it yourself: we will help you do
> it.

**Status: 0.1.4, released.** In the Marketplace's catalog ([install it
below](#install-it-step-by-step)).

Original work by StrausbergAutomationWorks. Not affiliated with, or endorsed
by, aisstream.io, Fintraffic (Finland), BarentsWatch (Norway), Wikidata,
Wikimedia Commons, VesselFinder, MarineTraffic, any vessel operator, or any
maritime authority.

> ⚠ **Not a safety system.** It shows public data, often seconds old and
> sometimes minutes, and only what receivers happen to hear. It is not for
> navigation, collision avoidance or any other operational purpose. On the
> water, use your own AIS, radar, charts and VHF radio.

---

## Contents

1. [Everything it does](#everything-it-does)
2. [Where it works](#where-it-works)
3. [Part of Live Track: the other modules](#part-of-live-track-the-other-modules)
4. [Before you start](#before-you-start)
5. [Install it, step by step](#install-it-step-by-step)
6. [Set it up, step by step](#set-it-up-step-by-step)
7. [Free keys that switch on more, step by step](#free-keys-that-switch-on-more-step-by-step)
8. [Put the map on a dashboard](#put-the-map-on-a-dashboard)
9. [Use it in automations](#use-it-in-automations)
10. [Everything on the map, in detail](#everything-on-the-map-in-detail)
11. [All the entities it creates](#all-the-entities-it-creates)
12. [What it sends and downloads](#what-it-sends-and-downloads)
13. [Help it grow](#help-it-grow)
14. [Languages](#languages)
15. [Credits and licences](#credits-and-licences)
16. [Keywords](#keywords)

---

## Everything it does

### On the map, with nothing to set up

You add an **area**: a centre and a radius on the map, and one data source.
Everything below then appears in that area. Fintraffic Digitraffic (Finland)
and your own receiver need no key; aisstream.io and BarentsWatch (Norway) need
a free one ([below](#switched-on-by-your-own-free-key-or-account)).

| What | Where | From |
|---|---|---|
| **Vessels**: cargo ships, tankers, ferries, tugs, fishing boats, pleasure craft and sailboats, each with its own picture, turned to its heading | in each area | the source you choose |
| **Things that are not ships**: fishing-gear buoys, aids to navigation, AIS base stations, search-and-rescue aircraft and distress beacons | in each area, when the source sends them | the source you choose |
| **Photos and links**: a photo of the ship when one is known, and a link to the vessel on VesselFinder | every vessel with an IMO number or an MMSI | Wikidata and Wikimedia Commons |
| **Tracks**: where a vessel has been in the last 24 hours, drawn when you ask | every vessel | kept by your own Home Assistant |
| **Coast Guard vessels in immigration work**, drawn in the Coast Guard's colours | wherever they are heard | the public EnforcementVessels list |
| **Arrivals and departures**: an event for your automations when a vessel comes into an area or leaves it | in each area | worked out by your own Home Assistant |

### Switched on by your own free key or account

| Free key or account | What it adds |
|---|---|
| **aisstream.io** key | vessels anywhere in the world where volunteers run receivers; and **watched vessels**: chosen ships followed wherever they are, with an event when one arrives, departs, goes silent or changes its destination |
| **BarentsWatch** account (Norway) | vessels in Norwegian waters, Svalbard included, with names and vessel types on every position |

Each takes a few minutes to get: [step by step below](#free-keys-that-switch-on-more-step-by-step).

---

## Where it works

| Region | What you get | From | Needs |
|---|---|---|---|
| **The whole world** | vessels where volunteers run receivers: good near busy coasts and ports, thin or absent elsewhere | aisstream.io | a free key |
| **Europe**: Finland and the Baltic Sea | vessels in Finnish and Baltic waters, new positions every minute | Fintraffic Digitraffic (Finland) | nothing |
| **Europe**: Norway | vessels in Norwegian waters, Svalbard included, with names and types on every position | BarentsWatch (Norway) | a free account |
| **Your own receiver**: anywhere | everything your antenna hears, with no internet | your own AIS receiver | a receiver that sends NMEA over UDP |

You choose one source for each area. Which kinds of thing appear, how fresh
the positions are and how complete the vessel details are all depend on that
source.

⚠ **Coverage is good where receivers are, and absent where they are not.** No
setting can create coverage that does not exist. Measured on 2026-09-02 on
aisstream.io around Chicago (United States): 100 vessels in 120 seconds across
the Great Lakes, but zero vessels in one hour on the canals south of the city,
where tows do run: commercial services see them by satellite, which free
sources do not carry. **No vessels in your area may mean no receivers, not no
boats.** Check that your source covers your water before you decide that
something is broken.

⚠ **Your own receiver:**

* One area listens on one port. Two receivers need two ports.
* Everything the receiver hears inside your circle is shown, aids to
  navigation and base stations included. Its station sensor also counts what
  it hears outside the circle.
* A sentence carries no date, so a position's time is when Home Assistant
  received it.
* Rate of turn is not shown for this source.
* So far this is tested with recorded sentences sent over UDP, not with a
  receiver. If you try it with yours, [tell us how it went](#help-it-grow).

Not on the list? [Tell us](#help-it-grow). Where someone publishes the data
openly, we will look at adding it.

---

## Part of Live Track: the other modules

Live Track is a set of Home Assistant integrations, one per kind of moving
thing, all drawn on the same map card. Each works on its own; together they
make one live picture. They share the map card and a Python library
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
so installing another one adds no requests to a source another already reads.

| Module | What it puts on the map | Status |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | aircraft overhead from ADS-B, with routes and type icons | released |
| **Live Track Ships** | ships and boats from AIS, near you or anywhere (this module) | released |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | commuter trains in North America, Europe and Australia | released |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | intercity and long-distance trains in North America, Europe and Australia | released |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | immigration and federal law-enforcement aircraft and vessels, from public lists | released |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | weather, storms and natural hazards | released |
| [Live Track Internet](https://github.com/StrausbergAutomationWorks/LiveTrackInternet) | internet outages, submarine cables and terrestrial links | released |
| Live Track Stations | departure boards and "time to leave" alerts for every station | planned |
| Live Track Satellites | satellites passing overhead | planned |
| Live Track Freight Trains | freight and work trains where railways publish them | planned |
| Live Track Transit | city buses, trams, ferries and metro | planned |
| Live Track Intercity Buses | intercity and regional coaches | planned |
| Live Track Commuter Buses | commuter buses | planned |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | the shared map card every module draws on | released, installed with each module |

Everything is free and open source. Nothing is held back for sponsors.

---

## Before you start

* **Home Assistant** 2026.11 or later.
* **The Marketplace** (HACS) in your Home Assistant, to install and update it
  the easy way. Without it you can copy the files by hand.
* **Internet access** for Home Assistant, for the online sources and the
  photos. Your own receiver works without it.
* **A data source.** Digitraffic (Finland) and your own receiver need no
  account. aisstream.io and BarentsWatch (Norway) need a free key
  ([step by step](#free-keys-that-switch-on-more-step-by-step)).
* **Optional: your own AIS receiver.** The receiver, or the program that
  decodes it, sends NMEA sentences (`!AIVDM`) over UDP to your Home
  Assistant's address, on the same network. In AIS-catcher that is
  `-u <address> <port>`; in rtl-ais, `-h <address> -P <port>`; OpenCPN and
  Signal K add it as a UDP output connection. A receiver that plugs in by USB,
  such as a dAISy, needs one of those programs to pass its sentences on.
* Nothing to pay. No account is needed for Digitraffic or your own receiver;
  the free keys are needed only for aisstream.io and BarentsWatch.

---

## Install it, step by step

### From the Marketplace (recommended)

1. In Home Assistant, open **Settings → Marketplace** (HACS).
2. Search for **Live Track Ships** and open it.
3. Choose **Download** (or **Install**).
4. **Restart Home Assistant**: **Settings → System → Repairs** offers the
   restart, or use **Settings → System → Restart**.

If the search doesn't find it, add it by its link: choose **Add from link** (or
the three-dot menu → **Custom repositories**), enter
`StrausbergAutomationWorks/LiveTrackShips`, choose **Integration** if asked for
the type, then carry on from step 3.

The Marketplace then offers each new release as an update.

### By hand

1. Download the source code of the
   [latest release](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest).
2. Copy its `custom_components/live_track_ships` folder into the
   `custom_components` folder of your Home Assistant configuration folder
   (create `custom_components` if it is not there).
3. Restart Home Assistant.

---

## Set it up, step by step

1. Open **Settings → Devices & services**.
2. Choose **Add integration** (bottom right) and search for **Live Track Ships**.
3. Choose **Every vessel in an area**. (The other choice, **Chosen vessels,
   wherever they are**, follows a list of vessels anywhere: see
   [Watched vessels](#watched-vessels-chosen-ships-anywhere).)
4. **Data source**: choose one. If unsure: in Finland choose Fintraffic
   Digitraffic, which needs no key; in Norway, BarentsWatch; anywhere else,
   aisstream.io.
5. **API key** (aisstream.io), or **Client ID** and **Client secret**
   (BarentsWatch): paste them
   ([how to get them](#free-keys-that-switch-on-more-step-by-step)). An area
   you already set up fills them in for you.
6. **UDP port (your own receiver)**: only for your own receiver. Enter the port
   it sends to, from 1024 to 65535. Leave 10110 if you did not change it.
7. **Centre**: drag the marker to the middle of the water you want to watch.
   It starts at your home.
8. **Radius (km)**: from 1 to 500 km (0.6 to 310 miles). If unsure, keep
   50 km (31 miles).
9. **Maximum vessels to track**: keep 1,000 unless your machine is small.
10. Choose **Submit**.

That is all. Vessels appear within a minute or two, as the source sends them.
Vessel types and sizes fill in over the next several minutes. Each area is one
entry, titled *Ships near <latitude>, <longitude>*. Add more areas the same
way.

* The same source cannot watch the same centre twice.
* When at least 5% of a BarentsWatch circle lies outside the waters
  BarentsWatch publishes, the dialog says how much before the area is created.
  Choose **Submit** to keep that circle anyway.

### Change what it shows: the options

Open **Settings → Devices & services → Live Track Ships → Configure** (the cog)
on the area you want to change. Every option, in plain words:

| Option | What it does | Default |
|---|---|---|
| **Centre** | moves the area; it is renamed to its new position and reloads | your home |
| **Radius (km)** | how far from the centre vessels are shown, 1 to 500 km (0.6 to 310 miles) | 50 km (31 miles) |
| **Maximum vessels to track** | a safety limit for this area, 1 to 5,000; when there are more, the nearest are kept | 1,000 |
| **Maximum vessels on the map, all Live Track Ships entries together** | the ceiling for all your areas together, 100 to 2,500; lower it on a small machine; the lowest setting on any area applies | 2,500 |
| **UDP port (your own receiver)** | the port your receiver sends to; changing it reloads the area | 10110 |

How many vessels a circle holds depends far more on which water than on how
large it is. In testing, a 50 km (31 miles) circle held about 4 vessels over
Chicago (United States) and about 340 over the Solent (England): the same
radius, about 80 times the traffic. When a limit cuts the list, the area's
`sensor.ships_in_range` says so.

---

## Free keys that switch on more, step by step

All of these are free and personal: each person who installs Live Track Ships
gets their own. Paste each into the setup dialog when you add an area (step 5
of [Set it up](#set-it-up-step-by-step)).

### aisstream.io (vessels and watched vessels, the whole world)

1. Open <https://aisstream.io/account> and sign in. (The **API keys** link at
   the top of aisstream.io opens the same page.)
2. Create a new API key there.
3. Copy the key at once: aisstream.io shows it only once.
4. Paste it into **API key**.

⚠ aisstream.io allows three connections for each account and three for each
public internet address. Live Track Ships uses at most two: one for all your
areas, and one for your watched vessels, which it shares with Live Track SALT
if that is installed on the same key. If other programs use the same key or the
same internet connection, count them too.

### BarentsWatch (vessels in Norwegian waters, Norway)

1. Open <https://www.barentswatch.no/minside/> and create a user, or log in.
2. Under **API access (for developers)** (*API-tilgang (for utviklere)*),
   choose **New Client** (*Ny klient*).
3. Choose the AIS client, not the API client.
4. Copy the **client ID**. It looks like
   `your.email@example.com:live_track_ships`. Paste it exactly as shown into
   **Client ID**.
5. Copy the **client secret** into **Client secret**. It is shown only once; if
   you did not keep it, generate a new one.

---

## Put the map on a dashboard

The map is [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
the card every Live Track module draws on. **It is installed with Live Track
Ships**: nothing to download, nothing to copy, no resource to add.

1. Open a dashboard, choose the pencil (**Edit dashboard**), then **Add card**.
2. Scroll to the bottom and choose **Manual**.
3. Paste this, and choose **Save**:

```yaml
type: custom:live-track-map-card
entity_filter:
  include:
    - domain: geo_location
      attributes:
        source: live_track_ships
```

Other Live Track modules go in `entity_filter` the same way: one more
`- domain: geo_location` rule for each source.

**On the map:**

* Each vessel is drawn with its own picture, turned to its heading, and slides
  between its reported positions along the water rather than across the land.
* **Point at** a vessel to see its name, and its photo when there is one.
  **Click** it for its photo, its links, **Track** and **Details**
  ([Photos and links](#photos-and-links), [Tracks](#tracks)).
* The **filter card** (`custom:live-track-map-filter-card`) hides the vessel
  types you untick ([Hiding vessel types](#hiding-vessel-types)).

If your dashboards' resources are set in YAML (`lovelace: resource_mode: yaml`),
nothing can be registered for you: a **Repairs** issue then gives the exact
line to add. A card you installed yourself through the Marketplace is left
alone. If the integration's files are removed while its areas are still set
up, and no other Live Track module is installed, remove the card's row
yourself in **Settings → Dashboards → Resources**. Any other map card that
shows `geo_location` entities shows the vessels too, without their pictures.

---

## Use it in automations

Everything is an ordinary Home Assistant entity or event, so the automation
editor works with it, no code needed.

**A notification when a ship over 150 m (490 feet) comes into your area:**

1. **Settings → Automations & scenes → Create automation → Create new
   automation**.
2. **When**: **Add trigger**, search for **Manual event received**, and enter
   the **Event type** `live_track_ships_entry`.
3. **And if**: **Add condition** → **Template**, and enter this **Value
   template**: `{{ trigger.event.data.length_m | default(0) > 150 }}`
4. **Then do**: **Add action**, search for your phone's notification action
   (it carries your phone's name), and enter this message:

   ```text
   {{ trigger.event.data.name | default('A ship') }}, {{ trigger.event.data.length_m }} m, {{ trigger.event.data.distance_km }} km away
   ```

5. **Save**.

**Other ideas:** a light on when the evening ferry reaches your harbour in
Norway; a message when a family member's boat, a watched vessel, comes home
to Finland; a notification when the cruise ship you are meeting arrives in
Sydney (Australia); a dashboard count of ships in your harbour from
`sensor.ships_in_range`.

**The area events.** Each area fires `live_track_ships_entry` when a vessel
comes into its circle and `live_track_ships_exit` when it leaves. Every vessel
is announced; your automation picks the ones that matter. The fields use the
same names and units as the vessel's attributes, and leave out whatever the
source did not send:

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
| `reason` | exit only: `left` (heard outside the circle) or `silent` (not heard for a while, so it may still be there) |

⚠ Four things to know:

* **An arrival is announced only if the vessel was heard outside the circle
  first.** A vessel first heard inside may have been there all along: after a
  restart the sources keep delivering vessels that have not moved for many
  minutes. So a vessel the receivers missed on its way in, or one that switches
  its transponder on inside, is not announced.
* **A departure heard outside is always announced**, even for a vessel that
  was there before Home Assistant started. A vessel that goes silent is
  announced as leaving (`reason: silent`) only if its arrival was.
* **An exit waits 2 minutes.** A vessel that comes back inside sooner, along
  the edge of the circle, is not announced as leaving and arriving again.
* **Details may be missing on arrival.** Name, type and size travel in a
  slower message than position. A vessel heard for the first time can arrive
  with a position and nothing else.

Two areas over the same water each fire their own events. The limits on how
many vessels are drawn never make a vessel enter or leave.

**The watched-vessel event.** [Watched vessels](#watched-vessels-chosen-ships-anywhere)
fire one event, `live_track_ships_watched`, whose `change` says what happened:

| `change` | When |
|---|---|
| `arrived` | the vessel reports itself moored or at anchor, or, with no status, stays under 3.7 km/h (2 knots) |
| `departed` | it is under way again |
| `silent` | not heard for 30 minutes (6 hours if moored or at anchor); it leaves the map, and may still be there |
| `heard` | heard again after `silent` |
| `destination` | the crew changed its destination; `destination_previous` holds the old one |

The data carries `watch_id`, `watch`, `identity`, your `label`, and the same
vessel fields as the area events, with the distance and bearing from your home.
Arrived and departed wait until the new state has held for 5 minutes by the
vessel's own clock, so a boat drifting slowly does not switch back and forth.
Nothing is announced from a vessel's first position after a restart: that sets
the starting point. Destinations are typed by the crew and are often out of
date.

---

## Everything on the map, in detail

AIS (Automatic Identification System) is a VHF radio broadcast that vessels use
to announce their position, identity and voyage to each other and to the
shore. It is the marine version of what aircraft send as ADS-B. Commercial
vessels must carry it; many pleasure boats carry it by choice, usually as a
lower-powered Class B unit. AIS is broadcast openly: anyone with a receiver can
hear it, and public services pass it on. **Live Track Ships shows everything
the source sends.** Nothing is filtered out, and there is no setting to hide a
category from Home Assistant.

### Vessels

Each vessel is a marker whose state is its distance from the area's centre, in
kilometres. Most vessels are drawn by type: cargo ship, tanker, ferry, tug and
so on. Some get their own picture: royal and state yachts, and well-known
boats such as a city's tour boats, water taxis and fireboats. Know a ship that
deserves one, anywhere in the world? [Suggest it](#help-it-grow), with its name
and its MMSI or IMO number, and a photo or a link if you have one.

To see a vessel leave at once, each online source is asked for a ring a little
wider than your circle (10%, at least 1 km), and your own receiver sends
everything it hears. Only vessels inside your circle are kept: a vessel heard
outside leaves the map at once. A vessel that is not heard again leaves after
a period of silence. A vessel that stops appearing has not necessarily left:
none of these sources promises to deliver every message.

⚠ **Vessel type is often missing, especially for small boats.** Position and
name arrive with nearly every message. Type and size arrive in a separate,
slower message, and many Class B units rarely send it. Expect many vessels,
most small boats among them, to show no type or size, and expect all vessels
to have few details for several minutes after Home Assistant restarts. That is
the data, not a fault. Types and sizes once heard are kept across restarts.

The vessel's attributes include its name, MMSI, call sign, speed, course,
heading, length, beam, vessel type, destination, `object_kind`, `last_seen`
and `attribution`, each only when the source sent it. A vessel seen by two
areas is one entity.

### Private boats and sailboats

A pleasure boat that transmits AIS appears on your map exactly like a cargo
ship. Depending on what the boat broadcasts, its entity can carry:

* its **name**, which is also the label drawn on the map;
* its **MMSI** and **radio call sign**, both permanent and publicly searchable;
* its **position** to about a metre, its previous position, and when each was
  heard;
* its speed, course and heading, and its length, beam and type, when sent.

A boat that keeps its transponder on at the dock stays on the map at its berth
for as long as it transmits. Anyone who can open your map can also press
**Track** on such a boat and see where it has been over the last 24 hours (or
as long as you set), its berth included.

There is no opt-out list for AIS, as there is for aircraft, and this
integration does not invent one. If you want fewer private boats on your map,
make the radius smaller.

### Things that are not ships

Each entity carries `object_kind`: `vessel`, `net_buoy` (fishing-gear buoy),
`aton` (aid to navigation: a buoy, beacon or lighthouse), `base_station` (an
AIS station on shore), `sar_aircraft` (a search-and-rescue aircraft) or
`distress_beacon`. Most are told apart by the identity format the
International Telecommunication Union (ITU) gives them. Fishing-gear buoys are
not: they transmit with ship-style identities, so they are recognised by their
factory names (FISHING BOUY, NET MARK, BUOY) together with the absence of a
broadcast length.

Anything that is not a vessel is shown without a vessel type, size or
navigational status. Fishing-gear buoys drift with their lines, so they keep
their speed and course, and are drawn as a fish pointing the way they drift.

Which of these appear depends on the source. Measured on one evening:

| Source | Fishing-gear buoys | Search-and-rescue aircraft | Aids to navigation, base stations |
|---|---|---|---|
| BarentsWatch | yes | yes | none seen |
| Digitraffic | none seen | yes | none seen |
| aisstream.io | none seen | none seen | none seen |
| Your own receiver | whatever it hears | whatever it hears | whatever it hears |

aisstream.io delivered only vessel positions and vessel details, both over the
Great Lakes (North America) and over the same Norwegian and Danish waters
where BarentsWatch shows the buoys.

### Coast Guard vessels in immigration work

A vessel on the public
[EnforcementVessels](https://github.com/StrausbergAutomationWorks/EnforcementVessels)
list (United States Coast Guard vessels used in immigration work) is drawn in
the Coast Guard's colours, with the list's name and agency, wherever it is
heard.

### Watched vessels: chosen ships anywhere

Besides areas, you can follow a list of vessels wherever they are: a family
member's boat, a ferry you take, a cruise ship coming home. It needs an
aisstream.io key, and there is one such list for each Home Assistant.

1. Open **Settings → Devices & services**, choose **Add integration** and
   search for **Live Track Ships**.
2. Choose **Chosen vessels, wherever they are**.
3. **API key**: the key of an area you already set up is filled in.
4. **Vessels**: one vessel per line, its 9-digit MMSI, then a label of your
   own if you like:

   ```text
   244650000 Dad's boat
   366999999 The ferry
   ```

5. Choose **Submit**.

At most 100 vessels. aisstream.io follows at most 200 MMSIs for each key, and
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
if installed on the same key, uses part of that. A list that would go over is
refused when the entry loads, with the reason. To change the list, open the
entry's **Configure**.

A watched vessel is drawn on the map like any other, wherever it is heard, and
its state is its distance from your home. An area that already shows it keeps
it: one vessel, one marker. The entry adds `sensor.watched_vessels`: how many
of the listed vessels are heard now. Its `vessels` attribute lists every one of
them, with its label and its last known state. Its event is described under
[Use it in automations](#use-it-in-automations).

### Photos and links

When a vessel sends an IMO number and Wikidata knows a photo of that ship on
Wikimedia Commons, the vessel carries `marker_photo`. The map shows the photo
when you point at the vessel, with the photographer and the licence; a click
opens it larger, with links to the photo's page and to its licence. Every
vessel with an IMO number or an MMSI also carries `marker_links`, a link to
the vessel on VesselFinder. The popup's **Details** button opens the vessel's
usual dialog.

Your Home Assistant asks Wikidata and Commons itself, 20 IMO numbers at a
time, ten seconds apart, and keeps each answer for 30 days (14 days when there
is no photo) in `.storage/saw_vessel_photos.json`. Expect photos for about one
vessel in ten: on our test system, 49 of 521 IMO numbers had one.

⚠ A photo can show the ship under an earlier name: the IMO number belongs to
the hull and stays with it when the ship is renamed.

### Tracks

Every vessel also carries `marker_track`. Click a vessel and press **Track**
in its popup: the map draws where it has been, as one line ending at the
vessel, and the line grows while you watch. **Hide track** takes it off.
Nothing is drawn until you ask, so a busy port does not disappear under lines.

The track holds only positions the vessel reported while on your map, thinned
to one every 25 m (82 feet) or 10 minutes, and never two within 30 seconds.
Your Home Assistant keeps it in memory and saves it to
`.storage/saw_vessel_tracks.json`, so it survives a restart. It covers the last
24 hours. To keep more or less:

1. Open **Settings → Tools → Actions**.
2. Choose the action **Live Track Ships: Set track hours**.
3. Enter **Hours**, from 1 to 168 (one week), and choose **Perform action**.

It applies to every area at once; a shorter setting drops older positions
straight away.

⚠ The track starts empty on a first install. A vessel that left the area or
went quiet has a gap, drawn as a straight line between the positions on either
side.

### Hiding vessel types

Every vessel carries `marker_group`, `marker_group_label` and
`marker_group_order`: one of thirteen groups (cargo; tanker; passenger and
ferry; fishing; pleasure and sailing; tug, pilot and port service; government,
search and rescue and law enforcement; high speed and other; type not sent;
fishing-gear buoys; aids to navigation; base stations; search-and-rescue
aircraft). The map card's filter card, `custom:live-track-map-filter-card`,
lists the groups with how many of each are on the map, and hides the ones you
untick. Put it on any view of the dashboard. Your choice is kept in that
browser only.

Hiding is only on the map: the integration still counts every vessel and fires
its events for every vessel. A distress beacon has no group, so it is never
hidden.

---

## All the entities it creates

| Entity | What it is |
|---|---|
| `geo_location.vessel_<MMSI>` | one marker for each vessel or other AIS object; its state is the distance from the area's centre (or from your home, for a watched vessel), in kilometres. It comes and goes, and has no unique ID |
| `sensor.ships_in_range` | one for each area: how many vessels it shows, and whether a limit cut the list |
| `sensor.ais_station` | your own receiver only: messages per minute. Its attributes give `vessels_heard` (in the last 10 minutes), `farthest_km` and `farthest_mmsi` (from the area's centre), `last_message`, `udp_port`, `listening`, and `port_error` when the port cannot be opened. It updates every 30 seconds, so a receiver that stops sending shows 0 |
| `sensor.watched_vessels` | watched vessels only: how many of your listed vessels are heard now |

Attributes that change on every update are kept out of Home Assistant's
history, so your database does not grow with them: each vessel's
`marker_photo`, `marker_links` and `marker_track`, and the sensors'
fast-changing attributes.

**Your database.** Home Assistant's recorder stores a new row each time an
entity changes, and a moving vessel changes with every position it reports.
On our test system, one area with 43 vessels wrote 27,109 rows in about 30
hours, 8.8% of the whole database. By default the recorder keeps 10 days and
cleans up every night at 04:12 local time, so the growth levels off, but at a
size you may not want.

A vessel keeps the same entity ID, `geo_location.vessel_<MMSI>`, every time it
appears, so one pattern, `geo_location.vessel_*`, covers everything this
integration has ever put on the map. To keep only the last day of it:

1. **Settings → Automations & scenes → Create automation → Create new
   automation**.
2. Open the three-dot menu, choose **Edit in YAML**, replace everything with
   this, and choose **Save**:

```yaml
alias: Trim vessel history
triggers:
  - trigger: time
    at: "03:30:00"
actions:
  - action: recorder.purge_entities
    data:
      entity_globs:
        - geo_location.vessel_*
      keep_days: 1
```

If you leave out `keep_days` (default 0), all their rows go at once. To record
none of it, put the pattern under `recorder:` → `exclude:` → `entity_globs:`
in `configuration.yaml`; a map card set to draw history (`history_start`) then
has no trail to draw. `sensor.ships_in_range` is a plain count and cheap to
keep.

---

## What it sends and downloads

**About your location.** Each area's centre is your home unless you move it.
It goes only to the source you chose for that area: to aisstream.io as a
rectangle around a circle a little larger than yours (10%, at least 1 km); to
Digitraffic (Finland) as the centre and that larger radius; to BarentsWatch
(Norway) as that larger circle. For watched vessels, the MMSI numbers in your
list go to aisstream.io. Your own receiver sends nothing anywhere: Home
Assistant only listens. For photos, the IMO numbers of vessels on your map go
to Wikidata and Wikimedia Commons, with nothing about you. To stop all of
this, delete the area or the watched-vessels entry in **Settings → Devices &
services → Live Track Ships**. Nothing else about you is sent anywhere.

**How much.**

* **aisstream.io**: one connection for all your areas and one for your watched
  vessels, each kept open; vessels arrive as they report. After an error it
  reconnects after a pause.
* **Digitraffic**: positions every 60 seconds and vessel details every 15
  minutes, for your circle only. After an error it tries again at the next
  turn.
* **BarentsWatch**: one stream kept open for each area. If nothing arrives for
  150 seconds, it reconnects.
* **Photos**: 20 IMO numbers at a time, 10 seconds apart, only for vessels not
  asked about in the last 30 days (14 when there was no photo). A failed
  request is asked again later.
* **Your own receiver**: nothing is downloaded.

---

## Help it grow

Live Track Ships is still growing. We add data sources and countries as we find
them, and we want to know what you would like next.

### Suggest something

Is your country or AIS service missing? Is something wrong, or hard to
understand? Tell us whichever way is easier for you:

* [**Fill in a short form**](https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues/new?template=en.yml)
  in English. You need a free GitHub account.
* **Write an email** to
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  No account needed.

Either way, it helps to tell us:

* what you would like to see, and where in the world;
* a link to where the data is published, if you know one (an open-data page,
  a public feed, a service's website): not needed, but it helps;
* your Home Assistant language, if the problem is the wording or a
  translation.

Write in English or in your own language, whichever is easier for you.

### Add it yourself, with our help

If you would like to add something yourself, we will help you do it, from
the first question to the finished release. You do not need to be a
developer to start:

* **A translation.** The words in the setup dialog are a short list of
  phrases in one text file. We will show you which file and which lines.
* **A new data source.** Tell us where the data is published. We can write
  the code together, or look over yours.
* **Testing where you live.** Install it, look at your part of the map, and
  tell us what is right and what is not.
* **A fix to this README.** If a step did not match what you saw, tell us
  what you saw.

[**Tell us what you have in mind**](https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues/new?template=en.yml)
or write to
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
and we will reply with the next steps.

---

## Languages

This README: **English**, [Deutsch](README.de.md), [Français](README.fr.md),
[Nederlands](README.nl.md), [简体中文](README.zh-Hans.md),
[Español](README.es.md), [Italiano](README.it.md), [Dansk](README.da.md) and
[Kalaallisut](README.kl.md) (a short draft, sent to Oqaasileriffik,
Greenland's language secretariat, for review; until then the Danish page is
the reliable one). Each translated README is complete.

The setup dialog and the options appear in your Home Assistant language when it
is one of these: English, Dansk, Deutsch, Español, Français, Gaeilge,
Íslenska, Italiano, Nederlands, Norsk Bokmål, Polski, Português, Português
(BR), Suomi, Svenska and 简体中文. Any other language shows English.
Kalaallisut is not a Home Assistant language yet; we have asked Home Assistant
to add it. The map card's own labels (**Track**, **Details**) are in English
in every language.

Found a mistake in a translation, or need another language? Tell us at
<https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues>, or
[translate it with our help](#add-it-yourself-with-our-help).

---

## Credits and licences

* **aisstream.io**: no published terms. <https://aisstream.io>
* **Fintraffic Digitraffic** (Finland): data under CC BY 4.0.
  <https://www.digitraffic.fi/en/terms-of-service/>
* **BarentsWatch** (Norway): data under the Norwegian Licence for Open
  Government Data (NLOD).
  <https://www.barentswatch.no/en/articles/api-terms-and-conditions/>
* **Your own receiver**: your own data.
* **Wikidata**: CC0. **Wikimedia Commons**: each photo under its own licence,
  shown with its photographer and licence.
* **VesselFinder**: linked only; nothing is fetched from it.
* **EnforcementVessels**: ODbL 1.0.
  <https://github.com/StrausbergAutomationWorks/EnforcementVessels>

What this integration changes: units are converted, and only vessels inside
your circle are kept. Every vessel entity, and each area's
`sensor.ships_in_range`, carries an `attribution` naming its source; Home
Assistant shows it in the entity's details. If you show this data to others,
for example on a public dashboard, keep the credit with it and read the
source's own terms. The exact credit lines, and the credits for the vessel
pictures, are in [ATTRIBUTION.md](ATTRIBUTION.md).

None of these organisations made or endorsed this integration.

**Code**: MIT, in [LICENSE](LICENSE).

**For developers:** AIS sentences from your own receiver are decoded by
[pyais](https://github.com/M0r13n/pyais) (MIT); Home Assistant installs
`saw-livetrack` and `pyais` itself the first time it loads the integration.
The tests in `tests/` each run on their own with Python; some need Home
Assistant installed, and the `*_live` tests need your own keys.

---

## Keywords

Home Assistant ships · Home Assistant AIS · ship tracking · vessel tracker ·
boat tracker · marine traffic map · AIS map card · AIS receiver · NMEA ·
AIS-catcher · aisstream.io · Digitraffic · BarentsWatch · Schiffsverfolgung ·
Schiffe Karte · suivi des navires · scheepvaart volgen · seguimiento de barcos ·
tracciamento navi · skibstrafik · skibe kort · 船舶追踪 · geo_location ·
map card · Lovelace · HACS · Marketplace · Live Track · LiveTrack ·
StrausbergAutomationWorks

---

**Acknowledgement.** StrausbergAutomationWorks acknowledges the Indigenous
peoples of every land and water on this map, all over the world, and pays its
respect to their Elders, past and present.
