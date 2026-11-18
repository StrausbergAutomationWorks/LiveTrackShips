# Live Track Ships

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · **Italiano** · [Dansk](README.da.md) · [Kalaallisut](README.kl.md) · [Tutte le lingue](#lingue)

**Navi e barche per Home Assistant, su una sola mappa.** Live Track Ships
mette sulla tua mappa di Home Assistant navi, barche e tutto ciò che
trasmette l'AIS (il segnale radio con cui le navi dicono dove sono), vicino a
te o in qualunque parte del mondo tu scelga. Segue anche le navi che scegli,
ovunque vadano, e avvisa le tue automazioni quando una nave entra nella tua
area o ne esce.

> **Live Track Ships è un modulo di Live Track**, una famiglia di
> integrazioni di Home Assistant che disegnano tutto ciò che si muove, e il
> tempo che attraversa, su una mappa condivisa: aerei, navi, treni e meteo.
> Installalo da solo o accanto agli altri moduli
> ([elenco sotto](#parte-di-live-track-gli-altri-moduli)).

> **In crescita, e aperto alle idee.** Oggi Live Track Ships copre tutto il
> mondo dove volontari gestiscono ricevitori, la Finlandia e la Norvegia con
> più dettaglio, e il tuo ricevitore. Stiamo aggiungendo altre fonti di dati e
> altri paesi. Manca il tuo? [Suggeriscilo](#aiutaci-a-farlo-crescere), o
> aggiungilo tu: ti aiuteremo a farlo.

**Stato: 0.1.0, la prima versione.** Si aggiunge al Marketplace tramite link
([sotto](#installazione-passo-dopo-passo)); non è ancora nel catalogo del
Marketplace.

Opera originale di StrausbergAutomationWorks. Non affiliato a, né approvato
da, aisstream.io, Fintraffic (Finlandia), BarentsWatch (Norvegia), Wikidata,
Wikimedia Commons, VesselFinder, MarineTraffic, alcun armatore o alcuna
autorità marittima.

> ⚠ **Non è un sistema di sicurezza.** Mostra dati pubblici, spesso vecchi di
> pochi secondi e a volte di minuti, e solo ciò che i ricevitori riescono a
> sentire. Non serve per navigare, evitare collisioni o per qualunque altro
> uso operativo. In acqua, usa il tuo AIS, il radar, le carte nautiche e la
> radio VHF.

---

## Indice

1. [Tutto quello che fa](#tutto-quello-che-fa)
2. [Dove funziona](#dove-funziona)
3. [Parte di Live Track: gli altri moduli](#parte-di-live-track-gli-altri-moduli)
4. [Prima di iniziare](#prima-di-iniziare)
5. [Installazione, passo dopo passo](#installazione-passo-dopo-passo)
6. [Configurazione, passo dopo passo](#configurazione-passo-dopo-passo)
7. [Chiavi gratuite che attivano di più, passo dopo passo](#chiavi-gratuite-che-attivano-di-più-passo-dopo-passo)
8. [Mettere la mappa su una plancia](#mettere-la-mappa-su-una-plancia)
9. [Usarlo nelle automazioni](#usarlo-nelle-automazioni)
10. [Tutto sulla mappa, nel dettaglio](#tutto-sulla-mappa-nel-dettaglio)
11. [Tutte le entità che crea](#tutte-le-entità-che-crea)
12. [Cosa invia e scarica](#cosa-invia-e-scarica)
13. [Aiutaci a farlo crescere](#aiutaci-a-farlo-crescere)
14. [Lingue](#lingue)
15. [Riconoscimenti e licenze](#riconoscimenti-e-licenze)
16. [Parole chiave](#parole-chiave)

---

## Tutto quello che fa

### Sulla mappa, senza configurare nulla

Aggiungi un'**area**: un centro e un raggio sulla mappa, e una fonte di dati.
Tutto ciò che segue compare allora in quell'area. Fintraffic Digitraffic
(Finlandia) e il tuo ricevitore non richiedono chiavi; aisstream.io e
BarentsWatch (Norvegia) ne richiedono una gratuita
([sotto](#con-la-tua-chiave-o-il-tuo-account-gratuito)).

| Cosa | Dove | Da |
|---|---|---|
| **Navi**: navi da carico, petroliere, traghetti, rimorchiatori, pescherecci, imbarcazioni da diporto e barche a vela, ognuna con la propria immagine, ruotata secondo la sua rotta | in ogni area | la fonte che scegli |
| **Ciò che non è una nave**: boe di attrezzi da pesca, aiuti alla navigazione, stazioni base AIS, aerei di ricerca e soccorso e radiofari di emergenza | in ogni area, quando la fonte li invia | la fonte che scegli |
| **Foto e link**: una foto della nave quando se ne conosce una, e un link alla nave su VesselFinder | ogni nave con numero IMO o MMSI | Wikidata e Wikimedia Commons |
| **Tracce**: dove è stata una nave nelle ultime 24 ore, disegnato quando lo chiedi | ogni nave | conservate dal tuo Home Assistant |
| **Navi della guardia costiera impiegate nell'immigrazione**, disegnate con i colori della guardia costiera | ovunque vengano sentite | l'elenco pubblico EnforcementVessels |
| **Arrivi e partenze**: un evento per le tue automazioni quando una nave entra in un'area o ne esce | in ogni area | calcolati dal tuo Home Assistant |

### Con la tua chiave o il tuo account gratuito

| Chiave o account gratuito | Cosa aggiunge |
|---|---|
| Chiave **aisstream.io** | navi in qualunque parte del mondo dove volontari gestiscono ricevitori; e le **navi seguite**: navi scelte, seguite ovunque si trovino, con un evento quando una arriva, parte, tace o cambia destinazione |
| Account **BarentsWatch** (Norvegia) | navi nelle acque norvegesi, Svalbard compreso, con nome e tipo di nave a ogni posizione |

Ognuna si ottiene in pochi minuti: [passo dopo passo sotto](#chiavi-gratuite-che-attivano-di-più-passo-dopo-passo).

---

## Dove funziona

| Regione | Cosa ottieni | Da | Serve |
|---|---|---|---|
| **Tutto il mondo** | navi dove volontari gestiscono ricevitori: bene vicino a coste e porti trafficati, poco o niente altrove | aisstream.io | una chiave gratuita |
| **Europa**: Finlandia e mar Baltico | navi nelle acque finlandesi e baltiche, nuove posizioni ogni minuto | Fintraffic Digitraffic (Finlandia) | niente |
| **Europa**: Norvegia | navi nelle acque norvegesi, Svalbard compreso, con nome e tipo a ogni posizione | BarentsWatch (Norvegia) | un account gratuito |
| **Il tuo ricevitore**: ovunque | tutto ciò che sente la tua antenna, senza internet | il tuo ricevitore AIS | un ricevitore che invia NMEA via UDP |

Scegli una fonte per ogni area. Quali tipi di oggetti compaiono, quanto sono
recenti le posizioni e quanto sono completi i dati delle navi dipende tutto da
quella fonte.

⚠ **La copertura è buona dove ci sono ricevitori, e assente dove non ci
sono.** Nessuna impostazione può creare una copertura che non esiste.
Misurato il 2026-09-02 con aisstream.io intorno a Chicago (Stati Uniti):
100 navi in 120 secondi sui Grandi Laghi, ma nessuna nave in un'ora sui canali
a sud della città, dove pure passano convogli di chiatte: i servizi
commerciali li vedono via satellite, cosa che le fonti gratuite non offrono.
**Nessuna nave nella tua area può significare nessun ricevitore, non nessuna
barca.** Controlla che la tua fonte copra le tue acque prima di pensare che
qualcosa sia guasto.

⚠ **Il tuo ricevitore:**

* Un'area ascolta su una porta. Due ricevitori richiedono due porte.
* Tutto ciò che il ricevitore sente dentro il tuo cerchio viene mostrato,
  aiuti alla navigazione e stazioni base compresi. Il suo sensore di stazione
  conta anche ciò che sente fuori dal cerchio.
* Una frase NMEA non porta la data, quindi l'ora di una posizione è l'ora in
  cui Home Assistant l'ha ricevuta.
* La velocità di accostata non viene mostrata per questa fonte.
* Finora è stato provato con frasi registrate inviate via UDP, non con un
  ricevitore. Se lo provi con il tuo,
  [raccontaci com'è andata](#aiutaci-a-farlo-crescere).

Non è nell'elenco? [Diccelo](#aiutaci-a-farlo-crescere). Dove qualcuno
pubblica i dati apertamente, valuteremo di aggiungerli.

---

## Parte di Live Track: gli altri moduli

Live Track è un insieme di integrazioni di Home Assistant, una per ogni tipo
di cosa che si muove, tutte disegnate sulla stessa scheda mappa. Ognuna
funziona da sola; insieme formano un'unica immagine dal vivo. Condividono la
scheda mappa e una libreria Python
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
quindi installarne un'altra non aggiunge richieste a una fonte che un'altra
legge già.

| Modulo | Cosa mette sulla mappa | Stato |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | aerei sopra di te tramite ADS-B, con rotte e icone per tipo | pubblicato |
| **Live Track Ships** | navi e barche tramite AIS, vicino a te o ovunque (questo modulo) | pubblicato |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | treni suburbani in Nord America, Europa e Australia | pubblicato |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | treni intercity e a lunga percorrenza in Nord America, Europa e Australia | pubblicato |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | aerei e navi dell'immigrazione e delle forze dell'ordine federali, da elenchi pubblici | pubblicato |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | meteo, tempeste e rischi naturali | pubblicato |
| Live Track Stations | tabelloni delle partenze e avvisi "è ora di andare" per ogni stazione | previsto |
| Live Track Satellites | satelliti che passano sopra di te | previsto |
| Live Track Freight Trains | treni merci e di servizio dove le ferrovie li pubblicano | previsto |
| Live Track Transit | autobus urbani, tram, traghetti e metropolitane | previsto |
| Live Track Intercity Buses | autobus interurbani e regionali | previsto |
| Live Track Commuter Buses | autobus per pendolari | previsto |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | la scheda mappa condivisa su cui disegna ogni modulo | pubblicata, installata con ogni modulo |

Tutto è gratuito e open source. Niente è riservato agli sponsor.

---

## Prima di iniziare

* **Home Assistant** 2026.11 o successivo.
* **Il Marketplace** (HACS) nel tuo Home Assistant, per installarlo e
  aggiornarlo in modo semplice. Senza, puoi copiare i file a mano.
* **Accesso a internet** per Home Assistant, per le fonti online e le foto. Il
  tuo ricevitore funziona senza.
* **Una fonte di dati.** Digitraffic (Finlandia) e il tuo ricevitore non
  richiedono account. aisstream.io e BarentsWatch (Norvegia) richiedono una
  chiave gratuita
  ([passo dopo passo](#chiavi-gratuite-che-attivano-di-più-passo-dopo-passo)).
* **Facoltativo: il tuo ricevitore AIS.** Il ricevitore, o il programma che
  lo decodifica, invia frasi NMEA (`!AIVDM`) via UDP all'indirizzo del tuo
  Home Assistant, sulla stessa rete. In AIS-catcher è `-u <address> <port>`;
  in rtl-ais, `-h <address> -P <port>`; OpenCPN e Signal K lo aggiungono come
  connessione di uscita UDP. Un ricevitore che si collega via USB, come un
  dAISy, ha bisogno di uno di questi programmi per passare le sue frasi.
* **Facoltativo: auto-entities** dal Marketplace, per mettere i segnaposto
  sulla mappa (vedi [Mettere la mappa su una plancia](#mettere-la-mappa-su-una-plancia)).
* Niente da pagare. Per Digitraffic e il tuo ricevitore non serve un account;
  le chiavi gratuite servono solo per aisstream.io e BarentsWatch.

---

## Installazione, passo dopo passo

### Dal Marketplace (consigliato)

Live Track Ships non è ancora nel catalogo del Marketplace. Aggiungilo tramite
il suo link:

1. In Home Assistant, apri **Impostazioni → Marketplace** (HACS).
2. Scegli **Aggiungi da link** (o il menu a tre puntini →
   **Repository personalizzati**).
3. Inserisci `StrausbergAutomationWorks/LiveTrackShips`. Se viene chiesto il
   tipo, scegli **Integrazione**.
4. Trova **Live Track Ships** nell'elenco e scegli **Scarica** o
   **Installa**.
5. **Riavvia Home Assistant**: **Impostazioni → Sistema → Riparazioni** offre
   il riavvio, oppure usa **Impostazioni → Sistema → Riavvia**.

### A mano

1. Scarica il codice sorgente della
   [versione più recente](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest).
2. Copia la sua cartella `custom_components/live_track_ships` nella cartella
   `custom_components` della cartella di configurazione del tuo Home Assistant
   (crea `custom_components` se non c'è).
3. Riavvia Home Assistant.

---

## Configurazione, passo dopo passo

1. Apri **Impostazioni → Dispositivi e servizi**.
2. Scegli **Aggiungi integrazione** (in basso a destra) e cerca **Live Track
   Ships**.
3. Scegli **Tutte le navi di un'area**. (L'altra scelta, **Navi scelte,
   ovunque si trovino**, segue un elenco di navi ovunque: vedi
   [Navi seguite](#navi-seguite-navi-scelte-ovunque).)
4. **Fonte dei dati**: scegline una. Se non sei sicuro: in Finlandia
   Fintraffic Digitraffic, che non richiede chiavi; in Norvegia BarentsWatch;
   altrove aisstream.io.
5. **Chiave API** (aisstream.io), oppure **ID client** e **Segreto client**
   (BarentsWatch): incollali
   ([come ottenerli](#chiavi-gratuite-che-attivano-di-più-passo-dopo-passo)).
   Un'area che hai già configurato li compila per te.
6. **Porta UDP (il tuo ricevitore)**: solo per il tuo ricevitore. Inserisci la
   porta a cui invia, da 1024 a 65535. Lascia 10110 se non l'hai cambiata.
7. **Centro**: trascina il segnaposto al centro delle acque che vuoi
   osservare. Parte da casa tua.
8. **Raggio (km)**: da 1 a 500 km (da 0,6 a 310 miglia). Se non sei sicuro,
   lascia 50 km (31 miglia).
9. **Numero massimo di navi seguite**: lascia 1.000, a meno che la tua
   macchina sia piccola.
10. Scegli **Invia**.

È tutto. Le navi compaiono entro un minuto o due, man mano che la fonte le
invia. Tipi e dimensioni si completano nei minuti successivi. Ogni area è una
voce, intitolata *Ships near <latitude>, <longitude>*. Aggiungi altre aree
nello stesso modo.

* La stessa fonte non può osservare due volte lo stesso centro.
* Quando almeno il 5% di un cerchio BarentsWatch cade fuori dalle acque che
  BarentsWatch pubblica, la finestra di dialogo dice quanto prima di creare
  l'area. Scegli **Invia** per tenere comunque quel cerchio.

### Cambiare ciò che mostra: le opzioni

Apri **Impostazioni → Dispositivi e servizi → Live Track Ships → Configura**
(l'ingranaggio) sull'area da cambiare. Ogni opzione, in parole semplici:

| Opzione | Cosa fa | Predefinito |
|---|---|---|
| **Centro** | sposta l'area; viene rinominata secondo la nuova posizione e ricaricata | casa tua |
| **Raggio (km)** | fino a che distanza dal centro vengono mostrate le navi, da 1 a 500 km (da 0,6 a 310 miglia) | 50 km (31 miglia) |
| **Numero massimo di navi seguite** | un limite di sicurezza per quest'area, da 1 a 5.000; se ce ne sono di più, si tengono le più vicine | 1.000 |
| **Numero massimo di navi sulla mappa, tutte le voci di Live Track Ships insieme** | il tetto per tutte le tue aree insieme, da 100 a 2.500; abbassalo su una macchina piccola; vale l'impostazione più bassa tra tutte le aree | 2.500 |
| **Porta UDP (il tuo ricevitore)** | la porta a cui invia il tuo ricevitore; cambiarla ricarica l'area | 10110 |

Quante navi contiene un cerchio dipende molto più da quali acque sono che
dalla sua grandezza. Nei test, un cerchio di 50 km (31 miglia) conteneva circa
4 navi sopra Chicago (Stati Uniti) e circa 340 sopra il Solent (Inghilterra):
lo stesso raggio, circa 80 volte il traffico. Quando un limite taglia
l'elenco, il `sensor.ships_in_range` dell'area lo indica.

---

## Chiavi gratuite che attivano di più, passo dopo passo

Sono tutte gratuite e personali: ogni persona che installa Live Track Ships
ottiene le proprie. Incollale nella finestra di configurazione quando aggiungi
un'area (passo 5 della [configurazione](#configurazione-passo-dopo-passo)).

### aisstream.io (navi e navi seguite, tutto il mondo)

1. Apri <https://aisstream.io/account> e accedi. (Il link **API keys** in
   alto su aisstream.io apre la stessa pagina.)
2. Crea lì una nuova chiave API.
3. Copia subito la chiave: aisstream.io la mostra una sola volta.
4. Incollala in **Chiave API**.

⚠ aisstream.io consente tre connessioni per account e tre per indirizzo
internet pubblico. Live Track Ships ne usa al massimo due: una per tutte le
tue aree e una per le tue navi seguite, che condivide con Live Track SALT se è
installato con la stessa chiave. Se altri programmi usano la stessa chiave o
la stessa connessione a internet, contali anche loro.

### BarentsWatch (navi nelle acque norvegesi, Norvegia)

1. Apri <https://www.barentswatch.no/minside/> e crea un utente, oppure
   accedi.
2. Sotto **API access (for developers)** (*API-tilgang (for utviklere)*),
   scegli **New Client** (*Ny klient*).
3. Scegli il client AIS, non il client API.
4. Copia l'**ID client**. Ha questo aspetto:
   `your.email@example.com:live_track_ships`. Incollalo esattamente così in
   **ID client**.
5. Copia il **segreto client** in **Segreto client**. Viene mostrato una sola
   volta; se non l'hai conservato, generane uno nuovo.

---

## Mettere la mappa su una plancia

La mappa è [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
la scheda su cui disegna ogni modulo di Live Track. **Viene installata con
Live Track Ships**: niente da scaricare, niente da copiare, nessuna risorsa da
aggiungere.

1. Apri una plancia, scegli la matita (**Modifica la plancia**), poi
   **Aggiungi scheda**.
2. Scorri fino in fondo e scegli **Manuale**.
3. Incolla questo e scegli **Salva**:

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

I segnaposto richiedono
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities) dal
Marketplace. Se sono installati altri moduli di Live Track, aggiungi un altro
filtro `- domain: geo_location` per ciascuna delle loro fonti
(`live_track_aircraft`, `live_track_weather` e così via).

**Sulla mappa:**

* Ogni nave è disegnata con la propria immagine, ruotata secondo la sua rotta,
  e scivola tra le posizioni segnalate seguendo l'acqua invece di attraversare
  la terra.
* **Punta** una nave per vederne il nome, e la foto quando c'è. **Fai clic**
  per vederne la foto, i link, **Track** e **Details**
  ([Foto e link](#foto-e-link), [Tracce](#tracce)).
* La **scheda filtro** (`custom:live-track-map-filter-card`) nasconde i tipi
  di nave che deselezioni ([Nascondere tipi di nave](#nascondere-tipi-di-nave)).

Se le risorse delle tue plance sono definite in YAML
(`lovelace: resource_mode: yaml`), non si può registrare nulla per te: un
avviso in **Riparazioni** ti dà allora la riga esatta da aggiungere. Una
scheda che hai installato tu dal Marketplace non viene toccata. Se i file
dell'integrazione vengono rimossi mentre le sue aree sono ancora configurate,
e nessun altro modulo di Live Track è installato, rimuovi tu la riga della
scheda in **Impostazioni → Plance → Risorse**. Qualunque altra scheda mappa
che mostra entità `geo_location` mostra anche le navi, senza le loro
immagini.

---

## Usarlo nelle automazioni

Tutto è un'entità o un evento normale di Home Assistant, quindi l'editor delle
automazioni funziona con esso, senza codice.

**Una notifica quando una nave lunga più di 150 m (490 piedi) entra nella tua
area:**

1. **Impostazioni → Automazioni e scenari → Crea automazione → Crea una nuova
   automazione**.
2. **Quando**: **Aggiungi attivazione**, cerca **Ricevuto evento manuale** e
   inserisci come **Tipo di evento** `live_track_ships_entry`.
3. **e se**: **Aggiungi condizione** → **Modello**, e inserisci questo
   **Valore modello**: `{{ trigger.event.data.length_m | default(0) > 150 }}`
4. **Allora**: **Aggiungi azione**, cerca l'azione di notifica del tuo
   telefono (porta il nome del tuo telefono) e inserisci questo messaggio:

   ```text
   {{ trigger.event.data.name | default('Una nave') }}, {{ trigger.event.data.length_m }} m, a {{ trigger.event.data.distance_km }} km
   ```

5. **Salva**.

**Altre idee:** accendere una luce quando il traghetto della sera arriva nel
tuo porto in Norvegia; un messaggio quando la barca di un familiare, una nave
seguita, torna a casa in Finlandia; una notifica quando la nave da crociera
che aspetti arriva a Sydney (Australia); il numero di navi nel tuo porto su
una plancia, da `sensor.ships_in_range`.

**Gli eventi di area.** Ogni area lancia `live_track_ships_entry` quando una
nave entra nel suo cerchio e `live_track_ships_exit` quando ne esce. Ogni nave
viene annunciata; la tua automazione sceglie quelle che contano. I campi usano
gli stessi nomi e le stesse unità degli attributi della nave, e omettono ciò
che la fonte non ha inviato:

| Campo | Cosa contiene |
|---|---|
| `area_id`, `area` | l'ID della voce di configurazione dell'area e il suo titolo |
| `identity` | l'MMSI |
| `name`, `call_sign`, `imo` | se inviati |
| `object_kind` | `vessel`, `net_buoy`, `aton`, `base_station`, `sar_aircraft` o `distress_beacon` |
| `ship_type`, `ship_type_label`, `length_m`, `beam_m`, `draught_m`, `destination`, `nav_status` | solo navi, se inviati |
| `speed_kmh`, `course_deg`, `heading_deg` | se inviati |
| `latitude`, `longitude`, `distance_km`, `bearing_from_centre_deg`, `last_seen` | dove è stata sentita, dal centro dell'area |
| `entity_id` | solo all'ingresso: `geo_location.vessel_<MMSI>`, quando la nave è sulla mappa |
| `reason` | solo all'uscita: `left` (sentita fuori dal cerchio) o `silent` (non sentita da un po', quindi forse ancora lì) |

⚠ Quattro cose da sapere:

* **Un arrivo viene annunciato solo se la nave è stata sentita prima fuori dal
  cerchio.** Una nave sentita per la prima volta dentro forse era lì da
  sempre: dopo un riavvio, le fonti continuano per molti minuti a consegnare
  navi che non si sono mosse. Quindi una nave che i ricevitori hanno perso
  mentre entrava, o una che accende il transponder dentro, non viene
  annunciata.
* **Una partenza sentita fuori viene sempre annunciata**, anche per una nave
  che era lì prima dell'avvio di Home Assistant. Una nave che tace viene
  annunciata come partita (`reason: silent`) solo se il suo arrivo lo è stato.
* **Un'uscita attende 2 minuti.** Una nave che torna prima, lungo il bordo del
  cerchio, non viene annunciata come partita e poi di nuovo arrivata.
* **All'arrivo possono mancare dei dati.** Nome, tipo e dimensioni viaggiano
  in un messaggio più lento della posizione. Una nave sentita per la prima
  volta può arrivare con una posizione e nient'altro.

Due aree sulle stesse acque lanciano ciascuna i propri eventi. I limiti su
quante navi vengono disegnate non fanno mai entrare o uscire una nave.

**L'evento delle navi seguite.**
[Le navi seguite](#navi-seguite-navi-scelte-ovunque) lanciano un evento,
`live_track_ships_watched`, il cui `change` dice cosa è successo:

| `change` | Quando |
|---|---|
| `arrived` | la nave si dichiara ormeggiata o alla fonda o, senza stato, resta sotto 3,7 km/h (2 nodi) |
| `departed` | è di nuovo in navigazione |
| `silent` | non sentita per 30 minuti (6 ore se ormeggiata o alla fonda); lascia la mappa, e forse è ancora lì |
| `heard` | sentita di nuovo dopo `silent` |
| `destination` | l'equipaggio ha cambiato destinazione; `destination_previous` contiene quella vecchia |

I dati contengono `watch_id`, `watch`, `identity`, il tuo `label` e gli
stessi campi della nave degli eventi di area, con distanza e rilevamento da
casa tua. Arrivo e partenza attendono che il nuovo stato sia durato 5 minuti
secondo l'orologio della nave stessa, perché una barca che deriva lentamente
non passi continuamente da uno stato all'altro. Nulla viene annunciato dalla
prima posizione di una nave dopo un riavvio: quella fissa il punto di
partenza. Le destinazioni le scrive l'equipaggio e spesso non sono
aggiornate.

---

## Tutto sulla mappa, nel dettaglio

L'AIS (Automatic Identification System, sistema di identificazione
automatica) è una trasmissione radio VHF con cui le navi comunicano posizione,
identità e viaggio alle altre navi e a terra. È la versione marittima di ciò
che gli aerei inviano come ADS-B. Le navi commerciali devono averlo; molte
imbarcazioni da diporto lo hanno per scelta, di solito come apparato di
classe B meno potente. L'AIS è trasmesso in chiaro: chiunque abbia un
ricevitore può sentirlo, e servizi pubblici lo ritrasmettono. **Live Track
Ships mostra tutto ciò che la fonte invia.** Non viene filtrato nulla, e non
c'è alcuna impostazione per nascondere una categoria a Home Assistant.

### Navi

Ogni nave è un segnaposto il cui stato è la sua distanza dal centro
dell'area, in chilometri. La maggior parte delle navi è disegnata per tipo:
nave da carico, petroliera, traghetto, rimorchiatore e così via. Alcune hanno
un'immagine propria: yacht reali e di Stato, e barche note come i battelli
turistici, i taxi d'acqua e le motobarche dei pompieri di una città. Conosci
una nave che ne merita una, in qualunque parte del mondo?
[Suggeriscila](#aiutaci-a-farlo-crescere), con il nome e il numero MMSI o
IMO, e una foto o un link se ne hai.

Perché una nave sparisca appena se ne va, a ogni fonte online si chiede un
anello un po' più largo del tuo cerchio (il 10%, almeno 1 km), e il tuo
ricevitore invia tutto ciò che sente. Si tengono solo le navi dentro il tuo
cerchio: una nave sentita fuori lascia subito la mappa. Una nave che non viene
più sentita sparisce dopo un periodo di silenzio. Una nave che smette di
comparire non è per forza andata via: nessuna di queste fonti promette di
consegnare ogni messaggio.

⚠ **Il tipo di nave manca spesso, soprattutto per le barche piccole.**
Posizione e nome arrivano con quasi ogni messaggio. Tipo e dimensioni
arrivano in un messaggio a parte, più lento, che molti apparati di classe B
inviano di rado. Aspettati che molte navi, tra cui la maggior parte delle
barche piccole, non mostrino tipo né dimensioni, e che tutte abbiano pochi
dati per diversi minuti dopo un riavvio di Home Assistant. Sono i dati, non un
guasto. Tipi e dimensioni sentiti una volta restano dopo i riavvii.

Gli attributi di una nave comprendono nome, MMSI, nominativo radio, velocità,
rotta, prua, lunghezza, larghezza, tipo, destinazione, `object_kind`,
`last_seen` e `attribution`, ciascuno solo se la fonte l'ha inviato. Una nave
vista da due aree è una sola entità.

### Barche private e barche a vela

Un'imbarcazione da diporto che trasmette l'AIS compare sulla tua mappa
esattamente come una nave da carico. A seconda di ciò che la barca trasmette,
la sua entità può contenere:

* il suo **nome**, che è anche l'etichetta disegnata sulla mappa;
* il suo **MMSI** e il suo **nominativo radio**, entrambi permanenti e
  consultabili pubblicamente;
* la sua **posizione** con una precisione di circa un metro, la posizione
  precedente e quando ciascuna è stata sentita;
* velocità, rotta e prua, e lunghezza, larghezza e tipo, se inviati.

Una barca che lascia il transponder acceso al pontile resta sulla mappa al
suo ormeggio finché trasmette. Chiunque possa aprire la tua mappa può anche
premere **Track** su una barca del genere e vedere dove è stata nelle ultime
24 ore (o per il tempo che imposti), ormeggio compreso.

Non esiste un elenco di esclusione per l'AIS, come c'è per gli aerei, e
questa integrazione non se ne inventa uno. Se vuoi meno barche private sulla
mappa, riduci il raggio.

### Ciò che non è una nave

Ogni entità porta `object_kind`: `vessel`, `net_buoy` (boa di attrezzi da
pesca), `aton` (aiuto alla navigazione: una boa, un segnale o un faro),
`base_station` (una stazione AIS a terra), `sar_aircraft` (un aereo di
ricerca e soccorso) o `distress_beacon`. La maggior parte si distingue dal
formato di identità che assegna loro l'Unione internazionale delle
telecomunicazioni (UIT). Le boe di attrezzi da pesca no: trasmettono con
identità da nave, quindi si riconoscono dai nomi di fabbrica (FISHING BOUY,
NET MARK, BUOY) insieme alla mancanza di una lunghezza trasmessa.

Tutto ciò che non è una nave è mostrato senza tipo, dimensioni né stato di
navigazione. Le boe di attrezzi da pesca derivano con le loro lenze, quindi
mantengono velocità e rotta, e sono disegnate come un pesce che punta nella
direzione in cui derivano.

Quali compaiono dipende dalla fonte. Misurato in una serata:

| Fonte | Boe di attrezzi da pesca | Aerei di ricerca e soccorso | Aiuti alla navigazione, stazioni base |
|---|---|---|---|
| BarentsWatch | sì | sì | nessuno visto |
| Digitraffic | nessuna vista | sì | nessuno visto |
| aisstream.io | nessuna vista | nessuno visto | nessuno visto |
| Il tuo ricevitore | ciò che sente | ciò che sente | ciò che sente |

aisstream.io ha consegnato solo posizioni e dati delle navi, sia sui Grandi
Laghi (Nord America) sia sulle stesse acque norvegesi e danesi dove
BarentsWatch mostra le boe.

### Navi della guardia costiera impiegate nell'immigrazione

Una nave dell'elenco pubblico
[EnforcementVessels](https://github.com/StrausbergAutomationWorks/EnforcementVessels)
(navi della guardia costiera degli Stati Uniti impiegate nell'immigrazione)
è disegnata con i colori della guardia costiera, con il nome e l'ente presi
dall'elenco, ovunque venga sentita.

### Navi seguite: navi scelte ovunque

Oltre alle aree, puoi seguire un elenco di navi ovunque si trovino: la barca
di un familiare, un traghetto che prendi, una nave da crociera che torna a
casa. Serve una chiave aisstream.io, e c'è un solo elenco di questo tipo per
ogni Home Assistant.

1. Apri **Impostazioni → Dispositivi e servizi**, scegli **Aggiungi
   integrazione** e cerca **Live Track Ships**.
2. Scegli **Navi scelte, ovunque si trovino**.
3. **Chiave API**: la chiave di un'area che hai già configurato è compilata.
4. **Navi**: una nave per riga, il suo MMSI di 9 cifre e poi, se vuoi, un
   nome tuo:

   ```text
   244650000 La barca di papà
   366999999 Il traghetto
   ```

5. Scegli **Invia**.

Al massimo 100 navi. aisstream.io segue al massimo 200 MMSI per chiave, e
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
se installato con la stessa chiave, ne usa una parte. Un elenco che li
supererebbe viene rifiutato al caricamento della voce, con il motivo. Per
cambiare l'elenco, apri **Configura** sulla voce.

Una nave seguita è disegnata sulla mappa come ogni altra, ovunque venga
sentita, e il suo stato è la distanza da casa tua. Un'area che la mostra già
la tiene: una nave, un segnaposto. La voce aggiunge `sensor.watched_vessels`:
quante delle navi dell'elenco si sentono ora. Il suo attributo `vessels` le
elenca tutte, con il loro nome e il loro ultimo stato noto. Il suo evento è
descritto in [Usarlo nelle automazioni](#usarlo-nelle-automazioni).

### Foto e link

Quando una nave invia un numero IMO e Wikidata conosce una foto di quella
nave su Wikimedia Commons, la nave porta `marker_photo`. La mappa mostra la
foto quando punti la nave, con il fotografo e la licenza; un clic la apre più
grande, con link alla pagina della foto e alla sua licenza. Ogni nave con
numero IMO o MMSI porta anche `marker_links`, un link alla nave su
VesselFinder. Il pulsante **Details** nella finestra apre la consueta finestra
di dialogo della nave.

Il tuo Home Assistant chiede da solo a Wikidata e Commons, 20 numeri IMO alla
volta, a dieci secondi di distanza, e tiene ogni risposta per 30 giorni
(14 giorni quando non c'è foto) in `.storage/saw_vessel_photos.json`. Aspettati
una foto per circa una nave su dieci: sul nostro sistema di prova, 49 numeri
IMO su 521 ne avevano una.

⚠ Una foto può mostrare la nave con un nome precedente: il numero IMO
appartiene allo scafo e lo segue quando la nave cambia nome.

### Tracce

Ogni nave porta anche `marker_track`. Fai clic su una nave e premi **Track**
nella sua finestra: la mappa disegna dove è stata, come una linea che finisce
sulla nave, e la linea cresce mentre guardi. **Hide track** la toglie. Non
viene disegnato nulla finché non lo chiedi, perché un porto trafficato non
sparisca sotto le linee.

La traccia contiene solo le posizioni che la nave ha segnalato mentre era
sulla tua mappa, ridotte a una ogni 25 m (82 piedi) o 10 minuti, e mai due in
meno di 30 secondi. Il tuo Home Assistant la tiene in memoria e la salva in
`.storage/saw_vessel_tracks.json`, quindi sopravvive a un riavvio. Copre le
ultime 24 ore. Per tenerne di più o di meno:

1. Apri **Impostazioni → Strumenti → Azioni**.
2. Scegli l'azione **Live Track Ships: Imposta le ore di traccia**.
3. Inserisci **Ore**, da 1 a 168 (una settimana), e scegli **Esegui azione**.

Vale per tutte le aree insieme; un'impostazione più corta elimina subito le
posizioni più vecchie.

⚠ La traccia parte vuota alla prima installazione. Una nave che ha lasciato
l'area o ha taciuto ha un vuoto, disegnato come una linea retta tra le
posizioni prima e dopo.

### Nascondere tipi di nave

Ogni nave porta `marker_group`, `marker_group_label` e `marker_group_order`:
uno di tredici gruppi (carico; petroliera; passeggeri e traghetto; pesca;
diporto e vela; rimorchiatore, pilota e servizio portuale; Stato, ricerca e
soccorso e forze dell'ordine; alta velocità e altri; tipo non inviato; boe di
attrezzi da pesca; aiuti alla navigazione; stazioni base; aerei di ricerca e
soccorso). La scheda filtro della scheda mappa,
`custom:live-track-map-filter-card`, elenca i gruppi con quanti ce ne sono
sulla mappa, e nasconde quelli che deselezioni. Mettila in qualunque vista
della plancia. La tua scelta resta solo in quel browser.

Nascondere vale solo per la mappa: l'integrazione continua a contare ogni
nave e a lanciare i suoi eventi per ogni nave. Un radiofaro di emergenza non
ha gruppo, quindi non viene mai nascosto.

---

## Tutte le entità che crea

| Entità | Che cos'è |
|---|---|
| `geo_location.vessel_<MMSI>` | un segnaposto per ogni nave o altro oggetto AIS; il suo stato è la distanza dal centro dell'area (o da casa tua, per una nave seguita), in chilometri. Va e viene, e non ha un ID univoco |
| `sensor.ships_in_range` | uno per area: quante navi mostra, e se un limite ha tagliato l'elenco |
| `sensor.ais_station` | solo il tuo ricevitore: messaggi al minuto. I suoi attributi danno `vessels_heard` (negli ultimi 10 minuti), `farthest_km` e `farthest_mmsi` (dal centro dell'area), `last_message`, `udp_port`, `listening`, e `port_error` quando la porta non si apre. Si aggiorna ogni 30 secondi, quindi un ricevitore che smette di inviare mostra 0 |
| `sensor.watched_vessels` | solo navi seguite: quante delle navi del tuo elenco si sentono ora |

Gli attributi che cambiano a ogni aggiornamento restano fuori dalla
cronologia di Home Assistant, così il tuo database non cresce con loro:
`marker_photo`, `marker_links` e `marker_track` di ogni nave, e gli attributi
dei sensori che cambiano in fretta.

**Il tuo database.** Il registratore di Home Assistant salva una nuova riga
ogni volta che un'entità cambia, e una nave in movimento cambia a ogni
posizione che segnala. Sul nostro sistema di prova, un'area con 43 navi ha
scritto 27.109 righe in circa 30 ore, l'8,8% dell'intero database. Per
impostazione predefinita, il registratore tiene 10 giorni e fa pulizia ogni
notte alle 04:12 ora locale, quindi la crescita si stabilizza, ma a una
dimensione che forse non vuoi.

Una nave mantiene lo stesso ID entità, `geo_location.vessel_<MMSI>`, ogni
volta che compare, quindi un solo schema, `geo_location.vessel_*`, copre tutto
ciò che questa integrazione ha mai messo sulla mappa. Per tenerne solo
l'ultimo giorno:

1. **Impostazioni → Automazioni e scenari → Crea automazione → Crea una nuova
   automazione**.
2. Apri il menu a tre puntini, scegli **Modifica in YAML**, sostituisci tutto
   con questo e scegli **Salva**:

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

Se ometti `keep_days` (predefinito 0), tutte le loro righe se ne vanno in una
volta. Per non registrarne nessuna, metti lo schema sotto `recorder:` →
`exclude:` → `entity_globs:` in `configuration.yaml`; una scheda mappa
impostata per disegnare la cronologia (`history_start`) non avrà allora
nessuna traccia da disegnare. `sensor.ships_in_range` è un semplice numero e
costa poco tenerlo.

---

## Cosa invia e scarica

**Sulla tua posizione.** Il centro di ogni area è casa tua, a meno che tu non
lo sposti. Va solo alla fonte che hai scelto per quell'area: ad aisstream.io
come rettangolo attorno a un cerchio un po' più grande del tuo (il 10%,
almeno 1 km); a Digitraffic (Finlandia) come centro e quel raggio più grande;
a BarentsWatch (Norvegia) come quel cerchio più grande. Per le navi seguite, i
numeri MMSI del tuo elenco vanno ad aisstream.io. Il tuo ricevitore non invia
nulla da nessuna parte: Home Assistant ascolta e basta. Per le foto, i numeri
IMO delle navi sulla tua mappa vanno a Wikidata e Wikimedia Commons, senza
nulla su di te. Per fermare tutto questo, elimina l'area o la voce delle navi
seguite in **Impostazioni → Dispositivi e servizi → Live Track Ships**.
Nient'altro su di te viene inviato da nessuna parte.

**Quanto.**

* **aisstream.io**: una connessione per tutte le tue aree e una per le tue
  navi seguite, ciascuna tenuta aperta; le navi arrivano man mano che
  segnalano. Dopo un errore si riconnette dopo una pausa.
* **Digitraffic**: posizioni ogni 60 secondi e dati delle navi ogni
  15 minuti, solo per il tuo cerchio. Dopo un errore riprova al giro
  successivo.
* **BarentsWatch**: un flusso tenuto aperto per area. Se non arriva nulla per
  150 secondi, si riconnette.
* **Foto**: 20 numeri IMO alla volta, a 10 secondi di distanza, solo per le
  navi non richieste negli ultimi 30 giorni (14 se non c'era foto). Una
  richiesta fallita viene ripetuta più tardi.
* **Il tuo ricevitore**: non viene scaricato nulla.

---

## Aiutaci a farlo crescere

Live Track Ships sta ancora crescendo. Aggiungiamo fonti di dati e paesi man
mano che li troviamo, e vogliamo sapere cosa ti piacerebbe in seguito.

### Suggerire qualcosa

Manca il tuo paese o il tuo servizio AIS? Qualcosa è sbagliato, o difficile
da capire? Diccelo nel modo più facile per te:

* [**Compila un breve modulo**](https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues/new?template=it.yml)
  in italiano. Ti serve un account GitHub gratuito.
* **Scrivi un'email** a
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Non serve un account.

In entrambi i casi, ci aiuta se ci dici:

* cosa ti piacerebbe vedere, e in quale parte del mondo;
* un link a dove sono pubblicati i dati, se ne conosci uno (una pagina di
  dati aperti, un feed pubblico, il sito di un servizio): non è necessario,
  ma aiuta;
* la lingua del tuo Home Assistant, se il problema è la formulazione o una
  traduzione.

Scrivi in inglese o nella tua lingua, come ti è più facile.

### Aggiungerlo tu, con il nostro aiuto

Se vuoi aggiungere qualcosa tu, ti aiuteremo a farlo, dalla prima domanda
alla versione finita. Non serve essere sviluppatori per iniziare:

* **Una traduzione.** I testi della finestra di configurazione sono un breve
  elenco di frasi in un solo file di testo. Ti mostreremo quale file e quali
  righe.
* **Una nuova fonte di dati.** Dicci dove sono pubblicati i dati. Possiamo
  scrivere il codice insieme, o rivedere il tuo.
* **Provarlo dove vivi.** Installalo, guarda la tua parte della mappa e
  dicci cosa va bene e cosa no.
* **Una correzione di questo README.** Se un passo non corrispondeva a ciò
  che hai visto, dicci cosa hai visto.

[**Dicci cosa hai in mente**](https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues/new?template=it.yml)
o scrivi a
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
e ti risponderemo con i passi successivi.

---

## Lingue

Questo README: [English](README.md), [Deutsch](README.de.md),
[Français](README.fr.md), [Nederlands](README.nl.md),
[简体中文](README.zh-Hans.md), [Español](README.es.md), **Italiano**,
[Dansk](README.da.md) e [Kalaallisut](README.kl.md) (una breve bozza, inviata
per la revisione a Oqaasileriffik, la segreteria della lingua della
Groenlandia; fino ad allora la pagina danese è quella affidabile). Ogni
README tradotto è completo.

La finestra di configurazione e le opzioni compaiono nella lingua del tuo
Home Assistant quando è una di queste: English, Dansk, Deutsch, Español,
Français, Gaeilge, Íslenska, Italiano, Nederlands, Norsk Bokmål, Polski,
Português, Português (BR), Suomi, Svenska e 简体中文. Qualunque altra lingua
mostra l'inglese. Il groenlandese (kalaallisut) non è ancora una lingua di
Home Assistant; abbiamo chiesto a Home Assistant di aggiungerlo. Le etichette
proprie della scheda mappa (**Track**, **Details**) sono in inglese in tutte
le lingue.

Hai trovato un errore in una traduzione, o ti serve un'altra lingua? Diccelo
su <https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues>, o
[traducilo con il nostro aiuto](#aggiungerlo-tu-con-il-nostro-aiuto).

---

## Riconoscimenti e licenze

* **aisstream.io**: nessuna condizione pubblicata. <https://aisstream.io>
* **Fintraffic Digitraffic** (Finlandia): dati con licenza CC BY 4.0.
  <https://www.digitraffic.fi/en/terms-of-service/>
* **BarentsWatch** (Norvegia): dati con la licenza norvegese per i dati
  pubblici aperti (NLOD).
  <https://www.barentswatch.no/en/articles/api-terms-and-conditions/>
* **Il tuo ricevitore**: i tuoi dati.
* **Wikidata**: CC0. **Wikimedia Commons**: ogni foto con la propria licenza,
  mostrata con il fotografo e la licenza.
* **VesselFinder**: solo collegato; da lì non si scarica nulla.
* **EnforcementVessels**: ODbL 1.0.
  <https://github.com/StrausbergAutomationWorks/EnforcementVessels>

Cosa cambia questa integrazione: le unità vengono convertite, e si tengono
solo le navi dentro il tuo cerchio. Ogni entità nave, e il
`sensor.ships_in_range` di ogni area, porta un'`attribution` con il nome della
fonte; Home Assistant la mostra nei dettagli dell'entità. Se mostri questi
dati ad altri, per esempio su una plancia pubblica, tieni il riconoscimento
insieme ai dati e leggi le condizioni della fonte. Le righe di
riconoscimento esatte, e i riconoscimenti per le immagini delle navi, sono in
[ATTRIBUTION.md](ATTRIBUTION.md).

Nessuna di queste organizzazioni ha realizzato o approvato questa
integrazione.

**Codice**: MIT, in [LICENSE](LICENSE).

**Per gli sviluppatori:** le frasi AIS del tuo ricevitore sono decodificate
da [pyais](https://github.com/M0r13n/pyais) (MIT); Home Assistant installa da
solo `saw-livetrack` e `pyais` la prima volta che carica l'integrazione. I
test in `tests/` si eseguono ciascuno da solo con Python; alcuni richiedono
Home Assistant installato, e i test `*_live` richiedono le tue chiavi.

---

## Parole chiave

Home Assistant navi · Home Assistant AIS · tracciamento navi · localizzazione
navi · tracciamento barche · mappa del traffico marittimo · scheda mappa AIS ·
ricevitore AIS · NMEA · AIS-catcher · aisstream.io · Digitraffic ·
BarentsWatch · ship tracking · vessel tracker · Schiffsverfolgung · suivi des
navires · scheepvaart volgen · seguimiento de barcos · skibstrafik · 船舶追踪 ·
geo_location · scheda mappa · Lovelace · HACS · Marketplace · Live Track ·
LiveTrack · StrausbergAutomationWorks
