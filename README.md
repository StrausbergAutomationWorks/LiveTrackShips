# Live Track Ships

**AIS ship, boat and vessel tracking for Home Assistant.** Part of Live Track —
ships, aircraft and trains on one map.

Live marine AIS data from [aisstream.io](https://aisstream.io), shown as Home
Assistant entities and map markers.

**Status: in design. Not yet functional.**

## What AIS actually is, and what this shows

AIS — Automatic Identification System — is a VHF broadcast that vessels use to
announce their position, identity and voyage to each other and to shore. It is
the marine equivalent of ADS-B.

The feed carries more than ships, and this integration is explicit about that
rather than quiet:

| In the feed | Shown |
|---|---|
| Cargo ships, tankers, tugs, ferries, passenger vessels | yes |
| Recreational craft and sailboats broadcasting Class B | yes |
| Aids to navigation — buoys, beacons, lighthouses | if your source sends them |
| AIS shore base stations | if your source sends them |
| Search-and-rescue (SAR) aircraft | if your source sends them |

**Nothing is filtered out.** The integration passes through whatever the source
publishes, so if a source starts sending aids to navigation or shore stations
they simply appear — no update, no setting to find.

In practice the cloud feed sends only vessels. Measured over 11 captures
including 15 minutes covering the whole Great Lakes, **only five message types
ever arrived**, all of them vessel positions and vessel details. Buoys, base
stations and SAR aircraft were never seen once.

A local receiver is different — it hears everything on the air, so those
categories would show up.

Buoys, beacons and shore stations exist to serve shipping, so they are
navigational context rather than separate features — hence the name.

## Where it looks

You give it a **latitude, a longitude and a radius**. That's it. The centre can
be anywhere in the world.

The default is a **50 km** circle. Vessels are listed nearest first, with their
distance from your centre point.

⚠ **There is a limit, and it exists for a measured reason.** How many vessels a
circle contains depends far more on *which water* than on *how big*. In testing,
a 50 km circle held about 4 vessels over Chicago and about 340 over the Solent
in southern England — the same radius, roughly 80× the traffic. So the
integration caps both the radius it will request and the number of vessels it
will track, and tells you when it is showing you the nearest few rather than
all of them.

## Coverage, measured rather than promised

aisstream.io aggregates receivers contributed by volunteers and operators. Its
coverage is good where people run receivers and absent where they do not, and
**no configuration can create coverage that does not exist**.

Measured on 2026-09-02 around Chicago:

- **Great Lakes** — 100 distinct vessels in 120 seconds, all five lakes plus
  the connecting waters. Good coverage.
- **Chicago River, downtown** — busy and reliable.
- **Chicago Sanitary and Ship Canal, Cal-Sag Channel, Calumet River** — one
  hour of listening, **zero vessels**. Not because the canal is empty: the
  tows there are visible on commercial services via satellite AIS, which free
  aggregators don't carry. The traffic is real; the terrestrial coverage isn't.

The lesson generalises. Absence of vessels in your area may mean absence of
receivers rather than absence of boats, and no configuration setting can fix
that. Check that the feed covers your water before assuming the integration is
broken.

## Requirements

- A free API key from [aisstream.io](https://aisstream.io/account)
- Home Assistant with outbound websocket access

⚠ aisstream allows **three connections per account and three per public IP**.
If you run other tools against the same key, budget for it.

## Not affiliated

Not affiliated with aisstream.io, MarineTraffic, VesselFinder, or any maritime
authority. AIS is a safety-of-navigation system; **this integration is for
interest and is not for navigation, collision avoidance, or any operational
purpose.**

## Licence

MIT.
