# Live Track Ships

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · **Italiano** · [Dansk](README.da.md) · [Kalaallisut](README.kl.md) · [Tutte le lingue](#lingue)

**Tracciamento AIS di navi, barche e imbarcazioni per Home Assistant.** Le
navi vicino a te, o in qualsiasi punto del mondo tu scelga, come segnaposto
in diretta sulla tua mappa. Parte di Live Track: navi, aerei e treni su
un'unica mappa.

Dati AIS marittimi in diretta da [aisstream.io](https://aisstream.io),
[Fintraffic Digitraffic](https://www.digitraffic.fi/en/marine-traffic/) o
[BarentsWatch](https://www.barentswatch.no/en/), mostrati come entità
`geo_location` di Home Assistant e disegnati sulla mappa condivisa di Live
Track.

**Stato: 0.1.0, la prima versione.** Si aggiunge al Marketplace tramite link
(sotto); non è ancora nel catalogo del Marketplace.

## Che cos'è l'AIS

L'AIS (Automatic Identification System, sistema di identificazione
automatica) è una trasmissione VHF con cui le navi comunicano posizione,
identità e viaggio alle altre navi e a terra. È l'equivalente marittimo
dell'ADS-B. Le navi commerciali sono obbligate ad averlo; molte imbarcazioni
da diporto lo hanno per scelta, di solito come apparato di classe B, meno
potente.

L'AIS viene trasmesso in chiaro. Chiunque abbia un ricevitore può sentirlo, e
aggregatori pubblici lo ripubblicano.

## Che cosa si vede

**Tutto ciò che la fonte invia.** Non viene filtrato nulla, e non c'è
un'impostazione per nascondere una categoria.

| Nei dati | Mostrato |
|---|---|
| Navi da carico, petroliere, rimorchiatori, traghetti, navi passeggeri | sì |
| Pescherecci, pilotine, mezzi delle autorità e altre imbarcazioni da lavoro | sì |
| **Imbarcazioni da diporto private e barche a vela** | **sì, con nome e posizione** |
| **Boe di attrezzi da pesca** che trasmettono AIS | **sì, disegnate come un pesce** |
| Aerei di ricerca e soccorso (SAR) | quando la fonte li invia |
| Aiuti alla navigazione: boe, mede, fari | quando la fonte li invia |
| Stazioni base AIS a terra | quando la fonte li invia |

### Si vedono le barche private, ed è bene che tu sappia che cosa significa

Un'imbarcazione da diporto che trasmette AIS compare sulla mappa esattamente
come una nave da carico. A seconda di ciò che trasmette, la sua entità può
contenere:

- il suo **nome**, che è anche l'etichetta sulla mappa
- il suo **MMSI** e il suo **nominativo radio**, entrambi permanenti e
  cercabili da chiunque
- la sua **posizione** con una precisione di circa un metro, la posizione
  precedente e quando ciascuna è stata sentita
- velocità, rotta e prua, se trasmesse
- lunghezza, larghezza e tipo, se trasmessi

Una barca che lascia il transponder acceso all'ormeggio resta sulla mappa al
suo posto finché continua a trasmettere.

Chi può aprire la tua mappa può anche premere **Track** su una barca così e
vedere dove è stata nelle ultime 24 ore (o per il tempo che imposti), non solo
dove si trova: una barca che ha lasciato l'ormeggio stamattina mostra
quell'ormeggio tutto il giorno.

Per l'AIS non esiste un elenco di esclusione come per gli aerei, e questa
integrazione non ne inventa uno. Se vuoi meno barche private sulla mappa,
riduci il raggio.

### Il tipo di nave manca spesso, soprattutto per le barche piccole

Posizione e nome arrivano con quasi ogni messaggio. Tipo e dimensioni
arrivano in un messaggio a parte, più raro, e molti apparati delle barche
piccole (classe B) inviano di rado la parte che li contiene. Aspettati che una
buona parte delle navi, tra cui la maggior parte delle piccole, compaia senza
tipo né dimensioni, e che tutte siano incomplete per qualche minuto dopo il
riavvio di Home Assistant. Sono i dati, non un guasto. Tipi e dimensioni già
sentiti si conservano tra un riavvio e l'altro.

### Non tutto ciò che trasmette AIS è una nave

Ogni entità porta `object_kind`: `vessel`, `net_buoy`, `aton` (aiuto alla
navigazione), `base_station`, `sar_aircraft` o `distress_beacon`. La maggior
parte si riconosce dal formato dell'identificativo che l'ITU assegna loro. Le
boe degli attrezzi da pesca no: trasmettono con identificativi da nave, e
quindi si riconoscono dai nomi di fabbrica (FISHING BOUY, NET MARK, BUOY)
insieme all'assenza di una lunghezza trasmessa.

Tutto ciò che non è una nave compare senza tipo, dimensioni né stato di
navigazione. Le boe degli attrezzi da pesca derivano con le loro lenze; per
questo conservano velocità e rotta e sono disegnate come un salmone rivolto
nella direzione in cui derivano.

Che cosa compare dipende dalla fonte. Misurato in una serata:

| Fonte | Boe di attrezzi da pesca | Aerei SAR | Aiuti alla navigazione, stazioni base |
|---|---|---|---|
| BarentsWatch | sì | sì | nessuno visto |
| Digitraffic | nessuna vista | sì | nessuno visto |
| aisstream.io | nessuna vista | nessuno visto | nessuno visto |
| Il tuo ricevitore | ciò che sente | ciò che sente | ciò che sente |

aisstream.io ha consegnato solo messaggi di posizione e di dati della nave,
sia sui Grandi Laghi sia sulle stesse acque norvegesi e danesi dove
BarentsWatch mostra le boe.

## Fonti

Scegli una fonte per ogni area che configuri.

| Fonte | Copertura | Serve |
|---|---|---|
| aisstream.io | tutto il mondo, dove ci sono volontari con ricevitori | una chiave API gratuita |
| Fintraffic Digitraffic | acque finlandesi e baltiche | niente |
| BarentsWatch AIS Live | acque norvegesi | un ID client e un segreto gratuiti |
| Il tuo ricevitore AIS | fin dove sente la tua antenna | un ricevitore che invia NMEA via UDP |

Quali categorie compaiono, quanto sono aggiornate le posizioni e quanto sono
completi i dati delle navi dipende dalla fonte che scegli.

### Il tuo ricevitore

Se hai un ricevitore AIS, Live Track Ships può mostrare ciò che sente, senza
account e senza Internet. Il ricevitore, o il programma che lo decodifica,
invia frasi NMEA (`!AIVDM`) via UDP all'indirizzo di Home Assistant, su una
porta che scegli tu (10110 se non la cambi). In AIS-catcher è
`-u <address> <port>`; in rtl-ais, `-h <address> -P <port>`; OpenCPN e
Signal K lo aggiungono come connessione di uscita UDP. Un ricevitore che si
collega via USB, come un dAISy, ha bisogno di uno di questi programmi per
passare le sue frasi.

- Un'area ascolta su una porta; due ricevitori richiedono due porte.
- Tutto ciò che il ricevitore sente dentro il tuo cerchio viene mostrato,
  compresi aiuti alla navigazione e stazioni base. Il sensore della stazione
  (sotto) conta anche ciò che sente fuori dal cerchio.
- Una frase non porta la data, quindi l'ora di una posizione è quella in cui
  Home Assistant l'ha ricevuta.
- La velocità di accostata non viene mostrata per questa fonte.
- Per ora è provato con frasi registrate inviate via UDP, non con un
  ricevitore. Se lo provi con il tuo, raccontaci com'è andata sulla
  [pagina delle issue](https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues).

### Attribuzione

Ogni entità nave, e il sensore `ships_in_range` di ogni area, porta un
attributo `attribution` con la fonte che l'ha fornita; Home Assistant lo
mostra nei dettagli dell'entità. Due delle fonti concedono i loro dati con una
licenza che chiede di essere citate, e Live Track Ships modifica ciò che
riceve (unità convertite, solo le navi dentro il tuo cerchio), quindi le loro
righe lo dicono. Se mostri questi dati ad altri, per esempio su una dashboard
pubblica, mantieni la citazione e leggi le condizioni della fonte:

- **aisstream.io**: nessuna condizione pubblicata. <https://aisstream.io>
- **Fintraffic Digitraffic**: CC BY 4.0.
  <https://www.digitraffic.fi/en/terms-of-service/>
- **BarentsWatch**: licenza norvegese per i dati pubblici aperti (NLOD).
  <https://www.barentswatch.no/en/articles/api-terms-and-conditions/>
- **Il tuo ricevitore**: dati tuoi; la sua riga lo dice.
- **EnforcementVessels** (l'elenco dietro l'aspetto da guardia costiera,
  sotto): ODbL v1.0.
  <https://github.com/StrausbergAutomationWorks/EnforcementVessels>

Le righe esatte sono in [ATTRIBUTION.md](ATTRIBUTION.md).

## Requisiti

- Home Assistant 2026.11 o successivo, con accesso a Internet per le fonti
  online.
- Per aisstream.io: una chiave API gratuita da
  [aisstream.io](https://aisstream.io/account). aisstream consente **tre
  connessioni per account e tre per IP pubblico**; se usi altri strumenti con
  la stessa chiave, tienine conto. Live Track SALT, se installato, usa una
  seconda connessione con la stessa chiave.
- Per BarentsWatch: un ID client e un segreto gratuiti, da registrare da te su
  BarentsWatch. Inserisci l'ID client esattamente come ti è stato rilasciato.
- Per il tuo ricevitore: un ricevitore e un programma che inviino NMEA via UDP
  a Home Assistant, sulla stessa rete. Non serve Internet.
- Home Assistant installa i pacchetti Python necessari (`saw-livetrack` e
  `pyais`) la prima volta che carica l'integrazione.

## Installazione

### Dal Marketplace

Live Track Ships non è ancora nel catalogo del Marketplace. Aggiungila
tramite link:

1. **Impostazioni > Marketplace**, poi **Aggiungi da link**.
2. Inserisci `StrausbergAutomationWorks/LiveTrackShips`. Se chiede il tipo,
   scegli **Integrazione**.
3. Installa **Live Track Ships**.
4. Riavvia Home Assistant. Il Marketplace propone il riavvio come
   riparazione in **Impostazioni > Sistema > Riparazioni**.

### A mano

1. Scarica il codice sorgente dell'[ultima versione](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest).
2. Copia la sua cartella `custom_components/live_track_ships` nella cartella
   `custom_components` della directory di configurazione di Home Assistant.
3. Riavvia Home Assistant.

## Configurazione

**Impostazioni > Dispositivi e servizi > Aggiungi integrazione > Live Track
Ships**, poi **Tutte le navi di un'area** (l'altra scelta, le navi seguite, è
[più sotto](#navi-seguite-segui-navi-scelte-ovunque)). Ogni area è una voce a
sé, intitolata *Ships near <latitudine>, <longitudine>*. La finestra appare in
italiano quando Home Assistant è in italiano.

| Campo | Che cosa accetta | Predefinito |
|---|---|---|
| Fonte dei dati | aisstream.io, Fintraffic Digitraffic, BarentsWatch AIS Live o il tuo ricevitore AIS | aisstream.io |
| Chiave API | solo aisstream.io. Presa da un'area già configurata; si può cambiare | vuota |
| ID client, segreto client | solo BarentsWatch. Presi da un'area già configurata | vuoti |
| Porta UDP | solo il tuo ricevitore: la porta a cui invia NMEA, da 1024 a 65535. Rifiutata se un'altra area o un altro programma la usa già | 10110 |
| Centro | un segnaposto su una mappa; trascinalo sull'acqua da osservare | casa tua |
| Raggio (km) | da 1 a 500 | 50 |
| Numero massimo di navi seguite | da 1 a 5.000; un limite di sicurezza per quest'area, restano le più vicine | 1.000 |

La stessa fonte non può osservare due volte lo stesso centro. Quando almeno
il 5 % di un cerchio BarentsWatch cade fuori dalle acque che BarentsWatch
pubblica, la finestra dice quanto prima di creare l'area; invia per tenere
comunque quel cerchio.

**Impostazioni di un'area** (Configura sulla sua voce): il centro, con lo
stesso segnaposto; il raggio; il numero massimo di navi seguite; e *Numero
massimo di navi sulla mappa, tutte le voci Live Track Ships insieme*, un
cursore da 100 a 2.500 a passi di 100 (2.500 predefinito); e, per il tuo ricevitore, la sua porta UDP. Spostare il centro
rinomina l'area secondo la nuova posizione e la ricarica. La stessa fonte
continua a non poter osservare un centro da due aree.

## Che cosa crea

- **Un'entità `geo_location` per nave**, `geo_location.vessel_<MMSI>`, il cui
  stato è la distanza dal centro dell'area in chilometri. Gli attributi
  comprendono nome, MMSI, nominativo, velocità, rotta, prua, lunghezza,
  larghezza, tipo, destinazione, `object_kind`, `last_seen` e `attribution`,
  ciascuno solo se la fonte l'ha inviato. Una nave vista da due aree è una
  sola entità.
- **Un sensore per area**, `sensor.ships_in_range`, che conta le navi
  mostrate e lo dice quando il limite dell'area o dell'intera installazione
  accorcia l'elenco.
- **Per il tuo ricevitore, un sensore in più**, `sensor.ais_station`:
  messaggi al minuto. I suoi attributi sono `vessels_heard` (negli ultimi 10
  minuti), `farthest_km` e `farthest_mmsi` (dal centro dell'area),
  `last_message`, `udp_port`, `listening`, e `port_error` quando la porta non
  si può aprire. Si aggiorna ogni 30 secondi, così un ricevitore che smette di
  inviare mostra 0.

Una nave sentita fuori dal tuo cerchio lascia subito la mappa. Per sentirla, a ogni fonte online si chiede un anello un po' più grande del tuo cerchio (il 10 %,
almeno 1 km), e il tuo ricevitore invia tutto ciò che sente; si tengono solo le navi dentro il tuo cerchio. Una nave che non
si sente più lascia la mappa dopo un periodo di silenzio, e una nave che
smette di comparire non è detto che se ne sia andata (sotto).

### Il tuo database

Il recorder di Home Assistant salva una nuova riga ogni volta che un'entità
cambia, e una nave in movimento cambia a ogni posizione che trasmette. Questa
integrazione può quindi far crescere rapidamente il tuo database: sul nostro
sistema di prova, un'area con 43 navi ha scritto 27.109 righe di stato in circa
30 ore, l'8,8% dell'intero database. Per impostazione predefinita il recorder
conserva 10 giorni ed esegue la pulizia ogni notte alle 04:12, quindi la
crescita si stabilizza, ma a una dimensione che potresti non volere.
`marker_photo`, `marker_links` e `marker_track` di ogni nave, e gli attributi dei sensori che
cambiano spesso, non vengono mai registrati.

Una nave mantiene lo stesso ID entità, `geo_location.vessel_<MMSI>`, ogni volta
che compare: un traghetto che parte e torna riutilizza la sua entità invece di
aggiungerne un'altra. Un solo schema, `geo_location.vessel_*`, copre quindi
tutto ciò che questa integrazione ha mai messo sulla mappa. Per conservarne
solo l'ultimo giorno, esegui `recorder.purge_entities` a orari stabiliti, per
esempio con questa automazione:

```yaml
alias: Accorcia la cronologia delle navi
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

Se ometti `keep_days` (predefinito 0), tutte le loro righe vengono eliminate in
una volta. Per non registrarne nulla, metti lo schema sotto `recorder:` →
`exclude:` → `entity_globs:` in `configuration.yaml`. Una scheda mappa
impostata per disegnare la cronologia (`history_start`) non avrà allora alcuna
traccia da disegnare. `sensor.ships_in_range` è un semplice numero, economico
da conservare, quindi la sua cronologia resta in entrambi i casi.

## Eventi: una nave entra nella tua area o ne esce

Ogni area genera due eventi di Home Assistant, perché un'automazione possa
avvisarti quando arriva una nave che ti interessa:

- `live_track_ships_entry` quando una nave entra nel cerchio dell'area
- `live_track_ships_exit` quando ne esce

L'integrazione segnala ogni nave; la tua automazione sceglie quelle che
contano. I dati dell'evento hanno gli stessi nomi e le stesse unità degli
attributi della nave, e omettono ciò che la fonte non ha inviato:

| Campo | Contenuto |
|---|---|
| `area_id`, `area` | l'ID della voce di configurazione dell'area e il suo titolo |
| `identity` | l'MMSI |
| `name`, `call_sign`, `imo` | se trasmessi |
| `object_kind` | `vessel`, `net_buoy`, `aton`, `base_station`, `sar_aircraft` o `distress_beacon` |
| `ship_type`, `ship_type_label`, `length_m`, `beam_m`, `draught_m`, `destination`, `nav_status` | solo navi, se trasmessi |
| `speed_kmh`, `course_deg`, `heading_deg` | se trasmessi |
| `latitude`, `longitude`, `distance_km`, `bearing_from_centre_deg`, `last_seen` | dove è stata sentita, dal centro dell'area |
| `entity_id` | solo all'ingresso: `geo_location.vessel_<MMSI>`, quando la nave è sulla mappa |
| `reason` | solo all'uscita: `left` (sentita fuori dal cerchio) o `silent` (non sentita per il tempo di conservazione, quindi forse ancora lì) |

Quattro cose da sapere:

- **Un arrivo viene segnalato solo se la nave è stata sentita prima fuori dal
  cerchio**, nell'anello che lo circonda. Una nave sentita per la prima volta
  dentro potrebbe essere stata lì da sempre: dopo un riavvio i ricevitori
  continuano per molti minuti a consegnare navi che non si sono mai mosse. Una
  nave che i ricevitori non hanno sentito entrare, o che accende il
  transponder quando è già dentro, quindi non viene segnalata.
- **Un'uscita sentita fuori viene sempre segnalata**, anche per una nave che
  c'era già prima dell'avvio di Home Assistant. Una nave che tace viene
  segnalata come uscita (`reason: silent`) solo se il suo arrivo era stato
  segnalato.
- **Un'uscita aspetta 2 minuti.** Una nave che rientra prima, lungo il bordo
  del cerchio, non viene segnalata come uscita e rientrata.
- **All'arrivo possono mancare dati.** Nome, tipo e dimensioni viaggiano in un
  messaggio più raro della posizione (sopra). Una nave sentita per la prima
  volta può arrivare con una posizione e nient'altro; una già sentita di solito
  porta tipo e dimensioni.

Due aree sulle stesse acque generano ciascuna i propri eventi. I limiti a
quante navi disegna la mappa non fanno mai entrare né uscire una nave.

Un'automazione che ti avvisa quando una nave di oltre 150 m entra in un'area:

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
      title: "{{ trigger.event.data.name | default('Una nave') }}"
      message: >-
        {{ trigger.event.data.ship_type_label | default('Nave') }},
        {{ trigger.event.data.length_m }} m,
        a {{ trigger.event.data.distance_km }} km, entra in
        {{ trigger.event.data.area }}.
```

## Navi seguite: segui navi scelte ovunque

Oltre alle aree puoi seguire un elenco di navi ovunque si trovino: la barca di
un familiare, un traghetto che prendi, una nave da crociera che torna a casa.
**Impostazioni > Dispositivi e servizi > Aggiungi integrazione > Live Track
Ships > Navi scelte, ovunque si trovino.** Serve una chiave di aisstream.io
(quella di un'area già configurata è compilata), e c'è un solo elenco di
questo tipo per Home Assistant.

Una nave per riga: il suo MMSI di 9 cifre e, se vuoi, un'etichetta tua.

```text
244650000 Barca di papà
366999999 Il traghetto
```

Al massimo 100 navi. aisstream segue al massimo 200 MMSI per chiave, e
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
se installato con la stessa chiave, ne usa una parte; un elenco che andrebbe
oltre viene rifiutato al caricamento della voce, con il motivo. Modifica
l'elenco nelle impostazioni della voce.

Una nave seguita viene disegnata sulla mappa come le altre, ovunque venga
sentita, e il suo stato è la distanza da casa tua. Un'area che la mostra già
se la tiene: una nave, un segnaposto. La voce crea `sensor.watched_vessels`:
quante delle navi dell'elenco si sentono adesso, con ciascuna di esse, la sua
etichetta e il suo ultimo stato noto nell'attributo `vessels`.

Genera un solo evento, `live_track_ships_watched`, il cui campo `change` dice
che cosa è successo:

| `change` | Quando |
|---|---|
| `arrived` | la nave si dichiara ormeggiata o alla fonda, o, senza stato, resta sotto i 2 nodi |
| `departed` | è di nuovo in navigazione |
| `silent` | non sentita per 30 minuti (6 ore se ormeggiata o alla fonda); lascia la mappa, e forse è ancora lì |
| `heard` | sentita di nuovo dopo `silent` |
| `destination` | l'equipaggio ha cambiato la destinazione; `destination_previous` contiene quella precedente |

I dati portano `watch_id`, `watch`, `identity`, la tua etichetta `label` e gli
stessi campi nave degli eventi di area, con distanza e rilevamento da casa
tua. Arrivo e partenza attendono che il nuovo stato duri 5 minuti secondo
l'orologio della nave stessa, perché una barca che deriva a 2 nodi non vada
avanti e indietro. Dalla prima posizione di una nave dopo un riavvio non si
segnala nulla: quella fissa il punto di partenza. Le destinazioni le digita
l'equipaggio e spesso sono vecchie.

## Scheda mappa

Le navi le disegna [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)
(`custom:live-track-map-card`), l'unica mappa su cui disegna ogni integrazione
Live Track. Disegna l'immagine propria di ogni nave, la ruota secondo la sua
prua e la fa scivolare tra posizioni reali lungo l'acqua invece che in linea
retta sopra la terra.

**La scheda si installa con l'integrazione.** Questa integrazione porta con sé
una copia pubblicata della scheda, la serve e la registra come risorsa della
dashboard all'avvio di Home Assistant; non c'è niente da scaricare né da
copiare in `www`. Ogni integrazione Live Track fa lo stesso, e insieme tengono
esattamente una riga di risorsa: la versione più alta della scheda che una di
esse porta, mai una più vecchia. Una scheda installata dal Marketplace non
viene toccata. Togliere l'ultima area di questa integrazione passa la riga a
un'altra integrazione Live Track, o la toglie se non ne resta nessuna. Vedi il
README della scheda, sezione
[Live Track](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).

Se le risorse delle tue dashboard sono definite in YAML
(`lovelace: resource_mode: yaml`), non si può registrare nulla per te. Una
riparazione ti dà allora la riga esatta da aggiungere; è così, con l'indirizzo
dell'integrazione al posto dei segnaposto:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_ships/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Se i file dell'integrazione vengono rimossi (dal Marketplace, per esempio)
mentre le sue aree sono ancora configurate, e non c'è un'altra integrazione
Live Track installata, nessuno sistema la riga: toglila in Impostazioni >
Dashboard > Risorse. Per installare la scheda a mano, segui il README della
scheda; la riga di risorsa di una copia installata a mano in `/local/` viene
puntata sulla copia di un'integrazione solo quando quella è una versione più
recente.

Dalle le navi con
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities),
filtrando su `domain: geo_location` e `attributes: {source: live_track_ships}`.
Con altre integrazioni Live Track installate, aggiungi un filtro per ciascuna
delle loro fonti.

Qualsiasi altra scheda mappa che mostra entità `geo_location` mostra anche le
navi, senza le immagini e lo scorrimento di questa scheda.

Una nave dell'elenco pubblico
[EnforcementVessels](https://github.com/StrausbergAutomationWorks/EnforcementVessels)
(navi della guardia costiera impiegate nel lavoro sull'immigrazione) viene
disegnata con i colori della guardia costiera, con il nome e l'agenzia
dell'elenco, ovunque si trovi.

### Nascondere tipi di nave

Ogni nave porta `marker_group`, `marker_group_label` e `marker_group_order`:
uno di tredici gruppi (carico; cisterna; passeggeri e traghetti; pesca;
diporto e vela; rimorchiatori, piloti e servizio portuale; Stato, SAR e
polizia; alta velocità e altro; tipo non inviato; boe di attrezzi da pesca;
aiuti alla navigazione; stazioni base; aeromobili SAR). La scheda filtro della
mappa, `custom:live-track-map-filter-card`, li elenca con quanti ce ne sono
sulla mappa e nasconde quelli che deselezioni; mettila in qualsiasi vista della
dashboard. La tua scelta resta solo in quel browser. L'integrazione continua a
mostrare tutto: il suo sensore conta ogni nave e i suoi eventi scattano per
ogni nave. Un radiofaro di soccorso non ha gruppo, quindi non viene mai
nascosto.

### Foto e link

Quando una nave trasmette un numero IMO e Wikidata conosce una foto di quella
nave su Wikimedia Commons, la nave porta `marker_photo`. La mappa mostra la foto
nel riquadro al passaggio del mouse con il fotografo e la licenza; un clic la
apre più grande, con link alla pagina della foto e alla sua licenza. Ogni nave
con un numero IMO o un MMSI porta anche `marker_links`, un link alla nave su
VesselFinder. Il pulsante **Details** della finestra apre la solita finestra di
dialogo della nave. Il tuo Home Assistant interroga da sé Wikidata e Commons,
20 numeri IMO alla volta, a dieci secondi di distanza, e conserva ogni risposta
per 30 giorni (14 se non c'è foto) in `.storage/saw_vessel_photos.json`. Conta
su una foto per circa una nave su dieci: sul nostro sistema di prova, 49
numeri IMO su 521 ne avevano una.

### Tracce

Ogni nave porta anche `marker_track`. Fai clic su una nave e premi **Track**
nella sua finestra: la mappa disegna dove è passata, come una linea che finisce
alla nave e si allunga mentre guardi; **Hide track** la toglie. Non viene
disegnato nulla finché non lo chiedi, così un porto trafficato non sparisce mai
sotto le linee. La traccia contiene solo posizioni che la nave ha trasmesso
mentre era sulla tua mappa, ridotte a una ogni 25 m o ogni 10 minuti e mai due
entro 30 secondi. Il tuo Home Assistant la tiene in memoria e la salva in
`.storage/saw_vessel_tracks.json`, quindi sopravvive a un riavvio. Copre le
ultime 24 ore. Per conservarne di più o di meno, esegui l'azione
`live_track_ships.set_track_hours` con `hours` da 1 a 168 (una settimana), per
esempio da Strumenti per sviluppatori > Azioni:

```yaml
action: live_track_ships.set_track_hours
data:
  hours: 72
```

Vale per tutte le aree insieme; un valore più breve elimina subito le posizioni
più vecchie. Il recorder di Home Assistant non registra le tracce.

## Dove guarda

Metti un **centro e un raggio** sulla mappa. Il centro può essere in qualsiasi
punto del mondo; il raggio può andare da 1 a 500 km. Il predefinito è
**50 km**. Lo stato di ogni nave è la sua distanza dal tuo centro.

Quante navi ci sono in un cerchio dipende molto più da *quale acqua* che da
*quanto grande*. Nelle prove, un cerchio di 50 km conteneva circa 4 navi su
Chicago e circa 340 sul Solent, nel sud dell'Inghilterra: lo stesso raggio,
circa 80 volte il traffico. Per questo l'integrazione tiene al massimo un
numero fissato di navi (1.000 per impostazione predefinita, regolabile fino a
5.000), tiene le più vicine quando sono di più e lo dice sul suo sensore
`ships_in_range`.

Tutte le tue aree **insieme** mostrano al massimo 2.500 navi, qualunque sia la
loro fonte. Le impostazioni di ogni area hanno il cursore di sopra, che può
solo abbassare quel limite; vale l'impostazione più bassa tra le aree
attivate. Abbassalo su un hardware più lento.

## Copertura, misurata e non promessa

La copertura è buona dove ci sono ricevitori e assente dove non ci sono, e
**nessuna impostazione può creare una copertura che non esiste**.

Misurato il 2026-09-02 intorno a Chicago, con aisstream.io:

- **Grandi Laghi**: 100 navi diverse in 120 secondi, tutti e cinque i laghi e
  le acque che li collegano.
- **Chicago River, centro**: trafficato e affidabile.
- **Chicago Sanitary and Ship Canal, Cal-Sag Channel, Calumet River**: un'ora
  di ascolto, **zero navi**. Il canale non è vuoto: i suoi convogli a spinta si
  vedono sui servizi commerciali tramite AIS satellitare, che gli aggregatori
  gratuiti non hanno. Il traffico è reale; la copertura da terra no.

Nessuna nave nella tua area può voler dire nessun ricevitore piuttosto che
nessuna barca. Verifica che la tua fonte copra le tue acque prima di pensare
che l'integrazione sia guasta.

Una nave che smette di comparire non è detto che se ne sia andata. Nessuna di
queste fonti garantisce la consegna, quindi l'integrazione mostra quando ogni
nave è stata sentita l'ultima volta e la toglie solo dopo un periodo di
silenzio.

## Navi che meritano un'immagine tutta loro

La maggior parte delle navi viene disegnata secondo il tipo. Alcune hanno
un'immagine propria: yacht reali e di Stato, e barche famose come i battelli
turistici, i taxi d'acqua e le motobarche antincendio di Chicago. Conosci una
nave che ne merita una, in qualsiasi parte del mondo? Apri una issue su
<https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues> con il
nome e il numero MMSI o IMO, e una foto o un link se ce l'hai.

## Lingue

Questo README: [English](README.md), [Deutsch](README.de.md),
[Français](README.fr.md), [Nederlands](README.nl.md),
[简体中文](README.zh-Hans.md), [Español](README.es.md), **Italiano**,
[Dansk](README.da.md) e [Kalaallisut](README.kl.md) (una bozza, inviata per
la revisione a Oqaasileriffik, la segreteria della lingua groenlandese; fino
ad allora la pagina danese è quella affidabile). Il README è tradotto in un
breve elenco di lingue: quelle che legge la maggior parte degli utenti di Home
Assistant, e qualcun'altra quando c'è un buon motivo. Ogni README tradotto è
completo: tutto ciò che c'è in quello inglese c'è in ciascuno, e nessuno ti
rimanda all'inglese per i dettagli.

La finestra di configurazione e le impostazioni di un'area compaiono nella
lingua del tuo Home Assistant quando è una di queste: English, Dansk, Deutsch,
Español, Français, Gaeilge, Íslenska, Italiano, Nederlands, Norsk Bokmål,
Polski, Português, Português (BR), Suomi, Svenska e 简体中文. Qualsiasi altra
lingua mostra la finestra in inglese. Il kalaallisut non è ancora una lingua di
Home Assistant; abbiamo chiesto a Home Assistant di aggiungerlo, e la finestra
seguirà appena potrà essere mostrata.

Hai trovato in una traduzione un errore che cambia il senso o si legge male?
Diccelo su <https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues>.
Le traduzioni sono state scritte per questo progetto e non tutte sono state
ancora lette da un madrelingua.

**Fai fatica a seguire in una di queste lingue?** Chiedine un'altra allo stesso
indirizzo, e cercheremo di accontentarti.

## Parte di Live Track

Live Track è un insieme di integrazioni di Home Assistant, una per ogni tipo
di cosa che si muove, che disegnano tutte sulla stessa mappa. Condividono una
libreria Python
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore))
e la scheda mappa, così installarne un'altra non aggiunge richieste a una
fonte condivisa. Pubblicate:
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft),
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
[Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail),
[Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail)
e Live Track Ships. Ciascuna funziona anche da sola.

## Nessuna affiliazione

Non affiliata con aisstream.io, Fintraffic, BarentsWatch, MarineTraffic,
VesselFinder, alcun armatore né alcuna autorità marittima. L'AIS è un sistema
per la sicurezza della navigazione; **questa integrazione è per curiosità e non
serve per la navigazione, per evitare collisioni né per alcuno scopo
operativo.**

## Licenza

Codice: MIT, in [LICENSE](LICENSE). Crediti di dati e immagini:
[ATTRIBUTION.md](ATTRIBUTION.md).

## Parole chiave

Home Assistant AIS · tracciamento navi · navi sulla mappa · tracciamento
barche · traffico marittimo in diretta · mappa AIS · aisstream.io ·
Digitraffic · BarentsWatch · geo_location · integrazione HACS
