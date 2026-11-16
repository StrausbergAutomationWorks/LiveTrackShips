# Live Track Ships

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · **Nederlands** · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Kalaallisut](README.kl.md) · [Alle talen](#talen)

**AIS-tracking van schepen, boten en vaartuigen voor Home Assistant.** Schepen
bij jou in de buurt, of waar ook ter wereld, als live markeringen op je kaart.
Onderdeel van Live Track: schepen, vliegtuigen en treinen op één kaart.

Live AIS-gegevens van [aisstream.io](https://aisstream.io),
[Fintraffic Digitraffic](https://www.digitraffic.fi/en/marine-traffic/) of
[BarentsWatch](https://www.barentswatch.no/en/), getoond als
`geo_location`-entiteiten van Home Assistant en getekend op de gedeelde Live
Track-kaart.

**Status: 0.1.0, de eerste release.** Via een link aan de Marketplace toe te
voegen (hieronder); in de catalogus van de Marketplace staat hij nog niet.

## Wat AIS is

AIS (Automatic Identification System, automatisch identificatiesysteem) is een
VHF-uitzending waarmee schepen hun positie, identiteit en reis aan elkaar en
aan de wal doorgeven. Het is de scheepvaartversie van ADS-B. Beroepsvaart moet
het aan boord hebben; veel pleziervaartuigen hebben het vrijwillig, meestal als
zwakker klasse B-apparaat.

AIS wordt onversleuteld uitgezonden. Iedereen met een ontvanger kan het horen,
en openbare verzameldiensten publiceren het opnieuw.

## Wat er te zien is

**Alles wat de bron stuurt.** Er wordt niets weggefilterd, en er is geen
instelling om een categorie te verbergen.

| In de gegevens | Getoond |
|---|---|
| Vrachtschepen, tankers, sleepboten, veerboten, passagiersschepen | ja |
| Visserij-, loods-, handhavings- en andere werkvaartuigen | ja |
| **Particuliere pleziervaartuigen en zeilboten** | **ja, met naam en positie** |
| **Boeien van vistuig** die AIS uitzenden | **ja, getekend als vis** |
| Zoek- en reddingsvliegtuigen (SAR) | als de bron ze stuurt |
| Navigatiehulpmiddelen: boeien, bakens, vuurtorens | als de bron ze stuurt |
| AIS-walstations | als de bron ze stuurt |

### Particuliere boten worden getoond, en je moet weten wat dat betekent

Een pleziervaartuig met AIS verschijnt op je kaart precies zoals een
vrachtschip. Afhankelijk van wat de boot uitzendt, kan de entiteit bevatten:

- de **naam**, die ook als label op de kaart staat
- de **MMSI** en de **roepnaam**, beide blijvend en openbaar op te zoeken
- de **positie** tot op ongeveer een meter, de vorige positie en wanneer elk
  werd gehoord
- snelheid, koers en kompaskoers, als die worden uitgezonden
- lengte, breedte en scheepstype, als die worden uitgezonden

Een boot die zijn transponder aan de steiger aan laat staan, blijft op de
kaart op zijn ligplaats zolang hij uitzendt.

Wie je kaart kan openen, kan bij zo'n boot ook op **Track** drukken en zien
waar hij de afgelopen 24 uur (of zo lang als je instelt) is geweest, niet
alleen waar hij nu ligt: een boot die vanochtend zijn ligplaats verliet, toont
die ligplaats de hele dag.

Voor AIS bestaat geen uitsluitingslijst zoals voor vliegtuigen, en deze
integratie verzint er geen. Wil je minder pleziervaartuigen op je kaart, maak
dan de straal kleiner.

### Het scheepstype ontbreekt vaak, vooral bij kleine boten

Positie en naam komen met bijna elk bericht mee. Scheepstype en afmetingen
komen in een apart, zeldzamer bericht, en veel apparaten van kleine boten
(klasse B) sturen het deel dat ze bevat maar zelden. Reken erop dat een groot
deel van de schepen, de meeste kleine erbij, zonder type of afmetingen
verschijnt, en dat alle schepen enkele minuten na een herstart van Home
Assistant onvolledig zijn. Dat zijn de gegevens, geen storing. Eenmaal gehoorde
typen en afmetingen blijven bewaard na een herstart.

### Niet alles op AIS is een schip

Elke entiteit heeft `object_kind`: `vessel`, `net_buoy`, `aton`
(navigatiehulpmiddel), `base_station`, `sar_aircraft` of `distress_beacon`. De
meeste worden herkend aan het formaat van de identificatie die de ITU ze
toekent. Boeien van vistuig niet: die zenden uit met scheepsachtige
identificaties en worden daarom herkend aan hun fabrieksnamen (FISHING BOUY,
NET MARK, BUOY) samen met het ontbreken van een uitgezonden lengte.

Alles wat geen schip is, verschijnt zonder scheepstype, afmetingen of
navigatiestatus. Boeien van vistuig drijven mee met hun lijnen; ze houden dus
snelheid en koers en worden getekend als zalm die de kant op wijst waarheen ze
drijven.

Wat hiervan verschijnt, hangt af van de bron. Gemeten op één avond:

| Bron | Boeien van vistuig | SAR-vliegtuigen | Navigatiehulpmiddelen, walstations |
|---|---|---|---|
| BarentsWatch | ja | ja | geen gezien |
| Digitraffic | geen gezien | ja | geen gezien |
| aisstream.io | geen gezien | geen gezien | geen gezien |
| Je eigen ontvanger | wat hij hoort | wat hij hoort | wat hij hoort |

aisstream.io leverde alleen positie- en detailberichten van schepen, zowel
boven de Grote Meren als boven dezelfde Noorse en Deense wateren waar
BarentsWatch de boeien toont.

## Bronnen

Voor elk gebied dat je instelt, kies je één bron.

| Bron | Dekking | Nodig |
|---|---|---|
| aisstream.io | wereldwijd, waar vrijwilligers ontvangers draaien | een gratis API-sleutel |
| Fintraffic Digitraffic | Finse en Baltische wateren | niets |
| BarentsWatch AIS Live | Noorse wateren | een gratis client-ID en client-secret |
| Je eigen AIS-ontvanger | zo ver als je antenne hoort | een ontvanger die NMEA via UDP stuurt |

Welke categorieën verschijnen, hoe actueel de posities zijn en hoe volledig de
scheepsgegevens, hangt af van de bron die je kiest.

### Je eigen ontvanger

Heb je een AIS-ontvanger, dan kan Live Track Ships laten zien wat hij hoort,
zonder account en zonder internet. De ontvanger, of het programma dat hem
decodeert, stuurt NMEA-zinnen (`!AIVDM`) via UDP naar het adres van Home
Assistant, op een poort die je kiest (10110 als je niets verandert). In
AIS-catcher is dat `-u <address> <port>`, in rtl-ais `-h <address> -P <port>`;
OpenCPN en Signal K voegen het toe als uitgaande UDP-verbinding. Een
ontvanger die je via USB aansluit, zoals een dAISy, heeft een van die
programma's nodig om zijn zinnen door te geven.

- Eén gebied luistert op één poort; twee ontvangers hebben twee poorten nodig.
- Alles wat de ontvanger binnen je cirkel hoort, wordt getoond, ook
  navigatiehulpmiddelen en basisstations. De stationsensor (hieronder) telt
  ook wat hij buiten de cirkel hoort.
- Een zin bevat geen datum, dus de tijd van een positie is het moment waarop
  Home Assistant hem ontving.
- De draaisnelheid wordt voor deze bron niet getoond.
- Tot nu toe is dit getest met opgenomen zinnen die via UDP werden gestuurd,
  niet met een ontvanger. Probeer je het met de jouwe, laat dan op de
  [issuespagina](https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues) weten hoe het ging.

### Bronvermelding

Elke scheepsentiteit, en de sensor `ships_in_range` van elk gebied, heeft een
attribuut `attribution` dat de bron noemt; Home Assistant toont het in de
details van de entiteit. Twee van de bronnen geven hun gegevens onder een
licentie met naamsvermelding, en Live Track Ships verandert wat het ontvangt
(eenheden omgerekend, alleen schepen in je cirkel), dus hun regels zeggen dat.
Laat je deze gegevens aan anderen zien, bijvoorbeeld op een openbaar
dashboard, houd dan de vermelding erbij en lees de voorwaarden van de bron:

- **aisstream.io**: geen gepubliceerde voorwaarden. <https://aisstream.io>
- **Fintraffic Digitraffic**: CC BY 4.0.
  <https://www.digitraffic.fi/en/terms-of-service/>
- **BarentsWatch**: Noorse licentie voor open overheidsgegevens (NLOD).
  <https://www.barentswatch.no/en/articles/api-terms-and-conditions/>
- **Je eigen ontvanger**: je eigen gegevens; de regel zegt dat.
- **EnforcementVessels** (de lijst achter de kustwachtweergave, hieronder):
  ODbL v1.0. <https://github.com/StrausbergAutomationWorks/EnforcementVessels>

De precieze regels staan in [ATTRIBUTION.md](ATTRIBUTION.md).

## Vereisten

- Home Assistant 2026.11 of nieuwer, met internettoegang naar buiten voor de
  onlinebronnen.
- Voor aisstream.io: een gratis API-sleutel van
  [aisstream.io](https://aisstream.io/account). aisstream staat **drie
  verbindingen per account en drie per openbaar IP-adres** toe; gebruik je
  andere programma's met dezelfde sleutel, houd daar dan rekening mee. Live
  Track SALT gebruikt, als het geïnstalleerd is, een tweede verbinding met
  dezelfde sleutel.
- Voor BarentsWatch: een gratis client-ID en client-secret, zelf te
  registreren bij BarentsWatch. Vul de client-ID precies zo in als hij is
  uitgegeven.
- Voor je eigen ontvanger: een ontvanger en een programma die NMEA via UDP
  naar Home Assistant sturen, in hetzelfde netwerk. Internet is daarvoor niet
  nodig.
- Home Assistant installeert de benodigde Python-pakketten (`saw-livetrack` en
  `pyais`) zelf de eerste keer dat het de integratie laadt.

## Installatie

### Via de Marketplace

Live Track Ships staat nog niet in de catalogus van de Marketplace. Voeg hem
toe via een link:

1. **Instellingen > Marketplace**, dan **Toevoegen via link**.
2. Vul `StrausbergAutomationWorks/LiveTrackShips` in. Wordt naar het type
   gevraagd, kies dan **Integratie**.
3. Installeer **Live Track Ships**.
4. Herstart Home Assistant. De Marketplace biedt de herstart aan als
   reparatie onder **Instellingen > Systeem > Reparaties**.

### Met de hand

1. Download de broncode van de
   [nieuwste release](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest).
2. Kopieer de map `custom_components/live_track_ships` daaruit naar de map
   `custom_components` in de configuratiemap van Home Assistant.
3. Herstart Home Assistant.

## Instellen

**Instellingen > Apparaten en diensten > Integratie toevoegen > Live Track
Ships**, dan **Alle schepen in een gebied** (de andere keuze, gevolgde
schepen, staat [verderop](#gevolgde-schepen-gekozen-schepen-overal-volgen)).
Elk gebied is een eigen item met de titel *Ships near <breedte>, <lengte>*.
Het venster verschijnt in het Nederlands als Home Assistant in het Nederlands
staat.

| Veld | Wat het neemt | Standaard |
|---|---|---|
| Gegevensbron | aisstream.io, Fintraffic Digitraffic, BarentsWatch AIS Live of je eigen AIS-ontvanger | aisstream.io |
| API-sleutel | alleen aisstream.io. Overgenomen van een gebied dat je al hebt ingesteld; aan te passen | leeg |
| Client-ID, client-secret | alleen BarentsWatch. Overgenomen van een gebied dat je al hebt ingesteld | leeg |
| UDP-poort | alleen je eigen ontvanger: de poort waar hij NMEA naartoe stuurt, 1024 tot 65535. Geweigerd als een ander gebied of een ander programma hem al gebruikt | 10110 |
| Middelpunt | een markering op een kaart; sleep hem naar het water dat je wilt volgen | je huis |
| Straal (km) | 1 tot 500 | 50 |
| Maximaal aantal gevolgde schepen | 1 tot 5.000; een veiligheidsgrens voor dit gebied, de dichtstbijzijnde blijven | 1.000 |

Dezelfde bron kan hetzelfde middelpunt niet twee keer volgen. Ligt minstens
5 % van een BarentsWatch-cirkel buiten de wateren die BarentsWatch publiceert,
dan zegt het venster hoeveel voordat het gebied wordt aangemaakt; verzend om
die cirkel toch te houden.

**Instellingen van een gebied** (Configureren bij het item): het middelpunt,
met dezelfde markering; de straal; het maximale aantal gevolgde schepen; en
*Maximaal aantal schepen op de kaart, alle Live Track Ships-items samen*, een
schuifregelaar van 100 tot 2.500 in stappen van 100 (standaard 2.500); en, bij je eigen ontvanger, zijn UDP-poort. Het
middelpunt verplaatsen geeft het gebied een nieuwe naam naar zijn positie en
laadt het opnieuw. Dezelfde bron kan een middelpunt nog steeds niet vanuit
twee gebieden volgen.

## Wat er wordt aangemaakt

- **Eén `geo_location`-entiteit per schip**, `geo_location.vessel_<MMSI>`,
  met als toestand de afstand tot het middelpunt van het gebied in kilometers.
  Attributen zijn onder meer naam, MMSI, roepnaam, snelheid, koers,
  kompaskoers, lengte, breedte, scheepstype, bestemming, `object_kind`,
  `last_seen` en `attribution`, elk alleen als de bron het stuurde. Een schip
  dat twee gebieden zien, is één entiteit.
- **Eén sensor per gebied**, `sensor.ships_in_range`, die de getoonde schepen
  telt en het zegt als de grens van het gebied of van de hele installatie de
  lijst inkort.
- **Bij je eigen ontvanger nog een sensor**, `sensor.ais_station`: berichten
  per minuut. De attributen zijn `vessels_heard` (in de laatste 10 minuten),
  `farthest_km` en `farthest_mmsi` (vanaf het middelpunt van het gebied),
  `last_message`, `udp_port`, `listening`, en `port_error` als de poort niet
  kan worden geopend. Hij wordt elke 30 seconden bijgewerkt, dus een ontvanger
  die niets meer stuurt, toont 0.

Een schip dat buiten je cirkel wordt gehoord, verdwijnt meteen van de kaart.
Om dat te horen, wordt elke onlinebron gevraagd om een ring iets groter dan je
cirkel (10 %, minstens 1 km), en je eigen ontvanger stuurt alles wat hij hoort;
alleen schepen in je cirkel worden bewaard. Een
schip dat niet meer wordt gehoord, verdwijnt na een periode van stilte, en een
schip dat niet meer verschijnt, is niet per se weg (hieronder).

### Je database

De recorder van Home Assistant slaat een nieuwe rij op telkens als een entiteit
verandert, en een varend schip verandert bij elke positie die het meldt. Deze
integratie kan je database daardoor snel laten groeien: op ons testsysteem
schreef één gebied met 43 schepen in ongeveer 30 uur 27.109 statusrijen, 8,8%
van de hele database. Standaard bewaart de recorder 10 dagen en ruimt hij elke
nacht om 04:12 op, dus de groei vlakt af, maar op een omvang die je misschien
niet wilt. `marker_photo`, `marker_links` en `marker_track` van elk schip, en de snel
veranderende attributen van de sensoren, worden nooit vastgelegd.

Een schip houdt elke keer dat het verschijnt dezelfde entiteit-ID,
`geo_location.vessel_<MMSI>`: een veerboot die vertrekt en terugkomt
hergebruikt zijn entiteit in plaats van er een toe te voegen. Eén patroon,
`geo_location.vessel_*`, dekt dus alles wat deze integratie ooit op de kaart
heeft gezet. Om daarvan alleen de laatste dag te bewaren, voer je
`recorder.purge_entities` volgens schema uit, bijvoorbeeld met deze
automatisering:

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
Om er niets van vast te leggen, zet je het patroon onder `recorder:` →
`exclude:` → `entity_globs:` in `configuration.yaml`. Een kaartkaart die
geschiedenis moet tekenen (`history_start`) heeft dan geen spoor om te tekenen.
`sensor.ships_in_range` is een kaal getal en goedkoop om te bewaren, dus zijn
geschiedenis blijft in beide gevallen bestaan.

## Gebeurtenissen: een schip komt je gebied in of gaat eruit

Elk gebied vuurt twee gebeurtenissen af in Home Assistant, zodat een
automatisering je kan laten weten wanneer een schip aankomt dat voor jou telt:

- `live_track_ships_entry` wanneer een schip de cirkel van het gebied in komt
- `live_track_ships_exit` wanneer het eruit gaat

De integratie meldt elk schip; jouw automatisering kiest de schepen die
tellen. De gegevens van de gebeurtenis hebben dezelfde namen en eenheden als
de attributen van het schip en laten weg wat de bron niet stuurde:

| Veld | Inhoud |
|---|---|
| `area_id`, `area` | de ID van het configuratie-item van het gebied en de titel |
| `identity` | de MMSI |
| `name`, `call_sign`, `imo` | als ze worden uitgezonden |
| `object_kind` | `vessel`, `net_buoy`, `aton`, `base_station`, `sar_aircraft` of `distress_beacon` |
| `ship_type`, `ship_type_label`, `length_m`, `beam_m`, `draught_m`, `destination`, `nav_status` | alleen schepen, als ze worden uitgezonden |
| `speed_kmh`, `course_deg`, `heading_deg` | als ze worden uitgezonden |
| `latitude`, `longitude`, `distance_km`, `bearing_from_centre_deg`, `last_seen` | waar het werd gehoord, vanaf het middelpunt van het gebied |
| `entity_id` | alleen bij binnenkomst: `geo_location.vessel_<MMSI>`, als het schip op de kaart staat |
| `reason` | alleen bij vertrek: `left` (buiten de cirkel gehoord) of `silent` (niet gehoord gedurende de bewaartijd, dus misschien nog daar) |

Vier dingen om te weten:

- **Een aankomst wordt alleen gemeld als het schip eerst buiten de cirkel is
  gehoord**, in de ring eromheen. Een schip dat eerst binnen wordt gehoord, kan
  er al die tijd hebben gelegen: na een herstart blijven de ontvangers nog vele
  minuten schepen leveren die nooit hebben bewogen. Een schip dat de ontvangers
  op weg naar binnen niet hoorden, of een dat zijn transponder pas binnen de
  cirkel aanzet, wordt daarom niet gemeld.
- **Vertrek dat buiten wordt gehoord, wordt altijd gemeld**, ook voor een schip
  dat er al was voordat Home Assistant startte. Een schip dat stil valt, wordt
  alleen als vertrokken gemeld (`reason: silent`) als zijn aankomst gemeld is.
- **Een vertrek wacht 2 minuten.** Een schip dat eerder terugkomt, langs de
  rand van de cirkel, wordt niet gemeld als vertrokken en weer aangekomen.
- **Bij aankomst kunnen gegevens ontbreken.** Naam, type en afmetingen komen in
  een zeldzamer bericht dan de positie (hierboven). Een schip dat voor het eerst
  wordt gehoord, kan aankomen met alleen een positie; een schip dat eerder is
  gehoord, heeft meestal type en afmetingen.

Twee gebieden boven hetzelfde water vuren elk hun eigen gebeurtenissen af. De
grenzen aan hoeveel schepen de kaart tekent, laten nooit een schip binnenkomen
of vertrekken.

Een automatisering die het je laat weten als een schip van meer dan 150 m een
gebied in komt:

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
      title: "{{ trigger.event.data.name | default('Een schip') }}"
      message: >-
        {{ trigger.event.data.ship_type_label | default('Schip') }},
        {{ trigger.event.data.length_m }} m,
        {{ trigger.event.data.distance_km }} km verderop, komt
        {{ trigger.event.data.area }} binnen.
```

## Gevolgde schepen: gekozen schepen overal volgen

Naast gebieden kun je een lijst schepen volgen, waar ze ook zijn: de boot van
een familielid, een veerboot die je neemt, een cruiseschip op weg naar huis.
**Instellingen > Apparaten en diensten > Integratie toevoegen > Live Track
Ships > Gekozen schepen, waar ze ook zijn.** Er is een sleutel van
aisstream.io nodig (de sleutel van een gebied dat je al hebt ingesteld, is
ingevuld), en er is één zo'n lijst per Home Assistant.

Eén schip per regel: de MMSI van 9 cijfers, daarna desgewenst een eigen naam.

```text
244650000 Papa's boot
366999999 De veerboot
```

Hoogstens 100 schepen. aisstream volgt hoogstens 200 MMSI's per sleutel, en
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT)
gebruikt, als het met dezelfde sleutel is geïnstalleerd, een deel daarvan; een
lijst die daarboven zou komen, wordt bij het laden van het item geweigerd,
met de reden. Wijzig de lijst in de instellingen van het item.

Een gevolgd schip wordt op de kaart getekend zoals elk ander, waar het ook
wordt gehoord, en de toestand is de afstand tot je huis. Een gebied dat het
al toont, houdt het: één schip, één markering. Het item maakt
`sensor.watched_vessels` aan: hoeveel van de schepen op de lijst nu worden
gehoord, met elk ervan, je eigen naam en de laatst bekende toestand in het
attribuut `vessels`.

Het vuurt één gebeurtenis af, `live_track_ships_watched`, waarvan het veld
`change` zegt wat er gebeurde:

| `change` | Wanneer |
|---|---|
| `arrived` | het schip meldt zich afgemeerd of voor anker, of blijft zonder status onder 2 knopen |
| `departed` | het vaart weer |
| `silent` | 30 minuten niet gehoord (6 uur als het afgemeerd of voor anker ligt); het verdwijnt van de kaart en is misschien nog daar |
| `heard` | weer gehoord na `silent` |
| `destination` | de bemanning heeft de bestemming gewijzigd; `destination_previous` bevat de oude |

De gegevens bevatten `watch_id`, `watch`, `identity`, je eigen naam `label` en
dezelfde scheepsvelden als de gebiedsgebeurtenissen, met afstand en richting
vanaf je huis. Aankomst en vertrek wachten tot de nieuwe toestand 5 minuten
heeft geduurd volgens de eigen klok van het schip, zodat een boot die met 2
knopen drijft niet heen en weer springt. Uit de eerste positie van een schip
na een herstart wordt niets gemeld: die legt het uitgangspunt vast.
Bestemmingen worden door de bemanning ingetypt en zijn vaak verouderd.

## Kaartkaart

De schepen worden getekend door [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)
(`custom:live-track-map-card`), de ene kaart waarop elke Live Track-integratie
tekent. Hij tekent de eigen afbeelding van elk schip, draait die naar de
kompaskoers en laat hem tussen echte posities over het water glijden in plaats
van recht over land.

**De kaart wordt met de integratie geïnstalleerd.** Deze integratie heeft een
uitgebrachte kopie van de kaart bij zich, serveert die en registreert hem als
dashboardbron wanneer Home Assistant start; er is niets te downloaden of naar
`www` te kopiëren. Elke Live Track-integratie doet hetzelfde, en samen houden
ze precies één bronregel: de hoogste kaartversie die een van hen meebrengt,
nooit een oudere. Een kaart die via de Marketplace is geïnstalleerd, blijft
ongemoeid. Het laatste gebied van deze integratie verwijderen geeft de regel
aan een andere Live Track-integratie, of verwijdert hem als er geen meer is.
Zie de README van de kaart, onderdeel
[Live Track](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).

Zijn de bronnen van je dashboards in YAML vastgelegd
(`lovelace: resource_mode: yaml`), dan kan er niets voor je worden
geregistreerd. Een reparatiemelding geeft dan de precieze regel; die ziet er
zo uit, met het adres van de integratie in plaats van de plaatshouders:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_ships/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Worden de bestanden van de integratie verwijderd (via de Marketplace,
bijvoorbeeld) terwijl de gebieden nog zijn ingesteld, en is er geen andere
Live Track-integratie geïnstalleerd, dan ruimt niets de regel op: verwijder
hem onder Instellingen > Dashboards > Bronnen. Wil je de kaart liever met de
hand installeren, volg dan de README van de kaart; de bronregel van een met
de hand geïnstalleerde kopie onder `/local/` wordt alleen naar de kopie van
een integratie omgezet als die een nieuwere release is.

Geef hem de schepen met
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities),
gefilterd op `domain: geo_location` en `attributes: {source: live_track_ships}`.
Zijn er andere Live Track-integraties geïnstalleerd, voeg dan voor elk van hun
bronnen een filter toe.

Elke andere kaart die `geo_location`-entiteiten toont, toont de schepen ook,
zonder de afbeeldingen en het glijden van deze kaart.

Een schip op de openbare lijst
[EnforcementVessels](https://github.com/StrausbergAutomationWorks/EnforcementVessels)
(kustwachtschepen die bij immigratiewerk worden ingezet) wordt getekend in de
kleuren van de kustwacht, met de naam en de dienst van de lijst, waar het ook
is.

### Scheepstypen verbergen

Elk schip draagt `marker_group`, `marker_group_label` en `marker_group_order`:
een van dertien groepen (vracht; tanker; passagiers en veerboten; visserij;
plezier en zeilen; sleepboten, loodsen en havendienst; overheid, SAR en
politie; snelle schepen en overige; type niet verzonden; boeien van
vistuig; navigatiehulpmiddelen; basisstations; SAR-vliegtuigen). De
filterkaart van de kaartkaart, `custom:live-track-map-filter-card`, toont ze
met hoeveel er van elk op de kaart staan en verbergt wat je uitvinkt; zet hem
op een willekeurige weergave van het dashboard. Je keuze wordt alleen in die
browser bewaard. De integratie toont nog steeds alles: haar sensor telt elk
schip en haar gebeurtenissen gaan voor elk schip af. Een noodbaken heeft geen
groep en wordt dus nooit verborgen.

### Foto's en links

Als een schip een IMO-nummer verstuurt en Wikidata een foto van dat schip op
Wikimedia Commons kent, draagt het schip `marker_photo`. De kaart toont de foto
in het zweefvenster met de fotograaf en de licentie; een klik opent hem groter,
met links naar de pagina van de foto en naar de licentie. Elk schip met een
IMO-nummer of een MMSI draagt ook `marker_links`, een link naar het schip op
VesselFinder. De knop **Details** in het venster opent het gewone dialoogvenster
van het schip. Je Home Assistant vraagt Wikidata en Commons zelf, 20
IMO-nummers tegelijk, tien seconden na elkaar, en bewaart elk antwoord 30 dagen
(14 als er geen foto is) in `.storage/saw_vessel_photos.json`. Reken op foto's
voor ongeveer één op de tien schepen: op ons testsysteem hadden 49 van de 521
IMO-nummers er een.

### Sporen

Elk schip heeft ook `marker_track`. Klik op een schip en druk in het venster op
**Track**: de kaart tekent waar het geweest is, als één lijn die bij het schip
eindigt en groeit terwijl je kijkt; **Hide track** haalt hem weg. Er wordt
niets getekend tot je erom vraagt, zodat een drukke haven nooit onder lijnen
verdwijnt. Het spoor bevat alleen posities die het schip meldde terwijl het op
je kaart stond, uitgedund tot één per 25 m of 10 minuten en nooit twee binnen
30 seconden. Je Home Assistant houdt het in het geheugen en bewaart het in
`.storage/saw_vessel_tracks.json`, dus het overleeft een herstart. Het beslaat
de laatste 24 uur. Om meer of minder te bewaren, voer je de actie
`live_track_ships.set_track_hours` uit met `hours` van 1 tot 168 (een week),
bijvoorbeeld via Ontwikkelhulpmiddelen > Acties:

```yaml
action: live_track_ships.set_track_hours
data:
  hours: 72
```

Het geldt voor alle gebieden tegelijk; een kortere instelling verwijdert
oudere posities meteen. De recorder van Home Assistant legt sporen niet vast.

## Waar hij kijkt

Je zet een **middelpunt en een straal** op de kaart. Het middelpunt kan
overal ter wereld liggen; de straal kan 1 tot 500 km zijn. Standaard is
**50 km**. De toestand van elk schip is de afstand tot je middelpunt.

Hoeveel schepen een cirkel bevat, hangt veel meer af van *welk water* dan van
*hoe groot*. In tests bevatte een cirkel van 50 km boven Chicago ongeveer 4
schepen en boven de Solent in Zuid-Engeland ongeveer 340: dezelfde straal,
ongeveer 80 keer zoveel verkeer. Daarom houdt de integratie hoogstens een vast
aantal schepen bij (standaard 1.000, instelbaar tot 5.000), houdt de
dichtstbijzijnde als het er meer zijn, en zegt dat op de sensor
`ships_in_range`.

Al je gebieden **samen** tonen hoogstens 2.500 schepen, welke bronnen ze ook
hebben. De instellingen van elk gebied hebben de schuifregelaar van
hierboven, die dat plafond alleen kan verlagen; de laagste instelling van een
ingeschakeld gebied geldt. Verlaag hem op tragere hardware.

## Dekking, gemeten in plaats van beloofd

De dekking is goed waar ontvangers staan en ontbreekt waar ze niet staan, en
**geen instelling kan dekking maken die niet bestaat**.

Gemeten op 2026-09-02 rond Chicago, met aisstream.io:

- **Grote Meren**: 100 verschillende schepen in 120 seconden, alle vijf de
  meren en de verbindende wateren.
- **Chicago River, binnenstad**: druk en betrouwbaar.
- **Chicago Sanitary and Ship Canal, Cal-Sag Channel, Calumet River**: een uur
  luisteren, **nul schepen**. Het kanaal is niet leeg: de duwbakken zijn bij
  commerciële diensten te zien via satelliet-AIS, dat gratis verzameldiensten
  niet doorgeven. Het verkeer is echt; de dekking vanaf land niet.

Geen schepen in je gebied kan betekenen dat er geen ontvangers zijn in plaats
van geen boten. Controleer of je bron je water dekt voordat je aanneemt dat de
integratie stuk is.

Een schip dat niet meer verschijnt, is niet per se weg. Geen van deze bronnen
garandeert aflevering, dus de integratie laat zien wanneer elk schip voor het
laatst werd gehoord en verwijdert het pas na een periode van stilte.

## Schepen die een eigen afbeelding verdienen

De meeste schepen worden getekend naar hun type. Sommige hebben een eigen
afbeelding: koninklijke en staatsjachten, en bekende boten zoals de
rondvaartboten, watertaxi's en blusboten van Chicago. Ken je een schip dat er
een verdient, waar ook ter wereld? Open een issue op
<https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues> met de
naam en het MMSI- of IMO-nummer, en een foto of link als je die hebt.

## Talen

Deze README: [English](README.md), [Deutsch](README.de.md),
[Français](README.fr.md), **Nederlands**, [简体中文](README.zh-Hans.md),
[Español](README.es.md), [Italiano](README.it.md), [Dansk](README.da.md) en
[Kalaallisut](README.kl.md) (een concept, ter beoordeling gestuurd naar
Oqaasileriffik, het taalsecretariaat van Groenland; tot dan is de Deense
pagina de betrouwbare). De README is vertaald in een korte lijst talen: die
de meeste gebruikers van Home Assistant lezen, en een paar meer waar daar een
goede reden voor is. Elke vertaalde README is volledig: alles uit de Engelse
staat in elk ervan, en geen enkele stuurt je voor de details naar het Engels.

Het instellingsvenster en de instellingen van een gebied verschijnen in de
taal van je Home Assistant als dat een van deze is: English, Dansk, Deutsch,
Español, Français, Gaeilge, Íslenska, Italiano, Nederlands, Norsk Bokmål,
Polski, Português, Português (BR), Suomi, Svenska en 简体中文. Elke andere taal
toont het Engelse venster. Kalaallisut is nog geen taal van Home Assistant; we
hebben Home Assistant gevraagd het toe te voegen, en het venster volgt zodra
het kan worden getoond.

Een fout gevonden in een vertaling die de betekenis verandert of slecht
leest? Laat het ons weten op
<https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues>. De
vertalingen zijn voor dit project geschreven en nog niet allemaal door een
moedertaalspreker gelezen.

**Moeite om dit in een van deze talen te volgen?** Vraag op hetzelfde adres
om een andere taal, en we proberen je tegemoet te komen.

## Onderdeel van Live Track

Live Track is een reeks Home Assistant-integraties, één per soort ding dat
beweegt, die allemaal op dezelfde kaart tekenen. Ze delen een
Python-bibliotheek
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore))
en de kaart, zodat een extra integratie geen verzoeken toevoegt aan een
gedeelde bron. Uitgebracht:
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft),
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
[Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail),
[Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail)
en Live Track Ships. Elk werkt ook op zichzelf.

## Niet gelieerd

Niet gelieerd aan aisstream.io, Fintraffic, BarentsWatch, MarineTraffic,
VesselFinder, een rederij of een maritieme overheid. AIS is een systeem voor
de veiligheid van de scheepvaart; **deze integratie is voor de
belangstelling en niet voor navigatie, het vermijden van aanvaringen of enig
operationeel doel.**

## Licentie

Code: MIT, in [LICENSE](LICENSE). Vermeldingen van gegevens en afbeeldingen:
[ATTRIBUTION.md](ATTRIBUTION.md).

## Trefwoorden

Home Assistant AIS · schepen volgen · schepen op de kaart · boten volgen ·
scheepvaartverkeer live · AIS-kaart · aisstream.io · Digitraffic ·
BarentsWatch · geo_location · HACS-integratie
