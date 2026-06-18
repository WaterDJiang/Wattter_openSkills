# 风格选择（Styles）

本 skill 支持多种**风格**（Style）。每种风格是独立的视觉语汇系统：字体体系 + 网格哲学 + 配色 + 装饰语汇 + 节奏感。

**当前支持 3 种风格**：

| 内部 ID | 用户展示名 | 适合内容 | 视觉锚点 |
|---|---|---|---|
| `editorial` | 杂志叙事型 | 叙事 / 观点 / 分享 / 个人风格表达 | *Monocle* / *Apartamento* / *Wallpaper\** / IDEAT 等独立杂志 |
| `swiss` | 瑞士信息型 | 事实 / 产品 / 分析 / 方法论 / 数据汇报 | Massimo Vignelli / Josef Müller-Brockmann / Helvetica Forever / Beck Design |
| `linear` | Linear 科技型 | 产品发布 / AI 工作流 / SaaS / 工程团队 / 路线图 | Linear.app 的 product system / issue board / roadmap / agent workflow |

> 选风格在选主题之前。对用户展示时使用“杂志叙事型 / 瑞士信息型 / Linear 科技型”，内部构建仍使用 `editorial` / `swiss` / `linear`。**不同风格不能混用**（字体/网格/装饰逻辑不同）。选定 style 后，只读取该 style 的 layouts / themes / components；`assets/core/` 只是低层骨架，不是可自由混搭的组件菜单。

---

## 杂志叙事型 · Editorial

**特点**：衬线中文（Noto Serif SC）+ 衬线英文（Playfair Display）+ 非衬线正文（Noto Sans SC）+ 等宽元数据（IBM Plex Mono）。WebGL `fluid` 背景（hero 页透出）。15 种布局 × 2-3 个变体。5 套配色主题。

**5 套配色主题**（色板变体，不影响风格）：

| 主题 | 主色 | 气质 | 适合 |
|---|---|---|---|
| 墨水经典 `ink-classic` | `#4A5A6E` | 墨黑+暖米，最安全默认 | 通用 / 商业 |
| 靛蓝瓷 `indigo-porcelain` | `#2F5FA8` | 深靛蓝+冷瓷白，冷静理性 | 科技 / 数据 / 研究 |
| 森林墨 `forest-ink` | `#2D6A4F` | 墨绿+暖象牙，沉稳 | 自然 / 文化 / 非虚构 |
| 牛皮纸 `kraft-paper` | `#8B5E3C` | 暖褐+米黄，年代感 | 人文 / 文学 / 怀旧 |
| 沙丘 `dune` | `#B8860B` | 炭褐+冷沙金，克制高级 | 艺术 / 设计 / 创意 |

详细色值与适配见 [`assets/styles/editorial/themes.md`](../../assets/styles/editorial/themes.md)。

**15 种布局**（每种含 2-3 个变体 A/B/C）：见 `assets/styles/editorial/layouts/` 下的 15 个 .md 文件。

**4 个预设**（主序列 + 备选序列）：见 `assets/styles/editorial/presets/` 下的 4 个 .md 文件。

---

## 瑞士信息型 · Swiss

**特点**：无衬线（Inter / Helvetica）统一字体；display 用 Inter 200/300 极细大字或 800 巨型 KPI；单一高饱和锚点色（每 deck 只用 1 个 anchor，其他都是黑灰白）；1px hairline 直角发丝线；零圆角；大量 negative space；使用极简 `grid` shader，不用 editorial 的 fluid shader 背景。

**9 套配色主题**（色板变体）：

| 主题 | 主色 | 适合 |
|---|---|---|
| 克莱因蓝 `ikb-blue` | `#002FA7` | 经典瑞士，理性、严肃 |
| 爱马仕橙 `hermes-orange` | `#F37021` | 奢侈品、零售、生活方式 |
| 银行红 `bank-red` | `#BA0C2F` | 金融、风险、严肃商业 |
| 蒂芙尼蓝 `tiffany-blue` | `#0ABAB5` | 消费品牌、服务体验 |
| 华伦天奴粉 `valentino-pink` | `#E4007F` | 时尚、美妆、活动发布 |
| 宝缇嘉绿 `bottega-green` | `#006A4E` | 高端品牌、可持续 |
| 柠檬黄 `lemon-yellow` | `#FFE800` | 年轻、运动、数据重点 |
| 柠檬绿 `lemon-green` | `#C5E803` | 环保、可持续 |
| 安全橙 `safety-orange` | `#FF4D00` | 警示、行动 |

