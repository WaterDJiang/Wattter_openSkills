# wtt-magazine-deck 模板扩展规范

本文档只约束新增模板和新增风格的维护方式。运行 skill 生成 deck 时，以 `SKILL.md` 和相关 `references/` 为准。

## 模板定义

这里的模板指 `assets/styles/<style-id>/` 下的一套可复用风格，不是某一次生成出来的 deck 成品。

新增模板必须能在不改共享核心层的前提下接入现有构建流程：

- 共享骨架：`assets/core/`
- 共享动效：`assets/motions/`
- 共享 WebGL：`assets/webgl/`
- 风格自包含层：`assets/styles/<style-id>/`

## 目录契约

新增 `assets/styles/<style-id>/` 时，至少包含：

- `template.html`：该风格的 HTML 模板。
- `style.css`：该风格的字体、栅格、版式语汇和组件视觉。
- `themes/`：该风格的主题 CSS 文件。
- `themes.md`：主题名称、适用场景、色彩变量和禁用规则。
- `validate-rules.json`：该风格的机器校验规则。
- 版式文档：可以是 `layouts.md`，也可以是 `layouts/` 目录。

按需添加：

- `components/`：只放该风格独有组件。
- `recipes.js`：只放该风格独有的入场动画编排。
- `presets/`：只放该风格常用页面序列。

## 快速创建新风格

从模板目录复制一份，然后替换 `STYLE_ID` / `STYLE_NAME`：

```bash
STYLE_ID="new-style"
STYLE_NAME="新风格名称"
cp -R assets/styles/_template "assets/styles/$STYLE_ID"
rg -l "STYLE_ID|STYLE_NAME" "assets/styles/$STYLE_ID" | xargs perl -pi -e "s/STYLE_ID/${STYLE_ID}/g; s/STYLE_NAME/${STYLE_NAME}/g"
```

复制后至少要改这些文件：

- `template.html`：替换 `<body data-style>`、字体链接、`theme-link` 默认主题、`data-theme-list`。
- `style.css`：定义字体、字号、栅格、圆角、深浅页、accent 页和该风格核心视觉语汇。
- `themes/default.css`：替换真实 `--ink`、`--paper`、`--accent` 等主题变量。
- `themes.md`：写清主题适用场景、禁用规则、T 键切换准备方式。
- `layouts.md`：登记至少封面和正文两种版式，使用该风格自己的 layout ID。
- `validate-rules.json`：登记 allowed layouts 和风格专属硬规则。
- `registry-entry.template.json`：复制其中对象到 `assets/styles/registry.json` 的 `styles` 数组。
- `components/`：放该风格独有组件 CSS；不需要专属组件时保留 README 即可。
- `recipes.js`：只有该风格需要专属 `data-animate` 编排时才启用。

新增风格后还要更新：

- `assets/styles/registry.json`：新增 style 条目、主题列表、文件路径、webgl/motions、`styleIsolation`。
- `references/styles/index.md`：新增人类可读说明和选择建议。
- `node scripts/validate-theme-contract.mjs`：新增或修改主题、模板、T 按钮、主题列表后必须通过这条跨风格契约检查。

## 新风格必须提供的组件能力

每个新风格不是只换颜色，必须提供一套完整且可验证的视觉系统：

- **模板组件**：`template.html` 必须加载 `base.css`、`style.css`、具体主题 CSS、`nav.js`、`fit.js`，并保留五个占位符。
- **主题组件**：至少 1 个主题 CSS；支持 T 键时提供 2 个以上预设主题，并在 `body[data-theme-list]` 登记。
- **版式组件**：至少 2 个 layout（封面 + 正文），每个 layout 有稳定 ID、用途、关键 class、动效和溢出处理。
- **可读性组件**：`style.css` 必须定义 `.slide.light`、`.slide.dark`、`.slide.accent` 的背景、文字、meta、边框可读性。
- **内容适配组件**：长标题使用 `.fit-safe-text`；高密度主体使用 `.fit-shell` 或明确要求拆页。
- **导航组件**：必须保留 `#nav`、`#nav-btns`、`#btn-prev`、`#btn-next`，可改视觉但不能移除。
- **隔离组件**：在 `registry.json` 写 `styleIsolation.forbidLayoutPattern` 和 `styleIsolation.forbidClasses`，禁止其他风格 layout/class 混入。
- **校验组件**：`validate-rules.json` 至少检查 layout allowlist 和首页主题信号。

