---
deck_id: 浙江地铁运营版
kind: deck
display_name: 浙江地铁运营版
summary: "浙江交通集团与浙江轨道集团蓝色运营培训 deck，完整保留 34 页轨交图片、流程、关系、排期、组织和数据仪表结构。"
canvas_format: ppt169
page_count: 34
primary_color: "#0165FF"
category: brand
keywords: [浙江交通集团, 浙江轨道集团, 轨道交通, 地铁运营, 企业培训, 运营汇报]
replication_mode: mirror
source: "培训PPT模板（浙江交通集团1）.pptx"
---

# 浙江地铁运营版 — Design Specification

## I. Template Overview

面向轨道交通运营培训、安全服务培训、内部汇报、项目计划和经营数据复盘的品牌化 deck。主题模式为 mixed：封面与内容页以大面积白色、雾蓝为主，章节页使用蓝青渐变大面，结尾页回到浅蓝留白。

本模板采用 mirror 模式，34 张 SVG 按源顺序完整保留原始页面文字、图形几何、图片裁切、图表占位和装饰层。页面使用 `<NNN>_<page_type>_<layout_id>.svg` 语义命名；下游先查 `page_catalog.json`，按用途、结构、数量和内容槽位选出 canonical `reference`，再写入 `spec_lock.md page_layouts`。旧的 `NNN_content` 引用由目录中的 `aliases` 兼容。选页后直接编辑页面中的文字和图表对象，不执行 `{{...}}` 占位替换。

本轮导入已保留乱序渐变 stop、负坐标路径渐变、渐变描边、图片 `alphaModFix` 透明度、组填充继承，以及 `donut` / `blockArc` / `snip2DiagRect` / `arc` 的关键几何语义。第 3 页蓝青渐变叠图、第 12 页组填充图标、第 19 页双 U 形轨道均已按原稿复核。

## II. Color Scheme

| 角色 | HEX | 使用方式 |
|---|---|---|
| Rail Blue | `#0165FF` | 主色；流程、卡片标题、关键数字、连接线与品牌锚点 |
| Cyan | `#00BEFF` | 辅色；渐变高光、推进状态、强调节点与轨道装饰 |
| Deep Blue | `#004CC0` | 深色阶段、数据卡和完成态 |
| Ending Blue | `#0056DA` | 结尾艺术字渐变下沿 |
| Pale Blue | `#CCE0FF` | 内容页背景、关系图辅助面与弱分区 |
| Mist Blue | `#E6F0FF` | 浅色背景过渡 |
| Soft Blue | `#F2F7FF` | 卡片底、表格底和次级信息区 |
| Text Black | `#262626` | 标题与高权重正文 |
| Body Gray | `#404040` | 正文、标签与图表说明 |
| White | `#FFFFFF` | 卡片、深色背景文字与结构留白 |

主题 XML 还包含 `#FFC000`、`#5B9BD5`、`#70AD47`，但源页实际视觉语言以蓝、青、雾蓝为主；除复刻原页已有对象外，不主动扩大黄、绿的使用面积。

## III. Typography

| 角色 | 字体栈 | 说明 |
|---|---|---|
| 中文标题 | `"HarmonyOS Sans SC Black", "Microsoft YaHei", sans-serif` | 章节、页面标题、关键数字 |
| 中文正文 | `"HarmonyOS Sans SC", "Microsoft YaHei", sans-serif` | 正文、标签、图表说明 |
| 英文标题 | `"Montserrat Black", "HarmonyOS Sans SC Black", Arial, sans-serif` | Chapter、编号与英文章名 |
| 英文正文 | `Montserrat, Arial, "Microsoft YaHei", sans-serif` | 英文副标题、日期和短标签 |
| 结尾艺术字 | `"云峰飞云体", "HarmonyOS Sans SC Black", "Microsoft YaHei", sans-serif` | 仅 `034_ending_train_thanks.svg`；未安装艺术字时按后备字体显示 |

源页常用正文为 18.67–24px，卡片标题为 26.67–32px，页面标题约 42.67px，章节标题约 80px。Mirror 页面保留源字号，不在模板层统一重排。

## IV. Signature Design Elements

- **轨交图片作为页面骨架**：动车山景用于封面、目录和章节；车辆基地、轨道、运营建筑与运营团队照片承担图文内容页。
- **蓝青渐变轨道语言**：胶囊标题、发光节点、流线、轨道、面积波浪和关键数字均以 `#0165FF → #00BEFF` 表达推进、连接和增长。
- **雾蓝内容底板**：内容页使用浅蓝渐变背景，右上联合品牌标识，底部以蓝青弧形或斜切色块收边。
- **白色承载面**：正文、表格和数据图表优先置于白色卡片或白色大面内，保持轨交行业的秩序感与可读性。
- **圆、六边形与轨道组合**：关系表达大量使用中心圆、卫星节点、六边形模块、时间轨道和层级连线，适合运营系统、能力模型和项目路径。
- **克制的 3D 高光**：节点和 KPI 卡保留源模板的径向高光与轻阴影；不扩展为玻璃拟态或大面积霓虹。

