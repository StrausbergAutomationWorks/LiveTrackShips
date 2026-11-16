# Attribution

Live Track Ships reads AIS data at runtime, from the one source each area is
set up with. Nothing from any of these sources is shipped in this repository.
Every vessel entity, and each area's `ships_in_range` sensor, carries an
`attribution` with the credit line below for its source; Home Assistant shows
it in the entity's details. If you show this data to others, for example on a
public dashboard, keep that credit with it and read the source's own terms.

## aisstream.io

Streamed from [aisstream.io](https://aisstream.io) with the user's own account
and API key. aisstream.io publishes no terms of use. Credit line:

> Data: aisstream.io (https://aisstream.io)

## Fintraffic Digitraffic (CC BY 4.0)

Polled from [Fintraffic Digitraffic](https://www.digitraffic.fi/en/marine-traffic/),
licensed under [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/).
Terms: <https://www.digitraffic.fi/en/terms-of-service/>. Fintraffic asks for
its own wording and a notice when the data is changed; Live Track Ships changes
it (units converted, only vessels inside your circle), so the line says so:

> Source: Fintraffic / digitraffic.fi (https://www.digitraffic.fi/en/marine-traffic/),
> license CC 4.0 BY (https://creativecommons.org/licenses/by/4.0/). Changed by
> Live Track Ships: units converted, limited to your circle.

## BarentsWatch (NLOD)

Streamed from [BarentsWatch AIS](https://www.barentswatch.no/en/) with the
user's own client registration, under the
[Norwegian Licence for Open Government Data (NLOD) 2.0](https://data.norge.no/nlod/en/2.0).
Terms: <https://www.barentswatch.no/en/articles/api-terms-and-conditions/>.
NLOD asks that the licensor be named and changes be indicated:

> Contains data under the Norwegian licence for Open Government data (NLOD)
> (https://data.norge.no/nlod/en/2.0) distributed by BarentsWatch
> (https://www.barentswatch.no). Changed by Live Track Ships: units converted,
> limited to your circle.

## Your own receiver

Received over UDP from the user's own AIS receiver, and decoded with
[pyais](https://github.com/M0r13n/pyais) (MIT), which Home Assistant installs
as a requirement. Nobody else's data, so no licence applies. Credit line:

> Data: your own AIS receiver

## The EnforcementVessels list (ODbL v1.0)

A vessel on the list is drawn with the list's look, name and agency, and its
entity carries the list's credit. The list is read through the `saw-livetrack`
library; this repository does not copy it.

Contains information from [EnforcementVessels](https://github.com/StrausbergAutomationWorks/EnforcementVessels),
which is made available under the [Open Database License (ODbL) v1.0](https://opendatacommons.org/licenses/odbl/1-0/).

## Vessel types

The labels in `custom_components/live_track_ships/ship_types.py` name the AIS
ship-type codes of ITU-R M.1371. The icon chosen for each code follows the US
Coast Guard's AIS Encoding Guide, a US government publication. Both are used
as references; no text from either is copied.

## Icons and artwork

Every vessel, buoy and aircraft picture in `custom_components/live_track_ships/icons/`
was drawn for StrausbergAutomationWorks and is under the MIT licence in
`LICENSE`. The state vessels carry their countries' flags, drawn from the
flags' published proportions and colours. The named boats are drawn in their
operators' colours to tell them apart on the map; no operator's logo or
lettering is reproduced, and none of these operators endorses this project.

The brand icon in `custom_components/live_track_ships/brand/` is the
StrausbergAutomationWorks logo with a container ship drawn for
StrausbergAutomationWorks.

## The map card

`custom_components/live_track_ships/frontend/live-track-map-card.js` is a
released build of [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)
(MIT), committed byte for byte. The notices for the packages bundled in it are
in the file's first lines.

## The code

MIT, in `LICENSE`.
