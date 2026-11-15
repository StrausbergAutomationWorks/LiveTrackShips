# Live Track Ships

[English](README.md) · [Suomi](README.fi.md) · [Svenska](README.sv.md) · **Norsk** · [Español](README.es.md) · [Nederlands](README.nl.md) · [Gaeilge](README.ga.md)

Skip, båter og andre fartøy i sanntid på Home Assistant-kartet. Live Track
Ships er en Home Assistant-integrasjon (custom component, installeres fra
Marketplace / HACS) som viser AIS-data for fartøyene i området du velger: hvor
hvert fartøy er, navn, fart, kurs, type og størrelse når fartøyet sender dem.
Hvert fartøy er en `geo_location`-entitet som flytter seg på kartet når nye
posisjoner kommer. Midtpunktet for området kan ligge hvor som helst i verden.

**Status: 0.1.0, første utgivelse.**

## Fritidsbåter vises også

Integrasjonen viser alt kilden sender, og ingenting kan filtreres bort. En
fritidsbåt med AIS-sender vises på kartet akkurat som et lasteskip: navn, MMSI,
kallesignal og posisjon på omtrent en meter nær. En båt som har senderen på
ved kaia, blir stående på kartet ved kaia. Det finnes ingen reservasjonsliste
for AIS. Vil du ha færre fritidsbåter på kartet, gjør radien mindre.

## Kilder

Du velger én kilde for hvert område.

| Kilde | Dekning | Trenger |
|---|---|---|
| aisstream.io | hele verden, der frivillige har mottakere | en gratis API-nøkkel |
| Fintraffic Digitraffic | finske farvann og Østersjøen | ingenting |
| BarentsWatch AIS Live | norske farvann | gratis client ID og secret |

BarentsWatch-data: inneholder data under Norsk lisens for offentlige data
(NLOD), distribuert av BarentsWatch, endret (enheter konvertert, bare fartøy
innenfor sirkelen). Hvert fartøys attributt `attribution` oppgir kilden. Alle
kildehenvisninger: [ATTRIBUTION.md](ATTRIBUTION.md).

BarentsWatch viser bare norske farvann. Ligger minst 5 % av en
BarentsWatch-sirkel utenfor, sier dialogen fra før området opprettes.

## En del av Live Track

Live Track er en gruppe Home Assistant-integrasjoner, én for hver slags ting
som beveger seg, som alle tegner på samme kart
([LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
som installeres med integrasjonen). Utgitt:
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft),
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
[Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail),
[Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail)
og Live Track Ships. Hver av dem fungerer alene.

## Krav

- Home Assistant 2026.11 eller nyere.
- aisstream.io: en gratis API-nøkkel fra
  [aisstream.io](https://aisstream.io/account). aisstream tillater tre
  tilkoblinger per konto og per offentlig IP-adresse.
- BarentsWatch: gratis client ID og secret, registrert selv hos BarentsWatch.
  Skriv client ID nøyaktig slik den ble utstedt.
- Digitraffic trenger verken nøkkel eller konto.

## Installasjon

### Fra Marketplace

Integrasjonen er ennå ikke i Marketplace-katalogen. Legg den til med lenke:

1. **Settings > Marketplace** og **Add from link**.
2. Skriv `StrausbergAutomationWorks/LiveTrackShips`. Spør den etter type,
   velg **Integration**.
3. Installer **Live Track Ships**.
4. Start Home Assistant på nytt. Marketplace tilbyr omstarten som en
   reparasjon under **Settings > System > Repairs**.

### For hånd

1. Last ned kildekoden til den
   [nyeste utgivelsen](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest).
2. Kopier mappen `custom_components/live_track_ships` til mappen
   `custom_components` i konfigurasjonskatalogen til Home Assistant.
3. Start Home Assistant på nytt.

## Oppsett

**Settings > Devices & services > Add integration > Live Track Ships.** Velg
kilde, oppgi nøkkelen om den trengs, dra markøren på kartet til vannet du vil
følge, og velg radius (1–500 km, standard 50). Hvert område er en egen
oppføring. Dialogen er på engelsk; menynavnene over er fra det engelske
grensesnittet.

Alle områdene til sammen viser høyst 2 500 fartøy. Innstillingene for hvert
område har en glidebryter som bare kan senke taket; bruk den på tregere
maskinvare.

## Data og lisens

Fartøyene leses mens integrasjonen kjører, direkte fra den valgte kilden; dette
repositoriet inneholder ingen data fra kildene. Kode: MIT.

Ikke tilknyttet aisstream.io, Fintraffic, BarentsWatch eller noen
sjøfartsmyndighet. **Ikke for navigasjon eller for å unngå kollisjoner.** Alle
detaljer: [README på engelsk](README.md).

## Nøkkelord

Home Assistant AIS · skip på kartet · skipssporing · båter på kartet ·
skipstrafikk i sanntid · BarentsWatch AIS · HACS-integrasjon
