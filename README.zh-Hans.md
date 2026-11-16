# Live Track Ships

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · **简体中文** · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Kalaallisut](README.kl.md) · [所有语言](#语言)

**适用于 Home Assistant 的 AIS 船舶、游艇与船只跟踪。** 你附近的船，或你选定的
世界任何地方的船，都会作为实时标记显示在你的地图上。它是 Live Track 的一部分：
船、飞机和火车都在同一张地图上。

实时海上 AIS 数据来自 [aisstream.io](https://aisstream.io)、
[Fintraffic Digitraffic](https://www.digitraffic.fi/en/marine-traffic/) 或
[BarentsWatch](https://www.barentswatch.no/en/)，以 Home Assistant 的
`geo_location` 实体呈现，并绘制在共用的 Live Track 地图上。

**状态：0.1.0，首个版本。** 可通过链接添加到 Marketplace（见下文）；它还没有进入
Marketplace 的目录。

## 什么是 AIS

AIS（Automatic Identification System，船舶自动识别系统）是一种甚高频（VHF）
广播，船舶用它向彼此和岸上通报自己的位置、身份和航程。它相当于航空领域的
ADS-B。商船必须配备；许多游艇自愿配备，通常是功率较低的 B 类设备。

AIS 以明文广播。任何有接收机的人都能收到，公共汇集平台也会再次发布这些数据。

## 显示哪些内容

**数据源发送的一切。** 不过滤任何内容，也没有隐藏某一类别的设置。

| 数据中的对象 | 是否显示 |
|---|---|
| 货船、油轮、拖船、渡轮、客船 | 是 |
| 渔船、引航船、执法船和其他工作船 | 是 |
| **私人游艇和帆船** | **是，带名称和位置** |
| 发送 AIS 的**渔具浮标** | **是，画成一条鱼** |
| 搜救（SAR）飞机 | 数据源发送时显示 |
| 助航设施：浮标、信标、灯塔 | 数据源发送时显示 |
| AIS 岸基站 | 数据源发送时显示 |

### 私人船只也会显示，你应该了解这意味着什么

一艘发送 AIS 的游艇在你的地图上显示得和货船完全一样。根据船上发送的内容，它的
实体可能包含：

- 它的**名称**，也就是地图上显示的标签
- 它的 **MMSI** 和**无线电呼号**，两者都是固定的，并且可以公开查到
- 它的**位置**，精确到大约一米，上一个位置，以及各自被收到的时间
- 航速、航向和船首向（如有发送）
- 船长、船宽和船舶类型（如有发送）

在泊位上一直开着应答器的船，只要还在发送，就会一直停在地图上的泊位处。

AIS 没有像飞机那样的退出名单，本集成也不会自造一份。如果你想让地图上的私人船只
少一些，请缩小半径。

### 经常缺少船舶类型，小船尤其如此

位置和名称几乎随每条消息一起到达。船舶类型和尺寸在另一条更少见的消息里，而且
许多小船设备（B 类）很少发送包含这些内容的部分。请预料到相当一部分船只，包括
大多数小船，会没有类型和尺寸；Home Assistant 重启后的几分钟里，所有船只的信息
都会不全。这是数据本身的情况，不是故障。已经收到过的类型和尺寸会在重启后保留。

### AIS 上的并不都是船

每个实体都带有 `object_kind`：`vessel`、`net_buoy`、`aton`（助航设施）、
`base_station`、`sar_aircraft` 或 `distress_beacon`。大多数可以通过国际电信
联盟（ITU）分配给它们的识别码格式来区分。渔具浮标不行：它们用类似船舶的识别码
发送，因此要根据它们的出厂名称（FISHING BOUY、NET MARK、BUOY）以及没有发送
船长来识别。

不是船的对象都显示为没有船舶类型、尺寸或航行状态。渔具浮标随着渔线漂流，所以
保留航速和航向，并画成一条朝漂流方向的鲑鱼。

会出现哪些对象取决于数据源。某个晚上的测量结果：

| 数据源 | 渔具浮标 | 搜救飞机 | 助航设施、岸基站 |
|---|---|---|---|
| BarentsWatch | 有 | 有 | 未见 |
| Digitraffic | 未见 | 有 | 未见 |
| aisstream.io | 未见 | 未见 | 未见 |
| 你自己的接收机 | 收到什么就有什么 | 收到什么就有什么 | 收到什么就有什么 |

aisstream.io 只提供了船舶位置和船舶详情消息，无论是在北美五大湖上空，还是在
BarentsWatch 显示浮标的同一片挪威和丹麦水域。

## 数据来源

你为设置的每个区域选择一个数据源。

| 数据源 | 覆盖范围 | 需要 |
|---|---|---|
| aisstream.io | 全球，凡有志愿者运行接收机的地方 | 一个免费的 API 密钥 |
| Fintraffic Digitraffic | 芬兰和波罗的海水域 | 不需要 |
| BarentsWatch AIS Live | 挪威水域 | 免费的客户端 ID 和客户端密钥 |
| 你自己的 AIS 接收机 | 你的天线能收到多远就多远 | 一台通过 UDP 发送 NMEA 的接收机 |

会出现哪些类别、位置有多新、船舶详情有多完整，都取决于你选择的数据源。

### 你自己的接收机

如果你有一台 AIS 接收机，Live Track Ships 可以显示它收到的内容，不需要账户，也不需要
互联网。接收机或为它解码的程序，通过 UDP 把 NMEA 语句（`!AIVDM`）发送到 Home Assistant
的地址和你选定的端口（不改的话是 10110）。在 AIS-catcher 中用 `-u <address> <port>`，
在 rtl-ais 中用 `-h <address> -P <port>`；OpenCPN 和 Signal K 把它添加为一个 UDP 输出
连接。通过 USB 连接的接收机（例如 dAISy）需要借助上述某个程序来转发它的语句。

- 一个区域监听一个端口；两台接收机需要两个端口。
- 接收机在你圆圈内收到的一切都会显示，包括助航设施和基站。站点传感器（见下文）还会
  统计它在圆圈外收到的内容。
- 语句不带日期，所以一个位置的时间是 Home Assistant 收到它的时间。
- 此数据源不显示转向速率。
- 目前只用通过 UDP 发送的录制语句测试过，还没有用真实接收机测试。如果你用自己的接收机
  试过，请在 [issues 页面](https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues) 告诉我们结果。

### 数据来源说明

每个船舶实体，以及每个区域的 `ships_in_range` 传感器，都带有一个 `attribution`
属性，写明提供数据的来源；Home Assistant 会在实体详情中显示它。其中两个数据源
以要求署名的许可发布数据，而 Live Track Ships 会修改收到的数据（换算单位，只保留
你圆圈内的船只），所以它们的说明会写明这一点。如果你把这些数据给别人看，例如放在
公开的仪表板上，请保留来源说明，并阅读数据源自己的条款：

- **aisstream.io**：没有公布条款。<https://aisstream.io>
- **Fintraffic Digitraffic**：CC BY 4.0。
  <https://www.digitraffic.fi/en/terms-of-service/>
- **BarentsWatch**：挪威政府开放数据许可（NLOD）。
  <https://www.barentswatch.no/en/articles/api-terms-and-conditions/>
- **你自己的接收机**：你自己的数据；其署名行会注明这一点。
- **EnforcementVessels**（海岸警卫队外观背后的名单，见下文）：ODbL v1.0。
  <https://github.com/StrausbergAutomationWorks/EnforcementVessels>

准确的说明文字见 [ATTRIBUTION.md](ATTRIBUTION.md)。

## 要求

- Home Assistant 2026.11 或更新版本，在线数据源需要能访问互联网。
- 使用 aisstream.io：需要从 [aisstream.io](https://aisstream.io/account)
  获取的免费 API 密钥。aisstream **每个账户和每个公网 IP 各允许三个连接**；
  如果你还有其他工具使用同一个密钥，请把它们算进去。如果安装了 Live Track SALT，
  它会用同一个密钥占用第二个连接。
- 使用 BarentsWatch：需要你自己在 BarentsWatch 注册的免费客户端 ID 和客户端
  密钥。请完全按照发放时的样子输入客户端 ID。
- 使用你自己的接收机：需要一台接收机和一个程序，在同一网络内通过 UDP 向
  Home Assistant 发送 NMEA。这不需要互联网。
- 首次加载本集成时，Home Assistant 会自动安装所需的 Python 包
  （`saw-livetrack` 和 `pyais`）。

## 安装

### 通过 Marketplace

Live Track Ships 还没有进入 Marketplace 的目录。请通过链接添加：

1. **设置 > Marketplace**，然后选择**通过链接添加**。
2. 输入 `StrausbergAutomationWorks/LiveTrackShips`。如果询问类型，请选择
   **集成**。
3. 安装 **Live Track Ships**。
4. 重启 Home Assistant。Marketplace 会在**设置 > 系统 > 修复**中以修复项的
   形式提供重启。

### 手动安装

1. 下载[最新版本](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest)
   的源代码。
2. 把其中的 `custom_components/live_track_ships` 文件夹复制到 Home Assistant
   配置目录下的 `custom_components` 文件夹。
3. 重启 Home Assistant。

## 设置

**设置 > 设备与服务 > 添加集成 > Live Track Ships**，然后选择**某个区域内的所有
船只**（另一个选项，关注的船只，见[下文](#关注的船只在任何地方跟踪选定的船)）。
你添加的每个区域都是一个独立条目，标题为 *Ships near <纬度>, <经度>*。当 Home
Assistant 使用简体中文时，设置对话框也以简体中文显示。

| 字段 | 填写内容 | 默认值 |
|---|---|---|
| 数据源 | aisstream.io、Fintraffic Digitraffic、BarentsWatch AIS Live 或你自己的 AIS 接收机 | aisstream.io |
| API 密钥 | 仅 aisstream.io。从你已经设置的区域自动填入；可以修改 | 空 |
| 客户端 ID、客户端密钥 | 仅 BarentsWatch。从你已经设置的区域自动填入 | 空 |
| UDP 端口 | 仅你自己的接收机：它发送 NMEA 的端口，1024 到 65535。如果另一个区域或另一个程序已在使用，会被拒绝 | 10110 |
| 中心点 | 地图上的一个标记；把它拖到你想观察的水域 | 你的家 |
| 半径（公里） | 1 到 500 | 50 |
| 最多跟踪船只数 | 1 到 5,000；本区域的安全上限，保留最近的船只 | 1,000 |

同一个数据源不能两次观察同一个中心点。当一个 BarentsWatch 圆圈至少有 5% 位于
BarentsWatch 发布的水域之外时，对话框会在创建区域之前告诉你占多少；提交即可仍然
保留这个圆圈。

**区域的设置**（在其条目上点“配置”）：中心点，使用同一个地图标记；半径；最多
跟踪船只数；以及*地图上的最多船只数，所有 Live Track Ships 条目合计*，这是一个从
100 到 2,500、步长 100 的滑块（默认 2,500）；对于你自己的接收机，还有它的 UDP 端口。移动中心点会按新位置重命名该区域
并重新加载。同一个数据源仍然不能从两个区域观察同一个中心点。

## 会创建什么

- **每艘船一个 `geo_location` 实体**，`geo_location.vessel_<MMSI>`，其状态是
  它与区域中心的距离（公里）。属性包括名称、MMSI、呼号、航速、航向、船首向、
  船长、船宽、船舶类型、目的地、`object_kind`、`last_seen` 和 `attribution`，
  每项只在数据源发送时才有。被两个区域看到的船只是同一个实体。
- **每个区域一个传感器**，`sensor.ships_in_range`，统计显示的船只数；当区域或
  整个安装的上限截断列表时，它会说明。
- **对于你自己的接收机，还有一个传感器**，`sensor.ais_station`：每分钟消息数。其属性有
  `vessels_heard`（最近 10 分钟内）、`farthest_km` 和 `farthest_mmsi`（相对区域中心点）、
  `last_message`、`udp_port`、`listening`，以及端口无法打开时的 `port_error`。它每 30 秒
  更新一次，所以停止发送的接收机会显示 0。

在你的圆圈外收到的船会立即从地图上消失。为了能收到这一点，每个在线数据源都会被请求
比你的圆圈稍大一圈的范围（大 10%，至少 1 公里），而你自己的接收机会发送它收到的一切；只保留你圆圈内的船只。之后再也
没有收到的船会在一段静默期后消失，而不再出现的船并不一定已经离开（见下文）。

### 你的数据库

Home Assistant 的 recorder 在实体每次变化时都会存一行新记录，而一艘航行中的船每报告一次位置就变化一次。因此这个集成可能让你的数据库快速增长：在我们的测试系统上，一个有 43 艘船的区域在大约 30 小时内写入了 27,109 行状态记录，占整个数据库的 8.8%。recorder 默认保留 10 天，并在每晚 04:12 清理，所以增长会趋于平稳，但停下来的大小可能不是你想要的。每艘船的 `marker_photo` 和 `marker_links`，以及各传感器变化很快的属性，从不被记录。

一艘船每次出现都保持同一个实体 ID，`geo_location.vessel_<MMSI>`：一艘离开又回来的渡轮会重新使用它的实体，而不是再添加一个。所以一个模式 `geo_location.vessel_*` 就涵盖这个集成曾经放到地图上的一切。若只想保留最近一天的记录，可以定时运行 `recorder.purge_entities`，例如使用这个自动化：

```yaml
alias: 缩减船只历史
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

如果省略 `keep_days`（默认为 0），它们的所有记录会一次删除。若完全不想记录，请在 `configuration.yaml` 中把这个模式放在 `recorder:` → `exclude:` → `entity_globs:` 下。这样，设置为绘制历史（`history_start`）的地图卡片就没有轨迹可画。`sensor.ships_in_range` 只是一个数字，保存成本很低，所以无论哪种做法，它的历史都会保留。

## 事件：有船进入或离开你的区域

每个区域都会触发两个 Home Assistant 事件，这样自动化就能在你关心的船到达时
通知你：

- 船进入区域的圆圈时触发 `live_track_ships_entry`
- 船离开时触发 `live_track_ships_exit`

集成会报告每一艘船；由你的自动化挑出重要的船。事件数据的名称和单位与船舶实体的
属性相同，数据源没有发送的内容会被省略：

| 字段 | 内容 |
|---|---|
| `area_id`、`area` | 区域配置条目的 ID 和标题 |
| `identity` | MMSI |
| `name`、`call_sign`、`imo` | 如有发送 |
| `object_kind` | `vessel`、`net_buoy`、`aton`、`base_station`、`sar_aircraft` 或 `distress_beacon` |
| `ship_type`、`ship_type_label`、`length_m`、`beam_m`、`draught_m`、`destination`、`nav_status` | 仅船舶，如有发送 |
| `speed_kmh`、`course_deg`、`heading_deg` | 如有发送 |
| `latitude`、`longitude`、`distance_km`、`bearing_from_centre_deg`、`last_seen` | 收到它的位置，从区域中心算起 |
| `entity_id` | 仅进入时：`geo_location.vessel_<MMSI>`，当船在地图上时 |
| `reason` | 仅离开时：`left`（在圆圈外收到）或 `silent`（在保留时间内没有收到，因此可能仍在那里） |

需要了解的四点：

- **只有先在圆圈外被收到的船才会报告进入**，也就是在圆圈周围的那一圈里。第一次
  就在圈内收到的船可能一直都在那里：重启之后，接收站会在很多分钟里继续送来从未
  移动过的船。因此，接收站没收到它驶入过程的船，或者进入圈内后才打开应答器的船，
  都不会报告进入。
- **在圈外收到的离开总会报告**，即使这艘船在 Home Assistant 启动前就已经在那里。
  停止发送信号的船，只有在报告过它进入时，才会报告离开（`reason: silent`）。
- **离开要等 2 分钟才报告。** 船在此之前沿着圆圈边缘回到圈内，就不会报告为离开
  又进入。
- **刚进入时可能缺少信息。** 名称、类型和尺寸所在的消息比位置更少见（见上文）。
  第一次被收到的船可能只带位置进入；以前收到过的船通常带有类型和尺寸。

同一片水域上的两个区域各自触发自己的事件。地图绘制船只数量的上限，绝不会让一艘
船进入或离开。

一个在超过 150 米的船进入区域时通知你的自动化：

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
      title: "{{ trigger.event.data.name | default('一艘船') }}"
      message: >-
        {{ trigger.event.data.ship_type_label | default('船只') }}，
        {{ trigger.event.data.length_m }} 米，
        距离 {{ trigger.event.data.distance_km }} 公里，正在进入
        {{ trigger.event.data.area }}。
```

## 关注的船只：在任何地方跟踪选定的船

除了区域，你还可以关注一份船只列表，无论它们在哪里：家人的船、你常坐的渡轮、
返航的邮轮。**设置 > 设备与服务 > 添加集成 > Live Track Ships > 选定的船只，
无论它们在哪里。** 需要 aisstream.io 的密钥（已设置区域的密钥会自动填入），
每个 Home Assistant 只有一份这样的列表。

每行一艘船：先写 9 位 MMSI，后面可以加上你自己的名称。

```text
244650000 爸爸的船
366999999 渡轮
```

最多 100 艘。aisstream 每个密钥最多跟踪 200 个 MMSI，如果用同一个密钥安装了
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT)，
它会占用其中一部分；超过上限的列表会在加载条目时被拒绝，并说明原因。在条目的
设置中修改列表。

关注的船只和其他船一样画在地图上，只要被收到，无论在哪里；它的状态是与你家的
距离。已经由某个区域显示的船仍归那个区域：一艘船，一个标记。该条目会创建
`sensor.watched_vessels`：列表中现在能收到的船只数，`vessels` 属性中列出每一艘
船、你给它起的名称和它最后已知的状态。

它只触发一个事件 `live_track_ships_watched`，其 `change` 字段说明发生了什么：

| `change` | 何时 |
|---|---|
| `arrived` | 船报告自己已系泊或锚泊，或在没有状态时保持低于 2 节 |
| `departed` | 它重新起航 |
| `silent` | 30 分钟没有收到（系泊或锚泊时为 6 小时）；它会从地图上消失，但可能仍在那里 |
| `heard` | 在 `silent` 之后重新收到 |
| `destination` | 船员更改了目的地；`destination_previous` 保存原来的目的地 |

数据中包含 `watch_id`、`watch`、`identity`、你起的名称 `label`，以及与区域事件
相同的船舶字段，距离和方位从你家算起。到港和离港要等新状态按船自己的时钟持续
5 分钟后才报告，这样以 2 节漂流的船不会来回跳动。重启后一艘船的第一个位置不会
触发任何报告：它只设定起点。目的地由船员手动输入，常常已经过时。

## 地图卡片

船只由 [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)
（`custom:live-track-map-card`）绘制，这是所有 Live Track 集成共用的那一张地图。
它为每艘船绘制专属图标，按船首向旋转，并让它沿水面在真实位置之间滑动，而不是
直线穿过陆地。

**地图卡片随集成一起安装。** 本集成自带一份已发布的地图卡片，由它提供文件，并在
Home Assistant 启动时注册为仪表板资源；不需要下载任何东西，也不需要复制到 `www`。
每个 Live Track 集成都这样做，并且它们之间只保留一行资源：任何一个集成所带的
最高版本，绝不会降级。通过 Marketplace 安装的卡片不会被改动。删除本集成的最后
一个区域时，这一行会交给另一个 Live Track 集成；如果没有了，就会被删除。参见
卡片 README 的
[Live Track](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard#live-track)
一节。

如果你的仪表板资源是用 YAML 设置的（`lovelace: resource_mode: yaml`），就无法
替你注册。这时修复项会给出要添加的确切内容；它看起来像这样，占位符处是集成自己的
地址：

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_ships/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

如果在区域仍然存在时删除了集成的文件（例如通过 Marketplace），而且没有安装其他
Live Track 集成，就没有谁来清理这一行：请在 设置 > 仪表板 > 资源 中删除它。如果
想手动安装卡片，请按照卡片的 README 操作；手动安装在 `/local/` 下的副本，只有在
某个集成所带的副本是更新的版本时，其资源行才会改为指向集成的副本。

用 [auto-entities](https://github.com/thomasloven/lovelace-auto-entities)
把船只交给它，筛选条件为 `domain: geo_location` 和
`attributes: {source: live_track_ships}`。如果安装了其他 Live Track 集成，请为
它们的每个数据源各加一个筛选。

任何其他显示 `geo_location` 实体的地图卡片也会显示这些船，只是没有本卡片的图标
和滑动效果。

公开名单
[EnforcementVessels](https://github.com/StrausbergAutomationWorks/EnforcementVessels)
上的船（用于移民执法的海岸警卫队船只）无论在哪里，都会用海岸警卫队的配色，并
带上名单中的名称和机构来绘制。

### 隐藏船舶类型

每艘船都带有 `marker_group`、`marker_group_label` 和 `marker_group_order`：属于十三个组之一
（货船；油轮；客船和渡轮；渔船；游艇和帆船；拖船、引航和港口服务；政府、搜救和执法；
高速船及其他；未发送类型；渔具浮标；助航设施；基站；搜救飞机）。地图卡的筛选卡
`custom:live-track-map-filter-card` 会列出这些组以及每组在地图上的数量，并隐藏你取消勾选的组；
可以把它放在仪表板的任何视图上。你的选择只保存在该浏览器中。本集成仍然显示一切：它的传感器
统计每一艘船，它的事件也为每一艘船触发。遇险信标没有组，因此永远不会被隐藏。

### 照片和链接

当一艘船发送 IMO 编号，并且 Wikidata 知道这艘船在 Wikimedia Commons 上的照片时，该船带有
`marker_photo`。地图在悬停框中显示这张照片以及摄影者和许可；点击后以更大尺寸打开，并附有
指向照片页面和许可的链接。每艘有 IMO 编号或 MMSI 的船还带有 `marker_links`，即该船在
VesselFinder 上的链接。弹出窗口中的 **Details** 按钮会打开该船通常的对话框。你的 Home Assistant
自己查询 Wikidata 和 Commons，每次 20 个 IMO 编号，间隔十秒，并把每个结果在
`.storage/saw_vessel_photos.json` 中保存 30 天（没有照片时为 14 天）。大约每十艘船中有一艘会有照片：
在我们的测试系统上，521 个 IMO 编号中有 49 个有照片。

## 在哪里查找

你在地图上设定一个**中心点和半径**。中心点可以在世界任何地方；半径可以是 1 到
500 公里，默认 **50 公里**。每艘船的状态是它与你的中心点的距离。

一个圆圈里有多少船，更多取决于*哪片水域*，而不是*多大*。测试中，同样 50 公里的
圆圈，在芝加哥上空大约有 4 艘船，在英格兰南部的索伦特海峡大约有 340 艘：半径
相同，交通量相差约 80 倍。因此集成最多保留一定数量的船只（默认 1,000，可调到
5,000），超出时保留最近的，并在 `ships_in_range` 传感器上说明。

你所有的区域**合计**最多显示 2,500 艘船，无论来自哪个数据源。每个区域的设置里都
有上面提到的滑块，它只能调低这个上限；以已启用区域中最低的设置为准。在较慢的
设备上请调低它。

## 覆盖范围：测量而非承诺

有接收机的地方覆盖良好，没有接收机的地方就没有覆盖，**任何设置都无法创造并不
存在的覆盖**。

2026-09-02 在芝加哥周边用 aisstream.io 测量：

- **北美五大湖**：120 秒内 100 艘不同的船，五个湖以及相连水域都有。
- **芝加哥河，市中心**：繁忙且可靠。
- **Chicago Sanitary and Ship Canal、Cal-Sag Channel、Calumet River**：监听
  一小时，**零艘船**。运河并不空：商业服务通过卫星 AIS 能看到它的顶推船队，而
  免费汇集平台不提供卫星 AIS。交通是真实的；岸基覆盖却不存在。

你的区域里没有船，可能意味着没有接收机，而不是没有船。在认定集成出故障之前，请
先确认你的数据源覆盖你的水域。

不再出现的船并不一定已经离开。这些数据源都不保证送达，因此集成会显示每艘船最后
被收到的时间，并且只在一段静默期后才把它移除。

## 值得专属图标的船

大多数船按类型绘制。有些船有自己的图标：王室和国家游艇，以及芝加哥的观光船、
水上出租车和消防船等知名船只。你知道世界上哪艘船也值得一个吗？请在
<https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues> 提交 issue，
写上船名和 MMSI 或 IMO 编号，如有照片或链接也请附上。

## 语言

本 README：[English](README.md)、[Deutsch](README.de.md)、
[Français](README.fr.md)、[Nederlands](README.nl.md)、**简体中文**、
[Español](README.es.md)、[Italiano](README.it.md)、[Dansk](README.da.md) 和
[Kalaallisut](README.kl.md)（草稿，已发给格陵兰语言秘书处 Oqaasileriffik 审阅；
在此之前，丹麦语页面更可靠）。README 只翻译成少数几种语言：大多数 Home Assistant
用户阅读的语言，以及另有充分理由的几种。每份翻译的 README 都是完整的：英文版中的
所有内容都在每一份里，没有一份会让你回去看英文版才能了解细节。

当你的 Home Assistant 使用以下语言之一时，设置对话框和区域设置会以该语言显示：
English、Dansk、Deutsch、Español、Français、Gaeilge、Íslenska、Italiano、
Nederlands、Norsk Bokmål、Polski、Português、Português (BR)、Suomi、Svenska 和
简体中文。其他语言显示英文对话框。Kalaallisut 还不是 Home Assistant 的语言；我们
已请 Home Assistant 添加，一旦能够显示，对话框就会跟上。

在翻译中发现改变意思或读起来不通的错误了吗？请在
<https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues> 告诉我们。
这些译文是为本项目撰写的，并不是每一份都已经由母语者读过。

**用这些语言读起来有困难吗？** 请在同一地址申请其他语言，我们会尽量满足你。

## Live Track 的一部分

Live Track 是一组 Home Assistant 集成，每种会移动的东西一个，全部画在同一张地图
上。它们共用一个 Python 库
（[saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)）
和地图卡片，所以再安装一个也不会给共用的数据源增加请求。已发布：
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft)、
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT)、
[Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail)、
[Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail)
和 Live Track Ships。每一个都可以单独使用。

## 无隶属关系

与 aisstream.io、Fintraffic、BarentsWatch、MarineTraffic、VesselFinder、任何
船舶运营方或任何海事主管机构均无隶属关系。AIS 是保障航行安全的系统；**本集成
仅供兴趣使用，不可用于导航、避碰或任何实际作业用途。**

## 许可

代码：MIT，见 [LICENSE](LICENSE)。数据和图片来源：[ATTRIBUTION.md](ATTRIBUTION.md)。

## 关键词

Home Assistant AIS · 船舶跟踪 · 船只追踪 · 游艇跟踪 · 海上交通地图 · AIS 地图
卡片 · aisstream.io · Digitraffic · BarentsWatch · geo_location · HACS 集成
