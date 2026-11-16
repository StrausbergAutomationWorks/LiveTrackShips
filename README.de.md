# Live Track Ships

[English](README.md) · **Deutsch** · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Kalaallisut](README.kl.md) · [Alle Sprachen](#sprachen)

**AIS-Verfolgung von Schiffen, Booten und anderen Wasserfahrzeugen für Home
Assistant.** Schiffe in Ihrer Nähe oder an jedem beliebigen Ort der Welt als
Live-Markierungen auf Ihrer Karte. Teil von Live Track: Schiffe, Flugzeuge und
Züge auf einer Karte.

Live-AIS-Daten von [aisstream.io](https://aisstream.io),
[Fintraffic Digitraffic](https://www.digitraffic.fi/en/marine-traffic/) oder
[BarentsWatch](https://www.barentswatch.no/en/), dargestellt als
`geo_location`-Entitäten von Home Assistant und gezeichnet auf der
gemeinsamen Live-Track-Karte.

**Status: 0.1.0, die erste Veröffentlichung.** Per Link zum Marketplace
hinzufügbar (siehe unten); im Katalog des Marketplace ist sie noch nicht.

## Was AIS ist

AIS (Automatic Identification System, automatisches Identifikationssystem)
ist ein UKW-Funksignal, mit dem Schiffe einander und dem Land ihre Position,
Identität und Reise mitteilen. Es ist das Gegenstück zu ADS-B in der
Luftfahrt. Berufsschiffe müssen es an Bord haben; viele Sportboote haben es
freiwillig, meist als schwächeres Gerät der Klasse B.

AIS wird unverschlüsselt gesendet. Jeder mit einem Empfänger kann es hören,
und öffentliche Sammeldienste veröffentlichen es weiter.

## Was angezeigt wird

**Alles, was die Quelle sendet.** Nichts wird herausgefiltert, und es gibt
keine Einstellung, um eine Kategorie auszublenden.

| In den Daten | Angezeigt |
|---|---|
| Frachter, Tanker, Schlepper, Fähren, Fahrgastschiffe | ja |
| Fischerei-, Lotsen-, Behörden- und andere Arbeitsfahrzeuge | ja |
| **Private Sportboote und Segelboote** | **ja, mit Name und Position** |
| **Fanggeräte-Bojen**, die AIS senden | **ja, als Fisch gezeichnet** |
| Such- und Rettungsflugzeuge (SAR) | wenn die Quelle sie sendet |
| Navigationshilfen: Tonnen, Baken, Leuchttürme | wenn die Quelle sie sendet |
| AIS-Landstationen | wenn die Quelle sie sendet |

### Auch private Boote werden angezeigt, und Sie sollten wissen, was das bedeutet

Ein Sportboot mit AIS erscheint auf Ihrer Karte genau wie ein Frachter. Je
nachdem, was das Boot sendet, kann seine Entität enthalten:

- seinen **Namen**, der auch als Beschriftung auf der Karte steht
- seine **MMSI** und sein **Rufzeichen**, beide dauerhaft und öffentlich
  auffindbar
- seine **Position** auf etwa einen Meter genau, die vorige Position und wann
  jede gehört wurde
- Geschwindigkeit, Kurs und Steuerkurs, sofern gesendet
- Länge, Breite und Schiffstyp, sofern gesendet

Ein Boot, das seinen Transponder am Liegeplatz eingeschaltet lässt, bleibt
dort auf der Karte, solange es sendet.

Für AIS gibt es keine Sperrliste wie für Flugzeuge, und diese Integration
erfindet keine. Wer weniger Sportboote auf der Karte möchte, verkleinert den
Radius.

### Der Schiffstyp fehlt oft, besonders bei kleinen Booten

Position und Name kommen mit fast jeder Meldung. Schiffstyp und Größe kommen
in einer eigenen, selteneren Meldung, und viele Geräte kleiner Boote
(Klasse B) senden den Teil, der sie enthält, selten. Rechnen Sie damit, dass
ein großer Teil der Schiffe, darunter die meisten kleinen, ohne Typ und
Maße erscheint, und dass alle Schiffe nach einem Neustart von Home Assistant
einige Minuten lang lückenhaft sind. Das liegt an den Daten, nicht an einem
Fehler. Einmal gehörte Typen und Größen bleiben über Neustarts erhalten.

### Nicht alles auf AIS ist ein Schiff

Jede Entität trägt `object_kind`: `vessel`, `net_buoy`, `aton`
(Navigationshilfe), `base_station`, `sar_aircraft` oder `distress_beacon`. Die
meisten werden am Format der Kennung erkannt, das die ITU ihnen zuteilt.
Fanggeräte-Bojen nicht: Sie senden mit schiffsartigen Kennungen und werden
deshalb an ihren Werksnamen (FISHING BOUY, NET MARK, BUOY) und an der fehlenden
Längenangabe erkannt.

Alles, was kein Schiff ist, erscheint ohne Schiffstyp, Größe oder
Navigationsstatus. Fanggeräte-Bojen treiben mit ihren Leinen; sie behalten
deshalb Geschwindigkeit und Kurs und werden als Lachs gezeichnet, der in
Treibrichtung zeigt.

Was davon erscheint, hängt von der Quelle ab. Gemessen an einem Abend:

| Quelle | Fanggeräte-Bojen | SAR-Flugzeuge | Navigationshilfen, Landstationen |
|---|---|---|---|
| BarentsWatch | ja | ja | keine gesehen |
| Digitraffic | keine gesehen | ja | keine gesehen |
| aisstream.io | keine gesehen | keine gesehen | keine gesehen |
| Ihr eigener Empfänger | was er hört | was er hört | was er hört |

aisstream.io lieferte nur Positions- und Schiffsdatenmeldungen, sowohl über
den Großen Seen als auch über denselben norwegischen und dänischen Gewässern,
in denen BarentsWatch die Bojen zeigt.

## Quellen

Für jedes Gebiet, das Sie einrichten, wählen Sie eine Quelle.

| Quelle | Abdeckung | Benötigt |
|---|---|---|
| aisstream.io | weltweit, wo Freiwillige Empfänger betreiben | einen kostenlosen API-Schlüssel |
| Fintraffic Digitraffic | finnische und baltische Gewässer | nichts |
| BarentsWatch AIS Live | norwegische Gewässer | kostenlose Client-ID und Client-Secret |
| Ihr eigener AIS-Empfänger | so weit Ihre Antenne hört | einen Empfänger, der NMEA per UDP sendet |

Welche Kategorien erscheinen, wie aktuell die Positionen sind und wie
vollständig die Schiffsdaten, hängt von der gewählten Quelle ab.

### Ihr eigener Empfänger

Wenn Sie einen AIS-Empfänger betreiben, kann Live Track Ships zeigen, was er
hört, ohne Konto und ohne Internet. Der Empfänger oder das Programm, das ihn
dekodiert, sendet NMEA-Sätze (`!AIVDM`) per UDP an die Adresse von Home
Assistant, auf einem Port Ihrer Wahl (10110, wenn Sie nichts ändern). In
AIS-catcher geschieht das mit `-u <address> <port>`, in rtl-ais mit
`-h <address> -P <port>`; OpenCPN und Signal K richten es als
UDP-Ausgangsverbindung ein. Ein Empfänger, der per USB angeschlossen wird,
etwa ein dAISy, braucht eines dieser Programme, um seine Sätze weiterzugeben.

- Ein Gebiet lauscht auf einem Port; zwei Empfänger brauchen zwei Ports.
- Alles, was der Empfänger in Ihrem Kreis hört, wird gezeigt, auch
  Navigationshilfen und Basisstationen. Der Stationssensor (unten) zählt auch,
  was er außerhalb des Kreises hört.
- Ein Satz enthält kein Datum, daher ist die Zeit einer Position der Moment,
  in dem Home Assistant ihn empfangen hat.
- Die Drehrate wird für diese Quelle nicht angezeigt.
- Bisher ist das mit aufgezeichneten Sätzen getestet, die per UDP gesendet
  wurden, nicht mit einem Empfänger. Wenn Sie es mit Ihrem ausprobieren,
  berichten Sie uns auf der [Issues-Seite](https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues), wie es lief.

### Quellenangaben

Jede Schiffsentität und der Sensor `ships_in_range` jedes Gebiets tragen ein
Attribut `attribution`, das die liefernde Quelle nennt; Home Assistant zeigt es
in den Details der Entität. Zwei der Quellen lizenzieren ihre Daten mit
Namensnennung, und Live Track Ships verändert die empfangenen Daten (Einheiten
umgerechnet, nur Schiffe in Ihrem Kreis), daher sagen ihre Zeilen das. Wenn
Sie diese Daten anderen zeigen, etwa auf einem öffentlichen Dashboard, behalten
Sie die Quellenangabe bei und lesen Sie die Bedingungen der Quelle:

- **aisstream.io**: keine veröffentlichten Bedingungen. <https://aisstream.io>
- **Fintraffic Digitraffic**: CC BY 4.0.
  <https://www.digitraffic.fi/en/terms-of-service/>
- **BarentsWatch**: Norwegische Lizenz für offene Behördendaten (NLOD).
  <https://www.barentswatch.no/en/articles/api-terms-and-conditions/>
- **Ihr eigener Empfänger**: Ihre eigenen Daten; die Zeile sagt das.
- **EnforcementVessels** (die Liste hinter der Küstenwachen-Darstellung,
  unten): ODbL v1.0.
  <https://github.com/StrausbergAutomationWorks/EnforcementVessels>

Die genauen Quellenzeilen stehen in [ATTRIBUTION.md](ATTRIBUTION.md).

## Voraussetzungen

- Home Assistant 2026.11 oder neuer, mit Internetzugang nach außen für die
  Online-Quellen.
- Für aisstream.io: ein kostenloser API-Schlüssel von
  [aisstream.io](https://aisstream.io/account). aisstream erlaubt **drei
  Verbindungen pro Konto und drei pro öffentlicher IP-Adresse**; wenn Sie
  andere Programme mit demselben Schlüssel betreiben, planen Sie das ein. Live
  Track SALT nutzt, falls installiert, eine zweite Verbindung mit demselben
  Schlüssel.
- Für BarentsWatch: kostenlose Client-ID und Client-Secret, selbst bei
  BarentsWatch registriert. Geben Sie die Client-ID genau so ein, wie sie
  ausgestellt wurde.
- Für Ihren eigenen Empfänger: einen Empfänger und ein Programm, die NMEA per
  UDP an Home Assistant senden, im selben Netzwerk. Internetzugang braucht er
  nicht.
- Home Assistant installiert die benötigten Python-Pakete (`saw-livetrack` und
  `pyais`) beim ersten Laden der Integration selbst.

## Installation

### Über den Marketplace

Live Track Ships ist noch nicht im Katalog des Marketplace. Fügen Sie sie per
Link hinzu:

1. **Einstellungen > Marketplace**, dann **Über Link hinzufügen**.
2. `StrausbergAutomationWorks/LiveTrackShips` eingeben. Wird nach dem Typ
   gefragt, **Integration** wählen.
3. **Live Track Ships** installieren.
4. Home Assistant neu starten. Der Marketplace bietet den Neustart als
   Reparatur unter **Einstellungen > System > Reparaturen** an.

### Von Hand

1. Den Quellcode der
   [neuesten Version](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest)
   herunterladen.
2. Den Ordner `custom_components/live_track_ships` daraus in den Ordner
   `custom_components` Ihres Home-Assistant-Konfigurationsverzeichnisses
   kopieren.
3. Home Assistant neu starten.

## Einrichtung

**Einstellungen > Geräte & Dienste > Integration hinzufügen > Live Track
Ships**, dann **Alle Schiffe in einem Gebiet** (die andere Wahl, verfolgte
Schiffe, steht [weiter unten](#verfolgte-schiffe-ausgewählte-schiffe-überall-verfolgen)).
Jedes Gebiet ist ein eigener Eintrag mit dem Titel *Ships near <Breite>,
<Länge>*. Der Dialog erscheint auf Deutsch, wenn Home Assistant auf Deutsch
eingestellt ist.

| Feld | Was es nimmt | Standard |
|---|---|---|
| Datenquelle | aisstream.io, Fintraffic Digitraffic, BarentsWatch AIS Live oder Ihr eigener AIS-Empfänger | aisstream.io |
| API-Schlüssel | nur aisstream.io. Aus einem bereits eingerichteten Gebiet übernommen; änderbar | leer |
| Client-ID, Client-Secret | nur BarentsWatch. Aus einem bereits eingerichteten Gebiet übernommen | leer |
| UDP-Port | nur Ihr eigener Empfänger: der Port, an den er NMEA sendet, 1024 bis 65535. Abgelehnt, wenn ein anderes Gebiet oder ein anderes Programm ihn schon nutzt | 10110 |
| Mittelpunkt | eine Markierung auf einer Karte; ziehen Sie sie zum gewünschten Gewässer | Ihr Zuhause |
| Radius (km) | 1 bis 500 | 50 |
| Höchstzahl verfolgter Schiffe | 1 bis 5.000; eine Sicherheitsgrenze für dieses Gebiet, die nächsten bleiben | 1.000 |

Dieselbe Quelle kann denselben Mittelpunkt nicht zweimal beobachten. Liegen
mindestens 5 % eines BarentsWatch-Kreises außerhalb der Gewässer, die
BarentsWatch veröffentlicht, sagt der Dialog vor dem Anlegen, wie viel;
absenden behält den Kreis trotzdem.

**Einstellungen eines Gebiets** (Konfigurieren am Eintrag): der Mittelpunkt
mit derselben Markierung, der Radius, die Höchstzahl verfolgter Schiffe und
*Höchstzahl der Schiffe auf der Karte, alle Live-Track-Ships-Einträge
zusammen*, ein Schieberegler von 100 bis 2.500 in Schritten von 100 (Standard 2.500) sowie, bei Ihrem eigenen Empfänger, sein UDP-Port. Wird der Mittelpunkt verschoben, erhält das Gebiet einen neuen Namen
nach seiner Position und wird neu geladen. Dieselbe Quelle kann einen
Mittelpunkt weiterhin nicht aus zwei Gebieten beobachten.

## Was angelegt wird

- **Eine `geo_location`-Entität pro Schiff**, `geo_location.vessel_<MMSI>`,
  deren Zustand ihr Abstand vom Mittelpunkt des Gebiets in Kilometern ist.
  Attribute sind unter anderem Name, MMSI, Rufzeichen, Geschwindigkeit, Kurs,
  Steuerkurs, Länge, Breite, Schiffstyp, Ziel, `object_kind`, `last_seen` und
  `attribution`, jeweils nur wenn die Quelle sie gesendet hat. Ein Schiff, das
  zwei Gebiete sehen, ist eine Entität.
- **Ein Sensor pro Gebiet**, `sensor.ships_in_range`, der die angezeigten
  Schiffe zählt und es sagt, wenn die Grenze des Gebiets oder der ganzen
  Installation die Liste kürzt.
- **Bei Ihrem eigenen Empfänger ein weiterer Sensor**, `sensor.ais_station`:
  Nachrichten pro Minute. Seine Attribute sind `vessels_heard` (in den letzten
  10 Minuten), `farthest_km` und `farthest_mmsi` (vom Mittelpunkt des Gebiets),
  `last_message`, `udp_port`, `listening` und `port_error`, wenn der Port nicht
  geöffnet werden kann. Er wird alle 30 Sekunden aktualisiert, sodass ein
  Empfänger, der nichts mehr sendet, 0 zeigt.

Ein Schiff, das außerhalb Ihres Kreises gehört wird, verschwindet sofort von
der Karte. Damit das gehört wird, wird jede Online-Quelle um einen Ring etwas größer
als Ihr Kreis gebeten (10 %, mindestens 1 km), und Ihr eigener Empfänger sendet alles, was er
hört; behalten werden nur Schiffe in
Ihrem Kreis. Ein Schiff, das nicht mehr gehört wird, verschwindet nach einer
Zeit der Stille, und ein Schiff, das nicht mehr erscheint, ist nicht unbedingt
weg (siehe unten).

## Ereignisse: Ein Schiff kommt in Ihr Gebiet oder verlässt es

Jedes Gebiet löst zwei Ereignisse in Home Assistant aus, damit eine
Automatisierung Ihnen sagen kann, wenn ein Schiff ankommt, auf das es Ihnen
ankommt:

- `live_track_ships_entry`, wenn ein Schiff in den Kreis des Gebiets kommt
- `live_track_ships_exit`, wenn es ihn verlässt

Die Integration meldet jedes Schiff; Ihre Automatisierung wählt die aus, die
zählen. Die Ereignisdaten tragen dieselben Namen und Einheiten wie die
Attribute des Schiffs und lassen weg, was die Quelle nicht gesendet hat:

| Feld | Inhalt |
|---|---|
| `area_id`, `area` | die ID des Konfigurationseintrags des Gebiets und sein Titel |
| `identity` | die MMSI |
| `name`, `call_sign`, `imo` | sofern gesendet |
| `object_kind` | `vessel`, `net_buoy`, `aton`, `base_station`, `sar_aircraft` oder `distress_beacon` |
| `ship_type`, `ship_type_label`, `length_m`, `beam_m`, `draught_m`, `destination`, `nav_status` | nur Schiffe, sofern gesendet |
| `speed_kmh`, `course_deg`, `heading_deg` | sofern gesendet |
| `latitude`, `longitude`, `distance_km`, `bearing_from_centre_deg`, `last_seen` | wo es gehört wurde, vom Mittelpunkt des Gebiets aus |
| `entity_id` | nur beim Eintreten: `geo_location.vessel_<MMSI>`, wenn das Schiff auf der Karte ist |
| `reason` | nur beim Verlassen: `left` (außerhalb des Kreises gehört) oder `silent` (für die Haltezeit nicht gehört, also vielleicht noch da) |

Vier Dinge, die Sie wissen sollten:

- **Eine Ankunft wird nur gemeldet, wenn das Schiff zuerst außerhalb des
  Kreises gehört wurde**, im Ring um ihn. Ein Schiff, das zuerst innerhalb
  gehört wird, kann die ganze Zeit dort gelegen haben: Nach einem Neustart
  liefern die Empfänger noch viele Minuten lang Schiffe, die sich nie bewegt
  haben. Ein Schiff, das die Empfänger auf dem Weg hinein nicht gehört haben,
  oder eines, das seinen Transponder erst im Kreis einschaltet, wird deshalb
  nicht gemeldet.
- **Ein Verlassen, das außerhalb gehört wird, wird immer gemeldet**, auch für
  ein Schiff, das schon vor dem Start von Home Assistant da war. Ein Schiff,
  das verstummt, wird nur dann als abgefahren gemeldet (`reason: silent`), wenn
  seine Ankunft gemeldet wurde.
- **Ein Verlassen wartet 2 Minuten.** Ein Schiff, das vorher am Rand des
  Kreises zurückkommt, wird nicht als ab- und wieder angekommen gemeldet.
- **Bei der Ankunft können Angaben fehlen.** Name, Typ und Größe kommen in
  einer selteneren Meldung als die Position (siehe oben). Ein zum ersten Mal
  gehörtes Schiff kann nur mit einer Position ankommen; ein schon einmal
  gehörtes trägt meist Typ und Größe.

Zwei Gebiete über demselben Wasser lösen jeweils eigene Ereignisse aus. Die
Grenzen, wie viele Schiffe die Karte zeichnet, lassen nie ein Schiff ein- oder
austreten.

Eine Automatisierung, die meldet, wenn ein Schiff über 150 m in ein Gebiet
kommt:

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
      title: "{{ trigger.event.data.name | default('Ein Schiff') }}"
      message: >-
        {{ trigger.event.data.ship_type_label | default('Schiff') }},
        {{ trigger.event.data.length_m }} m,
        {{ trigger.event.data.distance_km }} km entfernt, kommt in
        {{ trigger.event.data.area }}.
```

## Verfolgte Schiffe: ausgewählte Schiffe überall verfolgen

Neben Gebieten können Sie eine Liste von Schiffen verfolgen, wo immer sie
sind: das Boot eines Familienmitglieds, eine Fähre, die Sie nehmen, ein
Kreuzfahrtschiff auf dem Heimweg. **Einstellungen > Geräte & Dienste >
Integration hinzufügen > Live Track Ships > Ausgewählte Schiffe, wo immer sie
sind.** Nötig ist ein Schlüssel von aisstream.io (der Schlüssel eines bereits
eingerichteten Gebiets ist eingetragen), und es gibt eine solche Liste pro
Home Assistant.

Ein Schiff pro Zeile: seine 9-stellige MMSI, danach auf Wunsch eine eigene
Bezeichnung.

```text
244650000 Papas Boot
366999999 Die Fähre
```

Höchstens 100 Schiffe. aisstream verfolgt höchstens 200 MMSI pro Schlüssel,
und [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT)
nutzt, falls mit demselben Schlüssel installiert, einen Teil davon; eine Liste,
die darüber ginge, wird beim Laden des Eintrags mit Begründung abgelehnt. Die
Liste ändern Sie in den Einstellungen des Eintrags.

Ein verfolgtes Schiff wird wie jedes andere auf der Karte gezeichnet, wo
immer es gehört wird, und sein Zustand ist sein Abstand von Ihrem Zuhause. Ein
Gebiet, das es schon zeigt, behält es: ein Schiff, eine Markierung. Der Eintrag
legt `sensor.watched_vessels` an: wie viele der aufgeführten Schiffe gerade
gehört werden, und im Attribut `vessels` jedes davon mit seiner Bezeichnung und
seinem letzten bekannten Zustand.

Er löst ein Ereignis aus, `live_track_ships_watched`, dessen Feld `change`
sagt, was geschah:

| `change` | Wann |
|---|---|
| `arrived` | das Schiff meldet sich festgemacht oder vor Anker, oder bleibt ohne Status unter 2 Knoten |
| `departed` | es ist wieder in Fahrt |
| `silent` | 30 Minuten lang nicht gehört (6 Stunden, wenn festgemacht oder vor Anker); es verschwindet von der Karte und ist vielleicht noch da |
| `heard` | nach `silent` wieder gehört |
| `destination` | die Besatzung hat das Ziel geändert; `destination_previous` enthält das alte |

Die Daten tragen `watch_id`, `watch`, `identity`, Ihre Bezeichnung `label` und
dieselben Schiffsfelder wie die Gebietsereignisse, mit Abstand und Richtung von
Ihrem Zuhause aus. Ankunft und Abfahrt warten, bis der neue Zustand nach der
eigenen Uhr des Schiffs 5 Minuten gehalten hat, damit ein Boot, das mit 2 Knoten
treibt, nicht hin und her springt. Aus der ersten Position eines Schiffs nach
einem Neustart wird nichts gemeldet: Sie legt den Ausgangszustand fest. Ziele
tippt die Besatzung ein, und sie sind oft veraltet.

## Kartenkarte

Die Schiffe zeichnet [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)
(`custom:live-track-map-card`), die eine Karte, auf der jede Live-Track-
Integration zeichnet. Sie zeichnet das eigene Bild jedes Schiffs, dreht es in
seinen Steuerkurs und lässt es zwischen echten Positionen über das Wasser
gleiten statt quer über Land.

**Die Karte wird mit der Integration installiert.** Diese Integration bringt
eine veröffentlichte Kopie der Karte mit, stellt sie bereit und trägt sie beim
Start von Home Assistant als Dashboard-Ressource ein; es gibt nichts
herunterzuladen oder nach `www` zu kopieren. Jede Live-Track-Integration macht
das ebenso, und gemeinsam halten sie genau eine Ressourcenzeile: die höchste
Kartenversion, die eine von ihnen mitbringt, nie eine ältere. Eine über den
Marketplace installierte Karte bleibt unberührt. Wird das letzte Gebiet dieser
Integration entfernt, geht die Zeile an eine andere Live-Track-Integration
über, oder sie wird entfernt, wenn keine mehr da ist. Siehe die README der
Karte, Abschnitt
[Live Track](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).

Sind die Ressourcen Ihrer Dashboards in YAML festgelegt
(`lovelace: resource_mode: yaml`), kann nichts für Sie eingetragen werden.
Eine Reparaturmeldung nennt dann die genaue Zeile; sie sieht so aus, mit der
Adresse der Integration an Stelle der Platzhalter:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_ships/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Werden die Dateien der Integration entfernt (etwa über den Marketplace),
während ihre Gebiete noch eingerichtet sind, und ist keine andere Live-Track-
Integration installiert, räumt niemand die Zeile auf: Entfernen Sie sie unter
Einstellungen > Dashboards > Ressourcen. Um die Karte stattdessen von Hand zu
installieren, folgen Sie der README der Karte; die Ressourcenzeile einer von
Hand installierten Kopie unter `/local/` wird nur dann auf die Kopie einer
Integration umgestellt, wenn diese eine neuere Version ist.

Geben Sie ihr die Schiffe mit
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities),
gefiltert auf `domain: geo_location` und
`attributes: {source: live_track_ships}`. Sind andere Live-Track-Integrationen
installiert, fügen Sie für jede ihrer Quellen einen Filter hinzu.

Jede andere Kartenkarte, die `geo_location`-Entitäten zeigt, zeigt die Schiffe
ebenfalls, ohne die Bilder und das Gleiten dieser Karte.

Ein Schiff auf der öffentlichen Liste
[EnforcementVessels](https://github.com/StrausbergAutomationWorks/EnforcementVessels)
(Küstenwachschiffe, die bei Einwanderungseinsätzen eingesetzt werden) wird in
den Farben der Küstenwache mit dem Namen und der Behörde aus der Liste
gezeichnet, wo immer es ist.

### Schiffstypen ausblenden

Jedes Schiff trägt `marker_group`, `marker_group_label` und `marker_group_order`:
eine von dreizehn Gruppen (Fracht; Tanker; Passagiere und Fähren; Fischerei;
Freizeit und Segeln; Schlepper, Lotsen und Hafendienst; Behörden, SAR und
Polizei; Schnellboote und Sonstige; Typ nicht gesendet; Fanggeräte-Bojen;
Navigationshilfen; Basisstationen; SAR-Flugzeuge). Die Filterkarte der
Kartenkarte, `custom:live-track-map-filter-card`, listet sie mit der Anzahl auf
der Karte auf und blendet die aus, deren Haken Sie entfernen; legen Sie sie auf
eine beliebige Ansicht des Dashboards. Ihre Wahl wird nur in diesem Browser
gespeichert. Die Integration zeigt weiterhin alles: Ihr Sensor zählt jedes
Schiff, und ihre Ereignisse werden für jedes Schiff ausgelöst. Ein Notsender hat
keine Gruppe und wird daher nie ausgeblendet.

### Fotos und Links

Wenn ein Schiff eine IMO-Nummer sendet und Wikidata ein Foto dieses Schiffs auf
Wikimedia Commons kennt, trägt das Schiff `marker_photo`. Die Karte zeigt das
Foto im Hover-Feld mit Fotograf und Lizenz; ein Klick öffnet es größer, mit
Links zur Seite des Fotos und zu seiner Lizenz. Jedes Schiff mit IMO-Nummer
oder MMSI trägt außerdem `marker_links`, einen Link zum Schiff auf
VesselFinder. Die Schaltfläche **Details** im Popup öffnet den gewohnten Dialog
des Schiffs. Ihr Home Assistant fragt Wikidata und Commons selbst ab, 20
IMO-Nummern auf einmal im Abstand von zehn Sekunden, und hält jede Antwort 30
Tage (14, wenn es kein Foto gibt) in `.storage/saw_vessel_photos.json`. Rechnen
Sie mit Fotos für etwa jedes zehnte Schiff: Auf unserem Testsystem hatten 49
von 521 IMO-Nummern eines.

## Wo gesucht wird

Sie setzen einen **Mittelpunkt und einen Radius** auf die Karte. Der
Mittelpunkt kann überall auf der Welt liegen; der Radius kann 1 bis 500 km
betragen. Standard sind **50 km**. Der Zustand jedes Schiffs ist sein Abstand
von Ihrem Mittelpunkt.

Wie viele Schiffe ein Kreis enthält, hängt viel mehr davon ab, *welches
Gewässer* es ist, als davon, *wie groß*. Im Test enthielt ein Kreis von 50 km
über Chicago etwa 4 Schiffe und über dem Solent in Südengland etwa 340:
derselbe Radius, ungefähr 80-mal so viel Verkehr. Deshalb behält die
Integration höchstens eine festgelegte Zahl von Schiffen (standardmäßig 1.000,
einstellbar bis 5.000), behält bei mehr die nächsten und sagt das an ihrem
Sensor `ships_in_range`.

Alle Ihre Gebiete **zusammen** zeigen höchstens 2.500 Schiffe, gleich welcher
Quelle. Die Einstellungen jedes Gebiets haben den Schieberegler von oben, der
diese Grenze nur senken kann; es gilt die niedrigste Einstellung eines
aktivierten Gebiets. Auf langsamerer Hardware senken.

## Abdeckung, gemessen statt versprochen

Die Abdeckung ist gut, wo Empfänger stehen, und fehlt, wo keine stehen, und
**keine Einstellung schafft Abdeckung, die es nicht gibt**.

Gemessen am 2026-09-02 rund um Chicago mit aisstream.io:

- **Große Seen**: 100 verschiedene Schiffe in 120 Sekunden, alle fünf Seen
  und die Verbindungsgewässer.
- **Chicago River, Innenstadt**: belebt und zuverlässig.
- **Chicago Sanitary and Ship Canal, Cal-Sag Channel, Calumet River**: eine
  Stunde Zuhören, **null Schiffe**. Der Kanal ist nicht leer: Seine Schubverbände
  sind bei kommerziellen Diensten über Satelliten-AIS zu sehen, das freie
  Sammeldienste nicht führen. Der Verkehr ist echt; die Abdeckung vom Land aus
  nicht.

Keine Schiffe in Ihrem Gebiet können fehlende Empfänger bedeuten statt
fehlender Boote. Prüfen Sie, ob Ihre Quelle Ihr Gewässer abdeckt, bevor Sie
die Integration für defekt halten.

Ein Schiff, das nicht mehr erscheint, ist nicht unbedingt weg. Keine dieser
Quellen garantiert die Zustellung, deshalb zeigt die Integration, wann jedes
Schiff zuletzt gehört wurde, und entfernt es erst nach einer Zeit der Stille.

## Schiffe, die ein eigenes Bild verdienen

Die meisten Schiffe werden nach ihrem Typ gezeichnet. Manche haben ein eigenes
Bild: königliche und staatliche Jachten sowie bekannte Boote wie die
Ausflugsschiffe, Wassertaxis und Feuerlöschboote von Chicago. Sie kennen ein
Schiff, das eines verdient, irgendwo auf der Welt? Eröffnen Sie ein Issue unter
<https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues> mit Name
und MMSI- oder IMO-Nummer, gern mit Foto oder Link.

## Sprachen

Diese README: [English](README.md), **Deutsch**, [Français](README.fr.md),
[Nederlands](README.nl.md), [简体中文](README.zh-Hans.md),
[Español](README.es.md), [Italiano](README.it.md), [Dansk](README.da.md) und
[Kalaallisut](README.kl.md) (ein Entwurf, an Oqaasileriffik, das
Sprachsekretariat Grönlands, zur Durchsicht geschickt; bis dahin ist die
dänische Seite die verlässliche). Die README gibt es in einer kurzen Liste von
Sprachen: denen, die die meisten Nutzer von Home Assistant lesen, und einigen
weiteren, wo es einen guten Grund gibt. Jede übersetzte README ist
vollständig: Alles aus der englischen steht in jeder von ihnen, und keine
schickt Sie für die Einzelheiten ins Englische.

Der Einrichtungsdialog und die Einstellungen eines Gebiets erscheinen in der
Sprache Ihres Home Assistant, wenn es eine dieser ist: English, Dansk,
Deutsch, Español, Français, Gaeilge, Íslenska, Italiano, Nederlands, Norsk
Bokmål, Polski, Português, Português (BR), Suomi, Svenska und 简体中文. Jede
andere Sprache zeigt den englischen Dialog. Kalaallisut ist noch keine Sprache
von Home Assistant; wir haben Home Assistant gebeten, sie aufzunehmen, und der
Dialog folgt, sobald er angezeigt werden kann.

Einen Fehler in einer Übersetzung gefunden, der den Sinn verändert oder sich
schlecht liest? Bitte melden Sie ihn unter
<https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues>. Die
Übersetzungen wurden für dieses Projekt geschrieben, und noch nicht alle hat
ein Muttersprachler gelesen.

**Fällt es Ihnen schwer, dem in einer dieser Sprachen zu folgen?** Bitten Sie
unter derselben Adresse um eine andere, und wir versuchen, Ihnen
entgegenzukommen.

## Teil von Live Track

Live Track ist eine Reihe von Home-Assistant-Integrationen, eine für jede Art
von Dingen, die sich bewegen, und alle zeichnen auf dieselbe Karte. Sie teilen
eine Python-Bibliothek
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore))
und die Kartenkarte, sodass eine weitere Integration keine zusätzlichen
Anfragen an eine gemeinsame Quelle stellt. Veröffentlicht:
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft),
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
[Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail),
[Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail)
und Live Track Ships. Jede funktioniert auch allein.

## Keine Verbindung

Nicht verbunden mit aisstream.io, Fintraffic, BarentsWatch, MarineTraffic,
VesselFinder, einem Schiffsbetreiber oder einer Schifffahrtsbehörde. AIS ist
ein System für die Sicherheit der Schifffahrt; **diese Integration dient dem
Interesse und ist nicht für die Navigation, die Kollisionsvermeidung oder
irgendeinen betrieblichen Zweck gedacht.**

## Lizenz

Code: MIT, in [LICENSE](LICENSE). Daten- und Bildnachweise:
[ATTRIBUTION.md](ATTRIBUTION.md).

## Stichwörter

Home Assistant AIS · Schiffsverfolgung · Schiffe auf der Karte · Boote
verfolgen · Schiffsverkehr live · AIS-Kartenkarte · aisstream.io ·
Digitraffic · BarentsWatch · geo_location · HACS-Integration
