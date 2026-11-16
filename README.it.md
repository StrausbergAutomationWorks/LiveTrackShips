# Live Track Ships

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · **Italiano** · [Dansk](README.da.md) · [Kalaallisut](README.kl.md)

Navi, barche e altre imbarcazioni in tempo reale sulla mappa di Home
Assistant. Live Track Ships è un'integrazione di Home Assistant (custom
component, si installa dal Marketplace / HACS) che mostra i dati AIS delle navi
nell'area che scegli: dove si trova ciascuna, nome, velocità, rotta, tipo e
dimensioni quando la nave li trasmette. Ogni nave è un'entità `geo_location`
che si sposta sulla mappa a ogni nuova posizione. Il centro dell'area può
trovarsi ovunque nel mondo.

**Stato: 0.1.0, la prima versione.**

## Si vedono anche le imbarcazioni da diporto

L'integrazione mostra tutto ciò che la fonte invia e non si può filtrare
nulla. Un'imbarcazione da diporto con transponder AIS compare sulla mappa come
una nave da carico: nome, MMSI, nominativo radio e posizione con una precisione
di circa un metro. Una barca che lascia il transponder acceso all'ormeggio
resta sulla mappa all'ormeggio. L'AIS non ha una lista di esclusione. Per
vedere meno imbarcazioni da diporto, riduci il raggio.

## Fonti

Scegli una fonte per ogni area.

| Fonte | Copertura | Serve |
|---|---|---|
| aisstream.io | tutto il mondo, dove i volontari hanno ricevitori | una chiave API gratuita |
| Fintraffic Digitraffic | acque finlandesi e del Baltico | niente |
| BarentsWatch AIS Live | acque norvegesi | ID client e segreto gratuiti |

L'attributo `attribution` di ogni nave indica la sua fonte. Tutte le
attribuzioni: [ATTRIBUTION.md](ATTRIBUTION.md).

La copertura è buona dove ci sono ricevitori, e nessuna impostazione crea una
copertura che non c'è. Se nella tua area non vedi navi, forse mancano i
ricevitori, non le barche.

## Requisiti

- Home Assistant 2026.11 o successivo.
- aisstream.io: una chiave API gratuita da
  [aisstream.io](https://aisstream.io/account). aisstream consente tre
  connessioni per account e per indirizzo IP pubblico.
- BarentsWatch: ID client e segreto gratuiti. Inserisci l'ID client
  esattamente come è stato emesso.
- Digitraffic non richiede chiavi né account.

## Installazione

### Dal Marketplace

L'integrazione non è ancora nel catalogo del Marketplace. Aggiungila tramite
link:

1. **Impostazioni > Marketplace**, poi aggiungi da link.
2. Inserisci `StrausbergAutomationWorks/LiveTrackShips`. Se chiede il tipo,
   scegli **Integrazione**.
3. Installa **Live Track Ships**.
4. Riavvia Home Assistant. Il Marketplace offre il riavvio come riparazione in
   **Impostazioni > Sistema > Riparazioni**.

### A mano

1. Scarica il codice sorgente dell'[ultima
   versione](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest).
2. Copia la cartella `custom_components/live_track_ships` nella cartella
   `custom_components` della directory di configurazione di Home Assistant.
3. Riavvia Home Assistant.

## Configurazione

**Impostazioni > Dispositivi e servizi > Aggiungi integrazione > Live Track
Ships.** Scegli la fonte, inserisci la chiave se serve, trascina il segnaposto
sulla mappa fino all'acqua che vuoi osservare e scegli il raggio (da 1 a 500
km, 50 predefinito). Ogni area è una voce a sé. La finestra appare in italiano
quando Home Assistant è in italiano.

Nelle impostazioni di un'area puoi spostare il centro con lo stesso
segnaposto; l'area viene rinominata e ricaricata. Tutte le aree insieme
mostrano al massimo 2.500 navi; un cursore nelle impostazioni può solo
abbassare questo limite. Usalo su una macchina lenta.

## Navi che meritano un'immagine tutta loro

La maggior parte delle navi è disegnata secondo il tipo. Alcune hanno
un'immagine propria: yacht reali e di Stato, e barche famose come i battelli
turistici, i taxi d'acqua e i battelli antincendio di Chicago. Conosci una nave
che ne meriti una, in qualsiasi parte del mondo? Apri una issue su
<https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues> con nome e
numero MMSI o IMO, e una foto o un link se li hai.

Hai trovato un errore importante in questa traduzione o nella finestra in
italiano? Segnalacelo allo stesso indirizzo.

## Parte di Live Track

Live Track è un insieme di integrazioni di Home Assistant, una per ogni tipo di
cosa che si muove, e tutte disegnano sulla stessa mappa
([LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
installata con l'integrazione). Pubblicate:
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft),
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
[Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail),
[Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail)
e Live Track Ships. Ognuna funziona da sola.

## Dati e licenza

Le navi vengono lette mentre l'integrazione è in funzione, direttamente dalla
fonte scelta; questo repository non contiene dati di quelle fonti. Codice: MIT.

Non affiliata con aisstream.io, Fintraffic, BarentsWatch né con alcuna
autorità marittima. **Non per la navigazione né per evitare collisioni.** Tutti
i dettagli e le lingue: [README in inglese](README.md#languages).

## Parole chiave

Home Assistant AIS · navi sulla mappa · tracciamento navi · seguire le barche ·
traffico marittimo in tempo reale · mappa AIS · integrazione HACS
