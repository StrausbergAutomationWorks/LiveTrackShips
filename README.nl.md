# Live Track Ships

[English](README.md) · [Suomi](README.fi.md) · [Svenska](README.sv.md) · [Norsk](README.nb.md) · [Español](README.es.md) · **Nederlands** · [Gaeilge](README.ga.md)

Schepen, boten en andere vaartuigen live op de kaart van Home Assistant. Live
Track Ships is een Home Assistant-integratie (custom component, te installeren
via de Marketplace / HACS) die de AIS-gegevens toont van de schepen in het
gebied dat je kiest: waar elk schip is, de naam, snelheid, koers, het type en
de afmetingen als het schip die uitzendt. Elk schip is een
`geo_location`-entiteit die over de kaart beweegt als er nieuwe posities
binnenkomen. Het middelpunt van het gebied kan overal ter wereld liggen.

**Status: 0.1.0, de eerste release.**

## Ook pleziervaartuigen zijn zichtbaar

De integratie toont alles wat de bron stuurt, en er valt niets weg te filteren.
Een pleziervaartuig met een AIS-transponder staat op de kaart net als een
vrachtschip: naam, MMSI, roepletters en positie tot op ongeveer een meter. Een
boot die de transponder aan laat in de haven, blijft op de kaart in de haven
liggen. Voor AIS bestaat geen opt-outlijst. Wil je minder pleziervaartuigen op
de kaart, maak de straal dan kleiner.

## Bronnen

Je kiest één bron per gebied.

| Bron | Dekking | Nodig |
|---|---|---|
| aisstream.io | de hele wereld, waar vrijwilligers ontvangers hebben | een gratis API-sleutel |
| Fintraffic Digitraffic | Finse wateren en de Oostzee | niets |
| BarentsWatch AIS Live | Noorse wateren | gratis client ID en secret |

Het attribuut `attribution` van elk schip noemt de bron. Alle
bronvermeldingen: [ATTRIBUTION.md](ATTRIBUTION.md).

De dekking is goed waar ontvangers staan, en geen instelling maakt dekking die
er niet is. Zie je geen schepen in je gebied, dan kan het aan ontbrekende
ontvangers liggen en niet aan ontbrekende boten. Op de Noordzee en in de
Nederlandse havens en rivieren hangt aisstream.io af van vrijwillige
ontvangers.

## Onderdeel van Live Track

Live Track is een reeks Home Assistant-integraties, één per soort ding dat
beweegt, die allemaal op dezelfde kaart tekenen
([LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
die met de integratie wordt geïnstalleerd). Uitgebracht:
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft),
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
[Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail),
[Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail)
en Live Track Ships. Elk werkt ook op zichzelf.

## Vereisten

- Home Assistant 2026.11 of nieuwer.
- aisstream.io: een gratis API-sleutel van
  [aisstream.io](https://aisstream.io/account). aisstream staat drie
  verbindingen toe per account en per openbaar IP-adres.
- BarentsWatch: gratis client ID en secret. Vul de client ID precies in zoals
  hij is uitgegeven.
- Digitraffic heeft geen sleutel of account nodig.

## Installatie

### Via de Marketplace

De integratie staat nog niet in de catalogus van de Marketplace. Voeg haar
toe via een link:

1. **Settings > Marketplace** en **Add from link**.
2. Vul `StrausbergAutomationWorks/LiveTrackShips` in. Vraagt hij om het type,
   kies dan **Integration**.
3. Installeer **Live Track Ships**.
4. Herstart Home Assistant. De Marketplace biedt de herstart aan als reparatie
   onder **Settings > System > Repairs**.

### Met de hand

1. Download de broncode van de
   [nieuwste release](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest).
2. Kopieer de map `custom_components/live_track_ships` naar de map
   `custom_components` in de configuratiemap van Home Assistant.
3. Herstart Home Assistant.

## Instellen

**Settings > Devices & services > Add integration > Live Track Ships.** Kies de
bron, vul zo nodig de sleutel in, sleep de markering op de kaart naar het water
dat je wilt volgen en kies de straal (1 tot 500 km, standaard 50). Elk gebied
is een eigen item. Het venster is in het Engels; de menunamen hierboven zijn
die van de Engelse interface.

Alle gebieden samen tonen hoogstens 2.500 schepen. De instellingen van elk
gebied hebben een schuifregelaar die dat plafond alleen kan verlagen; gebruik
die op tragere hardware.

## Gegevens en licentie

De schepen worden gelezen terwijl de integratie draait, rechtstreeks van de
gekozen bron; deze repository bevat geen gegevens van die bronnen. Code: MIT.

Niet verbonden aan aisstream.io, Fintraffic, BarentsWatch of een maritieme
autoriteit. **Niet voor navigatie of het vermijden van aanvaringen.** Alle
details: [README in het Engels](README.md).

## Trefwoorden

Home Assistant AIS · schepen op de kaart · scheepsvolger · boten volgen ·
scheepvaartverkeer live · AIS-kaart · HACS-integratie
