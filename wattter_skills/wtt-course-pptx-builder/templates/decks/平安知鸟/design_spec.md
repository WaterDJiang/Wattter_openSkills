---
deck_id: 平安知鸟
kind: deck
summary: "Pingan Zhiniao premium business course deck — unified Kaiti typography, restrained navy, warm gold, and diagram-rich executive-training layouts."
canvas_format: ppt169
page_count: 19
primary_color: "#003396"
category: brand
keywords: [平安知鸟, 楷体, 商务高级感, 企业培训, AI课程, 实战工作坊]
replication_mode: standard
fonts:
  all: "STKaiti / KaiTi"
font_sizes:
  body: 24
  dense_body_min: 20
  annotation: 18
  card_title: 28
  page_title: 52
  chapter_title: 84
  cover_title: 104
placeholders:
  - KICKER
  - TITLE
  - SUBTITLE
  - SECTION_LABEL
  - PAGE_TITLE
  - PAGE_SUBTITLE
  - CHAPTER_NUMBER
  - CHAPTER_TITLE
  - CHAPTER_SUBTITLE
  - CHAPTER_EN
  - CARD_01_NUM
  - CARD_01_TITLE
  - CARD_01_META
  - CARD_01_OUTCOME
  - CARD_02_NUM
  - CARD_02_TITLE
  - CARD_02_META
  - CARD_02_OUTCOME
  - CARD_03_NUM
  - CARD_03_TITLE
  - CARD_03_META
  - CARD_03_OUTCOME
  - CARD_04_NUM
  - CARD_04_TITLE
  - CARD_04_META
  - CARD_04_OUTCOME
  - TOC_01_NUM
  - TOC_01_TITLE
  - TOC_01_DESC
  - TOC_02_NUM
  - TOC_02_TITLE
  - TOC_02_DESC
  - TOC_03_NUM
  - TOC_03_TITLE
  - TOC_03_DESC
  - TOC_04_NUM
  - TOC_04_TITLE
  - TOC_04_DESC
  - THANK_YOU_LINE
  - THANK_YOU_CN
  - TAGLINE
  - STEP_01_NUM
  - STEP_01_TITLE
  - STEP_01_DESC
  - STEP_02_NUM
  - STEP_02_TITLE
  - STEP_02_DESC
  - STEP_03_NUM
  - STEP_03_TITLE
  - STEP_03_DESC
  - STEP_04_NUM
  - STEP_04_TITLE
  - STEP_04_DESC
  - BULLET_01_NUM
  - BULLET_01_TITLE
  - BULLET_01_TEXT
  - BULLET_02_NUM
  - BULLET_02_TITLE
  - BULLET_02_TEXT
  - BULLET_03_NUM
  - BULLET_03_TITLE
  - BULLET_03_TEXT
  - BULLET_04_NUM
  - BULLET_04_TITLE
  - BULLET_04_TEXT
  - BULLET_05_NUM
  - BULLET_05_TITLE
  - BULLET_05_TEXT
  - COL_A_TITLE
  - COL_A_LABEL_01
  - COL_A_01
  - COL_A_LABEL_02
  - COL_A_02
  - COL_A_LABEL_03
  - COL_A_03
  - COL_B_TITLE
  - COL_B_LABEL_01
  - COL_B_01
  - COL_B_LABEL_02
  - COL_B_02
  - COL_B_LABEL_03
  - COL_B_03
  - STAT_01_NUM
  - STAT_01_LABEL
  - STAT_01_DESC
  - STAT_02_NUM
  - STAT_02_LABEL
  - STAT_02_DESC
  - STAT_03_NUM
  - STAT_03_LABEL
  - STAT_03_DESC
---

# 平安知鸟 (Pingan Zhiniao) — Design Specification

## I. Template Overview

面向平安知鸟企业培训、AI 课程和实战工作坊的品牌化 deck。新版在保留知鸟 Logo、统一楷体字形和课程页型契约的基础上，对齐《AI办公提效 6课- 装修版.pptx》的商务高级感：白底大留白、深海军蓝主视觉、亮蓝信息强调、少量暖金曲线，以及扁平而克制的卡片体系。