### 最小组件矩阵

| 组件 | 必需文件 | 最低要求 | 常见遗漏 |
|---|---|---|---|
| 模板 | `template.html` | 加载 `base.css`、`style.css`、当前主题、`nav.js`、`fit.js`，保留全部占位符和 `#btn-theme` | 漏掉左右按钮或 T 键主题列表 |
| 主题 | `themes/default.css`、`themes.md` | 定义完整 CSS 变量和 `--accent-on`，并让首页能显著呈现 `--accent` | 只改颜色但首页仍像旧主题 |
| 版式 | `layouts.md` 或 `layouts/` | 至少封面 + 正文两种 layout，全部有稳定 `data-layout` | 复用其他风格的 `Sxx` / `Lxx` |
| 组件 | `style.css`、`components/*.css` | 只放本风格专属组件，命名不要泛化成 `.card` / `.item` | 把风格组件塞进 `assets/core/` |
| 适配 | `style.css`、`fit.js` | 长标题用 `.fit-safe-text`，密集内容用 `.fit-shell` 或拆页 | 页面无法整页显示 |
| 校验 | `validate-rules.json` | 检查 layout allowlist、首页主题信号、风格禁用项 | 只写文档不让脚本拦截 |
| 注册 | `registry-entry.template.json`、`registry.json` | 登记文件路径、主题列表、动效、WebGL、隔离规则 | 忘记注册导致构建/校验找不到风格 |

## 注册要求

新增模板后必须同步更新：

- `assets/styles/registry.json`
- `references/styles/index.md`

`registry.json` 是机器可读权威来源。新增字段要能支持校验脚本和构建流程读取，不要只写自然语言说明。

`assets/styles/_template/registry-entry.template.json` 是注册条目模板。复制其中对象到 `assets/styles/registry.json` 的 `styles` 数组后，必须检查：

- `id` 与 `<body data-style>`、目录名完全一致。
- `files.*` 指向真实存在的文件。
- `defaultTheme` 出现在 `availableThemes` 里，且对应 `themes/<theme>.css` 存在。
- `template.html` 的 `data-theme-list` 与 `availableThemes` 完全一致，`theme-link` 指向 `defaultTheme`。
- `styleIsolation` 写清禁止混入的其他风格 layout/class；没有禁用项时也要显式写空数组，避免边界不明。
- `webgl` 只能使用已有共享 shader，除非同时新增并登记 `assets/webgl/<shader>.js`。
- 运行 `node scripts/validate-theme-contract.mjs`，让脚本统一检查 registry、模板、主题 CSS、T 按钮和 `--accent` / `--accent-on` 对比度。

## template.html 要求

模板必须保留以下占位符：

- `{{MOTION_CSS}}`
- `{{LAYOUT_SECTIONS}}`
- `{{WEBGL_JS}}`
- `{{MOTION_JS}}`
- `{{FX_JS}}`
- `[必填]` 标题占位

模板必须包含通用翻页入口：

- `#nav`
- `#nav-btns`
- `#btn-prev`
- `#btn-next`

可以调整按钮视觉强弱，但不能移除按钮，也不能只依赖键盘、滚轮或 dots 翻页。

模板还必须暴露可读的深浅主题契约。深色页、浅色页、accent 色块不要依赖生成任务临时写内联 `color`，要在风格 CSS 里定义好对应 class 的背景色、文字色、meta 色和边框色。

## 主题规范