### Communication Rhythm

推荐的运营培训叙事顺序为：`封面立题 → 六章目录 → 章节切换 → 背景/现状 → 对比与拆解 → 方法/流程 → 系统关系 → 排期与组织 → 数据验证 → 总结致谢`。

- **背景与现状**：优先查 `text_canvas` / `photo_gallery_3` / `team_image_text`，用正文承载面、图片画廊或团队图文建立场景。
- **对比与拆解**：查 `dual_checklist_cards` / `dual_stage_track` / `vs_comparison` / `three_stage_columns` / `three_step_chain`。
- **系统关系**：查 `hub_spoke_3` / `hub_spoke_4_hex` / `four_layer_stack` / `radial_segments_5` / `half_circle_ecosystem_5`。
- **实施路径**：查 `wave_timeline_5` / `rising_milestones_4` / `double_track_workflow` / `growth_wave_milestones_6` / `calendar_schedule_4` / `gantt_timeline_6`。
- **组织与治理**：查 `org_chart_three_branch` / `hierarchy_tree_3x6` / `module_matrix_5_plus_2` / `center_workflow_side_support` / `data_table_4_col`。
- **经营结果**：查 `gauge_dashboard_4` / `kpi_cards_3_plus_5` / `dashboard_single_chart` / `dashboard_dual_chart`。

## V. Page Roster

| 文件 | 源页 | 页面结构 | 适用内容 |
|---|---:|---|---|
| `001_cover_rail_hero.svg` | 1 | 白底左文案、对角动车山景、联合品牌标识、超大淡色英文底纹 | 课程封面、运营主题发布、内部培训开场 |
| `002_toc_six_chapters.svg` | 2 | 左侧蓝色目录带、右侧白色悬浮面板、2×3 六章目录 | 4–6 章课程导航、项目总览 |
| `003_chapter_train_fullbleed.svg` | 3 | 蓝青渐变满版、动车背景、左侧章节信息、右侧巨大章号 | 正式章节切换 |
| `004_content_text_canvas.svg` | 4 | 雾蓝背景、白色大内容面、左上文本起点 | 通用正文、定义、长段说明 |
| `005_content_photo_gallery_3.svg` | 5 | 白色大内容面内横排三张运营照片 | 三场景展示、基地/轨道/建筑图集 |
| `006_content_team_image_text.svg` | 6 | 左侧运营团队大图、右侧文字说明 | 团队介绍、岗位职责、服务案例 |
| `007_content_dual_checklist_cards.svg` | 7 | 两张并列圆角清单卡、胶囊标题、三项要点 | 双模块说明、两类职责、并列方案 |
| `008_content_dual_stage_track.svg` | 8 | 双栏推进面板、底部蓝色轨道与方向箭头 | 双阶段推进、左右协同、双线任务 |
| `009_content_vs_comparison.svg` | 9 | 左右斜切对照面板、中心圆形 VS、双侧纵向清单 | 方案对比、现状/目标、传统/升级 |
| `010_content_three_stage_columns.svg` | 10 | 三列编号卡、01–03 淡色大号背景 | 三阶段、三原则、三项能力 |
| `011_content_three_step_chain.svg` | 11 | 三个发光圆节点串联、下方三列详细清单 | 三步流程、前中后阶段、闭环拆解 |
| `012_content_hub_spoke_3.svg` | 12 | 大中心圆与三个发光卫星节点 | 核心主题＋三项外部要素、三方关系 |
| `013_content_hub_spoke_4_hex.svg` | 13 | 中心六边形＋四个六边形卫星、环形关系底 | 四大能力、四个系统、中心辐射模型 |
| `014_content_four_layer_stack.svg` | 14 | 中央四层纵向堆栈、左右四个功能节点、地图点阵底纹 | 系统架构、平台分层、业务能力栈 |
| `015_content_radial_segments_5.svg` | 15 | 中心发光圆＋五个扇形模块 | 五步循环、五类职责、五维模型 |
| `016_content_half_circle_ecosystem_5.svg` | 16 | 下方半圆核心＋上方五个六边形节点 | 生态体系、中心组织与五类支撑 |
| `017_content_wave_timeline_5.svg` | 17 | 五个节点沿多条波形轨道交错排布 | 五阶段演进、交付节奏、波次推进 |
| `018_content_rising_milestones_4.svg` | 18 | 左下到右上的四级里程碑、纸飞机终点 | 成长路径、能力晋级、年度目标 |
| `019_content_double_track_workflow.svg` | 19 | 上下双轨、双圆转向节点、两排任务框 | 双线并行流程、循环运营、跨部门协同 |
| `020_content_growth_wave_milestones_6.svg` | 20 | 六个竖向里程碑叠加多层上升面积波 | 增长路线、成熟度曲线、阶段成果 |
| `021_content_calendar_schedule_4.svg` | 21 | 日历日刻度＋四条日期任务带 | 周计划、短周期项目、活动排程 |
| `022_content_gantt_timeline_6.svg` | 22 | 月份刻度＋六行横向甘特条＋天数 | 半年项目计划、跨月实施路径 |
| `023_content_org_chart_three_branch.svg` | 23 | 一主三分支、每分支两层子项的组织结构图 | 部门架构、三级职责、项目治理 |
| `024_content_hierarchy_tree_3x6.svg` | 24 | 根节点、三菱形中层、六圆形叶节点的树状关系 | 分类体系、组织分解、指标分层 |
| `025_content_module_matrix_5_plus_2.svg` | 25 | 上五列＋下两块的多模块信息矩阵 | 七模块总览、课程地图、产品/服务矩阵 |
| `026_content_center_workflow_side_support.svg` | 26 | 中央五步纵向流程＋左右对称要点面板 | 中心流程与两侧支撑、治理机制 |
| `027_content_data_table_4_col.svg` | 27 | 白色悬浮四列表格、蓝青表头、底部汇总行 | 课程表、职责表、指标清单、数据明细 |
| `028_content_gauge_dashboard_4.svg` | 28 | 四个串联环形仪表、每项百分比和行动方向 | 提升/降低指标、能力评分、成效对比 |
| `029_content_kpi_cards_3_plus_5.svg` | 29 | 上三张大 KPI 卡＋下五张小指标卡 | 经营概览、关键结果、运营数字看板 |
| `030_content_dashboard_single_chart.svg` | 30 | 左侧三张纵向 KPI 卡＋右侧单一大图表 | 核心数字＋趋势/构成图表 |
| `031_content_dashboard_dual_chart.svg` | 31 | 顶部四张 KPI 卡＋底部双图表 | 综合驾驶舱、双主题数据复盘 |
| `032_chapter_minimal_title.svg` | 32 | 雾蓝品牌底上的单一页面标题 | 极简过渡、补充章节标题 |
| `033_content_blank_brand_canvas.svg` | 33 | 仅保留品牌背景与右上联合标识的空白画布 | 自由构建、特殊图形、临时补页 |
| `034_ending_train_thanks.svg` | 34 | 浅蓝大圆、蓝青艺术字、底部动车横幅、右上品牌标识 | 致谢、课程收束、汇报结束 |

