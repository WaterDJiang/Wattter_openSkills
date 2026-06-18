---
name: wtt-magazine-deck
description: 当用户需要制作自包含横向翻页网页演示文稿、杂志风 PPT、瑞士风 PPT、发布会/分享/报告型网页 slides，或提到 magazine deck、Swiss style、horizontal swipe deck、editorial magazine、e-ink presentation 时使用。适用于从主题、大纲、素材或旧文档生成可本地打开的 HTML deck。
---

# 杂志风网页演示

生成一份**自包含文件夹**的横向翻页网页演示文稿。当前支持三种组件化风格：

- `editorial`：电子杂志 × 电子墨水。适合叙事、观点、分享、个人风格表达；衬线标题、WebGL `fluid`、5 套主题、15 种布局和 4 个预设。
- `swiss`：瑞士国际主义。适合事实、产品、分析、方法论、数据汇报；Inter 极细字重、1px 发丝线、单一高饱和锚点色、WebGL `grid`、9 套主题、22 个登记版式 S01-S22。
- `linear`：Linear 科技型。适合产品发布、AI 工作流、SaaS、工程团队、路线图和任务系统；深色产品界面、玻璃面板、issue/roadmap/agent 组件、WebGL `grid`、4 套主题、6 个登记版式 LNR-01-LNR-06。

**风格不能混用。** 先选 style，再选 theme、motion、layout/preset。

## 何时使用

适合：线下分享、行业内部讲话、发布会、demo day、数据报告、作品展廊、强个人风格演讲。

不适合：大段表格、复杂图表堆叠、培训课件、需要多人协作编辑的 PPT。

## 入口流程

1. **Brief Gate（生成前确认）。** 先读 `references/brief-gate.md`。如果用户没有明确给出内容组织、风格、颜色主题、模板/预设、动效模式，必须给选项卡让用户确认；如果用户给了完整大纲，也要先复述拟采用配置并等确认，除非用户明确说“直接生成 / 你决定 / 不用确认”。对用户展示风格时用“杂志叙事型 / 瑞士信息型 / Linear 科技型”这类中文名称，内部 id `editorial` / `swiss` / `linear` 只作为括号补充；颜色选项必须带主题色号和适用判断。
2. **确认输入完整度。** 确认受众场景、分享时长、原始素材、图片、主题色、硬约束是否足够决定页数和节奏；缺失项并入 Brief Gate 一次问完，不要边做边反复追问。
3. **选风格。** 读 `references/styles/index.md`。拿不准时默认 `editorial`；内容偏事实、产品、分析、方法论、数据汇报时优先 `swiss`。
4. **选引用资料。** 先读 `references/required-components.md`，把页面表达收敛到 6 个必须组件，再按风格读取对应 layout/theme。
   - `editorial`：读 `references/themes.md`、`references/presets.md`、`references/layouts.md`；细节组件读 `references/components.md`。
   - `swiss`：读 `references/swiss-layout-lock.md`、`assets/styles/swiss/layouts.md`、`assets/styles/swiss/themes.md`；地图页读 `references/swiss-map-component.md`。
   - `linear`：读 `assets/styles/linear/layouts.md`、`assets/styles/linear/themes.md`；适合产品 UI、issue board、roadmap、agent command 结构。
   - 动效细节读 `references/motions.md`；最终自检读 `references/checklist.md`。
5. **生成 deck 文件夹。** 输出目录必须命名为 `<YYYYMMDDHHmm>_<内容主题>_<模板主题色动效>`，例如 `202606181530_AI课程合作介绍_瑞士克莱因蓝电影`；目录内结构必须是可直接打开的静态文件夹：`index.html`、`css/`、`js/`、`images/`。
6. **运行校验。** 生成后必须先跑 `node scripts/validate-theme-contract.mjs`，再跑 `node scripts/validate-deck.mjs <index.html> <style-id>`；Swiss 额外跑 `node scripts/validate-swiss-deck.mjs <index.html>`。

## 构建契约

按 `assets/styles/registry.json` 作为机器可读权威来源，不要在脑中硬编码路径。当前构建顺序：

