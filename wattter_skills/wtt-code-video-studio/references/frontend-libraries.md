# 前端代码库与地理路线

由config/frontend-libraries.json生成；修改元数据后运行catalog.py build。

官方功能核实日期：2026-11-16。官方功能研究和按片选型；非新增预装后端。采用时固定精确版本/lockfile、核对LICENSE、资产许可与网络；本表null版本表示未为本片安装锁定。

图片生成/二维/三维的决策与接入步骤见[地理叙事](geographic-storytelling.md)；旧画法状态见[画法适配](visual-recipes.md)。

## 内容对应路线

| route | 内容与选择 | 主选 | 可选 | 替代 | 输入与不适用 |
|---|---|---|---|---|---|
| `terrain-2d` | 二维地形战役与地理叙事：主要俯视地图、路线推演、疆域变色；参考片首选 | d3-geo | topojson-client, turf, proj4js, geotiffjs, gsap | 无 | 已配准晕渲底图＋地点/区域/路线＋剧情事件；不适用：真实绕山俯冲或建筑背面 |
| `map-engine` | 真实地图与倾斜地形：需要地图瓦片与多级缩放；OpenLayers适合GIS/晕渲，Leaflet仅轻量二维替代 | maplibre-gl | deckgl, turf, proj4js | openlayers, leaflet | 可取得并获准使用的样式/瓦片/DEM/glyph/sprite；不适用：把所有替代库一起安装或假设它们都有三维地形 |
| `terrain-3d` | 自定义三维地形与城池：真实高度遮挡、绕行山谷、城池/机械/桌面构图 | threejs | geotiffjs, proj4js, gsap | 无 | 高程或建模网格＋贴图＋模型与单位；不适用：只有一张地图图片却声称能准确绕背面 |
| `globe-3d` | 地球到区域的三维镜头：全球飞行、卫星到地区、地球尺度迁徙 | cesiumjs | proj4js | 无 | 地形/影像/3D Tiles与绝对时间基准；不适用：无数据/服务准备的轻量短地图 |
| `illustrated-2p5d` | 图片生成与分层插画地图：虚构世界、风格插画、纸纹背景和分层视差 | pixijs | gsap | p5js | 固定构图的分层资产/透明遮罩；地理标注另存矢量；不适用：真实高程、疆界和坐标精确性要求 |
| `trajectory-data` | 多路线与流量叙事：大量同时运动轨迹、迁徙、贸易与交通 | deckgl | maplibre-gl, turf, proj4js | d3-geo | 路线坐标＋相对时间戳＋事件/颜色映射；不适用：把轨迹图层当自动战争推演器 |

主选/可选/替代不是整套必须安装；确定路线后只准备本片必需库。下列均为research-only，未完成新的后端渲染验证。

## D3-geo（d3-geo）

职责：地理投影与矢量路径。能力：GeoJSON投影；球面路径与裁切；向SVG/Canvas输出路径。

输入：带坐标的GeoJSON、明确投影和地图范围。边界：不提供地形数据、古代边界或战役逻辑。

接入帧契约：投影参数由绝对帧求值；地名坐标使用相同projection，屏幕标签单独排布。