设计事实来自附件的完整导入分析：1280×720、1 个 master、7 个 layout、140 张 slide；主题色 `#003396` / `#2E75FF` / `#C7A661`，章节页稳定使用蓝色大面与金色波形分界。模板吸收这些高频语言，但不复制附件的具体文案与品牌资产。

新增训战项目结构页参考《增长飞轮》营销材料的构图语言：多阶段项目路线、三线并行服务、密集课程表、导师督导卡、运营闭环和产品特点环绕图。该参考只用于结构、构图和 SVG 图形关系；所有橙色、原始 Logo、照片和主题皮肤均不迁移，统一重映射到本 deck 的海军蓝 / 亮蓝 / 暖金 / 浅蓝体系。

## II. Color Scheme

| 角色 | HEX | 使用规则 |
|---|---|---|
| Executive Navy | `#003396` | 章节大面、最终步骤、右栏重点、品牌锚点 |
| Brand Blue | `#2E75FF` | 编号、关键线、首要信息强调 |
| Comparison Cyan | `#1F90E0` | 双圆对比与分点图中的第二信息系列 |
| Chapter Blue | `#194791` | 章节渐变起点，只用于结构页 |
| Warm Gold | `#C7A661` | 曲线分界、细规则、单个高价值强调；单页面积不超过 10% |
| Pale Blue | `#ECF6FE` | 页脚波形、弱背景块 |
| Soft Panel | `#F1F8FE` | 浅色卡片与局部背景 |
| Theme Gray | `#44546A` | 次级标题与章节辅助信息 |
| Body Gray | `#666666` | 正文、说明、meta |
| Text Black | `#262626` | 主标题与卡片标题 |
| Hairline Gray | `#E7E6E6` | 1px 分隔线与描边 |
| White | `#FFFFFF` | 主背景、深色面文字 |

## III. Typography

所有页面、所有语言和所有信息层级统一使用 `STKaiti, KaiTi` 楷体字体栈。

| 角色 | 字体栈 | 层级方式 |
|---|---|---|
| 封面 / 页面标题 / 数据巨号 | STKaiti, KaiTi | 通过字号与字重形成主层级 |
| 卡片标题 / 重点标签 | STKaiti, KaiTi | 使用 700 字重和品牌色强调 |
| 正文 / 注释 | STKaiti, KaiTi | 使用常规字重和灰色层级 |
| 英文标签 / 数字 / 页眉页脚 | STKaiti, KaiTi | 与中文保持同一楷体字形 |

> **字体硬约束**：SVG 中不得出现任何非楷体字体声明；所有 `<text>` 统一使用 `font-family="STKaiti, KaiTi"`。

### Font Size Hierarchy

本模板以楷体正文 `24px`（导出后约 `18pt`）为字号锚点。高密度图表、五项卡片和辐射图可以降到 `20px`，但正文与信息标签不得低于该下限。

| 角色 | 标准字号 | 使用边界 |
|---|---:|---|
| 页脚 / 极弱注释 | 16–18px | 不承担主要信息 |
| 图表标注 / 编号 | 18–20px | 仅用于短标签 |
| 高密度正文下限 | 20px | 五项并列等受限布局 |
| 标准正文 | 22–24px | 默认使用 24px |
| 卡片 / 分点标题 | 26–30px | 单行短标题 |
| 页面副标题 | 22–30px | 按信息权重选择 |
| 页面标题 | 52px | 内容页统一 |
| 章节标题 | 84–88px | 结构页 |
| 封面 / 结尾主标题 | 104px | 主视觉焦点 |
| 数据巨号 | 112px | KPI 与统计页 |

> **禁止缩字适配**：内容放不下时，优先删减文案、拆页或更换版式；不得把正文压回 14–17px。五项卡片与辐射图中的说明文字必须保持短句。

## IV. Signature Design Elements