```bash
TOPIC="AI课程合作介绍"   # 用 deck 内容主题，不要用 generic deck / slides / output
STAMP="$(date +%Y%m%d%H%M)"
SAFE_TOPIC="$(printf '%s' "$TOPIC" | tr ' /\\:：' '-----')"
STYLE_LABEL="瑞士"       # 杂志 / 瑞士 / Linear
THEME_LABEL="克莱因蓝"   # 如：墨水经典、克莱因蓝、Linear深紫蓝
MOTION_LABEL="电影"      # 静态 / 微动 / 电影
CONFIG_LABEL="${STYLE_LABEL}${THEME_LABEL}${MOTION_LABEL}"
DIR="项目/XXX/${STAMP}_${SAFE_TOPIC}_${CONFIG_LABEL}"
mkdir -p "$DIR"/{css,js/fx,images}

cat <SKILL_ROOT>/assets/core/{tokens,slide,typography,layout,components,image,chrome,nav,responsive}.css > "$DIR/css/base.css"
cp <SKILL_ROOT>/assets/core/nav.js "$DIR/js/"
cp <SKILL_ROOT>/assets/core/fit.js "$DIR/js/"

# 风格层
cp <SKILL_ROOT>/assets/styles/<style-id>/style.css "$DIR/css/style.css"
cp <SKILL_ROOT>/assets/styles/<style-id>/themes/*.css "$DIR/css/"
# 预设主题：让 theme-link 指向具体主题文件（如 css/ikb-blue.css），T 键才能在当前风格内切换主题。
# 用户提供明确品牌/主题色时，改用 deck 专属主题，不要在 HTML 里散写颜色：
# node <SKILL_ROOT>/scripts/make-custom-theme.mjs <style-id> "#RRGGBB" "$DIR/css/theme.css" --name="brand-name"
# 自定义主题：让 theme-link 指向 css/theme.css；T 键会锁定，避免覆盖用户品牌色。

# swiss 专用
mkdir -p "$DIR/css/swiss"
cp <SKILL_ROOT>/assets/styles/swiss/components/*.css "$DIR/css/swiss/"
cp <SKILL_ROOT>/assets/styles/swiss/recipes.js "$DIR/js/recipes.js"

# 动效
cp <SKILL_ROOT>/assets/motions/animations.css "$DIR/css/"        # 仅 subtle/cinematic
cp <SKILL_ROOT>/assets/motions/subtle.js "$DIR/js/motion.js"     # subtle
cp <SKILL_ROOT>/assets/motions/cinematic.js "$DIR/js/motion.js"  # cinematic

# WebGL
cp <SKILL_ROOT>/assets/webgl/fluid.js "$DIR/js/webgl.js"  # editorial
cp <SKILL_ROOT>/assets/webgl/grid.js "$DIR/js/webgl.js"   # swiss / linear

# cinematic 特效
cp <SKILL_ROOT>/assets/fx/*.js "$DIR/js/fx/"
```

使用选定风格的模板：

- `assets/styles/editorial/template.html`
- `assets/styles/swiss/template.html`
- `assets/styles/linear/template.html`

替换 `{{MOTION_CSS}}`、`{{LAYOUT_SECTIONS}}`、`{{WEBGL_JS}}`、`{{MOTION_JS}}`、`{{FX_JS}}`，再替换 `[必填]` 标题。

## 硬性规则

