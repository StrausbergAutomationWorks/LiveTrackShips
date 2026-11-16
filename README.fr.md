# Live Track Ships

[English](README.md) · [Deutsch](README.de.md) · **Français** · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Kalaallisut](README.kl.md)

Navires, bateaux et autres embarcations en direct sur la carte de Home
Assistant. Live Track Ships est une intégration Home Assistant (custom
component, à installer depuis le Marketplace / HACS) qui affiche les données
AIS des navires de la zone choisie : où se trouve chacun, son nom, sa vitesse,
son cap, son type et sa taille quand le navire les transmet. Chaque navire est
une entité `geo_location` qui se déplace sur la carte à chaque nouvelle
position. Le centre de la zone peut se trouver n'importe où dans le monde.

**État : 0.1.0, la première version.**

## Les bateaux de plaisance sont affichés aussi

L'intégration affiche tout ce que la source envoie, et rien ne peut être
filtré. Un bateau de plaisance équipé d'un transpondeur AIS apparaît sur la
carte comme un cargo : nom, MMSI, indicatif d'appel et position à un mètre près
environ. Un bateau qui laisse son transpondeur allumé au port reste sur la
carte à sa place. L'AIS n'a pas de liste d'opposition. Pour voir moins de
bateaux de plaisance, réduisez le rayon.

## Sources

Vous choisissez une source par zone.

| Source | Couverture | Il faut |
|---|---|---|
| aisstream.io | le monde entier, là où des bénévoles ont des récepteurs | une clé API gratuite |
| Fintraffic Digitraffic | eaux finlandaises et baltes | rien |
| BarentsWatch AIS Live | eaux norvégiennes | un ID client et un secret gratuits |

L'attribut `attribution` de chaque navire indique sa source. Toutes les
mentions : [ATTRIBUTION.md](ATTRIBUTION.md).

La couverture est bonne là où il y a des récepteurs, et aucun réglage ne crée
une couverture qui n'existe pas. Si votre zone n'affiche aucun navire, il
manque peut-être des récepteurs, pas des bateaux.

## Prérequis

- Home Assistant 2026.11 ou plus récent.
- aisstream.io : une clé API gratuite sur
  [aisstream.io](https://aisstream.io/account). aisstream autorise trois
  connexions par compte et par adresse IP publique.
- BarentsWatch : un ID client et un secret gratuits. Saisissez l'ID client
  exactement tel qu'il a été délivré.
- Digitraffic ne demande ni clé ni compte.

## Installation

### Depuis le Marketplace

L'intégration n'est pas encore dans le catalogue du Marketplace. Ajoutez-la
par lien :

1. **Paramètres > Marketplace**, puis ajout depuis un lien.
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
Ships.** Choisissez la source, saisissez la clé si besoin, faites glisser le
repère de la carte sur l'eau à surveiller et choisissez le rayon (1 à 500 km,
50 par défaut). Chaque zone est une entrée distincte. La fenêtre s'affiche en
français quand Home Assistant est en français.

Dans les réglages d'une zone, vous pouvez déplacer le centre avec le même
repère ; la zone est alors renommée et rechargée. Toutes les zones ensemble
affichent au plus 2 500 navires ; un curseur dans les réglages ne peut que
baisser cette limite. Utilisez-le sur une machine lente.

## Les navires qui méritent leur propre image

La plupart des navires sont dessinés selon leur type. Certains ont leur propre
image : yachts royaux et d'État, et bateaux connus comme les bateaux
d'excursion, bateaux-taxis et bateaux-pompes de Chicago. Vous connaissez un
navire qui en mérite une, où que ce soit dans le monde ? Ouvrez une issue sur
<https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues> avec son
nom et son numéro MMSI ou IMO, et une photo ou un lien si vous en avez.

Vous avez trouvé une erreur importante dans cette traduction ou dans la fenêtre
en français ? Signalez-la à la même adresse.

## Une partie de Live Track

Live Track est un ensemble d'intégrations Home Assistant, une par type de chose
qui bouge, qui dessinent toutes sur la même carte
([LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
installée avec l'intégration). Publiées :
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft),
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
[Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail),
[Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail)
et Live Track Ships. Chacune fonctionne seule.

## Données et licence

Les navires sont lus pendant le fonctionnement, directement depuis la source
choisie ; ce dépôt ne contient aucune donnée de ces sources. Code : MIT.

Sans lien avec aisstream.io, Fintraffic, BarentsWatch ni aucune autorité
maritime. **Ne pas utiliser pour la navigation ni pour éviter les
collisions.** Tous les détails et toutes les langues :
[README en anglais](README.md#languages).

## Mots-clés

Home Assistant AIS · navires sur la carte · suivi de navires · suivi de
bateaux · trafic maritime en direct · carte AIS · intégration HACS