官方来源：[文档1](https://d3js.org/d3-geo)

## TopoJSON Client（topojson-client）

职责：边界拓扑。能力：TopoJSON转GeoJSON；提取共享边线mesh；合并具名区域。

输入：已制备TopoJSON和对象ID。边界：不识别历史疆域；不负责渲染或动画。

接入帧契约：预处理feature/mesh；占领状态选择固定区域ID，不每帧重建拓扑。

官方来源：[文档1](https://github.com/topojson/topojson-client)

## Turf.js（turf）

职责：地理计算。能力：沿路线按距离取点along；长度/方位角；缓冲与多边形运算。

输入：经纬度GeoJSON、单位、已核实路线。边界：不是寻路服务；两点连线不代表古代行军路线。

接入帧契约：预计算长度；按帧求距离再along；预计算区域交并，避免每帧昂贵运算。

官方来源：[文档1](https://turfjs.org/docs/api/along)

## Proj4js（proj4js）

职责：坐标转换。能力：坐标参考系转换；定义投影与基准；点坐标转换。

输入：源/目标CRS、轴顺序、必要基准参数。边界：不自动识别错标坐标；GCJ-02/BD-09并非可直接当EPSG转换处理。

接入帧契约：加载时统一坐标；明示经纬度顺序，不在每帧来回转换。

官方来源：[文档1](https://proj4js.org/)

## GeoTIFF.js（geotiffjs）

职责：高程与栅格读取。能力：浏览器/Node解析GeoTIFF；读取波段和地理元信息；读取窗口/像素。

输入：可用GeoTIFF/DEM、波段、NoData、CRS。边界：读数据不等于已配准或自动生成晕渲/三维模型。

接入帧契约：预读必要窗口、处理NoData并缓存；高程网格与颜色贴图共用范围。

官方来源：[文档1](https://geotiffjs.github.io/)

## MapLibre GL JS（maplibre-gl）

职责：WebGL地图引擎。能力：矢量/栅格地图与GeoJSON图层；raster-dem三维地形；bearing/pitch镜头。

输入：样式、瓦片/DEM、字体glyph、sprite和可用来源。边界：引擎不附免费无限瓦片；地形不自动包含历史边界。

接入帧契约：逐帧直接设置相机/图层状态，禁用实时flyTo；等待样式/瓦片/字体和绘制完成再截图。

官方来源：[文档1](https://maplibre.org/maplibre-gl-js/docs/examples/3d-terrain/)

## OpenLayers（openlayers）

职责：多数据源地图。能力：矢量与栅格地图；多投影及GeoTIFF接入路线；WebGL高程晕渲。

输入：CRS明确的数据源、地形编码及加载策略。边界：晕渲是二维地形表现，不能据此称真实三维相机。

接入帧契约：显式设置view与样式变量；等待rendercomplete和所有源数据就绪，不用墙钟动画。

官方来源：[文档1](https://openlayers.org/en/latest/examples/webgl-shaded-relief.html)

## Leaflet（leaflet）

职责：轻量二维地图。能力：瓦片/图片叠图；GeoJSON线面与标记；SVG/Canvas覆盖层。

输入：地图影像或瓦片、经纬度数据。边界：核心不提供三维地形或倾斜相机；主站可能指向预发布文档。

接入帧契约：关闭平移缩放动画；按帧设置视图，等待tile和覆盖层；采用版本对应API。

官方来源：[文档1](https://leafletjs.com/reference-1.9.4.html)

## Three.js（threejs）

职责：自定义三维场景。能力：几何/灯光/PBR材质与相机；位移贴图改变顶点形成地形；glTF模型与动画加载。

输入：网格/高程、贴图、模型、坐标与单位。边界：不是GIS数据源；低细分网格不能表达精细位移；单张图没有背面几何。

接入帧契约：停止默认循环；从帧号设置相机/物体/动画绝对时间；await纹理/模型后显式render。

官方来源：[文档1](https://threejs.org/docs/pages/MeshStandardMaterial.html)、[文档2](https://threejs.org/docs/pages/GLTFLoader.html)

## deck.gl（deckgl）

职责：GPU地理数据可视化。能力：TripsLayer时间轨迹；TerrainLayer从编码高程图建表面；路径/区域/文字/弧线图层。

输入：轨迹坐标与相对时间戳、高程编码、viewState。边界：TripsLayer不生成军事箭头或战争规则；避免大整数时间戳精度损失。

接入帧契约：关闭自动过渡，currentTime由帧求值；重设全部图层props并等待资源；可叠MapLibre但不是必须。

官方来源：[文档1](https://deck.gl/docs/api-reference/geo-layers/trips-layer)、[文档2](https://deck.gl/docs/api-reference/geo-layers/terrain-layer)

## CesiumJS（cesiumjs）

职责：地球尺度三维地理。能力：地球/地形/影像与3D Tiles；时变实体与相机；可控模拟时钟。

输入：地形/影像/3D Tiles来源、坐标、服务配置。边界：部分托管服务需要token；库不附无限免费数据；全球LOD加载增加导出复杂度。

接入帧契约：关闭默认循环/时钟推进；固定currentTime和相机，显式渲染并等瓦片LOD稳定；记录GPU环境。

官方来源：[文档1](https://cesium.com/learn/cesiumjs/ref-doc/Viewer.html)、[文档2](https://cesium.com/learn/cesiumjs/ref-doc/Clock.html)

## PixiJS（pixijs）

职责：高性能二维合成。能力：Sprite/Container/Graphics场景图；图片遮罩与滤镜；分层视差与精灵批处理。

输入：分层图片/透明资产、遮罩与固定坐标。边界：不是三维重建；平面视差无法展示正确建筑背面。

接入帧契约：停止ticker；从帧重设变换与滤镜，等待Assets后显式render；固定随机与反馈缓存。

官方来源：[文档1](https://pixijs.com/8.x/guides/components/scene-objects)

## p5.js（p5js）

职责：创意绘图。能力：程序图形；噪声/粒子和手绘式画法；受控逐帧重画。

输入：主体几何、固定seed、样式实现。边界：不自动具备GIS/DEM/历史疆域；笔刷插件另核版本与许可。

接入帧契约：noLoop后按frame求绝对状态并redraw；随机点预生成，不依赖前帧残留。

官方来源：[文档1](https://p5js.org/reference/p5/noLoop/)

## GSAP（gsap）

职责：补间编排。能力：Timeline seek；相机/面板/路径参数补间；标签与入场节奏。

输入：可插值对象、时间区间及初始状态。边界：不是渲染器或地图数据；seek跳过回调副作用会丢状态。

接入帧契约：建立暂停时间轴，seek(frame/fps)；状态不能仅靠onComplete累积；不启动第二帧时钟。

官方来源：[文档1](https://gsap.com/docs/v3/GSAP/Timeline/)

## Remotion（remotion）

职责：React视频宿主。能力：useCurrentFrame帧时钟；按帧合成组件；视频与声音编排及导出。

输入：React工程、素材与独立渲染配置。边界：不是地图画法；许可按实际用途核对；当前自带render.cjs验收不自动适用于该宿主。

接入帧契约：使用宿主当前帧，适配异步就绪/素材锁/四帧确认/编码验收，禁止嵌套自主时钟。

官方来源：[文档1](https://www.remotion.dev/docs/use-current-frame)
