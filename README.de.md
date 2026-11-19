# Live Track Ships

[English](README.md) · **Deutsch** · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Kalaallisut](README.kl.md) · [Alle Sprachen](#sprachen)

**Schiffe und Boote für Home Assistant, auf einer Karte.** Live Track Ships
bringt Schiffe, Boote und alles andere, was AIS sendet (das Funksignal, mit dem
Schiffe sagen, wo sie sind), auf Ihre Home-Assistant-Karte, in Ihrer Nähe oder
irgendwo auf der Welt, wo Sie wollen. Es folgt außerdem ausgewählten Schiffen,
wohin sie auch fahren, und meldet Ihren Automationen, wenn ein Schiff in Ihr
Gebiet kommt oder es verlässt.

> **Live Track Ships ist ein Modul von Live Track**, einer Familie von
> Home-Assistant-Integrationen, die alles, was sich bewegt, und das Wetter,
> durch das es sich bewegt, auf einer gemeinsamen Karte zeigen: Flugzeuge,
> Schiffe, Züge und Wetter. Installieren Sie es allein oder neben den anderen
> Modulen ([Liste unten](#teil-von-live-track-die-anderen-module)).

> **Es wächst, und Ideen sind willkommen.** Live Track Ships deckt heute die
> ganze Welt ab, wo Freiwillige Empfänger betreiben, Finnland und Norwegen
> ausführlicher, und Ihren eigenen Empfänger. Wir fügen weitere Datenquellen
> und Länder hinzu. Fehlt Ihres? [Schlagen Sie es vor](#helfen-sie-mit-es-zu-erweitern),
> oder fügen Sie es selbst hinzu: Wir helfen Ihnen dabei.

**Status: 0.1.0, die erste Veröffentlichung.** Per Link zum Marketplace
hinzufügbar ([siehe unten](#installation-schritt-für-schritt)); im Katalog des
Marketplace ist es noch nicht.

Eigenes Werk von StrausbergAutomationWorks. Nicht verbunden mit oder
unterstützt von aisstream.io, Fintraffic (Finnland), BarentsWatch (Norwegen),
Wikidata, Wikimedia Commons, VesselFinder, MarineTraffic, einem
Schiffsbetreiber oder einer Seefahrtsbehörde.

> ⚠ **Kein Sicherheitssystem.** Es zeigt öffentliche Daten, oft Sekunden alt,
> manchmal Minuten, und nur das, was Empfänger zufällig hören. Es ist nicht
> für die Navigation, die Kollisionsvermeidung oder einen anderen
> betrieblichen Zweck gedacht. Auf dem Wasser nutzen Sie Ihr eigenes AIS,
> Radar, Seekarten und UKW-Funk.

---

## Inhalt

1. [Alles, was es kann](#alles-was-es-kann)
2. [Wo es funktioniert](#wo-es-funktioniert)
3. [Teil von Live Track: die anderen Module](#teil-von-live-track-die-anderen-module)
4. [Bevor Sie beginnen](#bevor-sie-beginnen)
5. [Installation, Schritt für Schritt](#installation-schritt-für-schritt)
6. [Einrichtung, Schritt für Schritt](#einrichtung-schritt-für-schritt)
7. [Kostenlose Schlüssel, die mehr freischalten, Schritt für Schritt](#kostenlose-schlüssel-die-mehr-freischalten-schritt-für-schritt)
8. [Die Karte auf ein Dashboard bringen](#die-karte-auf-ein-dashboard-bringen)
9. [In Automationen verwenden](#in-automationen-verwenden)
10. [Alles auf der Karte im Detail](#alles-auf-der-karte-im-detail)
11. [Alle Entitäten, die es anlegt](#alle-entitäten-die-es-anlegt)
12. [Was es sendet und herunterlädt](#was-es-sendet-und-herunterlädt)
13. [Helfen Sie mit, es zu erweitern](#helfen-sie-mit-es-zu-erweitern)
14. [Sprachen](#sprachen)
15. [Danksagungen und Lizenzen](#danksagungen-und-lizenzen)
16. [Stichwörter](#stichwörter)

---

## Alles, was es kann

### Auf der Karte, ohne etwas einzurichten

Sie legen ein **Gebiet** an: einen Mittelpunkt und einen Radius auf der Karte,
und eine Datenquelle. Alles unten erscheint dann in diesem Gebiet. Fintraffic
Digitraffic (Finnland) und Ihr eigener Empfänger brauchen keinen Schlüssel;
aisstream.io und BarentsWatch (Norwegen) brauchen einen kostenlosen
([siehe unten](#mit-ihrem-eigenen-kostenlosen-schlüssel-oder-konto)).

| Was | Wo | Woher |
|---|---|---|
| **Schiffe**: Frachter, Tanker, Fähren, Schlepper, Fischerboote, Sportboote und Segelboote, jedes mit eigenem Bild, nach seinem Kurs gedreht | in jedem Gebiet | die Quelle, die Sie wählen |
| **Was keine Schiffe sind**: Fanggerätbojen, Navigationshilfen, AIS-Basisstationen, Such- und Rettungsflugzeuge und Notfunkbaken | in jedem Gebiet, wenn die Quelle sie sendet | die Quelle, die Sie wählen |
| **Fotos und Links**: ein Foto des Schiffs, wenn eines bekannt ist, und ein Link zum Schiff bei VesselFinder | jedes Schiff mit IMO-Nummer oder MMSI | Wikidata und Wikimedia Commons |
| **Spuren**: wo ein Schiff in den letzten 24 Stunden war, gezeichnet, wenn Sie danach fragen | jedes Schiff | von Ihrem eigenen Home Assistant gespeichert |
| **Küstenwachschiffe im Einwanderungseinsatz**, in den Farben der Küstenwache gezeichnet | wo immer sie gehört werden | die öffentliche Liste EnforcementVessels |
| **Ankünfte und Abfahrten**: ein Ereignis für Ihre Automationen, wenn ein Schiff in ein Gebiet kommt oder es verlässt | in jedem Gebiet | von Ihrem eigenen Home Assistant ermittelt |

### Mit Ihrem eigenen kostenlosen Schlüssel oder Konto

| Kostenloser Schlüssel oder Konto | Was er hinzufügt |
|---|---|
| **aisstream.io**-Schlüssel | Schiffe überall auf der Welt, wo Freiwillige Empfänger betreiben; und **beobachtete Schiffe**: ausgewählte Schiffe, verfolgt, wo immer sie sind, mit einem Ereignis, wenn eines ankommt, abfährt, verstummt oder sein Ziel ändert |
| **BarentsWatch**-Konto (Norwegen) | Schiffe in norwegischen Gewässern, Svalbard eingeschlossen, mit Namen und Schiffstyp bei jeder Position |

Jeder ist in wenigen Minuten erhältlich: [Schritt für Schritt unten](#kostenlose-schlüssel-die-mehr-freischalten-schritt-für-schritt).

---

## Wo es funktioniert

| Region | Was Sie bekommen | Woher | Braucht |
|---|---|---|---|
| **Die ganze Welt** | Schiffe, wo Freiwillige Empfänger betreiben: gut an belebten Küsten und Häfen, dünn oder gar nicht anderswo | aisstream.io | einen kostenlosen Schlüssel |
| **Europa**: Finnland und die Ostsee | Schiffe in finnischen und baltischen Gewässern, jede Minute neue Positionen | Fintraffic Digitraffic (Finnland) | nichts |
| **Europa**: Norwegen | Schiffe in norwegischen Gewässern, Svalbard eingeschlossen, mit Namen und Typ bei jeder Position | BarentsWatch (Norwegen) | ein kostenloses Konto |
| **Ihr eigener Empfänger**: überall | alles, was Ihre Antenne hört, ohne Internet | Ihr eigener AIS-Empfänger | einen Empfänger, der NMEA über UDP sendet |

Sie wählen für jedes Gebiet eine Quelle. Welche Arten von Dingen erscheinen,
wie frisch die Positionen sind und wie vollständig die Schiffsdaten sind,
hängt alles von dieser Quelle ab.

⚠ **Die Abdeckung ist gut, wo Empfänger stehen, und fehlt, wo keine sind.**
Keine Einstellung kann Abdeckung schaffen, die es nicht gibt. Gemessen am
2026-09-02 mit aisstream.io rund um Chicago (USA): 100 Schiffe in 120 Sekunden
auf den Großen Seen, aber null Schiffe in einer Stunde auf den Kanälen südlich
der Stadt, wo durchaus Schubverbände fahren: Kommerzielle Dienste sehen sie per
Satellit, und das bieten kostenlose Quellen nicht. **Keine Schiffe in Ihrem
Gebiet kann heißen: keine Empfänger, nicht keine Boote.** Prüfen Sie, ob Ihre
Quelle Ihr Gewässer abdeckt, bevor Sie annehmen, dass etwas kaputt ist.

⚠ **Ihr eigener Empfänger:**

* Ein Gebiet lauscht auf einem Port. Zwei Empfänger brauchen zwei Ports.
* Alles, was der Empfänger innerhalb Ihres Kreises hört, wird gezeigt,
  Navigationshilfen und Basisstationen eingeschlossen. Sein Stationssensor
  zählt auch, was er außerhalb des Kreises hört.
* Ein Satz trägt kein Datum, also ist die Zeit einer Position die Zeit, zu der
  Home Assistant sie empfangen hat.
* Die Drehrate wird für diese Quelle nicht gezeigt.
* Bisher ist das mit aufgezeichneten, über UDP gesendeten Sätzen getestet,
  nicht mit einem Empfänger. Wenn Sie es mit Ihrem versuchen,
  [sagen Sie uns, wie es lief](#helfen-sie-mit-es-zu-erweitern).

Nicht auf der Liste? [Sagen Sie es uns](#helfen-sie-mit-es-zu-erweitern). Wo
jemand die Daten offen veröffentlicht, prüfen wir, ob wir sie hinzufügen.

---

## Teil von Live Track: die anderen Module

Live Track ist eine Reihe von Home-Assistant-Integrationen, eine für jede Art
von beweglichem Ding, alle auf derselben Kartenkarte gezeichnet. Jede
funktioniert allein; zusammen ergeben sie ein lebendiges Bild. Sie teilen sich
die Kartenkarte und eine Python-Bibliothek
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
sodass eine weitere installierte Integration keine zusätzlichen Anfragen an
eine Quelle stellt, die eine andere bereits liest.

| Modul | Was es auf die Karte bringt | Status |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | Flugzeuge über Ihnen per ADS-B, mit Routen und Typsymbolen | veröffentlicht |
| **Live Track Ships** | Schiffe und Boote per AIS, in Ihrer Nähe oder irgendwo (dieses Modul) | veröffentlicht |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | Nahverkehrszüge in Nordamerika, Europa und Australien | veröffentlicht |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | Intercity- und Fernzüge in Nordamerika, Europa und Australien | veröffentlicht |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | Flugzeuge und Schiffe der Einwanderungs- und Bundespolizeibehörden, aus öffentlichen Listen | veröffentlicht |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | Wetter, Stürme und Naturgefahren | veröffentlicht |
| Live Track Stations | Abfahrtstafeln und „Zeit zu gehen“-Hinweise für jeden Bahnhof | geplant |
| Live Track Satellites | Satelliten, die über Sie hinwegziehen | geplant |
| Live Track Freight Trains | Güter- und Arbeitszüge, wo Bahnen sie veröffentlichen | geplant |
| Live Track Transit | Stadtbusse, Straßenbahnen, Fähren und U-Bahnen | geplant |
| Live Track Intercity Buses | Fernbusse und Regionalbusse | geplant |
| Live Track Commuter Buses | Pendlerbusse | geplant |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | die gemeinsame Kartenkarte, auf der jedes Modul zeichnet | veröffentlicht, mit jedem Modul installiert |

Alles ist kostenlos und quelloffen. Nichts wird für Sponsoren zurückgehalten.

---

## Bevor Sie beginnen

* **Home Assistant** 2026.11 oder neuer.
* **Der Marketplace** (HACS) in Ihrem Home Assistant, um es bequem zu
  installieren und zu aktualisieren. Ohne ihn können Sie die Dateien von Hand
  kopieren.
* **Internetzugang** für Home Assistant, für die Online-Quellen und die
  Fotos. Ihr eigener Empfänger funktioniert ohne.
* **Eine Datenquelle.** Digitraffic (Finnland) und Ihr eigener Empfänger
  brauchen kein Konto. aisstream.io und BarentsWatch (Norwegen) brauchen einen
  kostenlosen Schlüssel
  ([Schritt für Schritt](#kostenlose-schlüssel-die-mehr-freischalten-schritt-für-schritt)).
* **Optional: Ihr eigener AIS-Empfänger.** Der Empfänger, oder das Programm,
  das ihn dekodiert, sendet NMEA-Sätze (`!AIVDM`) über UDP an die Adresse Ihres
  Home Assistant, im selben Netzwerk. In AIS-catcher ist das
  `-u <address> <port>`; in rtl-ais `-h <address> -P <port>`; OpenCPN und
  Signal K richten es als UDP-Ausgangsverbindung ein. Ein Empfänger, der per
  USB angeschlossen wird, etwa ein dAISy, braucht eines dieser Programme, um
  seine Sätze weiterzugeben.
* **Optional: auto-entities** aus dem Marketplace, um die Markierungen auf die
  Karte zu bringen (siehe
  [Die Karte auf ein Dashboard bringen](#die-karte-auf-ein-dashboard-bringen)).
* Nichts zu bezahlen. Für Digitraffic und Ihren eigenen Empfänger ist kein
  Konto nötig; die kostenlosen Schlüssel braucht es nur für aisstream.io und
  BarentsWatch.

---

## Installation, Schritt für Schritt

### Über den Marketplace (empfohlen)

Live Track Ships ist noch nicht im Katalog des Marketplace. Fügen Sie es per
Link hinzu:

1. Öffnen Sie in Home Assistant **Einstellungen → Marketplace** (HACS).
2. Wählen Sie **Per Link hinzufügen** (oder das Dreipunktmenü →
   **Benutzerdefinierte Repositories**).
3. Geben Sie `StrausbergAutomationWorks/LiveTrackShips` ein. Wenn nach dem Typ
   gefragt wird, wählen Sie **Integration**.
4. Suchen Sie **Live Track Ships** in der Liste und wählen Sie
   **Herunterladen** oder **Installieren**.
5. **Starten Sie Home Assistant neu**: **Einstellungen → System → Reparaturen**
   bietet den Neustart an, oder nutzen Sie **Einstellungen → System → Neu
   starten**.

### Von Hand

1. Laden Sie den Quellcode der
   [neuesten Veröffentlichung](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest)
   herunter.
2. Kopieren Sie dessen Ordner `custom_components/live_track_ships` in den
   Ordner `custom_components` Ihres Home-Assistant-Konfigurationsordners
   (legen Sie `custom_components` an, falls es ihn nicht gibt).
3. Starten Sie Home Assistant neu.

---

## Einrichtung, Schritt für Schritt

1. Öffnen Sie **Einstellungen → Geräte & Dienste**.
2. Wählen Sie **Integration hinzufügen** (unten rechts) und suchen Sie nach
   **Live Track Ships**.
3. Wählen Sie **Alle Schiffe in einem Gebiet**. (Die andere Wahl,
   **Ausgewählte Schiffe, wo immer sie sind**, folgt einer Liste von Schiffen
   überall: siehe
   [Beobachtete Schiffe](#beobachtete-schiffe-ausgewählte-schiffe-überall).)
4. **Datenquelle**: Wählen Sie eine. Im Zweifel: in Finnland Fintraffic
   Digitraffic, das keinen Schlüssel braucht; in Norwegen BarentsWatch;
   überall sonst aisstream.io.
5. **API-Schlüssel** (aisstream.io), oder **Client-ID** und **Client-Secret**
   (BarentsWatch): Fügen Sie sie ein
   ([so bekommen Sie sie](#kostenlose-schlüssel-die-mehr-freischalten-schritt-für-schritt)).
   Ein Gebiet, das Sie schon eingerichtet haben, füllt sie für Sie aus.
6. **UDP-Port (eigener Empfänger)**: nur für Ihren eigenen Empfänger. Geben
   Sie den Port ein, an den er sendet, von 1024 bis 65535. Lassen Sie 10110,
   wenn Sie ihn nicht geändert haben.
7. **Mittelpunkt**: Ziehen Sie die Markierung in die Mitte des Gewässers, das
   Sie beobachten wollen. Sie beginnt bei Ihrem Zuhause.
8. **Radius (km)**: von 1 bis 500 km (0,6 bis 310 Meilen). Im Zweifel lassen
   Sie 50 km (31 Meilen).
9. **Höchstzahl verfolgter Schiffe**: Lassen Sie 1.000, außer Ihr Rechner ist
   klein.
10. Wählen Sie **OK**.

Das ist alles. Schiffe erscheinen innerhalb von ein, zwei Minuten, so wie die
Quelle sie sendet. Schiffstypen und Größen kommen in den nächsten Minuten
hinzu. Jedes Gebiet ist ein Eintrag mit dem Titel *Ships near <latitude>,
<longitude>*. Weitere Gebiete legen Sie genauso an.

* Dieselbe Quelle kann denselben Mittelpunkt nicht zweimal beobachten.
* Liegen mindestens 5 % eines BarentsWatch-Kreises außerhalb der Gewässer, die
  BarentsWatch veröffentlicht, nennt der Dialog den Anteil, bevor das Gebiet
  angelegt wird. Wählen Sie **OK**, um den Kreis trotzdem zu behalten.

### Ändern, was es zeigt: die Optionen

Öffnen Sie **Einstellungen → Geräte & Dienste → Live Track Ships →
Konfigurieren** (das Zahnrad) beim Gebiet, das Sie ändern wollen. Jede Option,
in einfachen Worten:

| Option | Was sie bewirkt | Standard |
|---|---|---|
| **Mittelpunkt** | verschiebt das Gebiet; es wird nach seiner neuen Position benannt und neu geladen | Ihr Zuhause |
| **Radius (km)** | wie weit vom Mittelpunkt Schiffe gezeigt werden, 1 bis 500 km (0,6 bis 310 Meilen) | 50 km (31 Meilen) |
| **Höchstzahl verfolgter Schiffe** | eine Sicherheitsgrenze für dieses Gebiet, 1 bis 5.000; gibt es mehr, werden die nächsten behalten | 1.000 |
| **Höchstzahl der Schiffe auf der Karte, alle Live-Track-Ships-Einträge zusammen** | die Obergrenze für alle Ihre Gebiete zusammen, 100 bis 2.500; senken Sie sie auf einem kleinen Rechner; es gilt die niedrigste Einstellung aller Gebiete | 2.500 |
| **UDP-Port (eigener Empfänger)** | der Port, an den Ihr Empfänger sendet; eine Änderung lädt das Gebiet neu | 10110 |

Wie viele Schiffe ein Kreis enthält, hängt viel mehr davon ab, welches
Gewässer es ist, als davon, wie groß er ist. Im Test enthielt ein Kreis von
50 km (31 Meilen) etwa 4 Schiffe über Chicago (USA) und etwa 340 über dem
Solent (England): derselbe Radius, etwa 80-mal so viel Verkehr. Wenn eine
Grenze die Liste kürzt, sagt das der `sensor.ships_in_range` des Gebiets.

---

## Kostenlose Schlüssel, die mehr freischalten, Schritt für Schritt

Alle sind kostenlos und persönlich: Jede Person, die Live Track Ships
installiert, bekommt ihre eigenen. Fügen Sie jeden im Einrichtungsdialog ein,
wenn Sie ein Gebiet anlegen (Schritt 5 der
[Einrichtung](#einrichtung-schritt-für-schritt)).

### aisstream.io (Schiffe und beobachtete Schiffe, die ganze Welt)

1. Öffnen Sie <https://aisstream.io/account> und melden Sie sich an. (Der Link
   **API keys** oben auf aisstream.io öffnet dieselbe Seite.)
2. Erstellen Sie dort einen neuen API-Schlüssel.
3. Kopieren Sie den Schlüssel sofort: aisstream.io zeigt ihn nur einmal.
4. Fügen Sie ihn in **API-Schlüssel** ein.

⚠ aisstream.io erlaubt drei Verbindungen je Konto und drei je öffentlicher
Internetadresse. Live Track Ships nutzt höchstens zwei: eine für alle Ihre
Gebiete und eine für Ihre beobachteten Schiffe, die es mit Live Track SALT
teilt, wenn das mit demselben Schlüssel installiert ist. Nutzen andere
Programme denselben Schlüssel oder dieselbe Internetverbindung, zählen Sie sie
mit.

### BarentsWatch (Schiffe in norwegischen Gewässern, Norwegen)

1. Öffnen Sie <https://www.barentswatch.no/minside/> und legen Sie einen
   Benutzer an, oder melden Sie sich an.
2. Wählen Sie unter **API access (for developers)** (*API-tilgang (for
   utviklere)*) **New Client** (*Ny klient*).
3. Wählen Sie den AIS-Client, nicht den API-Client.
4. Kopieren Sie die **Client-ID**. Sie sieht so aus:
   `your.email@example.com:live_track_ships`. Fügen Sie sie genau so in
   **Client-ID** ein.
5. Kopieren Sie das **Client-Secret** in **Client-Secret**. Es wird nur einmal
   gezeigt; haben Sie es nicht aufbewahrt, erzeugen Sie ein neues.

---

## Die Karte auf ein Dashboard bringen

Die Karte ist [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
die Karte, auf der jedes Live-Track-Modul zeichnet. **Sie wird mit Live Track
Ships installiert**: nichts herunterzuladen, nichts zu kopieren, keine
Ressource hinzuzufügen.

1. Öffnen Sie ein Dashboard, wählen Sie den Stift (**Dashboard bearbeiten**),
   dann **Karte hinzufügen**.
2. Scrollen Sie nach unten und wählen Sie **Manuell**.
3. Fügen Sie dies ein und wählen Sie **Speichern**:

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

Die Markierungen brauchen
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities) aus dem
Marketplace. Sind andere Live-Track-Module installiert, fügen Sie für jede
ihrer Quellen einen weiteren Filter `- domain: geo_location` hinzu
(`live_track_aircraft`, `live_track_weather` und so weiter).

**Auf der Karte:**

* Jedes Schiff wird mit seinem eigenen Bild gezeichnet, nach seinem Kurs
  gedreht, und gleitet zwischen seinen gemeldeten Positionen über das Wasser
  statt über das Land.
* **Zeigen** Sie auf ein Schiff, um seinen Namen zu sehen, und sein Foto, wenn
  es eines gibt. **Klicken** Sie darauf für sein Foto, seine Links, **Track**
  und **Details** ([Fotos und Links](#fotos-und-links), [Spuren](#spuren)).
* Die **Filterkarte** (`custom:live-track-map-filter-card`) blendet die
  Schiffstypen aus, deren Häkchen Sie entfernen
  ([Schiffstypen ausblenden](#schiffstypen-ausblenden)).

Sind die Ressourcen Ihrer Dashboards in YAML festgelegt
(`lovelace: resource_mode: yaml`), kann nichts für Sie registriert werden: Ein
Eintrag unter **Reparaturen** nennt dann die genaue Zeile, die Sie hinzufügen
müssen. Eine Karte, die Sie selbst über den Marketplace installiert haben,
bleibt unberührt. Werden die Dateien der Integration entfernt, während ihre
Gebiete noch eingerichtet sind, und ist kein anderes Live-Track-Modul
installiert, entfernen Sie die Zeile der Karte selbst unter **Einstellungen →
Dashboards → Ressourcen**. Jede andere Kartenkarte, die
`geo_location`-Entitäten zeigt, zeigt die Schiffe auch, ohne ihre Bilder.

---

## In Automationen verwenden

Alles ist eine gewöhnliche Home-Assistant-Entität oder ein gewöhnliches
Ereignis, also funktioniert der Automationseditor damit, ohne Code.

**Eine Benachrichtigung, wenn ein Schiff über 150 m (490 Fuß) in Ihr Gebiet
kommt:**

1. **Einstellungen → Automationen & Szenen → Automation erstellen → Neue
   Automation erstellen**.
2. **Sobald**: **Auslöser hinzufügen**, suchen Sie nach **Manuelles Ereignis
   empfangen**, und geben Sie als **Ereignistyp** `live_track_ships_entry` ein.
3. **Und wenn**: **Bedingung hinzufügen** → **Template**, und geben Sie dieses
   **Wert-Template** ein: `{{ trigger.event.data.length_m | default(0) > 150 }}`
4. **Dann**: **Aktion hinzufügen**, suchen Sie die Benachrichtigungsaktion
   Ihres Handys (sie trägt den Namen Ihres Handys), und geben Sie diese
   Nachricht ein:

   ```text
   {{ trigger.event.data.name | default('Ein Schiff') }}, {{ trigger.event.data.length_m }} m, {{ trigger.event.data.distance_km }} km entfernt
   ```

5. **Speichern**.

**Weitere Ideen:** ein Licht an, wenn die Abendfähre Ihren Hafen in Norwegen
erreicht; eine Nachricht, wenn das Boot eines Familienmitglieds, ein
beobachtetes Schiff, nach Finnland heimkommt; eine Benachrichtigung, wenn das
Kreuzfahrtschiff, das Sie abholen, in Sydney (Australien) ankommt; eine
Anzeige der Schiffe in Ihrem Hafen auf dem Dashboard aus
`sensor.ships_in_range`.

**Die Gebietsereignisse.** Jedes Gebiet löst `live_track_ships_entry` aus,
wenn ein Schiff in seinen Kreis kommt, und `live_track_ships_exit`, wenn es
ihn verlässt. Jedes Schiff wird gemeldet; Ihre Automation wählt die, auf die es
ankommt. Die Felder haben dieselben Namen und Einheiten wie die Attribute des
Schiffs und lassen weg, was die Quelle nicht gesendet hat:

| Feld | Was es enthält |
|---|---|
| `area_id`, `area` | die ID des Konfigurationseintrags des Gebiets und sein Titel |
| `identity` | die MMSI |
| `name`, `call_sign`, `imo` | wenn gesendet |
| `object_kind` | `vessel`, `net_buoy`, `aton`, `base_station`, `sar_aircraft` oder `distress_beacon` |
| `ship_type`, `ship_type_label`, `length_m`, `beam_m`, `draught_m`, `destination`, `nav_status` | nur Schiffe, wenn gesendet |
| `speed_kmh`, `course_deg`, `heading_deg` | wenn gesendet |
| `latitude`, `longitude`, `distance_km`, `bearing_from_centre_deg`, `last_seen` | wo es gehört wurde, vom Mittelpunkt des Gebiets aus |
| `entity_id` | nur beim Eintritt: `geo_location.vessel_<MMSI>`, wenn das Schiff auf der Karte ist |
| `reason` | nur beim Austritt: `left` (außerhalb des Kreises gehört) oder `silent` (eine Weile nicht gehört, also vielleicht noch da) |

⚠ Vier Dinge, die Sie wissen sollten:

* **Eine Ankunft wird nur gemeldet, wenn das Schiff zuerst außerhalb des
  Kreises gehört wurde.** Ein Schiff, das zuerst innerhalb gehört wird, war
  vielleicht die ganze Zeit da: Nach einem Neustart liefern die Quellen noch
  minutenlang Schiffe, die sich nicht bewegt haben. Ein Schiff, das die
  Empfänger auf dem Weg hinein verpasst haben, oder eines, das seinen
  Transponder innerhalb einschaltet, wird also nicht gemeldet.
* **Eine außerhalb gehörte Abfahrt wird immer gemeldet**, auch für ein Schiff,
  das schon vor dem Start von Home Assistant da war. Ein Schiff, das verstummt,
  wird nur dann als abfahrend gemeldet (`reason: silent`), wenn seine Ankunft
  gemeldet wurde.
* **Ein Austritt wartet 2 Minuten.** Ein Schiff, das früher zurückkommt, am
  Rand des Kreises entlang, wird nicht als abfahrend und wieder ankommend
  gemeldet.
* **Bei der Ankunft können Angaben fehlen.** Name, Typ und Größe kommen in
  einer langsameren Nachricht als die Position. Ein Schiff, das zum ersten Mal
  gehört wird, kann nur mit einer Position und sonst nichts ankommen.

Zwei Gebiete über demselben Gewässer lösen jeweils ihre eigenen Ereignisse
aus. Die Grenzen, wie viele Schiffe gezeichnet werden, lassen nie ein Schiff
eintreten oder austreten.

**Das Ereignis der beobachteten Schiffe.**
[Beobachtete Schiffe](#beobachtete-schiffe-ausgewählte-schiffe-überall) lösen
ein Ereignis aus, `live_track_ships_watched`, dessen `change` sagt, was
geschehen ist:

| `change` | Wann |
|---|---|
| `arrived` | das Schiff meldet sich als festgemacht oder vor Anker, oder bleibt ohne Status unter 3,7 km/h (2 Knoten) |
| `departed` | es ist wieder in Fahrt |
| `silent` | 30 Minuten nicht gehört (6 Stunden, wenn festgemacht oder vor Anker); es verlässt die Karte und ist vielleicht noch da |
| `heard` | nach `silent` wieder gehört |
| `destination` | die Besatzung hat das Ziel geändert; `destination_previous` enthält das alte |

Die Daten enthalten `watch_id`, `watch`, `identity`, Ihr `label` und dieselben
Schiffsfelder wie die Gebietsereignisse, mit Entfernung und Peilung von Ihrem
Zuhause aus. Ankunft und Abfahrt warten, bis der neue Zustand 5 Minuten nach
der eigenen Uhr des Schiffs gehalten hat, damit ein langsam treibendes Boot
nicht hin und her springt. Aus der ersten Position eines Schiffs nach einem
Neustart wird nichts gemeldet: Sie setzt den Ausgangspunkt. Ziele werden von
der Besatzung eingetippt und sind oft veraltet.

---

## Alles auf der Karte im Detail

AIS (Automatic Identification System, automatisches Identifikationssystem) ist
eine UKW-Funkaussendung, mit der Schiffe einander und dem Land ihre Position,
ihre Identität und ihre Reise mitteilen. Es ist die Seefahrtsversion dessen,
was Flugzeuge als ADS-B senden. Berufsschiffe müssen es an Bord haben; viele
Sportboote haben es freiwillig, meist als schwächeres Gerät der Klasse B. AIS
wird offen gesendet: Jeder mit einem Empfänger kann es hören, und öffentliche
Dienste geben es weiter. **Live Track Ships zeigt alles, was die Quelle
sendet.** Nichts wird herausgefiltert, und es gibt keine Einstellung, um eine
Kategorie vor Home Assistant zu verbergen.

### Schiffe

Jedes Schiff ist eine Markierung, deren Zustand ihre Entfernung vom
Mittelpunkt des Gebiets in Kilometern ist. Die meisten Schiffe werden nach Typ
gezeichnet: Frachter, Tanker, Fähre, Schlepper und so weiter. Manche bekommen
ein eigenes Bild: königliche und staatliche Jachten und bekannte Boote wie die
Ausflugsboote, Wassertaxis und Feuerlöschboote einer Stadt. Kennen Sie ein
Schiff, das eines verdient, irgendwo auf der Welt?
[Schlagen Sie es vor](#helfen-sie-mit-es-zu-erweitern), mit seinem Namen und
seiner MMSI- oder IMO-Nummer, und einem Foto oder Link, wenn Sie einen haben.

Damit ein Schiff sofort verschwindet, wenn es geht, wird jede Online-Quelle um
einen Ring gebeten, der etwas breiter ist als Ihr Kreis (10 %, mindestens
1 km), und Ihr eigener Empfänger sendet alles, was er hört. Nur Schiffe
innerhalb Ihres Kreises werden behalten: Ein außerhalb gehörtes Schiff
verlässt die Karte sofort. Ein Schiff, das nicht wieder gehört wird,
verschwindet nach einer Zeit der Stille. Ein Schiff, das nicht mehr erscheint,
ist nicht unbedingt weg: Keine dieser Quellen verspricht, jede Nachricht zu
liefern.

⚠ **Der Schiffstyp fehlt oft, besonders bei kleinen Booten.** Position und
Name kommen mit fast jeder Nachricht. Typ und Größe kommen in einer eigenen,
langsameren Nachricht, und viele Geräte der Klasse B senden sie selten.
Rechnen Sie damit, dass viele Schiffe, darunter die meisten kleinen Boote,
keinen Typ und keine Größe zeigen, und dass alle Schiffe in den ersten Minuten
nach einem Neustart von Home Assistant wenige Angaben haben. Das sind die
Daten, kein Fehler. Einmal gehörte Typen und Größen bleiben über Neustarts
erhalten.

Zu den Attributen eines Schiffs gehören Name, MMSI, Rufzeichen,
Geschwindigkeit, Kurs, Steuerkurs, Länge, Breite, Schiffstyp, Ziel,
`object_kind`, `last_seen` und `attribution`, jedes nur, wenn die Quelle es
gesendet hat. Ein Schiff, das zwei Gebiete sehen, ist eine Entität.

### Private Boote und Segelboote

Ein Sportboot, das AIS sendet, erscheint auf Ihrer Karte genau wie ein
Frachter. Je nachdem, was das Boot sendet, kann seine Entität enthalten:

* seinen **Namen**, der auch die Beschriftung auf der Karte ist;
* seine **MMSI** und sein **Funkrufzeichen**, beide dauerhaft und öffentlich
  auffindbar;
* seine **Position** auf etwa einen Meter genau, seine vorherige Position und
  wann jede gehört wurde;
* Geschwindigkeit, Kurs und Steuerkurs, sowie Länge, Breite und Typ, wenn
  gesendet.

Ein Boot, das seinen Transponder am Steg eingeschaltet lässt, bleibt an seinem
Liegeplatz auf der Karte, solange es sendet. Wer Ihre Karte öffnen kann, kann
bei einem solchen Boot auch **Track** drücken und sehen, wo es in den letzten
24 Stunden war (oder so lange, wie Sie einstellen), sein Liegeplatz
eingeschlossen.

Für AIS gibt es keine Sperrliste wie für Flugzeuge, und diese Integration
erfindet keine. Wenn Sie weniger private Boote auf Ihrer Karte wollen,
verkleinern Sie den Radius.

### Was keine Schiffe sind

Jede Entität trägt `object_kind`: `vessel`, `net_buoy` (Fanggerätboje),
`aton` (Navigationshilfe: eine Tonne, Bake oder ein Leuchtturm),
`base_station` (eine AIS-Station an Land), `sar_aircraft` (ein Such- und
Rettungsflugzeug) oder `distress_beacon`. Die meisten werden am
Identitätsformat unterschieden, das die Internationale Fernmeldeunion (ITU)
ihnen gibt. Fanggerätbojen nicht: Sie senden mit Identitäten wie Schiffe, also
werden sie an ihren Werksnamen erkannt (FISHING BOUY, NET MARK, BUOY),
zusammen mit dem Fehlen einer gesendeten Länge.

Alles, was kein Schiff ist, wird ohne Schiffstyp, Größe und Navigationsstatus
gezeigt. Fanggerätbojen treiben mit ihren Leinen, also behalten sie
Geschwindigkeit und Kurs und werden als Fisch gezeichnet, der in ihre
Treibrichtung zeigt.

Welche davon erscheinen, hängt von der Quelle ab. Gemessen an einem Abend:

| Quelle | Fanggerätbojen | Such- und Rettungsflugzeuge | Navigationshilfen, Basisstationen |
|---|---|---|---|
| BarentsWatch | ja | ja | keine gesehen |
| Digitraffic | keine gesehen | ja | keine gesehen |
| aisstream.io | keine gesehen | keine gesehen | keine gesehen |
| Ihr eigener Empfänger | was er hört | was er hört | was er hört |

aisstream.io lieferte nur Schiffspositionen und Schiffsdaten, sowohl über den
Großen Seen (Nordamerika) als auch über denselben norwegischen und dänischen
Gewässern, wo BarentsWatch die Bojen zeigt.

### Küstenwachschiffe im Einwanderungseinsatz

Ein Schiff auf der öffentlichen Liste
[EnforcementVessels](https://github.com/StrausbergAutomationWorks/EnforcementVessels)
(Schiffe der Küstenwache der USA im Einwanderungseinsatz) wird in den Farben
der Küstenwache gezeichnet, mit dem Namen und der Behörde aus der Liste, wo
immer es gehört wird.

### Beobachtete Schiffe: ausgewählte Schiffe überall

Neben Gebieten können Sie einer Liste von Schiffen folgen, wo immer sie sind:
dem Boot eines Familienmitglieds, einer Fähre, die Sie nehmen, einem
Kreuzfahrtschiff auf dem Heimweg. Dafür brauchen Sie einen
aisstream.io-Schlüssel, und es gibt eine solche Liste je Home Assistant.

1. Öffnen Sie **Einstellungen → Geräte & Dienste**, wählen Sie **Integration
   hinzufügen** und suchen Sie nach **Live Track Ships**.
2. Wählen Sie **Ausgewählte Schiffe, wo immer sie sind**.
3. **API-Schlüssel**: Der Schlüssel eines Gebiets, das Sie schon eingerichtet
   haben, ist eingetragen.
4. **Schiffe**: ein Schiff je Zeile, seine 9-stellige MMSI, dann, wenn Sie
   wollen, eine eigene Bezeichnung:

   ```text
   244650000 Papas Boot
   366999999 Die Fähre
   ```

5. Wählen Sie **OK**.

Höchstens 100 Schiffe. aisstream.io folgt höchstens 200 MMSI je Schlüssel, und
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
wenn mit demselben Schlüssel installiert, nutzt einen Teil davon. Eine Liste,
die darüber ginge, wird beim Laden des Eintrags mit Begründung abgelehnt. Um
die Liste zu ändern, öffnen Sie beim Eintrag **Konfigurieren**.

Ein beobachtetes Schiff wird wie jedes andere auf der Karte gezeichnet, wo
immer es gehört wird, und sein Zustand ist seine Entfernung von Ihrem Zuhause.
Ein Gebiet, das es schon zeigt, behält es: ein Schiff, eine Markierung. Der
Eintrag fügt `sensor.watched_vessels` hinzu: wie viele der aufgelisteten
Schiffe gerade gehört werden. Sein Attribut `vessels` listet jedes von ihnen
auf, mit seiner Bezeichnung und seinem letzten bekannten Zustand. Sein
Ereignis ist unter [In Automationen verwenden](#in-automationen-verwenden)
beschrieben.

### Fotos und Links

Wenn ein Schiff eine IMO-Nummer sendet und Wikidata ein Foto dieses Schiffs
auf Wikimedia Commons kennt, trägt das Schiff `marker_photo`. Die Karte zeigt
das Foto, wenn Sie auf das Schiff zeigen, mit Fotograf und Lizenz; ein Klick
öffnet es größer, mit Links zur Seite des Fotos und zu seiner Lizenz. Jedes
Schiff mit IMO-Nummer oder MMSI trägt außerdem `marker_links`, einen Link zum
Schiff bei VesselFinder. Die Schaltfläche **Details** im Popup öffnet den
gewohnten Dialog des Schiffs.

Ihr Home Assistant fragt Wikidata und Commons selbst, 20 IMO-Nummern auf
einmal, zehn Sekunden auseinander, und behält jede Antwort 30 Tage (14 Tage,
wenn es kein Foto gibt) in `.storage/saw_vessel_photos.json`. Rechnen Sie mit
Fotos für etwa jedes zehnte Schiff: Auf unserem Testsystem hatten 49 von 521
IMO-Nummern eines.

⚠ Ein Foto kann das Schiff unter einem früheren Namen zeigen: Die IMO-Nummer
gehört zum Rumpf und bleibt bei ihm, wenn das Schiff umbenannt wird.

### Spuren

Jedes Schiff trägt auch `marker_track`. Klicken Sie auf ein Schiff und drücken
Sie **Track** in seinem Popup: Die Karte zeichnet, wo es war, als eine Linie,
die beim Schiff endet, und die Linie wächst, während Sie zusehen. **Hide
track** nimmt sie wieder weg. Nichts wird gezeichnet, bevor Sie fragen, damit
ein belebter Hafen nicht unter Linien verschwindet.

Die Spur enthält nur Positionen, die das Schiff gemeldet hat, während es auf
Ihrer Karte war, ausgedünnt auf eine alle 25 m (82 Fuß) oder 10 Minuten, und
nie zwei innerhalb von 30 Sekunden. Ihr Home Assistant hält sie im Speicher und
sichert sie in `.storage/saw_vessel_tracks.json`, sodass sie einen Neustart
übersteht. Sie umfasst die letzten 24 Stunden. Um mehr oder weniger zu
behalten:

1. Öffnen Sie **Einstellungen → Werkzeuge → Aktionen**.
2. Wählen Sie die Aktion **Live Track Ships: Spurdauer festlegen**.
3. Geben Sie **Stunden** ein, von 1 bis 168 (eine Woche), und wählen Sie
   **Aktion ausführen**.

Das gilt für alle Gebiete auf einmal; eine kürzere Einstellung verwirft ältere
Positionen sofort.

⚠ Die Spur beginnt bei einer Erstinstallation leer. Ein Schiff, das das Gebiet
verlassen hat oder still war, hat eine Lücke, gezeichnet als gerade Linie
zwischen den Positionen davor und danach.

### Schiffstypen ausblenden

Jedes Schiff trägt `marker_group`, `marker_group_label` und
`marker_group_order`: eine von dreizehn Gruppen (Fracht; Tanker; Passagier
und Fähre; Fischerei; Sport und Segeln; Schlepper, Lotse und Hafendienst;
Behörden, Seenotrettung und Polizei; Schnellboote und Sonstige; Typ nicht
gesendet; Fanggerätbojen; Navigationshilfen; Basisstationen; Such- und
Rettungsflugzeuge). Die Filterkarte der Kartenkarte,
`custom:live-track-map-filter-card`, listet die Gruppen mit der Anzahl auf der
Karte und blendet die aus, deren Häkchen Sie entfernen. Legen Sie sie auf eine
beliebige Ansicht des Dashboards. Ihre Wahl wird nur in diesem Browser
gespeichert.

Ausgeblendet wird nur auf der Karte: Die Integration zählt weiterhin jedes
Schiff und löst ihre Ereignisse für jedes Schiff aus. Eine Notfunkbake hat
keine Gruppe und wird daher nie ausgeblendet.

---

## Alle Entitäten, die es anlegt

| Entität | Was sie ist |
|---|---|
| `geo_location.vessel_<MMSI>` | eine Markierung für jedes Schiff oder andere AIS-Objekt; ihr Zustand ist die Entfernung vom Mittelpunkt des Gebiets (oder von Ihrem Zuhause, bei einem beobachteten Schiff), in Kilometern. Sie kommt und geht und hat keine eindeutige ID |
| `sensor.ships_in_range` | einer je Gebiet: wie viele Schiffe es zeigt, und ob eine Grenze die Liste gekürzt hat |
| `sensor.ais_station` | nur Ihr eigener Empfänger: Nachrichten pro Minute. Seine Attribute nennen `vessels_heard` (in den letzten 10 Minuten), `farthest_km` und `farthest_mmsi` (vom Mittelpunkt des Gebiets), `last_message`, `udp_port`, `listening`, und `port_error`, wenn der Port sich nicht öffnen lässt. Er aktualisiert alle 30 Sekunden, also zeigt ein Empfänger, der nichts mehr sendet, 0 |
| `sensor.watched_vessels` | nur beobachtete Schiffe: wie viele Ihrer aufgelisteten Schiffe gerade gehört werden |

Attribute, die sich bei jeder Aktualisierung ändern, bleiben aus dem Verlauf
von Home Assistant heraus, damit Ihre Datenbank nicht mit ihnen wächst:
`marker_photo`, `marker_links` und `marker_track` jedes Schiffs und die sich
schnell ändernden Attribute der Sensoren.

**Ihre Datenbank.** Der Recorder von Home Assistant speichert jedes Mal eine
neue Zeile, wenn sich eine Entität ändert, und ein fahrendes Schiff ändert
sich mit jeder Position, die es meldet. Auf unserem Testsystem schrieb ein
Gebiet mit 43 Schiffen in etwa 30 Stunden 27.109 Zeilen, 8,8 % der ganzen
Datenbank. Standardmäßig behält der Recorder 10 Tage und räumt jede Nacht um
04:12 Ortszeit auf, also flacht das Wachstum ab, aber bei einer Größe, die Sie
vielleicht nicht wollen.

Ein Schiff behält bei jedem Erscheinen dieselbe Entitäts-ID,
`geo_location.vessel_<MMSI>`, also erfasst ein Muster,
`geo_location.vessel_*`, alles, was diese Integration je auf die Karte
gebracht hat. Um nur den letzten Tag davon zu behalten:

1. **Einstellungen → Automationen & Szenen → Automation erstellen → Neue
   Automation erstellen**.
2. Öffnen Sie das Dreipunktmenü, wählen Sie **In YAML bearbeiten**, ersetzen
   Sie alles durch dies und wählen Sie **Speichern**:

```yaml
alias: Schiffsverlauf kürzen
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

Lassen Sie `keep_days` weg (Standard 0), verschwinden alle ihre Zeilen auf
einmal. Um nichts davon aufzuzeichnen, setzen Sie das Muster in
`configuration.yaml` unter `recorder:` → `exclude:` → `entity_globs:`; eine
Kartenkarte, die den Verlauf zeichnen soll (`history_start`), hat dann keine
Spur zu zeichnen. `sensor.ships_in_range` ist eine einfache Zahl und billig zu
behalten.

---

## Was es sendet und herunterlädt

**Über Ihren Standort.** Der Mittelpunkt jedes Gebiets ist Ihr Zuhause, außer
Sie verschieben ihn. Er geht nur an die Quelle, die Sie für dieses Gebiet
gewählt haben: an aisstream.io als Rechteck um einen etwas größeren Kreis als
Ihren (10 %, mindestens 1 km); an Digitraffic (Finnland) als Mittelpunkt und
dieser größere Radius; an BarentsWatch (Norwegen) als dieser größere Kreis.
Für beobachtete Schiffe gehen die MMSI-Nummern Ihrer Liste an aisstream.io.
Ihr eigener Empfänger sendet nichts irgendwohin: Home Assistant hört nur zu.
Für Fotos gehen die IMO-Nummern der Schiffe auf Ihrer Karte an Wikidata und
Wikimedia Commons, ohne etwas über Sie. Um all das zu beenden, löschen Sie das
Gebiet oder den Eintrag der beobachteten Schiffe unter **Einstellungen →
Geräte & Dienste → Live Track Ships**. Sonst wird nichts über Sie irgendwohin
gesendet.

**Wie viel.**

* **aisstream.io**: eine Verbindung für alle Ihre Gebiete und eine für Ihre
  beobachteten Schiffe, beide offen gehalten; Schiffe kommen an, wenn sie
  melden. Nach einem Fehler verbindet es sich nach einer Pause neu.
* **Digitraffic**: Positionen alle 60 Sekunden und Schiffsdaten alle 15
  Minuten, nur für Ihren Kreis. Nach einem Fehler versucht es es beim nächsten
  Durchgang wieder.
* **BarentsWatch**: ein offen gehaltener Datenstrom je Gebiet. Kommt
  150 Sekunden lang nichts, verbindet es sich neu.
* **Fotos**: 20 IMO-Nummern auf einmal, 10 Sekunden auseinander, nur für
  Schiffe, nach denen in den letzten 30 Tagen nicht gefragt wurde (14, wenn es
  kein Foto gab). Eine fehlgeschlagene Anfrage wird später wiederholt.
* **Ihr eigener Empfänger**: Es wird nichts heruntergeladen.

---

## Helfen Sie mit, es zu erweitern

Live Track Ships wächst noch. Wir fügen Datenquellen und Länder hinzu, sobald
wir sie finden, und wir möchten wissen, was Sie sich als Nächstes wünschen.

### Etwas vorschlagen

Fehlt Ihr Land oder Ihr AIS-Dienst? Ist etwas falsch oder schwer zu verstehen?
Sagen Sie es uns auf dem Weg, der für Sie einfacher ist:

* [**Füllen Sie ein kurzes Formular aus**](https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues/new?template=de.yml)
  auf Deutsch. Sie brauchen ein kostenloses GitHub-Konto.
* **Schreiben Sie eine E-Mail** an
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Kein Konto nötig.

In beiden Fällen hilft es, wenn Sie uns sagen:

* was Sie gern sehen würden, und wo auf der Welt;
* einen Link, wo die Daten veröffentlicht werden, falls Sie einen kennen (eine
  Open-Data-Seite, ein öffentlicher Feed, die Website eines Dienstes): nicht
  nötig, aber hilfreich;
* die Sprache Ihres Home Assistant, wenn es um die Formulierung oder eine
  Übersetzung geht.

Schreiben Sie auf Englisch oder in Ihrer eigenen Sprache, was für Sie
einfacher ist.

### Selbst etwas hinzufügen, mit unserer Hilfe

Wenn Sie selbst etwas hinzufügen möchten, helfen wir Ihnen dabei, von der
ersten Frage bis zur fertigen Veröffentlichung. Sie müssen kein Entwickler
sein, um anzufangen:

* **Eine Übersetzung.** Die Texte im Einrichtungsdialog sind eine kurze Liste
  von Sätzen in einer Textdatei. Wir zeigen Ihnen, welche Datei und welche
  Zeilen.
* **Eine neue Datenquelle.** Sagen Sie uns, wo die Daten veröffentlicht
  werden. Wir können den Code gemeinsam schreiben oder Ihren durchsehen.
* **Testen, wo Sie wohnen.** Installieren Sie es, sehen Sie sich Ihren Teil
  der Karte an, und sagen Sie uns, was stimmt und was nicht.
* **Eine Korrektur dieser README.** Wenn ein Schritt nicht zu dem passte, was
  Sie gesehen haben, sagen Sie uns, was Sie gesehen haben.

[**Sagen Sie uns, was Sie vorhaben**](https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues/new?template=de.yml)
oder schreiben Sie an
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
und wir antworten mit den nächsten Schritten.

---

## Sprachen

Diese README: [English](README.md), **Deutsch**, [Français](README.fr.md),
[Nederlands](README.nl.md), [简体中文](README.zh-Hans.md),
[Español](README.es.md), [Italiano](README.it.md), [Dansk](README.da.md) und
[Kalaallisut](README.kl.md) (ein kurzer Entwurf, zur Durchsicht an
Oqaasileriffik geschickt, das Sprachsekretariat Grönlands; bis dahin ist die
dänische Seite die verlässliche). Jede übersetzte README ist vollständig.

Der Einrichtungsdialog und die Optionen erscheinen in der Sprache Ihres Home
Assistant, wenn es eine dieser ist: English, Dansk, Deutsch, Español,
Français, Gaeilge, Íslenska, Italiano, Nederlands, Norsk Bokmål, Polski,
Português, Português (BR), Suomi, Svenska und 简体中文. Jede andere Sprache
zeigt Englisch. Kalaallisut ist noch keine Sprache von Home Assistant; wir
haben Home Assistant gebeten, sie hinzuzufügen. Die Beschriftungen der
Kartenkarte (**Track**, **Details**) sind in jeder Sprache englisch.

Einen Fehler in einer Übersetzung gefunden, oder eine andere Sprache nötig?
Sagen Sie es uns unter
<https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues>, oder
[übersetzen Sie mit unserer Hilfe](#selbst-etwas-hinzufügen-mit-unserer-hilfe).

---

## Danksagungen und Lizenzen

* **aisstream.io**: keine veröffentlichten Bedingungen. <https://aisstream.io>
* **Fintraffic Digitraffic** (Finnland): Daten unter CC BY 4.0.
  <https://www.digitraffic.fi/en/terms-of-service/>
* **BarentsWatch** (Norwegen): Daten unter der norwegischen Lizenz für offene
  Verwaltungsdaten (NLOD).
  <https://www.barentswatch.no/en/articles/api-terms-and-conditions/>
* **Ihr eigener Empfänger**: Ihre eigenen Daten.
* **Wikidata**: CC0. **Wikimedia Commons**: jedes Foto unter seiner eigenen
  Lizenz, gezeigt mit Fotograf und Lizenz.
* **VesselFinder**: nur verlinkt; von dort wird nichts abgerufen.
* **EnforcementVessels**: ODbL 1.0.
  <https://github.com/StrausbergAutomationWorks/EnforcementVessels>

Was diese Integration ändert: Einheiten werden umgerechnet, und nur Schiffe
innerhalb Ihres Kreises werden behalten. Jede Schiffsentität und der
`sensor.ships_in_range` jedes Gebiets tragen eine `attribution`, die ihre
Quelle nennt; Home Assistant zeigt sie in den Details der Entität. Wenn Sie
diese Daten anderen zeigen, etwa auf einem öffentlichen Dashboard, behalten Sie
den Nachweis dabei und lesen Sie die eigenen Bedingungen der Quelle. Die
genauen Nachweiszeilen und die Nachweise für die Schiffsbilder stehen in
[ATTRIBUTION.md](ATTRIBUTION.md).

Keine dieser Organisationen hat diese Integration gemacht oder unterstützt.

**Code**: MIT, in [LICENSE](LICENSE).

**Für Entwickler:** AIS-Sätze von Ihrem eigenen Empfänger dekodiert
[pyais](https://github.com/M0r13n/pyais) (MIT); Home Assistant installiert
`saw-livetrack` und `pyais` selbst, wenn es die Integration zum ersten Mal
lädt. Die Tests in `tests/` laufen jeweils einzeln mit Python; manche brauchen
ein installiertes Home Assistant, und die Tests `*_live` brauchen Ihre eigenen
Schlüssel.

---

## Stichwörter

Home Assistant Schiffe · Home Assistant AIS · Schiffsverfolgung ·
Schiffsortung · Bootsverfolgung · Schiffsverkehr Karte · AIS Kartenkarte ·
AIS-Empfänger · NMEA · AIS-catcher · aisstream.io · Digitraffic · BarentsWatch ·
ship tracking · vessel tracker · suivi des navires · scheepvaart volgen ·
seguimiento de barcos · tracciamento navi · skibstrafik · 船舶追踪 ·
geo_location · Kartenkarte · Lovelace · HACS · Marketplace · Live Track ·
LiveTrack · StrausbergAutomationWorks

---

**Würdigung.** StrausbergAutomationWorks würdigt die indigenen Völker aller
Länder und Gewässer auf dieser Karte, überall auf der Welt, und erweist ihren
Ältesten, in Vergangenheit und Gegenwart, seinen Respekt.