**22 个登记版式**：见 [`assets/styles/swiss/layouts.md`](../../assets/styles/swiss/layouts.md)。正文页默认只能使用 S01-S22、S08 + Map 扩展和两个 ASCII 变体。

**当前限制**：
- 只有"静态"和"微动"两种动效模式（无 cinematic / FX）
- 每页必须有 `data-layout="Sxx"` + `data-animate="recipe-name"`

---

## Linear 科技型 · Linear

**特点**：Inter + JetBrains Mono；深色产品界面、玻璃面板、细边框、紫蓝电光、issue row、roadmap timeline、agent command。使用 WebGL `grid` 背景，支持静态 / 微动 / 沉浸。

**4 套配色主题**：

| 主题 | 主色 | 适合 |
|---|---|---|
| Linear 深紫蓝 `linear-dark` | `#5E6AD2` | 默认，最接近 Linear 式暗底产品界面 |
| 极光紫 `linear-aurora` | `#8B5CF6` | AI、agent、自动化、发布会视觉 |
| 石墨银灰 `linear-graphite` | `#94A3B8` | 严肃产品汇报、工程质量、系统架构 |
| 暗底暖金 `linear-solar` | `#F59E0B` | 增长、行动、优先级、决策节点 |

**6 个登记版式**：见 [`assets/styles/linear/layouts.md`](../../assets/styles/linear/layouts.md)。默认使用 LNR-01 至 LNR-06。

---

## 加新风格（Style C / D ...）

组件化架构的核心承诺：**加新风格 = 4 步，零侵入**。

1. 在 `assets/styles/<id>/` 建目录，放 `template.html` + `style.css` + `layouts/` + `themes/`
2. 在 `assets/styles/registry.json` 的 `styles` 数组里加一段，包含 template / style / themes / layouts / webgl / motions / validateRules
3. （可选）在 `assets/styles/<id>/validate-rules.json` 写专属校验，`scripts/validate-deck.mjs` 会按 registry 自动加载
4. 在 `references/styles/index.md` 的人类可读表格加一行

**不需要**：
- 改 `assets/core/`（任何文件）
- 改 `nav.js` / 既有 `webgl/*.js` / `fx/`
- 改现有风格的任何文件

`style.css` 通过覆写 `var(--serif-zh)`/`var(--sans-zh)`/圆角/字号等变量来定义风格——核心层一行不动，类名约定保持一致。

## 风格隔离边界

- `editorial` 只使用 `Lxx` / editorial layouts / editorial presets，不使用 Swiss 的 `Sxx`、`.canvas-card`、`.chrome-min`、`.timeline-h`、`.kpi-row-4`、`.dot-mat` 等组件。
- `swiss` 只使用登记的 `S01-S22` / `SWISS-*` / Swiss components，不使用 editorial 的 `.chrome`、`.foot`、`.quote-wall`、`.big-num`、`.body-serif`、`.rowline` 等组件。
- 新增风格必须在 `registry.json` 写 `styleIsolation.forbidLayoutPattern` 和 `styleIsolation.forbidClasses`；`validate-deck.mjs` 会据此拦截跨风格漂移。

---

## 风格选择决策表

> 用户没明确指定时，按内容/气质关键词匹配推荐。

| 用户说... | 推荐风格 | 推荐主题 |
|---|---|---|
| 故事 / 观点 / 生活方式 / 私人分享 / 哲学 | `editorial` | `kraft-paper` 或 `dune` |
| 行业分析 / 文化现象 / 行业评论 | `editorial` | `forest-ink` 或 `ink-classic` |
| AI / 数据 / 研究 / 技术 / 工程师 | `editorial` | `indigo-porcelain` |
| 不知道 / 第一次用 / 通用 / 商业发布 | `editorial` | `ink-classic` |
| 数据 / 报表 / 季度汇报 / 方法论 | `swiss` | `ikb-blue` |
| SaaS / AI 工作流 / 工程团队 / 路线图 | `linear` | `linear-dark` 或 `linear-aurora` |
| 金融 / 投融资 / 风险 / 严肃商业 | `swiss` | `bank-red` |
| 奢侈品 / 零售 / 生活方式 | `swiss` | `hermes-orange` |
| 时尚 / 美妆 / 活动 / 强态度 | `swiss` | `valentino-pink` |
| 消费品牌 / 服务体验 / 清爽产品 | `swiss` | `tiffany-blue` |
| 警示 / 行动 / 风险 / 增长 | `swiss` | `safety-orange` 或 `lemon-yellow` |
| 环保 / 可持续 / 高端生活方式 | `swiss` | `lemon-green` 或 `bottega-green` |

详细见 `SKILL.md` 的 Step 1 · 需求澄清。
