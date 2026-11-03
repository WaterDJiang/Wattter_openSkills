# 分类路径与能力状态

由 `config/capabilities.json` 生成；修改元数据后运行 `python3 scripts/catalog.py build`。

## 按目的找到制作路径

| 目的 | 形式（可组合） | 输入示例 | 方法 |
|---|---|---|---|
| **知识与原理**：把知识讲明白 | 概念图解 / 机制演示 / 尺度漫游 / 反事实实验 / 知识寓言 | 给初学者讲清瓶颈怎样限制流量 | [配方](explanation.md) |
| **故事与观点**：让经历与观点被理解 | 角色故事 / 寓言 / 个人经历 / 观点短片 / 手绘电影式角色动画 | 把一次失败写成有转折的小故事 | [配方](story-and-timing.md) |
| **产品与教程**：让人看懂功能与操作 | 产品展示 / UI操作 / 流程教程 / 机械拆解 | 用40秒介绍我这个工具的使用过程 | [配方](video-layout.md) |
| **资讯与纪实**：把事件和证据讲清楚 | 档案纪录片 / 视觉调查 / 新闻包装 / 多机位事件回顾 / 直播式录播包装 | 根据我提供的视频和记录梳理事件时间线 | [配方](video-formats.md) |
| **数据与汇报**：让数字支持结论 | 动态图表 / 对比分析 / 业务复盘 / 研究摘要 | 用这份CSV解释增长来自哪里 | [配方](explanation.md) |
| **视觉与创意**：用运动与材质表达 | 沙画演变 / 生成艺术 / 片头 / 像素循环 / 音乐视觉化 / 季节地图明信片 / 手绘电影式动画 | 做一个沙粒聚成山川的片头 | [配方](visual-recipes.md) |

路径：**想法/材料 → 主用途 → 内容与脚本 → 五种完整方向（形式+策略+画风） → 用户决定 → 代码实现 → MP4及验收**。

分类用于浏览和自动路由，不是新加的开场选择。文字/静态SVG/交互HTML可从知识解释分支直接交付。

## 视觉风格（与用途自由组合）