- **蓝色大面 + 暖金曲线**：封面、章节、结尾使用非对称蓝色大面，金色曲线作为白区与蓝区之间的唯一高价值分界。
- **商务页眉 chrome**：左上 6px 金色短竖线 + 小号章节标签，右上保留知鸟 Logo；页面标题下使用 1px 灰线。
- **扁平信息面**：内容页以白底和浅蓝面板为主，圆角固定 6px；不使用大面积阴影、发光或透明玻璃卡片。
- **蓝金节制**：蓝色负责信息层级，金色只负责“转折、重点、完成态”，不与蓝色争夺视觉面积。
- **插画降频**：3D 插画只出现在封面与结尾；内容页全部回归图形、线条、留白和文字。
- **图形化表达优先**：对比关系优先使用双圆交叠；并列要点优先使用中心辐射或编号卡片，不把所有内容退化成文字列表。
- **结构页更有气势，内容页更安静**：章节页可使用渐变大色块；内容页保持白底、细线与明确栅格。
- **复杂项目页使用“系统图”承载**：训战实施方案、陪跑服务、课程排期和运营闭环优先使用时间轴、泳道、表格矩阵、环形闭环和中心环绕图，不把复杂方案压成普通卡片列表。
- **参考模板只借结构**：来自《增长飞轮》营销材料的橙色图形，在本 deck 内全部转换为 `#003396` / `#2E75FF` / `#C7A661` / `#F1F8FE`；禁止保留参考模板橙色皮肤。

## V. Page Roster

| 文件 | 页型 | 新版视觉特征 | 关键占位 |
|---|---|---|---|
| `01_cover.svg` | cover | 左侧白底标题，右侧蓝色曲面 + 金线 + 知鸟插画 | `{{KICKER}}` `{{TITLE}}` `{{SUBTITLE}}` |
| `02_toc.svg` | toc | 2×2 扁平目录块，蓝 / 深蓝 / 金三档强调，无圆形徽章堆叠 | `{{PAGE_TITLE}}` `{{TOC_01_*}}`…`{{TOC_04_*}}` |
| `03_chapter.svg` | chapter classic | 左白右蓝，巨大章号 + 金线，适合正式章节切换 | `{{CHAPTER_NUMBER}}` `{{CHAPTER_TITLE}}` `{{CHAPTER_SUBTITLE}}` |
| `03b_chapter_modern.svg` | chapter modern | 附件式蓝色大面与金色波形分界，英文章标在白区 | `{{CHAPTER_EN}}` `{{CHAPTER_TITLE}}` `{{CHAPTER_SUBTITLE}}` |
| `04_content.svg` | content cards | 白底 2×2 信息卡；窄色条、方形编号、轻描边 | `{{CARD_01_*}}`…`{{CARD_04_*}}` |
| `04b_content_flow.svg` | content flow | 浅蓝流程带 + 四步竖卡；终点用深海军蓝、金色完成态 | `{{STEP_01_*}}`…`{{STEP_04_*}}` |
| `04c_content_bullets.svg` | content bullets | 左侧深蓝章节面，右侧五条编辑式清单 | `{{BULLET_01_*}}`…`{{BULLET_05_*}}` |
| `04d_content_compare.svg` | content compare | 白 / 浅蓝双栏，金色中轴与 VS 标记，右栏深蓝表头 | `{{COL_A_*}}` `{{COL_B_*}}` |
| `04e_content_stats.svg` | content stats | 三张大数字卡，蓝 / 金 / 深蓝形成强弱节奏 | `{{STAT_01_*}}`…`{{STAT_03_*}}` |
| `04f_content_compare_orbit.svg` | content compare orbit | 双圆交叠 + 左右各 3 个论点，适合 Before/After、传统/AI、方案 A/B | `{{COL_A_*}}` `{{COL_B_*}}` `{{PAGE_SUBTITLE}}` |
| `04g_content_points_radial.svg` | content points radial | 中心主题 + 五个卫星分点，适合公式、能力、要素、模块概览 | `{{BULLET_01_*}}`…`{{BULLET_05_*}}` |
| `04h_content_points_cards.svg` | content points cards | 五张编号卡片，中间重点卡深蓝突出，适合工具、原则、清单 | `{{BULLET_01_*}}`…`{{BULLET_05_*}}` |
| `04i_content_project_roadmap.svg` | content project roadmap | 参考训战实施方案构图：顶部长箭头时间轴 + 五阶段列 + 底部成果带，适合 7 天 / 21 天 / 项目实施计划 | `{{STEP_01_*}}`…`{{STEP_04_*}}` `{{CARD_*}}` `{{STAT_*}}` |
| `04j_content_service_swimlanes.svg` | content service swimlanes | 参考陪跑服务页构图：左侧三线标签 + 中央服务泳道 + 右侧准备清单 + 底部周节奏 | `{{STEP_*}}` `{{CARD_*}}` `{{BULLET_*}}` `{{COL_B_*}}` |
| `04k_content_agenda_matrix.svg` | content agenda matrix | 参考课程安排页构图：日期 / 时间 / 模块 / 内容 / 工具五列表格，适合密集课表和训练营日程 | `{{COL_*}}` `{{STEP_*}}` `{{CARD_*}}` |
| `04l_content_mentor_three_cards.svg` | content mentor three cards | 参考督导页构图：左侧导师/对象视觉锚点 + 右侧三张主题督导卡 | `{{COL_A_*}}` `{{CARD_01_*}}`…`{{CARD_03_*}}` |
| `04m_content_operation_loop.svg` | content operation loop | 参考运营服务页构图：左侧四步闭环 + 右侧 2×2 服务模块 + 底部成果条 | `{{COL_A_*}}` `{{BULLET_*}}` `{{CARD_*}}` `{{STAT_*}}` |
| `04n_content_feature_orbit_icons.svg` | content feature orbit icons | 参考产品特点页构图：中心大圆 + 六个环绕卖点 + 线性图标，占位字段仍复用五项分点与统计字段 | `{{BULLET_01_*}}`…`{{BULLET_05_*}}` `{{STAT_03_*}}` |
| `05_ending.svg` | ending | 大号亮蓝致谢，右侧蓝色曲面 + 金线 + 插画 | `{{THANK_YOU_CN}}` `{{THANK_YOU_LINE}}` `{{TAGLINE}}` |

