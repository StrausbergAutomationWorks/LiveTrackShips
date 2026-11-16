# Live Track Ships

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · **Nederlands** · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Kalaallisut](README.kl.md)

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
| BarentsWatch AIS Live | Noorse wateren | gratis client-ID en secret |

Het attribuut `attribution` van elk schip noemt de bron. Alle
bronvermeldingen: [ATTRIBUTION.md](ATTRIBUTION.md).

De dekking is goed waar ontvangers staan, en geen instelling maakt dekking die
er niet is. Zie je geen schepen in je gebied, dan kan het aan ontbrekende
ontvangers liggen en niet aan ontbrekende boten. Op de Noordzee en in de
Nederlandse en Belgische havens en rivieren hangt aisstream.io af van
vrijwillige ontvangers.

## Vereisten

- Home Assistant 2026.11 of nieuwer.
- aisstream.io: een gratis API-sleutel van
  [aisstream.io](https://aisstream.io/account). aisstream staat drie
  verbindingen toe per account en per openbaar IP-adres.
- BarentsWatch: gratis client-ID en secret. Vul de client-ID precies in zoals
  hij is uitgegeven.
- Digitraffic heeft geen sleutel of account nodig.

## Installatie

### Via de Marketplace

De integratie staat nog niet in de catalogus van de Marketplace. Voeg haar
toe via een link:

1. **Instellingen > Marketplace** en **Toevoegen via link**.
2. Vul `StrausbergAutomationWorks/LiveTrackShips` in. Vraagt hij om het type,
   kies dan **Integratie**.
3. Installeer **Live Track Ships**.
4. Herstart Home Assistant. De Marketplace biedt de herstart aan als reparatie
   onder **Instellingen > Systeem > Reparaties**.

### Met de hand

1. Download de broncode van de
   [nieuwste release](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest).
2. Kopieer de map `custom_components/live_track_ships` naar de map
   `custom_components` in de configuratiemap van Home Assistant.
3. Herstart Home Assistant.

## Instellen

**Instellingen > Apparaten en diensten > Integratie toevoegen > Live Track
Ships.** Kies de bron, vul zo nodig de sleutel in, sleep de markering op de
kaart naar het water dat je wilt volgen en kies de straal (1 tot 500 km,
standaard 50). Elk gebied is een eigen item. Het venster verschijnt in het
Nederlands als Home Assistant in het Nederlands staat.

In de instellingen van een gebied kun je het middelpunt verplaatsen met
dezelfde markering; het gebied krijgt dan een nieuwe naam en wordt opnieuw
geladen. Alle gebieden samen tonen hoogstens 2.500 schepen; een schuifregelaar
in de instellingen kan dat plafond alleen verlagen. Gebruik die op tragere
hardware.

## Gebeurtenissen: een schip komt je gebied in of gaat eruit

Elk gebied vuurt twee gebeurtenissen af in Home Assistant: `live_track_ships_entry` wanneer een schip
de cirkel in komt, en `live_track_ships_exit` wanneer het eruit gaat. De integratie meldt elk
schip; jouw automatisering kiest de schepen die voor jou tellen, bijvoorbeeld
op naam, type, lengte of snelheid. De velden hebben dezelfde namen en eenheden
als de attributen van het schip; de lijst en een voorbeeld staan in de
[Engelse README](README.md#events-a-ship-comes-into-your-area-or-leaves-it).

- Een aankomst wordt alleen gemeld als het schip eerst buiten de cirkel is
  gehoord, in de ring eromheen. Een schip dat eerst binnen wordt gehoord, kan
  er al die tijd hebben gelegen; een schip dat de ontvangers op weg naar
  binnen niet hoorden, wordt daarom niet gemeld.
- Vertrek dat buiten de cirkel wordt gehoord, wordt altijd gemeld. Een schip
  dat stil valt, wordt alleen als vertrokken gemeld als zijn aankomst gemeld
  is.
- Vertrek wordt pas na 2 minuten gemeld; een schip dat eerder terugkomt, wordt
  niet gemeld als vertrokken en weer aangekomen.
- Bij aankomst kunnen naam, type en afmetingen ontbreken, omdat die minder vaak
  worden uitgezonden dan de positie.

## Schepen die een eigen afbeelding verdienen

De meeste schepen worden getekend naar hun type. Sommige hebben een eigen
afbeelding: koninklijke en staatsjachten, en bekende boten zoals de
rondvaartboten, watertaxi's en blusboten van Chicago. Ken je een schip dat er
een verdient, waar ook ter wereld? Maak een issue aan op
<https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues> met de
naam en het MMSI- of IMO-nummer, en een foto of link als je die hebt.

Een belangrijke fout gevonden in deze vertaling of in het Nederlandse venster?
Laat het ons op hetzelfde adres weten.

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

## Gegevens en licentie

De schepen worden gelezen terwijl de integratie draait, rechtstreeks van de
gekozen bron; deze repository bevat geen gegevens van die bronnen. Code: MIT.

Niet verbonden aan aisstream.io, Fintraffic, BarentsWatch of een maritieme
autoriteit. **Niet voor navigatie of het vermijden van aanvaringen.** Alle
details en talen: [README in het Engels](README.md#languages).

## Trefwoorden

Home Assistant AIS · schepen op de kaart · scheepsvolger · boten volgen ·
scheepvaartverkeer live · AIS-kaart · HACS-integratie