| ID | 风格 | 基础状态 |
|---|---|---|
| `flat` | [扁平插画](style-catalog.md) | 起步模板；按内容重画 |
| `ink-paper` | [墨线与纸纹](style-catalog.md) | 方法已收录；本片须实现验证 |
| `riso-halftone` | [Risograph 孔版印刷](styles/risograph/STYLE.md) | 方法已收录；本片须实现验证 |
| `pixel` | [像素](style-catalog.md) | 方法已收录；本片须实现验证 |
| `watercolor-brush` | [水彩笔刷](styles/watercolor/STYLE.md) | 方法已收录；本片须实现验证 |
| `sand` | [沙画](style-catalog.md) | 方法已收录；本片须实现验证 |
| `chalk` | [黑板粉笔](styles/chalkboard/STYLE.md) | 方法已收录；本片须实现验证 |
| `particles` | [粒子构成](style-catalog.md) | 起步模板；按内容重画 |
| `glass-mosaic` | [玻璃马赛克](style-catalog.md) | 方法已收录；本片须实现验证 |
| `clay-stopmotion` | [黏土定格外观](style-catalog.md) | 方法已收录；本片须实现验证 |
| `technical` | [精细技术图解](style-catalog.md) | 方法已收录；本片须实现验证 |
| `paper-theatre` | [纸偶舞台](style-catalog.md) | 方法已收录；本片须实现验证 |
| `product-light` | [留白产品界面](style-catalog.md) | 方法已收录；本片须实现验证 |
| `archive-dark` | [档案与地图](style-catalog.md) | 方法已收录；本片须实现验证 |
| `data-editorial` | [编辑式图表](style-catalog.md) | 方法已收录；本片须实现验证 |
| `kinetic-type` | [动态文字](style-catalog.md) | 方法已收录；本片须实现验证 |
| `caption-news` | [字幕新闻](styles/caption-news/STYLE.md) | 方法已收录；本片须实现验证 |
| `newsreel` | [1920s 新闻影片](styles/newsreel/STYLE.md) | 方法已收录；本片须实现验证 |
| `countdown` | [实时倒计时分屏](styles/countdown/STYLE.md) | 方法已收录；本片须实现验证 |
| `city-symphony` | [延时交响](styles/city-symphony/STYLE.md) | 方法已收录；本片须实现验证 |
| `visual-investigation` | [视觉调查](styles/visual-investigation/STYLE.md) | 方法已收录；本片须实现验证 |
| `kino-montage` | [构成主义蒙太奇](styles/kino-montage/STYLE.md) | 方法已收录；本片须实现验证 |
| `telestrator` | [体育战术板](styles/telestrator/STYLE.md) | 方法已收录；本片须实现验证 |
| `news-package` | [电视新闻包装](styles/news-package/STYLE.md) | 方法已收录；本片须实现验证 |
| `satellite-briefing` | [卫星简报](styles/satellite-briefing/STYLE.md) | 方法已收录；本片须实现验证 |
| `briefing-board` | [工程简报板](styles/briefing-board/STYLE.md) | 方法已收录；本片须实现验证 |
| `lidar-survey` | [点云测绘](styles/lidar-survey/STYLE.md) | 方法已收录；本片须实现验证 |
| `white-model` | [白模投影](styles/white-model/STYLE.md) | 方法已收录；本片须实现验证 |
| `data-physical` | [数据实物化](styles/data-physical/STYLE.md) | 方法已收录；本片须实现验证 |
| `teardown` | [产品拆解](styles/teardown/STYLE.md) | 方法已收录；本片须实现验证 |
| `microscope` | [显微叙事](styles/microscope/STYLE.md) | 方法已收录；本片须实现验证 |
| `archive-lighttable` | [档案灯台](styles/archive-lighttable/STYLE.md) | 方法已收录；本片须实现验证 |
| `crayon-book` | [蜡笔儿童绘本](styles/crayon-book/STYLE.md) | 方法已收录；本片须实现验证 |
| `ink-wash` | [中国水墨](styles/ink-wash/STYLE.md) | 方法已收录；本片须实现验证 |
| `impasto` | [油画厚涂](styles/impasto/STYLE.md) | 方法已收录；本片须实现验证 |
| `one-line` | [一笔画](styles/one-line/STYLE.md) | 方法已收录；本片须实现验证 |
| `whiteboard` | [白板讲解](styles/whiteboard/STYLE.md) | 方法已收录；本片须实现验证 |
| `urban-sketch` | [钢笔淡彩](styles/urban-sketch/STYLE.md) | 方法已收录；本片须实现验证 |
| `shadow-puppet` | [皮影戏](styles/shadow-puppet/STYLE.md) | 方法已收录；本片须实现验证 |
| `ukiyoe` | [浮世绘](styles/ukiyoe/STYLE.md) | 方法已收录；本片须实现验证 |
| `papercut-red` | [红色窗花剪纸](styles/papercut-red/STYLE.md) | 方法已收录；本片须实现验证 |
| `paper-lantern` | [纸雕灯影](styles/paper-lantern/STYLE.md) | 方法已收录；本片须实现验证 |
| `halftone-dossier` | [复古半调案卷](styles/halftone-dossier/STYLE.md) | 方法已收录；本片须实现验证 |
| `woodcut` | [木刻版画](styles/woodcut/STYLE.md) | 方法已收录；本片须实现验证 |
| `engraving` | [铜版画](styles/engraving/STYLE.md) | 方法已收录；本片须实现验证 |
| `silkscreen-poster` | [丝印旅行海报](styles/silkscreen-poster/STYLE.md) | 方法已收录；本片须实现验证 |
| `printed-long-take` | [印刷长镜头](styles/printed-long-take/STYLE.md) | 方法已收录；本片须实现验证 |
| `swiss-motion` | [瑞士动态排版](styles/swiss-motion/STYLE.md) | 方法已收录；本片须实现验证 |
| `spy-titles` | [60s 间谍片头](styles/spy-titles/STYLE.md) | 方法已收录；本片须实现验证 |
| `art-deco` | [装饰艺术](styles/art-deco/STYLE.md) | 方法已收录；本片须实现验证 |
| `blueprint` | [蓝图 / 工程制图](styles/blueprint/STYLE.md) | 方法已收录；本片须实现验证 |
| `stained-glass` | [彩色玻璃窗](styles/stained-glass/STYLE.md) | 方法已收录；本片须实现验证 |
| `pictogram-motion` | [象形运动图形](styles/pictogram-motion/STYLE.md) | 方法已收录；本片须实现验证 |
| `ascii-crt` | [ASCII / CRT 终端](styles/ascii-crt/STYLE.md) | 方法已收录；本片须实现验证 |
| `dataviz` | [数据叙事](styles/dataviz/STYLE.md) | 方法已收录；本片须实现验证 |
| `iso-infographic` | [等距信息图](styles/iso-infographic/STYLE.md) | 方法已收录；本片须实现验证 |
| `dark-keynote` | [暗色科技发布](styles/dark-keynote/STYLE.md) | 方法已收录；本片须实现验证 |
| `living-screencast` | [活体实机录屏](styles/living-screencast/STYLE.md) | 方法已收录；本片须实现验证 |
| `hologram-hud` | [科幻全息界面](styles/hologram-hud/STYLE.md) | 方法已收录；本片须实现验证 |
| `transit-map` | [地铁线路图](styles/transit-map/STYLE.md) | 方法已收录；本片须实现验证 |
| `isometric-picture-book` | [等距绘本](styles/isometric-picture-book/STYLE.md) | 方法已收录；本片须实现验证 |
| `circuit-board` | [电路板](styles/circuit-board/STYLE.md) | 方法已收录；本片须实现验证 |
| `rubber-hose` | [1930s 橡皮管卡通](styles/rubber-hose/STYLE.md) | 方法已收录；本片须实现验证 |
| `cel-anime-80s` | [80 年代赛璐璐动画](styles/cel-anime-80s/STYLE.md) | 方法已收录；本片须实现验证 |
| `scifi-toon` | [科幻情景喜剧卡通](styles/scifi-toon/STYLE.md) | 方法已收录；本片须实现验证 |
| `midcentury-toon` | [50s 扁平卡通](styles/midcentury-toon/STYLE.md) | 方法已收录；本片须实现验证 |
| `pixel-rpg` | [16-bit 像素 RPG](styles/pixel-rpg/STYLE.md) | 方法已收录；本片须实现验证 |
| `hd-2d` | [HD-2D](styles/hd-2d/STYLE.md) | 方法已收录；本片须实现验证 |
| `microgame` | [微游戏快闪](styles/microgame/STYLE.md) | 方法已收录；本片须实现验证 |
| `game-show` | [综艺节奏扁平](styles/game-show/STYLE.md) | 方法已收录；本片须实现验证 |
| `silent-film` | [1920s 默片](styles/silent-film/STYLE.md) | 方法已收录；本片须实现验证 |
| `backrooms` | [后室 / 新怪谈](styles/backrooms/STYLE.md) | 方法已收录；本片须实现验证 |
| `brick-toy` | [积木玩具](styles/brick-toy/STYLE.md) | 方法已收录；本片须实现验证 |
| `paper-popup` | [纸片立体书](styles/paper-popup/STYLE.md) | 方法已收录；本片须实现验证 |
| `tilt-shift` | [移轴微缩](styles/tilt-shift/STYLE.md) | 方法已收录；本片须实现验证 |
| `lowpoly-island` | [低多边形等距](styles/lowpoly-island/STYLE.md) | 方法已收录；本片须实现验证 |
| `glass-product` | [玻璃质感产品](styles/glass-product/STYLE.md) | 方法已收录；本片须实现验证 |
| `memphis-diorama` | [孟菲斯微缩景观](styles/memphis-diorama/STYLE.md) | 方法已收录；本片须实现验证 |
| `desktop-flythrough` | [桌面穿梭](styles/desktop-flythrough/STYLE.md) | 方法已收录；本片须实现验证 |
| `seasonal-map-postcard` | [季节地图明信片](seasonal-map.md) | 起步模板；按内容重画 |
| `handpainted-cinema` | [手绘电影式角色动画](handpainted-cinema.md) | 方法已收录；本片须实现验证 |

