# Themes · 瑞士国际主义（Swiss Style）

9 套基于瑞士国际主义风格的**高反差配色**。**每套都遵循"高级灰白底 + 单一高饱和高亮色"的极简原则**——这是瑞士风的灵魂，**不允许混搭多个高亮色**。

---

## 使用方法（新架构）

新架构下 swiss 主题改为**外链主题 CSS**（与 editorial 一致），不再是改 inline `:root`：

1. 用户从 9 套预设选一套（或基于内容推荐）。如果用户给了明确品牌/主题色，用 `scripts/make-custom-theme.mjs` 生成 deck 专属主题。
2. 预设主题：把全部 9 套主题 css 拷进 deck 的 `css/`，并让 `theme-link` 指向具体主题文件，例如 `css/ikb-blue.css`。T 键或右上角 `T` 按钮会在当前风格内热切换这些预设：
   ```bash
   cp <SKILL_ROOT>/assets/styles/swiss/themes/*.css "$DIR/css/"
   ```
3. 明确品牌/主题色使用：
   ```bash
   node <SKILL_ROOT>/scripts/make-custom-theme.mjs swiss "#RRGGBB" "$DIR/css/theme.css" --name="brand-name"
   ```
   这会保持 Swiss 灰阶统一，只替换 `--accent` / `--accent-rgb` / `--accent-on` / `--accent-bright` / `--accent-2`。
4. 自定义主题使用 `css/theme.css` 时，初始主题可以正常显示，但 T 键会保持锁定，避免覆盖一次性自定义主题。
5. 主题 css 只覆写 accent 相关变量（`--accent`/`--accent-rgb`/`--accent-on`/`--accent-bright`/`--accent-2`）和少量 tint/语义变量，灰阶跨主题统一
6. WebGL grid shader 自动读取 `--paper-rgb`/`--ink-rgb`/`--accent`，换主题 → 网格底色 + 晕染色一起变

---

## 🔵 ikb-blue · 克莱因蓝 IKB（默认）

**适合**：通用场合、商业发布、AI / 科技产品、设计领域分享。
**调性**：纯白底 + IKB 克莱因蓝，极致冷静、理性、有学术感，像 Helvetica Forever 或 Massimo Vignelli 的作品集。
**文件**：`themes/ikb-blue.css`

```css
--accent:#002FA7;      --accent-2:#5B7BFF;
--accent-on:#ffffff;
```

**使用要点**：
- IKB 是高饱和深蓝，在大色块（如 `.accent-block`）上极有视觉冲击
- KPI 数字加 `.accent` 类用蓝色，但**不要满屏蓝**——IKB 一旦泛滥就掉档
- 推荐配合 `dark` 主题页交替使用，黑底高亮 IKB 同样高级

---

## 🟡 lemon-yellow · 柠檬黄

**适合**：年轻、运动、零售、消费品、活力主题、Y2K 复古设计。
**调性**：浅米白底 + 柠檬黄，鲜亮、有活力、警示感强，像 IKEA 或 Beck Design 的视觉语言。
**文件**：`themes/lemon-yellow.css`

```css
--accent:#C8A800;      /* 深一档柠檬黄，背景黄上能看清 */
--accent-2:#FFE800;    /* 纯柠檬黄，做高亮块用 */
--accent-on:#0a0a0a;   /* 必须黑 */
```

**使用要点**：
- 柠檬黄非常亮，accent 上的反色文字**必须黑**（`--accent-on:#0a0a0a`），不要用白
- 数据/警示页用黄色非常有效，但**全文要克制**，不要全 deck 黄

---

## 🟢 lemon-green · 柠檬绿

**适合**：环保、可持续、生态、农业、绿色能源。
**调性**：荧光浅绿 + 米白底，自然、年轻、有生命感，像环保 NGO 或可持续品牌。
**文件**：`themes/lemon-green.css`

```css
--accent:#C5E803;
--accent-on:#0a0a0a;   /* 必须黑 */
```

**使用要点**：
- `#C5E803` 是非常鲜亮的荧光绿，accent 上反色文字**必须黑**
- 与蓝色（IKB）色调对比强烈，**不混搭**

---

## 🟠 safety-orange · 安全橙

**适合**：警示、行动、风险、增长黑客、紧迫感主题。
**调性**：浅米白底 + 工业警示橙，温暖但有力，像工业 4.0 或增长黑客。
**文件**：`themes/safety-orange.css`

```css
--accent:#FF6B35;
--accent-on:#ffffff;   /* 白字勉强可读，建议 font-weight:600+ */
```

**使用要点**：
- 警示页/CTA 按钮用橙色非常有效
- 全文克制，避免"工地警示"的廉价感

---

## 🟠 hermes-orange · 爱马仕橙

**适合**：奢侈品、零售、生活方式、品牌发布、活动邀请。
**调性**：暖橙 + 高级灰白底，强品牌识别，既有行动力也有时尚感。
**文件**：`themes/hermes-orange.css`

```css
--accent:#F37021;
--accent-on:#0a0a0a;
```

**使用要点**：
- 爱马仕橙偏亮，accent 色块上必须用黑字
- 适合封面、章节页、CTA，不适合连续多页大面积铺满

---

## 🔴 bank-red · 银行红

**适合**：金融、政策、投融资、风险、增长复盘、严肃商业汇报。
**调性**：深银行红 + 灰白底，稳重、权威、带风险提示感。
**文件**：`themes/bank-red.css`

```css
--accent:#BA0C2F;
--accent-on:#ffffff;
```

**使用要点**：
- 适合关键结论、风险提示、财务节点
- 红色语义很强，避免每页都用满屏红

---

## 🟦 tiffany-blue · 蒂芙尼蓝

