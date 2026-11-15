# Live Track Ships

[English](README.md) · [Suomi](README.fi.md) · [Svenska](README.sv.md) · [Norsk](README.nb.md) · **Español** · [Nederlands](README.nl.md) · [Gaeilge](README.ga.md)

Barcos, embarcaciones y buques en tiempo real en el mapa de Home Assistant.
Live Track Ships es una integración de Home Assistant (custom component, se
instala desde el Marketplace / HACS) que muestra los datos AIS de los buques
de la zona que elijas: dónde está cada uno, su nombre, velocidad, rumbo, tipo
y tamaño cuando el buque los transmite. Cada buque es una entidad
`geo_location` que se mueve en el mapa al llegar nuevas posiciones. El centro
de la zona puede estar en cualquier lugar del mundo.

**Estado: 0.1.0, la primera versión.**

## También se ven las embarcaciones de recreo

La integración muestra todo lo que envía la fuente y nada se puede filtrar. Una
embarcación de recreo con transpondedor AIS aparece en el mapa igual que un
carguero: nombre, MMSI, indicativo de llamada y posición con precisión de un
metro aproximadamente. Un barco que deja el transpondedor encendido en el
amarre sigue en el mapa en su amarre. El AIS no tiene lista de exclusión. Si
quieres menos embarcaciones de recreo en el mapa, reduce el radio.

## Fuentes

Eliges una fuente para cada zona.

| Fuente | Cobertura | Necesita |
|---|---|---|
| aisstream.io | todo el mundo, donde haya receptores de voluntarios | una clave de API gratuita |
| Fintraffic Digitraffic | aguas de Finlandia y el Báltico | nada |
| BarentsWatch AIS Live | aguas de Noruega | client ID y secret gratuitos |

El atributo `attribution` de cada buque indica su fuente. Todas las
atribuciones: [ATTRIBUTION.md](ATTRIBUTION.md).

La cobertura es buena donde hay receptores, y ningún ajuste crea cobertura
donde no la hay. Si no ves buques en tu zona, puede que falten receptores, no
barcos.

## Parte de Live Track

Live Track es un conjunto de integraciones de Home Assistant, una por cada tipo
de cosa que se mueve, y todas dibujan en el mismo mapa
([LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
que se instala con la integración). Publicadas:
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft),
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
[Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail),
[Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail)
y Live Track Ships. Cada una funciona por sí sola.

## Requisitos

- Home Assistant 2026.11 o posterior.
- aisstream.io: una clave de API gratuita de
  [aisstream.io](https://aisstream.io/account). aisstream permite tres
  conexiones por cuenta y por dirección IP pública.
- BarentsWatch: client ID y secret gratuitos. Escribe el client ID tal como se
  emitió.
- Digitraffic no necesita clave ni cuenta.

## Instalación

### Desde el Marketplace

La integración aún no está en el catálogo del Marketplace. Añádela por enlace:

1. **Settings > Marketplace** y **Add from link**.
2. Escribe `StrausbergAutomationWorks/LiveTrackShips`. Si pide el tipo, elige
   **Integration**.
3. Instala **Live Track Ships**.
4. Reinicia Home Assistant. El Marketplace ofrece el reinicio como reparación
   en **Settings > System > Repairs**.

### A mano

1. Descarga el código fuente de la
   [última versión](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest).
2. Copia su carpeta `custom_components/live_track_ships` en la carpeta
   `custom_components` del directorio de configuración de Home Assistant.
3. Reinicia Home Assistant.

## Configuración

**Settings > Devices & services > Add integration > Live Track Ships.** Elige
la fuente, introduce la clave si hace falta, arrastra el marcador del mapa al
agua que quieres vigilar y elige el radio (de 1 a 500 km, 50 por defecto). Cada
zona es una entrada aparte. El diálogo está en inglés; los nombres de menú de
arriba son los de la interfaz en inglés.

Todas las zonas juntas muestran como máximo 2.500 buques. Los ajustes de cada
zona tienen un control deslizante que solo puede bajar ese límite; úsalo en un
equipo más lento.

## Datos y licencia

Los buques se leen mientras la integración funciona, directamente de la fuente
elegida; este repositorio no contiene datos de esas fuentes. Código: MIT.

No está afiliada a aisstream.io, Fintraffic, BarentsWatch ni a ninguna
autoridad marítima. **No sirve para navegar ni para evitar colisiones.** Todos
los detalles: [README en inglés](README.md).

## Palabras clave

Home Assistant AIS · barcos en el mapa · seguimiento de buques · tráfico
marítimo en tiempo real · localizador de barcos · integración HACS
