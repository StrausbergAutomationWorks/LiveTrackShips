# Live Track Ships

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Nederlands](README.nl.md) · **简体中文** · [Español](README.es.md) · [Italiano](README.it.md) · [Dansk](README.da.md) · [Kalaallisut](README.kl.md)

在 Home Assistant 地图上实时显示船舶、小艇和其他船只。Live Track Ships 是一个
Home Assistant 集成（custom component，可通过 Marketplace / HACS 安装），显示你
所选区域内船只的 AIS 数据：每艘船的位置，以及船只发送时的船名、航速、航向、
船型和尺寸。每艘船都是一个 `geo_location` 实体，随新位置在地图上移动。区域中心
可以设在世界任何地方。

**状态：0.1.0，首个版本。**

## 游艇也会显示

本集成显示数据源发送的一切内容，无法过滤。装有 AIS 应答器的游艇会像货船一样
出现在地图上：船名、MMSI、呼号，以及精确到约一米的位置。在泊位上开着应答器的
船，会一直留在地图上的泊位处。AIS 没有退出名单。如果想在地图上少看到一些游艇，
请缩小半径。

## 数据来源

每个区域选择一个数据源。

| 数据源 | 覆盖范围 | 需要 |
|---|---|---|
| aisstream.io | 全球，有志愿者接收站的地方 | 免费 API 密钥 |
| Fintraffic Digitraffic | 芬兰及波罗的海水域 | 无 |
| BarentsWatch AIS Live | 挪威水域 | 免费的客户端 ID 和密钥 |

每艘船的 `attribution` 属性注明其来源。全部署名：[ATTRIBUTION.md](ATTRIBUTION.md)。

有接收站的地方覆盖就好，任何设置都无法创造不存在的覆盖。如果你的区域里看不到
船只，可能是缺少接收站，而不是没有船。aisstream.io 在中国沿海和长江等水域依赖
志愿者接收站，覆盖可能很少。

## 要求

- Home Assistant 2026.11 或更高版本。
- aisstream.io：从 [aisstream.io](https://aisstream.io/account) 获取免费 API
  密钥。aisstream 允许每个账户、每个公网 IP 地址各三个连接。
- BarentsWatch：免费的客户端 ID 和密钥。请按发放时的原样输入客户端 ID。
- Digitraffic 不需要密钥或账户。

## 安装

### 通过 Marketplace

本集成尚未收录在 Marketplace 目录中。请通过链接添加：

1. 打开 **设置 > Marketplace**，选择通过链接添加。
2. 输入 `StrausbergAutomationWorks/LiveTrackShips`。如询问类型，选择
   **集成**。
3. 安装 **Live Track Ships**。
4. 重启 Home Assistant。Marketplace 会在 **设置 > 系统 > 修复** 中提供重启。

### 手动安装

1. 下载[最新版本](https://github.com/StrausbergAutomationWorks/LiveTrackShips/releases/latest)的源代码。
2. 将其中的 `custom_components/live_track_ships` 文件夹复制到 Home Assistant
   配置目录的 `custom_components` 文件夹中。
3. 重启 Home Assistant。

## 设置

**设置 > 设备与服务 > 添加集成 > Live Track Ships。** 选择数据源，按需输入密钥，
把地图上的标记拖到你想观察的水域，再选择半径（1 到 500 公里，默认 50）。每个
区域是一个独立条目。当 Home Assistant 使用简体中文时，设置对话框也以简体中文
显示。

在区域的设置中，可以用同一个标记移动中心点；区域会随之重命名并重新加载。所有
区域合计最多显示 2,500 艘船；设置中的滑块只能调低这个上限。在性能较弱的设备上
请使用它。

## 事件：有船进入或离开你的区域

每个区域会触发两个 Home Assistant 事件：船进入圆圈时触发 `live_track_ships_entry`，离开时触发 `live_track_ships_exit`。
集成会报告每一艘船，由你的自动化按名称、类型、船长或航速挑出你关心的船。字段
的名称和单位与船舶实体的属性相同；字段列表和示例见[英文 README](README.md#events-a-ship-comes-into-your-area-or-leaves-it)。

- 只有先在圆圈外（周围的一圈）被收到、再进入圆圈的船才会触发进入事件。第一次就在
  圈内收到的船可能一直都在那里；因此接收站没收到它驶入过程的船不会报告进入。
- 在圈外收到的离开总会报告。停止发送信号的船，只有在报告过它进入时才会报告离开。
- 离开事件要等 2 分钟；船在此之前回到圈内，就不会报告为离开又进入。
- 刚进入时可能还没有名称、类型和尺寸，因为这些信息的发送频率低于位置。

## 关注的船只：在任何地方跟踪选定的船

除了区域，你还可以关注一份船只列表，无论它们在哪里：家人的船、你常坐的渡轮、
返航的邮轮。添加 Live Track Ships 时选择“选定的船只，无论它们在哪里”。需要
aisstream.io 的密钥，每个 Home Assistant 只有一份这样的列表。每行一艘船：先写
9 位 MMSI，后面可以加上你自己的名称，最多 100 艘。

这些船只只要被收到就会显示在地图上，`sensor.watched_vessels` 列出每艘船及其最后
已知状态。事件 `live_track_ships_watched` 带有 `change` 字段：`arrived`, `departed`, `silent`, `heard`, `destination`。到港和离港要等新状态持续 5 分钟后
才报告。详情见[英文 README](README.md#watched-vessels-follow-chosen-ships-anywhere)。

## 值得专属图标的船

大多数船只按船型绘制。有些船有专属图标：皇家和国家游艇，以及著名船只，例如
芝加哥的观光船、水上出租车和消防船。知道世界上哪艘船值得拥有专属图标吗？请在
<https://github.com/StrausbergAutomationWorks/LiveTrackShips/issues> 提交 issue，
写上船名和 MMSI 或 IMO 编号，如有照片或链接也请附上。

如在本翻译或中文对话框中发现重要错误，也请在同一地址告诉我们。

## Live Track 的一部分

Live Track 是一组 Home Assistant 集成，每种会移动的东西一个，全部绘制在同一张
地图上（[LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard)，
随集成一同安装）。已发布：
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft)、
[Live Track SALT](https://github.com/StrausbergAutomationWorks/LiveTrackSALT)、
[Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail)、
[Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail)
和 Live Track Ships。每个都可以单独使用。

## 数据与许可

集成运行时直接从所选数据源读取船只；本仓库不含这些数据源的数据。代码：MIT。

与 aisstream.io、Fintraffic、BarentsWatch 及任何海事主管机构均无关联。
**不可用于导航或避碰。** 全部细节和语言：[英文 README](README.md#languages)。

## 关键词

Home Assistant AIS · 地图上的船 · 船舶追踪 · 船只定位 · 实时海上交通 · AIS 地图 ·
HACS 集成
