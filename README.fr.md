# Live Track Ships

[English](README.md) · [Deutsch](README.de.md) · **Français** · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Kalaallisut](README.kl.md) · [Toutes les langues](#langues)

**Suivi AIS des navires, bateaux et embarcations pour Home Assistant.** Les
navires près de chez vous, ou n'importe où dans le monde, en repères en
direct sur votre carte. Une partie de Live Track : navires, avions et trains
sur une seule carte.

Données AIS marines en direct d'[aisstream.io](https://aisstream.io), de
[Fintraffic Digitraffic](https://www.digitraffic.fi/en/marine-traffic/) ou de
[BarentsWatch](https://www.barentswatch.no/en/), présentées comme entités
`geo_location` de Home Assistant et dessinées sur la carte Live Track commune.

**État : 0.1.0, la première version.** Ajoutée au Marketplace par lien
(ci-dessous) ; elle n'est pas encore dans le catalogue du Marketplace.

## Ce qu'est l'AIS

L'AIS (Automatic Identification System, système d'identification
automatique) est une émission VHF par laquelle les navires annoncent leur
position, leur identité et leur voyage aux autres navires et à la terre.
C'est l'équivalent maritime de l'ADS-B. Les navires de commerce doivent en
être équipés ; beaucoup de bateaux de plaisance l'ont volontairement, le plus
souvent en classe B, moins puissante.

L'AIS est émis en clair. N'importe qui avec un récepteur peut l'entendre, et
des agrégateurs publics le republient.

## Ce qui est affiché

**Tout ce que la source envoie.** Rien n'est filtré, et aucun réglage ne
permet de masquer une catégorie.

| Dans le flux | Affiché |
|---|---|
| Cargos, pétroliers, remorqueurs, ferries, navires à passagers | oui |
| Navires de pêche, de pilotage, des autorités et autres navires de travail | oui |
| **Bateaux de plaisance privés et voiliers** | **oui, avec nom et position** |
| **Bouées d'engins de pêche** qui émettent de l'AIS | **oui, dessinées en poisson** |
| Aéronefs de recherche et sauvetage (SAR) | quand la source les envoie |
| Aides à la navigation : bouées, balises, phares | quand la source les envoie |
| Stations de base AIS à terre | quand la source les envoie |

### Les bateaux privés sont affichés, et vous devez savoir ce que cela implique

Un bateau de plaisance qui émet de l'AIS apparaît sur votre carte exactement
comme un cargo. Selon ce qu'il émet, son entité peut contenir :

- son **nom**, qui est aussi l'étiquette dessinée sur la carte
- son **MMSI** et son **indicatif radio**, permanents et consultables
  publiquement
- sa **position** à environ un mètre près, sa position précédente et l'heure
  à laquelle chacune a été entendue
- sa vitesse, sa route et son cap, s'ils sont émis
- sa longueur, sa largeur et son type, s'ils sont émis

Un bateau qui laisse son transpondeur allumé au port reste sur la carte à son
poste tant qu'il émet.

Il n'existe pas de liste d'exclusion pour l'AIS, comme il en existe pour les
avions, et cette intégration n'en invente pas. Si vous voulez moins de bateaux
privés sur votre carte, réduisez le rayon.

### Le type de navire manque souvent, surtout pour les petits bateaux

La position et le nom arrivent avec presque chaque message. Le type et la
taille arrivent dans un message séparé, plus rare, et beaucoup d'appareils de
petits bateaux (classe B) n'envoient que rarement la partie qui les contient.
Attendez-vous à ce qu'une grande part des navires, dont la plupart des petits,
n'aient ni type ni dimensions, et à ce que tous soient incomplets pendant
quelques minutes après un redémarrage de Home Assistant. Ce sont les données,
pas une panne. Les types et tailles déjà entendus sont conservés d'un
redémarrage à l'autre.

### Tout ce qui émet de l'AIS n'est pas un navire

Chaque entité porte `object_kind` : `vessel`, `net_buoy`, `aton` (aide à la
navigation), `base_station`, `sar_aircraft` ou `distress_beacon`. La plupart
sont reconnus au format d'identifiant que leur attribue l'UIT. Les bouées
d'engins de pêche non : elles émettent avec des identifiants de type navire,
et sont donc reconnues à leurs noms d'usine (FISHING BOUY, NET MARK, BUOY) et
à l'absence de longueur émise.

Tout ce qui n'est pas un navire est affiché sans type, taille ni statut de
navigation. Les bouées d'engins de pêche dérivent avec leurs lignes ; elles
gardent donc vitesse et route, et sont dessinées en saumon tourné dans le sens
de la dérive.

Ce qui apparaît dépend de la source. Mesuré sur une soirée :

| Source | Bouées d'engins de pêche | Aéronefs SAR | Aides à la navigation, stations de base |
|---|---|---|---|
| BarentsWatch | oui | oui | aucune vue |
| Digitraffic | aucune vue | oui | aucune vue |
| aisstream.io | aucune vue | aucun vu | aucune vue |
| Votre propre récepteur | ce qu'il entend | ce qu'il entend | ce qu'il entend |

aisstream.io n'a livré que des messages de position et de détails des
navires, aussi bien sur les Grands Lacs que sur les mêmes eaux norvégiennes et
danoises où BarentsWatch montre les bouées.

## Sources

Vous choisissez une source pour chaque zone que vous créez.

| Source | Couverture | Il faut |
|---|---|---|
| aisstream.io | le monde entier, là où des bénévoles font tourner des récepteurs | une clé API gratuite |
| Fintraffic Digitraffic | eaux finlandaises et baltes | rien |
| BarentsWatch AIS Live | eaux norvégiennes | un ID client et un secret gratuits |
| Votre propre récepteur AIS | aussi loin que votre antenne entend | un récepteur qui envoie le NMEA en UDP |

Les catégories qui apparaissent, la fraîcheur des positions et la
complétude des détails dépendent de la source choisie.

### Votre propre récepteur

Si vous avez un récepteur AIS, Live Track Ships peut afficher ce qu'il
entend, sans compte et sans Internet. Le récepteur, ou le programme qui le
décode, envoie des phrases NMEA (`!AIVDM`) en UDP à l'adresse de Home
Assistant, sur un port de votre choix (10110 si vous ne le changez pas). Dans
AIS-catcher, c'est `-u <address> <port>` ; dans rtl-ais,
`-h <address> -P <port>` ; OpenCPN et Signal K l'ajoutent comme connexion de
sortie UDP. Un récepteur qui se branche en USB, comme un dAISy, a besoin de
l'un de ces programmes pour transmettre ses phrases.

- Une zone écoute un port ; deux récepteurs demandent deux ports.
- Tout ce que le récepteur entend dans votre cercle est affiché, aides à la
  navigation et stations de base comprises. Le capteur de station
  (ci-dessous) compte aussi ce qu'il entend hors du cercle.
- Une phrase ne porte pas de date : l'heure d'une position est celle où Home
  Assistant l'a reçue.
- La vitesse de giration n'est pas affichée pour cette source.
- Pour l'instant, c'est testé avec des phrases enregistrées envoyées en UDP,
  pas avec un récepteur. Si vous l'essayez avec le vôtre, dites-nous comment
  ça s'est passé sur la [page des issues](https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues).

### Mentions de source

Chaque entité navire, et le capteur `ships_in_range` de chaque zone, porte un
attribut `attribution` qui nomme la source ; Home Assistant l'affiche dans les
détails de l'entité. Deux des sources accordent leurs données sous une licence
qui demande d'être cité, et Live Track Ships modifie les données reçues
(unités converties, seulement les navires dans votre cercle), donc leurs
lignes le disent. Si vous montrez ces données à d'autres, par exemple sur un
tableau de bord public, gardez la mention et lisez les conditions de la
source :

- **aisstream.io** : aucune condition publiée. <https://aisstream.io>
- **Fintraffic Digitraffic** : CC BY 4.0.
  <https://www.digitraffic.fi/en/terms-of-service/>
- **BarentsWatch** : licence norvégienne pour les données publiques ouvertes
  (NLOD). <https://www.barentswatch.no/en/articles/api-terms-and-conditions/>
- **Votre propre récepteur** : vos propres données ; sa ligne le dit.
- **EnforcementVessels** (la liste derrière l'aspect garde-côtes, ci-dessous) :
  ODbL v1.0. <https://github.com/StrausbergAutomationWorks/EnforcementVessels>

Les lignes exactes figurent dans [ATTRIBUTION.md](ATTRIBUTION.md).

## Prérequis

- Home Assistant 2026.11 ou plus récent, avec un accès à Internet pour les
  sources en ligne.
- Pour aisstream.io : une clé API gratuite sur
  [aisstream.io](https://aisstream.io/account). aisstream autorise **trois
  connexions par compte et trois par adresse IP publique** ; si d'autres outils
  utilisent la même clé, tenez-en compte. Live Track SALT, s'il est installé,
  utilise une seconde connexion avec la même clé.
- Pour BarentsWatch : un ID client et un secret gratuits, à enregistrer
  soi-même chez BarentsWatch. Saisissez l'ID client exactement tel qu'il a été
  délivré.
- Pour votre propre récepteur : un récepteur et un programme qui envoient le
  NMEA en UDP à Home Assistant, sur le même réseau. Il n'a pas besoin
  d'Internet.
- Home Assistant installe les paquets Python nécessaires (`saw-livetrack` et
  `pyais`) au premier chargement de l'intégration.

## Installation

### Depuis le Marketplace

Live Track Ships n'est pas encore dans le catalogue du Marketplace.
Ajoutez-la par lien :

1. **Paramètres > Marketplace**, puis **Ajouter depuis un lien**.
2. Saisissez `StrausbergAutomationWorks/LiveTrackShips`. Si le type est
   demandé, choisissez **Intégration**.
3. Installez **Live Track Ships**.
4. Redémarrez Home Assistant. Le Marketplace propose le redémarrage comme
   réparation dans **Paramètres > Système > Réparations**.

### À la main

1. Téléchargez le code source de la
   [dernière version](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest).
2. Copiez son dossier `custom_components/live_track_ships` dans le dossier
   `custom_components` du répertoire de configuration de Home Assistant.
3. Redémarrez Home Assistant.

## Configuration

**Paramètres > Appareils et services > Ajouter une intégration > Live Track
Ships**, puis **Tous les navires d'une zone** (l'autre choix, les navires
suivis, est [plus bas](#navires-suivis--suivre-des-navires-choisis-partout)).
Chaque zone est une entrée distincte, intitulée *Ships near <latitude>,
<longitude>*. La fenêtre s'affiche en français quand Home Assistant est en
français.

| Champ | Ce qu'il accepte | Par défaut |
|---|---|---|
| Source des données | aisstream.io, Fintraffic Digitraffic, BarentsWatch AIS Live ou votre propre récepteur AIS | aisstream.io |
| Clé API | aisstream.io seulement. Reprise d'une zone déjà créée ; modifiable | vide |
| ID client, secret client | BarentsWatch seulement. Repris d'une zone déjà créée | vide |
| Port UDP | votre propre récepteur seulement : le port auquel il envoie le NMEA, de 1024 à 65535. Refusé si une autre zone ou un autre programme l'utilise déjà | 10110 |
| Centre | un repère sur une carte ; faites-le glisser sur l'eau à surveiller | votre domicile |
| Rayon (km) | 1 à 500 | 50 |
| Nombre maximal de navires suivis | 1 à 5 000 ; une limite de sécurité pour cette zone, les plus proches sont gardés | 1 000 |

Une même source ne peut pas surveiller deux fois le même centre. Quand au
moins 5 % d'un cercle BarentsWatch se trouve hors des eaux que publie
BarentsWatch, la fenêtre indique la proportion avant de créer la zone ;
validez pour garder ce cercle quand même.

**Réglages d'une zone** (Configurer sur son entrée) : le centre, avec le même
repère ; le rayon ; le nombre maximal de navires suivis ; et *Nombre maximal
de navires sur la carte, toutes les entrées Live Track Ships ensemble*, un
curseur de 100 à 2 500 par pas de 100 (2 500 par défaut) ; et, pour votre propre récepteur, son port UDP. Déplacer le centre
renomme la zone d'après sa nouvelle position et la recharge. Une même source
ne peut toujours pas surveiller un centre depuis deux zones.

## Ce qui est créé

- **Une entité `geo_location` par navire**, `geo_location.vessel_<MMSI>`,
  dont l'état est sa distance au centre de la zone en kilomètres. Les
  attributs comprennent le nom, le MMSI, l'indicatif, la vitesse, la route, le
  cap, la longueur, la largeur, le type, la destination, `object_kind`,
  `last_seen` et `attribution`, chacun seulement si la source l'a envoyé. Un
  navire vu par deux zones est une seule entité.
- **Un capteur par zone**, `sensor.ships_in_range`, qui compte les navires
  affichés et le signale quand la limite de la zone ou de l'installation
  écourte la liste.
- **Pour votre propre récepteur, un capteur de plus**, `sensor.ais_station` :
  les messages par minute. Ses attributs sont `vessels_heard` (sur les 10
  dernières minutes), `farthest_km` et `farthest_mmsi` (depuis le centre de la
  zone), `last_message`, `udp_port`, `listening`, et `port_error` quand le
  port ne peut pas être ouvert. Il se met à jour toutes les 30 secondes : un
  récepteur qui n'envoie plus rien affiche 0.

Un navire entendu hors de votre cercle quitte la carte aussitôt. Pour
l'entendre, chaque source en ligne est interrogée sur un anneau un peu plus grand que
votre cercle (10 %, au moins 1 km), et votre propre récepteur envoie tout ce qu'il entend ;
seuls les navires dans votre cercle sont
gardés. Un navire qu'on n'entend plus quitte la carte après une période de
silence, et un navire qui n'apparaît plus n'est pas forcément parti
(ci-dessous).

## Événements : un navire entre dans votre zone ou en sort

Chaque zone déclenche deux événements Home Assistant, pour qu'une
automatisation vous prévienne quand arrive un navire qui vous intéresse :

- `live_track_ships_entry` quand un navire entre dans le cercle de la zone
- `live_track_ships_exit` quand il en sort

L'intégration annonce tous les navires ; votre automatisation choisit ceux
qui comptent. Les données de l'événement portent les mêmes noms et unités que
les attributs du navire, et omettent ce que la source n'a pas envoyé :

| Champ | Contenu |
|---|---|
| `area_id`, `area` | l'ID de l'entrée de configuration de la zone et son titre |
| `identity` | le MMSI |
| `name`, `call_sign`, `imo` | s'ils sont émis |
| `object_kind` | `vessel`, `net_buoy`, `aton`, `base_station`, `sar_aircraft` ou `distress_beacon` |
| `ship_type`, `ship_type_label`, `length_m`, `beam_m`, `draught_m`, `destination`, `nav_status` | navires seulement, s'ils sont émis |
| `speed_kmh`, `course_deg`, `heading_deg` | s'ils sont émis |
| `latitude`, `longitude`, `distance_km`, `bearing_from_centre_deg`, `last_seen` | où il a été entendu, depuis le centre de la zone |
| `entity_id` | entrée seulement : `geo_location.vessel_<MMSI>`, quand le navire est sur la carte |
| `reason` | sortie seulement : `left` (entendu hors du cercle) ou `silent` (pas entendu pendant la durée de conservation, donc peut-être encore là) |

Quatre choses à savoir :

- **Une arrivée n'est annoncée que si le navire a d'abord été entendu hors du
  cercle**, dans l'anneau qui l'entoure. Un navire entendu d'abord à
  l'intérieur était peut-être là depuis le début : après un redémarrage, les
  récepteurs continuent pendant de longues minutes à livrer des navires qui
  n'ont jamais bougé. Un navire que les récepteurs n'ont pas entendu en
  entrant, ou qui allume son transpondeur à l'intérieur, n'est donc pas
  annoncé.
- **Une sortie entendue hors du cercle est toujours annoncée**, même pour un
  navire présent avant le démarrage de Home Assistant. Un navire qui se tait
  n'est annoncé comme sorti (`reason: silent`) que si son arrivée l'a été.
- **Une sortie attend 2 minutes.** Un navire qui revient avant, le long du
  bord du cercle, n'est pas annoncé comme sorti puis rentré.
- **Des détails peuvent manquer à l'arrivée.** Le nom, le type et la taille
  voyagent dans un message plus rare que la position (ci-dessus). Un navire
  entendu pour la première fois peut arriver avec une position et rien
  d'autre ; un navire déjà entendu porte en général son type et sa taille.

Deux zones sur les mêmes eaux déclenchent chacune leurs propres événements.
Les limites du nombre de navires dessinés ne font jamais entrer ni sortir un
navire.

Une automatisation qui vous prévient quand un navire de plus de 150 m entre
dans une zone :

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
      title: "{{ trigger.event.data.name | default('Un navire') }}"
      message: >-
        {{ trigger.event.data.ship_type_label | default('Navire') }},
        {{ trigger.event.data.length_m }} m,
        à {{ trigger.event.data.distance_km }} km, entre dans
        {{ trigger.event.data.area }}.
```

## Navires suivis : suivre des navires choisis partout

En plus des zones, vous pouvez suivre une liste de navires où qu'ils soient :
le bateau d'un proche, un ferry que vous prenez, un navire de croisière qui
rentre. **Paramètres > Appareils et services > Ajouter une intégration > Live
Track Ships > Des navires choisis, où qu'ils soient.** Il faut une clé
aisstream.io (celle d'une zone déjà créée est préremplie), et il y a une seule
liste de ce type par Home Assistant.

Un navire par ligne : son MMSI à 9 chiffres, puis un nom de votre choix si
vous le souhaitez.

```text
244650000 Bateau de papa
366999999 Le ferry
```

100 navires au plus. aisstream suit au plus 200 MMSI par clé, et
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
s'il est installé avec la même clé, en utilise une partie ; une liste qui
dépasserait est refusée au chargement de l'entrée, avec la raison. Modifiez la
liste dans les réglages de l'entrée.

Un navire suivi est dessiné sur la carte comme les autres, là où il est
entendu, et son état est sa distance à votre domicile. Une zone qui l'affiche
déjà le garde : un navire, un repère. L'entrée ajoute
`sensor.watched_vessels` : combien des navires de la liste sont entendus en ce
moment, avec chacun d'eux, son nom donné et son dernier état connu dans
l'attribut `vessels`.

Elle déclenche un seul événement, `live_track_ships_watched`, dont le champ
`change` dit ce qui s'est passé :

| `change` | Quand |
|---|---|
| `arrived` | le navire se déclare amarré ou au mouillage, ou, sans statut, reste sous 2 nœuds |
| `departed` | il fait de nouveau route |
| `silent` | pas entendu pendant 30 minutes (6 heures s'il est amarré ou au mouillage) ; il quitte la carte, et il est peut-être encore là |
| `heard` | de nouveau entendu après `silent` |
| `destination` | l'équipage a changé la destination ; `destination_previous` contient l'ancienne |

Les données portent `watch_id`, `watch`, `identity`, votre nom donné `label`
et les mêmes champs navire que les événements de zone, avec la distance et le
relèvement depuis votre domicile. L'arrivée et le départ attendent que le
nouvel état ait tenu 5 minutes selon l'horloge du navire, pour qu'un bateau
qui dérive à 2 nœuds ne fasse pas l'aller-retour. Rien n'est annoncé à partir
de la première position d'un navire après un redémarrage : elle fixe le point
de départ. Les destinations sont saisies par l'équipage et souvent périmées.

## Carte

Les navires sont dessinés par [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)
(`custom:live-track-map-card`), la carte unique sur laquelle dessine chaque
intégration Live Track. Elle dessine l'image propre de chaque navire, la
tourne selon son cap et la fait glisser entre de vraies positions le long de
l'eau plutôt qu'en ligne droite à travers les terres.

**La carte est installée avec l'intégration.** Cette intégration embarque une
copie publiée de la carte, la sert et l'enregistre comme ressource de tableau
de bord au démarrage de Home Assistant ; il n'y a rien à télécharger ni à
copier dans `www`. Chaque intégration Live Track fait de même, et elles
gardent entre elles exactement une ligne de ressource : la version de la carte
la plus récente que l'une d'elles embarque, jamais une plus ancienne. Une
carte installée par le Marketplace n'est pas touchée. Retirer la dernière zone
de cette intégration confie la ligne à une autre intégration Live Track, ou la
supprime s'il n'en reste aucune. Voir le README de la carte, section
[Live Track](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).

Si les ressources de vos tableaux de bord sont définies en YAML
(`lovelace: resource_mode: yaml`), rien ne peut être enregistré pour vous. Une
réparation donne alors la ligne exacte à ajouter ; elle ressemble à ceci, avec
l'adresse de l'intégration à la place des espaces réservés :

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_ships/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Si les fichiers de l'intégration sont supprimés (par le Marketplace, par
exemple) alors que ses zones sont encore configurées, et qu'aucune autre
intégration Live Track n'est installée, personne ne range la ligne :
supprimez-la dans Paramètres > Tableaux de bord > Ressources. Pour installer
la carte à la main, suivez le README de la carte ; la ligne de ressource
d'une copie installée à la main sous `/local/` n'est dirigée vers la copie
d'une intégration que si celle-ci est une version plus récente.

Donnez-lui les navires avec
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities), en
filtrant sur `domain: geo_location` et `attributes: {source: live_track_ships}`.
Avec d'autres intégrations Live Track installées, ajoutez un filtre pour
chacune de leurs sources.

Toute autre carte qui affiche des entités `geo_location` affiche aussi les
navires, sans les images ni le glissement de cette carte.

Un navire de la liste publique
[EnforcementVessels](https://github.com/StrausbergAutomationWorks/EnforcementVessels)
(navires des garde-côtes employés pour l'immigration) est dessiné aux couleurs
des garde-côtes avec le nom et l'agence de la liste, où qu'il soit.

### Masquer des types de navires

Chaque navire porte `marker_group`, `marker_group_label` et `marker_group_order` :
l'un de treize groupes (cargo ; pétrolier ; passagers et ferries ; pêche ;
plaisance et voile ; remorqueurs, pilotes et service portuaire ; État, SAR et
police ; grande vitesse et autres ; type non transmis ; bouées d'engins de
pêche ; aides à la navigation ; stations de base ; aéronefs SAR). La carte de
filtre de la carte, `custom:live-track-map-filter-card`, les liste avec leur
nombre sur la carte et masque ceux que vous décochez ; placez-la sur n'importe
quelle vue du tableau de bord. Votre choix n'est gardé que dans ce navigateur.
L'intégration montre toujours tout : son capteur compte chaque navire et ses
événements se déclenchent pour chaque navire. Une balise de détresse n'a pas de
groupe : elle n'est jamais masquée.

### Photos et liens

Quand un navire transmet un numéro IMO et que Wikidata connaît une photo de ce
navire sur Wikimedia Commons, le navire porte `marker_photo`. La carte affiche
la photo dans l'infobulle avec le photographe et la licence ; un clic l'ouvre en
plus grand, avec des liens vers la page de la photo et vers sa licence. Tout
navire qui a un numéro IMO ou un MMSI porte aussi `marker_links`, un lien vers
le navire sur VesselFinder. Le bouton **Details** de la fenêtre ouvre la boîte
de dialogue habituelle du navire. Votre Home Assistant interroge lui-même
Wikidata et Commons, 20 numéros IMO à la fois, à dix secondes d'intervalle, et
garde chaque réponse 30 jours (14 quand il n'y a pas de photo) dans
`.storage/saw_vessel_photos.json`. Comptez sur une photo pour environ un navire
sur dix : sur notre système de test, 49 numéros IMO sur 521 en avaient une.

## Où elle cherche

Vous placez un **centre et un rayon** sur la carte. Le centre peut être
n'importe où dans le monde ; le rayon va de 1 à 500 km. Par défaut : **50 km**.
L'état de chaque navire est sa distance à votre centre.

Le nombre de navires dans un cercle dépend bien plus de *quelle eau* que de
*quelle taille*. En test, un cercle de 50 km contenait environ 4 navires
au-dessus de Chicago et environ 340 au-dessus du Solent, dans le sud de
l'Angleterre : le même rayon, environ 80 fois plus de trafic. L'intégration
garde donc au plus un nombre fixé de navires (1 000 par défaut, réglable
jusqu'à 5 000), garde les plus proches quand il y en a plus, et le signale sur
son capteur `ships_in_range`.

Toutes vos zones **ensemble** affichent au plus 2 500 navires, quelles que
soient leurs sources. Les réglages de chaque zone ont le curseur ci-dessus,
qui ne peut que baisser cette limite ; le réglage le plus bas d'une zone
activée s'applique. Baissez-le sur un matériel plus lent.

## Couverture, mesurée plutôt que promise

La couverture est bonne là où il y a des récepteurs et absente ailleurs, et
**aucun réglage ne peut créer une couverture qui n'existe pas**.

Mesuré le 2026-09-02 autour de Chicago, avec aisstream.io :

- **Grands Lacs** : 100 navires différents en 120 secondes, les cinq lacs et
  les eaux qui les relient.
- **Chicago River, centre-ville** : fréquentée et fiable.
- **Chicago Sanitary and Ship Canal, Cal-Sag Channel, Calumet River** : une
  heure d'écoute, **zéro navire**. Le canal n'est pas vide : ses convois
  poussés sont visibles sur les services commerciaux par AIS satellite, que
  les agrégateurs gratuits ne transmettent pas. Le trafic est réel ; la
  couverture terrestre, non.

Aucun navire dans votre zone peut vouloir dire aucun récepteur plutôt
qu'aucun bateau. Vérifiez que votre source couvre vos eaux avant de croire
l'intégration en panne.

Un navire qui n'apparaît plus n'est pas forcément parti. Aucune de ces
sources ne garantit la livraison ; l'intégration montre donc quand chaque
navire a été entendu pour la dernière fois et ne le retire qu'après une
période de silence.

## Les navires qui méritent leur propre image

La plupart des navires sont dessinés selon leur type. Certains ont leur
propre image : yachts royaux et d'État, et bateaux connus comme les bateaux
de croisière, bateaux-taxis et bateaux-pompes de Chicago. Vous connaissez un
navire qui en mérite une, n'importe où dans le monde ? Ouvrez une issue sur
<https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues> avec son
nom et son numéro MMSI ou IMO, et une photo ou un lien si vous en avez.

## Langues

Ce README : [English](README.md), [Deutsch](README.de.md), **Français**,
[Nederlands](README.nl.md), [简体中文](README.zh-Hans.md),
[Español](README.es.md), [Italiano](README.it.md), [Dansk](README.da.md) et
[Kalaallisut](README.kl.md) (un brouillon, envoyé pour relecture à
Oqaasileriffik, le secrétariat de la langue groenlandaise ; d'ici là, la page
danoise est la plus fiable). Le README est traduit dans une courte liste de
langues : celles que lisent le plus d'utilisateurs de Home Assistant, et
quelques autres quand il y a une bonne raison. Chaque README traduit est
complet : tout ce que contient l'anglais s'y trouve, et aucun ne vous renvoie
à l'anglais pour les détails.

La fenêtre de configuration et les réglages d'une zone s'affichent dans la
langue de votre Home Assistant quand c'est l'une de celles-ci : English,
Dansk, Deutsch, Español, Français, Gaeilge, Íslenska, Italiano, Nederlands,
Norsk Bokmål, Polski, Português, Português (BR), Suomi, Svenska et 简体中文.
Toute autre langue affiche la fenêtre en anglais. Le kalaallisut n'est pas
encore une langue de Home Assistant ; nous avons demandé à Home Assistant de
l'ajouter, et la fenêtre suivra dès qu'elle pourra être affichée.

Vous avez trouvé dans une traduction une erreur qui change le sens ou se lit
mal ? Dites-le-nous sur
<https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues>. Les
traductions ont été écrites pour ce projet et toutes n'ont pas encore été lues
par un locuteur natif.

**Vous avez du mal à suivre dans l'une de ces langues ?** Demandez-en une
autre à la même adresse, et nous essaierons de vous satisfaire.

## Une partie de Live Track

Live Track est un ensemble d'intégrations Home Assistant, une par sorte de
chose qui bouge, qui dessinent toutes sur la même carte. Elles partagent une
bibliothèque Python
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore))
et la carte, si bien qu'en installer une de plus n'ajoute aucune requête à une
source partagée. Publiées :
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft),
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
[Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail),
[Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail)
et Live Track Ships. Chacune fonctionne seule.

## Aucune affiliation

Sans lien avec aisstream.io, Fintraffic, BarentsWatch, MarineTraffic,
VesselFinder, un armateur ou une autorité maritime. L'AIS est un système de
sécurité de la navigation ; **cette intégration est faite pour la curiosité
et ne sert ni à la navigation, ni à l'évitement des collisions, ni à aucun
usage opérationnel.**

## Licence

Code : MIT, dans [LICENSE](LICENSE). Mentions des données et des images :
[ATTRIBUTION.md](ATTRIBUTION.md).

## Mots-clés

Home Assistant AIS · suivi des navires · navires sur la carte · suivi de
bateaux · trafic maritime en direct · carte AIS · aisstream.io · Digitraffic ·
BarentsWatch · geo_location · intégration HACS
