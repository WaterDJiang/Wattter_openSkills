# 质量检查清单（Checklist）

这个清单来自真实分享 PPT 的迭代过程。每一条都是踩过坑之后总结的，按重要性排序。

生成 PPT 前，先通读一遍；生成后，逐项自检。

---

## 🔴 P0 · 一定不能犯的错

### 0. 生成前必须通过的类名校验(最重要)

**现象**：直接把 layouts.md 的骨架粘到新 HTML,结果样式全部丢失——大标题变成非衬线、数据大字报字体小得像正文、pipeline 多页糊成一坨、图片堆到浏览器底部。

**根因**：如果 `css/base.css` 里没有这些类的定义,浏览器就 fallback 到默认样式。

**做法**：
- **生成 PPT 前,必须先 `Read` `css/base.css`**,确认 layouts.md 里用到的类都已定义
- 最常见遗漏的类:`title-block / title-heading / figure-frame / figure-media / metric-block / metric-value / comparison-block / comparison-item / sequence-block / sequence-step / evidence-strip / h-hero / h-xl / h-sub / h-md / lead / meta-row / stat-card / stat-label / stat-nb / stat-unit / stat-note / pipeline-section / pipeline-label / pipeline / step / step-nb / step-title / step-desc / grid-2-7-5 / grid-2-6-6 / grid-2-8-4 / grid-2-5-7 / grid-2-4-8 / grid-3-3 / grid-6 / grid-4 / grid-3 / frame / img-cap / callout-src / timeline / tl-node / tl-year / tl-title / tl-desc / quote-wall / qw-item / qw-text / qw-cite / pillar / big-num / mid-num / bottom-left / bottom-right / rule`
- 如果某个类确实缺了,**在 `base.css` 末尾补上**,不要在每页 inline 重写
- 生成后打开浏览器,如果看到"大标题是非衬线"或"pipeline 步骤挤在一行",几乎 100% 是这个问题

### 1. 不要用 emoji 作图标

**现象**：在中式杂志风格里用 emoji 会立刻破坏格调。

**做法**：用 Lucide 图标库，CDN 方式引用：

```html
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
...
<i data-lucide="target" class="ico-md"></i>
...
<script>lucide.createIcons();</script>
```

常用图标名：`target / palette / search-check / compass / share-2 / crown / check-circle / x-circle / plus / arrow-right / grid-2x2 / network`

### 2. 图片只允许裁底部，左右和顶部绝对不能切

**现象**：用 `aspect-ratio` 撑图，网格会在父容器不足时堆叠或切掉图片关键信息（比如截图上部的标题栏）。

**做法**：图片容器用**固定 height + overflow hidden**，图片走 `object-fit:cover + object-position:top`：

```html
<figure class="frame-img" style="height:26vh">
  <img src="screenshot.png">
</figure>
```

CSS 里 `.frame-img img` 已经预设 `object-position:top`，只裁底。

**绝不用这种写法**（会在网格中撑破容器）：

```html
<!-- 坏例 -->
<figure class="frame-img" style="aspect-ratio: 16/9">...</figure>
```

**例外**：单张主视觉（非网格内）可以用 `aspect-ratio + max-height`，因为父容器会兜底。

### 2b. 亮页面配暗 WebGL = 灰蒙蒙(主题切换没生效)

**现象**:所有 light 页面背景都像蒙了一层灰,甚至 hero light 也灰。

**根因**:JS 根据 slide 的主题切换两张 canvas 的 opacity。如果 slide 必须明确带 `light` 或 `dark` 类。

**做法**:
- slide 必须明确带 `light` 或 `dark` 类。不要漏写,更不要用其他自定义主题名
- hero 页用 `hero light` / `hero dark`,正文页用 `light` / `dark`。只写 `hero` 不带主题色是坏的
- 一个 deck 里必须至少有一个 **非 hero 的 light 页**,确保 body 有机会加 `light-bg`

### 2b-2. 整个 deck 全是 light,没有节奏

**现象**:除封面 `hero dark` 外,其余所有页面默认写 `light`——视觉平淡,没有呼吸感。

**做法**:
- **生成前画"主题节奏表"**:每一页写清 `hero dark` / `hero light` / `light` / `dark`
- **硬规则**:连续 3 页以上同主题 = 不允许;6 页以上必须有 ≥1 `hero dark` + ≥1 `hero light`;不能全是 `light` 正文页
- **生成后自检**:`grep 'class="slide' index.html`,目视确认节奏有交错

### 2c. chrome 和 kicker 不要写同一句话

**做法**:
- chrome = 杂志页眉 / 导航标签（跨多页可相同）
- kicker = 本页独一份的引导句（短、有钩子）
- 一个描述栏目,一个描述这一页——绝不互相翻译

### 3. 大标题字号不能超过屏宽 / 单字数

**做法**：
- `h-hero`（最大）：10vw，**且标题长度 ≤ 5 字**
- `h-xl`（次大）：6vw-7vw
- 长标题用 `<br>` 手工断行
- 必要时加 `white-space:nowrap`

### 4. 字体分工：标题衬线、正文非衬线

