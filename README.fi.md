# Live Track Ships

[English](README.md) · **Suomi** · [Svenska](README.sv.md) · [Norsk](README.nb.md) · [Español](README.es.md) · [Nederlands](README.nl.md) · [Gaeilge](README.ga.md)

Laivat, veneet ja muut alukset reaaliajassa Home Assistantin kartalla. Live
Track Ships on Home Assistant -integraatio (custom component, asennetaan
Marketplacesta / HACS:sta), joka näyttää AIS-tiedot valitsemasi alueen
aluksista: missä kukin on, sen nimen, nopeuden, suunnan, tyypin ja koon, kun
alus lähettää ne. Jokainen alus on `geo_location`-entiteetti, joka liikkuu
kartalla uusien sijaintien mukaan. Alueen keskipiste voi olla missä tahansa
maailmassa.

**Tila: 0.1.0, ensimmäinen julkaisu.**

## Huviveneetkin näkyvät

Integraatio näyttää kaiken, mitä lähde lähettää, eikä mitään voi suodattaa
pois. AIS-lähetintä käyttävä huvivene näkyy kartalla kuin rahtilaiva: nimi,
MMSI, kutsutunnus ja sijainti noin metrin tarkkuudella. Laiturissa lähetintään
pitävä vene pysyy kartalla laiturissa. AIS:lle ei ole kieltäytymisluetteloa.
Jos haluat kartalle vähemmän huviveneitä, pienennä sädettä.

## Lähteet

Valitset yhden lähteen kullekin alueelle.

| Lähde | Kattavuus | Tarvitaan |
|---|---|---|
| aisstream.io | koko maailma, siellä missä vapaaehtoisilla on vastaanottimia | ilmainen API-avain |
| Fintraffic Digitraffic | Suomen ja Itämeren vedet | ei mitään |
| BarentsWatch AIS Live | Norjan vedet | ilmainen client ID ja secret |

Digitrafficin tiedot: Fintraffic / digitraffic.fi, lisenssi CC 4.0 BY,
muutettu (yksiköt muunnettu, vain ympyrän sisällä olevat alukset). Jokaisen
aluksen `attribution`-määrite kertoo sen lähteen. Kaikki lähdemerkinnät:
[ATTRIBUTION.md](ATTRIBUTION.md).

Kattavuus on hyvä siellä, missä on vastaanottimia, eikä mikään asetus luo
kattavuutta, jota ei ole. Jos alueellasi ei näy aluksia, syynä voi olla
vastaanottimien puute eikä veneiden.

## Osa Live Trackia

Live Track on joukko Home Assistant -integraatioita, yksi kullekin liikkuvalle
asialle, ja kaikki piirtävät samalle kartalle
([LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
joka asentuu integraation mukana). Julkaistu:
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft),
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
[Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail),
[Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail)
ja Live Track Ships. Jokainen toimii yksinäänkin.

## Vaatimukset

- Home Assistant 2026.11 tai uudempi.
- aisstream.io: ilmainen API-avain osoitteesta
  [aisstream.io](https://aisstream.io/account). aisstream sallii kolme yhteyttä
  tiliä ja julkista IP-osoitetta kohden.
- BarentsWatch: ilmainen client ID ja secret. Kirjoita client ID täsmälleen
  sellaisena kuin se annettiin.
- Digitraffic ei tarvitse avainta eikä tiliä.

## Asennus

### Marketplacesta

Integraatio ei ole vielä Marketplacen luettelossa. Lisää se linkillä:

1. **Settings > Marketplace** ja **Add from link**.
2. Kirjoita `StrausbergAutomationWorks/LiveTrackShips`. Jos tyyppiä kysytään,
   valitse **Integration**.
3. Asenna **Live Track Ships**.
4. Käynnistä Home Assistant uudelleen. Marketplace tarjoaa uudelleenkäynnistystä
   korjauksena kohdassa **Settings > System > Repairs**.

### Käsin

1. Lataa [uusimman julkaisun](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest)
   lähdekoodi.
2. Kopioi sen kansio `custom_components/live_track_ships` Home Assistantin
   asetushakemiston kansioon `custom_components`.
3. Käynnistä Home Assistant uudelleen.

## Käyttöönotto

**Settings > Devices & services > Add integration > Live Track Ships.** Valitse
lähde, anna avain tarvittaessa, vedä kartan merkki veden kohdalle ja valitse
säde (1–500 km, oletus 50). Kukin alue on oma merkintänsä. Asetusikkuna on
englanniksi; valikoiden nimet yllä ovat englanninkielisen käyttöliittymän
nimiä.

Kaikki alueet yhteensä näyttävät enintään 2 500 alusta. Alueen asetuksissa on
liukusäädin, jolla rajaa voi vain laskea; käytä sitä hitaammalla laitteistolla.

## Tiedot ja lisenssi

Alukset luetaan integraation ollessa käynnissä suoraan valitusta lähteestä;
tämä repositorio ei sisällä niiden tietoja. Koodi: MIT.

Ei sidoksissa aisstream.io:hon, Fintrafficiin, BarentsWatchiin eikä mihinkään
merenkulkuviranomaiseen. **Ei navigointiin eikä törmäysten välttämiseen.**
Kaikki yksityiskohdat: [englanninkielinen README](README.md).

## Hakusanat

Home Assistant AIS · laivat kartalla · alusten seuranta · veneet kartalla ·
meriliikenne reaaliajassa · Digitraffic meriliikenne · HACS-integraatio
