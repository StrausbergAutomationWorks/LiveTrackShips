# Live Track Ships

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · **Español** · [Italiano](README.it.md) · [Dansk](README.da.md) · [Kalaallisut](README.kl.md) · [Todos los idiomas](#idiomas)

**Buques y barcos para Home Assistant, en un solo mapa.** Live Track Ships
pone en tu mapa de Home Assistant los buques, los barcos y todo lo demás que
emite AIS (la señal de radio con la que los buques dicen dónde están), cerca
de ti o en cualquier lugar del mundo que elijas. También sigue a los buques
que elijas, vayan donde vayan, y avisa a tus automatizaciones cuando un buque
entra en tu zona o sale de ella.

> **Live Track Ships es un módulo de Live Track**, una familia de
> integraciones de Home Assistant que dibujan todo lo que se mueve, y el
> tiempo que atraviesa, en un mapa compartido: aviones, buques, trenes y
> tiempo. Instálalo solo o junto a los demás módulos
> ([lista abajo](#parte-de-live-track-los-demás-módulos)).

> **Está creciendo, y las ideas son bienvenidas.** Hoy Live Track Ships cubre
> todo el mundo donde hay voluntarios con receptores, Finlandia y Noruega con
> más detalle, y tu propio receptor. Estamos añadiendo más fuentes de datos y
> países. ¿Falta el tuyo? [Sugiérelo](#ayúdanos-a-hacerlo-crecer), o añádelo
> tú mismo: te ayudaremos a hacerlo.

**Estado: 0.1.0, la primera versión.** Se añade al Marketplace por enlace
([abajo](#instalación-paso-a-paso)); todavía no está en el catálogo del
Marketplace.

Obra original de StrausbergAutomationWorks. Sin relación con, ni respaldo de,
aisstream.io, Fintraffic (Finlandia), BarentsWatch (Noruega), Wikidata,
Wikimedia Commons, VesselFinder, MarineTraffic, ningún armador ni ninguna
autoridad marítima.

> ⚠ **No es un sistema de seguridad.** Muestra datos públicos, a menudo con
> segundos de retraso y a veces con minutos, y solo lo que los receptores
> llegan a oír. No sirve para navegar, evitar colisiones ni ningún otro uso
> operativo. En el agua, usa tu propio AIS, radar, cartas náuticas y radio
> VHF.

---

## Contenido

1. [Todo lo que hace](#todo-lo-que-hace)
2. [Dónde funciona](#dónde-funciona)
3. [Parte de Live Track: los demás módulos](#parte-de-live-track-los-demás-módulos)
4. [Antes de empezar](#antes-de-empezar)
5. [Instalación, paso a paso](#instalación-paso-a-paso)
6. [Configuración, paso a paso](#configuración-paso-a-paso)
7. [Claves gratuitas que activan más, paso a paso](#claves-gratuitas-que-activan-más-paso-a-paso)
8. [Poner el mapa en un panel](#poner-el-mapa-en-un-panel)
9. [Usarlo en automatizaciones](#usarlo-en-automatizaciones)
10. [Todo lo que hay en el mapa, en detalle](#todo-lo-que-hay-en-el-mapa-en-detalle)
11. [Todas las entidades que crea](#todas-las-entidades-que-crea)
12. [Qué envía y descarga](#qué-envía-y-descarga)
13. [Ayúdanos a hacerlo crecer](#ayúdanos-a-hacerlo-crecer)
14. [Idiomas](#idiomas)
15. [Créditos y licencias](#créditos-y-licencias)
16. [Palabras clave](#palabras-clave)

---

## Todo lo que hace

### En el mapa, sin configurar nada

Añades una **zona**: un centro y un radio en el mapa, y una fuente de datos.
Todo lo de abajo aparece entonces en esa zona. Fintraffic Digitraffic
(Finlandia) y tu propio receptor no necesitan clave; aisstream.io y
BarentsWatch (Noruega) necesitan una gratuita
([abajo](#con-tu-propia-clave-o-cuenta-gratuita)).

| Qué | Dónde | De dónde |
|---|---|---|
| **Buques**: cargueros, petroleros, ferris, remolcadores, pesqueros, embarcaciones de recreo y veleros, cada uno con su propio dibujo, girado según su rumbo | en cada zona | la fuente que elijas |
| **Lo que no es un buque**: boyas de artes de pesca, ayudas a la navegación, estaciones base AIS, aeronaves de búsqueda y rescate y radiobalizas de socorro | en cada zona, cuando la fuente los envía | la fuente que elijas |
| **Fotos y enlaces**: una foto del buque cuando se conoce una, y un enlace al buque en VesselFinder | cada buque con número IMO o MMSI | Wikidata y Wikimedia Commons |
| **Rastros**: por dónde ha pasado un buque en las últimas 24 horas, dibujado cuando lo pides | cada buque | guardado por tu propio Home Assistant |
| **Buques de guardacostas en tareas de inmigración**, dibujados con los colores de los guardacostas | donde se los oiga | la lista pública EnforcementVessels |
| **Llegadas y salidas**: un evento para tus automatizaciones cuando un buque entra en una zona o sale de ella | en cada zona | calculado por tu propio Home Assistant |

### Con tu propia clave o cuenta gratuita

| Clave o cuenta gratuita | Qué añade |
|---|---|
| Clave de **aisstream.io** | buques en cualquier lugar del mundo donde haya voluntarios con receptores; y **buques vigilados**: buques elegidos, seguidos estén donde estén, con un evento cuando uno llega, sale, deja de oírse o cambia de destino |
| Cuenta de **BarentsWatch** (Noruega) | buques en aguas noruegas, Svalbard incluido, con nombre y tipo de buque en cada posición |

Cada una se consigue en pocos minutos: [paso a paso abajo](#claves-gratuitas-que-activan-más-paso-a-paso).

---

## Dónde funciona

| Región | Qué obtienes | De dónde | Necesita |
|---|---|---|---|
| **Todo el mundo** | buques donde hay voluntarios con receptores: bien cerca de costas y puertos concurridos, poco o nada en otros sitios | aisstream.io | una clave gratuita |
| **Europa**: Finlandia y el mar Báltico | buques en aguas finlandesas y bálticas, posiciones nuevas cada minuto | Fintraffic Digitraffic (Finlandia) | nada |
| **Europa**: Noruega | buques en aguas noruegas, Svalbard incluido, con nombre y tipo en cada posición | BarentsWatch (Noruega) | una cuenta gratuita |
| **Tu propio receptor**: en cualquier lugar | todo lo que oye tu antena, sin internet | tu propio receptor AIS | un receptor que envíe NMEA por UDP |

Eliges una fuente para cada zona. Qué tipos de cosas aparecen, lo recientes
que son las posiciones y lo completos que son los datos de los buques dependen
de esa fuente.

⚠ **La cobertura es buena donde hay receptores y no existe donde no los hay.**
Ningún ajuste puede crear una cobertura que no existe. Medido el 2026-09-02
con aisstream.io alrededor de Chicago (Estados Unidos): 100 buques en
120 segundos en los Grandes Lagos, pero ningún buque en una hora en los
canales al sur de la ciudad, por donde sí circulan convoyes de barcazas: los
servicios comerciales los ven por satélite, y eso no lo ofrecen las fuentes
gratuitas. **Que no haya buques en tu zona puede significar que no hay
receptores, no que no haya barcos.** Comprueba que tu fuente cubre tus aguas
antes de dar algo por roto.

⚠ **Tu propio receptor:**

* Una zona escucha en un puerto. Dos receptores necesitan dos puertos.
* Todo lo que el receptor oye dentro de tu círculo se muestra, incluidas las
  ayudas a la navegación y las estaciones base. Su sensor de estación también
  cuenta lo que oye fuera del círculo.
* Una sentencia NMEA no lleva fecha, así que la hora de una posición es la
  hora en que Home Assistant la recibió.
* La velocidad de giro no se muestra para esta fuente.
* Hasta ahora se ha probado con sentencias grabadas enviadas por UDP, no con
  un receptor. Si lo pruebas con el tuyo,
  [cuéntanos cómo fue](#ayúdanos-a-hacerlo-crecer).

¿No está en la lista? [Cuéntanoslo](#ayúdanos-a-hacerlo-crecer). Donde alguien
publique los datos abiertamente, estudiaremos añadirlos.

---

## Parte de Live Track: los demás módulos

Live Track es un conjunto de integraciones de Home Assistant, una por cada
tipo de cosa que se mueve, todas dibujadas en la misma tarjeta de mapa. Cada
una funciona sola; juntas forman una sola imagen en vivo. Comparten la tarjeta
de mapa y una biblioteca de Python
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
así que instalar otra no añade peticiones a una fuente que otra ya lee.

| Módulo | Qué pone en el mapa | Estado |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | aviones sobre ti por ADS-B, con rutas e iconos por tipo | publicado |
| **Live Track Ships** | buques y barcos por AIS, cerca de ti o en cualquier lugar (este módulo) | publicado |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | trenes de cercanías en Norteamérica, Europa y Australia | publicado |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | trenes interurbanos y de larga distancia en Norteamérica, Europa y Australia | publicado |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | aviones y buques de inmigración y de las fuerzas federales del orden, a partir de listas públicas | publicado |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | tiempo, tormentas y riesgos naturales | publicado |
| Live Track Stations | paneles de salidas y avisos de "hora de salir" para cada estación | previsto |
| Live Track Satellites | satélites que pasan sobre ti | previsto |
| Live Track Freight Trains | trenes de mercancías y de obras donde los ferrocarriles los publican | previsto |
| Live Track Transit | autobuses urbanos, tranvías, ferris y metro | previsto |
| Live Track Intercity Buses | autocares interurbanos y regionales | previsto |
| Live Track Commuter Buses | autobuses de cercanías | previsto |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | la tarjeta de mapa compartida en la que dibuja cada módulo | publicada, instalada con cada módulo |

Todo es gratuito y de código abierto. Nada se reserva para patrocinadores.

---

## Antes de empezar

* **Home Assistant** 2026.11 o posterior.
* **El Marketplace** (HACS) en tu Home Assistant, para instalarlo y
  actualizarlo de forma sencilla. Sin él puedes copiar los archivos a mano.
* **Acceso a internet** para Home Assistant, para las fuentes en línea y las
  fotos. Tu propio receptor funciona sin él.
* **Una fuente de datos.** Digitraffic (Finlandia) y tu propio receptor no
  necesitan cuenta. aisstream.io y BarentsWatch (Noruega) necesitan una clave
  gratuita
  ([paso a paso](#claves-gratuitas-que-activan-más-paso-a-paso)).
* **Opcional: tu propio receptor AIS.** El receptor, o el programa que lo
  decodifica, envía sentencias NMEA (`!AIVDM`) por UDP a la dirección de tu
  Home Assistant, en la misma red. En AIS-catcher es `-u <address> <port>`;
  en rtl-ais, `-h <address> -P <port>`; OpenCPN y Signal K lo añaden como
  conexión de salida UDP. Un receptor que se conecta por USB, como un dAISy,
  necesita uno de esos programas para pasar sus sentencias.
* **Opcional: auto-entities** del Marketplace, para poner los marcadores en
  el mapa (consulta [Poner el mapa en un panel](#poner-el-mapa-en-un-panel)).
* Nada que pagar. Digitraffic y tu propio receptor no necesitan cuenta; las
  claves gratuitas solo hacen falta para aisstream.io y BarentsWatch.

---

## Instalación, paso a paso

### Desde el Marketplace (recomendado)

Live Track Ships todavía no está en el catálogo del Marketplace. Añádelo por
su enlace:

1. En Home Assistant, abre **Configuración → Marketplace** (HACS).
2. Elige **Añadir desde un enlace** (o el menú de tres puntos →
   **Repositorios personalizados**).
3. Escribe `StrausbergAutomationWorks/LiveTrackShips`. Si te pide el tipo,
   elige **Integración**.
4. Busca **Live Track Ships** en la lista y elige **Descargar** o
   **Instalar**.
5. **Reinicia Home Assistant**: **Configuración → Sistema → Reparaciones**
   ofrece el reinicio, o usa **Configuración → Sistema → Reiniciar**.

### A mano

1. Descarga el código fuente de la
   [última versión](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest).
2. Copia su carpeta `custom_components/live_track_ships` en la carpeta
   `custom_components` de la carpeta de configuración de tu Home Assistant
   (crea `custom_components` si no existe).
3. Reinicia Home Assistant.

---

## Configuración, paso a paso

1. Abre **Configuración → Dispositivos y servicios**.
2. Elige **Añadir integración** (abajo a la derecha) y busca **Live Track
   Ships**.
3. Elige **Todos los buques de una zona**. (La otra opción, **Buques
   elegidos, estén donde estén**, sigue una lista de buques en cualquier
   lugar: consulta
   [Buques vigilados](#buques-vigilados-buques-elegidos-en-cualquier-lugar).)
4. **Fuente de datos**: elige una. Si no estás seguro: en Finlandia,
   Fintraffic Digitraffic, que no necesita clave; en Noruega, BarentsWatch; en
   cualquier otro lugar, aisstream.io.
5. **Clave de API** (aisstream.io), o **ID de cliente** y **Secreto de
   cliente** (BarentsWatch): pégalos
   ([cómo conseguirlos](#claves-gratuitas-que-activan-más-paso-a-paso)). Una
   zona que ya hayas configurado los rellena por ti.
6. **Puerto UDP (tu propio receptor)**: solo para tu propio receptor. Escribe
   el puerto al que envía, de 1024 a 65535. Deja 10110 si no lo cambiaste.
7. **Centro**: arrastra el marcador al centro de las aguas que quieras
   vigilar. Empieza en tu casa.
8. **Radio (km)**: de 1 a 500 km (0,6 a 310 millas). Si no estás seguro,
   deja 50 km (31 millas).
9. **Máximo de buques seguidos**: deja 1.000, salvo que tu equipo sea
   pequeño.
10. Elige **Enviar**.

Eso es todo. Los buques aparecen en uno o dos minutos, según los envía la
fuente. Los tipos y tamaños se completan en los minutos siguientes. Cada zona
es una entrada, titulada *Ships near <latitude>, <longitude>*. Añade más zonas
de la misma forma.

* La misma fuente no puede vigilar dos veces el mismo centro.
* Si al menos el 5 % de un círculo de BarentsWatch queda fuera de las aguas
  que publica BarentsWatch, el diálogo dice cuánto antes de crear la zona.
  Elige **Enviar** para conservar ese círculo de todos modos.

### Cambiar lo que muestra: las opciones

Abre **Configuración → Dispositivos y servicios → Live Track Ships →
Configurar** (el engranaje) en la zona que quieras cambiar. Cada opción, en
palabras sencillas:

| Opción | Qué hace | Por defecto |
|---|---|---|
| **Centro** | mueve la zona; se renombra según su nueva posición y se recarga | tu casa |
| **Radio (km)** | hasta qué distancia del centro se muestran los buques, de 1 a 500 km (0,6 a 310 millas) | 50 km (31 millas) |
| **Máximo de buques seguidos** | un límite de seguridad para esta zona, de 1 a 5.000; si hay más, se conservan los más cercanos | 1.000 |
| **Máximo de buques en el mapa, todas las entradas de Live Track Ships juntas** | el tope para todas tus zonas juntas, de 100 a 2.500; bájalo en un equipo pequeño; se aplica el ajuste más bajo de todas las zonas | 2.500 |
| **Puerto UDP (tu propio receptor)** | el puerto al que envía tu receptor; cambiarlo recarga la zona | 10110 |

Cuántos buques hay en un círculo depende mucho más de qué aguas sean que de su
tamaño. En las pruebas, un círculo de 50 km (31 millas) tenía unos 4 buques
sobre Chicago (Estados Unidos) y unos 340 sobre el Solent (Inglaterra): el
mismo radio, unas 80 veces más tráfico. Cuando un límite recorta la lista, el
`sensor.ships_in_range` de la zona lo indica.

---

## Claves gratuitas que activan más, paso a paso

Todas son gratuitas y personales: cada persona que instala Live Track Ships
consigue las suyas. Pega cada una en el diálogo de configuración cuando
añadas una zona (paso 5 de la [configuración](#configuración-paso-a-paso)).

### aisstream.io (buques y buques vigilados, todo el mundo)

1. Abre <https://aisstream.io/account> e inicia sesión. (El enlace
   **API keys** de la parte superior de aisstream.io abre la misma página.)
2. Crea allí una nueva clave de API.
3. Copia la clave en el momento: aisstream.io solo la muestra una vez.
4. Pégala en **Clave de API**.

⚠ aisstream.io permite tres conexiones por cuenta y tres por dirección de
internet pública. Live Track Ships usa como mucho dos: una para todas tus
zonas y otra para tus buques vigilados, que comparte con Live Track SALT si
está instalado con la misma clave. Si otros programas usan la misma clave o la
misma conexión a internet, cuéntalos también.

### BarentsWatch (buques en aguas noruegas, Noruega)

1. Abre <https://www.barentswatch.no/minside/> y crea un usuario, o inicia
   sesión.
2. En **API access (for developers)** (*API-tilgang (for utviklere)*), elige
   **New Client** (*Ny klient*).
3. Elige el cliente AIS, no el cliente API.
4. Copia el **ID de cliente**. Tiene este aspecto:
   `your.email@example.com:live_track_ships`. Pégalo tal cual en **ID de
   cliente**.
5. Copia el **secreto de cliente** en **Secreto de cliente**. Solo se muestra
   una vez; si no lo guardaste, genera uno nuevo.

---

## Poner el mapa en un panel

El mapa es [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
la tarjeta en la que dibuja cada módulo de Live Track. **Se instala con Live
Track Ships**: nada que descargar, nada que copiar, ningún recurso que añadir.

1. Abre un panel, elige el lápiz (**Editar panel de control**) y luego
   **Añadir tarjeta**.
2. Desplázate hasta abajo y elige **Manual**.
3. Pega esto y elige **Guardar**:

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

Los marcadores necesitan
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities) del
Marketplace. Si tienes otros módulos de Live Track instalados, añade un filtro
`- domain: geo_location` más por cada una de sus fuentes
(`live_track_aircraft`, `live_track_weather` y así sucesivamente).

**En el mapa:**

* Cada buque se dibuja con su propio dibujo, girado según su rumbo, y se
  desliza entre sus posiciones notificadas siguiendo el agua en lugar de
  cruzar la tierra.
* **Señala** un buque para ver su nombre, y su foto cuando la hay. **Haz
  clic** en él para ver su foto, sus enlaces, **Track** y **Details**
  ([Fotos y enlaces](#fotos-y-enlaces), [Rastros](#rastros)).
* La **tarjeta de filtro** (`custom:live-track-map-filter-card`) oculta los
  tipos de buque que desmarques
  ([Ocultar tipos de buque](#ocultar-tipos-de-buque)).

Si los recursos de tus paneles se definen en YAML
(`lovelace: resource_mode: yaml`), no se puede registrar nada por ti: un aviso
en **Reparaciones** te da entonces la línea exacta que debes añadir. Una
tarjeta que hayas instalado tú mismo desde el Marketplace no se toca. Si se
eliminan los archivos de la integración mientras sus zonas siguen
configuradas, y no hay otro módulo de Live Track instalado, elimina tú mismo
la línea de la tarjeta en **Configuración → Paneles de control → Recursos**.
Cualquier otra tarjeta de mapa que muestre entidades `geo_location` también
muestra los buques, sin sus dibujos.

---

## Usarlo en automatizaciones

Todo es una entidad o un evento normal de Home Assistant, así que el editor de
automatizaciones funciona con ello, sin código.

**Una notificación cuando un buque de más de 150 m (490 pies) entra en tu
zona:**

1. **Configuración → Automatizaciones y escenas → Crear automatización →
   Crear nueva automatización**.
2. **Cuando**: **Añadir disparador**, busca **Recibido evento manual** y
   escribe como **Tipo de evento** `live_track_ships_entry`.
3. **Y si**: **Añadir condición** → **Plantilla**, y escribe este **Valor de
   la plantilla**: `{{ trigger.event.data.length_m | default(0) > 150 }}`
4. **Entonces hacer**: **Añadir acción**, busca la acción de notificación de
   tu teléfono (lleva el nombre de tu teléfono) y escribe este mensaje:

   ```text
   {{ trigger.event.data.name | default('Un buque') }}, {{ trigger.event.data.length_m }} m, a {{ trigger.event.data.distance_km }} km
   ```

5. **Guardar**.

**Otras ideas:** encender una luz cuando el ferri de la tarde llega a tu
puerto en Noruega; un mensaje cuando el barco de un familiar, un buque
vigilado, vuelve a casa en Finlandia; una notificación cuando el crucero que
esperas llega a Sídney (Australia); el número de buques en tu puerto en un
panel, a partir de `sensor.ships_in_range`.

**Los eventos de zona.** Cada zona lanza `live_track_ships_entry` cuando un
buque entra en su círculo y `live_track_ships_exit` cuando sale. Se avisa de
cada buque; tu automatización elige los que importan. Los campos usan los
mismos nombres y unidades que los atributos del buque, y omiten lo que la
fuente no envió:

| Campo | Qué contiene |
|---|---|
| `area_id`, `area` | el ID de la entrada de configuración de la zona y su título |
| `identity` | el MMSI |
| `name`, `call_sign`, `imo` | si se envían |
| `object_kind` | `vessel`, `net_buoy`, `aton`, `base_station`, `sar_aircraft` o `distress_beacon` |
| `ship_type`, `ship_type_label`, `length_m`, `beam_m`, `draught_m`, `destination`, `nav_status` | solo buques, si se envían |
| `speed_kmh`, `course_deg`, `heading_deg` | si se envían |
| `latitude`, `longitude`, `distance_km`, `bearing_from_centre_deg`, `last_seen` | dónde se oyó, desde el centro de la zona |
| `entity_id` | solo al entrar: `geo_location.vessel_<MMSI>`, cuando el buque está en el mapa |
| `reason` | solo al salir: `left` (oído fuera del círculo) o `silent` (no se oye desde hace un rato, así que quizá siga ahí) |

⚠ Cuatro cosas que conviene saber:

* **Solo se avisa de una llegada si el buque se oyó antes fuera del
  círculo.** Un buque que se oye primero dentro quizá estuvo ahí todo el
  tiempo: tras un reinicio, las fuentes siguen entregando durante muchos
  minutos buques que no se han movido. Así que no se avisa de un buque que
  los receptores no oyeron al entrar, ni de uno que enciende su transpondedor
  dentro.
* **Siempre se avisa de una salida oída fuera**, incluso de un buque que ya
  estaba antes de que arrancara Home Assistant. De un buque que deja de oírse
  solo se avisa como salida (`reason: silent`) si se avisó de su llegada.
* **Una salida espera 2 minutos.** Un buque que vuelve antes, bordeando el
  círculo, no se anuncia como salida y nueva llegada.
* **Pueden faltar datos a la llegada.** El nombre, el tipo y el tamaño viajan
  en un mensaje más lento que la posición. Un buque que se oye por primera vez
  puede llegar con una posición y nada más.

Dos zonas sobre las mismas aguas lanzan cada una sus propios eventos. Los
límites de cuántos buques se dibujan nunca hacen que un buque entre o salga.

**El evento de los buques vigilados.**
[Los buques vigilados](#buques-vigilados-buques-elegidos-en-cualquier-lugar)
lanzan un evento, `live_track_ships_watched`, cuyo `change` dice qué ha
pasado:

| `change` | Cuándo |
|---|---|
| `arrived` | el buque se declara amarrado o fondeado o, sin estado, se mantiene por debajo de 3,7 km/h (2 nudos) |
| `departed` | vuelve a navegar |
| `silent` | no se oye desde hace 30 minutos (6 horas si está amarrado o fondeado); sale del mapa, y quizá siga ahí |
| `heard` | se vuelve a oír tras `silent` |
| `destination` | la tripulación cambió el destino; `destination_previous` guarda el anterior |

Los datos llevan `watch_id`, `watch`, `identity`, tu `label` y los mismos
campos de buque que los eventos de zona, con la distancia y la demora desde tu
casa. La llegada y la salida esperan a que el nuevo estado se haya mantenido
5 minutos según el propio reloj del buque, para que un barco que deriva
despacio no cambie de un estado a otro sin parar. No se avisa de nada a partir
de la primera posición de un buque tras un reinicio: esa fija el punto de
partida. Los destinos los escribe la tripulación y a menudo están
desactualizados.

---

## Todo lo que hay en el mapa, en detalle

AIS (Automatic Identification System, sistema de identificación automática)
es una emisión de radio VHF con la que los buques comunican su posición, su
identidad y su viaje a otros buques y a tierra. Es la versión marítima de lo
que los aviones envían como ADS-B. Los buques comerciales deben llevarlo;
muchas embarcaciones de recreo lo llevan por elección, normalmente como un
equipo de clase B de menor potencia. AIS se emite en abierto: cualquiera con
un receptor puede oírlo, y hay servicios públicos que lo retransmiten. **Live
Track Ships muestra todo lo que envía la fuente.** No se filtra nada, y no hay
ningún ajuste para ocultar una categoría a Home Assistant.

### Buques

Cada buque es un marcador cuyo estado es su distancia al centro de la zona, en
kilómetros. La mayoría de los buques se dibujan según su tipo: carguero,
petrolero, ferri, remolcador, etc. Algunos tienen su propio dibujo: yates
reales y de Estado, y barcos conocidos como los barcos turísticos, los taxis
acuáticos y los barcos de bomberos de una ciudad. ¿Conoces un buque que
merezca uno, en cualquier parte del mundo? [Sugiérelo](#ayúdanos-a-hacerlo-crecer),
con su nombre y su número MMSI o IMO, y una foto o un enlace si los tienes.

Para que un buque desaparezca en cuanto se va, a cada fuente en línea se le
pide un anillo algo más ancho que tu círculo (un 10 %, al menos 1 km), y tu
propio receptor envía todo lo que oye. Solo se conservan los buques dentro de
tu círculo: un buque oído fuera sale del mapa enseguida. Un buque que no se
vuelve a oír desaparece tras un tiempo de silencio. Un buque que deja de
aparecer no se ha ido necesariamente: ninguna de estas fuentes promete
entregar cada mensaje.

⚠ **El tipo de buque suele faltar, sobre todo en barcos pequeños.** La
posición y el nombre llegan con casi cada mensaje. El tipo y el tamaño llegan
en un mensaje aparte, más lento, que muchos equipos de clase B envían pocas
veces. Cuenta con que muchos buques, entre ellos la mayoría de los barcos
pequeños, no muestren tipo ni tamaño, y con que todos tengan pocos datos
durante varios minutos tras reiniciar Home Assistant. Son los datos, no un
fallo. Los tipos y tamaños oídos una vez se conservan entre reinicios.

Los atributos de un buque incluyen su nombre, MMSI, indicativo de llamada,
velocidad, rumbo, proa, eslora, manga, tipo, destino, `object_kind`,
`last_seen` y `attribution`, cada uno solo si la fuente lo envió. Un buque que
ven dos zonas es una sola entidad.

### Barcos privados y veleros

Una embarcación de recreo que emite AIS aparece en tu mapa exactamente igual
que un carguero. Según lo que emita el barco, su entidad puede llevar:

* su **nombre**, que también es la etiqueta dibujada en el mapa;
* su **MMSI** y su **indicativo de radio**, ambos permanentes y consultables
  públicamente;
* su **posición** con una precisión de un metro aproximadamente, su posición
  anterior y cuándo se oyó cada una;
* su velocidad, rumbo y proa, y su eslora, manga y tipo, si se envían.

Un barco que deja el transpondedor encendido en el pantalán sigue en el mapa
en su amarre mientras emita. Cualquiera que pueda abrir tu mapa también puede
pulsar **Track** en ese barco y ver por dónde ha pasado en las últimas
24 horas (o el tiempo que configures), su amarre incluido.

No existe una lista de exclusión para AIS, como la hay para los aviones, y
esta integración no se inventa una. Si quieres menos barcos privados en tu
mapa, reduce el radio.

### Lo que no es un buque

Cada entidad lleva `object_kind`: `vessel`, `net_buoy` (boya de artes de
pesca), `aton` (ayuda a la navegación: una boya, una baliza o un faro),
`base_station` (una estación AIS en tierra), `sar_aircraft` (una aeronave de
búsqueda y rescate) o `distress_beacon`. La mayoría se distinguen por el
formato de identidad que les asigna la Unión Internacional de
Telecomunicaciones (UIT). Las boyas de artes de pesca no: emiten con
identidades de buque, así que se reconocen por sus nombres de fábrica
(FISHING BOUY, NET MARK, BUOY) junto con la falta de una eslora emitida.

Todo lo que no es un buque se muestra sin tipo, tamaño ni estado de
navegación. Las boyas de artes de pesca derivan con sus líneas, así que
conservan su velocidad y su rumbo, y se dibujan como un pez que apunta hacia
donde derivan.

Cuáles aparecen depende de la fuente. Medido una tarde:

| Fuente | Boyas de artes de pesca | Aeronaves de búsqueda y rescate | Ayudas a la navegación, estaciones base |
|---|---|---|---|
| BarentsWatch | sí | sí | ninguna vista |
| Digitraffic | ninguna vista | sí | ninguna vista |
| aisstream.io | ninguna vista | ninguna vista | ninguna vista |
| Tu propio receptor | lo que oiga | lo que oiga | lo que oiga |

aisstream.io solo entregó posiciones y datos de buques, tanto sobre los
Grandes Lagos (Norteamérica) como sobre las mismas aguas noruegas y danesas
donde BarentsWatch muestra las boyas.

### Buques de guardacostas en tareas de inmigración

Un buque de la lista pública
[EnforcementVessels](https://github.com/StrausbergAutomationWorks/EnforcementVessels)
(buques de la Guardia Costera de Estados Unidos empleados en tareas de
inmigración) se dibuja con los colores de la Guardia Costera, con el nombre y
el organismo de la lista, dondequiera que se le oiga.

### Buques vigilados: buques elegidos en cualquier lugar

Además de las zonas, puedes seguir una lista de buques estén donde estén: el
barco de un familiar, un ferri que tomas, un crucero que vuelve a casa.
Necesita una clave de aisstream.io, y hay una sola lista así por cada Home
Assistant.

1. Abre **Configuración → Dispositivos y servicios**, elige **Añadir
   integración** y busca **Live Track Ships**.
2. Elige **Buques elegidos, estén donde estén**.
3. **Clave de API**: la clave de una zona que ya configuraste aparece
   rellenada.
4. **Buques**: un buque por línea, su MMSI de 9 cifras y, si quieres, un
   nombre tuyo:

   ```text
   244650000 El barco de papá
   366999999 El ferri
   ```

5. Elige **Enviar**.

Como mucho 100 buques. aisstream.io sigue como mucho 200 MMSI por clave, y
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
si está instalado con la misma clave, usa parte de ellos. Una lista que los
superara se rechaza al cargar la entrada, con el motivo. Para cambiar la
lista, abre **Configurar** en la entrada.

Un buque vigilado se dibuja en el mapa como cualquier otro, dondequiera que se
le oiga, y su estado es su distancia a tu casa. Una zona que ya lo muestra lo
conserva: un buque, un marcador. La entrada añade `sensor.watched_vessels`:
cuántos de los buques de la lista se oyen ahora. Su atributo `vessels` los
enumera todos, con su nombre y su último estado conocido. Su evento se
describe en [Usarlo en automatizaciones](#usarlo-en-automatizaciones).

### Fotos y enlaces

Cuando un buque envía un número IMO y Wikidata conoce una foto de ese buque en
Wikimedia Commons, el buque lleva `marker_photo`. El mapa muestra la foto
cuando señalas el buque, con el fotógrafo y la licencia; un clic la abre más
grande, con enlaces a la página de la foto y a su licencia. Cada buque con
número IMO o MMSI lleva también `marker_links`, un enlace al buque en
VesselFinder. El botón **Details** de la ventana emergente abre el diálogo
habitual del buque.

Tu Home Assistant pregunta él mismo a Wikidata y a Commons, 20 números IMO a
la vez, con diez segundos de separación, y guarda cada respuesta 30 días
(14 días cuando no hay foto) en `.storage/saw_vessel_photos.json`. Cuenta con
fotos para uno de cada diez buques aproximadamente: en nuestro sistema de
pruebas, 49 de 521 números IMO tenían una.

⚠ Una foto puede mostrar el buque con un nombre anterior: el número IMO
pertenece al casco y lo acompaña cuando el buque cambia de nombre.

### Rastros

Cada buque lleva también `marker_track`. Haz clic en un buque y pulsa
**Track** en su ventana emergente: el mapa dibuja por dónde ha pasado, como
una línea que termina en el buque, y la línea crece mientras miras.
**Hide track** la quita. No se dibuja nada hasta que lo pides, para que un
puerto concurrido no desaparezca bajo las líneas.

El rastro solo contiene las posiciones que el buque notificó mientras estaba
en tu mapa, reducidas a una cada 25 m (82 pies) o cada 10 minutos, y nunca dos
en menos de 30 segundos. Tu Home Assistant lo guarda en memoria y en
`.storage/saw_vessel_tracks.json`, así que sobrevive a un reinicio. Cubre las
últimas 24 horas. Para guardar más o menos:

1. Abre **Configuración → Herramientas → Acciones**.
2. Elige la acción **Live Track Ships: Fijar las horas de rastro**.
3. Escribe **Horas**, de 1 a 168 (una semana), y elige **Realizar una
   acción**.

Se aplica a todas las zonas a la vez; un ajuste más corto borra en el acto
las posiciones más antiguas.

⚠ El rastro empieza vacío en una primera instalación. Un buque que salió de la
zona o dejó de oírse tiene un hueco, dibujado como una línea recta entre las
posiciones de antes y de después.

### Ocultar tipos de buque

Cada buque lleva `marker_group`, `marker_group_label` y
`marker_group_order`: uno de trece grupos (carga; petrolero; pasaje y ferri;
pesca; recreo y vela; remolcador, práctico y servicio portuario; Estado,
búsqueda y rescate y fuerzas del orden; alta velocidad y otros; tipo no
enviado; boyas de artes de pesca; ayudas a la navegación; estaciones base;
aeronaves de búsqueda y rescate). La tarjeta de filtro de la tarjeta de mapa,
`custom:live-track-map-filter-card`, enumera los grupos con cuántos de cada
uno hay en el mapa, y oculta los que desmarques. Ponla en cualquier vista del
panel. Tu elección se guarda solo en ese navegador.

Ocultar solo afecta al mapa: la integración sigue contando cada buque y lanza
sus eventos para cada buque. Una radiobaliza de socorro no tiene grupo, así
que nunca se oculta.

---

## Todas las entidades que crea

| Entidad | Qué es |
|---|---|
| `geo_location.vessel_<MMSI>` | un marcador por cada buque u otro objeto AIS; su estado es la distancia al centro de la zona (o a tu casa, para un buque vigilado), en kilómetros. Aparece y desaparece, y no tiene ID único |
| `sensor.ships_in_range` | uno por zona: cuántos buques muestra, y si un límite recortó la lista |
| `sensor.ais_station` | solo tu propio receptor: mensajes por minuto. Sus atributos dan `vessels_heard` (en los últimos 10 minutos), `farthest_km` y `farthest_mmsi` (desde el centro de la zona), `last_message`, `udp_port`, `listening`, y `port_error` cuando el puerto no se puede abrir. Se actualiza cada 30 segundos, así que un receptor que deja de enviar muestra 0 |
| `sensor.watched_vessels` | solo buques vigilados: cuántos de los buques de tu lista se oyen ahora |

Los atributos que cambian en cada actualización se mantienen fuera del
historial de Home Assistant, para que tu base de datos no crezca con ellos:
`marker_photo`, `marker_links` y `marker_track` de cada buque, y los atributos
de los sensores que cambian rápido.

**Tu base de datos.** El registrador de Home Assistant guarda una fila nueva
cada vez que una entidad cambia, y un buque en movimiento cambia con cada
posición que notifica. En nuestro sistema de pruebas, una zona con 43 buques
escribió 27.109 filas en unas 30 horas, el 8,8 % de toda la base de datos. Por
defecto, el registrador guarda 10 días y limpia cada noche a las 04:12 hora
local, así que el crecimiento se estabiliza, pero en un tamaño que quizá no
quieras.

Un buque conserva el mismo ID de entidad, `geo_location.vessel_<MMSI>`, cada
vez que aparece, así que un solo patrón, `geo_location.vessel_*`, cubre todo
lo que esta integración ha puesto alguna vez en el mapa. Para guardar solo el
último día:

1. **Configuración → Automatizaciones y escenas → Crear automatización →
   Crear nueva automatización**.
2. Abre el menú de tres puntos, elige **Editar en YAML**, sustituye todo por
   esto y elige **Guardar**:

```yaml
alias: Recortar el historial de buques
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

Si omites `keep_days` (0 por defecto), todas sus filas se borran de golpe.
Para no registrar nada, pon el patrón en `configuration.yaml` bajo
`recorder:` → `exclude:` → `entity_globs:`; una tarjeta de mapa configurada
para dibujar el historial (`history_start`) no tendrá entonces ningún rastro
que dibujar. `sensor.ships_in_range` es un simple número y cuesta poco
conservarlo.

---

## Qué envía y descarga

**Sobre tu ubicación.** El centro de cada zona es tu casa, salvo que lo
muevas. Solo se envía a la fuente que elegiste para esa zona: a aisstream.io
como un rectángulo alrededor de un círculo algo mayor que el tuyo (un 10 %, al
menos 1 km); a Digitraffic (Finlandia) como el centro y ese radio mayor; a
BarentsWatch (Noruega) como ese círculo mayor. Para los buques vigilados, los
números MMSI de tu lista se envían a aisstream.io. Tu propio receptor no envía
nada a ninguna parte: Home Assistant solo escucha. Para las fotos, los números
IMO de los buques de tu mapa se envían a Wikidata y a Wikimedia Commons, sin
nada sobre ti. Para detener todo esto, borra la zona o la entrada de buques
vigilados en **Configuración → Dispositivos y servicios → Live Track Ships**.
No se envía nada más sobre ti a ninguna parte.

**Cuánto.**

* **aisstream.io**: una conexión para todas tus zonas y otra para tus buques
  vigilados, ambas abiertas; los buques llegan a medida que informan. Tras un
  error, se vuelve a conectar después de una pausa.
* **Digitraffic**: posiciones cada 60 segundos y datos de los buques cada
  15 minutos, solo para tu círculo. Tras un error, lo vuelve a intentar en la
  siguiente ronda.
* **BarentsWatch**: un flujo abierto por zona. Si no llega nada en
  150 segundos, se vuelve a conectar.
* **Fotos**: 20 números IMO a la vez, con 10 segundos de separación, solo
  para buques por los que no se preguntó en los últimos 30 días (14 si no
  había foto). Una petición fallida se repite más tarde.
* **Tu propio receptor**: no se descarga nada.

---

## Ayúdanos a hacerlo crecer

Live Track Ships sigue creciendo. Añadimos fuentes de datos y países a medida
que los encontramos, y queremos saber qué te gustaría a continuación.

### Sugerir algo

¿Falta tu país o tu servicio AIS? ¿Hay algo mal, o difícil de entender?
Cuéntanoslo de la forma que te resulte más fácil:

* [**Rellena un formulario corto**](https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues/new?template=es.yml)
  en español. Necesitas una cuenta gratuita de GitHub.
* **Escribe un correo** a
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  No hace falta cuenta.

En cualquier caso, ayuda que nos digas:

* qué te gustaría ver, y en qué parte del mundo;
* un enlace a donde se publican los datos, si conoces uno (una página de
  datos abiertos, un canal público, la web de un servicio): no es necesario,
  pero ayuda;
* el idioma de tu Home Assistant, si el problema es la redacción o una
  traducción.

Escribe en inglés o en tu propio idioma, lo que te resulte más fácil.

### Añadirlo tú mismo, con nuestra ayuda

Si quieres añadir algo tú mismo, te ayudaremos a hacerlo, desde la primera
pregunta hasta la versión terminada. No necesitas ser desarrollador para
empezar:

* **Una traducción.** Los textos del diálogo de configuración son una lista
  corta de frases en un archivo de texto. Te mostraremos qué archivo y qué
  líneas.
* **Una nueva fuente de datos.** Dinos dónde se publican los datos. Podemos
  escribir el código juntos, o revisar el tuyo.
* **Probarlo donde vives.** Instálalo, mira tu parte del mapa y dinos qué está
  bien y qué no.
* **Una corrección de este README.** Si un paso no coincidía con lo que
  viste, dinos lo que viste.

[**Cuéntanos qué tienes en mente**](https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues/new?template=es.yml)
o escribe a
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
y te responderemos con los siguientes pasos.

---

## Idiomas

Este README: [English](README.md), [Deutsch](README.de.md),
[Français](README.fr.md), [Nederlands](README.nl.md),
[简体中文](README.zh-Hans.md), **Español**, [Italiano](README.it.md),
[Dansk](README.da.md) y [Kalaallisut](README.kl.md) (un borrador corto,
enviado para su revisión a Oqaasileriffik, la secretaría de la lengua de
Groenlandia; hasta entonces, la página danesa es la fiable). Cada README
traducido está completo.

El diálogo de configuración y las opciones aparecen en el idioma de tu Home
Assistant cuando es uno de estos: English, Dansk, Deutsch, Español, Français,
Gaeilge, Íslenska, Italiano, Nederlands, Norsk Bokmål, Polski, Português,
Português (BR), Suomi, Svenska y 简体中文. Cualquier otro idioma muestra el
inglés. El groenlandés (kalaallisut) aún no es un idioma de Home Assistant;
hemos pedido a Home Assistant que lo añada. Las etiquetas propias de la
tarjeta de mapa (**Track**, **Details**) están en inglés en todos los idiomas.

¿Has encontrado un error en una traducción, o necesitas otro idioma?
Cuéntanoslo en <https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues>,
o [tradúcelo con nuestra ayuda](#añadirlo-tú-mismo-con-nuestra-ayuda).

---

## Créditos y licencias

* **aisstream.io**: sin condiciones publicadas. <https://aisstream.io>
* **Fintraffic Digitraffic** (Finlandia): datos bajo CC BY 4.0.
  <https://www.digitraffic.fi/en/terms-of-service/>
* **BarentsWatch** (Noruega): datos bajo la licencia noruega de datos
  públicos abiertos (NLOD).
  <https://www.barentswatch.no/en/articles/api-terms-and-conditions/>
* **Tu propio receptor**: tus propios datos.
* **Wikidata**: CC0. **Wikimedia Commons**: cada foto bajo su propia licencia,
  mostrada con su fotógrafo y su licencia.
* **VesselFinder**: solo enlazado; no se descarga nada de allí.
* **EnforcementVessels**: ODbL 1.0.
  <https://github.com/StrausbergAutomationWorks/EnforcementVessels>

Lo que cambia esta integración: las unidades se convierten, y solo se
conservan los buques dentro de tu círculo. Cada entidad de buque, y el
`sensor.ships_in_range` de cada zona, lleva una `attribution` con el nombre de
su fuente; Home Assistant la muestra en los detalles de la entidad. Si
muestras estos datos a otras personas, por ejemplo en un panel público,
mantén el crédito con ellos y lee las condiciones de la propia fuente. Las
líneas de crédito exactas, y los créditos de los dibujos de los buques, están
en [ATTRIBUTION.md](ATTRIBUTION.md).

Ninguna de estas organizaciones ha hecho ni respaldado esta integración.

**Código**: MIT, en [LICENSE](LICENSE).

**Para desarrolladores:** las sentencias AIS de tu propio receptor las
decodifica [pyais](https://github.com/M0r13n/pyais) (MIT); Home Assistant
instala por sí mismo `saw-livetrack` y `pyais` la primera vez que carga la
integración. Las pruebas de `tests/` se ejecutan cada una por separado con
Python; algunas necesitan Home Assistant instalado, y las pruebas `*_live`
necesitan tus propias claves.

---

## Palabras clave

Home Assistant buques · Home Assistant AIS · seguimiento de barcos ·
seguimiento de buques · rastreo de embarcaciones · mapa de tráfico marítimo ·
tarjeta de mapa AIS · receptor AIS · NMEA · AIS-catcher · aisstream.io ·
Digitraffic · BarentsWatch · ship tracking · vessel tracker ·
Schiffsverfolgung · suivi des navires · scheepvaart volgen · tracciamento
navi · skibstrafik · 船舶追踪 · geo_location · tarjeta de mapa · Lovelace ·
HACS · Marketplace · Live Track · LiveTrack · StrausbergAutomationWorks
