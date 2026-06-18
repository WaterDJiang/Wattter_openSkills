# 风格选择（Styles）

本 skill 支持多种**风格**（Style）。每种风格是独立的视觉语汇系统：字体体系 + 网格哲学 + 配色 + 装饰语汇 + 节奏感。

**当前支持 2 种风格**：

| 风格 ID | 名称 | 适合内容 | 视觉锚点 |
|---|---|---|---|
| `editorial` | 电子杂志 × 电子墨水 | 叙事 / 观点 / 分享 / 个人风格表达 | *Monocle* / *Apartamento* / *Wallpaper\** / IDEAT 等独立杂志 |
| `swiss` | 瑞士国际主义 | 事实 / 产品 / 分析 / 方法论 / 数据汇报 | Massimo Vignelli / Josef Müller-Brockmann / Helvetica Forever / Beck Design |

> 选风格在选主题之前。**风格 A 和风格 B 不能混用**（两者的字体/网格/装饰逻辑不同）。选定 style 后，只读取该 style 的 layouts / themes / components；`assets/core/` 只是低层骨架，不是可自由混搭的组件菜单。

---

## 风格 A · 电子杂志 × 电子墨水

**特点**：衬线中文（Noto Serif SC）+ 衬线英文（Playfair Display）+ 非衬线正文（Noto Sans SC）+ 等宽元数据（IBM Plex Mono）。WebGL `fluid` 背景（hero 页透出）。15 种布局 × 2-3 个变体。5 套配色主题。

**5 套配色主题**（色板变体，不影响风格）：

| 主题 | 气质 | 适合 |
|---|---|---|
| 🖋 ink-classic | 墨黑+暖米，最安全默认 | 通用 / 商业 |
| 🌊 indigo-porcelain | 深靛蓝+冷瓷白，冷静理性 | 科技 / 数据 / 研究 |
| 🌿 forest-ink | 墨绿+暖象牙，沉稳 | 自然 / 文化 / 非虚构 |
| 🍂 kraft-paper | 暖褐+米黄，年代感 | 人文 / 文学 / 怀旧 |
| 🌙 dune | 炭褐+冷沙金，克制高级 | 艺术 / 设计 / 创意 |

详细色值与适配见 [`assets/styles/editorial/themes.md`](../../assets/styles/editorial/themes.md)。

**15 种布局**（每种含 2-3 个变体 A/B/C）：见 `assets/styles/editorial/layouts/` 下的 15 个 .md 文件。

**4 个预设**（主序列 + 备选序列）：见 `assets/styles/editorial/presets/` 下的 4 个 .md 文件。

---

## 风格 B · 瑞士国际主义

**特点**：无衬线（Inter / Helvetica）统一字体；display 用 Inter 200/300 极细大字或 800 巨型 KPI；单一高饱和锚点色（每 deck 只用 1 个 anchor，其他都是黑灰白）；1px hairline 直角发丝线；零圆角；大量 negative space；使用极简 `grid` shader，不用 editorial 的 fluid shader 背景。

**9 套配色主题**（色板变体）：

| 主题 | 锚点色 | 适合 |
|---|---|---|
| `ikb-blue` | 国际克莱因蓝 `#002FA7` | 经典瑞士，理性、严肃 |
| `hermes-orange` | 爱马仕橙 `#F37021` | 奢侈品、零售、生活方式 |
| `bank-red` | 银行红 `#BA0C2F` | 金融、风险、严肃商业 |
| `tiffany-blue` | 蒂芙尼蓝 `#0ABAB5` | 消费品牌、服务体验 |
| `valentino-pink` | 华伦天奴粉 `#E4007F` | 时尚、美妆、活动发布 |
| `bottega-green` | 宝缇嘉绿 `#006A4E` | 高端品牌、可持续 |
| `lemon-yellow` | 柠檬黄 `#FFE800` | 年轻、运动、数据重点 |
| `lemon-green` | 柠檬绿 `#C5E803` | 环保、可持续 |
| `safety-orange` | 安全橙 `#FF4D00` | 警示、行动 |

**22 个登记版式**：见 [`assets/styles/swiss/layouts.md`](../../assets/styles/swiss/layouts.md)。正文页默认只能使用 S01-S22、S08 + Map 扩展和两个 ASCII 变体。

**当前限制**：
- 只有"静态"和"微动"两种动效模式（无 cinematic / FX）
- 每页必须有 `data-layout="Sxx"` + `data-animate="recipe-name"`

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
| 金融 / 投融资 / 风险 / 严肃商业 | `swiss` | `bank-red` |
| 奢侈品 / 零售 / 生活方式 | `swiss` | `hermes-orange` |
| 时尚 / 美妆 / 活动 / 强态度 | `swiss` | `valentino-pink` |
| 消费品牌 / 服务体验 / 清爽产品 | `swiss` | `tiffany-blue` |
| 警示 / 行动 / 风险 / 增长 | `swiss` | `safety-orange` 或 `lemon-yellow` |
| 环保 / 可持续 / 高端生活方式 | `swiss` | `lemon-green` 或 `bottega-green` |

详细见 `SKILL.md` 的 Step 1 · 需求澄清。