页面选择：有明确两方差异且每方不超过 3 点时使用 `04f`；一个中心概念向外展开 5 个要素时使用 `04g`；5 个平级工具、原则或能力项使用 `04h`；需要逐条阅读时再使用 `04c`。训战项目、陪跑服务、课程排期、督导主题、运营服务和产品卖点分别优先使用 `04i` / `04j` / `04k` / `04l` / `04m` / `04n`，避免把复杂项目方案降级成普通卡片页。

## VI. Assets

| 文件 | 状态 | 用法 |
|---|---|---|
| `logo_white.png` | active | 每页右上角知鸟品牌标 |
| `cover_illustration.png` | active | 仅封面右侧蓝色 hero 区 |
| `ending_illustration.png` | active | 仅结尾右侧蓝色 hero 区 |
| `cover_bg.jpeg` / `content_bg.jpeg` / `chapter_bg.jpeg` | legacy | 为旧项目兼容保留；新版模板不再依赖照片底图 |
| `cover_accent_bar.png` / `section_accent.png` / `chapter_band.png` / `chapter_accent_bar.png` / `chapter_illustration.png` / `ending_accent_bar.png` | legacy | 为旧项目兼容保留；新版已用可编辑 SVG 几何替代 |

## VII. Placeholder Overrides

本 deck 保留既有的平安知鸟课程语义占位词：卡片同时表达 `TITLE / META / OUTCOME`，流程页使用 `STEP_0N_*`，对比页使用 `COL_A_* / COL_B_*`，数据页使用 `STAT_0N_*`。完整词表以 frontmatter `placeholders` 为准。