## 完整参考目录覆盖

固定版本：`bebbbe1aa92a3cb4bb6f83500e61b23a17d1aa00`；参考11组66条全部映射，本库去重后共81项（含15项本库补充），上面的6类是用途。

| 参考组 | 数量 | 本地方法入口 |
|---|---|---|
| 剪辑与纪实 | 8 | [字幕新闻](styles/caption-news/STYLE.md)、[1920s 新闻影片](styles/newsreel/STYLE.md)、[实时倒计时分屏](styles/countdown/STYLE.md)、[延时交响](styles/city-symphony/STYLE.md)、[视觉调查](styles/visual-investigation/STYLE.md)、[构成主义蒙太奇](styles/kino-montage/STYLE.md)、[体育战术板](styles/telestrator/STYLE.md)、[电视新闻包装](styles/news-package/STYLE.md) |
| 实证影像 | 8 | [卫星简报](styles/satellite-briefing/STYLE.md)、[工程简报板](styles/briefing-board/STYLE.md)、[点云测绘](styles/lidar-survey/STYLE.md)、[白模投影](styles/white-model/STYLE.md)、[数据实物化](styles/data-physical/STYLE.md)、[产品拆解](styles/teardown/STYLE.md)、[显微叙事](styles/microscope/STYLE.md)、[档案灯台](styles/archive-lighttable/STYLE.md) |
| 手绘与绘画 | 8 | [蜡笔儿童绘本](styles/crayon-book/STYLE.md)、[水彩笔刷](styles/watercolor/STYLE.md)、[中国水墨](styles/ink-wash/STYLE.md)、[油画厚涂](styles/impasto/STYLE.md)、[一笔画](styles/one-line/STYLE.md)、[白板讲解](styles/whiteboard/STYLE.md)、[钢笔淡彩](styles/urban-sketch/STYLE.md)、[黑板粉笔](styles/chalkboard/STYLE.md) |
| 东方传统 | 4 | [皮影戏](styles/shadow-puppet/STYLE.md)、[浮世绘](styles/ukiyoe/STYLE.md)、[红色窗花剪纸](styles/papercut-red/STYLE.md)、[纸雕灯影](styles/paper-lantern/STYLE.md) |
| 印刷与版画 | 6 | [Risograph 孔版印刷](styles/risograph/STYLE.md)、[复古半调案卷](styles/halftone-dossier/STYLE.md)、[木刻版画](styles/woodcut/STYLE.md)、[铜版画](styles/engraving/STYLE.md)、[丝印旅行海报](styles/silkscreen-poster/STYLE.md)、[印刷长镜头](styles/printed-long-take/STYLE.md) |
| 图形与排版 | 7 | [瑞士动态排版](styles/swiss-motion/STYLE.md)、[60s 间谍片头](styles/spy-titles/STYLE.md)、[装饰艺术](styles/art-deco/STYLE.md)、[蓝图 / 工程制图](styles/blueprint/STYLE.md)、[彩色玻璃窗](styles/stained-glass/STYLE.md)、[象形运动图形](styles/pictogram-motion/STYLE.md)、[ASCII / CRT 终端](styles/ascii-crt/STYLE.md) |
| 信息与发布 | 8 | [数据叙事](styles/dataviz/STYLE.md)、[等距信息图](styles/iso-infographic/STYLE.md)、[暗色科技发布](styles/dark-keynote/STYLE.md)、[活体实机录屏](styles/living-screencast/STYLE.md)、[科幻全息界面](styles/hologram-hud/STYLE.md)、[地铁线路图](styles/transit-map/STYLE.md)、[等距绘本](styles/isometric-picture-book/STYLE.md)、[电路板](styles/circuit-board/STYLE.md) |
| 卡通与动画 | 4 | [1930s 橡皮管卡通](styles/rubber-hose/STYLE.md)、[80 年代赛璐璐动画](styles/cel-anime-80s/STYLE.md)、[科幻情景喜剧卡通](styles/scifi-toon/STYLE.md)、[50s 扁平卡通](styles/midcentury-toon/STYLE.md) |
| 游戏 | 4 | [16-bit 像素 RPG](styles/pixel-rpg/STYLE.md)、[HD-2D](styles/hd-2d/STYLE.md)、[微游戏快闪](styles/microgame/STYLE.md)、[综艺节奏扁平](styles/game-show/STYLE.md) |
| 电影与时代 | 2 | [1920s 默片](styles/silent-film/STYLE.md)、[后室 / 新怪谈](styles/backrooms/STYLE.md) |
| 材质与 3D | 7 | [积木玩具](styles/brick-toy/STYLE.md)、[纸片立体书](styles/paper-popup/STYLE.md)、[移轴微缩](styles/tilt-shift/STYLE.md)、[低多边形等距](styles/lowpoly-island/STYLE.md)、[玻璃质感产品](styles/glass-product/STYLE.md)、[孟菲斯微缩景观](styles/memphis-diorama/STYLE.md)、[桌面穿梭](styles/desktop-flythrough/STYLE.md) |

