# Live Track Ships

[English](README.md) · [Deutsch](README.de.md) · **Français** · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Kalaallisut](README.kl.md) · [Toutes les langues](#langues)

**Navires et bateaux pour Home Assistant, sur une seule carte.** Live Track
Ships affiche sur votre carte Home Assistant les navires, les bateaux et tout
ce qui émet l'AIS (le signal radio par lequel les navires disent où ils sont),
près de chez vous ou n'importe où dans le monde. Il suit aussi des navires
choisis où qu'ils aillent, et prévient vos automatisations quand un navire
entre dans votre zone ou en sort.

> **Live Track Ships est un module de Live Track**, une famille
> d'intégrations Home Assistant qui dessinent tout ce qui bouge, et la météo
> que cela traverse, sur une carte partagée : avions, navires, trains et
> météo. Installez-le seul ou à côté des autres modules
> ([liste ci-dessous](#les-autres-modules-de-live-track)).

> **En croissance, et ouvert aux idées.** Aujourd'hui, Live Track Ships couvre
> le monde entier là où des bénévoles font tourner des récepteurs, la Finlande
> et la Norvège avec plus de détail, et votre propre récepteur. Nous ajoutons
> d'autres sources de données et d'autres pays. Le vôtre manque ?
> [Proposez-le](#aidez-le-à-grandir), ou ajoutez-le vous-même : nous vous
> aiderons à le faire.

**État : 0.1.3, publié.** Dans le catalogue du Marketplace ([l'installer
ci-dessous](#installation-pas-à-pas)).

Œuvre originale de StrausbergAutomationWorks. Sans lien avec, ni approbation
de, aisstream.io, Fintraffic (Finlande), BarentsWatch (Norvège), Wikidata,
Wikimedia Commons, VesselFinder, MarineTraffic, un armateur ou une autorité
maritime.

> ⚠ **Ce n'est pas un système de sécurité.** Il affiche des données publiques,
> souvent vieilles de quelques secondes, parfois de quelques minutes, et
> seulement ce que des récepteurs captent. Il ne sert ni à la navigation, ni à
> l'évitement des collisions, ni à aucun autre usage opérationnel. Sur l'eau,
> utilisez votre propre AIS, votre radar, vos cartes et votre radio VHF.

---

## Sommaire

1. [Tout ce qu'il fait](#tout-ce-quil-fait)
2. [Où il fonctionne](#où-il-fonctionne)
3. [Les autres modules de Live Track](#les-autres-modules-de-live-track)
4. [Avant de commencer](#avant-de-commencer)
5. [Installation, pas à pas](#installation-pas-à-pas)
6. [Configuration, pas à pas](#configuration-pas-à-pas)
7. [Clés gratuites qui activent davantage, pas à pas](#clés-gratuites-qui-activent-davantage-pas-à-pas)
8. [Mettre la carte sur un tableau de bord](#mettre-la-carte-sur-un-tableau-de-bord)
9. [L'utiliser dans des automatisations](#lutiliser-dans-des-automatisations)
10. [Tout ce qui est sur la carte, en détail](#tout-ce-qui-est-sur-la-carte-en-détail)
11. [Toutes les entités qu'il crée](#toutes-les-entités-quil-crée)
12. [Ce qu'il envoie et télécharge](#ce-quil-envoie-et-télécharge)
13. [Aidez-le à grandir](#aidez-le-à-grandir)
14. [Langues](#langues)
15. [Crédits et licences](#crédits-et-licences)
16. [Mots-clés](#mots-clés)

---

## Tout ce qu'il fait

### Sur la carte, sans rien configurer

Vous ajoutez une **zone** : un centre et un rayon sur la carte, et une source
de données. Tout ce qui suit apparaît alors dans cette zone. Fintraffic
Digitraffic (Finlande) et votre propre récepteur ne demandent aucune clé ;
aisstream.io et BarentsWatch (Norvège) demandent une clé gratuite
([voir ci-dessous](#avec-votre-propre-clé-ou-compte-gratuit)).

| Quoi | Où | Source |
|---|---|---|
| **Navires** : cargos, pétroliers, ferries, remorqueurs, bateaux de pêche, bateaux de plaisance et voiliers, chacun avec sa propre image, tourné selon son cap | dans chaque zone | la source que vous choisissez |
| **Ce qui n'est pas un navire** : bouées d'engins de pêche, aides à la navigation, stations de base AIS, aéronefs de recherche et de sauvetage et balises de détresse | dans chaque zone, quand la source les envoie | la source que vous choisissez |
| **Photos et liens** : une photo du navire quand on en connaît une, et un lien vers le navire sur VesselFinder | chaque navire qui a un numéro IMO ou un MMSI | Wikidata et Wikimedia Commons |
| **Traces** : où un navire est passé ces dernières 24 heures, dessiné quand vous le demandez | chaque navire | gardé par votre propre Home Assistant |
| **Navires des garde-côtes engagés dans l'immigration**, dessinés aux couleurs des garde-côtes | partout où ils sont captés | la liste publique EnforcementVessels |
| **Arrivées et départs** : un événement pour vos automatisations quand un navire entre dans une zone ou en sort | dans chaque zone | calculé par votre propre Home Assistant |

### Avec votre propre clé ou compte gratuit

| Clé ou compte gratuit | Ce qu'il ajoute |
|---|---|
| Clé **aisstream.io** | des navires partout dans le monde là où des bénévoles font tourner des récepteurs ; et les **navires suivis** : des navires choisis, suivis où qu'ils soient, avec un événement quand l'un arrive, part, se tait ou change de destination |
| Compte **BarentsWatch** (Norvège) | des navires dans les eaux norvégiennes, Svalbard compris, avec le nom et le type à chaque position |

Chacun s'obtient en quelques minutes : [pas à pas ci-dessous](#clés-gratuites-qui-activent-davantage-pas-à-pas).

---

## Où il fonctionne

| Région | Ce que vous obtenez | Source | Ce qu'il faut |
|---|---|---|---|
| **Le monde entier** | des navires là où des bénévoles font tourner des récepteurs : bien près des côtes et des ports fréquentés, peu ou rien ailleurs | aisstream.io | une clé gratuite |
| **Europe** : Finlande et mer Baltique | des navires dans les eaux finlandaises et baltes, nouvelles positions chaque minute | Fintraffic Digitraffic (Finlande) | rien |
| **Europe** : Norvège | des navires dans les eaux norvégiennes, Svalbard compris, avec le nom et le type à chaque position | BarentsWatch (Norvège) | un compte gratuit |
| **Votre propre récepteur** : partout | tout ce que votre antenne capte, sans Internet | votre propre récepteur AIS | un récepteur qui envoie du NMEA par UDP |

Vous choisissez une source pour chaque zone. Les types d'objets qui
apparaissent, la fraîcheur des positions et le détail des données des navires
dépendent tous de cette source.

⚠ **La couverture est bonne là où il y a des récepteurs, et absente là où il
n'y en a pas.** Aucun réglage ne peut créer une couverture qui n'existe pas.
Mesuré le 2026-09-02 sur aisstream.io autour de Chicago (États-Unis) :
100 navires en 120 secondes sur les Grands Lacs, mais zéro navire en une heure
sur les canaux au sud de la ville, où des convois de barges circulent
pourtant : les services commerciaux les voient par satellite, ce que les
sources gratuites ne fournissent pas. **Aucun navire dans votre zone peut
vouloir dire aucun récepteur, pas aucun bateau.** Vérifiez que votre source
couvre vos eaux avant de conclure que quelque chose est cassé.

⚠ **Votre propre récepteur :**

* Une zone écoute sur un port. Deux récepteurs demandent deux ports.
* Tout ce que le récepteur capte dans votre cercle est affiché, aides à la
  navigation et stations de base comprises. Son capteur de station compte
  aussi ce qu'il capte hors du cercle.
* Une phrase NMEA ne porte pas de date : l'heure d'une position est donc
  l'heure où Home Assistant l'a reçue.
* Le taux de giration n'est pas affiché pour cette source.
* Jusqu'ici, c'est testé avec des phrases enregistrées envoyées par UDP, pas
  avec un récepteur. Si vous l'essayez avec le vôtre,
  [dites-nous comment cela s'est passé](#aidez-le-à-grandir).

Pas dans la liste ? [Dites-le-nous](#aidez-le-à-grandir). Là où quelqu'un
publie les données ouvertement, nous étudierons leur ajout.

---

## Les autres modules de Live Track

Live Track est un ensemble d'intégrations Home Assistant, une par type d'objet
en mouvement, toutes dessinées sur la même carte. Chacune fonctionne seule ;
ensemble, elles forment une seule image en direct. Elles partagent la carte et
une bibliothèque Python
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
donc en installer une autre n'ajoute aucune requête à une source qu'une autre
lit déjà.

| Module | Ce qu'il met sur la carte | État |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | les avions au-dessus de vous via l'ADS-B, avec routes et icônes par type | publié |
| **Live Track Ships** | navires et bateaux via l'AIS, près de chez vous ou n'importe où (ce module) | publié |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | trains de banlieue en Amérique du Nord, en Europe et en Australie | publié |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | trains intercités et grandes lignes en Amérique du Nord, en Europe et en Australie | publié |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | avions et navires des services d'immigration et des forces de l'ordre fédérales, d'après des listes publiques | publié |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | météo, tempêtes et risques naturels | publié |
| Live Track Stations | tableaux des départs et rappels « il est temps de partir » pour chaque gare | prévu |
| Live Track Satellites | les satellites qui passent au-dessus de vous | prévu |
| Live Track Freight Trains | trains de marchandises et de travaux là où les chemins de fer les publient | prévu |
| Live Track Transit | bus urbains, tramways, ferries et métros | prévu |
| Live Track Intercity Buses | autocars interurbains et régionaux | prévu |
| Live Track Commuter Buses | bus de banlieue | prévu |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | la carte partagée sur laquelle dessine chaque module | publiée, installée avec chaque module |

Tout est gratuit et libre. Rien n'est réservé aux sponsors.

---

## Avant de commencer

* **Home Assistant** 2026.11 ou plus récent.
* **Le Marketplace** (HACS) dans votre Home Assistant, pour l'installer et le
  mettre à jour facilement. Sans lui, vous pouvez copier les fichiers à la
  main.
* **Un accès à Internet** pour Home Assistant, pour les sources en ligne et
  les photos. Votre propre récepteur fonctionne sans.
* **Une source de données.** Digitraffic (Finlande) et votre propre récepteur
  ne demandent aucun compte. aisstream.io et BarentsWatch (Norvège) demandent
  une clé gratuite
  ([pas à pas](#clés-gratuites-qui-activent-davantage-pas-à-pas)).
* **Facultatif : votre propre récepteur AIS.** Le récepteur, ou le programme
  qui le décode, envoie des phrases NMEA (`!AIVDM`) par UDP à l'adresse de
  votre Home Assistant, sur le même réseau. Dans AIS-catcher, c'est
  `-u <address> <port>` ; dans rtl-ais, `-h <address> -P <port>` ; OpenCPN et
  Signal K l'ajoutent comme connexion de sortie UDP. Un récepteur qui se
  branche en USB, comme un dAISy, a besoin de l'un de ces programmes pour
  transmettre ses phrases.
* **Facultatif : auto-entities** depuis le Marketplace, pour mettre les
  marqueurs sur la carte (voir
  [Mettre la carte sur un tableau de bord](#mettre-la-carte-sur-un-tableau-de-bord)).
* Rien à payer. Aucun compte n'est nécessaire pour Digitraffic ni pour votre
  propre récepteur ; les clés gratuites ne servent que pour aisstream.io et
  BarentsWatch.

---

## Installation, pas à pas

### Depuis le Marketplace (recommandé)

1. Dans Home Assistant, ouvrez **Paramètres → Marketplace** (HACS).
2. Recherchez **Live Track Ships** et ouvrez-le.
3. Choisissez **Télécharger** (ou **Installer**).
4. **Redémarrez Home Assistant** : **Paramètres → Système → Corrections**
   propose le redémarrage, ou utilisez **Paramètres → Système → Redémarrer**.

Si la recherche ne le trouve pas, ajoutez-le par son lien : choisissez **Ajouter
depuis un lien** (ou le menu à trois points → **Dépôts personnalisés**),
saisissez `StrausbergAutomationWorks/LiveTrackShips`, choisissez **Intégration**
si le type est demandé, puis reprenez à l'étape 3.

Le Marketplace propose ensuite chaque nouvelle version comme mise à jour.

### À la main

1. Téléchargez le code source de la
   [dernière version](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest).
2. Copiez son dossier `custom_components/live_track_ships` dans le dossier
   `custom_components` de votre dossier de configuration Home Assistant
   (créez `custom_components` s'il n'existe pas).
3. Redémarrez Home Assistant.

---

## Configuration, pas à pas

1. Ouvrez **Paramètres → Appareils et services**.
2. Choisissez **Ajouter une intégration** (en bas à droite) et cherchez
   **Live Track Ships**.
3. Choisissez **Tous les navires d'une zone**. (L'autre choix, **Des navires
   choisis, où qu'ils soient**, suit une liste de navires partout : voir
   [Navires suivis](#navires-suivis--des-navires-choisis-partout).)
4. **Source des données** : choisissez-en une. En cas de doute : en Finlande,
   Fintraffic Digitraffic, qui ne demande aucune clé ; en Norvège,
   BarentsWatch ; partout ailleurs, aisstream.io.
5. **Clé API** (aisstream.io), ou **ID client** et **Secret client**
   (BarentsWatch) : collez-les
   ([comment les obtenir](#clés-gratuites-qui-activent-davantage-pas-à-pas)).
   Une zone que vous avez déjà configurée les remplit pour vous.
6. **Port UDP (votre propre récepteur)** : seulement pour votre propre
   récepteur. Saisissez le port vers lequel il envoie, de 1024 à 65535.
   Laissez 10110 si vous ne l'avez pas changé.
7. **Centre** : faites glisser le marqueur au milieu des eaux que vous voulez
   surveiller. Il part de votre domicile.
8. **Rayon (km)** : de 1 à 500 km (0,6 à 310 miles). En cas de doute, gardez
   50 km (31 miles).
9. **Nombre maximal de navires suivis** : gardez 1 000, sauf si votre machine
   est petite.
10. Choisissez **Valider**.

C'est tout. Les navires apparaissent en une minute ou deux, au rythme où la
source les envoie. Les types et les tailles se complètent dans les minutes
suivantes. Chaque zone est une entrée, intitulée *Ships near <latitude>,
<longitude>*. Ajoutez d'autres zones de la même façon.

* Une même source ne peut pas surveiller deux fois le même centre.
* Quand au moins 5 % d'un cercle BarentsWatch se trouve hors des eaux que
  BarentsWatch publie, la boîte de dialogue indique la proportion avant de
  créer la zone. Choisissez **Valider** pour garder ce cercle malgré tout.

### Modifier ce qu'il affiche : les options

Ouvrez **Paramètres → Appareils et services → Live Track Ships → Configurer**
(la roue dentée) sur la zone à modifier. Chaque option, en termes simples :

| Option | Ce qu'elle fait | Par défaut |
|---|---|---|
| **Centre** | déplace la zone ; elle est renommée selon sa nouvelle position et rechargée | votre domicile |
| **Rayon (km)** | jusqu'à quelle distance du centre les navires sont affichés, de 1 à 500 km (0,6 à 310 miles) | 50 km (31 miles) |
| **Nombre maximal de navires suivis** | une limite de sécurité pour cette zone, de 1 à 5 000 ; s'il y en a plus, les plus proches sont gardés | 1 000 |
| **Nombre maximal de navires sur la carte, toutes les entrées Live Track Ships ensemble** | le plafond pour toutes vos zones ensemble, de 100 à 2 500 ; baissez-le sur une petite machine ; c'est le réglage le plus bas de toutes les zones qui s'applique | 2 500 |
| **Port UDP (votre propre récepteur)** | le port vers lequel votre récepteur envoie ; le changer recharge la zone | 10110 |

Le nombre de navires dans un cercle dépend bien plus des eaux que de sa
taille. Lors des tests, un cercle de 50 km (31 miles) contenait environ
4 navires au-dessus de Chicago (États-Unis) et environ 340 au-dessus du Solent
(Angleterre) : le même rayon, environ 80 fois plus de trafic. Quand une limite
coupe la liste, le `sensor.ships_in_range` de la zone l'indique.

---

## Clés gratuites qui activent davantage, pas à pas

Toutes sont gratuites et personnelles : chaque personne qui installe Live
Track Ships obtient les siennes. Collez chacune dans la boîte de dialogue de
configuration quand vous ajoutez une zone (étape 5 de la
[configuration](#configuration-pas-à-pas)).

### aisstream.io (navires et navires suivis, le monde entier)

1. Ouvrez <https://aisstream.io/account> et connectez-vous. (Le lien
   **API keys** en haut d'aisstream.io ouvre la même page.)
2. Créez-y une nouvelle clé API.
3. Copiez la clé tout de suite : aisstream.io ne l'affiche qu'une fois.
4. Collez-la dans **Clé API**.

⚠ aisstream.io autorise trois connexions par compte et trois par adresse
Internet publique. Live Track Ships en utilise au plus deux : une pour toutes
vos zones, et une pour vos navires suivis, qu'il partage avec Live Track SALT
si celui-ci est installé avec la même clé. Si d'autres programmes utilisent la
même clé ou la même connexion Internet, comptez-les aussi.

### BarentsWatch (navires dans les eaux norvégiennes, Norvège)

1. Ouvrez <https://www.barentswatch.no/minside/> et créez un utilisateur, ou
   connectez-vous.
2. Sous **API access (for developers)** (*API-tilgang (for utviklere)*),
   choisissez **New Client** (*Ny klient*).
3. Choisissez le client AIS, pas le client API.
4. Copiez l'**ID client**. Il ressemble à
   `your.email@example.com:live_track_ships`. Collez-le exactement tel quel
   dans **ID client**.
5. Copiez le **secret client** dans **Secret client**. Il n'est affiché qu'une
   fois ; si vous ne l'avez pas gardé, générez-en un nouveau.

---

## Mettre la carte sur un tableau de bord

La carte est [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
la carte sur laquelle dessine chaque module Live Track. **Elle est installée
avec Live Track Ships** : rien à télécharger, rien à copier, aucune ressource
à ajouter.

1. Ouvrez un tableau de bord, choisissez le crayon (**Modifier le tableau de
   bord**), puis **Ajouter une carte**.
2. Faites défiler jusqu'en bas et choisissez **Manuel**.
3. Collez ceci, et choisissez **Enregistrer** :

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

Cette forme nécessite
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities) depuis
le Marketplace. Si d'autres modules Live Track sont installés, ajoutez un
filtre `- domain: geo_location` de plus pour chacune de leurs sources
(`live_track_aircraft`, `live_track_weather` et ainsi de suite).

**Sans auto-entities :** LiveTrackMapCard peut choisir elle-même ce qu'elle
affiche, avec `entity_filter`. Collez plutôt ceci ; rien d'autre à installer :

```yaml
type: custom:live-track-map-card
entity_filter:
  include:
    - domain: geo_location
      attributes:
        source: live_track_ships
```

Les autres modules Live Track vont dans `entity_filter` de la même façon : une
règle `- domain: geo_location` de plus pour chaque source.

**Sur la carte :**

* Chaque navire est dessiné avec sa propre image, tourné selon son cap, et
  glisse entre ses positions signalées en suivant l'eau plutôt qu'en coupant
  par la terre.
* **Pointez** un navire pour voir son nom, et sa photo quand il y en a une.
  **Cliquez** dessus pour sa photo, ses liens, **Track** et **Details**
  ([Photos et liens](#photos-et-liens), [Traces](#traces)).
* La **carte de filtre** (`custom:live-track-map-filter-card`) masque les
  types de navires que vous décochez
  ([Masquer des types de navires](#masquer-des-types-de-navires)).

Si les ressources de vos tableaux de bord sont définies en YAML
(`lovelace: resource_mode: yaml`), rien ne peut être enregistré pour vous : un
problème dans **Corrections** donne alors la ligne exacte à ajouter. Une carte
que vous avez installée vous-même depuis le Marketplace n'est pas touchée. Si
les fichiers de l'intégration sont supprimés alors que ses zones sont encore
configurées, et qu'aucun autre module Live Track n'est installé, supprimez
vous-même la ligne de la carte dans **Paramètres → Tableaux de bord →
Ressources**. Toute autre carte qui affiche les entités `geo_location` montre
aussi les navires, sans leurs images.

---

## L'utiliser dans des automatisations

Tout est une entité ou un événement Home Assistant ordinaire, donc l'éditeur
d'automatisations fonctionne avec, sans code.

**Une notification quand un navire de plus de 150 m (490 pieds) entre dans
votre zone :**

1. **Paramètres → Automatisations et scènes → Créer une automatisation →
   Créer une nouvelle automatisation**.
2. **Quand** : **Ajouter un déclencheur**, cherchez **Événement manuel reçu**,
   et saisissez comme **Type d'événement** `live_track_ships_entry`.
3. **Et si** : **Ajouter une condition** → **Modèle**, et saisissez ce
   **Modèle de valeur** : `{{ trigger.event.data.length_m | default(0) > 150 }}`
4. **Alors faire** : **Ajouter une action**, cherchez l'action de
   notification de votre téléphone (elle porte le nom de votre téléphone), et
   saisissez ce message :

   ```text
   {{ trigger.event.data.name | default('Un navire') }}, {{ trigger.event.data.length_m }} m, à {{ trigger.event.data.distance_km }} km
   ```

5. **Enregistrer**.

**Autres idées :** une lumière qui s'allume quand le ferry du soir arrive dans
votre port en Norvège ; un message quand le bateau d'un proche, un navire
suivi, rentre en Finlande ; une notification quand le paquebot que vous
attendez arrive à Sydney (Australie) ; le nombre de navires dans votre port
sur un tableau de bord, depuis `sensor.ships_in_range`.

**Les événements de zone.** Chaque zone déclenche `live_track_ships_entry`
quand un navire entre dans son cercle et `live_track_ships_exit` quand il en
sort. Chaque navire est annoncé ; votre automatisation choisit ceux qui
comptent. Les champs portent les mêmes noms et unités que les attributs du
navire, et omettent ce que la source n'a pas envoyé :

| Champ | Ce qu'il contient |
|---|---|
| `area_id`, `area` | l'ID de l'entrée de configuration de la zone et son titre |
| `identity` | le MMSI |
| `name`, `call_sign`, `imo` | s'ils sont envoyés |
| `object_kind` | `vessel`, `net_buoy`, `aton`, `base_station`, `sar_aircraft` ou `distress_beacon` |
| `ship_type`, `ship_type_label`, `length_m`, `beam_m`, `draught_m`, `destination`, `nav_status` | navires seulement, s'ils sont envoyés |
| `speed_kmh`, `course_deg`, `heading_deg` | s'ils sont envoyés |
| `latitude`, `longitude`, `distance_km`, `bearing_from_centre_deg`, `last_seen` | où il a été capté, depuis le centre de la zone |
| `entity_id` | entrée seulement : `geo_location.vessel_<MMSI>`, quand le navire est sur la carte |
| `reason` | sortie seulement : `left` (capté hors du cercle) ou `silent` (pas capté depuis un moment, donc peut-être encore là) |

⚠ Quatre choses à savoir :

* **Une arrivée n'est annoncée que si le navire a d'abord été capté hors du
  cercle.** Un navire capté d'abord à l'intérieur y était peut-être depuis le
  début : après un redémarrage, les sources continuent pendant de longues
  minutes de livrer des navires qui n'ont pas bougé. Un navire que les
  récepteurs ont manqué à l'entrée, ou un navire qui allume son transpondeur à
  l'intérieur, n'est donc pas annoncé.
* **Un départ capté à l'extérieur est toujours annoncé**, même pour un navire
  qui était là avant le démarrage de Home Assistant. Un navire qui se tait
  n'est annoncé comme partant (`reason: silent`) que si son arrivée l'a été.
* **Une sortie attend 2 minutes.** Un navire qui revient plus tôt, en longeant
  le bord du cercle, n'est pas annoncé comme partant puis arrivant à nouveau.
* **Des détails peuvent manquer à l'arrivée.** Le nom, le type et la taille
  arrivent dans un message plus lent que la position. Un navire capté pour la
  première fois peut arriver avec une position et rien d'autre.

Deux zones sur les mêmes eaux déclenchent chacune leurs propres événements.
Les limites sur le nombre de navires dessinés ne font jamais entrer ni sortir
un navire.

**L'événement des navires suivis.**
[Les navires suivis](#navires-suivis--des-navires-choisis-partout) déclenchent
un événement, `live_track_ships_watched`, dont le `change` dit ce qui s'est
passé :

| `change` | Quand |
|---|---|
| `arrived` | le navire se déclare amarré ou au mouillage, ou, sans statut, reste sous 3,7 km/h (2 nœuds) |
| `departed` | il fait de nouveau route |
| `silent` | pas capté depuis 30 minutes (6 heures s'il est amarré ou au mouillage) ; il quitte la carte, et est peut-être encore là |
| `heard` | capté de nouveau après `silent` |
| `destination` | l'équipage a changé sa destination ; `destination_previous` contient l'ancienne |

Les données contiennent `watch_id`, `watch`, `identity`, votre `label`, et les
mêmes champs de navire que les événements de zone, avec la distance et le
relèvement depuis votre domicile. L'arrivée et le départ attendent que le
nouvel état ait tenu 5 minutes selon l'horloge du navire lui-même, pour qu'un
bateau qui dérive lentement ne bascule pas sans cesse. Rien n'est annoncé à
partir de la première position d'un navire après un redémarrage : elle sert de
point de départ. Les destinations sont saisies par l'équipage et souvent
périmées.

---

## Tout ce qui est sur la carte, en détail

L'AIS (Automatic Identification System, système d'identification automatique)
est une émission radio VHF par laquelle les navires annoncent leur position,
leur identité et leur voyage aux autres navires et à la terre. C'est
l'équivalent maritime de ce que les avions envoient en ADS-B. Les navires de
commerce doivent en être équipés ; beaucoup de bateaux de plaisance l'ont par
choix, souvent sous forme d'un appareil de classe B moins puissant. L'AIS est
émis en clair : quiconque a un récepteur peut le capter, et des services
publics le relaient. **Live Track Ships affiche tout ce que la source
envoie.** Rien n'est filtré, et aucun réglage ne cache une catégorie à Home
Assistant.

### Navires

Chaque navire est un marqueur dont l'état est sa distance au centre de la
zone, en kilomètres. La plupart des navires sont dessinés selon leur type :
cargo, pétrolier, ferry, remorqueur, etc. Certains ont leur propre image :
yachts royaux et d'État, et bateaux connus comme les bateaux d'excursion, les
bateaux-taxis et les bateaux-pompes d'une ville. Vous connaissez un navire qui
en mérite une, n'importe où dans le monde ? [Proposez-le](#aidez-le-à-grandir),
avec son nom et son numéro MMSI ou IMO, et une photo ou un lien si vous en
avez un.

Pour qu'un navire disparaisse dès qu'il part, chaque source en ligne est
interrogée sur un anneau un peu plus large que votre cercle (10 %, au moins
1 km), et votre propre récepteur envoie tout ce qu'il capte. Seuls les navires
à l'intérieur de votre cercle sont gardés : un navire capté à l'extérieur
quitte la carte aussitôt. Un navire qui n'est plus capté disparaît après un
moment de silence. Un navire qui n'apparaît plus n'est pas forcément parti :
aucune de ces sources ne promet de livrer chaque message.

⚠ **Le type de navire manque souvent, surtout pour les petits bateaux.** La
position et le nom arrivent avec presque chaque message. Le type et la taille
arrivent dans un message à part, plus lent, que beaucoup d'appareils de
classe B envoient rarement. Attendez-vous à ce que beaucoup de navires, dont
la plupart des petits bateaux, n'aient ni type ni taille, et à ce que tous
aient peu de détails pendant plusieurs minutes après un redémarrage de Home
Assistant. Ce sont les données, pas une panne. Les types et tailles captés une
fois sont gardés d'un redémarrage à l'autre.

Les attributs d'un navire comprennent son nom, son MMSI, son indicatif
d'appel, sa vitesse, sa route, son cap, sa longueur, sa largeur, son type, sa
destination, `object_kind`, `last_seen` et `attribution`, chacun seulement si
la source l'a envoyé. Un navire vu par deux zones est une seule entité.

### Bateaux privés et voiliers

Un bateau de plaisance qui émet l'AIS apparaît sur votre carte exactement
comme un cargo. Selon ce que le bateau émet, son entité peut contenir :

* son **nom**, qui est aussi l'étiquette dessinée sur la carte ;
* son **MMSI** et son **indicatif d'appel radio**, tous deux permanents et
  consultables publiquement ;
* sa **position** à un mètre près environ, sa position précédente, et le
  moment où chacune a été captée ;
* sa vitesse, sa route et son cap, ainsi que sa longueur, sa largeur et son
  type, s'ils sont envoyés.

Un bateau qui laisse son transpondeur allumé au ponton reste sur la carte à
son poste d'amarrage tant qu'il émet. Quiconque peut ouvrir votre carte peut
aussi appuyer sur **Track** pour un tel bateau et voir où il est allé ces
dernières 24 heures (ou la durée que vous réglez), son poste d'amarrage
compris.

Il n'existe pas de liste d'exclusion pour l'AIS, comme il en existe pour les
avions, et cette intégration n'en invente pas. Si vous voulez moins de bateaux
privés sur votre carte, réduisez le rayon.

### Ce qui n'est pas un navire

Chaque entité porte `object_kind` : `vessel`, `net_buoy` (bouée d'engin de
pêche), `aton` (aide à la navigation : bouée, balise ou phare),
`base_station` (une station AIS à terre), `sar_aircraft` (un aéronef de
recherche et de sauvetage) ou `distress_beacon`. La plupart se distinguent
par le format d'identité que leur attribue l'Union internationale des
télécommunications (UIT). Pas les bouées d'engins de pêche : elles émettent
avec des identités de type navire, et sont donc reconnues à leur nom d'usine
(FISHING BOUY, NET MARK, BUOY) et à l'absence de longueur émise.

Tout ce qui n'est pas un navire est affiché sans type, taille ni statut de
navigation. Les bouées d'engins de pêche dérivent avec leurs lignes : elles
gardent leur vitesse et leur route, et sont dessinées comme un poisson pointé
dans le sens de leur dérive.

Ce qui apparaît dépend de la source. Mesuré un soir :

| Source | Bouées d'engins de pêche | Aéronefs de recherche et de sauvetage | Aides à la navigation, stations de base |
|---|---|---|---|
| BarentsWatch | oui | oui | aucune vue |
| Digitraffic | aucune vue | oui | aucune vue |
| aisstream.io | aucune vue | aucun vu | aucune vue |
| Votre propre récepteur | ce qu'il capte | ce qu'il capte | ce qu'il capte |

aisstream.io n'a livré que des positions et des données de navires, aussi
bien sur les Grands Lacs (Amérique du Nord) que sur les mêmes eaux
norvégiennes et danoises où BarentsWatch montre les bouées.

### Navires des garde-côtes engagés dans l'immigration

Un navire de la liste publique
[EnforcementVessels](https://github.com/StrausbergAutomationWorks/EnforcementVessels)
(navires des garde-côtes des États-Unis employés dans l'immigration) est
dessiné aux couleurs des garde-côtes, avec le nom et l'agence tirés de la
liste, partout où il est capté.

### Navires suivis : des navires choisis, partout

En plus des zones, vous pouvez suivre une liste de navires où qu'ils soient :
le bateau d'un proche, un ferry que vous prenez, un paquebot qui rentre. Il
faut une clé aisstream.io, et il y a une seule liste de ce genre par Home
Assistant.

1. Ouvrez **Paramètres → Appareils et services**, choisissez **Ajouter une
   intégration** et cherchez **Live Track Ships**.
2. Choisissez **Des navires choisis, où qu'ils soient**.
3. **Clé API** : la clé d'une zone que vous avez déjà configurée est remplie.
4. **Navires** : un navire par ligne, son MMSI à 9 chiffres, puis un nom à
   vous si vous le souhaitez :

   ```text
   244650000 Le bateau de papa
   366999999 Le ferry
   ```

5. Choisissez **Valider**.

Au plus 100 navires. aisstream.io suit au plus 200 MMSI par clé, et
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
s'il est installé avec la même clé, en utilise une partie. Une liste qui
dépasserait est refusée au chargement de l'entrée, avec la raison. Pour
modifier la liste, ouvrez **Configurer** sur l'entrée.

Un navire suivi est dessiné sur la carte comme les autres, partout où il est
capté, et son état est sa distance à votre domicile. Une zone qui l'affiche
déjà le garde : un navire, un marqueur. L'entrée ajoute
`sensor.watched_vessels` : combien des navires de la liste sont captés en ce
moment. Son attribut `vessels` les énumère tous, avec leur nom et leur dernier
état connu. Son événement est décrit dans
[L'utiliser dans des automatisations](#lutiliser-dans-des-automatisations).

### Photos et liens

Quand un navire envoie un numéro IMO et que Wikidata connaît une photo de ce
navire sur Wikimedia Commons, le navire porte `marker_photo`. La carte affiche
la photo quand vous pointez le navire, avec le photographe et la licence ; un
clic l'ouvre en plus grand, avec des liens vers la page de la photo et vers sa
licence. Chaque navire qui a un numéro IMO ou un MMSI porte aussi
`marker_links`, un lien vers le navire sur VesselFinder. Le bouton **Details**
de la fenêtre ouvre la boîte de dialogue habituelle du navire.

Votre Home Assistant interroge lui-même Wikidata et Commons, 20 numéros IMO à
la fois, à dix secondes d'intervalle, et garde chaque réponse 30 jours
(14 jours quand il n'y a pas de photo) dans `.storage/saw_vessel_photos.json`.
Comptez une photo pour environ un navire sur dix : sur notre système de test,
49 numéros IMO sur 521 en avaient une.

⚠ Une photo peut montrer le navire sous un ancien nom : le numéro IMO
appartient à la coque et la suit quand le navire est rebaptisé.

### Traces

Chaque navire porte aussi `marker_track`. Cliquez sur un navire et appuyez sur
**Track** dans sa fenêtre : la carte dessine où il est passé, en une ligne qui
se termine au navire, et la ligne s'allonge pendant que vous regardez.
**Hide track** l'enlève. Rien n'est dessiné tant que vous ne le demandez pas,
pour qu'un port fréquenté ne disparaisse pas sous les lignes.

La trace ne contient que les positions que le navire a signalées pendant qu'il
était sur votre carte, réduites à une tous les 25 m (82 pieds) ou toutes les
10 minutes, et jamais deux en moins de 30 secondes. Votre Home Assistant la
garde en mémoire et l'enregistre dans `.storage/saw_vessel_tracks.json`, donc
elle survit à un redémarrage. Elle couvre les dernières 24 heures. Pour en
garder plus ou moins :

1. Ouvrez **Paramètres → Outils → Actions**.
2. Choisissez l'action **Live Track Ships: Définir la durée de la trace**.
3. Saisissez **Heures**, de 1 à 168 (une semaine), et choisissez **Effectuer
   une action**.

Cela s'applique à toutes les zones à la fois ; un réglage plus court supprime
aussitôt les positions plus anciennes.

⚠ La trace commence vide lors d'une première installation. Un navire qui a
quitté la zone ou s'est tu a un trou, dessiné comme une ligne droite entre les
positions de part et d'autre.

### Masquer des types de navires

Chaque navire porte `marker_group`, `marker_group_label` et
`marker_group_order` : l'un de treize groupes (cargo ; pétrolier ; passagers
et ferry ; pêche ; plaisance et voile ; remorqueur, pilote et service
portuaire ; administration, recherche et sauvetage et forces de l'ordre ;
grande vitesse et autres ; type non envoyé ; bouées d'engins de pêche ; aides
à la navigation ; stations de base ; aéronefs de recherche et de sauvetage).
La carte de filtre de la carte, `custom:live-track-map-filter-card`, énumère
les groupes avec leur nombre sur la carte, et masque ceux que vous décochez.
Placez-la sur n'importe quelle vue du tableau de bord. Votre choix n'est gardé
que dans ce navigateur.

Le masquage n'a lieu que sur la carte : l'intégration compte toujours chaque
navire et déclenche ses événements pour chaque navire. Une balise de détresse
n'a pas de groupe, donc elle n'est jamais masquée.

---

## Toutes les entités qu'il crée

| Entité | Ce que c'est |
|---|---|
| `geo_location.vessel_<MMSI>` | un marqueur pour chaque navire ou autre objet AIS ; son état est la distance au centre de la zone (ou à votre domicile, pour un navire suivi), en kilomètres. Il va et vient, et n'a pas d'identifiant unique |
| `sensor.ships_in_range` | un par zone : combien de navires elle affiche, et si une limite a coupé la liste |
| `sensor.ais_station` | votre propre récepteur seulement : messages par minute. Ses attributs donnent `vessels_heard` (sur les 10 dernières minutes), `farthest_km` et `farthest_mmsi` (depuis le centre de la zone), `last_message`, `udp_port`, `listening`, et `port_error` quand le port ne peut pas être ouvert. Il se met à jour toutes les 30 secondes, donc un récepteur qui n'envoie plus rien affiche 0 |
| `sensor.watched_vessels` | navires suivis seulement : combien des navires de votre liste sont captés en ce moment |

Les attributs qui changent à chaque mise à jour sont tenus hors de
l'historique de Home Assistant, pour que votre base de données ne grossisse
pas avec eux : `marker_photo`, `marker_links` et `marker_track` de chaque
navire, et les attributs des capteurs qui changent vite.

**Votre base de données.** L'enregistreur de Home Assistant stocke une
nouvelle ligne chaque fois qu'une entité change, et un navire en mouvement
change à chaque position qu'il signale. Sur notre système de test, une zone de
43 navires a écrit 27 109 lignes en environ 30 heures, 8,8 % de toute la base.
Par défaut, l'enregistreur garde 10 jours et fait le ménage chaque nuit à
04:12 heure locale : la croissance se stabilise, mais à une taille que vous ne
voulez peut-être pas.

Un navire garde le même ID d'entité, `geo_location.vessel_<MMSI>`, à chaque
apparition, donc un seul motif, `geo_location.vessel_*`, couvre tout ce que
cette intégration a jamais mis sur la carte. Pour n'en garder que le dernier
jour :

1. **Paramètres → Automatisations et scènes → Créer une automatisation →
   Créer une nouvelle automatisation**.
2. Ouvrez le menu à trois points, choisissez **Modifier en YAML**, remplacez
   tout par ceci, et choisissez **Enregistrer** :

```yaml
alias: Réduire l'historique des navires
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

Si vous omettez `keep_days` (0 par défaut), toutes leurs lignes partent d'un
coup. Pour n'en enregistrer aucune, mettez le motif sous `recorder:` →
`exclude:` → `entity_globs:` dans `configuration.yaml` ; une carte réglée pour
dessiner l'historique (`history_start`) n'a alors plus de tracé à dessiner.
`sensor.ships_in_range` est un simple nombre, peu coûteux à garder.

---

## Ce qu'il envoie et télécharge

**À propos de votre position.** Le centre de chaque zone est votre domicile,
sauf si vous le déplacez. Il ne part que vers la source choisie pour cette
zone : vers aisstream.io sous forme d'un rectangle autour d'un cercle un peu
plus grand que le vôtre (10 %, au moins 1 km) ; vers Digitraffic (Finlande)
sous forme du centre et de ce rayon plus grand ; vers BarentsWatch (Norvège)
sous forme de ce cercle plus grand. Pour les navires suivis, les numéros MMSI
de votre liste partent vers aisstream.io. Votre propre récepteur n'envoie rien
nulle part : Home Assistant ne fait qu'écouter. Pour les photos, les numéros
IMO des navires de votre carte partent vers Wikidata et Wikimedia Commons,
sans rien sur vous. Pour arrêter tout cela, supprimez la zone ou l'entrée des
navires suivis dans **Paramètres → Appareils et services → Live Track Ships**.
Rien d'autre vous concernant n'est envoyé nulle part.

**Combien.**

* **aisstream.io** : une connexion pour toutes vos zones et une pour vos
  navires suivis, chacune gardée ouverte ; les navires arrivent au fil de
  leurs messages. Après une erreur, il se reconnecte après une pause.
* **Digitraffic** : positions toutes les 60 secondes et données des navires
  toutes les 15 minutes, pour votre cercle seulement. Après une erreur, il
  réessaie au tour suivant.
* **BarentsWatch** : un flux gardé ouvert par zone. Si rien n'arrive pendant
  150 secondes, il se reconnecte.
* **Photos** : 20 numéros IMO à la fois, à 10 secondes d'intervalle, seulement
  pour les navires non demandés ces 30 derniers jours (14 quand il n'y avait
  pas de photo). Une requête qui échoue est refaite plus tard.
* **Votre propre récepteur** : rien n'est téléchargé.

---

## Aidez-le à grandir

Live Track Ships continue de grandir. Nous ajoutons des sources de données et
des pays à mesure que nous les trouvons, et nous voulons savoir ce que vous
aimeriez ensuite.

### Proposer quelque chose

Votre pays ou votre service AIS manque ? Quelque chose est faux, ou difficile
à comprendre ? Dites-le-nous de la façon la plus simple pour vous :

* [**Remplissez un court formulaire**](https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues/new?template=fr.yml)
  en français. Il vous faut un compte GitHub gratuit.
* **Écrivez un e-mail** à
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  Aucun compte n'est nécessaire.

Dans les deux cas, il nous aide que vous nous disiez :

* ce que vous aimeriez voir, et où dans le monde ;
* un lien vers l'endroit où les données sont publiées, si vous en connaissez
  un (une page de données ouvertes, un flux public, le site d'un service) : ce
  n'est pas nécessaire, mais cela aide ;
* la langue de votre Home Assistant, si le problème concerne la formulation ou
  une traduction.

Écrivez en anglais ou dans votre propre langue, ce qui est le plus simple pour
vous.

### L'ajouter vous-même, avec notre aide

Si vous souhaitez ajouter quelque chose vous-même, nous vous aiderons à le
faire, de la première question jusqu'à la version terminée. Vous n'avez pas
besoin d'être développeur pour commencer :

* **Une traduction.** Les textes de la boîte de dialogue de configuration sont
  une courte liste de phrases dans un seul fichier texte. Nous vous montrerons
  quel fichier et quelles lignes.
* **Une nouvelle source de données.** Dites-nous où les données sont publiées.
  Nous pouvons écrire le code ensemble, ou relire le vôtre.
* **Le tester là où vous habitez.** Installez-le, regardez votre partie de la
  carte, et dites-nous ce qui est juste et ce qui ne l'est pas.
* **Une correction de ce README.** Si une étape ne correspondait pas à ce que
  vous avez vu, dites-nous ce que vous avez vu.

[**Dites-nous ce que vous avez en tête**](https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues/new?template=fr.yml)
ou écrivez à
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
et nous vous répondrons avec les prochaines étapes.

---

## Langues

Ce README : [English](README.md), [Deutsch](README.de.md), **Français**,
[Nederlands](README.nl.md), [简体中文](README.zh-Hans.md),
[Español](README.es.md), [Italiano](README.it.md), [Dansk](README.da.md) et
[Kalaallisut](README.kl.md) (un court brouillon, envoyé pour relecture à
Oqaasileriffik, le secrétariat de la langue du Groenland ; d'ici là, la page
danoise est la page fiable). Chaque README traduit est complet.

La boîte de dialogue de configuration et les options s'affichent dans la
langue de votre Home Assistant quand c'est l'une de celles-ci : English,
Dansk, Deutsch, Español, Français, Gaeilge, Íslenska, Italiano, Nederlands,
Norsk Bokmål, Polski, Português, Português (BR), Suomi, Svenska et 简体中文.
Toute autre langue affiche l'anglais. Le kalaallisut n'est pas encore une
langue de Home Assistant ; nous avons demandé à Home Assistant de l'ajouter.
Les libellés propres à la carte (**Track**, **Details**) sont en anglais dans
toutes les langues.

Vous avez trouvé une erreur dans une traduction, ou il vous faut une autre
langue ? Dites-le-nous sur
<https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues>, ou
[traduisez-le avec notre aide](#lajouter-vous-même-avec-notre-aide).

---

## Crédits et licences

* **aisstream.io** : pas de conditions publiées. <https://aisstream.io>
* **Fintraffic Digitraffic** (Finlande) : données sous CC BY 4.0.
  <https://www.digitraffic.fi/en/terms-of-service/>
* **BarentsWatch** (Norvège) : données sous la licence norvégienne pour les
  données publiques ouvertes (NLOD).
  <https://www.barentswatch.no/en/articles/api-terms-and-conditions/>
* **Votre propre récepteur** : vos propres données.
* **Wikidata** : CC0. **Wikimedia Commons** : chaque photo sous sa propre
  licence, affichée avec son photographe et sa licence.
* **VesselFinder** : seulement un lien ; rien n'y est récupéré.
* **EnforcementVessels** : ODbL 1.0.
  <https://github.com/StrausbergAutomationWorks/EnforcementVessels>

Ce que cette intégration modifie : les unités sont converties, et seuls les
navires à l'intérieur de votre cercle sont gardés. Chaque entité de navire, et
le `sensor.ships_in_range` de chaque zone, porte une `attribution` qui nomme
sa source ; Home Assistant l'affiche dans les détails de l'entité. Si vous
montrez ces données à d'autres, par exemple sur un tableau de bord public,
gardez le crédit avec elles et lisez les conditions propres à la source. Les
lignes de crédit exactes, et les crédits des images de navires, sont dans
[ATTRIBUTION.md](ATTRIBUTION.md).

Aucune de ces organisations n'a fait ni approuvé cette intégration.

**Code** : MIT, dans [LICENSE](LICENSE).

**Pour les développeurs :** les phrases AIS de votre propre récepteur sont
décodées par [pyais](https://github.com/M0r13n/pyais) (MIT) ; Home Assistant
installe lui-même `saw-livetrack` et `pyais` la première fois qu'il charge
l'intégration. Les tests dans `tests/` se lancent chacun seul avec Python ;
certains demandent Home Assistant installé, et les tests `*_live` demandent
vos propres clés.

---

## Mots-clés

Home Assistant navires · Home Assistant AIS · suivi des navires · suivi de
bateaux · carte du trafic maritime · carte AIS · récepteur AIS · NMEA ·
AIS-catcher · aisstream.io · Digitraffic · BarentsWatch · ship tracking ·
vessel tracker · Schiffsverfolgung · scheepvaart volgen · seguimiento de
barcos · tracciamento navi · skibstrafik · 船舶追踪 · geo_location · carte ·
Lovelace · HACS · Marketplace · Live Track · LiveTrack ·
StrausbergAutomationWorks

---

**Reconnaissance.** StrausbergAutomationWorks reconnaît les peuples autochtones
de toutes les terres et de toutes les eaux de cette carte, partout dans le
monde, et rend hommage à leurs Aînés d'hier et d'aujourd'hui.
