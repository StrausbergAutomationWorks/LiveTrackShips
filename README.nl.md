# Live Track Ships

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · **Nederlands** · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Kalaallisut](README.kl.md) · [Alle talen](#talen)

**Schepen en boten voor Home Assistant, op één kaart.** Live Track Ships zet
schepen, boten en alles wat verder AIS uitzendt (het radiosignaal waarmee
schepen laten weten waar ze zijn) op je Home Assistant-kaart, bij jou in de
buurt of waar ook ter wereld. Het volgt ook gekozen schepen waar ze ook gaan,
en laat je automatiseringen weten wanneer een schip je gebied binnenvaart of
verlaat.

> **Live Track Ships is één module van Live Track**, een familie van Home
> Assistant-integraties die alles wat beweegt, en het weer waar het doorheen
> beweegt, op één gedeelde kaart tekenen: vliegtuigen, schepen, treinen en
> weer. Installeer het los, of naast de andere modules
> ([lijst hieronder](#onderdeel-van-live-track-de-andere-modules)).

> **Het groeit, en ideeën zijn welkom.** Live Track Ships dekt vandaag de hele
> wereld waar vrijwilligers ontvangers draaien, Finland en Noorwegen in meer
> detail, en je eigen ontvanger. We voegen meer gegevensbronnen en landen
> toe. Ontbreekt het jouwe? [Stel het voor](#help-het-groeien), of voeg het
> zelf toe: we helpen je daarbij.

**Status: 0.1.3, uitgebracht.** In de catalogus van de Marktplaats ([installeer
het hieronder](#installeren-stap-voor-stap)).

Eigen werk van StrausbergAutomationWorks. Niet verbonden aan, of
goedgekeurd door, aisstream.io, Fintraffic (Finland), BarentsWatch
(Noorwegen), Wikidata, Wikimedia Commons, VesselFinder, MarineTraffic, een
rederij of een maritieme autoriteit.

> ⚠ **Geen veiligheidssysteem.** Het toont openbare gegevens, vaak seconden
> oud en soms minuten, en alleen wat ontvangers toevallig horen. Het is niet
> bedoeld voor navigatie, het vermijden van aanvaringen of enig ander
> operationeel doel. Gebruik op het water je eigen AIS, radar, kaarten en
> marifoon.

---

## Inhoud

1. [Alles wat het doet](#alles-wat-het-doet)
2. [Waar het werkt](#waar-het-werkt)
3. [Onderdeel van Live Track: de andere modules](#onderdeel-van-live-track-de-andere-modules)
4. [Voordat je begint](#voordat-je-begint)
5. [Installeren, stap voor stap](#installeren-stap-voor-stap)
6. [Instellen, stap voor stap](#instellen-stap-voor-stap)
7. [Gratis sleutels die meer aanzetten, stap voor stap](#gratis-sleutels-die-meer-aanzetten-stap-voor-stap)
8. [De kaart op een dashboard zetten](#de-kaart-op-een-dashboard-zetten)
9. [Gebruiken in automatiseringen](#gebruiken-in-automatiseringen)
10. [Alles op de kaart, in detail](#alles-op-de-kaart-in-detail)
11. [Alle entiteiten die het aanmaakt](#alle-entiteiten-die-het-aanmaakt)
12. [Wat het verstuurt en downloadt](#wat-het-verstuurt-en-downloadt)
13. [Help het groeien](#help-het-groeien)
14. [Talen](#talen)
15. [Vermeldingen en licenties](#vermeldingen-en-licenties)
16. [Trefwoorden](#trefwoorden)

---

## Alles wat het doet

### Op de kaart, zonder iets in te stellen

Je voegt een **gebied** toe: een middelpunt en een straal op de kaart, en één
gegevensbron. Alles hieronder verschijnt dan in dat gebied. Fintraffic
Digitraffic (Finland) en je eigen ontvanger hebben geen sleutel nodig;
aisstream.io en BarentsWatch (Noorwegen) hebben een gratis sleutel nodig
([hieronder](#met-je-eigen-gratis-sleutel-of-account)).

| Wat | Waar | Van |
|---|---|---|
| **Schepen**: vrachtschepen, tankers, veerboten, sleepboten, vissersboten, plezierjachten en zeilboten, elk met een eigen afbeelding, gedraaid naar zijn koers | in elk gebied | de bron die je kiest |
| **Wat geen schip is**: boeien van vistuig, navigatiehulpmiddelen, AIS-basisstations, zoek- en reddingsvliegtuigen en noodbakens | in elk gebied, als de bron ze stuurt | de bron die je kiest |
| **Foto's en links**: een foto van het schip als er een bekend is, en een link naar het schip op VesselFinder | elk schip met een IMO-nummer of een MMSI | Wikidata en Wikimedia Commons |
| **Sporen**: waar een schip de laatste 24 uur is geweest, getekend als je erom vraagt | elk schip | bijgehouden door je eigen Home Assistant |
| **Kustwachtschepen in immigratiewerk**, getekend in de kleuren van de kustwacht | waar ze ook gehoord worden | de openbare lijst EnforcementVessels |
| **Aankomsten en vertrekken**: een gebeurtenis voor je automatiseringen als een schip een gebied binnenkomt of verlaat | in elk gebied | bepaald door je eigen Home Assistant |

### Met je eigen gratis sleutel of account

| Gratis sleutel of account | Wat het toevoegt |
|---|---|
| **aisstream.io**-sleutel | schepen overal ter wereld waar vrijwilligers ontvangers draaien; en **gevolgde schepen**: gekozen schepen, gevolgd waar ze ook zijn, met een gebeurtenis als er een aankomt, vertrekt, stil wordt of zijn bestemming wijzigt |
| **BarentsWatch**-account (Noorwegen) | schepen in Noorse wateren, Spitsbergen inbegrepen, met naam en scheepstype bij elke positie |

Elk heb je in een paar minuten: [stap voor stap hieronder](#gratis-sleutels-die-meer-aanzetten-stap-voor-stap).

---

## Waar het werkt

| Regio | Wat je krijgt | Van | Nodig |
|---|---|---|---|
| **De hele wereld** | schepen waar vrijwilligers ontvangers draaien: goed bij drukke kusten en havens, weinig of niets elders | aisstream.io | een gratis sleutel |
| **Europa**: Finland en de Oostzee | schepen in Finse en Baltische wateren, elke minuut nieuwe posities | Fintraffic Digitraffic (Finland) | niets |
| **Europa**: Noorwegen | schepen in Noorse wateren, Spitsbergen inbegrepen, met naam en type bij elke positie | BarentsWatch (Noorwegen) | een gratis account |
| **Je eigen ontvanger**: overal | alles wat je antenne hoort, zonder internet | je eigen AIS-ontvanger | een ontvanger die NMEA via UDP verstuurt |

Je kiest één bron per gebied. Welke soorten dingen verschijnen, hoe vers de
posities zijn en hoe volledig de scheepsgegevens zijn, hangt allemaal af van
die bron.

⚠ **De dekking is goed waar ontvangers staan, en ontbreekt waar ze niet
staan.** Geen instelling kan dekking maken die er niet is. Gemeten op
2026-09-02 met aisstream.io rond Chicago (Verenigde Staten): 100 schepen in
120 seconden op de Grote Meren, maar nul schepen in een uur op de kanalen ten
zuiden van de stad, waar wel duwbakken varen: commerciële diensten zien ze via
satellieten, en die hebben gratis bronnen niet. **Geen schepen in je gebied
kan betekenen: geen ontvangers, niet geen boten.** Controleer of je bron jouw
water dekt voordat je besluit dat er iets kapot is.

⚠ **Je eigen ontvanger:**

* Eén gebied luistert op één poort. Twee ontvangers hebben twee poorten nodig.
* Alles wat de ontvanger binnen je cirkel hoort wordt getoond,
  navigatiehulpmiddelen en basisstations inbegrepen. Zijn stationssensor telt
  ook wat hij buiten de cirkel hoort.
* Een zin draagt geen datum, dus de tijd van een positie is het moment waarop
  Home Assistant hem ontving.
* De draaisnelheid wordt voor deze bron niet getoond.
* Tot nu toe is dit getest met opgenomen zinnen die via UDP zijn verstuurd,
  niet met een ontvanger. Probeer je het met de jouwe,
  [laat ons weten hoe het ging](#help-het-groeien).

Staat het er niet bij? [Laat het ons weten](#help-het-groeien). Waar iemand de
gegevens open publiceert, kijken we of we ze kunnen toevoegen.

---

## Onderdeel van Live Track: de andere modules

Live Track is een reeks Home Assistant-integraties, één per soort bewegend
ding, allemaal getekend op dezelfde kaart. Elke werkt op zichzelf; samen
vormen ze één live beeld. Ze delen de kaart en een Python-bibliotheek
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
dus een extra module installeren voegt geen verzoeken toe aan een bron die een
andere al leest.

| Module | Wat het op de kaart zet | Status |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | vliegtuigen boven je via ADS-B, met routes en typesymbolen | uitgebracht |
| **Live Track Ships** | schepen en boten via AIS, bij jou in de buurt of overal (deze module) | uitgebracht |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | forensentreinen in Noord-Amerika, Europa en Australië | uitgebracht |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | intercity- en langeafstandstreinen in Noord-Amerika, Europa en Australië | uitgebracht |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | vliegtuigen en schepen van immigratie- en federale ordediensten, uit openbare lijsten | uitgebracht |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | weer, stormen en natuurgevaren | uitgebracht |
| Live Track Stations | vertrekborden en "tijd om te gaan"-meldingen voor elk station | gepland |
| Live Track Satellites | satellieten die over je heen trekken | gepland |
| Live Track Freight Trains | goederen- en werktreinen waar spoorwegen ze publiceren | gepland |
| Live Track Transit | stadsbussen, trams, veerboten en metro | gepland |
| Live Track Intercity Buses | intercity- en streekbussen | gepland |
| Live Track Commuter Buses | forensenbussen | gepland |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | de gedeelde kaart waarop elke module tekent | uitgebracht, met elke module geïnstalleerd |

Alles is gratis en open source. Niets wordt achtergehouden voor sponsors.

---

## Voordat je begint

* **Home Assistant** 2026.11 of nieuwer.
* **De Marktplaats** (HACS) in je Home Assistant, om het makkelijk te
  installeren en bij te werken. Zonder kun je de bestanden met de hand
  kopiëren.
* **Internettoegang** voor Home Assistant, voor de online bronnen en de
  foto's. Je eigen ontvanger werkt zonder.
* **Een gegevensbron.** Digitraffic (Finland) en je eigen ontvanger hebben
  geen account nodig. aisstream.io en BarentsWatch (Noorwegen) hebben een
  gratis sleutel nodig
  ([stap voor stap](#gratis-sleutels-die-meer-aanzetten-stap-voor-stap)).
* **Optioneel: je eigen AIS-ontvanger.** De ontvanger, of het programma dat
  hem decodeert, stuurt NMEA-zinnen (`!AIVDM`) via UDP naar het adres van je
  Home Assistant, op hetzelfde netwerk. In AIS-catcher is dat
  `-u <address> <port>`; in rtl-ais `-h <address> -P <port>`; OpenCPN en
  Signal K voegen het toe als UDP-uitgang. Een ontvanger die via USB wordt
  aangesloten, zoals een dAISy, heeft een van die programma's nodig om zijn
  zinnen door te geven.
* **Optioneel: auto-entities** uit de Marktplaats, om de markeringen op de
  kaart te zetten (zie
  [De kaart op een dashboard zetten](#de-kaart-op-een-dashboard-zetten)).
* Niets te betalen. Voor Digitraffic en je eigen ontvanger is geen account
  nodig; de gratis sleutels zijn alleen nodig voor aisstream.io en
  BarentsWatch.

---

## Installeren, stap voor stap

### Via de Marktplaats (aanbevolen)

1. Open in Home Assistant **Instellingen → Marktplaats** (HACS).
2. Zoek **Live Track Ships** en open het.
3. Kies **Downloaden** (of **Installeren**).
4. **Herstart Home Assistant**: **Instellingen → Systeem → Reparaties** biedt
   de herstart aan, of gebruik **Instellingen → Systeem → Herstart**.

Vindt de zoekfunctie het niet, voeg het dan toe via de link: kies **Toevoegen
via link** (of het menu met drie puntjes → **Aangepaste repositories**), voer
`StrausbergAutomationWorks/LiveTrackShips` in, kies **Integratie** als om het
type wordt gevraagd en ga daarna verder bij stap 3.

De Marktplaats biedt daarna elke nieuwe release als update aan.

### Met de hand

1. Download de broncode van de
   [nieuwste release](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest).
2. Kopieer de map `custom_components/live_track_ships` daarin naar de map
   `custom_components` in de configuratiemap van je Home Assistant (maak
   `custom_components` aan als die er niet is).
3. Herstart Home Assistant.

---

## Instellen, stap voor stap

1. Open **Instellingen → Apparaten en diensten**.
2. Kies **Voeg integratie toe** (rechtsonder) en zoek naar **Live Track
   Ships**.
3. Kies **Alle schepen in een gebied**. (De andere keuze, **Gekozen schepen,
   waar ze ook zijn**, volgt een lijst schepen overal: zie
   [Gevolgde schepen](#gevolgde-schepen-gekozen-schepen-overal).)
4. **Gegevensbron**: kies er een. Twijfel je: in Finland Fintraffic
   Digitraffic, dat geen sleutel nodig heeft; in Noorwegen BarentsWatch;
   overal elders aisstream.io.
5. **API-sleutel** (aisstream.io), of **Client-ID** en **Client-secret**
   (BarentsWatch): plak ze
   ([zo krijg je ze](#gratis-sleutels-die-meer-aanzetten-stap-voor-stap)).
   Een gebied dat je al hebt ingesteld vult ze voor je in.
6. **UDP-poort (eigen ontvanger)**: alleen voor je eigen ontvanger. Voer de
   poort in waarnaar hij stuurt, van 1024 tot 65535. Laat 10110 staan als je
   die niet hebt veranderd.
7. **Middelpunt**: sleep de markering naar het midden van het water dat je
   wilt volgen. Hij begint bij je huis.
8. **Straal (km)**: van 1 tot 500 km (0,6 tot 310 mijl). Twijfel je, houd
   50 km (31 mijl).
9. **Maximaal aantal gevolgde schepen**: houd 1.000, tenzij je machine klein
   is.
10. Kies **Verzend**.

Dat is alles. Schepen verschijnen binnen een minuut of twee, zoals de bron ze
stuurt. Scheepstypen en afmetingen komen er de minuten daarna bij. Elk gebied
is één item, met de titel *Ships near <latitude>, <longitude>*. Voeg meer
gebieden op dezelfde manier toe.

* Dezelfde bron kan hetzelfde middelpunt niet twee keer volgen.
* Ligt minstens 5% van een BarentsWatch-cirkel buiten de wateren die
  BarentsWatch publiceert, dan zegt de dialoog hoeveel, voordat het gebied
  wordt aangemaakt. Kies **Verzend** om die cirkel toch te houden.

### Wijzigen wat het toont: de opties

Open **Instellingen → Apparaten en diensten → Live Track Ships → Configureer**
(het tandwiel) bij het gebied dat je wilt wijzigen. Elke optie, in gewone
woorden:

| Optie | Wat het doet | Standaard |
|---|---|---|
| **Middelpunt** | verplaatst het gebied; het krijgt de naam van zijn nieuwe positie en wordt opnieuw geladen | je huis |
| **Straal (km)** | tot hoe ver van het middelpunt schepen worden getoond, 1 tot 500 km (0,6 tot 310 mijl) | 50 km (31 mijl) |
| **Maximaal aantal gevolgde schepen** | een veiligheidsgrens voor dit gebied, 1 tot 5.000; zijn er meer, dan worden de dichtstbijzijnde gehouden | 1.000 |
| **Maximaal aantal schepen op de kaart, alle Live Track Ships-items samen** | het plafond voor al je gebieden samen, 100 tot 2.500; verlaag het op een kleine machine; de laagste instelling van alle gebieden geldt | 2.500 |
| **UDP-poort (eigen ontvanger)** | de poort waarnaar je ontvanger stuurt; wijzigen laadt het gebied opnieuw | 10110 |

Hoeveel schepen een cirkel bevat, hangt veel meer af van welk water het is dan
van hoe groot hij is. Bij het testen bevatte een cirkel van 50 km (31 mijl)
ongeveer 4 schepen boven Chicago (Verenigde Staten) en ongeveer 340 boven de
Solent (Engeland): dezelfde straal, ongeveer 80 keer zoveel verkeer. Als een
grens de lijst inkort, zegt de `sensor.ships_in_range` van het gebied dat.

---

## Gratis sleutels die meer aanzetten, stap voor stap

Ze zijn allemaal gratis en persoonlijk: iedereen die Live Track Ships
installeert, krijgt zijn eigen. Plak elk in de instellingsdialoog als je een
gebied toevoegt (stap 5 van [Instellen](#instellen-stap-voor-stap)).

### aisstream.io (schepen en gevolgde schepen, de hele wereld)

1. Open <https://aisstream.io/account> en meld je aan. (De link **API keys**
   bovenaan aisstream.io opent dezelfde pagina.)
2. Maak daar een nieuwe API-sleutel aan.
3. Kopieer de sleutel meteen: aisstream.io toont hem maar één keer.
4. Plak hem in **API-sleutel**.

⚠ aisstream.io staat drie verbindingen per account toe en drie per openbaar
internetadres. Live Track Ships gebruikt er hoogstens twee: één voor al je
gebieden, en één voor je gevolgde schepen, die het deelt met Live Track SALT
als dat met dezelfde sleutel is geïnstalleerd. Gebruiken andere programma's
dezelfde sleutel of dezelfde internetverbinding, tel die dan mee.

### BarentsWatch (schepen in Noorse wateren, Noorwegen)

1. Open <https://www.barentswatch.no/minside/> en maak een gebruiker aan, of
   meld je aan.
2. Kies onder **API access (for developers)** (*API-tilgang (for utviklere)*)
   **New Client** (*Ny klient*).
3. Kies de AIS-client, niet de API-client.
4. Kopieer de **client-ID**. Die ziet eruit als
   `your.email@example.com:live_track_ships`. Plak hem precies zo in
   **Client-ID**.
5. Kopieer het **client-secret** naar **Client-secret**. Het wordt maar één
   keer getoond; heb je het niet bewaard, maak dan een nieuw aan.

---

## De kaart op een dashboard zetten

De kaart is [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
de kaart waarop elke Live Track-module tekent. **Hij wordt met Live Track
Ships geïnstalleerd**: niets te downloaden, niets te kopiëren, geen bron toe te
voegen.

1. Open een dashboard, kies het potlood (**Wijzig dashboard**), dan **Voeg
   kaart toe**.
2. Scrol naar beneden en kies **Handmatig**.
3. Plak dit en kies **Bewaar**:

```yaml
type: custom:auto-entities
card:
  type: custom:live-track-map-card
filter:
  include:
    - domain: geo_location
      attributes:
        source: live_track_ships
```

Deze vorm heeft
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities) uit de
Marktplaats nodig. Zijn er andere Live Track-modules geïnstalleerd, voeg dan
voor elk van hun bronnen nog een filter `- domain: geo_location` toe
(`live_track_aircraft`, `live_track_weather` enzovoort).

**Zonder auto-entities:** LiveTrackMapCard kan met `entity_filter` zelf kiezen
wat hij toont. Plak in plaats daarvan dit; er hoeft niets meer geïnstalleerd
te worden:

```yaml
type: custom:live-track-map-card
entity_filter:
  include:
    - domain: geo_location
      attributes:
        source: live_track_ships
```

Andere Live Track-modules gaan op dezelfde manier in `entity_filter`: nog een
regel `- domain: geo_location` voor elke bron.

**Op de kaart:**

* Elk schip wordt getekend met zijn eigen afbeelding, gedraaid naar zijn
  koers, en glijdt tussen zijn gemelde posities over het water in plaats van
  over het land.
* **Wijs** een schip aan om zijn naam te zien, en zijn foto als die er is.
  **Klik** erop voor zijn foto, zijn links, **Track** en **Details**
  ([Foto's en links](#fotos-en-links), [Sporen](#sporen)).
* De **filterkaart** (`custom:live-track-map-filter-card`) verbergt de
  scheepstypen die je uitvinkt
  ([Scheepstypen verbergen](#scheepstypen-verbergen)).

Zijn de bronnen van je dashboards in YAML ingesteld
(`lovelace: resource_mode: yaml`), dan kan er niets voor je worden
geregistreerd: een melding onder **Reparaties** geeft dan de precieze regel om
toe te voegen. Een kaart die je zelf via de Marktplaats hebt geïnstalleerd,
blijft ongemoeid. Worden de bestanden van de integratie verwijderd terwijl
haar gebieden nog zijn ingesteld, en is geen andere Live Track-module
geïnstalleerd, verwijder dan zelf de regel van de kaart in **Instellingen →
Dashboards → Bronnen**. Elke andere kaart die `geo_location`-entiteiten toont,
toont de schepen ook, zonder hun afbeeldingen.

---

## Gebruiken in automatiseringen

Alles is een gewone Home Assistant-entiteit of -gebeurtenis, dus de
automatiseringseditor werkt ermee, zonder code.

**Een melding als een schip van meer dan 150 m (490 voet) je gebied
binnenkomt:**

1. **Instellingen → Automatiseringen en scènes → Maak automatisering aan →
   Voeg automatisering toe**.
2. **Wanneer**: **Voeg trigger toe**, zoek naar **Handmatige gebeurtenis
   ontvangen**, en vul als **Type gebeurtenis** `live_track_ships_entry` in.
3. **En als**: **Voeg voorwaarde toe** → **Sjabloon**, en vul dit
   **Waardesjabloon** in: `{{ trigger.event.data.length_m | default(0) > 150 }}`
4. **Doe dan**: **Voeg actie toe**, zoek de meldingsactie van je telefoon
   (die draagt de naam van je telefoon), en vul dit bericht in:

   ```text
   {{ trigger.event.data.name | default('Een schip') }}, {{ trigger.event.data.length_m }} m, op {{ trigger.event.data.distance_km }} km
   ```

5. **Bewaar**.

**Meer ideeën:** een lamp aan als de avondveerboot je haven in Noorwegen
bereikt; een bericht als de boot van een familielid, een gevolgd schip, thuis
in Finland aankomt; een melding als het cruiseschip dat je opwacht in Sydney
(Australië) aankomt; een telling van de schepen in je haven op een dashboard,
uit `sensor.ships_in_range`.

**De gebiedsgebeurtenissen.** Elk gebied vuurt `live_track_ships_entry` af als
een schip zijn cirkel binnenkomt en `live_track_ships_exit` als het die
verlaat. Elk schip wordt gemeld; je automatisering kiest de schepen die ertoe
doen. De velden hebben dezelfde namen en eenheden als de attributen van het
schip, en laten weg wat de bron niet stuurde:

| Veld | Wat het bevat |
|---|---|
| `area_id`, `area` | de ID van het configuratie-item van het gebied en zijn titel |
| `identity` | de MMSI |
| `name`, `call_sign`, `imo` | als ze zijn verstuurd |
| `object_kind` | `vessel`, `net_buoy`, `aton`, `base_station`, `sar_aircraft` of `distress_beacon` |
| `ship_type`, `ship_type_label`, `length_m`, `beam_m`, `draught_m`, `destination`, `nav_status` | alleen schepen, als ze zijn verstuurd |
| `speed_kmh`, `course_deg`, `heading_deg` | als ze zijn verstuurd |
| `latitude`, `longitude`, `distance_km`, `bearing_from_centre_deg`, `last_seen` | waar het werd gehoord, vanaf het middelpunt van het gebied |
| `entity_id` | alleen bij binnenkomst: `geo_location.vessel_<MMSI>`, als het schip op de kaart staat |
| `reason` | alleen bij vertrek: `left` (buiten de cirkel gehoord) of `silent` (een tijd niet gehoord, dus misschien nog daar) |

⚠ Vier dingen om te weten:

* **Een aankomst wordt alleen gemeld als het schip eerst buiten de cirkel
  werd gehoord.** Een schip dat eerst binnen wordt gehoord, was er misschien
  al die tijd: na een herstart leveren de bronnen nog vele minuten schepen die
  niet bewogen hebben. Een schip dat de ontvangers op weg naar binnen misten,
  of een schip dat zijn transponder binnen aanzet, wordt dus niet gemeld.
* **Een vertrek dat buiten wordt gehoord, wordt altijd gemeld**, ook voor een
  schip dat er al was voordat Home Assistant startte. Een schip dat stil wordt,
  wordt alleen als vertrokken gemeld (`reason: silent`) als zijn aankomst werd
  gemeld.
* **Een vertrek wacht 2 minuten.** Een schip dat eerder terugkomt, langs de
  rand van de cirkel, wordt niet als vertrokken en opnieuw aangekomen gemeld.
* **Bij aankomst kunnen gegevens ontbreken.** Naam, type en afmeting komen in
  een tragere melding dan de positie. Een schip dat voor het eerst wordt
  gehoord, kan aankomen met een positie en verder niets.

Twee gebieden boven hetzelfde water vuren elk hun eigen gebeurtenissen af. De
grenzen aan hoeveel schepen worden getekend, laten nooit een schip binnenkomen
of vertrekken.

**De gebeurtenis van gevolgde schepen.**
[Gevolgde schepen](#gevolgde-schepen-gekozen-schepen-overal) vuren één
gebeurtenis af, `live_track_ships_watched`, waarvan `change` zegt wat er
gebeurde:

| `change` | Wanneer |
|---|---|
| `arrived` | het schip meldt zich afgemeerd of voor anker, of blijft zonder status onder 3,7 km/u (2 knopen) |
| `departed` | het vaart weer |
| `silent` | 30 minuten niet gehoord (6 uur als het afgemeerd of voor anker ligt); het verlaat de kaart en is er misschien nog |
| `heard` | na `silent` weer gehoord |
| `destination` | de bemanning heeft de bestemming gewijzigd; `destination_previous` bevat de oude |

De gegevens bevatten `watch_id`, `watch`, `identity`, je `label`, en dezelfde
scheepsvelden als de gebiedsgebeurtenissen, met afstand en peiling vanaf je
huis. Aankomst en vertrek wachten tot de nieuwe toestand 5 minuten heeft
standgehouden volgens de eigen klok van het schip, zodat een langzaam
drijvende boot niet heen en weer springt. Uit de eerste positie van een schip
na een herstart wordt niets gemeld: die bepaalt het beginpunt. Bestemmingen
worden door de bemanning ingetypt en zijn vaak verouderd.

---

## Alles op de kaart, in detail

AIS (Automatic Identification System, automatisch identificatiesysteem) is
een VHF-radio-uitzending waarmee schepen hun positie, identiteit en reis aan
elkaar en aan de wal melden. Het is de scheepvaartversie van wat vliegtuigen
als ADS-B uitzenden. Beroepsschepen moeten het aan boord hebben; veel
plezierboten hebben het uit eigen keus, meestal als zwakker toestel van
klasse B. AIS wordt open uitgezonden: iedereen met een ontvanger kan het horen,
en openbare diensten geven het door. **Live Track Ships toont alles wat de
bron stuurt.** Er wordt niets weggefilterd, en er is geen instelling om een
categorie voor Home Assistant te verbergen.

### Schepen

Elk schip is een markering waarvan de toestand de afstand tot het middelpunt
van het gebied is, in kilometers. De meeste schepen worden getekend naar type:
vrachtschip, tanker, veerboot, sleepboot enzovoort. Sommige krijgen een eigen
afbeelding: koninklijke en staatsjachten, en bekende boten zoals de
rondvaartboten, watertaxi's en blusboten van een stad. Ken je een schip dat er
een verdient, waar ook ter wereld? [Stel het voor](#help-het-groeien), met de
naam en het MMSI- of IMO-nummer, en een foto of link als je die hebt.

Om een schip meteen te zien vertrekken, wordt elke online bron gevraagd om een
ring die iets breder is dan je cirkel (10%, minstens 1 km), en stuurt je eigen
ontvanger alles wat hij hoort. Alleen schepen binnen je cirkel worden gehouden:
een schip dat buiten wordt gehoord, verlaat de kaart meteen. Een schip dat niet
meer wordt gehoord, verdwijnt na een periode van stilte. Een schip dat niet
meer verschijnt, is niet per se weg: geen van deze bronnen belooft elk bericht
te leveren.

⚠ **Het scheepstype ontbreekt vaak, vooral bij kleine boten.** Positie en naam
komen met bijna elk bericht. Type en afmeting komen in een apart, trager
bericht, en veel toestellen van klasse B sturen dat zelden. Reken erop dat
veel schepen, de meeste kleine boten erbij, geen type of afmeting tonen, en dat
alle schepen de eerste minuten na een herstart van Home Assistant weinig
gegevens hebben. Dat zijn de gegevens, geen fout. Eenmaal gehoorde typen en
afmetingen blijven bewaard na een herstart.

De attributen van een schip omvatten naam, MMSI, roepnaam, snelheid, koers,
kompaskoers, lengte, breedte, scheepstype, bestemming, `object_kind`,
`last_seen` en `attribution`, elk alleen als de bron het stuurde. Een schip dat
twee gebieden zien, is één entiteit.

### Privéboten en zeilboten

Een plezierboot die AIS uitzendt, verschijnt op je kaart precies zoals een
vrachtschip. Afhankelijk van wat de boot uitzendt, kan zijn entiteit bevatten:

* zijn **naam**, die ook het label op de kaart is;
* zijn **MMSI** en **roepnaam**, beide blijvend en openbaar op te zoeken;
* zijn **positie** tot op ongeveer een meter, zijn vorige positie, en wanneer
  elk werd gehoord;
* snelheid, koers en kompaskoers, en lengte, breedte en type, als ze worden
  verstuurd.

Een boot die zijn transponder aan de steiger aan laat staan, blijft op zijn
ligplaats op de kaart zolang hij uitzendt. Wie je kaart kan openen, kan bij
zo'n boot ook op **Track** drukken en zien waar hij de laatste 24 uur is
geweest (of zo lang als je instelt), zijn ligplaats inbegrepen.

Er bestaat geen uitschrijflijst voor AIS, zoals voor vliegtuigen, en deze
integratie verzint er geen. Wil je minder privéboten op je kaart, maak de
straal dan kleiner.

### Wat geen schip is

Elke entiteit draagt `object_kind`: `vessel`, `net_buoy` (boei van vistuig),
`aton` (navigatiehulpmiddel: een boei, baken of vuurtoren), `base_station`
(een AIS-station aan wal), `sar_aircraft` (een zoek- en reddingsvliegtuig) of
`distress_beacon`. De meeste worden onderscheiden aan het identiteitsformaat
dat de Internationale Telecommunicatie-unie (ITU) ze geeft. Boeien van vistuig
niet: die zenden uit met identiteiten zoals schepen, dus worden ze herkend aan
hun fabrieksnamen (FISHING BOUY, NET MARK, BUOY) samen met het ontbreken van
een uitgezonden lengte.

Alles wat geen schip is, wordt getoond zonder scheepstype, afmeting of
navigatiestatus. Boeien van vistuig drijven met hun lijnen mee, dus houden ze
snelheid en koers en worden ze getekend als een vis die in hun drijfrichting
wijst.

Welke hiervan verschijnen, hangt af van de bron. Gemeten op één avond:

| Bron | Boeien van vistuig | Zoek- en reddingsvliegtuigen | Navigatiehulpmiddelen, basisstations |
|---|---|---|---|
| BarentsWatch | ja | ja | geen gezien |
| Digitraffic | geen gezien | ja | geen gezien |
| aisstream.io | geen gezien | geen gezien | geen gezien |
| Je eigen ontvanger | wat hij hoort | wat hij hoort | wat hij hoort |

aisstream.io leverde alleen scheepsposities en scheepsgegevens, zowel boven de
Grote Meren (Noord-Amerika) als boven dezelfde Noorse en Deense wateren waar
BarentsWatch de boeien toont.

### Kustwachtschepen in immigratiewerk

Een schip op de openbare lijst
[EnforcementVessels](https://github.com/StrausbergAutomationWorks/EnforcementVessels)
(schepen van de kustwacht van de Verenigde Staten die bij immigratiewerk
worden ingezet) wordt getekend in de kleuren van de kustwacht, met de naam en
de dienst uit de lijst, waar het ook wordt gehoord.

### Gevolgde schepen: gekozen schepen overal

Naast gebieden kun je een lijst schepen volgen, waar ze ook zijn: de boot van
een familielid, een veerboot die je neemt, een cruiseschip op weg naar huis.
Daarvoor heb je een aisstream.io-sleutel nodig, en er is één zo'n lijst per
Home Assistant.

1. Open **Instellingen → Apparaten en diensten**, kies **Voeg integratie toe**
   en zoek naar **Live Track Ships**.
2. Kies **Gekozen schepen, waar ze ook zijn**.
3. **API-sleutel**: de sleutel van een gebied dat je al hebt ingesteld, is
   ingevuld.
4. **Schepen**: één schip per regel, zijn MMSI van 9 cijfers, dan als je wilt
   een eigen naam:

   ```text
   244650000 De boot van papa
   366999999 De veerboot
   ```

5. Kies **Verzend**.

Hoogstens 100 schepen. aisstream.io volgt hoogstens 200 MMSI's per sleutel, en
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
als dat met dezelfde sleutel is geïnstalleerd, gebruikt daar een deel van. Een
lijst die eroverheen zou gaan, wordt geweigerd als het item wordt geladen, met
de reden. Om de lijst te wijzigen, open je **Configureer** bij het item.

Een gevolgd schip wordt op de kaart getekend zoals elk ander, waar het ook
wordt gehoord, en zijn toestand is de afstand tot je huis. Een gebied dat het
al toont, houdt het: één schip, één markering. Het item voegt
`sensor.watched_vessels` toe: hoeveel van de schepen op de lijst nu worden
gehoord. Het attribuut `vessels` noemt ze allemaal, met hun naam en hun laatst
bekende toestand. De gebeurtenis staat beschreven onder
[Gebruiken in automatiseringen](#gebruiken-in-automatiseringen).

### Foto's en links

Als een schip een IMO-nummer stuurt en Wikidata een foto van dat schip op
Wikimedia Commons kent, draagt het schip `marker_photo`. De kaart toont de foto
als je het schip aanwijst, met fotograaf en licentie; een klik opent hem
groter, met links naar de pagina van de foto en naar de licentie. Elk schip met
een IMO-nummer of een MMSI draagt ook `marker_links`, een link naar het schip
op VesselFinder. De knop **Details** in de pop-up opent het gewone dialoogvenster
van het schip.

Je Home Assistant vraagt het Wikidata en Commons zelf, 20 IMO-nummers tegelijk,
tien seconden na elkaar, en bewaart elk antwoord 30 dagen (14 dagen als er geen
foto is) in `.storage/saw_vessel_photos.json`. Reken op foto's voor ongeveer
één op de tien schepen: op ons testsysteem hadden 49 van de 521 IMO-nummers er
een.

⚠ Een foto kan het schip onder een vroegere naam tonen: het IMO-nummer hoort
bij de romp en blijft erbij als het schip een andere naam krijgt.

### Sporen

Elk schip draagt ook `marker_track`. Klik op een schip en druk op **Track** in
de pop-up: de kaart tekent waar het is geweest, als één lijn die bij het schip
eindigt, en de lijn groeit terwijl je kijkt. **Hide track** haalt hem weg. Er
wordt niets getekend tot je erom vraagt, zodat een drukke haven niet onder
lijnen verdwijnt.

Het spoor bevat alleen posities die het schip meldde terwijl het op je kaart
stond, uitgedund tot één per 25 m (82 voet) of 10 minuten, en nooit twee binnen
30 seconden. Je Home Assistant houdt het in het geheugen en bewaart het in
`.storage/saw_vessel_tracks.json`, zodat het een herstart overleeft. Het beslaat
de laatste 24 uur. Om meer of minder te bewaren:

1. Open **Instellingen → Hulpmiddelen → Acties**.
2. Kies de actie **Live Track Ships: Spoorduur instellen**.
3. Vul **Uren** in, van 1 tot 168 (een week), en kies **Voer actie uit**.

Het geldt voor alle gebieden tegelijk; een kortere instelling gooit oudere
posities meteen weg.

⚠ Het spoor begint leeg bij een eerste installatie. Een schip dat het gebied
verliet of stil werd, heeft een gat, getekend als een rechte lijn tussen de
posities ervoor en erna.

### Scheepstypen verbergen

Elk schip draagt `marker_group`, `marker_group_label` en
`marker_group_order`: een van dertien groepen (vracht; tanker; passagiers en
veerboot; visserij; plezier en zeilen; sleepboot, loods en havendienst;
overheid, zoek en redding en ordediensten; snel en overig; type niet
verstuurd; boeien van vistuig; navigatiehulpmiddelen; basisstations; zoek- en
reddingsvliegtuigen). De filterkaart van de kaart,
`custom:live-track-map-filter-card`, noemt de groepen met hoeveel van elk er op
de kaart staan, en verbergt de groepen die je uitvinkt. Zet hem op elke
weergave van het dashboard. Je keuze wordt alleen in die browser bewaard.

Verbergen gebeurt alleen op de kaart: de integratie telt nog steeds elk schip
en vuurt haar gebeurtenissen voor elk schip af. Een noodbaken heeft geen groep,
dus wordt het nooit verborgen.

---

## Alle entiteiten die het aanmaakt

| Entiteit | Wat het is |
|---|---|
| `geo_location.vessel_<MMSI>` | één markering per schip of ander AIS-object; de toestand is de afstand tot het middelpunt van het gebied (of tot je huis, bij een gevolgd schip), in kilometers. Hij komt en gaat, en heeft geen unieke ID |
| `sensor.ships_in_range` | één per gebied: hoeveel schepen het toont, en of een grens de lijst heeft ingekort |
| `sensor.ais_station` | alleen je eigen ontvanger: berichten per minuut. De attributen geven `vessels_heard` (in de laatste 10 minuten), `farthest_km` en `farthest_mmsi` (vanaf het middelpunt van het gebied), `last_message`, `udp_port`, `listening`, en `port_error` als de poort niet open kan. Hij werkt elke 30 seconden bij, dus een ontvanger die niets meer stuurt, toont 0 |
| `sensor.watched_vessels` | alleen gevolgde schepen: hoeveel van je schepen op de lijst nu worden gehoord |

Attributen die bij elke update veranderen, blijven buiten de geschiedenis van
Home Assistant, zodat je database er niet door groeit: `marker_photo`,
`marker_links` en `marker_track` van elk schip, en de snel veranderende
attributen van de sensoren.

**Je database.** De recorder van Home Assistant slaat een nieuwe rij op elke
keer dat een entiteit verandert, en een varend schip verandert met elke
positie die het meldt. Op ons testsysteem schreef één gebied met 43 schepen in
ongeveer 30 uur 27.109 rijen, 8,8% van de hele database. Standaard bewaart de
recorder 10 dagen en ruimt hij elke nacht om 04:12 plaatselijke tijd op, dus de
groei vlakt af, maar op een grootte die je misschien niet wilt.

Een schip houdt elke keer dat het verschijnt dezelfde entiteits-ID,
`geo_location.vessel_<MMSI>`, dus één patroon, `geo_location.vessel_*`, dekt
alles wat deze integratie ooit op de kaart heeft gezet. Om alleen de laatste
dag ervan te bewaren:

1. **Instellingen → Automatiseringen en scènes → Maak automatisering aan →
   Voeg automatisering toe**.
2. Open het menu met drie puntjes, kies **Wijzig in YAML**, vervang alles door
   dit, en kies **Bewaar**:

```yaml
alias: Scheepsgeschiedenis inkorten
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

Laat je `keep_days` weg (standaard 0), dan gaan al hun rijen in één keer weg.
Wil je er niets van opnemen, zet het patroon dan onder `recorder:` →
`exclude:` → `entity_globs:` in `configuration.yaml`; een kaart die de
geschiedenis tekent (`history_start`) heeft dan geen spoor om te tekenen.
`sensor.ships_in_range` is een gewoon getal en goedkoop om te bewaren.

---

## Wat het verstuurt en downloadt

**Over je locatie.** Het middelpunt van elk gebied is je huis, tenzij je het
verplaatst. Het gaat alleen naar de bron die je voor dat gebied koos: naar
aisstream.io als een rechthoek rond een cirkel die iets groter is dan de jouwe
(10%, minstens 1 km); naar Digitraffic (Finland) als het middelpunt en die
grotere straal; naar BarentsWatch (Noorwegen) als die grotere cirkel. Voor
gevolgde schepen gaan de MMSI-nummers van je lijst naar aisstream.io. Je eigen
ontvanger stuurt nergens iets heen: Home Assistant luistert alleen. Voor
foto's gaan de IMO-nummers van de schepen op je kaart naar Wikidata en
Wikimedia Commons, zonder iets over jou. Om dit alles te stoppen, verwijder je
het gebied of het item van de gevolgde schepen in **Instellingen → Apparaten
en diensten → Live Track Ships**. Verder wordt er niets over jou verstuurd.

**Hoeveel.**

* **aisstream.io**: één verbinding voor al je gebieden en één voor je gevolgde
  schepen, elk open gehouden; schepen komen binnen zodra ze melden. Na een fout
  maakt het na een pauze opnieuw verbinding.
* **Digitraffic**: posities elke 60 seconden en scheepsgegevens elke 15
  minuten, alleen voor je cirkel. Na een fout probeert het de volgende keer
  opnieuw.
* **BarentsWatch**: één open gehouden stroom per gebied. Komt er 150 seconden
  niets, dan maakt het opnieuw verbinding.
* **Foto's**: 20 IMO-nummers tegelijk, 10 seconden na elkaar, alleen voor
  schepen waarnaar de laatste 30 dagen niet is gevraagd (14 als er geen foto
  was). Een mislukt verzoek wordt later opnieuw gedaan.
* **Je eigen ontvanger**: er wordt niets gedownload.

---

## Help het groeien

Live Track Ships groeit nog. We voegen gegevensbronnen en landen toe zodra we
ze vinden, en we willen weten wat je hierna zou willen.

### Iets voorstellen

Ontbreekt je land of je AIS-dienst? Klopt er iets niet, of is iets moeilijk te
begrijpen? Laat het ons weten op de manier die voor jou het makkelijkst is:

* [**Vul een kort formulier in**](https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues/new?template=nl.yml)
  in het Nederlands. Je hebt een gratis GitHub-account nodig.
* **Stuur een e-mail** naar
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Geen account nodig.

Hoe dan ook, het helpt als je ons vertelt:

* wat je graag zou zien, en waar ter wereld;
* een link naar waar de gegevens worden gepubliceerd, als je die kent (een
  open-datapagina, een openbare feed, de website van een dienst): niet nodig,
  maar het helpt;
* de taal van je Home Assistant, als het probleem de formulering of een
  vertaling is.

Schrijf in het Engels of in je eigen taal, wat voor jou het makkelijkst is.

### Zelf iets toevoegen, met onze hulp

Wil je zelf iets toevoegen, dan helpen we je daarbij, van de eerste vraag tot
de afgeronde release. Je hoeft geen ontwikkelaar te zijn om te beginnen:

* **Een vertaling.** De teksten in de instellingsdialoog zijn een korte lijst
  zinnen in één tekstbestand. We laten je zien welk bestand en welke regels.
* **Een nieuwe gegevensbron.** Vertel ons waar de gegevens worden
  gepubliceerd. We kunnen de code samen schrijven, of de jouwe nakijken.
* **Testen waar je woont.** Installeer het, bekijk jouw deel van de kaart, en
  vertel ons wat klopt en wat niet.
* **Een verbetering van deze README.** Als een stap niet overeenkwam met wat
  je zag, vertel ons wat je zag.

[**Vertel ons wat je in gedachten hebt**](https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues/new?template=nl.yml)
of schrijf naar
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
en we antwoorden met de volgende stappen.

---

## Talen

Deze README: [English](README.md), [Deutsch](README.de.md),
[Français](README.fr.md), **Nederlands**, [简体中文](README.zh-Hans.md),
[Español](README.es.md), [Italiano](README.it.md), [Dansk](README.da.md) en
[Kalaallisut](README.kl.md) (een kort concept, ter controle gestuurd naar
Oqaasileriffik, het taalsecretariaat van Groenland; tot die tijd is de Deense
pagina de betrouwbare). Elke vertaalde README is volledig.

De instellingsdialoog en de opties verschijnen in de taal van je Home
Assistant als het een van deze is: English, Dansk, Deutsch, Español,
Français, Gaeilge, Íslenska, Italiano, Nederlands, Norsk Bokmål, Polski,
Português, Português (BR), Suomi, Svenska en 简体中文. Elke andere taal toont
Engels. Kalaallisut is nog geen taal van Home Assistant; we hebben Home
Assistant gevraagd het toe te voegen. De eigen labels van de kaart (**Track**,
**Details**) zijn in elke taal Engels.

Een fout in een vertaling gevonden, of een andere taal nodig? Laat het ons
weten op <https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues>,
of [vertaal het met onze hulp](#zelf-iets-toevoegen-met-onze-hulp).

---

## Vermeldingen en licenties

* **aisstream.io**: geen gepubliceerde voorwaarden. <https://aisstream.io>
* **Fintraffic Digitraffic** (Finland): gegevens onder CC BY 4.0.
  <https://www.digitraffic.fi/en/terms-of-service/>
* **BarentsWatch** (Noorwegen): gegevens onder de Noorse licentie voor open
  overheidsgegevens (NLOD).
  <https://www.barentswatch.no/en/articles/api-terms-and-conditions/>
* **Je eigen ontvanger**: je eigen gegevens.
* **Wikidata**: CC0. **Wikimedia Commons**: elke foto onder zijn eigen
  licentie, getoond met fotograaf en licentie.
* **VesselFinder**: alleen gelinkt; er wordt niets van opgehaald.
* **EnforcementVessels**: ODbL 1.0.
  <https://github.com/StrausbergAutomationWorks/EnforcementVessels>

Wat deze integratie verandert: eenheden worden omgerekend, en alleen schepen
binnen je cirkel worden gehouden. Elke scheepsentiteit, en de
`sensor.ships_in_range` van elk gebied, draagt een `attribution` met de naam
van de bron; Home Assistant toont die in de details van de entiteit. Laat je
deze gegevens aan anderen zien, bijvoorbeeld op een openbaar dashboard, houd
de vermelding er dan bij en lees de eigen voorwaarden van de bron. De precieze
vermeldingsregels, en de vermeldingen voor de scheepsafbeeldingen, staan in
[ATTRIBUTION.md](ATTRIBUTION.md).

Geen van deze organisaties heeft deze integratie gemaakt of goedgekeurd.

**Code**: MIT, in [LICENSE](LICENSE).

**Voor ontwikkelaars:** AIS-zinnen van je eigen ontvanger worden gedecodeerd
door [pyais](https://github.com/M0r13n/pyais) (MIT); Home Assistant installeert
`saw-livetrack` en `pyais` zelf de eerste keer dat het de integratie laadt. De
tests in `tests/` draaien elk los met Python; sommige hebben een geïnstalleerde
Home Assistant nodig, en de tests `*_live` hebben je eigen sleutels nodig.

---

## Trefwoorden

Home Assistant schepen · Home Assistant AIS · schepen volgen · scheepvaart
volgen · boten volgen · scheepvaartkaart · AIS-kaart · AIS-ontvanger · NMEA ·
AIS-catcher · aisstream.io · Digitraffic · BarentsWatch · ship tracking ·
vessel tracker · Schiffsverfolgung · suivi des navires · seguimiento de
barcos · tracciamento navi · skibstrafik · 船舶追踪 · geo_location · kaart ·
Lovelace · HACS · Marketplace · Live Track · LiveTrack ·
StrausbergAutomationWorks

---

**Erkenning.** StrausbergAutomationWorks erkent de inheemse volken van alle
landen en wateren op deze kaart, overal ter wereld, en betuigt zijn respect aan
hun Elders, van vroeger en nu.