### Mirror Fidelity Notes

- `028_content_gauge_dashboard_4.svg` 的四个环形数据扇区来自源 PPTX 图表；源包未携带可直接复用的图表预览，因此 SVG 保留图表边界与可编辑提示，外围刻度、底座、文字和连接关系均已抽取。
- `030_content_dashboard_single_chart.svg`、`031_content_dashboard_dual_chart.svg` 同样保留原图表位置与数据编辑提示；图表本体需在下游用真实数据重新绘制。
- `014_content_four_layer_stack.svg` 的中央层叠卡片含 PowerPoint 3D 透视；SVG 保留卡片层级、尺寸、颜色、连线和节点，3D 投影按二维圆角卡近似。
- 以上限制不影响其他 31 页的 SVG 图形、渐变、图片和分段沟通结构复用。

## VI. Assets

| 文件 | 尺寸 | 状态 | 用途 |
|---|---:|---|---|
| `brand_lockup.png` | 5320×710 | active | 浙江交通集团与浙江轨道集团联合标识；封面及内容页右上品牌锚点 |
| `footer_mascot.jpeg` | 818×818 | source-compatibility | 原模板前 3 页右下角小图；完整镜像保留，不建议用于新内容页 |
| `rail_hero_wide.png` | 2000×1000 | active | 封面与目录动车山景主视觉 |
| `rail_toc_portrait.png` | 795×1125 | active | 目录左侧竖向动车裁切 |
| `chapter_train_bg.png` | 2000×1125 | active | 章节满版动车背景 |
| `depot_train_photo.png` | 1436×868 | active | 车辆基地与列车照片 |
| `elevated_track_photo.png` | 1364×868 | active | 城市高架轨道照片 |
| `operations_building_photo.png` | 1360×868 | active | 运营建筑与环境照片 |
| `operations_team_photo.jpeg` | 3711×2475 | active | 地铁运营服务团队合照 |
| `ending_train_strip.png` | 1920×605 | active | 结尾页底部动车横幅 |
| `assets/depot_train_photo_embedded.svg` | 359×217 | archive | PPTX 内嵌的车辆基地栅格 SVG 副本；完整资产归档 |
| `assets/elevated_track_photo_embedded.svg` | 341×217 | archive | PPTX 内嵌的高架轨道栅格 SVG 副本；完整资产归档 |
| `assets/operations_building_photo_embedded.svg` | 340×217 | archive | PPTX 内嵌的运营建筑栅格 SVG 副本；完整资产归档 |
