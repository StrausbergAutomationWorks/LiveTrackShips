# Live Track Ships

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · [简体中文](README.zh-Hans.md) · **Español** · [Italiano](README.it.md) · [Dansk](README.da.md) · [Kalaallisut](README.kl.md) · [Todos los idiomas](#idiomas)

**Seguimiento AIS de buques, barcos y embarcaciones para Home Assistant.**
Los buques cerca de ti, o en cualquier lugar del mundo que elijas, como
marcadores en directo en tu mapa. Parte de Live Track: buques, aviones y
trenes en un solo mapa.

Datos AIS marítimos en directo de [aisstream.io](https://aisstream.io),
[Fintraffic Digitraffic](https://www.digitraffic.fi/en/marine-traffic/) o
[BarentsWatch](https://www.barentswatch.no/en/), mostrados como entidades
`geo_location` de Home Assistant y dibujados en el mapa compartido de Live
Track.

**Estado: 0.1.0, la primera versión.** Se añade al Marketplace por enlace
(más abajo); todavía no está en el catálogo del Marketplace.

## Qué es el AIS

El AIS (Automatic Identification System, sistema de identificación
automática) es una emisión de VHF con la que los buques anuncian su posición,
su identidad y su viaje a otros buques y a tierra. Es el equivalente marítimo
del ADS-B. Los buques comerciales están obligados a llevarlo; muchas
embarcaciones de recreo lo llevan voluntariamente, casi siempre como equipo de
clase B, de menor potencia.

El AIS se emite sin cifrar. Cualquiera con un receptor puede oírlo, y hay
agregadores públicos que lo vuelven a publicar.

## Qué se muestra

**Todo lo que envía la fuente.** No se filtra nada, y no hay ningún ajuste
para ocultar una categoría.

| En los datos | Se muestra |
|---|---|
| Cargueros, petroleros, remolcadores, ferris, buques de pasaje | sí |
| Pesqueros, prácticos, buques de las autoridades y otros barcos de trabajo | sí |
| **Embarcaciones de recreo privadas y veleros** | **sí, con nombre y posición** |
| **Boyas de artes de pesca** que emiten AIS | **sí, dibujadas como un pez** |
| Aeronaves de búsqueda y salvamento (SAR) | cuando la fuente las envía |
| Ayudas a la navegación: boyas, balizas, faros | cuando la fuente las envía |
| Estaciones base AIS en tierra | cuando la fuente las envía |

### Se ven las embarcaciones privadas, y conviene que sepas lo que eso supone

Una embarcación de recreo que emite AIS aparece en tu mapa exactamente igual
que un carguero. Según lo que emita, su entidad puede incluir:

- su **nombre**, que es también la etiqueta del mapa
- su **MMSI** y su **indicativo de llamada**, ambos permanentes y fáciles de
  buscar
- su **posición** con un metro de precisión aproximadamente, su posición
  anterior y cuándo se oyó cada una
- su velocidad, rumbo y proa, si los emite
- su eslora, manga y tipo, si los emite

Un barco que deja el transpondedor encendido en el amarre sigue en el mapa en
su atraque mientras siga emitiendo.

No existe para el AIS una lista de exclusión como la de los aviones, y esta
integración no se inventa una. Si quieres menos embarcaciones privadas en el
mapa, reduce el radio.

### A menudo falta el tipo de buque, sobre todo en barcos pequeños

La posición y el nombre llegan con casi todos los mensajes. El tipo y el
tamaño llegan en un mensaje aparte, menos frecuente, y muchos equipos de
barcos pequeños (clase B) rara vez envían la parte que los contiene. Cuenta con
que una buena parte de los buques, entre ellos casi todos los pequeños,
aparezca sin tipo ni dimensiones, y con que todos estén incompletos durante
unos minutos después de reiniciar Home Assistant. Son los datos, no un fallo.
Los tipos y tamaños ya oídos se conservan entre reinicios.

### No todo lo que emite AIS es un buque

Cada entidad lleva `object_kind`: `vessel`, `net_buoy`, `aton` (ayuda a la
navegación), `base_station`, `sar_aircraft` o `distress_beacon`. La mayoría se
distingue por el formato de identificador que les asigna la UIT. Las boyas de
artes de pesca no: emiten con identificadores de buque, así que se reconocen
por sus nombres de fábrica (FISHING BOUY, NET MARK, BUOY) junto con la falta
de una eslora emitida.

Todo lo que no es un buque se muestra sin tipo, tamaño ni estado de
navegación. Las boyas de artes de pesca derivan con sus líneas, así que
conservan velocidad y rumbo, y se dibujan como un salmón que apunta hacia
donde derivan.

Lo que aparece depende de la fuente. Medido una noche:

| Fuente | Boyas de artes de pesca | Aeronaves SAR | Ayudas a la navegación, estaciones base |
|---|---|---|---|
| BarentsWatch | sí | sí | ninguna vista |
| Digitraffic | ninguna vista | sí | ninguna vista |
| aisstream.io | ninguna vista | ninguna vista | ninguna vista |
| Tu propio receptor | lo que oiga | lo que oiga | lo que oiga |

aisstream.io solo entregó mensajes de posición y de datos del buque, tanto
sobre los Grandes Lagos como sobre las mismas aguas noruegas y danesas donde
BarentsWatch muestra las boyas.

## Fuentes

Eliges una fuente para cada zona que configuras.

| Fuente | Cobertura | Necesita |
|---|---|---|
| aisstream.io | todo el mundo, donde hay voluntarios con receptores | una clave API gratuita |
| Fintraffic Digitraffic | aguas finlandesas y bálticas | nada |
| BarentsWatch AIS Live | aguas noruegas | un ID de cliente y un secreto gratuitos |
| Tu propio receptor AIS | hasta donde oiga tu antena | un receptor que envíe NMEA por UDP |

Qué categorías aparecen, lo recientes que son las posiciones y lo completos
que son los datos de los buques depende de la fuente que elijas.

### Tu propio receptor

Si tienes un receptor AIS, Live Track Ships puede mostrar lo que oye, sin
cuenta y sin Internet. El receptor, o el programa que lo decodifica, envía
frases NMEA (`!AIVDM`) por UDP a la dirección de Home Assistant, en un puerto
que eliges tú (10110 si no lo cambias). En AIS-catcher es
`-u <address> <port>`; en rtl-ais, `-h <address> -P <port>`; OpenCPN y
Signal K lo añaden como conexión de salida UDP. Un receptor que se conecta
por USB, como un dAISy, necesita uno de esos programas para pasar sus frases.

- Una zona escucha en un puerto; dos receptores necesitan dos puertos.
- Se muestra todo lo que el receptor oye dentro de tu círculo, incluidas
  ayudas a la navegación y estaciones base. El sensor de estación (más abajo)
  cuenta también lo que oye fuera del círculo.
- Una frase no lleva fecha, así que la hora de una posición es cuando Home
  Assistant la recibió.
- La velocidad de giro no se muestra para esta fuente.
- Por ahora está probado con frases grabadas enviadas por UDP, no con un
  receptor. Si lo pruebas con el tuyo, cuéntanos cómo fue en la
  [página de issues](https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues).

### Atribución

Cada entidad de buque, y el sensor `ships_in_range` de cada zona, lleva un
atributo `attribution` con la fuente que lo proporcionó; Home Assistant lo
muestra en los detalles de la entidad. Dos de las fuentes ceden sus datos con
una licencia que pide citarlas, y Live Track Ships modifica lo que recibe
(unidades convertidas, solo los buques dentro de tu círculo), así que sus
líneas lo dicen. Si muestras estos datos a otros, por ejemplo en un panel
público, mantén la cita y lee las condiciones de la fuente:

- **aisstream.io**: no publica condiciones. <https://aisstream.io>
- **Fintraffic Digitraffic**: CC BY 4.0.
  <https://www.digitraffic.fi/en/terms-of-service/>
- **BarentsWatch**: licencia noruega de datos públicos abiertos (NLOD).
  <https://www.barentswatch.no/en/articles/api-terms-and-conditions/>
- **Tu propio receptor**: tus propios datos; su línea lo dice.
- **EnforcementVessels** (la lista que hay detrás del aspecto de guardacostas,
  más abajo): ODbL v1.0.
  <https://github.com/StrausbergAutomationWorks/EnforcementVessels>

Las líneas exactas están en [ATTRIBUTION.md](ATTRIBUTION.md).

## Requisitos

- Home Assistant 2026.11 o posterior, con salida a Internet para las fuentes
  en línea.
- Para aisstream.io: una clave API gratuita de
  [aisstream.io](https://aisstream.io/account). aisstream permite **tres
  conexiones por cuenta y tres por IP pública**; si usas otras herramientas
  con la misma clave, tenlo en cuenta. Live Track SALT, si está instalado, usa
  una segunda conexión con la misma clave.
- Para BarentsWatch: un ID de cliente y un secreto gratuitos, que registras tú
  mismo en BarentsWatch. Introduce el ID de cliente exactamente como te lo
  dieron.
- Para tu propio receptor: un receptor y un programa que envíen NMEA por UDP a
  Home Assistant, en la misma red. No necesita Internet.
- Home Assistant instala los paquetes de Python necesarios (`saw-livetrack` y
  `pyais`) la primera vez que carga la integración.

## Instalación

### Desde el Marketplace

Live Track Ships aún no está en el catálogo del Marketplace. Añádelo por
enlace:

1. **Ajustes > Marketplace** y luego **Añadir desde enlace**.
2. Introduce `StrausbergAutomationWorks/LiveTrackShips`. Si pregunta el tipo,
   elige **Integración**.
3. Instala **Live Track Ships**.
4. Reinicia Home Assistant. El Marketplace ofrece el reinicio como reparación
   en **Ajustes > Sistema > Reparaciones**.

### A mano

1. Descarga el código fuente de la
   [última versión](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest).
2. Copia su carpeta `custom_components/live_track_ships` en la carpeta
   `custom_components` del directorio de configuración de Home Assistant.
3. Reinicia Home Assistant.

## Configuración

**Ajustes > Dispositivos y servicios > Añadir integración > Live Track
Ships**, y luego **Todos los buques de una zona** (la otra opción, los buques
seguidos, está [más abajo](#buques-seguidos-sigue-buques-elegidos-en-cualquier-lugar)).
Cada zona es una entrada aparte, titulada *Ships near <latitud>, <longitud>*.
El diálogo aparece en español cuando Home Assistant está en español.

| Campo | Qué admite | Por defecto |
|---|---|---|
| Fuente de datos | aisstream.io, Fintraffic Digitraffic, BarentsWatch AIS Live o tu propio receptor AIS | aisstream.io |
| Clave API | solo aisstream.io. Se toma de una zona que ya configuraste; puedes cambiarla | vacía |
| ID de cliente, secreto de cliente | solo BarentsWatch. Se toman de una zona que ya configuraste | vacíos |
| Puerto UDP | solo tu propio receptor: el puerto al que envía NMEA, de 1024 a 65535. Se rechaza si otra zona u otro programa ya lo usa | 10110 |
| Centro | un marcador en un mapa; arrástralo al agua que quieres vigilar | tu casa |
| Radio (km) | de 1 a 500 | 50 |
| Número máximo de buques seguidos | de 1 a 5.000; un límite de seguridad para esta zona, se quedan los más cercanos | 1.000 |

Una misma fuente no puede vigilar dos veces el mismo centro. Cuando al menos
un 5 % de un círculo de BarentsWatch queda fuera de las aguas que publica
BarentsWatch, el diálogo dice cuánto antes de crear la zona; envíalo para
quedarte con ese círculo de todos modos.

**Ajustes de una zona** (Configurar en su entrada): el centro, con el mismo
marcador; el radio; el número máximo de buques seguidos; y *Número máximo de
buques en el mapa, todas las entradas de Live Track Ships juntas*, un control
deslizante de 100 a 2.500 en pasos de 100 (2.500 por defecto); y, para tu propio receptor, su puerto UDP. Mover el centro
cambia el nombre de la zona según su nueva posición y la recarga. Una misma
fuente sigue sin poder vigilar un centro desde dos zonas.

## Qué crea

- **Una entidad `geo_location` por buque**, `geo_location.vessel_<MMSI>`,
  cuyo estado es su distancia al centro de la zona en kilómetros. Entre sus
  atributos están el nombre, el MMSI, el indicativo, la velocidad, el rumbo,
  la proa, la eslora, la manga, el tipo, el destino, `object_kind`,
  `last_seen` y `attribution`, cada uno solo si la fuente lo envió. Un buque
  que ven dos zonas es una sola entidad.
- **Un sensor por zona**, `sensor.ships_in_range`, que cuenta los buques
  mostrados y lo dice cuando el límite de la zona o de toda la instalación
  recorta la lista.
- **Para tu propio receptor, un sensor más**, `sensor.ais_station`: mensajes
  por minuto. Sus atributos son `vessels_heard` (en los últimos 10 minutos),
  `farthest_km` y `farthest_mmsi` (desde el centro de la zona),
  `last_message`, `udp_port`, `listening`, y `port_error` cuando no se puede
  abrir el puerto. Se actualiza cada 30 segundos, así que un receptor que deja
  de enviar muestra 0.

Un buque que se oye fuera de tu círculo sale del mapa enseguida. Para oírlo,
a cada fuente en línea se le pide un anillo un poco mayor que tu círculo (un 10 %, al menos 1 km), y tu propio receptor envía todo lo que oye; solo se guardan los buques de dentro de tu círculo. Un buque que
ya no se oye sale del mapa tras un periodo de silencio, y un buque que deja de
aparecer no tiene por qué haberse ido (más abajo).

### Tu base de datos

El recorder de Home Assistant guarda una fila nueva cada vez que cambia una
entidad, y un buque en movimiento cambia con cada posición que informa. Por eso
esta integración puede hacer crecer tu base de datos rápidamente: en nuestro
sistema de pruebas, una zona con 43 buques escribió 27.109 filas de estado en
unas 30 horas, el 8,8 % de toda la base de datos. Por defecto, el recorder
conserva 10 días y purga cada noche a las 04:12, así que el crecimiento se
estabiliza, pero en un tamaño que quizá no quieras. Los `marker_photo` y
`marker_links` de cada buque, y los atributos de los sensores que cambian
rápido, nunca se registran.

Un buque conserva el mismo ID de entidad, `geo_location.vessel_<MMSI>`, cada
vez que aparece: un ferri que se va y vuelve reutiliza su entidad en lugar de
añadir otra. Así, un solo patrón, `geo_location.vessel_*`, abarca todo lo que
esta integración ha puesto alguna vez en el mapa. Para conservar solo el último
día, ejecuta `recorder.purge_entities` de forma programada, por ejemplo con
esta automatización:

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

Si omites `keep_days` (por defecto 0), todas sus filas se borran de una vez.
Para no registrar nada de ello, pon el patrón bajo `recorder:` → `exclude:` →
`entity_globs:` en `configuration.yaml`. Una tarjeta de mapa configurada para
dibujar el historial (`history_start`) no tendrá entonces ningún rastro que
dibujar. `sensor.ships_in_range` es un simple número y cuesta poco conservarlo,
así que su historial se mantiene en ambos casos.

## Eventos: un buque entra en tu zona o sale de ella

Cada zona lanza dos eventos de Home Assistant, para que una automatización te
avise cuando llegue un buque que te interese:

- `live_track_ships_entry` cuando un buque entra en el círculo de la zona
- `live_track_ships_exit` cuando sale

La integración avisa de todos los buques; tu automatización elige los que
importan. Los datos del evento llevan los mismos nombres y unidades que los
atributos del buque, y omiten lo que la fuente no envió:

| Campo | Qué contiene |
|---|---|
| `area_id`, `area` | el ID de la entrada de configuración de la zona y su título |
| `identity` | el MMSI |
| `name`, `call_sign`, `imo` | si se emiten |
| `object_kind` | `vessel`, `net_buoy`, `aton`, `base_station`, `sar_aircraft` o `distress_beacon` |
| `ship_type`, `ship_type_label`, `length_m`, `beam_m`, `draught_m`, `destination`, `nav_status` | solo buques, si se emiten |
| `speed_kmh`, `course_deg`, `heading_deg` | si se emiten |
| `latitude`, `longitude`, `distance_km`, `bearing_from_centre_deg`, `last_seen` | dónde se oyó, desde el centro de la zona |
| `entity_id` | solo al entrar: `geo_location.vessel_<MMSI>`, cuando el buque está en el mapa |
| `reason` | solo al salir: `left` (oído fuera del círculo) o `silent` (no oído durante el tiempo de retención, así que puede seguir ahí) |

Cuatro cosas que conviene saber:

- **Una llegada solo se anuncia si el buque se oyó primero fuera del
  círculo**, en el anillo que lo rodea. Un buque que se oye primero dentro
  puede haber estado allí todo el tiempo: después de un reinicio, los
  receptores siguen entregando durante muchos minutos buques que no se han
  movido. Por eso no se anuncia un buque que los receptores no oyeron al
  entrar, ni uno que enciende el transpondedor ya dentro.
- **Una salida que se oye fuera se anuncia siempre**, incluso la de un buque
  que ya estaba antes de arrancar Home Assistant. Un buque que deja de emitir
  solo se anuncia como salido (`reason: silent`) si se anunció su llegada.
- **Una salida espera 2 minutos.** Un buque que vuelve antes, por el borde del
  círculo, no se anuncia como salido y vuelto a entrar.
- **Al llegar pueden faltar datos.** El nombre, el tipo y el tamaño viajan en
  un mensaje menos frecuente que la posición (más arriba). Un buque que se oye
  por primera vez puede llegar solo con una posición; uno que ya se había oído
  suele traer tipo y tamaño.

Dos zonas sobre las mismas aguas lanzan cada una sus propios eventos. Los
límites de cuántos buques dibuja el mapa nunca hacen que un buque entre o
salga.

Una automatización que te avisa cuando un buque de más de 150 m entra en una
zona:

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
      title: "{{ trigger.event.data.name | default('Un buque') }}"
      message: >-
        {{ trigger.event.data.ship_type_label | default('Buque') }},
        {{ trigger.event.data.length_m }} m,
        a {{ trigger.event.data.distance_km }} km, entra en
        {{ trigger.event.data.area }}.
```

## Buques seguidos: sigue buques elegidos en cualquier lugar

Además de zonas, puedes seguir una lista de buques estén donde estén: el barco
de un familiar, un ferry que tomas, un crucero que vuelve a casa. **Ajustes >
Dispositivos y servicios > Añadir integración > Live Track Ships > Buques
elegidos, estén donde estén.** Hace falta una clave de aisstream.io (se
rellena con la de una zona que ya hayas configurado), y hay una sola lista así
por Home Assistant.

Un buque por línea: su MMSI de 9 cifras y, si quieres, una etiqueta propia.

```text
244650000 Barco de papá
366999999 El ferry
```

Como máximo 100 buques. aisstream sigue como máximo 200 MMSI por clave, y
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
si está instalado con la misma clave, usa parte de ellos; una lista que se
pasara se rechaza al cargar la entrada, con el motivo. Cambia la lista en los
ajustes de la entrada.

Un buque seguido se dibuja en el mapa como cualquier otro, allí donde se oiga,
y su estado es su distancia a tu casa. Una zona que ya lo muestra se lo queda:
un buque, un marcador. La entrada crea `sensor.watched_vessels`: cuántos de los
buques de la lista se oyen ahora, con cada uno de ellos, su etiqueta y su
último estado conocido en el atributo `vessels`.

Lanza un solo evento, `live_track_ships_watched`, cuyo campo `change` dice qué
pasó:

| `change` | Cuándo |
|---|---|
| `arrived` | el buque se declara amarrado o fondeado, o, sin estado, se queda por debajo de 2 nudos |
| `departed` | vuelve a navegar |
| `silent` | no se oye durante 30 minutos (6 horas si está amarrado o fondeado); sale del mapa, y puede seguir ahí |
| `heard` | se vuelve a oír después de `silent` |
| `destination` | la tripulación cambió el destino; `destination_previous` guarda el anterior |

Los datos llevan `watch_id`, `watch`, `identity`, tu etiqueta `label` y los
mismos campos del buque que los eventos de zona, con la distancia y la
demora desde tu casa. La llegada y la salida esperan a que el nuevo estado se
mantenga 5 minutos según el reloj del propio buque, para que un barco que
deriva a 2 nudos no vaya y venga. No se anuncia nada a partir de la primera
posición de un buque después de un reinicio: esa fija el punto de partida.
Los destinos los teclea la tripulación y suelen estar desfasados.

## Tarjeta de mapa

Los buques los dibuja [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)
(`custom:live-track-map-card`), el único mapa en el que dibujan todas las
integraciones de Live Track. Dibuja la imagen propia de cada buque, la gira
según su proa y la desliza entre posiciones reales por el agua en lugar de en
línea recta por tierra.

**La tarjeta se instala con la integración.** Esta integración lleva una
copia publicada de la tarjeta, la sirve y la registra como recurso de panel al
arrancar Home Assistant; no hay nada que descargar ni que copiar en `www`.
Todas las integraciones de Live Track hacen lo mismo, y entre ellas mantienen
exactamente una fila de recurso: la versión más alta de la tarjeta que lleve
cualquiera de ellas, nunca una anterior. Una tarjeta instalada desde el
Marketplace no se toca. Al quitar la última zona de esta integración, la fila
pasa a otra integración de Live Track, o se quita si no queda ninguna.
Consulta el README de la tarjeta, sección
[Live Track](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track).

Si los recursos de tus paneles se definen en YAML
(`lovelace: resource_mode: yaml`), no se puede registrar nada por ti. Una
reparación te da entonces la línea exacta que añadir; es así, con la
dirección de la integración en lugar de los marcadores:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_ships/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Si se borran los archivos de la integración (desde el Marketplace, por
ejemplo) mientras sus zonas siguen configuradas, y no hay otra integración de
Live Track instalada, nadie ordena la fila: quítala en Ajustes > Paneles >
Recursos. Para instalar la tarjeta a mano, sigue el README de la tarjeta; la
fila de recurso de una copia instalada a mano en `/local/` solo se apunta a la
copia de una integración cuando esa copia es una versión más nueva.

Dale los buques con
[auto-entities](https://github.com/thomasloven/lovelace-auto-entities),
filtrando por `domain: geo_location` y `attributes: {source: live_track_ships}`.
Si tienes otras integraciones de Live Track instaladas, añade un filtro por
cada una de sus fuentes.

Cualquier otra tarjeta de mapa que muestre entidades `geo_location` muestra
también los buques, sin las imágenes ni el deslizamiento de esta tarjeta.

Un buque de la lista pública
[EnforcementVessels](https://github.com/StrausbergAutomationWorks/EnforcementVessels)
(buques de guardacostas usados en tareas de inmigración) se dibuja con los
colores de los guardacostas y el nombre y la agencia de la lista, esté donde
esté.

### Ocultar tipos de buque

Cada buque lleva `marker_group`, `marker_group_label` y `marker_group_order`:
uno de trece grupos (carga; petrolero; pasaje y ferris; pesca; recreo y vela;
remolcadores, prácticos y servicio portuario; Estado, SAR y policía; alta
velocidad y otros; tipo no enviado; boyas de artes de pesca; ayudas a la
navegación; estaciones base; aeronaves SAR). La tarjeta de filtro del mapa,
`custom:live-track-map-filter-card`, los enumera con cuántos hay de cada uno en
el mapa y oculta los que desmarques; ponla en cualquier vista del panel. Tu
elección se guarda solo en ese navegador. La integración sigue mostrándolo
todo: su sensor cuenta todos los buques y sus eventos se disparan para todos.
Una radiobaliza de socorro no tiene grupo, así que nunca se oculta.

### Fotos y enlaces

Cuando un buque envía un número IMO y Wikidata conoce una foto de ese buque en
Wikimedia Commons, el buque lleva `marker_photo`. El mapa muestra la foto en el
cuadro emergente con el fotógrafo y la licencia; un clic la abre más grande,
con enlaces a la página de la foto y a su licencia. Todo buque con número IMO o
MMSI lleva además `marker_links`, un enlace al buque en VesselFinder. El botón
**Details** de la ventana abre el diálogo habitual del buque. Tu Home Assistant
consulta él mismo Wikidata y Commons, 20 números IMO cada vez, con diez
segundos entre consultas, y guarda cada respuesta 30 días (14 si no hay foto)
en `.storage/saw_vessel_photos.json`. Cuenta con fotos para más o menos uno de
cada diez buques: en nuestro sistema de pruebas, 49 de 521 números IMO tenían
una.

## Dónde mira

Pones un **centro y un radio** en el mapa. El centro puede estar en cualquier
lugar del mundo; el radio puede ir de 1 a 500 km. Por defecto son **50 km**.
El estado de cada buque es su distancia a tu centro.

Cuántos buques hay en un círculo depende mucho más de *qué agua* que de *qué
tamaño*. En las pruebas, un círculo de 50 km tenía unos 4 buques sobre Chicago
y unos 340 sobre el Solent, en el sur de Inglaterra: el mismo radio, unas 80
veces más tráfico. Por eso la integración guarda como máximo un número fijo de
buques (1.000 por defecto, ajustable hasta 5.000), se queda con los más
cercanos cuando hay más y lo dice en su sensor `ships_in_range`.

Todas tus zonas **juntas** muestran como máximo 2.500 buques, sean cuales sean
sus fuentes. Los ajustes de cada zona tienen el control deslizante de arriba,
que solo puede bajar ese límite; se aplica el ajuste más bajo de las zonas
activadas. Bájalo en un equipo más lento.

## Cobertura, medida y no prometida

La cobertura es buena donde hay receptores y no existe donde no los hay, y
**ningún ajuste puede crear una cobertura que no existe**.

Medido el 2026-09-02 alrededor de Chicago, con aisstream.io:

- **Grandes Lagos**: 100 buques distintos en 120 segundos, los cinco lagos y
  las aguas que los unen.
- **Chicago River, centro**: concurrido y fiable.
- **Chicago Sanitary and Ship Canal, Cal-Sag Channel, Calumet River**: una
  hora escuchando, **cero buques**. El canal no está vacío: sus convoyes de
  empuje se ven en servicios comerciales mediante AIS por satélite, que los
  agregadores gratuitos no ofrecen. El tráfico es real; la cobertura desde
  tierra, no.

Que no haya buques en tu zona puede significar que no hay receptores, no que
no haya barcos. Comprueba que tu fuente cubre tus aguas antes de dar por roto
la integración.

Un buque que deja de aparecer no tiene por qué haberse ido. Ninguna de estas
fuentes garantiza la entrega, así que la integración muestra cuándo se oyó
cada buque por última vez y solo lo quita tras un periodo de silencio.

## Buques que merecen su propia imagen

La mayoría de los buques se dibujan según su tipo. Algunos tienen su propia
imagen: yates reales y de Estado, y barcos conocidos como los barcos
turísticos, los taxis acuáticos y los barcos bomba de Chicago. ¿Conoces un
buque que merezca la suya, en cualquier lugar del mundo? Abre una issue en
<https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues> con su
nombre y su número MMSI o IMO, y una foto o un enlace si los tienes.

## Idiomas

Este README: [English](README.md), [Deutsch](README.de.md),
[Français](README.fr.md), [Nederlands](README.nl.md),
[简体中文](README.zh-Hans.md), **Español**, [Italiano](README.it.md),
[Dansk](README.da.md) y [Kalaallisut](README.kl.md) (un borrador, enviado
para su revisión a Oqaasileriffik, la secretaría de la lengua de
Groenlandia; mientras tanto, la página danesa es la fiable). El README está
traducido a una lista corta de idiomas: los que leen la mayoría de usuarios
de Home Assistant, y algunos más cuando hay un buen motivo. Cada README
traducido está completo: todo lo que tiene el inglés está en cada uno, y
ninguno te remite al inglés para los detalles.

El diálogo de configuración y los ajustes de una zona aparecen en el idioma
de tu Home Assistant cuando es uno de estos: English, Dansk, Deutsch,
Español, Français, Gaeilge, Íslenska, Italiano, Nederlands, Norsk Bokmål,
Polski, Português, Português (BR), Suomi, Svenska y 简体中文. Cualquier otro
idioma muestra el diálogo en inglés. El kalaallisut todavía no es un idioma de
Home Assistant; hemos pedido a Home Assistant que lo añada, y el diálogo
llegará cuando pueda mostrarse.

¿Has encontrado en una traducción un error que cambia el sentido o se lee mal?
Dínoslo en <https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues>.
Las traducciones se escribieron para este proyecto y no todas las ha leído
todavía un hablante nativo.

**¿Te cuesta seguir esto en alguno de estos idiomas?** Pide otro en la misma
dirección, e intentaremos atenderte.

## Parte de Live Track

Live Track es un conjunto de integraciones de Home Assistant, una por cada
tipo de cosa que se mueve, que dibujan todas en el mismo mapa. Comparten una
biblioteca de Python
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore))
y la tarjeta de mapa, así que instalar otra no añade peticiones a una fuente
compartida. Publicadas:
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft),
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
[Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail),
[Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail)
y Live Track Ships. Cada una funciona por sí sola.

## Sin afiliación

Sin relación con aisstream.io, Fintraffic, BarentsWatch, MarineTraffic,
VesselFinder, ningún armador ni ninguna autoridad marítima. El AIS es un
sistema de seguridad de la navegación; **esta integración es para la
curiosidad y no sirve para navegar, evitar colisiones ni ningún fin
operativo.**

## Licencia

Código: MIT, en [LICENSE](LICENSE). Créditos de datos e imágenes:
[ATTRIBUTION.md](ATTRIBUTION.md).

## Palabras clave

Home Assistant AIS · seguimiento de buques · buques en el mapa · seguimiento
de barcos · tráfico marítimo en directo · mapa AIS · aisstream.io ·
Digitraffic · BarentsWatch · geo_location · integración HACS