查看[可筛选风格库](../assets/gallery/styles.html)。SOURCE.md保留带MIT归属的完整方法，STYLE.md为本库中文适配。方法收录不等于每条都完成本库原创视频验证；当前实测样片仍为6个。


长篇画法见[风格配方](style-catalog.md)。具体样例状态独立列于下面，不能从一个样例推广到整类能力。

## 技术选项

| 技术 | 状态 | 用途与边界 |
|---|---|---|
| canvas2d | tested-core | 确定性逐帧绘图，内置导出 |
| svg-html | reference | 静态矢量/交互；自有参考代码 |
| p5js | recipe | 生成艺术、噪声、笔刷；须处理帧时钟 |
| threejs | recipe | 空间遮挡、真实3D镜头；本轮未跑3D |
| gsap | recipe | 复杂补间，必须可seek且禁用自主ticker |
| d3 | recipe | 数据比例尺/路径，动画仍从整数帧派生 |
| remotion | recipe | React视频合成；需要适配原素材/声音/验收契约 |

**有 Three.js 路线**，但当前内置逐帧底座和本轮六例均为 Canvas；Three.js/p5.js/Remotion 等需要为具体镜头接入、检查确定性和渲染，不能当作已安装即用的全部后端。

## 新制样片

| 用途 | 作品 | 风格 | 秒数 | 状态 |
|---|---|---|---|---|
| 知识与原理 | [慢的一环，决定流速](../assets/examples/knowledge/DEMO.md) | 精细技术图解 | 8 | rendered |
| 故事与观点 | [把光，递给下一个人](../assets/examples/story/DEMO.md) | 纸偶舞台 | 8 | rendered |
| 产品与教程 | [把杂乱，收进一个动作](../assets/examples/product/DEMO.md) | 留白产品界面 | 7 | rendered |
| 资讯与纪实 | [六分钟，一条时间线](../assets/examples/documentary/DEMO.md) | 档案与地图 | 8 | rendered |
| 数据与汇报 | [总量增长，来源不同](../assets/examples/data/DEMO.md) | 编辑式图表 | 7 | rendered |
| 视觉与创意 | [风把山，写进沙里](../assets/examples/creative/DEMO.md) | 沙画 | 8 | rendered |

打开[本地画廊](../assets/gallery/index.html)浏览视频和静帧。`rendered`仅表示真实生成并有技术证据；视觉/试听/用户采用详见每片报告。纪实/产品/数据样例含明确标注的虚构或示例内容。
