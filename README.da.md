# Live Track Ships

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · **Dansk** · [Kalaallisut](README.kl.md)

Skibe, både og andre fartøjer i realtid på Home Assistants kort. Live Track
Ships er en Home Assistant-integration (custom component, installeres fra
Marketplace / HACS), der viser AIS-data for skibene i det område, du vælger:
hvor hvert skib er, dets navn, fart, kurs, type og størrelse, når skibet
sender dem. Hvert skib er en `geo_location`-entitet, der flytter sig på
kortet, når nye positioner kommer. Områdets midtpunkt kan ligge hvor som helst
i verden.

**Status: 0.1.0, første udgivelse.**

## Også lystbåde vises

Integrationen viser alt, hvad kilden sender, og intet kan filtreres fra. En
lystbåd med AIS-transponder vises på kortet præcis som et fragtskib: navn,
MMSI, kaldesignal og position med omkring en meters nøjagtighed. En båd, der
har transponderen tændt i havnen, bliver stående på kortet i havnen. AIS har
ingen frabedelsesliste. Vil du have færre lystbåde på kortet, så gør radius
mindre.

## Kilder

Du vælger én kilde for hvert område.

| Kilde | Dækning | Kræver |
|---|---|---|
| aisstream.io | hele verden, hvor frivillige har modtagere | en gratis API-nøgle |
| Fintraffic Digitraffic | finske farvande og Østersøen | intet |
| BarentsWatch AIS Live | norske farvande | gratis klient-id og klienthemmelighed |

Hvert skibs attribut `attribution` angiver dets kilde. Alle kildeangivelser:
[ATTRIBUTION.md](ATTRIBUTION.md).

Dækningen er god, hvor der står modtagere, og ingen indstilling skaber dækning,
der ikke findes. Viser dit område ingen skibe, mangler der måske modtagere,
ikke både. I danske farvande og omkring Grønland og Færøerne afhænger
aisstream.io af frivillige modtagere.

## Krav

- Home Assistant 2026.11 eller nyere.
- aisstream.io: en gratis API-nøgle fra
  [aisstream.io](https://aisstream.io/account). aisstream tillader tre
  forbindelser pr. konto og pr. offentlig IP-adresse.
- BarentsWatch: gratis klient-id og klienthemmelighed. Skriv klient-id'et
  præcis, som det blev udstedt.
- Digitraffic kræver hverken nøgle eller konto.

## Installation

### Fra Marketplace

Integrationen er endnu ikke i Marketplace-kataloget. Tilføj den via link:

1. **Indstillinger > Marketplace**, og tilføj derefter fra et link.
2. Skriv `StrausbergAutomationWorks/LiveTrackShips`. Bliver du spurgt om
   typen, så vælg **Integration**.
3. Installér **Live Track Ships**.
4. Genstart Home Assistant. Marketplace tilbyder genstarten som en reparation
   under **Indstillinger > System > Reparationer**.

### Manuelt

1. Hent kildekoden til den
   [nyeste udgivelse](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest).
2. Kopiér mappen `custom_components/live_track_ships` til mappen
   `custom_components` i Home Assistants konfigurationsmappe.
3. Genstart Home Assistant.

## Opsætning

**Indstillinger > Enheder og tjenester > Tilføj integration > Live Track
Ships.** Vælg kilde, angiv nøglen hvis den kræves, træk markøren på kortet hen
til det farvand, du vil følge, og vælg radius (1 til 500 km, standard 50).
Hvert område er en selvstændig post. Dialogen vises på dansk, når Home
Assistant er sat til dansk.

I et områdes indstillinger kan du flytte midtpunktet med den samme markør;
området får så nyt navn og genindlæses. Alle områder tilsammen viser højst
2.500 skibe; en skyder i indstillingerne kan kun sænke den grænse. Brug den på
en langsom maskine.

## Hændelser: et skib kommer ind i dit område eller forlader det

Hvert område sender to hændelser i Home Assistant: `live_track_ships_entry`, når et skib kommer ind
i cirklen, og `live_track_ships_exit`, når det forlader den. Integrationen melder alle skibe; din
automatisering vælger dem, der betyder noget for dig, for eksempel efter navn,
type, længde eller fart. Felterne har samme navne og enheder som skibets
attributter; listen og et eksempel står i den [engelske README](README.md#events-a-ship-comes-into-your-area-or-leaves-it).

- En ankomst meldes kun, hvis skibet først er hørt uden for cirklen, i ringen
  omkring den. Et skib, der først høres inde i cirklen, kan have ligget der
  hele tiden; et skib, som modtagerne ikke hørte på vej ind, meldes derfor
  ikke.
- En afgang, der høres uden for cirklen, meldes altid. Et skib, der tier,
  meldes kun ude, hvis dets ankomst blev meldt.
- Et skib meldes først ude efter 2 minutter; vender det tilbage inden da,
  meldes det ikke ud og ind igen.
- Ved ankomsten kan navn, type og størrelse mangle, fordi de sendes sjældnere
  end positionen.

## Skibe, der fortjener deres eget billede

De fleste skibe tegnes efter deres type. Nogle har deres eget billede:
kongelige og statslige skibe som Kongeskibet Dannebrog, og kendte både som
Chicagos udflugtsbåde, vandtaxaer og brandbåde. Kender du et skib, der
fortjener ét, hvor som helst i verden? Opret en issue på
<https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues> med navn
og MMSI- eller IMO-nummer, gerne med et foto eller et link.

Har du fundet en væsentlig fejl i denne oversættelse eller i den danske
dialog? Skriv til os på samme adresse.

## En del af Live Track

Live Track er en række Home Assistant-integrationer, én for hver slags ting,
der bevæger sig, og alle tegner på samme kort
([LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
som installeres sammen med integrationen). Udgivet:
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft),
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
[Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail),
[Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail)
og Live Track Ships. Hver af dem fungerer også alene.

## Data og licens

Skibene læses, mens integrationen kører, direkte fra den valgte kilde; dette
repository indeholder ingen data fra kilderne. Kode: MIT.

Ikke tilknyttet aisstream.io, Fintraffic, BarentsWatch eller nogen
søfartsmyndighed. **Ikke til navigation eller til at undgå kollisioner.** Alle
detaljer og sprog: [README på engelsk](README.md#languages).

## Nøgleord

Home Assistant AIS · skibe på kortet · skibssporing · både på kortet ·
skibstrafik i realtid · AIS-kort · HACS-integration
