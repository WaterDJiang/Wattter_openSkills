---
template_id: 浙江地铁集团版
deck_id: 浙江地铁集团版
kind: deck
display_name: 浙江地铁集团版
summary: "浙江交通集团与浙江轨道集团联合品牌的蓝色轨交培训 deck，完整保留 19 页图文、关系、流程、排期与荣誉表达结构。"
category: brand
keywords: [浙江交通集团, 浙江轨道集团, 轨道交通, 地铁培训, 企业汇报, 项目复盘]
primary_color: "#00489B"
canvas_format: ppt169
page_count: 19
page_types: [cover, toc, chapter, content, ending]
replication_mode: mirror
page_catalog: page_catalog.json
source: "培训PPT模板（浙江交通集团2）.pptx"
---

# 浙江地铁集团版 — Design Specification

## I. Template Overview

面向轨道交通企业培训、运营介绍、项目汇报、年度复盘和荣誉展示的联合品牌 deck。主题模式为 mixed：大多数内容页使用高明度雾蓝背景，章节与时间线页面使用深蓝大面，封面和结尾以列车、天空、花海等轨交摄影建立场景。

本模板采用 mirror 模式，19 张 SVG 按源顺序完整保留原始页面文字、图形几何、图片裁切、渐变、装饰层和联合品牌标识。下游先从 `page_catalog.json` 按页面类型、用途、结构、槽位、密度、图片要求和排除条件选择 canonical reference，再以 §V Page Roster 做人工复核；直接编辑现有文字和图形，不执行 `{{...}}` 占位替换。

## II. Color Scheme

| 角色 | HEX | 使用方式 |
|---|---|---|
| Rail Blue | `#00489B` | 主色；联合品牌、页面锚点、连线、标题胶囊和大面积深蓝结构 |
| Process Blue | `#0070C0` | 流程、节点、图标、月桂和次级强调 |
| Deep Blue | `#003674` / `#081891` | 深色背景、时间线和高权重文字 |
| Accent Yellow | `#FBC641` | 目录箭头、图片描边、关键节点和小面积提示 |
| Sky Blue | `#B8D9FF` | 组织图节点、弱分区和浅色信息承载面 |
| Honor Blue | `#5372D0` | 荣誉月桂渐变和奖项装饰 |
| Text Black | `#262626` | 标题与高权重正文 |
| Body Gray | `#333F50` / `#404040` | 正文、标签和说明文字 |
| White | `#FFFFFF` | 内容卡、深色背景文字和留白 |

主题 XML 还包含 `#FFC000`、`#5B9BD5`、`#70AD47`，但源页实际视觉语言以 `#00489B`、`#0070C0`、白色和雾蓝为主；除原页面已有对象外，不主动扩大其他主题色的使用面积。

## III. Typography

| 角色 | 字体栈 | 说明 |
|---|---|---|
| 中文标题 | `"HarmonyOS Sans SC Black", "OPPOSans B", "Microsoft YaHei", sans-serif` | 页面标题、章节标题、模块名称 |
| 中文正文 | `"HarmonyOS Sans SC", "OPPOSans R", "Microsoft YaHei", sans-serif` | 正文、标签、流程与说明 |
| 英文标题 | `"Gotham Black", Arial, sans-serif` | CONTENTS、数字编号和英文强调 |
| 英文正文 | `Gotham, Arial, sans-serif` | 日期、短标签和辅助说明 |
| 特殊展示字 | `"字制区喜脉体", "思源宋体", "HarmonyOS Sans SC", sans-serif` | 个别封面、荣誉页和数字装饰；缺字时使用后备字体 |

Mirror 页面保留源文件中的字体栈和字号，不在模板层统一重排。

## IV. Signature Design Elements

- **联合品牌锚点**：浙江交通集团与浙江轨道集团 Logo 在内容页右上角固定出现，封面移至左上并放大。
- **轨交摄影骨架**：高架列车、城市花海、车库夜景、轨道绿道和工业场景承担封面、目录、图文与结尾页面的视觉叙事。
- **雾蓝通道背景**：内容页以虚化走廊、云层和径向白光构成高明度背景，保留大面积可读留白。
- **蓝色胶囊与圆形节点**：阶段标题、流程节点、分类标签和环形关系均用深蓝到亮蓝渐变承载。
- **黄色微锚点**：只用于目录翻页、圆形描边、关系节点和重点提示，维持小面积高对比。
- **左上三角页标**：多数内容页使用蓝色小三角作为统一页眉起点；右上联合 Logo 与其形成对角秩序。
- **轨道式推进结构**：横向连线、环形轨道、波浪切面、时间线和表格式排期共同表达连接、推进与阶段演进。