**适合**：消费品牌、服务体验、女性用户、清爽产品叙事、生活方式。
**调性**：亮蓝绿 + 高级灰白底，清洁、轻盈、识别度高。
**文件**：`themes/tiffany-blue.css`

```css
--accent:#0ABAB5;
--accent-on:#0a0a0a;
```

**使用要点**：
- 蒂芙尼蓝偏亮，accent 色块上必须黑字
- 适合体验旅程、用户洞察、服务产品，不适合过度严肃的风控页

---

## 🩷 valentino-pink · 华伦天奴粉

**适合**：时尚、美妆、活动发布、态度表达、强视觉冲击分享。
**调性**：高饱和粉 + 灰白底，鲜明、年轻、有舞台感。
**文件**：`themes/valentino-pink.css`

```css
--accent:#E4007F;
--accent-on:#ffffff;
```

**使用要点**：
- 适合封面和高能观点页
- 粉色冲击强，正文页建议回到纸白底，只用 accent 做强调

---

## 🟢 bottega-green · 宝缇嘉绿

**适合**：时尚、生活方式、可持续品牌、高端零售、品牌策略。
**调性**：深亮绿 + 灰白底，高级、现代、有品牌记忆点。
**文件**：`themes/bottega-green.css`

```css
--accent:#006A4E;
--accent-on:#ffffff;
```

**使用要点**：
- 适合品牌策略、视觉趋势、可持续叙事
- 与柠檬绿相比更稳重，更适合高端商业语境

---

## 内容 → 主题推荐表

| 内容类型 / 关键词 | 推荐主题 | 理由 |
|---|---|---|
| 数据 / 报表 / 季度汇报 / 方法论 / 经典瑞士 | `ikb-blue` | 克莱因蓝理性严肃，最安全默认 |
| 奢侈品 / 零售 / 生活方式 / 品牌发布 | `hermes-orange` | 爱马仕橙识别度高，时尚但有行动力 |
| 金融 / 投融资 / 风险 / 政策 / 严肃商业 | `bank-red` | 银行红权威、稳重、风险语义强 |
| 消费品牌 / 服务体验 / 女性用户 / 清爽产品 | `tiffany-blue` | 蒂芙尼蓝轻盈、清洁、识别度高 |
| 时尚 / 美妆 / 活动 / 强态度 | `valentino-pink` | 高饱和粉有强舞台感和视觉冲击 |
| 高端品牌 / 可持续 / 生活方式策略 | `bottega-green` | 宝缇嘉绿高级、稳重、有品牌记忆 |
| 警示 / 行动 / 风险 / 增长 / 紧迫 | `safety-orange` | 工业橙有行动力 |
| 环保 / 可持续 / 生态 / 农业 | `lemon-green` | 荧光绿有生命感 |
| 年轻 / 运动 / 零售 / 消费品 / Y2K | `lemon-yellow` | 柠檬黄鲜亮有活力 |

---

## 切换原则

- 首页必须是主题色第一印象页。默认用 `S01` / `SWISS-COVER-ASCII` + `slide accent`，让 `--accent` 大面积出现；无论选择预设还是自定义品牌色，第一页都不能只做灰白底小面积点缀。
- **灰阶跨主题统一**（`--paper/--ink/--grey-1/2/3` 永远不变），只换 `--accent` / `--accent-rgb` / `--accent-on` / `--accent-bright` / `--accent-2`
- 选定后可在 chrome 文案里用一个相关词强化语义：
  - IKB 配 `International / Helvetica / Swiss / Classic`
  - 爱马仕橙配 `Luxury / Retail / Lifestyle / Signal`
  - 银行红配 `Capital / Risk / Finance / Authority`
  - 蒂芙尼蓝配 `Service / Fresh / Clarity / Care`
  - 华伦天奴粉配 `Fashion / Bold / Stage / Attitude`
  - 宝缇嘉绿配 `Craft / Premium / Sustainable / Modern`
  - 柠檬黄配 `Active / Living / Bright / Bold`
  - 柠檬绿配 `Eco / Sustainable / Natural / Green`
  - 安全橙配 `Action / Alert / Growth / Fast`
- WebGL 网格背景（`webgl/grid.js`）自动读取主题变量，换主题 → 网格底色 + 晕染色一起变
- ASCII 呼吸场 canvas 不需要改（`rgba(255,255,255,...)` 在所有 accent 上都自然发亮）

## ❌ 不要做的事

- ❌ 改 `--paper / --ink / --grey-*`（灰阶跨主题统一）
- ❌ 混搭 2 套 accent（一页里同时出现 IKB 蓝 + 柠檬黄）
- ❌ 给 accent 加阴影 / 圆角 / 透明度（瑞士风纯色直角不透明）
- ❌ 把用户品牌色直接写进 HTML inline style；明确主题色必须进入 deck 专属 `theme.css`
- ❌ 一份 deck 用 2 套主题

## 加新主题（后续扩展）

新增一套长期复用的 swiss 主题**只需 3 步，不碰 shader 和 JS**：

1. 复制 `assets/styles/swiss/themes/` 下任意一个 css（如 `ikb-blue.css`）为新文件，kebab-case 命名
2. 改 `:root` 里的 accent 相关变量（`--accent`/`--accent-rgb`/`--accent-on`/`--accent-bright`/`--accent-2`）
3. 改顶部结构化注释块（适合 / 调性），在本表 + `assets/styles/registry.json` 的 `availableThemes` 各加一行

shader（`webgl/grid.js`）自动读取新主题变量，网格背景即刻适配——无需改 JS。

一次性品牌色不要登记到 skill：直接用 `scripts/make-custom-theme.mjs` 输出到目标 deck 的 `css/theme.css`。