不要让生成任务在 HTML 里直接散写 hex 色值。主题色必须沉淀为 `themes/<theme>.css` 或一次性 deck 专属 `css/theme.css`，并通过 CSS 变量暴露给 `style.css` 和组件使用。

主题 CSS 必须提供可检查的 `--accent` 与 `--accent-on`，两者对比度至少 4.5:1。不要为某个模板临时写反色规则；亮色/深色主题都必须通过主题变量和共享组件规则解决。

每个主题文档至少说明：

- 主题 ID 和显示名称。
- 适合的内容场景。
- 关键 CSS 变量。
- 禁止和其他主题混用的规则。

如果模板支持键盘热切换主题，必须在主题文档里写清初始化拷贝命令，并保证构建契约会把全部可切换主题 CSS 放到 deck 的 `css/` 目录。

如果用户提供明确品牌/主题色，模板必须提供生成 deck 专属主题的流程；长期复用主题才登记到 `assets/styles/<style-id>/themes/` 和 `registry.json`。

模板必须包含内容适配策略：模板脚本加载 `js/fit.js`；Editorial 主内容使用 `.frame`，Swiss 以 `.canvas-card` 作为安全框并在高密度主体内包 `.fit-shell`；长标题使用 `.fit-safe-text` 或拆页，避免生成结果在 16:9 视口内上下漂移。

## 版式规范

新增版式前先判断是否属于既有风格的变体。只有当它引入稳定、可复用、可校验的新结构时，才新增版式。

新增版式必须写清：

- 版式 ID。
- 适用页面类型。
- 必需 class 和 data 属性。
- 图片槽位和比例约束。
- 推荐动效。
- 禁止使用场景。
- 中文、长标签、长数字等容易溢出的替代 class。

Swiss 风格的正文页必须继续使用登记的 `Sxx` 版式编号；实验版式需要在校验规则里显式区分。

## 修改边界

新增模板时默认不要修改：

- `assets/core/`
- 既有 `assets/styles/<existing-style>/`
- 既有 `assets/webgl/*.js`
- 既有 `assets/motions/*.js`

只有共享契约确实变化时，才改共享层。改共享层时必须同步验证所有已登记风格。

`assets/core/` 只允许放低层结构能力：slide 容器、通用 grid、图片槽位、导航、字体变量占位、内容适配。不要把某个风格的审美组件放进 core。凡是带明确风格指纹的组件都必须放入 `assets/styles/<style-id>/components/` 或该风格的 `style.css`，例如：

- Editorial 专属：`.quote-wall`、`.big-num`、`.body-serif`、`.rowline`、`.plat`。
- Swiss 专属：`.canvas-card` 的具体用法、`.timeline-h`、`.timeline-v`、`.kpi-row-4`、`.dot-mat`、`.accent-block`、`.stacked-ledger`、`.duo-compare`。

生成后的 deck 必须只有一种风格的版式系统。`editorial` 不允许混入 `Sxx`/Swiss-only class；`swiss` 不允许混入 `Lxx`/Editorial-only class。这个边界由 `scripts/validate-deck.mjs` 负责拦截。

## 校验清单

提交新增模板前至少运行：

```bash
python3 /Users/water/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
node --check scripts/validate-deck.mjs
node --check scripts/validate-swiss-deck.mjs
node scripts/validate-deck.mjs <deck>/index.html <style-id>
git diff --check
```

如果新增或修改 Swiss 模板，还要运行：

```bash
node scripts/validate-swiss-deck.mjs <deck>/index.html
```

实际 deck 还要浏览器人工检查：左右按钮、键盘方向键、滚轮/触摸翻页、dots、图片渲染、标题替换、无 `{{...}}` 占位符残留。

## 新增模板提交流程

1. 创建 `assets/styles/<style-id>/` 并补齐目录契约。
2. 更新 `assets/styles/registry.json`。
3. 更新 `references/styles/index.md`。
4. 补充主题、版式和校验规则文档。
5. 用最小示例 deck 跑统一校验。
6. 如改到共享层，补跑所有已登记风格的校验。
