# Live Track Ships

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · **Dansk** · [Kalaallisut](README.kl.md) · [Alle sprog](#sprog)

**Skibe og både til Home Assistant, på ét kort.** Live Track Ships sætter
skibe, både og alt andet, der sender AIS (det radiosignal, skibe bruger til at
fortælle, hvor de er), på dit Home Assistant-kort, nær dig eller hvor som
helst i verden, du vælger. Den følger også udvalgte skibe, hvor de end sejler
hen, og fortæller dine automatiseringer, når et skib kommer ind i dit område
eller forlader det.

> **Live Track Ships er ét modul i Live Track**, en familie af Home
> Assistant-integrationer, der tegner alt, hvad der bevæger sig, og det vejr,
> det bevæger sig igennem, på ét fælles kort: fly, skibe, tog og vejr.
> Installer det alene eller ved siden af de andre moduler
> ([liste nedenfor](#en-del-af-live-track-de-andre-moduler)).

> **Den vokser, og idéer er velkomne.** I dag dækker Live Track Ships hele
> verden, hvor frivillige driver modtagere, Finland og Norge mere detaljeret,
> og din egen modtager. Vi tilføjer flere datakilder og lande. Mangler dit?
> [Foreslå det](#hjælp-den-med-at-vokse), eller tilføj det selv: vi hjælper
> dig med det.

**Status: 0.1.4, udgivet.** I Markedspladsens katalog ([installer det
nedenfor](#installation-trin-for-trin)).

Eget værk af StrausbergAutomationWorks. Ikke tilknyttet eller godkendt af
aisstream.io, Fintraffic (Finland), BarentsWatch (Norge), Wikidata, Wikimedia
Commons, VesselFinder, MarineTraffic, nogen skibsoperatør eller nogen
søfartsmyndighed.

> ⚠ **Ikke et sikkerhedssystem.** Den viser offentlige data, ofte sekunder
> gamle og nogle gange minutter, og kun det, modtagerne tilfældigvis hører.
> Den er ikke til navigation, undgåelse af kollisioner eller noget andet
> operationelt formål. På vandet skal du bruge dit eget AIS, radar, søkort og
> VHF-radio.

---

## Indhold

1. [Alt, hvad den gør](#alt-hvad-den-gør)
2. [Hvor den virker](#hvor-den-virker)
3. [En del af Live Track: de andre moduler](#en-del-af-live-track-de-andre-moduler)
4. [Før du begynder](#før-du-begynder)
5. [Installation, trin for trin](#installation-trin-for-trin)
6. [Opsætning, trin for trin](#opsætning-trin-for-trin)
7. [Gratis nøgler, der slår mere til, trin for trin](#gratis-nøgler-der-slår-mere-til-trin-for-trin)
8. [Sæt kortet på et dashboard](#sæt-kortet-på-et-dashboard)
9. [Brug den i automatiseringer](#brug-den-i-automatiseringer)
10. [Alt på kortet i detaljer](#alt-på-kortet-i-detaljer)
11. [Alle entiteter, den opretter](#alle-entiteter-den-opretter)
12. [Hvad den sender og henter](#hvad-den-sender-og-henter)
13. [Hjælp den med at vokse](#hjælp-den-med-at-vokse)
14. [Sprog](#sprog)
15. [Tak og licenser](#tak-og-licenser)
16. [Nøgleord](#nøgleord)

---

## Alt, hvad den gør

### På kortet, uden at sætte noget op

Du tilføjer et **område**: et midtpunkt og en radius på kortet, og én
datakilde. Alt nedenfor vises så i det område. Fintraffic Digitraffic
(Finland) og din egen modtager kræver ingen nøgle; aisstream.io og
BarentsWatch (Norge) kræver en gratis nøgle
([nedenfor](#med-din-egen-gratis-nøgle-eller-konto)).

| Hvad | Hvor | Fra |
|---|---|---|
| **Skibe**: fragtskibe, tankskibe, færger, slæbebåde, fiskefartøjer, lystbåde og sejlbåde, hver med sit eget billede, drejet efter sin kurs | i hvert område | den kilde, du vælger |
| **Det, der ikke er skibe**: bøjer på fiskeredskaber, navigationshjælpemidler, AIS-basestationer, rednings- og eftersøgningsfly og nødradiofyr | i hvert område, når kilden sender dem | den kilde, du vælger |
| **Fotos og links**: et foto af skibet, når et er kendt, og et link til skibet på VesselFinder | hvert skib med IMO-nummer eller MMSI | Wikidata og Wikimedia Commons |
| **Spor**: hvor et skib har været de seneste 24 timer, tegnet når du beder om det | hvert skib | gemt af din egen Home Assistant |
| **Kystvagtens skibe i udlændingeopgaver**, tegnet i kystvagtens farver | hvor end de høres | den offentlige liste EnforcementVessels |
| **Ankomster og afgange**: en hændelse til dine automatiseringer, når et skib kommer ind i et område eller forlader det | i hvert område | beregnet af din egen Home Assistant |

### Med din egen gratis nøgle eller konto

| Gratis nøgle eller konto | Hvad den tilføjer |
|---|---|
| **aisstream.io**-nøgle | skibe overalt i verden, hvor frivillige driver modtagere; og **fulgte skibe**: udvalgte skibe, fulgt hvor de end er, med en hændelse, når et ankommer, afgår, bliver tavst eller skifter destination |
| **BarentsWatch**-konto (Norge) | skibe i norske farvande, Svalbard medregnet, med navn og skibstype ved hver position |

Hver tager få minutter at få: [trin for trin nedenfor](#gratis-nøgler-der-slår-mere-til-trin-for-trin).

---

## Hvor den virker

| Region | Hvad du får | Fra | Kræver |
|---|---|---|---|
| **Hele verden** | skibe, hvor frivillige driver modtagere: godt ved travle kyster og havne, sparsomt eller intet andre steder | aisstream.io | en gratis nøgle |
| **Europa**: Finland og Østersøen | skibe i finske og baltiske farvande, nye positioner hvert minut | Fintraffic Digitraffic (Finland) | intet |
| **Europa**: Norge | skibe i norske farvande, Svalbard medregnet, med navn og type ved hver position | BarentsWatch (Norge) | en gratis konto |
| **Din egen modtager**: overalt | alt, hvad din antenne hører, uden internet | din egen AIS-modtager | en modtager, der sender NMEA over UDP |

Du vælger én kilde til hvert område. Hvilke slags ting der vises, hvor friske
positionerne er, og hvor fuldstændige skibsdata er, afhænger alt sammen af den
kilde.

⚠ **Dækningen er god, hvor der er modtagere, og fraværende, hvor der ikke
er.** Ingen indstilling kan skabe dækning, der ikke findes. Målt 2026-09-02
med aisstream.io omkring Chicago (USA): 100 skibe på 120 sekunder på de Store
Søer, men nul skibe på en time i kanalerne syd for byen, hvor der ellers
sejler pramme: kommercielle tjenester ser dem via satellit, og det har gratis
kilder ikke. **Ingen skibe i dit område kan betyde ingen modtagere, ikke
ingen både.** Tjek, at din kilde dækker dit farvand, før du beslutter, at
noget er i stykker.

⚠ **Din egen modtager:**

* Ét område lytter på én port. To modtagere kræver to porte.
* Alt, hvad modtageren hører inden for din cirkel, vises, også
  navigationshjælpemidler og basestationer. Dens stationssensor tæller også,
  hvad den hører uden for cirklen.
* En NMEA-sætning har ingen dato, så en positions tid er det tidspunkt, Home
  Assistant modtog den.
* Drejehastigheden vises ikke for denne kilde.
* Indtil videre er dette testet med optagede sætninger sendt over UDP, ikke
  med en modtager. Hvis du prøver det med din,
  [så fortæl os, hvordan det gik](#hjælp-den-med-at-vokse).

Ikke på listen? [Fortæl os det](#hjælp-den-med-at-vokse). Hvor nogen
offentliggør data åbent, ser vi på at tilføje dem.

---

## En del af Live Track: de andre moduler

Live Track er en række Home Assistant-integrationer, én for hver slags ting,
der bevæger sig, alle tegnet på det samme kortkort. Hver virker for sig;
sammen giver de ét levende billede. De deler kortkortet og et Python-bibliotek
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
så installerer du endnu et modul, kommer der ingen ekstra forespørgsler til en
kilde, som et andet allerede læser.

| Modul | Hvad det sætter på kortet | Status |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | fly over dig via ADS-B, med ruter og typeikoner | udgivet |
| **Live Track Ships** | skibe og både via AIS, nær dig eller hvor som helst (dette modul) | udgivet |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | nærbanetog i Nordamerika, Europa og Australien | udgivet |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | intercity- og fjerntog i Nordamerika, Europa og Australien | udgivet |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | fly og skibe fra udlændinge- og føderale ordensmyndigheder, fra offentlige lister | udgivet |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | vejr, storme og naturfarer | udgivet |
| [Live Track Internet](https://github.com/StrausbergAutomationWorks/LiveTrackInternet) | internetudfald, søkabler og landkabler | udgivet |
| Live Track Stations | afgangstavler og "tid til at gå"-påmindelser for hver station | planlagt |
| Live Track Satellites | satellitter, der passerer over dig | planlagt |
| Live Track Freight Trains | gods- og arbejdstog, hvor jernbaner offentliggør dem | planlagt |
| Live Track Transit | bybusser, sporvogne, færger og metro | planlagt |
| Live Track Intercity Buses | fjern- og regionalbusser | planlagt |
| Live Track Commuter Buses | pendlerbusser | planlagt |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | det fælles kortkort, som hvert modul tegner på | udgivet, installeres med hvert modul |

Alt er gratis og open source. Intet holdes tilbage til sponsorer.

---

## Før du begynder

* **Home Assistant** 2026.11 eller nyere.
* **Markedspladsen** (HACS) i din Home Assistant, så du nemt kan installere
  og opdatere. Uden den kan du kopiere filerne manuelt.
* **Internetadgang** for Home Assistant, til onlinekilderne og fotoene. Din
  egen modtager virker uden.
* **En datakilde.** Digitraffic (Finland) og din egen modtager kræver ingen
  konto. aisstream.io og BarentsWatch (Norge) kræver en gratis nøgle
  ([trin for trin](#gratis-nøgler-der-slår-mere-til-trin-for-trin)).
* **Valgfrit: din egen AIS-modtager.** Modtageren, eller det program, der
  afkoder den, sender NMEA-sætninger (`!AIVDM`) over UDP til din Home
  Assistants adresse på det samme netværk. I AIS-catcher er det
  `-u <address> <port>`; i rtl-ais `-h <address> -P <port>`; OpenCPN og
  Signal K tilføjer det som en UDP-udgangsforbindelse. En modtager, der
  sluttes til via USB, for eksempel en dAISy, skal bruge et af de programmer
  til at sende sine sætninger videre.
* Intet at betale. Digitraffic og din egen modtager kræver ingen konto; de
  gratis nøgler skal kun bruges til aisstream.io og BarentsWatch.

---

## Installation, trin for trin

### Fra Markedspladsen (anbefalet)

1. Åbn **Indstillinger → Markedsplads** (HACS) i Home Assistant.
2. Søg efter **Live Track Ships**, og åbn det.
3. Vælg **Download** (eller **Installer**).
4. **Genstart Home Assistant**: **Indstillinger → System → Reparationer**
   tilbyder genstarten, eller brug **Indstillinger → System → Genstart**.

Hvis søgningen ikke finder det, så tilføj det via dets link: vælg **Tilføj fra
link** (eller menuen med tre prikker → **Brugerdefinerede repositories**), skriv
`StrausbergAutomationWorks/LiveTrackShips`, vælg **Integration**, hvis du bliver
spurgt om typen, og fortsæt derefter fra trin 3.

Markedspladsen tilbyder derefter hver ny udgivelse som en opdatering.

### Manuelt

1. Hent kildekoden til den
   [seneste udgivelse](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest).
2. Kopiér mappen `custom_components/live_track_ships` fra den over i mappen
   `custom_components` i din Home Assistants konfigurationsmappe (opret
   `custom_components`, hvis den ikke findes).
3. Genstart Home Assistant.

---

## Opsætning, trin for trin

1. Åbn **Indstillinger → Enheder & tjenester**.
2. Vælg **Tilføj integration** (nederst til højre), og søg efter **Live Track
   Ships**.
3. Vælg **Alle skibe i et område**. (Det andet valg, **Udvalgte skibe, hvor de
   end er**, følger en liste af skibe overalt: se
   [Fulgte skibe](#fulgte-skibe-udvalgte-skibe-overalt).)
4. **Datakilde**: vælg én. Er du i tvivl: i Finland Fintraffic Digitraffic,
   som ikke kræver nøgle; i Norge BarentsWatch; alle andre steder
   aisstream.io.
5. **API-nøgle** (aisstream.io), eller **Klient-id** og **Klienthemmelighed**
   (BarentsWatch): indsæt dem
   ([sådan får du dem](#gratis-nøgler-der-slår-mere-til-trin-for-trin)). Et
   område, du allerede har sat op, udfylder dem for dig.
6. **UDP-port (din egen modtager)**: kun til din egen modtager. Skriv den
   port, den sender til, fra 1024 til 65535. Lad 10110 stå, hvis du ikke har
   ændret den.
7. **Midtpunkt**: træk markøren til midten af det farvand, du vil holde øje
   med. Den starter ved dit hjem.
8. **Radius (km)**: fra 1 til 500 km (0,6 til 310 miles). Er du i tvivl, så
   behold 50 km (31 miles).
9. **Højeste antal fulgte skibe**: behold 1.000, medmindre din maskine er
   lille.
10. Vælg **Indsend**.

Det er det hele. Skibene vises inden for et minut eller to, efterhånden som
kilden sender dem. Skibstyper og størrelser kommer til i de næste minutter.
Hvert område er én post med titlen *Ships near <latitude>, <longitude>*.
Tilføj flere områder på samme måde.

* Den samme kilde kan ikke holde øje med det samme midtpunkt to gange.
* Ligger mindst 5 % af en BarentsWatch-cirkel uden for de farvande,
  BarentsWatch offentliggør, siger dialogen hvor meget, før området oprettes.
  Vælg **Indsend** for at beholde cirklen alligevel.

### Ændr, hvad den viser: indstillingerne

Åbn **Indstillinger → Enheder & tjenester → Live Track Ships → Konfigurér**
(tandhjulet) på det område, du vil ændre. Hver indstilling, i almindelige
ord:

| Indstilling | Hvad den gør | Standard |
|---|---|---|
| **Midtpunkt** | flytter området; det omdøbes efter sin nye position og genindlæses | dit hjem |
| **Radius (km)** | hvor langt fra midtpunktet skibe vises, 1 til 500 km (0,6 til 310 miles) | 50 km (31 miles) |
| **Højeste antal fulgte skibe** | en sikkerhedsgrænse for dette område, 1 til 5.000; er der flere, beholdes de nærmeste | 1.000 |
| **Højeste antal skibe på kortet, alle Live Track Ships-poster tilsammen** | loftet for alle dine områder tilsammen, 100 til 2.500; sænk det på en lille maskine; den laveste indstilling på noget område gælder | 2.500 |
| **UDP-port (din egen modtager)** | den port, din modtager sender til; ændres den, genindlæses området | 10110 |

Hvor mange skibe en cirkel rummer, afhænger langt mere af, hvilket farvand det
er, end af hvor stor den er. I test rummede en cirkel på 50 km (31 miles)
omkring 4 skibe over Chicago (USA) og omkring 340 over Solent (England): samme
radius, omkring 80 gange så meget trafik. Når en grænse skærer listen ned,
siger områdets `sensor.ships_in_range` det.

---

## Gratis nøgler, der slår mere til, trin for trin

De er alle gratis og personlige: hver person, der installerer Live Track
Ships, får sine egne. Indsæt hver af dem i opsætningsdialogen, når du tilføjer
et område (trin 5 i [Opsætning](#opsætning-trin-for-trin)).

### aisstream.io (skibe og fulgte skibe, hele verden)

1. Åbn <https://aisstream.io/account>, og log ind. (Linket **API keys** øverst
   på aisstream.io åbner samme side.)
2. Opret en ny API-nøgle der.
3. Kopiér nøglen med det samme: aisstream.io viser den kun én gang.
4. Indsæt den i **API-nøgle**.

⚠ aisstream.io tillader tre forbindelser pr. konto og tre pr. offentlig
internetadresse. Live Track Ships bruger højst to: én til alle dine områder og
én til dine fulgte skibe, som den deler med Live Track SALT, hvis det er
installeret med samme nøgle. Bruger andre programmer samme nøgle eller samme
internetforbindelse, så tæl dem med.

### BarentsWatch (skibe i norske farvande, Norge)

1. Åbn <https://www.barentswatch.no/minside/>, og opret en bruger, eller log
   ind.
2. Under **API access (for developers)** (*API-tilgang (for utviklere)*) vælger
   du **New Client** (*Ny klient*).
3. Vælg AIS-klienten, ikke API-klienten.
4. Kopiér **klient-id'et**. Det ser sådan ud:
   `your.email@example.com:live_track_ships`. Indsæt det præcis, som det er, i
   **Klient-id**.
5. Kopiér **klienthemmeligheden** til **Klienthemmelighed**. Den vises kun én
   gang; har du ikke gemt den, så lav en ny.

---

## Sæt kortet på et dashboard

Kortet er [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
det kort, som hvert Live Track-modul tegner på. **Det installeres med Live
Track Ships**: intet at hente, intet at kopiere, ingen ressource at tilføje.

1. Åbn et betjeningspanel, vælg blyanten (**Redigér betjeningspanel**), og
   derefter **Tilføj kort**.
2. Rul ned til bunden, og vælg **Manuel**.
3. Indsæt dette, og vælg **Gem**:

```yaml
type: custom:live-track-map-card
entity_filter:
  include:
    - domain: geo_location
      attributes:
        source: live_track_ships
```

Andre Live Track-moduler kommer i `entity_filter` på samme måde: én regel
`- domain: geo_location` mere for hver kilde.

**På kortet:**

* Hvert skib tegnes med sit eget billede, drejet efter sin kurs, og glider
  mellem sine meldte positioner hen over vandet i stedet for over land.
* **Peg** på et skib for at se dets navn, og dets foto, når der er et.
  **Klik** på det for at se foto, links, **Track** og **Details**
  ([Fotos og links](#fotos-og-links), [Spor](#spor)).
* **Filterkortet** (`custom:live-track-map-filter-card`) skjuler de
  skibstyper, du fjerner fluebenet fra ([Skjul skibstyper](#skjul-skibstyper)).

Er dine betjeningspanelers ressourcer sat op i YAML
(`lovelace: resource_mode: yaml`), kan intet registreres for dig: en
meddelelse under **Reparationer** giver så den præcise linje, du skal
tilføje. Et kort, du selv har installeret via Markedspladsen, får lov at være.
Fjernes integrationens filer, mens dens områder stadig er sat op, og er intet
andet Live Track-modul installeret, så fjern selv kortets linje under
**Indstillinger → Betjeningspaneler → Ressourcer**. Ethvert andet kortkort,
der viser `geo_location`-entiteter, viser også skibene, uden deres billeder.

---

## Brug den i automatiseringer

Alt er almindelige Home Assistant-entiteter og -hændelser, så
automatiseringseditoren virker med dem, uden kode.

**En notifikation, når et skib på over 150 m (490 fod) kommer ind i dit
område:**

1. **Indstillinger → Automatiseringer & scener → Tilføj automatisering →
   Opret ny automatisering**.
2. **Når**: **Tilføj udløser**, søg efter **Manuel hændelse modtages**, og
   skriv `live_track_ships_entry` som **Hændelsestype**.
3. **Og hvis**: **Tilføj betingelse** → **Skabelon**, og skriv denne
   **Værdi-skabelon**: `{{ trigger.event.data.length_m | default(0) > 150 }}`
4. **Så gør**: **Tilføj handling**, søg efter din telefons
   notifikationshandling (den bærer din telefons navn), og skriv denne
   besked:

   ```text
   {{ trigger.event.data.name | default('Et skib') }}, {{ trigger.event.data.length_m }} m, {{ trigger.event.data.distance_km }} km væk
   ```

5. **Gem**.

**Andre idéer:** tænd et lys, når aftenfærgen når din havn i Norge; en besked,
når et familiemedlems båd, et fulgt skib, kommer hjem til Finland; en
notifikation, når det krydstogtskib, du skal møde, ankommer til Sydney
(Australien); antallet af skibe i din havn på et betjeningspanel, fra
`sensor.ships_in_range`.

**Områdets hændelser.** Hvert område udløser `live_track_ships_entry`, når et
skib kommer ind i dets cirkel, og `live_track_ships_exit`, når det forlader
den. Hvert skib meldes; din automatisering vælger dem, der betyder noget.
Felterne har samme navne og enheder som skibets attributter og udelader det,
kilden ikke sendte:

| Felt | Hvad det indeholder |
|---|---|
| `area_id`, `area` | områdets konfigurationspost-id og titel |
| `identity` | MMSI'en |
| `name`, `call_sign`, `imo` | når de sendes |
| `object_kind` | `vessel`, `net_buoy`, `aton`, `base_station`, `sar_aircraft` eller `distress_beacon` |
| `ship_type`, `ship_type_label`, `length_m`, `beam_m`, `draught_m`, `destination`, `nav_status` | kun skibe, når de sendes |
| `speed_kmh`, `course_deg`, `heading_deg` | når de sendes |
| `latitude`, `longitude`, `distance_km`, `bearing_from_centre_deg`, `last_seen` | hvor det blev hørt, set fra områdets midtpunkt |
| `entity_id` | kun ved indgang: `geo_location.vessel_<MMSI>`, når skibet er på kortet |
| `reason` | kun ved udgang: `left` (hørt uden for cirklen) eller `silent` (ikke hørt i et stykke tid, så det er måske der endnu) |

⚠ Fire ting, du skal vide:

* **En ankomst meldes kun, hvis skibet først blev hørt uden for cirklen.**
  Et skib, der først høres indenfor, har måske været der hele tiden: efter en
  genstart leverer kilderne i mange minutter skibe, der ikke har flyttet sig.
  Et skib, som modtagerne missede på vej ind, eller et, der tænder sin
  transponder indenfor, meldes altså ikke.
* **En afgang, der høres udenfor, meldes altid**, også for et skib, der var
  der, før Home Assistant startede. Et skib, der bliver tavst, meldes kun som
  afgået (`reason: silent`), hvis dets ankomst blev meldt.
* **En udgang venter 2 minutter.** Et skib, der kommer tilbage før, langs
  kanten af cirklen, meldes ikke som afgået og ankommet igen.
* **Oplysninger kan mangle ved ankomsten.** Navn, type og størrelse kommer i
  en langsommere besked end positionen. Et skib, der høres for første gang,
  kan ankomme med en position og intet andet.

To områder over det samme farvand udløser hver deres egne hændelser.
Grænserne for, hvor mange skibe der tegnes, får aldrig et skib til at komme
ind eller forlade området.

**De fulgte skibes hændelse.**
[Fulgte skibe](#fulgte-skibe-udvalgte-skibe-overalt) udløser én hændelse,
`live_track_ships_watched`, hvis `change` siger, hvad der skete:

| `change` | Hvornår |
|---|---|
| `arrived` | skibet melder sig fortøjet eller for anker, eller holder sig uden status under 3,7 km/t (2 knob) |
| `departed` | det sejler igen |
| `silent` | ikke hørt i 30 minutter (6 timer, hvis det er fortøjet eller for anker); det forlader kortet og er måske der endnu |
| `heard` | hørt igen efter `silent` |
| `destination` | besætningen har skiftet destination; `destination_previous` indeholder den gamle |

Dataene indeholder `watch_id`, `watch`, `identity`, dit `label` og de samme
skibsfelter som områdets hændelser, med afstand og pejling fra dit hjem.
Ankomst og afgang venter, til den nye tilstand har holdt i 5 minutter efter
skibets eget ur, så en båd, der driver langsomt, ikke skifter frem og tilbage.
Intet meldes ud fra et skibs første position efter en genstart: den sætter
udgangspunktet. Destinationer tastes af besætningen og er ofte forældede.

---

## Alt på kortet i detaljer

AIS (Automatic Identification System, automatisk identifikationssystem) er en
VHF-radioudsendelse, som skibe bruger til at meddele deres position, identitet
og rejse til hinanden og til land. Det er søfartens udgave af det, fly sender
som ADS-B. Erhvervsskibe skal have det om bord; mange lystbåde har det af egen
lyst, som regel som en svagere klasse B-enhed. AIS sendes åbent: alle med en
modtager kan høre det, og offentlige tjenester sender det videre. **Live Track
Ships viser alt, hvad kilden sender.** Intet filtreres fra, og der er ingen
indstilling, der skjuler en kategori for Home Assistant.

### Skibe

Hvert skib er en markør, hvis tilstand er afstanden til områdets midtpunkt, i
kilometer. De fleste skibe tegnes efter type: fragtskib, tankskib, færge,
slæbebåd og så videre. Nogle får deres eget billede: kongelige skibe og
statsskibe, og kendte både som en bys turbåde, vandtaxaer og brandbåde.
Kender du et skib, der fortjener ét, hvor som helst i verden?
[Foreslå det](#hjælp-den-med-at-vokse), med navn og MMSI- eller IMO-nummer,
og et foto eller et link, hvis du har et.

For at et skib forsvinder, så snart det sejler, bliver hver onlinekilde bedt
om en ring, der er lidt bredere end din cirkel (10 %, mindst 1 km), og din
egen modtager sender alt, hvad den hører. Kun skibe inden for din cirkel
beholdes: et skib, der høres udenfor, forlader kortet med det samme. Et skib,
der ikke høres igen, forsvinder efter en periode med stilhed. Et skib, der
holder op med at blive vist, er ikke nødvendigvis sejlet: ingen af kilderne
lover at levere hver besked.

⚠ **Skibstypen mangler ofte, især for små både.** Position og navn kommer med
næsten hver besked. Type og størrelse kommer i en separat, langsommere besked,
som mange klasse B-enheder sjældent sender. Regn med, at mange skibe,
heriblandt de fleste små både, ikke viser type eller størrelse, og at alle
skibe har få oplysninger i flere minutter efter en genstart af Home Assistant.
Det er dataene, ikke en fejl. Typer og størrelser, der er hørt én gang,
gemmes på tværs af genstarter.

Et skibs attributter omfatter navn, MMSI, kaldesignal, fart, kurs, retning,
længde, bredde, skibstype, destination, `object_kind`, `last_seen` og
`attribution`, hver kun når kilden har sendt den. Et skib, som to områder ser,
er én entitet.

### Private både og sejlbåde

En lystbåd, der sender AIS, vises på dit kort præcis som et fragtskib.
Afhængigt af, hvad båden sender, kan dens entitet indeholde:

* dens **navn**, som også er etiketten på kortet;
* dens **MMSI** og **radiokaldesignal**, begge permanente og offentligt
  søgbare;
* dens **position** med omkring en meters nøjagtighed, dens forrige position,
  og hvornår hver blev hørt;
* fart, kurs og retning, samt længde, bredde og type, når de sendes.

En båd, der lader sin transponder være tændt ved broen, bliver stående på
kortet ved sin bådplads, så længe den sender. Alle, der kan åbne dit kort, kan
også trykke **Track** på sådan en båd og se, hvor den har været de seneste
24 timer (eller så længe, som du indstiller), bådpladsen medregnet.

Der findes ingen frabedelsesliste for AIS, som der gør for fly, og denne
integration opfinder ikke én. Vil du have færre private både på dit kort, så
gør radius mindre.

### Det, der ikke er skibe

Hver entitet har `object_kind`: `vessel`, `net_buoy` (bøje på fiskeredskab),
`aton` (navigationshjælpemiddel: en bøje, en båke eller et fyr),
`base_station` (en AIS-station på land), `sar_aircraft` (et rednings- og
eftersøgningsfly) eller `distress_beacon`. De fleste kendes fra hinanden på
det identitetsformat, Den Internationale Telekommunikationsunion (ITU) giver
dem. Bøjer på fiskeredskaber gør ikke: de sender med identiteter som skibe, så
de genkendes på deres fabriksnavne (FISHING BOUY, NET MARK, BUOY) sammen med,
at de ikke sender nogen længde.

Alt, hvad der ikke er et skib, vises uden skibstype, størrelse eller
navigationsstatus. Bøjer på fiskeredskaber driver med deres liner, så de
beholder fart og kurs og tegnes som en fisk, der peger i den retning, de
driver.

Hvilke af dem der vises, afhænger af kilden. Målt en aften:

| Kilde | Bøjer på fiskeredskaber | Rednings- og eftersøgningsfly | Navigationshjælpemidler, basestationer |
|---|---|---|---|
| BarentsWatch | ja | ja | ingen set |
| Digitraffic | ingen set | ja | ingen set |
| aisstream.io | ingen set | ingen set | ingen set |
| Din egen modtager | hvad den hører | hvad den hører | hvad den hører |

aisstream.io leverede kun skibspositioner og skibsdata, både over de Store
Søer (Nordamerika) og over de samme norske og danske farvande, hvor
BarentsWatch viser bøjerne.

### Kystvagtens skibe i udlændingeopgaver

Et skib på den offentlige liste
[EnforcementVessels](https://github.com/StrausbergAutomationWorks/EnforcementVessels)
(skibe fra USA's kystvagt, der bruges i udlændingeopgaver) tegnes i
kystvagtens farver, med listens navn og myndighed, hvor end det høres.

### Fulgte skibe: udvalgte skibe overalt

Ud over områder kan du følge en liste af skibe, hvor de end er: et
familiemedlems båd, en færge, du tager, et krydstogtskib på vej hjem. Det
kræver en aisstream.io-nøgle, og der er én sådan liste pr. Home Assistant.

1. Åbn **Indstillinger → Enheder & tjenester**, vælg **Tilføj integration**,
   og søg efter **Live Track Ships**.
2. Vælg **Udvalgte skibe, hvor de end er**.
3. **API-nøgle**: nøglen fra et område, du allerede har sat op, er udfyldt.
4. **Skibe**: ét skib pr. linje, dets 9-cifrede MMSI og derefter, hvis du vil,
   et navn, du selv vælger:

   ```text
   244650000 Fars båd
   366999999 Færgen
   ```

5. Vælg **Indsend**.

Højst 100 skibe. aisstream.io følger højst 200 MMSI'er pr. nøgle, og
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
hvis det er installeret med samme nøgle, bruger en del af dem. En liste, der
ville gå over, afvises, når posten indlæses, med begrundelsen. For at ændre
listen åbner du **Konfigurér** på posten.

Et fulgt skib tegnes på kortet som alle andre, hvor end det høres, og dets
tilstand er afstanden til dit hjem. Et område, der allerede viser det,
beholder det: ét skib, én markør. Posten tilføjer `sensor.watched_vessels`:
hvor mange af skibene på listen der høres lige nu. Dens attribut `vessels`
nævner dem alle, med deres navn og seneste kendte tilstand. Dens hændelse er
beskrevet under [Brug den i automatiseringer](#brug-den-i-automatiseringer).

### Fotos og links

Når et skib sender et IMO-nummer, og Wikidata kender et foto af skibet på
Wikimedia Commons, har skibet `marker_photo`. Kortet viser fotoet, når du
peger på skibet, med fotograf og licens; et klik åbner det større, med links
til fotoets side og til dets licens. Hvert skib med IMO-nummer eller MMSI har
også `marker_links`, et link til skibet på VesselFinder. Knappen **Details** i
pop op-vinduet åbner skibets sædvanlige dialog.

Din Home Assistant spørger selv Wikidata og Commons, 20 IMO-numre ad gangen,
ti sekunder imellem, og gemmer hvert svar i 30 dage (14 dage, når der ikke er
noget foto) i `.storage/saw_vessel_photos.json`. Regn med fotos for omkring
hvert tiende skib: på vores testsystem havde 49 af 521 IMO-numre et.

⚠ Et foto kan vise skibet under et tidligere navn: IMO-nummeret hører til
skroget og følger det, når skibet skifter navn.

### Spor

Hvert skib har også `marker_track`. Klik på et skib, og tryk **Track** i dets
pop op-vindue: kortet tegner, hvor det har været, som én linje, der ender ved
skibet, og linjen vokser, mens du ser på. **Hide track** fjerner den. Intet
tegnes, før du beder om det, så en travl havn ikke forsvinder under linjer.

Sporet indeholder kun positioner, skibet meldte, mens det var på dit kort,
tyndet ud til én for hver 25 m (82 fod) eller 10 minutter, og aldrig to inden
for 30 sekunder. Din Home Assistant holder det i hukommelsen og gemmer det i
`.storage/saw_vessel_tracks.json`, så det overlever en genstart. Det dækker de
seneste 24 timer. For at gemme mere eller mindre:

1. Åbn **Indstillinger → Værktøjer → Handlinger**.
2. Vælg handlingen **Live Track Ships: Angiv sporets timer**.
3. Skriv **Timer**, fra 1 til 168 (en uge), og vælg **Udfør handling**.

Det gælder alle områder på én gang; en kortere indstilling sletter ældre
positioner med det samme.

⚠ Sporet starter tomt ved en første installation. Et skib, der forlod området
eller blev tavst, har et hul, tegnet som en lige linje mellem positionerne før
og efter.

### Skjul skibstyper

Hvert skib har `marker_group`, `marker_group_label` og `marker_group_order`:
en af tretten grupper (fragt; tank; passager og færge; fiskeri; lystbåde og
sejlads; slæbebåd, lods og havnetjeneste; myndigheder, redning og politi;
hurtigfærger og andet; type ikke sendt; bøjer på fiskeredskaber;
navigationshjælpemidler; basestationer; rednings- og eftersøgningsfly).
Kortkortets filterkort, `custom:live-track-map-filter-card`, viser grupperne
med hvor mange af hver, der er på kortet, og skjuler dem, du fjerner
fluebenet fra. Sæt det på en hvilken som helst visning af betjeningspanelet.
Dit valg gemmes kun i den browser.

Skjulningen sker kun på kortet: integrationen tæller stadig hvert skib og
udløser sine hændelser for hvert skib. Et nødradiofyr har ingen gruppe, så det
skjules aldrig.

---

## Alle entiteter, den opretter

| Entitet | Hvad den er |
|---|---|
| `geo_location.vessel_<MMSI>` | én markør for hvert skib eller andet AIS-objekt; tilstanden er afstanden til områdets midtpunkt (eller til dit hjem, for et fulgt skib), i kilometer. Den kommer og går og har intet unikt id |
| `sensor.ships_in_range` | én pr. område: hvor mange skibe det viser, og om en grænse har skåret listen ned |
| `sensor.ais_station` | kun din egen modtager: beskeder pr. minut. Dens attributter giver `vessels_heard` (de seneste 10 minutter), `farthest_km` og `farthest_mmsi` (fra områdets midtpunkt), `last_message`, `udp_port`, `listening`, og `port_error`, når porten ikke kan åbnes. Den opdateres hvert 30. sekund, så en modtager, der holder op med at sende, viser 0 |
| `sensor.watched_vessels` | kun fulgte skibe: hvor mange af dine skibe på listen der høres lige nu |

Attributter, der ændrer sig ved hver opdatering, holdes ude af Home
Assistants historik, så din database ikke vokser af dem: hvert skibs
`marker_photo`, `marker_links` og `marker_track`, og sensorernes hurtigt
skiftende attributter.

**Din database.** Home Assistants optager gemmer en ny række, hver gang en
entitet ændrer sig, og et sejlende skib ændrer sig med hver position, det
melder. På vores testsystem skrev ét område med 43 skibe 27.109 rækker på
omkring 30 timer, 8,8 % af hele databasen. Som standard gemmer optageren
10 dage og rydder op hver nat kl. 04:12 lokal tid, så væksten flader ud, men
ved en størrelse, du måske ikke ønsker.

Et skib beholder det samme entitets-id, `geo_location.vessel_<MMSI>`, hver
gang det dukker op, så ét mønster, `geo_location.vessel_*`, dækker alt, hvad
denne integration nogensinde har sat på kortet. For kun at beholde det seneste
døgn af det:

1. **Indstillinger → Automatiseringer & scener → Tilføj automatisering →
   Opret ny automatisering**.
2. Åbn menuen med tre prikker, vælg **Redigér i YAML**, erstat alt med dette,
   og vælg **Gem**:

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

Udelader du `keep_days` (standard 0), forsvinder alle deres rækker på én
gang. Vil du slet ikke optage noget af det, så sæt mønsteret under
`recorder:` → `exclude:` → `entity_globs:` i `configuration.yaml`; et
kortkort, der skal tegne historik (`history_start`), har så intet spor at
tegne. `sensor.ships_in_range` er et simpelt tal og billigt at beholde.

---

## Hvad den sender og henter

**Om din placering.** Hvert områdes midtpunkt er dit hjem, medmindre du
flytter det. Det sendes kun til den kilde, du har valgt til området: til
aisstream.io som et rektangel omkring en cirkel, der er lidt større end din
(10 %, mindst 1 km); til Digitraffic (Finland) som midtpunktet og den større
radius; til BarentsWatch (Norge) som den større cirkel. For fulgte skibe
sendes MMSI-numrene på din liste til aisstream.io. Din egen modtager sender
intet nogen steder hen: Home Assistant lytter kun. For fotos sendes
IMO-numrene på skibene på dit kort til Wikidata og Wikimedia Commons, uden
noget om dig. For at stoppe alt dette sletter du området eller posten med
fulgte skibe under **Indstillinger → Enheder & tjenester → Live Track Ships**.
Intet andet om dig sendes nogen steder hen.

**Hvor meget.**

* **aisstream.io**: én forbindelse til alle dine områder og én til dine fulgte
  skibe, begge holdt åbne; skibene kommer, efterhånden som de melder. Efter en
  fejl forbinder den igen efter en pause.
* **Digitraffic**: positioner hvert 60. sekund og skibsdata hvert
  15. minut, kun for din cirkel. Efter en fejl prøver den igen ved næste
  runde.
* **BarentsWatch**: én åben datastrøm pr. område. Kommer der intet i
  150 sekunder, forbinder den igen.
* **Fotos**: 20 IMO-numre ad gangen, 10 sekunder imellem, kun for skibe, der
  ikke er spurgt efter de seneste 30 dage (14, hvis der ikke var noget foto).
  En mislykket forespørgsel gentages senere.
* **Din egen modtager**: intet hentes.

---

## Hjælp den med at vokse

Live Track Ships vokser stadig. Vi tilføjer datakilder og lande, efterhånden
som vi finder dem, og vi vil gerne vide, hvad du kunne tænke dig næste gang.

### Foreslå noget

Mangler dit land eller din AIS-tjeneste? Er noget forkert eller svært at
forstå? Fortæl os det på den måde, der er nemmest for dig:

* [**Udfyld en kort formular**](https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues/new?template=da.yml)
  på dansk. Du skal have en gratis GitHub-konto.
* **Skriv en e-mail** til
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Ingen konto nødvendig.

Uanset hvad hjælper det, hvis du fortæller os:

* hvad du gerne vil se, og hvor i verden;
* et link til, hvor dataene offentliggøres, hvis du kender et (en side med
  åbne data, et offentligt feed, en tjenestes hjemmeside): ikke nødvendigt,
  men det hjælper;
* din Home Assistants sprog, hvis problemet er formuleringen eller en
  oversættelse.

Skriv på engelsk eller på dit eget sprog, hvad der er nemmest for dig.

### Tilføj det selv, med vores hjælp

Vil du selv tilføje noget, hjælper vi dig med det, fra det første spørgsmål
til den færdige udgivelse. Du behøver ikke være udvikler for at begynde:

* **En oversættelse.** Teksterne i opsætningsdialogen er en kort liste af
  sætninger i én tekstfil. Vi viser dig hvilken fil og hvilke linjer.
* **En ny datakilde.** Fortæl os, hvor dataene offentliggøres. Vi kan skrive
  koden sammen eller se din igennem.
* **Test, hvor du bor.** Installer den, se på din del af kortet, og fortæl os,
  hvad der er rigtigt, og hvad der ikke er.
* **En rettelse til denne README.** Hvis et trin ikke passede med det, du så,
  så fortæl os, hvad du så.

[**Fortæl os, hvad du har i tankerne**](https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues/new?template=da.yml)
eller skriv til
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
så svarer vi med de næste skridt.

---

## Sprog

Denne README: [English](README.md), [Deutsch](README.de.md),
[Français](README.fr.md), [Nederlands](README.nl.md),
[简体中文](README.zh-Hans.md), [Español](README.es.md),
[Italiano](README.it.md), **Dansk** og [Kalaallisut](README.kl.md) (en kort
kladde, sendt til gennemsyn hos Oqaasileriffik, Grønlands sprogsekretariat;
indtil da er denne danske side den pålidelige). Hver oversat README er
komplet.

Opsætningsdialogen og indstillingerne vises på din Home Assistants sprog, når
det er et af disse: English, Dansk, Deutsch, Español, Français, Gaeilge,
Íslenska, Italiano, Nederlands, Norsk Bokmål, Polski, Português, Português
(BR), Suomi, Svenska og 简体中文. Alle andre sprog viser engelsk. Kalaallisut er
endnu ikke et Home Assistant-sprog; vi har bedt Home Assistant om at tilføje
det. Kortkortets egne etiketter (**Track**, **Details**) er på engelsk på
alle sprog.

Fundet en fejl i en oversættelse, eller brug for et andet sprog? Fortæl os det
på <https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues>, eller
[oversæt det med vores hjælp](#tilføj-det-selv-med-vores-hjælp).

---

## Tak og licenser

* **aisstream.io**: ingen offentliggjorte vilkår. <https://aisstream.io>
* **Fintraffic Digitraffic** (Finland): data under CC BY 4.0.
  <https://www.digitraffic.fi/en/terms-of-service/>
* **BarentsWatch** (Norge): data under den norske licens for åbne offentlige
  data (NLOD).
  <https://www.barentswatch.no/en/articles/api-terms-and-conditions/>
* **Din egen modtager**: dine egne data.
* **Wikidata**: CC0. **Wikimedia Commons**: hvert foto under sin egen licens,
  vist med fotograf og licens.
* **VesselFinder**: kun linket; intet hentes derfra.
* **EnforcementVessels**: ODbL 1.0.
  <https://github.com/StrausbergAutomationWorks/EnforcementVessels>

Hvad denne integration ændrer: enheder omregnes, og kun skibe inden for din
cirkel beholdes. Hver skibsentitet og hvert områdes `sensor.ships_in_range`
har en `attribution`, der nævner kilden; Home Assistant viser den i
entitetens detaljer. Viser du disse data for andre, for eksempel på et
offentligt betjeningspanel, så behold kildeangivelsen og læs kildens egne
vilkår. De præcise kildeangivelser og angivelserne for skibsbillederne står i
[ATTRIBUTION.md](ATTRIBUTION.md).

Ingen af disse organisationer har lavet eller godkendt denne integration.

**Kode**: MIT, i [LICENSE](LICENSE).

**For udviklere:** AIS-sætninger fra din egen modtager afkodes af
[pyais](https://github.com/M0r13n/pyais) (MIT); Home Assistant installerer
selv `saw-livetrack` og `pyais`, første gang den indlæser integrationen.
Testene i `tests/` køres hver for sig med Python; nogle kræver en installeret
Home Assistant, og testene `*_live` kræver dine egne nøgler.

---

## Nøgleord

Home Assistant skibe · Home Assistant AIS · skibstrafik · skibe kort ·
skibssporing · bådsporing · søtrafik kort · AIS-kortkort · AIS-modtager ·
NMEA · AIS-catcher · aisstream.io · Digitraffic · BarentsWatch · ship
tracking · vessel tracker · Schiffsverfolgung · suivi des navires ·
scheepvaart volgen · seguimiento de barcos · tracciamento navi · 船舶追踪 ·
geo_location · kortkort · Lovelace · HACS · Marketplace · Live Track ·
LiveTrack · StrausbergAutomationWorks

---

**Anerkendelse.** StrausbergAutomationWorks anerkender de oprindelige folk i
alle de lande og farvande, dette kort dækker, over hele verden, og viser sin
respekt for deres ældste, fortidens og nutidens.