**做法**：
- 大标题、重点 quote、数字大字 → **衬线字体**
- 正文、描述、pipeline 步骤名 → **非衬线字体**
- 元数据、代码、标签 → **等宽字体**

### 4b. 图片不要用 `align-self:end` 贴底

**做法**:
- 图文混排**必须用 `.frame.grid-2-7-5`**（或 `.grid-2-6-6`/`.grid-2-8-4`）
- 右列图片保持贴顶，要左列"贴底"效果用 flex column + `justify-content:space-between`

### 4c. 图片不要用原图奇葩比例

**做法**:固定用标准比例 **16/10 / 4/3 / 3/2 / 1:1 / 16/9**。

### 5. 不要给图片加厚边框 / 阴影

**做法**：最多 1-4px 的微圆角。不要加 `box-shadow`。

---

## 🟡 P1 · 排版节奏

### 6. Hero 页和非 hero 页要交替

**推荐节奏**：
- 5-8 页：1 个 hero 封面 + 1-2 个正文 dark 页 + 收束
- 10-15 页：封面 hero + 每 3-4 页插 1 个 hero + 收束
- 20+ 页：多幕结构，每幕开头是 hero 幕封

### 7. 大字报页和密集页要交替

### 8. 同一概念的英文/中文用法要统一

### 9. 底部 chrome 的页码要一致

用 `XX / 总页数` 格式。加页/删页时要手工改 N。

### 9b. 版式不得雷同（变体变换 · 核心）

**现象**：整本 deck 正文页都是"左字右图 7:5"、数据页都是"3×2 网格"、金句页都是"居中"——一眼就是模板套出来的，没有呼吸。

**根因**：layouts.md 每种布局虽然只有一种默认变体 A，但都提供了 2-3 个构图变体（A/B/C）。只用默认变体 = 版式固定。

**做法**：
- **同布局重复必须换变体**：Layout 4 出现两次 → 第二次用 B 或 C，不允许两页都 A。轮换速查见 `presets.md`。
- **相邻两页构图不得相同**：grid 比例 / 方向 / 结构至少一项不同。
- **grid 比例有意混用**：不要全 deck `grid-2-7-5`，7:5 / 5:7 / 8:4 / 6:6 / 3 栏穿插。
- **等分类不连用**：3-A 与 3-B、5-A 与 5-B 不相邻。
- **全幅叠加克制**：4-C / 10-C 合计 ≤ 2 个。
- **生成后自检**：`grep -oE 'grid-2-[0-9]+-[0-9]+|grid-[0-9]+' index.html | sort | uniq -c` 看比例是否混用；目视逐页确认无两页构图雷同。

详见 `layouts.md` 文末「变体变换规则」与 `presets.md` 的「如何避免雷同」。

---

## 🟡 P1.5 · 动效（微动 / 沉浸模式）

### 10. 每个 slide 至少有一个 data-anim

**做法**：
- Hero 页：`data-anim="spotlight"` 或 `data-anim="ripple-reveal"` 加在 `<section>` 上
- 正文页：`data-anim="fade-up"` 加在主要文字容器上
- 列表/网格：`data-anim="stagger-list"` 加在容器上
- 如果不确定加什么，`data-anim="fade-up"` 是最安全的默认

**Swiss 额外规则**：每个 `<section>` 必须写 `data-animate="recipe-name"`，recipe 名来自 `assets/styles/swiss/layouts.md` 登记的 22 个名称。`data-anim` 控制元素 reveal，`data-animate` 控制整页 recipe，两者不是同一个字段。

### 11. counter-up 要配 stat-nb

```html
<span class="stat-nb counter" data-to="128">0</span>
```

`data-to` 值必须是数字，`counter` 类和 `data-to` 缺一不可。

### 12. 沉浸模式 FX 容器内容要 z-index:1

FX 的 canvas 插入为容器第一个子元素（z-index:0），容器内的文字/图片需要 `style="z-index:1"` 或 `position:relative` 才能在 canvas 之上。

### 13. 沉浸模式只选 1-2 个 FX，不要堆砌

克制优于炫技。一个 deck 最多用 2 种不同的 FX。

---

## 🟢 P2 · 视觉打磨

### 14. WebGL 背景的遮罩透明度

- dark hero：遮罩 12-15%
- light hero：遮罩 16-20%
- 普通页：遮罩 92-95%

### 15. Light hero 的 shader 不能有强中心点

### 16. Dark hero 允许更多视觉冲击

### 17. 左文右图的对齐

网格整体 `align-items:start`，左列 `justify-content:space-between`。

### 18. 图片的微弱圆角

`border-radius:4px`，不要超过 8px。

---

## 🔵 P3 · 操作细节

### 19. 图片路径用相对路径

图片放在 `images/` 文件夹下。

### 20. 页码在 `.chrome` 里写死

### 21. 翻页导航要保留

不要删 nav.js 里的导航逻辑。

所有风格都必须保留可见左右翻页按钮：
- HTML 必须有 `#nav-btns`
- 按钮必须是 `#btn-prev` / `#btn-next`
- 即使是 Swiss 极简风，也只能弱化视觉，不能移除按钮