- 每份 deck 都必须包含可见翻页导航：`#nav`、`#nav-btns`、`#btn-prev`、`#btn-next`；Swiss 可以弱化按钮视觉，但不能移除按钮。
- 未经 Brief Gate 确认，不要开始生成 deck。用户只给主题或模糊方向时，必须先让用户在内容组织、风格、颜色、模板/预设、动效中确认或选择“按推荐生成”。
- 输出目录必须使用最终确认的内容主题、模板、主题色和动效命名，并以生成时间开头：`YYYYMMDDHHmm_内容主题_模板主题色动效`，例如 `202606181530_AI课程合作介绍_瑞士克莱因蓝电影`。不要再使用 `_Mdeck`，也不要输出到 `deck`、`dist`、`output`、`slides` 这类泛目录。
- 首页是主题色和风格方案的第一印象页：Swiss 首页必须用 `S01` 或 `SWISS-COVER-ASCII`，并用 `slide accent` 让所选主题色成为主视觉；Editorial 首页必须用 `hero dark/light` 并让主题的 WebGL/主色可见。
- 每页都必须有清晰视觉节奏。Editorial 写 section 前先规划 `hero dark` / `hero light` / `light` / `dark`；避免连续 3 页使用相同主题。
- 每页必须能整页显示。长标题加 `.fit-safe-text`；Editorial 主体用 `.frame`，Swiss 高密度主体在 `.canvas-card` 内包 `.fit-shell`。生成后观察是否出现 `内容过密` 标记，出现就删减文字、拆页或换低密度版式。
- T 键只切换当前风格内的主题色，不切换 `editorial`/`swiss` 风格；要换风格必须重新按目标 style 生成 deck。
- 不要发明 layout class。使用 `base.css` 的核心 class 和引用文件里的风格专属版式。
- 不要混用风格系统。Editorial 版式和 Swiss Sxx 版式有不同的字体、栅格、图片和动效契约。
- 选定风格后整份 deck 只使用该风格的模板、layout、components 和 theme；`scripts/validate-deck.mjs` 会拦截跨风格 class/layout 混入。
- 组件库做减法：新 deck 的内容表达先归入 `title-block`、`figure-frame`、`metric-block`、`comparison-block`、`sequence-block`、`evidence-strip` 六类。`decision-matrix`、`risk-register`、`screenshot-callout`、`roadmap-lanes`、`action-checklist` 等只能作为这六类的变体，不新增顶层组件。
- 主题色优先使用风格预设；如果用户给出明确品牌色/主题色，用 `scripts/make-custom-theme.mjs` 生成 deck 专属 `theme.css`，不要在 HTML 里散写 hex。
- 主题、T 按钮、`data-theme-list`、`--accent-on` 对比度都属于共享主题契约；新增或修改主题时先更新 `registry.json` 和主题 CSS，再跑 `scripts/validate-theme-contract.mjs`，不要只补某个模板。
- 文字颜色必须跟随所在底色 surface，而不是靠页面整体深浅猜测。局部深色底、底部压暗区、图片遮罩文字必须加 `.on-dark` / `.surface-dark` / `data-surface="dark"`；局部浅色底加 `.on-light`；主题色底加 `.on-accent`。图片或渐变上叠文字优先用 `.readable-zone.on-dark` / `.readable-zone.on-light`，不要单独写 `color:var(--ink)` 或 `color:var(--paper)`。
- 使用 Lucide 图标，不要使用 emoji。
- 图片放入 `images/`，使用 `01-cover.jpg` 这类稳定命名；文件名保持稳定，替换图片时不需要改 HTML。
- 微动/沉浸模式下，每页至少有一个 `data-anim`；Swiss section 还必须包含 `data-layout="Sxx"` 和 `data-animate="recipe-name"`。
- 不要用内联 `color:var(--paper)` 或 `color:var(--ink)` 硬改整页文字；跨模板可读性由 `assets/core/slide.css` 的 surface contract 和 `scripts/validate-deck.mjs` 检查。

## 扩展规则

新增长期复用主题时，在 `assets/styles/<style-id>/themes/` 下添加 CSS 文件，更新该风格的主题文档；必要时更新风格注册信息。一次性品牌色只生成 deck 内 `css/theme.css`，不要登记进 skill。

新增风格时，创建 `assets/styles/<id>/`，包含 `template.html`、`style.css`、`themes/`、版式文档、可选的 components/recipes，以及 `validate-rules.json`；随后登记到 `assets/styles/registry.json` 和 `references/styles/index.md`。除非共享契约变化，不要修改 `assets/core/`、既有风格或既有 WebGL 模块。

## 验证

Run these before delivery:

```bash
node scripts/validate-theme-contract.mjs
node scripts/validate-deck.mjs <deck>/index.html <style-id>
node scripts/validate-swiss-deck.mjs <deck>/index.html   # 仅 swiss
node --check scripts/validate-theme-contract.mjs
node --check scripts/validate-deck.mjs
node --check scripts/validate-swiss-deck.mjs
git diff --check
```

真实生成 deck 时，还要在浏览器打开 `index.html` 验证：左右翻页按钮、键盘方向键、滚轮/触摸导航、分页 dots、图片渲染、标题替换，以及没有残留 `{{...}}` 占位符。
