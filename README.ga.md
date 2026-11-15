# Live Track Ships

[English](README.md) · [Suomi](README.fi.md) · [Svenska](README.sv.md) · [Norsk](README.nb.md) · [Español](README.es.md) · [Nederlands](README.nl.md) · **Gaeilge**

Longa, báid agus soithí eile beo ar léarscáil Home Assistant. Is comhtháthú
Home Assistant é Live Track Ships (custom component, a shuiteáiltear ón
Marketplace / HACS) a thaispeánann sonraí AIS na soithí sa limistéar a
roghnaíonn tú: cá bhfuil gach soitheach, a ainm, a luas, a chúrsa, a chineál
agus a mhéid nuair a chraolann an soitheach iad. Is aonán `geo_location` gach
soitheach, agus bogann sé ar an léarscáil de réir mar a thagann suíomhanna
nua. Is féidir lár an limistéir a chur áit ar bith ar domhan.

**Stádas: 0.1.0, an chéad eisiúint.**

## Taispeántar báid phléisiúir freisin

Taispeánann an comhtháthú gach a seolann an fhoinse, agus ní féidir aon rud a
scagadh amach. Feictear bád pléisiúir a bhfuil trasfhreagróir AIS aige ar an
léarscáil díreach mar a fheictear long lasta: a ainm, a MMSI, a chomhartha
glao agus a shuíomh go dtí méadar nó mar sin. Fanann bád a choinníonn an
trasfhreagróir ar siúl ag an gcé ar an léarscáil ag an gcé. Níl liosta
diúltaithe ann do AIS. Más mian leat níos lú bád pléisiúir ar an léarscáil,
laghdaigh an ga.

## Foinsí

Roghnaíonn tú foinse amháin do gach limistéar.

| Foinse | Clúdach | Riachtanach |
|---|---|---|
| aisstream.io | an domhan ar fad, áit a bhfuil glacadóirí ag oibrithe deonacha | eochair API saor in aisce |
| Fintraffic Digitraffic | uiscí na Fionlainne agus na Mara Baltaí | faic |
| BarentsWatch AIS Live | uiscí na hIorua | client ID agus secret saor in aisce |

Insíonn tréith `attribution` gach soithigh cén fhoinse ónar tháinig sé. Gach
lua foinse: [ATTRIBUTION.md](ATTRIBUTION.md).

Tá an clúdach go maith áit a bhfuil glacadóirí, agus ní chruthaíonn socrú ar
bith clúdach nach bhfuil ann. Mura bhfeiceann tú soithí i do limistéar, b'fhéidir
nach bhfuil glacadóirí ann, seachas nach bhfuil báid ann. Timpeall chósta na
hÉireann, braitheann aisstream.io ar ghlacadóirí oibrithe deonacha.

## Cuid de Live Track

Is sraith comhtháthuithe Home Assistant é Live Track, ceann do gach cineál
ruda a ghluaiseann, agus tarraingíonn siad go léir ar an léarscáil chéanna
([LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
a shuiteáiltear leis an gcomhtháthú). Eisithe:
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft),
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT),
[Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail),
[Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail)
agus Live Track Ships. Oibríonn gach ceann acu leis féin.

## Riachtanais

- Home Assistant 2026.11 nó níos déanaí.
- aisstream.io: eochair API saor in aisce ó
  [aisstream.io](https://aisstream.io/account). Ceadaíonn aisstream trí
  cheangal in aghaidh an chuntais agus in aghaidh an tseolta IP phoiblí.
- BarentsWatch: client ID agus secret saor in aisce. Scríobh an client ID go
  díreach mar a eisíodh é.
- Ní theastaíonn eochair ná cuntas do Digitraffic.

## Suiteáil

### Ón Marketplace

Níl an comhtháthú i gcatalóg an Marketplace fós. Cuir leis é le nasc:

1. **Settings > Marketplace** agus **Add from link**.
2. Scríobh `StrausbergAutomationWorks/LiveTrackShips`. Má iarrann sé an cineál,
   roghnaigh **Integration**.
3. Suiteáil **Live Track Ships**.
4. Atosaigh Home Assistant. Tairgeann an Marketplace an t-atosú mar dheisiú
   faoi **Settings > System > Repairs**.

### De láimh

1. Íoslódáil cód foinse na
   [heisiúna is déanaí](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest).
2. Cóipeáil a fhillteán `custom_components/live_track_ships` isteach i
   bhfillteán `custom_components` eolaire cumraíochta Home Assistant.
3. Atosaigh Home Assistant.

## Socrú

**Settings > Devices & services > Add integration > Live Track Ships.**
Roghnaigh an fhoinse, cuir isteach an eochair más gá, tarraing an marcóir ar
an léarscáil go dtí an t-uisce is mian leat a fhaire, agus roghnaigh an ga (1
go 500 km, 50 de réir réamhshocraithe). Is iontráil ar leith gach limistéar. Tá
an dialóg i mBéarla; is ó chomhéadan an Bhéarla ainmneacha na roghchlár thuas.

Taispeánann na limistéir go léir le chéile 2,500 soitheach ar a mhéad. Tá
sleamhnán i socruithe gach limistéir nach féidir leis ach an teorainn sin a
ísliú; úsáid é ar chrua-earraí níos moille.

## Sonraí agus ceadúnas

Léitear na soithí fad atá an comhtháthú ag rith, díreach ón bhfoinse a
roghnaíodh; níl sonraí ó na foinsí sin sa stór seo. Cód: MIT.

Níl baint aige le aisstream.io, Fintraffic, BarentsWatch ná le húdarás
muirí ar bith. **Ní le haghaidh loingseoireachta ná seachaint imbhuailte é.**
Gach mionsonra: [an README i mBéarla](README.md).

## Eochairfhocail

Home Assistant AIS · longa ar an léarscáil · rianú long · báid ar an
léarscáil · trácht muirí beo · comhtháthú HACS
