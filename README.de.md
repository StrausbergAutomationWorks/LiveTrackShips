# Live Track Ships

[English](README.md) · **Deutsch** · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md)

Schiffe, Boote und andere Wasserfahrzeuge live auf der Karte von Home
Assistant. Live Track Ships ist eine Home-Assistant-Integration (Custom
Component, Installation über den Marketplace / HACS), die die AIS-Daten der
Schiffe im gewählten Gebiet zeigt: wo jedes Schiff ist, Name, Geschwindigkeit,
Kurs, Typ und Größe, sofern das Schiff sie sendet. Jedes Schiff ist eine
`geo_location`-Entität, die sich mit neuen Positionen über die Karte bewegt.
Der Mittelpunkt des Gebiets kann überall auf der Welt liegen.

**Status: 0.1.0, die erste Veröffentlichung.**

## Auch Sportboote werden angezeigt

Die Integration zeigt alles, was die Quelle sendet; nichts lässt sich
herausfiltern. Ein Sportboot mit AIS-Transponder erscheint auf der Karte genau
wie ein Frachter: Name, MMSI, Rufzeichen und Position auf etwa einen Meter
genau. Ein Boot, das den Transponder am Liegeplatz eingeschaltet lässt, bleibt
dort auf der Karte. Für AIS gibt es keine Sperrliste. Wer weniger Sportboote
auf der Karte möchte, verkleinert den Radius.

## Quellen

Für jedes Gebiet wählen Sie eine Quelle.

| Quelle | Abdeckung | Benötigt |
|---|---|---|
| aisstream.io | weltweit, wo Freiwillige Empfänger betreiben | einen kostenlosen API-Schlüssel |
| Fintraffic Digitraffic | finnische und baltische Gewässer | nichts |
| BarentsWatch AIS Live | norwegische Gewässer | kostenlose Client-ID und Client-Secret |

Das Attribut `attribution` jedes Schiffs nennt seine Quelle. Alle
Quellenangaben: [ATTRIBUTION.md](ATTRIBUTION.md).

Die Abdeckung ist gut, wo Empfänger stehen, und keine Einstellung schafft
Abdeckung, wo keine ist. Zeigt Ihr Gebiet keine Schiffe, fehlen vielleicht
Empfänger, nicht Boote. Auf Nord- und Ostsee, dem Bodensee und den Flüssen
hängt aisstream.io von freiwilligen Empfängern ab.

## Voraussetzungen

- Home Assistant 2026.11 oder neuer.
- aisstream.io: ein kostenloser API-Schlüssel von
  [aisstream.io](https://aisstream.io/account). aisstream erlaubt drei
  Verbindungen pro Konto und pro öffentlicher IP-Adresse.
- BarentsWatch: kostenlose Client-ID und Client-Secret. Geben Sie die
  Client-ID genau so ein, wie sie ausgestellt wurde.
- Digitraffic braucht weder Schlüssel noch Konto.

## Installation

### Über den Marketplace

Die Integration ist noch nicht im Katalog des Marketplace. Fügen Sie sie per
Link hinzu:

1. **Einstellungen > Marketplace** und dann über einen Link hinzufügen.
2. `StrausbergAutomationWorks/LiveTrackShips` eingeben. Wird nach dem Typ
   gefragt, **Integration** wählen.
3. **Live Track Ships** installieren.
4. Home Assistant neu starten. Der Marketplace bietet den Neustart als
   Reparatur unter **Einstellungen > System > Reparaturen** an.

### Von Hand

1. Den Quellcode der
   [neuesten Version](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest)
   herunterladen.
2. Den Ordner `custom_components/live_track_ships` in den Ordner
   `custom_components` des Home-Assistant-Konfigurationsverzeichnisses kopieren.
3. Home Assistant neu starten.

## Einrichtung

**Einstellungen > Geräte & Dienste > Integration hinzufügen > Live Track
Ships.** Quelle wählen, bei Bedarf den Schlüssel eingeben, die Markierung auf
der Karte zum gewünschten Gewässer ziehen und den Radius wählen (1 bis 500 km,
Standard 50). Jedes Gebiet ist ein eigener Eintrag. Der Dialog erscheint auf
Deutsch, wenn Home Assistant auf Deutsch eingestellt ist.

In den Einstellungen eines Gebiets lässt sich der Mittelpunkt mit derselben
Markierung verschieben; das Gebiet erhält dann einen neuen Namen und wird neu
geladen. Alle Gebiete zusammen zeigen höchstens 2.500 Schiffe; ein Schieberegler
in den Einstellungen kann diese Grenze nur senken. Auf langsamer Hardware
verwenden.

## Schiffe, die ein eigenes Bild verdienen

Die meisten Schiffe werden nach ihrem Typ gezeichnet. Manche haben ein eigenes
Bild: königliche und staatliche Jachten sowie bekannte Boote wie die
Ausflugsschiffe, Wassertaxis und Feuerlöschboote von Chicago. Sie kennen ein
Schiff, das eines verdient, irgendwo auf der Welt? Eröffnen Sie ein Issue unter
<https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues> mit Name
und MMSI- oder IMO-Nummer, gern mit Foto oder Link.

Einen wesentlichen Fehler in dieser Übersetzung oder im deutschen Dialog
gefunden? Bitte unter derselben Adresse melden.

## Teil von Live Track

Live Track ist eine Reihe von Home-Assistant-Integrationen, eine für jede Art
von Dingen, die sich bewegen, und alle zeichnen auf dieselbe Karte
([LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
die mit der Integration installiert wird). Veröffentlicht:
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft),
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
[Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail),
[Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail)
und Live Track Ships. Jede funktioniert auch allein.

## Daten und Lizenz

Die Schiffe werden während des Betriebs direkt von der gewählten Quelle
gelesen; dieses Repository enthält keine Daten dieser Quellen. Code: MIT.

Nicht verbunden mit aisstream.io, Fintraffic, BarentsWatch oder einer
Schifffahrtsbehörde. **Nicht zur Navigation oder Kollisionsvermeidung.** Alle
Einzelheiten und Sprachen: [README auf Englisch](README.md#languages).

## Stichwörter

Home Assistant AIS · Schiffe auf der Karte · Schiffsverfolgung · Boote
verfolgen · Schiffsverkehr live · AIS-Karte · HACS-Integration
