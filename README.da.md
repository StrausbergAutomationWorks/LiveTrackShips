# Live Track Ships

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · **Dansk** · [Kalaallisut](README.kl.md) · [Alle sprog](#sprog)

**AIS-sporing af skibe, både og fartøjer til Home Assistant.** Skibe nær dig,
eller hvor som helst i verden du vælger, som levende markører på dit kort. En
del af Live Track: skibe, fly og tog på ét kort.

Levende AIS-data fra havet fra [aisstream.io](https://aisstream.io),
[Fintraffic Digitraffic](https://www.digitraffic.fi/en/marine-traffic/) eller
[BarentsWatch](https://www.barentswatch.no/en/), vist som
`geo_location`-enheder i Home Assistant og tegnet på det fælles Live
Track-kort.

**Status: 0.1.0, den første udgivelse.** Tilføjes til Marketplace via et link
(nedenfor); den er endnu ikke i Marketplaces katalog.

## Hvad AIS er

AIS (Automatic Identification System, automatisk identifikationssystem) er
en VHF-udsendelse, som skibe bruger til at fortælle hinanden og land om deres
position, identitet og rejse. Det svarer til ADS-B i luftfarten. Erhvervsskibe
skal have det om bord; mange lystbåde har det frivilligt, som regel som en
svagere klasse B-enhed.

AIS sendes ukrypteret. Alle med en modtager kan høre det, og offentlige
samletjenester genudgiver det.

## Hvad der vises

**Alt, hvad kilden sender.** Intet filtreres fra, og der er ingen indstilling
til at skjule en kategori.

| I dataene | Vist |
|---|---|
| Fragtskibe, tankskibe, slæbebåde, færger, passagerskibe | ja |
| Fiskeri-, lods-, myndigheds- og andre arbejdsfartøjer | ja |
| **Private lystbåde og sejlbåde** | **ja, med navn og position** |
| **Bøjer fra fiskeredskaber**, der sender AIS | **ja, tegnet som en fisk** |
| Eftersøgnings- og redningsfly (SAR) | når kilden sender dem |
| Navigationshjælpemidler: bøjer, båker, fyr | når kilden sender dem |
| AIS-basestationer på land | når kilden sender dem |

### Private både vises, og du bør vide, hvad det betyder

En lystbåd, der sender AIS, vises på dit kort præcis som et fragtskib.
Afhængigt af hvad båden sender, kan dens enhed indeholde:

- dens **navn**, som også er etiketten på kortet
- dens **MMSI** og **kaldesignal**, begge faste og offentligt søgbare
- dens **position** på omkring en meter nær, den forrige position og hvornår
  hver blev hørt
- fart, kurs og retning, når de sendes
- længde, bredde og skibstype, når de sendes

En båd, der lader transponderen være tændt ved kajen, bliver på kortet ved sin
plads, så længe den sender.

Alle, der kan åbne dit kort, kan også trykke på **Track** for sådan en båd og
se, hvor den har været det seneste døgn (eller så længe, du indstiller), ikke
kun hvor den er nu: en båd, der forlod sin plads i morges, viser den plads hele
dagen.

Der findes ingen fravalgsliste for AIS, som der gør for fly, og denne
integration opfinder ikke en. Vil du have færre lystbåde på kortet, så gør
radius mindre.

### Skibstypen mangler ofte, især for små både

Position og navn kommer med næsten hver besked. Skibstype og størrelse kommer
i en særskilt, sjældnere besked, og mange enheder på små både (klasse B)
sender kun sjældent den del, der indeholder dem. Regn med, at en stor del af
skibene, de fleste små iblandt, vises uden type eller mål, og at alle skibe er
mangelfulde i nogle minutter efter en genstart af Home Assistant. Det er
dataene, ikke en fejl. Typer og størrelser, der én gang er hørt, gemmes
gennem genstarter.

### Ikke alt på AIS er et skib

Hver enhed har `object_kind`: `vessel`, `net_buoy`, `aton`
(navigationshjælpemiddel), `base_station`, `sar_aircraft` eller
`distress_beacon`. De fleste kendes på formatet af den identitet, ITU tildeler
dem. Bøjer fra fiskeredskaber gør ikke: de sender med skibslignende
identiteter og kendes derfor på deres fabriksnavne (FISHING BOUY, NET MARK,
BUOY) sammen med, at der ikke sendes nogen længde.

Alt, hvad der ikke er et skib, vises uden skibstype, størrelse eller
navigationsstatus. Bøjer fra fiskeredskaber driver med deres liner; de beholder
derfor fart og kurs og tegnes som en laks, der peger den vej, de driver.

Hvad der vises, afhænger af kilden. Målt en aften:

| Kilde | Bøjer fra fiskeredskaber | SAR-fly | Navigationshjælpemidler, basestationer |
|---|---|---|---|
| BarentsWatch | ja | ja | ingen set |
| Digitraffic | ingen set | ja | ingen set |
| aisstream.io | ingen set | ingen set | ingen set |
| Din egen modtager | hvad den hører | hvad den hører | hvad den hører |

aisstream.io leverede kun positions- og skibsdatabeskeder, både over de Store
Søer og over de samme norske og danske farvande, hvor BarentsWatch viser
bøjerne.

## Kilder

Du vælger én kilde for hvert område, du opretter.

| Kilde | Dækning | Kræver |
|---|---|---|
| aisstream.io | hele verden, hvor frivillige har modtagere kørende | en gratis API-nøgle |
| Fintraffic Digitraffic | finske og baltiske farvande | intet |
| BarentsWatch AIS Live | norske farvande | gratis klient-id og klienthemmelighed |
| Din egen AIS-modtager | så langt din antenne hører | en modtager, der sender NMEA over UDP |

Hvilke kategorier der vises, hvor friske positionerne er, og hvor fuldstændige
skibsdataene er, afhænger af den kilde, du vælger.

### Din egen modtager

Har du en AIS-modtager, kan Live Track Ships vise, hvad den hører, uden konto
og uden internet. Modtageren, eller det program der afkoder den, sender
NMEA-sætninger (`!AIVDM`) over UDP til Home Assistants adresse på en port, du
selv vælger (10110, hvis du ikke ændrer den). I AIS-catcher er det
`-u <address> <port>`, i rtl-ais `-h <address> -P <port>`; OpenCPN og
Signal K tilføjer det som en udgående UDP-forbindelse. En modtager, der
sluttes til med USB, som en dAISy, skal bruge et af de programmer til at
sende sine sætninger videre.

- Ét område lytter på én port; to modtagere skal bruge to porte.
- Alt, hvad modtageren hører inden for din cirkel, vises, også
  navigationshjælpemidler og basestationer. Stationssensoren (nedenfor) tæller
  også, hvad den hører uden for cirklen.
- En sætning har ingen dato, så en positions tid er det øjeblik, Home
  Assistant modtog den.
- Drejehastigheden vises ikke for denne kilde.
- Indtil videre er det testet med optagede sætninger sendt over UDP, ikke med
  en modtager. Prøver du det med din, så fortæl os, hvordan det gik, på
  [issues-siden](https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues).

### Kildeangivelse

Hver skibsenhed og hvert områdes sensor `ships_in_range` har en attribut
`attribution`, der nævner kilden; Home Assistant viser den i enhedens detaljer.
To af kilderne udgiver deres data under en licens, der kræver kildeangivelse,
og Live Track Ships ændrer de data, den modtager (enheder omregnet, kun skibe
inden for din cirkel), så deres linjer siger det. Hvis du viser disse data for
andre, for eksempel på et offentligt dashboard, så behold kildeangivelsen og
læs kildens egne vilkår:

- **aisstream.io**: ingen offentliggjorte vilkår. <https://aisstream.io>
- **Fintraffic Digitraffic**: CC BY 4.0.
  <https://www.digitraffic.fi/en/terms-of-service/>
- **BarentsWatch**: Norsk lisens for offentlige data (NLOD).
  <https://www.barentswatch.no/en/articles/api-terms-and-conditions/>
- **Din egen modtager**: dine egne data; linjen siger det.
- **EnforcementVessels** (listen bag kystvagt-udseendet, nedenfor): ODbL v1.0.
  <https://github.com/StrausbergAutomationWorks/EnforcementVessels>

De præcise linjer står i [ATTRIBUTION.md](ATTRIBUTION.md).

## Krav

- Home Assistant 2026.11 eller nyere, med adgang til internettet for
  onlinekilderne.
- Til aisstream.io: en gratis API-nøgle fra
  [aisstream.io](https://aisstream.io/account). aisstream tillader **tre
  forbindelser pr. konto og tre pr. offentlig IP-adresse**; bruger du andre
  værktøjer med samme nøgle, så tag højde for det. Live Track SALT bruger, hvis
  den er installeret, en anden forbindelse med samme nøgle.
- Til BarentsWatch: et gratis klient-id og en klienthemmelighed, som du selv
  registrerer hos BarentsWatch. Skriv klient-id'et præcis, som det blev udstedt.
- Til din egen modtager: en modtager og et program, der sender NMEA over UDP
  til Home Assistant på samme netværk. Den kræver ikke internet.
- Home Assistant installerer selv de Python-pakker, der skal bruges
  (`saw-livetrack` og `pyais`), første gang integrationen indlæses.

## Installation

### Fra Marketplace

Live Track Ships er endnu ikke i Marketplaces katalog. Tilføj den via et link:

1. **Indstillinger > Marketplace**, derefter **Tilføj fra link**.
2. Skriv `StrausbergAutomationWorks/LiveTrackShips`. Hvis den spørger om
   typen, så vælg **Integration**.
3. Installér **Live Track Ships**.
4. Genstart Home Assistant. Marketplace tilbyder genstarten som en
   reparation under **Indstillinger > System > Reparationer**.

### I hånden

1. Hent kildekoden til den
   [nyeste udgivelse](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest).
2. Kopiér dens mappe `custom_components/live_track_ships` til mappen
   `custom_components` i Home Assistants konfigurationsmappe.
3. Genstart Home Assistant.

## Opsætning

**Indstillinger > Enheder og tjenester > Tilføj integration > Live Track
Ships**, derefter **Alle skibe i et område** (det andet valg, fulgte skibe,
står [længere nede](#fulgte-skibe-følg-udvalgte-skibe-overalt)). Hvert område
er en selvstændig post med titlen *Ships near <bredde>, <længde>*. Dialogen
vises på dansk, når Home Assistant er sat til dansk.

| Felt | Hvad det tager | Standard |
|---|---|---|
| Datakilde | aisstream.io, Fintraffic Digitraffic, BarentsWatch AIS Live eller din egen AIS-modtager | aisstream.io |
| API-nøgle | kun aisstream.io. Hentes fra et område, du allerede har oprettet; kan ændres | tom |
| Klient-id, klienthemmelighed | kun BarentsWatch. Hentes fra et område, du allerede har oprettet | tom |
| UDP-port | kun din egen modtager: den port, den sender NMEA til, 1024 til 65535. Afvises, hvis et andet område eller et andet program allerede bruger den | 10110 |
| Midtpunkt | en markør på et kort; træk den hen til det farvand, du vil følge | dit hjem |
| Radius (km) | 1 til 500 | 50 |
| Højeste antal fulgte skibe | 1 til 5.000; en sikkerhedsgrænse for dette område, de nærmeste beholdes | 1.000 |

Den samme kilde kan ikke følge det samme midtpunkt to gange. Ligger mindst
5 % af en BarentsWatch-cirkel uden for de farvande, BarentsWatch udgiver,
siger dialogen hvor meget, før området oprettes; send formularen for at
beholde cirklen alligevel.

**Et områdes indstillinger** (Konfigurer på dets post): midtpunktet, med den
samme markør; radius; det højeste antal fulgte skibe; og *Højeste antal skibe
på kortet, alle Live Track Ships-poster tilsammen*, en skyder fra 100 til
2.500 i trin på 100 (standard 2.500); og, for din egen modtager, dens UDP-port. Flytter du midtpunktet, får området nyt
navn efter sin position og genindlæses. Den samme kilde kan stadig ikke følge
ét midtpunkt fra to områder.

## Hvad der oprettes

- **Én `geo_location`-enhed pr. skib**, `geo_location.vessel_<MMSI>`, hvis
  tilstand er afstanden til områdets midtpunkt i kilometer. Attributterne
  omfatter navn, MMSI, kaldesignal, fart, kurs, retning, længde, bredde,
  skibstype, destination, `object_kind`, `last_seen` og `attribution`, hver kun
  hvis kilden sendte den. Et skib, som to områder ser, er én enhed.
- **Én sensor pr. område**, `sensor.ships_in_range`, der tæller de viste skibe
  og siger det, når områdets eller hele installationens grænse beskærer
  listen.
- **For din egen modtager endnu en sensor**, `sensor.ais_station`: beskeder
  pr. minut. Dens attributter er `vessels_heard` (de seneste 10 minutter),
  `farthest_km` og `farthest_mmsi` (fra områdets midtpunkt), `last_message`,
  `udp_port`, `listening` og `port_error`, når porten ikke kan åbnes. Den
  opdateres hvert 30. sekund, så en modtager, der holder op med at sende,
  viser 0.

Et skib, der høres uden for din cirkel, forsvinder straks fra kortet. For at
høre det bliver hver onlinekilde bedt om en ring lidt større end din cirkel (10 %,
mindst 1 km), og din egen modtager sender alt, hvad den hører; kun skibe inden for din cirkel beholdes. Et skib, der ikke høres
igen, forsvinder efter en periode med stilhed, og et skib, der holder op med
at blive vist, er ikke nødvendigvis væk (nedenfor).

### Din database

Home Assistants recorder gemmer en ny række, hver gang en entitet ændrer sig,
og et skib i fart ændrer sig med hver position, det melder. Denne integration
kan derfor få din database til at vokse hurtigt: på vores testsystem skrev ét
område med 43 skibe 27.109 tilstandsrækker på omkring 30 timer, 8,8 % af hele
databasen. Som standard gemmer recorderen 10 dage og rydder op hver nat kl.
04:12, så væksten flader ud, men ved en størrelse, du måske ikke ønsker.
Hvert skibs `marker_photo`, `marker_links` og `marker_track` og sensorernes hurtigt skiftende
attributter bliver aldrig gemt.

Et skib beholder det samme entitets-id, `geo_location.vessel_<MMSI>`, hver gang
det dukker op: en færge, der sejler og kommer tilbage, genbruger sin entitet i
stedet for at tilføje en ny. Ét mønster, `geo_location.vessel_*`, dækker derfor
alt, hvad denne integration nogensinde har sat på kortet. For kun at beholde
det seneste døgn kører du `recorder.purge_entities` efter en tidsplan, for
eksempel med denne automatisering:

```yaml
alias: Afkort skibshistorik
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

Udelader du `keep_days` (standard 0), forsvinder alle deres rækker på én gang.
For slet ikke at gemme noget af det sætter du mønsteret under `recorder:` →
`exclude:` → `entity_globs:` i `configuration.yaml`. Et kortkort, der er sat
til at tegne historik (`history_start`), har så intet spor at tegne.
`sensor.ships_in_range` er et rent tal og billigt at gemme, så dens historik
overlever i begge tilfælde.

## Hændelser: et skib kommer ind i dit område eller forlader det

Hvert område sender to hændelser i Home Assistant, så en automatisering kan
fortælle dig, når et skib, du interesserer dig for, ankommer:

- `live_track_ships_entry`, når et skib kommer ind i områdets cirkel
- `live_track_ships_exit`, når det forlader den

Integrationen melder alle skibe; din automatisering vælger dem, der betyder
noget. Hændelsens data har samme navne og enheder som skibets attributter og
udelader det, kilden ikke sendte:

| Felt | Indhold |
|---|---|
| `area_id`, `area` | id'et på områdets konfigurationspost og dets titel |
| `identity` | MMSI'en |
| `name`, `call_sign`, `imo` | når de sendes |
| `object_kind` | `vessel`, `net_buoy`, `aton`, `base_station`, `sar_aircraft` eller `distress_beacon` |
| `ship_type`, `ship_type_label`, `length_m`, `beam_m`, `draught_m`, `destination`, `nav_status` | kun skibe, når de sendes |
| `speed_kmh`, `course_deg`, `heading_deg` | når de sendes |
| `latitude`, `longitude`, `distance_km`, `bearing_from_centre_deg`, `last_seen` | hvor det blev hørt, set fra områdets midtpunkt |
| `entity_id` | kun ved ankomst: `geo_location.vessel_<MMSI>`, når skibet er på kortet |
| `reason` | kun ved afgang: `left` (hørt uden for cirklen) eller `silent` (ikke hørt i opbevaringstiden, så det kan stadig være der) |

Fire ting, du bør vide:

- **En ankomst meldes kun, hvis skibet først er hørt uden for cirklen**, i
  ringen omkring den. Et skib, der først høres inde i cirklen, kan have ligget
  der hele tiden: efter en genstart bliver modtagerne ved i mange minutter med
  at levere skibe, der aldrig har flyttet sig. Et skib, som modtagerne ikke
  hørte på vej ind, eller et, der først tænder sin transponder inde i cirklen,
  meldes derfor ikke.
- **En afgang, der høres udenfor, meldes altid**, også for et skib, der var
  der, før Home Assistant startede. Et skib, der tier, meldes kun ude
  (`reason: silent`), hvis dets ankomst blev meldt.
- **En afgang venter 2 minutter.** Et skib, der vender tilbage inden da, langs
  cirklens kant, meldes ikke ud og ind igen.
- **Ved ankomsten kan oplysninger mangle.** Navn, type og størrelse kommer i en
  sjældnere besked end positionen (ovenfor). Et skib, der høres for første
  gang, kan ankomme med en position og intet andet; et, der er hørt før, har
  som regel type og størrelse med.

To områder over det samme farvand sender hver deres egne hændelser.
Grænserne for, hvor mange skibe kortet tegner, får aldrig et skib til at
komme ind eller forsvinde.

En automatisering, der giver besked, når et skib over 150 m kommer ind i et
område:

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
      title: "{{ trigger.event.data.name | default('Et skib') }}"
      message: >-
        {{ trigger.event.data.ship_type_label | default('Skib') }},
        {{ trigger.event.data.length_m }} m,
        {{ trigger.event.data.distance_km }} km væk, på vej ind i
        {{ trigger.event.data.area }}.
```

## Fulgte skibe: følg udvalgte skibe overalt

Ud over områder kan du følge en liste af skibe, hvor de end er: et
familiemedlems båd, en færge du tager, et krydstogtskib på vej hjem.
**Indstillinger > Enheder og tjenester > Tilføj integration > Live Track
Ships > Udvalgte skibe, hvor de end er.** Det kræver en nøgle fra aisstream.io
(nøglen fra et område, du allerede har oprettet, er udfyldt), og der er én
sådan liste pr. Home Assistant.

Ét skib pr. linje: dets 9-cifrede MMSI og eventuelt et navn efter eget valg.

```text
244650000 Fars båd
366999999 Færgen
```

Højst 100 skibe. aisstream følger højst 200 MMSI'er pr. nøgle, og
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT)
bruger, hvis den er installeret med samme nøgle, en del af dem; en liste, der
ville gå over, afvises, når posten indlæses, med begrundelsen. Ret listen i
postens indstillinger.

Et fulgt skib tegnes på kortet som alle andre, hvor end det høres, og dets
tilstand er afstanden til dit hjem. Et område, der allerede viser det,
beholder det: ét skib, én markør. Posten opretter `sensor.watched_vessels`:
hvor mange af skibene på listen der høres lige nu, med hvert af dem, dit navn
for det og dets seneste kendte tilstand i attributten `vessels`.

Den sender én hændelse, `live_track_ships_watched`, hvis felt `change` siger,
hvad der skete:

| `change` | Hvornår |
|---|---|
| `arrived` | skibet melder sig fortøjet eller til ankers, eller bliver uden status under 2 knob |
| `departed` | det er i fart igen |
| `silent` | ikke hørt i 30 minutter (6 timer, hvis det er fortøjet eller til ankers); det forsvinder fra kortet og kan stadig være der |
| `heard` | hørt igen efter `silent` |
| `destination` | besætningen har ændret destinationen; `destination_previous` indeholder den gamle |

Dataene har `watch_id`, `watch`, `identity`, dit navn `label` og de samme
skibsfelter som områdehændelserne, med afstand og retning fra dit hjem.
Ankomst og afgang venter, til den nye tilstand har holdt i 5 minutter efter
skibets eget ur, så en båd, der driver med 2 knob, ikke skifter frem og
tilbage. Der meldes intet ud fra et skibs første position efter en genstart:
den fastlægger udgangspunktet. Destinationer tastes ind af besætningen og er
ofte forældede.

## Kortkort

Skibene tegnes af [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)
(`custom:live-track-map-card`), det ene kort, som alle Live
Track-integrationer tegner på. Det tegner hvert skibs eget billede, drejer det
efter skibets retning og lader det glide mellem rigtige positioner hen over
vandet i stedet for lige hen over land.

**Kortet installeres sammen med integrationen.** Integrationen har en udgivet
kopi af kortet med, stiller den til rådighed og registrerer den som
dashboard-ressource, når Home Assistant starter; der er intet at hente eller
kopiere ind i `www`. Alle Live Track-integrationer gør det samme, og sammen
holder de præcis én ressourcelinje: den højeste kortversion, nogen af dem har
med, aldrig en ældre. Et kort, der er installeret via Marketplace, røres ikke.
Fjernes det sidste område i denne integration, går linjen videre til en anden
Live Track-integration, eller den fjernes, hvis der ikke er flere. Se kortets
README, afsnittet
[Live Track](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).

Er dine dashboards' ressourcer sat i YAML (`lovelace: resource_mode: yaml`),
kan intet registreres for dig. En reparation giver så den præcise linje, der
skal tilføjes; den ser sådan ud, med integrationens egen adresse i stedet for
pladsholderne:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_ships/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Fjernes integrationens filer (for eksempel via Marketplace), mens dens
områder stadig er oprettet, og er ingen anden Live Track-integration
installeret, er der intet tilbage til at rydde linjen op: fjern den under
Indstillinger > Dashboards > Ressourcer. Vil du hellere installere kortet i
hånden, så følg kortets README; ressourcelinjen for en kopi, der er
installeret i hånden under `/local/`, peges kun over på en integrations kopi,
når den er en nyere udgivelse.

Giv det skibene med
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities),
filtreret på `domain: geo_location` og `attributes: {source: live_track_ships}`.
Er andre Live Track-integrationer installeret, så tilføj et filter for hver af
deres kilder.

Ethvert andet kortkort, der viser `geo_location`-enheder, viser også skibene,
uden kortets billeder og glidninger.

Et skib på den offentlige liste
[EnforcementVessels](https://github.com/StrausbergAutomationWorks/EnforcementVessels)
(kystvagtskibe, der bruges i immigrationsarbejde) tegnes i kystvagtens farver
med listens navn og myndighed, hvor end det er.

### Skjul skibstyper

Hvert skib har `marker_group`, `marker_group_label` og `marker_group_order`:
en af tretten grupper (fragt; tankskib; passagerer og færger; fiskeri;
lystsejlads og sejlbåde; slæbebåde, lodser og havnetjeneste; myndigheder, SAR
og politi; hurtigfærger og andet; type ikke sendt; bøjer på fiskeredskaber;
navigationshjælpemidler; basestationer; SAR-fly). Kortkortets filterkort,
`custom:live-track-map-filter-card`, viser dem med hvor mange af hver der er
på kortet og skjuler dem, du fjerner fluebenet fra; sæt det på en hvilken som
helst visning af dashboardet. Dit valg gemmes kun i den browser.
Integrationen viser stadig alt: dens sensor tæller hvert skib, og dens
hændelser udløses for hvert skib. En nødradiobøje har ingen gruppe, så den
skjules aldrig.

### Fotos og links

Når et skib sender et IMO-nummer, og Wikidata kender et foto af skibet på
Wikimedia Commons, har skibet `marker_photo`. Kortet viser fotoet i
hover-boksen med fotograf og licens; et klik åbner det større, med links til
fotoets side og til licensen. Hvert skib med et IMO-nummer eller et MMSI har
også `marker_links`, et link til skibet på VesselFinder. Knappen **Details** i
vinduet åbner skibets sædvanlige dialog. Din Home Assistant spørger selv
Wikidata og Commons, 20 IMO-numre ad gangen med ti sekunders mellemrum, og
gemmer hvert svar i 30 dage (14, når der ikke er noget foto) i
`.storage/saw_vessel_photos.json`. Regn med fotos for omtrent hvert tiende
skib: på vores testsystem havde 49 af 521 IMO-numre et.

### Spor

Hvert skib har også `marker_track`. Klik på et skib, og tryk på **Track** i
dets vindue: kortet tegner, hvor det har været, som én linje, der ender ved
skibet og vokser, mens du ser på; **Hide track** fjerner den. Intet tegnes, før
du beder om det, så en travl havn aldrig forsvinder under streger. Sporet
rummer kun positioner, som skibet har meldt, mens det var på dit kort, udtyndet
til én for hver 25 m eller 10 minutter og aldrig to inden for 30 sekunder. Din
Home Assistant holder det i hukommelsen og gemmer det i
`.storage/saw_vessel_tracks.json`, så det overlever en genstart. Det dækker det
seneste døgn. Vil du gemme mere eller mindre, så kør handlingen
`live_track_ships.set_track_hours` med `hours` fra 1 til 168 (en uge), for
eksempel fra Udviklerværktøjer > Handlinger:

```yaml
action: live_track_ships.set_track_hours
data:
  hours: 72
```

Det gælder alle områder på én gang; en kortere indstilling sletter ældre
positioner med det samme. Home Assistants recorder gemmer ikke sporene.

## Hvor den kigger

Du sætter et **midtpunkt og en radius** på kortet. Midtpunktet kan ligge hvor
som helst i verden; radius kan være 1 til 500 km. Standard er **50 km**. Hvert
skibs tilstand er afstanden til dit midtpunkt.

Hvor mange skibe en cirkel rummer, afhænger langt mere af *hvilket farvand*
end af *hvor stor*. I test rummede en cirkel på 50 km omkring 4 skibe over
Chicago og omkring 340 over Solent i det sydlige England: samme radius, cirka
80 gange så meget trafik. Derfor beholder integrationen højst et fastsat antal
skibe (1.000 som standard, kan sættes op til 5.000), beholder de nærmeste, når
der er flere, og siger det på sin sensor `ships_in_range`.

Alle dine områder **tilsammen** viser højst 2.500 skibe, uanset kilde. Hvert
områdes indstillinger har skyderen fra ovenfor, som kun kan sænke den grænse;
den laveste indstilling på et aktiveret område gælder. Sænk den på
langsommere maskiner.

## Dækning, målt i stedet for lovet

Dækningen er god, hvor der er modtagere, og fraværende, hvor der ikke er, og
**ingen indstilling kan skabe dækning, der ikke findes**.

Målt 2026-09-02 omkring Chicago med aisstream.io:

- **De Store Søer**: 100 forskellige skibe på 120 sekunder, alle fem søer og
  farvandene imellem.
- **Chicago River, midtbyen**: travl og pålidelig.
- **Chicago Sanitary and Ship Canal, Cal-Sag Channel, Calumet River**: en time
  med lytning, **nul skibe**. Kanalen er ikke tom: dens skubbeslæb kan ses hos
  kommercielle tjenester via satellit-AIS, som gratis samletjenester ikke har.
  Trafikken er virkelig; dækningen fra land er ikke.

Ingen skibe i dit område kan betyde, at der ikke er modtagere, snarere end at
der ikke er både. Tjek, at din kilde dækker dit farvand, før du antager, at
integrationen er i stykker.

Et skib, der holder op med at blive vist, er ikke nødvendigvis væk. Ingen af
disse kilder garanterer levering, så integrationen viser, hvornår hvert skib
sidst blev hørt, og fjerner det først efter en periode med stilhed.

## Skibe, der fortjener deres eget billede

De fleste skibe tegnes efter deres type. Nogle har deres eget billede:
kongelige og statslige skibe som Kongeskibet Dannebrog, og kendte både som
Chicagos udflugtsbåde, vandtaxaer og brandbåde. Kender du et skib, der
fortjener ét, hvor som helst i verden? Opret en issue på
<https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues> med navn
og MMSI- eller IMO-nummer, gerne med et foto eller et link.

## Sprog

Denne README: [English](README.md), [Deutsch](README.de.md),
[Français](README.fr.md), [Nederlands](README.nl.md),
[简体中文](README.zh-Hans.md), [Español](README.es.md),
[Italiano](README.it.md), **Dansk** og [Kalaallisut](README.kl.md) (et udkast,
sendt til gennemlæsning hos Oqaasileriffik, Grønlands sprogsekretariat; indtil
da er den danske side den pålidelige). README'en er oversat til en kort liste
af sprog: dem, de fleste Home Assistant-brugere læser, og et par flere, hvor
der er en god grund. Hver oversat README er fuldstændig: alt i den engelske
står i hver af dem, og ingen sender dig tilbage til engelsk for detaljerne.

Opsætningsdialogen og et områdes indstillinger vises på dit Home
Assistant-sprog, når det er et af disse: English, Dansk, Deutsch, Español,
Français, Gaeilge, Íslenska, Italiano, Nederlands, Norsk Bokmål, Polski,
Português, Português (BR), Suomi, Svenska og 简体中文. Ethvert andet sprog viser
den engelske dialog. Kalaallisut er endnu ikke et Home Assistant-sprog; vi har
bedt Home Assistant om at tilføje det, og dialogen følger, så snart den kan
vises.

Har du fundet en fejl i en oversættelse, der ændrer meningen eller læses
dårligt? Skriv til os på
<https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues>.
Oversættelserne er skrevet til dette projekt, og ikke alle er endnu læst af en
person med sproget som modersmål.

**Har du svært ved at følge med på et af disse sprog?** Bed om et andet på samme
adresse, så prøver vi at imødekomme dig.

## En del af Live Track

Live Track er en række Home Assistant-integrationer, én for hver slags ting,
der bevæger sig, og alle tegner på samme kort. De deler et Python-bibliotek
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore))
og kortet, så endnu en integration ikke sender flere forespørgsler til en
fælles kilde. Udgivet:
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft),
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
[Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail),
[Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail)
og Live Track Ships. Hver virker også alene.

## Ingen tilknytning

Ikke tilknyttet aisstream.io, Fintraffic, BarentsWatch, MarineTraffic,
VesselFinder, noget rederi eller nogen søfartsmyndighed. AIS er et system for
sikkerheden til søs; **denne integration er til interesse og ikke til
navigation, undgåelse af kollisioner eller noget driftsformål.**

## Licens

Kode: MIT, i [LICENSE](LICENSE). Kildeangivelser for data og grafik:
[ATTRIBUTION.md](ATTRIBUTION.md).

## Nøgleord

Home Assistant AIS · skibssporing · skibe på kortet · bådsporing · skibstrafik
live · AIS-kort · aisstream.io · Digitraffic · BarentsWatch · geo_location ·
HACS-integration
