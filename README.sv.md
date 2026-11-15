# Live Track Ships

[English](README.md) · [Suomi](README.fi.md) · **Svenska** · [Norsk](README.nb.md) · [Español](README.es.md) · [Nederlands](README.nl.md) · [Gaeilge](README.ga.md)

Fartyg, båtar och annan sjötrafik i realtid på Home Assistants karta. Live Track
Ships är en Home Assistant-integration (custom component, installeras från
Marketplace / HACS) som visar AIS-data för fartygen i det område du väljer:
var varje fartyg är, dess namn, fart, kurs, typ och storlek när fartyget
sänder dem. Varje fartyg är en `geo_location`-entitet som flyttar sig på
kartan när nya positioner kommer. Områdets mittpunkt kan ligga var som helst i
världen.

**Status: 0.1.0, första versionen.**

## Även fritidsbåtar visas

Integrationen visar allt källan skickar, och ingenting kan filtreras bort. En
fritidsbåt med AIS-sändare syns på kartan precis som ett lastfartyg: namn,
MMSI, anropssignal och position på ungefär en meter när. En båt som har
sändaren på vid bryggan står kvar på kartan vid bryggan. Det finns ingen
spärrlista för AIS. Vill du ha färre fritidsbåtar på kartan, minska radien.

## Källor

Du väljer en källa för varje område.

| Källa | Täckning | Behövs |
|---|---|---|
| aisstream.io | hela världen, där frivilliga har mottagare | en gratis API-nyckel |
| Fintraffic Digitraffic | finska vatten och Östersjön | ingenting |
| BarentsWatch AIS Live | norska vatten | gratis client ID och secret |

Varje fartygs attribut `attribution` anger dess källa. Alla
källhänvisningar: [ATTRIBUTION.md](ATTRIBUTION.md).

Täckningen är god där det finns mottagare, och ingen inställning skapar
täckning som inte finns. Syns inga fartyg i ditt område kan det bero på att
mottagare saknas, inte båtar.

## En del av Live Track

Live Track är en grupp Home Assistant-integrationer, en för varje slags sak som
rör sig, som alla ritar på samma karta
([LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
som installeras med integrationen). Släppta:
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft),
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
[Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail),
[Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail)
och Live Track Ships. Var och en fungerar ensam.

## Krav

- Home Assistant 2026.11 eller senare.
- aisstream.io: en gratis API-nyckel från
  [aisstream.io](https://aisstream.io/account). aisstream tillåter tre
  anslutningar per konto och per offentlig IP-adress.
- BarentsWatch: gratis client ID och secret. Skriv client ID exakt som det
  utfärdades.
- Digitraffic behöver varken nyckel eller konto.

## Installation

### Från Marketplace

Integrationen finns ännu inte i Marketplace-katalogen. Lägg till den via länk:

1. **Settings > Marketplace** och **Add from link**.
2. Skriv `StrausbergAutomationWorks/LiveTrackShips`. Om typen efterfrågas,
   välj **Integration**.
3. Installera **Live Track Ships**.
4. Starta om Home Assistant. Marketplace erbjuder omstarten som en reparation
   under **Settings > System > Repairs**.

### För hand

1. Ladda ner källkoden för den
   [senaste versionen](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest).
2. Kopiera dess mapp `custom_components/live_track_ships` till mappen
   `custom_components` i Home Assistants konfigurationskatalog.
3. Starta om Home Assistant.

## Inställning

**Settings > Devices & services > Add integration > Live Track Ships.** Välj
källa, ange nyckeln om den behövs, dra markören på kartan till vattnet du vill
följa och välj radie (1–500 km, standard 50). Varje område är en egen post.
Dialogen är på engelska; menynamnen ovan är det engelska gränssnittets.

Alla områden tillsammans visar högst 2 500 fartyg. Varje områdes inställningar
har ett reglage som bara kan sänka taket; använd det på långsammare hårdvara.

## Data och licens

Fartygen läses medan integrationen körs, direkt från den valda källan; detta
repository innehåller inga data från källorna. Kod: MIT.

Inte knuten till aisstream.io, Fintraffic, BarentsWatch eller någon
sjöfartsmyndighet. **Inte för navigering eller för att undvika kollisioner.**
Alla detaljer: [README på engelska](README.md).

## Nyckelord

Home Assistant AIS · fartyg på kartan · fartygsspårning · båtar på kartan ·
sjötrafik i realtid · Digitraffic · BarentsWatch · HACS-integration