### 22. 不要用 `height:100vh` 硬设，用 `min-height:80vh`

### 23. 静态模式不要加载 WebGL 和动效文件

静态模式只保留 `base.css` + `style.css` + `theme.css` + `nav.js`（Swiss 还保留 `css/swiss/*.css`），删除 canvas 元素和 `js/webgl.js` / animations.css / motion.js 引用。

### 24. template 占位符必须全部处理

**做法**：生成 index.html 后，grep `{{` 确认没有残留的占位符：
- `{{MOTION_CSS}}` → 替换为 `<link>` 或删除
- `{{LAYOUT_SECTIONS}}` → 替换为实际 `<section>` 代码
- `{{WEBGL_JS}}` → 替换为 `<script>` 或删除
- `{{MOTION_JS}}` → 替换为 `<script>` 或删除
- `{{FX_JS}}` → 替换为 `<script>` 或删除

---

## 🧪 最终自检清单

```
预检(生成前)
  □ 已读过 css/base.css，确认所需类都存在
  □ 已读过 references/required-components.md，页面表达已收敛到 6 个必须组件，不新增一次性顶层组件
  □ 已选定主题色（5 选 1）
  □ 已选定动效模式（静态/微动/沉浸）
  □ 已选定预设方案或自定义布局序列
  □ 已决定每页用哪个 Layout(1-15) + 变体(A/B/C)
  □ 已画出"主题节奏表"
  □ 节奏表满足硬规则

template 组装
  □ 已完成 Brief Gate：内容组织 / 风格 / 颜色主题 / 模板预设或页面结构 / 动效模式均已确认
  □ index.html 由选定风格的 template.html + style.css + theme.css + 动效模式 + 布局序列组装生成
  □ template 中所有 {{占位符}} 已替换或删除（grep "{{" 应无结果）
  □ `<title>` 已改为实际 deck 标题(grep "[必填]" 应无结果)

文件结构
  □ deck 父目录命名符合 `YYYYMMDDHHmm_内容主题_模板主题色动效`，例如 `202606181530_AI课程合作介绍_瑞士克莱因蓝电影`
  □ css/base.css 存在且完整
  □ css/theme.css 是选定的主题
  □ 已运行 `node scripts/validate-theme-contract.mjs`，registry / template / theme CSS / T 按钮 / accent 对比度一致
  □ 微动模式：css/animations.css + js/motion.js 已加载
  □ 沉浸模式：js/fx/fx-runtime.js 已加载（autoloader 自动加载所有 FX）
  □ 静态模式：无多余动效文件，canvas/hint/progress 已删除

内容
  □ 每一幕的页数比例合理
  □ 没有使用 emoji 作图标
  □ 术语用法统一
  □ 每页的 kicker + 标题 + 正文 三级信息清晰
  □ 每页主体能归入 title-block / figure-frame / metric-block / comparison-block / sequence-block / evidence-strip 中至少一种

排版
  □ 所有大标题没有 1 字 1 行的换行
  □ 所有局部底色都已声明 surface：深色/底部压暗/图片文字区用 `.on-dark` 或 `data-surface="dark"`，浅色卡片用 `.on-light`，主题色块用 `.on-accent`
  □ 图片、渐变、深色底部上的文字使用 `.readable-zone.on-dark` / `.readable-zone.on-light` 或等价 surface 容器，未出现深字深底、浅字浅底
  □ 图片网格用 height:Nvh 而非 aspect-ratio
  □ 图片只裁底部
  □ 衬线/非衬线字体分工正确
  □ 同布局重复已换变体、相邻页构图不雷同、grid 比例有混用

动效（微动/沉浸）
  □ 每个 slide 至少有一个 data-anim
  □ counter-up 的 data-to 值正确
  □ 沉浸模式 FX 容器内容有 z-index:1
  □ 不超过 2 种不同 FX
  □ 沉浸模式：fx-runtime.js autoloader 正常加载（检查浏览器控制台无 404）
  □ Swiss：每个 section 都有 data-layout + data-animate，且通过 validate-swiss-deck.mjs

视觉
  □ hero 页和 non-hero 页交替
  □ WebGL 背景在 hero 页可见（非静态模式）
  □ 图片有微弱圆角
  □ 没有沉重的阴影和边框

交互
  □ ← → 翻页正常
  □ 两侧翻页按钮可见，且点击上一页/下一页正常
  □ 底部圆点数量与总页数匹配
  □ chrome 里的页码和实际页号一致
  □ F 键全屏可用
  □ T 键和右上角 T 按钮都能切换当前风格内的预设主题；如使用自定义 `css/theme.css`，T 切换应保持锁定
  □ 所有页面已加载 `js/fit.js`，没有 `内容过密` 标记；长标题使用 `.fit-safe-text` 或拆页
  □ 沉浸模式：N 键 Notes 抽屉、O 键 Overview
  □ 沉浸模式：A 键动画循环
  □ 沉浸模式：S 键演示者模式
  □ Hash 深链接：URL #/N 格式可正常跳转
```

全勾完，才是合格的 deck。