### Communication Rhythm

推荐叙事顺序：`封面立题 → 图片目录 → 概念对比 → 分类拆解 → 场景与系统关系 → 组织与流程 → 时间线与排期 → 荣誉证明 → 花海列车收束`。

- **开场与导航**：`001–002`，用联合品牌、列车场景和图片卡目录建立议题与章节预期。
- **概念与分类**：`003–005`，用双圆对比、双层图标组和三场景图组解释两类、两组或三项内容。
- **框架与系统**：`006–013`，从双区信息板、四维环形关系、章节分隔、五点模型、图片画廊、六宫格、七维关系到九分支组织逐级增加结构复杂度。
- **执行与排期**：`014–016`，用五阶段纵向泳道、年度时间线和矩阵排期承载实施路径。
- **证明与收束**：`017–019`，以月桂奖项墙、荣誉侧栏和花海列车致谢完成可信度证明与情绪收束。

## V. Page Roster

| 文件 | 源页 | 页面结构 | 适用内容 |
|---|---:|---|---|
| `001_cover_rail_brand.svg` | 1 | 左侧白色标题区、右侧深蓝品牌大面、底部高架列车、左上联合 Logo 与白鸽 | 课程封面、企业培训开场、轨交主题发布 |
| `002_toc_image_cards.svg` | 2 | 雾蓝通道背景、超大 CONTENTS 底纹、横向图片卡片目录与黄色翻页箭头 | 4–5 章课程目录、项目导航、场景化议程 |
| `003_content_dual_circle_compare.svg` | 3 | 左右两个大圆形视觉槽、下方横向文字条、中心分隔弧面 | 两类对比、双对象介绍、前后状态 |
| `004_content_six_items_two_groups.svg` | 4 | 上下两层白色圆角面板，每层三枚图标与短说明，右下列车切图 | 六项能力、两组分类、双层职责体系 |
| `005_content_three_scene_cards.svg` | 5 | 三张并列图片卡、顶部三段胶囊标题与连线、底部短说明 | 三阶段、三场景、三案例、三项成果 |
| `006_content_split_overview_panel.svg` | 6 | 深蓝渐变标题带叠加列车、白色大面板内左右信息区和标签组 | 项目概览、双区说明、资源与成果汇总 |
| `007_content_four_dimension_orbit.svg` | 7 | 中央圆形列车图、四个轨道图标、底部左右三项标签与中间箭头 | 四维系统、投入产出、前后端协同 |
| `008_chapter_four_module_preview.svg` | 8 | 深蓝弧形列车背景、居中章节标题、下沿四个圆形图标 | 章节切换、四模块预告、阶段总览 |
| `009_content_five_point_radial.svg` | 9 | 中央圆形主题与基座、外围五个编号节点、底部蓝色波浪 | 五项原则、五大抓手、中心辐射模型 |
| `010_content_photo_gallery.svg` | 10 | 一张横向主图叠加四张小图，统一蓝色渐隐底 | 场景画廊、案例集锦、项目风貌 |
| `011_content_six_module_grid.svg` | 11 | 2×3 六宫格图标卡，底部蓝色结论带 | 六项能力、六类服务、六个模块与一句总结 |
| `012_content_seven_factor_orbit.svg` | 12 | 中央大圆、外围七个编号节点和左右胶囊标签 | 七维模型、七项原则、环形关系拆解 |
| `013_content_nine_branch_map.svg` | 13 | 顶部总标题、九个并列分支节点、下层九个说明槽、底部深蓝总结带 | 九项职责、组织分工、指标分层、课程地图 |
| `014_content_five_stage_swimlane.svg` | 14 | 五列纵向泳道，每列含阶段标题、节点、任务条和下落箭头 | 五阶段流程、成熟度路径、跨部门推进 |
| `015_content_yearly_milestone_timeline.svg` | 15 | 左侧 2021–2025 年度事件列表、右侧信号灯与底部高架列车 | 年度里程碑、发展历程、战略演进 |
| `016_content_half_year_schedule_matrix.svg` | 16 | 顶部六节点时间轴、左侧三行任务标签、六列虚线矩阵 | 半年排期、项目计划、里程碑矩阵 |
| `017_content_four_award_wall.svg` | 17 | 四组月桂奖项位、左右大型月桂包围、雾蓝光束背景 | 核心奖项、认证荣誉、四项代表成果 |
| `018_content_honor_list_summary.svg` | 18 | 左侧深蓝荣誉侧栏含六项月桂，右侧高明度标题/总结区 | 多年荣誉清单、资质证明、成果总结 |
| `019_ending_flower_train_thanks.svg` | 19 | 花海列车全幅照片、天空水彩叠层、居中致谢字与心电线装饰 | 致谢、课程收束、汇报结束 |

