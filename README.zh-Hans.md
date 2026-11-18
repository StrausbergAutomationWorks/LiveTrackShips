# Live Track Ships

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · **简体中文** · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Kalaallisut](README.kl.md) · [所有语言](#语言)

**Home Assistant 的船只和船艇，显示在一张地图上。** Live Track Ships 把船只、船艇以及其他一切发送 AIS（船只用来报告自己位置的无线电信号）的东西显示在你的 Home Assistant 地图上，可以是你附近，也可以是你选择的世界任何地方。它还能跟踪选定的船只，无论它们去哪里，并在船只进入或离开你的区域时通知你的自动化。

> **Live Track Ships 是 Live Track 的一个模块**。Live Track 是一组 Home Assistant 集成，把一切移动的东西以及它们穿过的天气画在同一张共享地图上：飞机、船只、火车和天气。可以单独安装，也可以和其他模块一起安装（[见下方列表](#live-track-的组成部分其他模块)）。

> **正在成长，欢迎提出想法。** Live Track Ships 目前覆盖志愿者运行接收机的全世界，芬兰和挪威更详细，还有你自己的接收机。我们正在添加更多数据来源和国家。缺少你那里的吗？[提出建议](#帮助它成长)，或者自己添加：我们会帮你完成。

**状态：0.1.0，首个版本。** 可通过链接添加到 Marketplace（[见下文](#安装步骤)）；它还不在 Marketplace 的目录中。

StrausbergAutomationWorks 的原创作品。与 aisstream.io、Fintraffic（芬兰）、BarentsWatch（挪威）、Wikidata、Wikimedia Commons、VesselFinder、MarineTraffic、任何船舶运营者或任何海事主管机构均无关联，也未获得它们的认可。

> ⚠ **这不是安全系统。** 它显示公开数据，通常延迟几秒，有时几分钟，而且只显示接收机恰好收到的内容。它不能用于导航、避碰或任何其他操作用途。在水上，请使用你自己的 AIS、雷达、海图和甚高频（VHF）无线电。

---

## 目录

1. [全部功能](#全部功能)
2. [适用地区](#适用地区)
3. [Live Track 的组成部分：其他模块](#live-track-的组成部分其他模块)
4. [开始之前](#开始之前)
5. [安装步骤](#安装步骤)
6. [设置步骤](#设置步骤)
7. [解锁更多功能的免费密钥](#解锁更多功能的免费密钥)
8. [把地图放到仪表盘上](#把地图放到仪表盘上)
9. [在自动化中使用](#在自动化中使用)
10. [地图上的全部内容详解](#地图上的全部内容详解)
11. [它创建的全部实体](#它创建的全部实体)
12. [它发送和下载的内容](#它发送和下载的内容)
13. [帮助它成长](#帮助它成长)
14. [语言](#语言)
15. [致谢与许可](#致谢与许可)
16. [关键词](#关键词)

---

## 全部功能

### 在地图上，无需任何设置

你添加一个**区域**：地图上的一个中心点和一个半径，再加一个数据来源。之后下面的所有内容都会出现在这个区域里。Fintraffic Digitraffic（芬兰）和你自己的接收机不需要密钥；aisstream.io 和 BarentsWatch（挪威）需要一个免费密钥（[见下文](#用你自己的免费密钥或账户开启)）。

| 内容 | 范围 | 来源 |
|---|---|---|
| **船只**：货船、油轮、渡轮、拖船、渔船、游艇和帆船，每艘都有自己的图标，并按航向旋转 | 每个区域内 | 你选择的来源 |
| **不是船的东西**：渔具浮标、助航设施、AIS 基站、搜救飞机和遇险信标 | 每个区域内，来源发送时 | 你选择的来源 |
| **照片和链接**：已知时显示船只照片，以及 VesselFinder 上该船的链接 | 每艘有 IMO 编号或 MMSI 的船只 | Wikidata 和 Wikimedia Commons |
| **航迹**：船只过去 24 小时去过的地方，在你需要时绘制 | 每艘船只 | 由你自己的 Home Assistant 保存 |
| **从事移民执法的海岸警卫队船只**，以海岸警卫队的颜色绘制 | 在任何被收到的地方 | 公开的 EnforcementVessels 列表 |
| **到达和离开**：船只进入或离开区域时，为你的自动化触发一个事件 | 每个区域内 | 由你自己的 Home Assistant 计算 |

### 用你自己的免费密钥或账户开启

| 免费密钥或账户 | 增加的内容 |
|---|---|
| **aisstream.io** 密钥 | 世界上任何有志愿者运行接收机的地方的船只；以及**关注的船只**：无论身在何处都被跟踪的选定船只，在到达、离开、失去信号或更改目的地时触发事件 |
| **BarentsWatch** 账户（挪威） | 挪威水域（包括斯瓦尔巴群岛）的船只，每个位置都带有船名和船型 |

每个都只需几分钟即可获得：[下文有分步说明](#解锁更多功能的免费密钥)。

---

## 适用地区

| 地区 | 你能得到什么 | 来源 | 需要 |
|---|---|---|---|
| **全世界** | 有志愿者运行接收机的地方的船只：繁忙的海岸和港口附近效果好，其他地方稀少或没有 | aisstream.io | 一个免费密钥 |
| **欧洲**：芬兰和波罗的海 | 芬兰和波罗的海水域的船只，每分钟更新位置 | Fintraffic Digitraffic（芬兰） | 无 |
| **欧洲**：挪威 | 挪威水域（包括斯瓦尔巴群岛）的船只，每个位置都带有船名和船型 | BarentsWatch（挪威） | 一个免费账户 |
| **你自己的接收机**：任何地方 | 你的天线收到的一切，无需互联网 | 你自己的 AIS 接收机 | 一台通过 UDP 发送 NMEA 的接收机 |

每个区域选择一个来源。会出现哪些类型的东西、位置有多新、船只资料有多完整，都取决于这个来源。

⚠ **有接收机的地方覆盖良好，没有接收机的地方就没有覆盖。** 任何设置都无法创造不存在的覆盖。2026-09-02 在芝加哥（美国）周边用 aisstream.io 测得：五大湖上 120 秒内收到 100 艘船，但城市以南的运河上一小时内一艘也没有，而那里确实有拖驳船队在航行：商业服务通过卫星看到它们，而免费来源不提供卫星数据。**你的区域里没有船，可能意味着没有接收机，而不是没有船。** 在认为出了故障之前，请先确认你的来源覆盖你的水域。

⚠ **你自己的接收机：**

* 一个区域监听一个端口。两台接收机需要两个端口。
* 接收机在你的圆圈内收到的一切都会显示，包括助航设施和基站。它的站点传感器也会统计在圆圈外收到的内容。
* NMEA 语句不带日期，所以位置的时间是 Home Assistant 收到它的时间。
* 这个来源不显示转向率。
* 到目前为止，这只用通过 UDP 发送的录制语句测试过，还没有用真正的接收机测试。如果你用自己的接收机试了，[告诉我们效果如何](#帮助它成长)。

不在列表中？[告诉我们](#帮助它成长)。只要有人公开发布数据，我们就会考虑添加。

---

## Live Track 的组成部分：其他模块

Live Track 是一组 Home Assistant 集成，每种移动的东西一个，全部画在同一张地图卡片上。每个都能单独工作；合在一起就成为一幅实时画面。它们共享地图卡片和一个 Python 库（[saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)），因此再安装一个模块不会向另一个模块已在读取的来源增加请求。

| 模块 | 在地图上显示什么 | 状态 |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | 通过 ADS-B 显示头顶的飞机，带航线和机型图标 | 已发布 |
| **Live Track Ships** | 通过 AIS 显示船只和船艇，在你附近或任何地方（本模块） | 已发布 |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | 北美、欧洲和澳大利亚的通勤列车 | 已发布 |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | 北美、欧洲和澳大利亚的城际和长途列车 | 已发布 |
| [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) | 来自公开列表的移民和联邦执法飞机及船只 | 已发布 |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | 天气、风暴和自然灾害 | 已发布 |
| Live Track Stations | 每个车站的发车信息板和"该出发了"提醒 | 计划中 |
| Live Track Satellites | 从头顶经过的卫星 | 计划中 |
| Live Track Freight Trains | 铁路公开发布的货运和工程列车 | 计划中 |
| Live Track Transit | 城市公交、有轨电车、渡轮和地铁 | 计划中 |
| Live Track Intercity Buses | 城际和区域长途客车 | 计划中 |
| Live Track Commuter Buses | 通勤巴士 | 计划中 |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | 每个模块都在上面绘制的共享地图卡片 | 已发布，随每个模块一起安装 |

一切都是免费和开源的。没有任何功能只留给赞助者。

---

## 开始之前

* **Home Assistant** 2026.11 或更高版本。
* 你的 Home Assistant 中的 **Marketplace**（HACS），用来方便地安装和更新。没有它，你也可以手动复制文件。
* Home Assistant 需要**互联网访问**，用于在线来源和照片。你自己的接收机不需要互联网。
* **一个数据来源。** Digitraffic（芬兰）和你自己的接收机不需要账户。aisstream.io 和 BarentsWatch（挪威）需要一个免费密钥（[分步说明](#解锁更多功能的免费密钥)）。
* **可选：你自己的 AIS 接收机。** 接收机或为它解码的程序，通过 UDP 把 NMEA 语句（`!AIVDM`）发送到同一网络中你的 Home Assistant 的地址。在 AIS-catcher 中是 `-u <address> <port>`；在 rtl-ais 中是 `-h <address> -P <port>`；OpenCPN 和 Signal K 把它添加为 UDP 输出连接。通过 USB 连接的接收机（例如 dAISy）需要上述程序之一来转发它的语句。
* **可选：Marketplace 中的 auto-entities**，用来把标记放到地图上（见[把地图放到仪表盘上](#把地图放到仪表盘上)）。
* 无需付费。Digitraffic 和你自己的接收机不需要账户；只有 aisstream.io 和 BarentsWatch 需要免费密钥。

---

## 安装步骤

### 通过 Marketplace（推荐）

Live Track Ships 还不在 Marketplace 的目录中。通过它的链接添加：

1. 在 Home Assistant 中打开 **设置 → Marketplace**（HACS）。
2. 选择 **从链接添加**（或三点菜单 → **自定义存储库**）。
3. 输入 `StrausbergAutomationWorks/LiveTrackShips`。如果询问类型，选择 **集成**。
4. 在列表中找到 **Live Track Ships**，选择 **下载** 或 **安装**。
5. **重启 Home Assistant**：**设置 → 系统 → 修复** 会提供重启，或使用 **设置 → 系统 → 重启**。

### 手动安装

1. 下载[最新版本](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest)的源代码。
2. 把其中的 `custom_components/live_track_ships` 文件夹复制到 Home Assistant 配置文件夹中的 `custom_components` 文件夹（如果没有 `custom_components`，请创建它）。
3. 重启 Home Assistant。

---

## 设置步骤

1. 打开 **设置 → 设备与服务**。
2. 选择 **添加集成**（右下角），搜索 **Live Track Ships**。
3. 选择 **某个区域内的所有船只**。（另一个选项 **选定的船只，无论它们在哪里** 用于在任何地方跟踪一份船只列表：见[关注的船只](#关注的船只任意位置的选定船只)。）
4. **数据来源**：选择一个。如果不确定：在芬兰选择 Fintraffic Digitraffic，它不需要密钥；在挪威选择 BarentsWatch；其他地方选择 aisstream.io。
5. **API 密钥**（aisstream.io），或 **客户端 ID** 和 **客户端密钥**（BarentsWatch）：粘贴进去（[如何获取](#解锁更多功能的免费密钥)）。你已经设置过的区域会帮你自动填好。
6. **UDP 端口（自己的接收机）**：仅用于你自己的接收机。输入它发送到的端口，范围 1024 到 65535。如果你没有改过，保留 10110。
7. **中心点**：把标记拖到你想观察的水域中央。它最初在你的家。
8. **半径（公里）**：1 到 500 公里（0.6 到 310 英里）。如果不确定，保留 50 公里（31 英里）。
9. **最多跟踪船只数**：保留 1,000，除非你的设备性能较弱。
10. 选择 **提交**。

就这样。船只会在一两分钟内按来源发送的情况陆续出现。船型和尺寸会在接下来的几分钟里补全。每个区域是一个条目，标题为 *Ships near <latitude>, <longitude>*。用同样的方法添加更多区域。

* 同一个来源不能两次观察同一个中心点。
* 如果一个 BarentsWatch 圆圈至少有 5% 位于 BarentsWatch 发布的水域之外，对话框会在创建区域前告诉你比例。选择 **提交** 仍可保留这个圆圈。

### 更改显示内容：选项

在你要更改的区域上打开 **设置 → 设备与服务 → Live Track Ships → 配置**（齿轮图标）。每个选项的通俗说明：

| 选项 | 作用 | 默认值 |
|---|---|---|
| **中心点** | 移动区域；区域会按新位置重新命名并重新加载 | 你的家 |
| **半径（公里）** | 显示离中心点多远的船只，1 到 500 公里（0.6 到 310 英里） | 50 公里（31 英里） |
| **最多跟踪船只数** | 这个区域的安全上限，1 到 5,000；超过时保留最近的 | 1,000 |
| **地图上最多显示的船只数（所有 Live Track Ships 条目合计）** | 所有区域合计的上限，100 到 2,500；在性能较弱的设备上请调低；以所有区域中最低的设置为准 | 2,500 |
| **UDP 端口（自己的接收机）** | 你的接收机发送到的端口；更改后区域会重新加载 | 10110 |

一个圆圈里有多少船，取决于是哪片水域，远远超过取决于圆圈大小。测试中，一个 50 公里（31 英里）的圆圈在芝加哥（美国）上空约有 4 艘船，在索伦特海峡（英格兰）上空约有 340 艘：同样的半径，交通量相差约 80 倍。当上限截断列表时，该区域的 `sensor.ships_in_range` 会说明。

---

## 解锁更多功能的免费密钥

这些都是免费且属于个人的：每个安装 Live Track Ships 的人都获取自己的。添加区域时，把每个密钥粘贴到设置对话框中（[设置步骤](#设置步骤)的第 5 步）。

### aisstream.io（船只和关注的船只，全世界）

1. 打开 <https://aisstream.io/account> 并登录。（aisstream.io 顶部的 **API keys** 链接打开的是同一页面。）
2. 在那里创建一个新的 API 密钥。
3. 立即复制密钥：aisstream.io 只显示一次。
4. 把它粘贴到 **API 密钥** 中。

⚠ aisstream.io 每个账户允许三个连接，每个公网地址也允许三个。Live Track Ships 最多使用两个：一个用于你的所有区域，一个用于你关注的船只；如果 Live Track SALT 用同一个密钥安装，它会与 Live Track SALT 共用后者。如果其他程序使用同一个密钥或同一条互联网连接，也要把它们算进去。

### BarentsWatch（挪威水域的船只，挪威）

1. 打开 <https://www.barentswatch.no/minside/>，创建用户或登录。
2. 在 **API access (for developers)**（*API-tilgang (for utviklere)*）下，选择 **New Client**（*Ny klient*）。
3. 选择 AIS 客户端，而不是 API 客户端。
4. 复制**客户端 ID**。它看起来像 `your.email@example.com:live_track_ships`。原样粘贴到 **客户端 ID** 中。
5. 把**客户端密钥**复制到 **客户端密钥** 中。它只显示一次；如果你没有保存，请生成一个新的。

---

## 把地图放到仪表盘上

地图是 [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)，每个 Live Track 模块都在这张卡片上绘制。**它随 Live Track Ships 一起安装**：无需下载，无需复制，无需添加资源。

1. 打开一个仪表盘，选择铅笔图标（**编辑仪表盘**），然后选择 **添加卡片**。
2. 滚动到底部，选择 **手动**。
3. 粘贴以下内容，然后选择 **保存**：

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

标记需要 Marketplace 中的 [auto-entities](https://github.com/thomasloven/lovelace-auto-entities)。如果安装了其他 Live Track 模块，为它们的每个来源再添加一个 `- domain: geo_location` 过滤器（`live_track_aircraft`、`live_track_weather` 等）。

**在地图上：**

* 每艘船都用自己的图标绘制，按航向旋转，并在它报告的位置之间沿水面滑动，而不是横穿陆地。
* 把鼠标**指向**一艘船可以看到它的名字，有照片时还会显示照片。**点击**它可以看到照片、链接、**Track** 和 **Details**（[照片和链接](#照片和链接)、[航迹](#航迹)）。
* **过滤卡片**（`custom:live-track-map-filter-card`）会隐藏你取消勾选的船只类型（[隐藏船只类型](#隐藏船只类型)）。

如果你的仪表盘资源是用 YAML 设置的（`lovelace: resource_mode: yaml`），就无法替你自动注册：这时 **修复** 中会出现一个问题，给出需要添加的确切行。你自己通过 Marketplace 安装的卡片不会被改动。如果在区域仍然设置着的情况下删除了集成的文件，而且没有安装其他 Live Track 模块，请自己在 **设置 → 仪表盘 → 资源** 中删除卡片的那一行。任何其他显示 `geo_location` 实体的地图卡片也会显示这些船只，只是没有它们的图标。

---

## 在自动化中使用

一切都是普通的 Home Assistant 实体或事件，所以自动化编辑器可以直接使用，无需代码。

**当一艘长度超过 150 米（490 英尺）的船进入你的区域时发送通知：**

1. **设置 → 自动化与场景 → 创建自动化 → 创建新的自动化**。
2. **每当**：**添加触发条件**，搜索 **收到手动事件**，在 **事件类型** 中输入 `live_track_ships_entry`。
3. **且如果**：**添加条件** → **模板**，输入这个 **值模板**：`{{ trigger.event.data.length_m | default(0) > 150 }}`
4. **就执行**：**添加动作**，搜索你手机的通知动作（它带有你手机的名字），并输入这条消息：

   ```text
   {{ trigger.event.data.name | default('一艘船') }}，{{ trigger.event.data.length_m }} 米，距离 {{ trigger.event.data.distance_km }} 公里
   ```

5. **保存**。

**其他想法：** 傍晚的渡轮到达你在挪威的港口时开灯；家人的船（一艘关注的船只）回到芬兰时发消息；你要接的邮轮到达悉尼（澳大利亚）时发通知；用 `sensor.ships_in_range` 在仪表盘上显示港口里的船只数量。

**区域事件。** 每当有船进入圆圈，每个区域都会触发 `live_track_ships_entry`，离开时触发 `live_track_ships_exit`。每艘船都会被报告；由你的自动化挑出重要的。字段名称和单位与船只的属性相同，来源没有发送的字段会被省略：

| 字段 | 内容 |
|---|---|
| `area_id`、`area` | 区域配置条目的 ID 和标题 |
| `identity` | MMSI |
| `name`、`call_sign`、`imo` | 发送时才有 |
| `object_kind` | `vessel`、`net_buoy`、`aton`、`base_station`、`sar_aircraft` 或 `distress_beacon` |
| `ship_type`、`ship_type_label`、`length_m`、`beam_m`、`draught_m`、`destination`、`nav_status` | 仅船只，发送时才有 |
| `speed_kmh`、`course_deg`、`heading_deg` | 发送时才有 |
| `latitude`、`longitude`、`distance_km`、`bearing_from_centre_deg`、`last_seen` | 收到它的位置，以区域中心点为起点 |
| `entity_id` | 仅进入时：`geo_location.vessel_<MMSI>`，船只在地图上时才有 |
| `reason` | 仅离开时：`left`（在圆圈外收到）或 `silent`（有一段时间没收到，所以可能还在） |

⚠ 需要知道的四件事：

* **只有先在圆圈外收到过的船，才会报告到达。** 一艘第一次就在圆圈内收到的船，可能一直都在那里：重启后，来源在很多分钟内仍会发来没有移动过的船。所以，接收机在它驶入时漏掉的船，或者在圆圈内才打开应答器的船，不会被报告。
* **在圆圈外收到的离开总会被报告**，即使这艘船在 Home Assistant 启动之前就已在那里。失去信号的船，只有在报告过它的到达时，才会被报告为离开（`reason: silent`）。
* **离开会等待 2 分钟。** 沿着圆圈边缘提前回来的船，不会被报告为离开后又到达。
* **到达时可能缺少资料。** 船名、船型和尺寸通过比位置更慢的消息传送。第一次收到的船，可能只带一个位置到达，别无其他。

同一水域上的两个区域各自触发自己的事件。关于绘制多少艘船的上限，绝不会导致船只进入或离开。

**关注的船只的事件。** [关注的船只](#关注的船只任意位置的选定船只)触发一个事件 `live_track_ships_watched`，其 `change` 说明发生了什么：

| `change` | 何时 |
|---|---|
| `arrived` | 船只报告已系泊或锚泊，或者在没有状态时保持低于 3.7 公里/小时（2 节） |
| `departed` | 它再次航行 |
| `silent` | 30 分钟没有收到（如果系泊或锚泊则为 6 小时）；它会离开地图，但可能还在那里 |
| `heard` | 在 `silent` 之后再次收到 |
| `destination` | 船员更改了目的地；`destination_previous` 保存旧的目的地 |

数据包含 `watch_id`、`watch`、`identity`、你的 `label`，以及与区域事件相同的船只字段，距离和方位以你的家为起点。到达和离开会等到新状态按船只自己的时钟保持 5 分钟后才报告，这样慢慢漂流的船不会来回切换。重启后一艘船的第一个位置不会触发任何报告：它只作为起点。目的地由船员手动输入，经常是过时的。

---

## 地图上的全部内容详解

AIS（Automatic Identification System，船舶自动识别系统）是一种甚高频无线电广播，船只用它向其他船只和岸上报告自己的位置、身份和航程。它相当于飞机发送的 ADS-B 在航海上的版本。商船必须配备；许多游艇自愿配备，通常是功率较低的 B 类设备。AIS 是公开广播的：任何有接收机的人都能收到，公共服务也会转发它。**Live Track Ships 显示来源发送的一切。** 不过滤任何内容，也没有在 Home Assistant 中隐藏某一类的设置。

### 船只

每艘船都是一个标记，其状态是它与区域中心点的距离，单位为公里。大多数船只按类型绘制：货船、油轮、渡轮、拖船等。有些船有自己的专属图标：王室和国家游艇，以及某座城市的观光船、水上出租车和消防船等知名船只。知道世界上哪艘船值得拥有专属图标吗？[提出建议](#帮助它成长)，附上它的名字和 MMSI 或 IMO 编号，如果有照片或链接也请附上。

为了让船只一离开就立即消失，每个在线来源被请求的范围都是比你的圆圈稍宽的一圈（宽 10%，至少 1 公里），而你自己的接收机会发送它收到的一切。只有圆圈内的船会被保留：在圆圈外收到的船会立即离开地图。不再被收到的船会在一段静默时间后消失。不再出现的船不一定已经离开：这些来源都不保证送达每条消息。

⚠ **船型经常缺失，尤其是小船。** 位置和船名几乎每条消息都有。船型和尺寸在另一条较慢的消息中发送，很多 B 类设备很少发送它。可以预期很多船（其中包括大多数小船）不显示船型或尺寸，而且在 Home Assistant 重启后的几分钟内，所有船只的资料都很少。这是数据本身的情况，不是故障。收到过的船型和尺寸在重启后会保留。

船只的属性包括船名、MMSI、呼号、航速、航向、船首向、长度、宽度、船型、目的地、`object_kind`、`last_seen` 和 `attribution`，每项都只在来源发送时才有。两个区域都看到的船只是同一个实体。

### 私人船艇和帆船

发送 AIS 的游艇在你的地图上看起来和货船完全一样。根据船艇广播的内容，它的实体可能包含：

* 它的**船名**，也是地图上显示的标签；
* 它的 **MMSI** 和**无线电呼号**，两者都是永久的，并且可以公开查询；
* 它的**位置**，精确到大约一米，它的上一个位置，以及各自被收到的时间；
* 发送时，还有它的航速、航向和船首向，以及长度、宽度和船型。

一艘在码头仍开着应答器的船，只要还在发送，就会一直停在地图上它的泊位处。任何能打开你的地图的人，也可以对这样的船点击 **Track**，看到它在过去 24 小时（或你设置的时长）里去过哪里，包括它的泊位。

AIS 不像飞机那样有退出名单，这个集成也不会自己编造一个。如果你希望地图上的私人船艇少一些，请缩小半径。

### 不是船的东西

每个实体都带有 `object_kind`：`vessel`、`net_buoy`（渔具浮标）、`aton`（助航设施：浮标、信标或灯塔）、`base_station`（岸上的 AIS 站）、`sar_aircraft`（搜救飞机）或 `distress_beacon`。大多数通过国际电信联盟（ITU）分配给它们的识别码格式来区分。渔具浮标不行：它们使用和船只一样的识别码发送，所以要靠它们的出厂名称（FISHING BOUY、NET MARK、BUOY）以及没有广播长度来识别。

不是船的东西在显示时没有船型、尺寸和航行状态。渔具浮标随着它们的绳索漂流，所以保留航速和航向，并画成一条鱼，指向它们漂流的方向。

会出现哪些，取决于来源。在一个晚上测得：

| 来源 | 渔具浮标 | 搜救飞机 | 助航设施、基站 |
|---|---|---|---|
| BarentsWatch | 有 | 有 | 未见到 |
| Digitraffic | 未见到 | 有 | 未见到 |
| aisstream.io | 未见到 | 未见到 | 未见到 |
| 你自己的接收机 | 视收到的而定 | 视收到的而定 | 视收到的而定 |

aisstream.io 只提供了船只位置和船只资料，无论是在五大湖（北美）上空，还是在 BarentsWatch 显示浮标的同一片挪威和丹麦水域上空。

### 从事移民执法的海岸警卫队船只

公开的 [EnforcementVessels](https://github.com/StrausbergAutomationWorks/EnforcementVessels) 列表中的船只（用于移民执法的美国海岸警卫队船只），无论在哪里被收到，都会以海岸警卫队的颜色绘制，并显示列表中的船名和机构。

### 关注的船只：任意位置的选定船只

除了区域，你还可以跟踪一份船只列表，无论它们在哪里：家人的船、你常坐的渡轮、回家的邮轮。这需要一个 aisstream.io 密钥，每个 Home Assistant 只有一份这样的列表。

1. 打开 **设置 → 设备与服务**，选择 **添加集成**，搜索 **Live Track Ships**。
2. 选择 **选定的船只，无论它们在哪里**。
3. **API 密钥**：已设置区域的密钥会自动填好。
4. **船只**：每行一艘船，先写它的 9 位 MMSI，如果愿意，再写一个你自己起的名字：

   ```text
   244650000 爸爸的船
   366999999 渡轮
   ```

5. 选择 **提交**。

最多 100 艘船。aisstream.io 每个密钥最多跟踪 200 个 MMSI，如果 [Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT) 用同一个密钥安装，会占用其中一部分。超出的列表会在条目加载时被拒绝，并说明原因。要更改列表，请打开该条目的 **配置**。

关注的船只和其他船只一样画在地图上，无论在哪里被收到，其状态是它与你的家的距离。已经显示它的区域会保留它：一艘船，一个标记。这个条目会添加 `sensor.watched_vessels`：列表中现在能收到多少艘船。它的 `vessels` 属性列出每一艘，以及它的名字和最后已知的状态。它的事件在[在自动化中使用](#在自动化中使用)中说明。

### 照片和链接

当一艘船发送了 IMO 编号，而且 Wikidata 知道 Wikimedia Commons 上有这艘船的照片时，这艘船就带有 `marker_photo`。当你指向这艘船时，地图会显示照片，以及摄影者和许可证；点击后照片会放大，并附有照片页面和许可证的链接。每艘有 IMO 编号或 MMSI 的船还带有 `marker_links`，即 VesselFinder 上该船的链接。弹出窗口中的 **Details** 按钮会打开这艘船的常规对话框。

你的 Home Assistant 自己查询 Wikidata 和 Commons，每次 20 个 IMO 编号，间隔十秒，并把每个答案在 `.storage/saw_vessel_photos.json` 中保留 30 天（没有照片时为 14 天）。大约每十艘船有一艘有照片：在我们的测试系统中，521 个 IMO 编号中有 49 个有照片。

⚠ 照片显示的可能是这艘船以前的名字：IMO 编号属于船体，船改名后仍然跟着它。

### 航迹

每艘船还带有 `marker_track`。点击一艘船，在它的弹出窗口中点击 **Track**：地图会画出它去过的地方，是一条终止于这艘船的线，而且这条线会在你观看时不断延长。**Hide track** 会把它去掉。在你要求之前不会画任何东西，这样繁忙的港口不会被线条淹没。

航迹只包含这艘船在你的地图上时报告的位置，并精简为每 25 米（82 英尺）或每 10 分钟一个，30 秒内绝不会有两个。你的 Home Assistant 把它保存在内存中，并存入 `.storage/saw_vessel_tracks.json`，所以重启后仍然存在。它涵盖过去 24 小时。要保留更多或更少：

1. 打开 **设置 → 工具 → 动作**。
2. 选择动作 **Live Track Ships: 设置航迹时长**。
3. 输入 **小时**，1 到 168（一周），然后选择 **执行动作**。

它同时适用于所有区域；设置得更短会立即删除较早的位置。

⚠ 首次安装时航迹是空的。离开过区域或失去过信号的船会有一段空缺，画成前后两个位置之间的直线。

### 隐藏船只类型

每艘船都带有 `marker_group`、`marker_group_label` 和 `marker_group_order`：十三个组之一（货运；油轮；客运和渡轮；渔业；游艇和帆船；拖船、引航和港口服务；政府、搜救和执法；高速及其他；未发送类型；渔具浮标；助航设施；基站；搜救飞机）。地图卡片的过滤卡片 `custom:live-track-map-filter-card` 列出这些组以及每组在地图上的数量，并隐藏你取消勾选的组。把它放在仪表盘的任何视图中。你的选择只保存在这个浏览器中。

隐藏只在地图上发生：集成仍然统计每艘船，并为每艘船触发事件。遇险信标没有组，所以永远不会被隐藏。

---

## 它创建的全部实体

| 实体 | 是什么 |
|---|---|
| `geo_location.vessel_<MMSI>` | 每艘船或其他 AIS 对象一个标记；其状态是与区域中心点（对于关注的船只，则是与你的家）的距离，单位为公里。它会出现和消失，没有唯一 ID |
| `sensor.ships_in_range` | 每个区域一个：显示多少艘船，以及上限是否截断了列表 |
| `sensor.ais_station` | 仅你自己的接收机：每分钟消息数。它的属性给出 `vessels_heard`（过去 10 分钟内）、`farthest_km` 和 `farthest_mmsi`（距区域中心点）、`last_message`、`udp_port`、`listening`，以及端口无法打开时的 `port_error`。它每 30 秒更新一次，所以停止发送的接收机会显示 0 |
| `sensor.watched_vessels` | 仅关注的船只：你的列表中现在能收到多少艘船 |

每次更新都会变化的属性不会进入 Home Assistant 的历史记录，这样你的数据库不会因此增长：每艘船的 `marker_photo`、`marker_links` 和 `marker_track`，以及各传感器中快速变化的属性。

**你的数据库。** Home Assistant 的记录器在实体每次变化时都会存一行新数据，而一艘行驶中的船在每次报告位置时都会变化。在我们的测试系统中，一个有 43 艘船的区域在大约 30 小时内写入了 27,109 行，占整个数据库的 8.8%。默认情况下，记录器保留 10 天，并在每晚当地时间 04:12 清理，所以增长会趋于平稳，但可能停在你不想要的大小。

一艘船每次出现都使用同一个实体 ID `geo_location.vessel_<MMSI>`，所以一个模式 `geo_location.vessel_*` 就涵盖了这个集成放到地图上的一切。只保留最近一天的数据：

1. **设置 → 自动化与场景 → 创建自动化 → 创建新的自动化**。
2. 打开三点菜单，选择 **YAML 编辑**，把所有内容替换为以下内容，然后选择 **保存**：

```yaml
alias: 精简船只历史
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

如果省略 `keep_days`（默认 0），它们的所有行会一次性删除。如果完全不想记录，请在 `configuration.yaml` 中把这个模式放在 `recorder:` → `exclude:` → `entity_globs:` 下；设置为绘制历史的地图卡片（`history_start`）就没有轨迹可画了。`sensor.ships_in_range` 只是一个数字，保留它的成本很低。

---

## 它发送和下载的内容

**关于你的位置。** 每个区域的中心点默认是你的家，除非你移动它。它只发送给你为该区域选择的来源：发送给 aisstream.io 的是一个包围比你的圆圈稍大一圈（宽 10%，至少 1 公里）的矩形；发送给 Digitraffic（芬兰）的是中心点和这个更大的半径；发送给 BarentsWatch（挪威）的是这个更大的圆圈。对于关注的船只，你列表中的 MMSI 编号会发送给 aisstream.io。你自己的接收机不向任何地方发送任何东西：Home Assistant 只是在接听。对于照片，你地图上船只的 IMO 编号会发送给 Wikidata 和 Wikimedia Commons，不包含任何关于你的信息。要停止这一切，请在 **设置 → 设备与服务 → Live Track Ships** 中删除该区域或关注的船只条目。除此之外，不会向任何地方发送关于你的任何信息。

**数据量。**

* **aisstream.io**：所有区域共用一个连接，关注的船只另用一个，都保持打开；船只在报告时到达。出错后会在暂停一段时间后重新连接。
* **Digitraffic**：每 60 秒获取一次位置，每 15 分钟获取一次船只资料，只针对你的圆圈。出错后在下一轮重试。
* **BarentsWatch**：每个区域一个保持打开的数据流。如果 150 秒内什么都没收到，会重新连接。
* **照片**：每次 20 个 IMO 编号，间隔 10 秒，只针对过去 30 天内（没有照片时为 14 天）没有查询过的船只。失败的请求会稍后重试。
* **你自己的接收机**：不下载任何东西。

---

## 帮助它成长

Live Track Ships 仍在成长。我们发现新的数据来源和国家就会添加，也想知道你接下来希望看到什么。

### 提出建议

缺少你的国家或 AIS 服务吗？有什么地方不对，或难以理解？用你觉得最方便的方式告诉我们：

* [**填写一份简短的表单**](https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues/new?template=zh-Hans.yml)，使用中文。你需要一个免费的 GitHub 账户。
* **发送电子邮件**到 [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org)。无需账户。

无论哪种方式，告诉我们以下内容会有帮助：

* 你希望看到什么，以及在世界上的什么地方；
* 数据发布地点的链接，如果你知道的话（开放数据页面、公开数据源、服务网站）：不是必需的，但会有帮助；
* 你的 Home Assistant 语言，如果问题出在措辞或翻译上。

用英语或你自己的语言书写都可以，哪种方便用哪种。

### 在我们的帮助下自己添加

如果你想自己添加什么，我们会帮你完成，从第一个问题到最终发布。开始时你不需要是开发者：

* **翻译。** 设置对话框中的文字是一个文本文件里的一小串短语。我们会告诉你是哪个文件、哪几行。
* **新的数据来源。** 告诉我们数据在哪里发布。我们可以一起写代码，或者帮你检查你写的代码。
* **在你所在的地方测试。** 安装它，查看地图上你所在的部分，告诉我们哪些正确、哪些不正确。
* **修正这份 README。** 如果某个步骤与你看到的不一致，告诉我们你看到了什么。

[**告诉我们你的想法**](https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues/new?template=zh-Hans.yml)，或写信到 [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org)，我们会回复接下来的步骤。

---

## 语言

本 README：[English](README.md)、[Deutsch](README.de.md)、[Français](README.fr.md)、[Nederlands](README.nl.md)、**简体中文**、[Español](README.es.md)、[Italiano](README.it.md)、[Dansk](README.da.md) 和 [Kalaallisut](README.kl.md)（一份简短的草稿，已发给格陵兰语言秘书处 Oqaasileriffik 审阅；在此之前，丹麦语页面才是可靠的）。每份翻译的 README 都是完整的。

当你的 Home Assistant 语言是以下之一时，设置对话框和选项会以该语言显示：English、Dansk、Deutsch、Español、Français、Gaeilge、Íslenska、Italiano、Nederlands、Norsk Bokmål、Polski、Português、Português (BR)、Suomi、Svenska 和简体中文。其他语言显示英语。格陵兰语（Kalaallisut）还不是 Home Assistant 的语言；我们已请求 Home Assistant 添加它。地图卡片自身的标签（**Track**、**Details**）在所有语言中都是英语。

发现翻译中的错误，或需要其他语言？请在 <https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues> 告诉我们，或者[在我们的帮助下翻译](#在我们的帮助下自己添加)。

---

## 致谢与许可

* **aisstream.io**：没有公布的条款。<https://aisstream.io>
* **Fintraffic Digitraffic**（芬兰）：数据采用 CC BY 4.0。<https://www.digitraffic.fi/en/terms-of-service/>
* **BarentsWatch**（挪威）：数据采用挪威政府开放数据许可证（NLOD）。<https://www.barentswatch.no/en/articles/api-terms-and-conditions/>
* **你自己的接收机**：你自己的数据。
* **Wikidata**：CC0。**Wikimedia Commons**：每张照片采用各自的许可证，并与摄影者和许可证一起显示。
* **VesselFinder**：只提供链接；不从那里获取任何内容。
* **EnforcementVessels**：ODbL 1.0。<https://github.com/StrausbergAutomationWorks/EnforcementVessels>

这个集成做出的改变：单位经过换算，并且只保留你的圆圈内的船只。每个船只实体以及每个区域的 `sensor.ships_in_range` 都带有一个 `attribution`，写明它的来源；Home Assistant 会在实体详情中显示它。如果你向他人展示这些数据，例如在公开的仪表盘上，请保留署名，并阅读来源自己的条款。确切的署名文字以及船只图标的署名见 [ATTRIBUTION.md](ATTRIBUTION.md)。

这些组织都没有制作或认可这个集成。

**代码**：MIT，见 [LICENSE](LICENSE)。

**开发者须知：** 来自你自己接收机的 AIS 语句由 [pyais](https://github.com/M0r13n/pyais)（MIT）解码；Home Assistant 在首次加载集成时会自行安装 `saw-livetrack` 和 `pyais`。`tests/` 中的测试各自用 Python 单独运行；有些需要安装 Home Assistant，`*_live` 测试需要你自己的密钥。

---

## 关键词

Home Assistant 船只 · Home Assistant AIS · 船舶追踪 · 船只跟踪 · 船艇追踪 · 海上交通地图 · AIS 地图卡片 · AIS 接收机 · NMEA · AIS-catcher · aisstream.io · Digitraffic · BarentsWatch · ship tracking · vessel tracker · Schiffsverfolgung · suivi des navires · scheepvaart volgen · seguimiento de barcos · tracciamento navi · skibstrafik · geo_location · 地图卡片 · Lovelace · HACS · Marketplace · Live Track · LiveTrack · StrausbergAutomationWorks