## VI. Assets

### Brand and Shared Backgrounds

| 文件 | 尺寸 | 用途 |
|---|---:|---|
| `brand_lockup_cover.png` | 4400×705 | 封面联合品牌标识 |
| `brand_lockup_header.png` | 4398×705 | 内容页右上联合品牌标识 |
| `wind_coast_background.png` | 2000×1125 | Master 底层蓝天、海岸与风机背景 |
| `metro_corridor_background.png` | 1602×901 | 内容页雾蓝通道背景 |
| `cloud_layer_portrait.png` | 832×1456 | 内容页云层纵向裁切层 |
| `corridor_light_background.png` | 1285×723 | 荣誉页与高明度内容背景 |
| `industrial_workers_washout.png` | 1600×900 | 工业/安全/设备场景淡化背景 |
| `cover_industrial_blur.png` | 1500×1000 | 封面左侧虚化工业场景 |
| `cover_cloud_overlay_a.png` | 1200×709 | 封面云雾透明叠层 A |
| `cover_cloud_overlay_b.png` | 1200×709 | 封面云雾透明叠层 B |
| `sky_watercolor_overlay.png` | 1200×1200 | 结尾页天空水彩叠层 |

### Rail and Scenario Photography

| 文件 | 尺寸 | 用途 |
|---|---:|---|
| `elevated_train_cutout.png` | 3710×2473 | 封面与时间线列车主视觉 |
| `elevated_train_cutout_small.png` | 1964×916 | 内容页弧形列车切图 |
| `toc_train_blue_sky.jpeg` | 3714×2474 | 目录列车蓝天场景 |
| `toc_train_flower_field.jpeg` | 3714×2476 | 目录花海列车场景 |
| `toc_train_city_blossom.jpeg` | 1280×1075 | 目录城市花树列车场景 |
| `toc_depot_night.jpeg` | 3299×2475 | 目录车库夜景场景 |
| `toc_train_greenway.jpeg` | 3087×2476 | 目录绿道列车场景 |
| `train_blue_sky_panel.jpeg` | 3714×2476 | 三图内容页蓝天列车照片 |
| `train_blue_sky_orbit.jpeg` | 3711×2475 | 环形系统页中心照片 |
| `train_blue_sky_hub.jpeg` | 3713×2475 | 五点关系页中心照片 |
| `train_blue_sky_gallery_a.jpeg` | 3709×2476 | 图片画廊照片 A |
| `train_blue_sky_gallery_b.jpeg` | 3713×2474 | 图片画廊照片 B |
| `flower_rail_ending_photo.jpeg` | 3716×2478 | 结尾花海列车照片 |
| `metro_tunnel_mono.png` | 1600×908 | 深蓝章节背景中的黑白列车图 |

### Decorative and Diagram Assets

| 文件 | 尺寸 | 用途 |
|---|---:|---|
| `rail_emblem_watermark.png` | 1061×930 | 封面深蓝区大型轨道集团水印 |
| `circle_blue_glow.png` | 179×180 | 圆形节点高光 |
| `glass_platform.png` | 1097×531 | 三图页透明承载台 |
| `white_wave_splash.png` | 2004×325 | 三图页底部白色波浪装饰 |
| `red_light_streak_wide.png` | 896×73 | 图片画廊红色发光装饰 |
| `red_light_streak_small.png` | 348×62 | 图片画廊小型发光装饰 |
| `signal_light.png` | 1280×720 | 年度时间线信号灯视觉 |
| `signal_light_patch.png` | 55×58 | 信号灯局部补片 |
| `palm_shadow.png` | 772×514 | 荣誉侧栏顶部叶影 |
| `palm_leaf.png` | 645×637 | 荣誉侧栏绿色叶片 |
| `white_dove_left.png` | 97×115 | 封面白鸽装饰 |
| `white_dove_right.png` | 106×92 | 封面白鸽装饰 |
| `white_dove_hero.png` | 213×277 | 封面主白鸽装饰 |
