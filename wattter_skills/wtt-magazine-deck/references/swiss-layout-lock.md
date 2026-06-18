# Swiss Layout Lock · 硬约束

本文件是瑞士主题的**硬约束**。目的不是增加灵感，而是防止生成时"看起来像 Swiss，但已经脱离原始模板"。

## 黄金来源（Golden Source）

参考：
- `assets/styles/swiss/template.html`
- `assets/styles/swiss/layouts.md`
- 参考项目：`guizang-ppt-skill-main` 的 Swiss 模板语汇

瑞士主题生成时，**默认只能使用 `layouts-swiss.md` 登记的 22 个 Sxx 版式**。新增首页/尾页可使用 S01/S10 的 ASCII 变体，但**正文页必须来自 22 个登记版式**。

## 生成前硬规则

| # | 规则 |
|---|---|
| M1 | 每个 `<section class="slide">` 必须写 `data-layout="Sxx"` 或 `SWISS-COVER-ASCII` / `SWISS-CLOSING-ASCII` |
| M2 | 顶部中文标题**左对齐贴近左上内容轴**（`S03/S09/S10` / ASCII 封面/收尾例外允许居中） |
| M3 | 主体 padding 必须为 0；页面安全边距来自 `.slide` 的 `--slide-pad`，`.canvas-card` 只负责 100% 内容框，避免二次叠加 |
| M4 | kicker 必须在大标题**上方**（`flex-direction:column;gap:1.4vh`，不用 `auto 1fr` 压成左右） |
| M5 | 大字号双约束 `font-size:min(Xvw, Yvh)`，**Y ≥ X × 1.6**（防 16:9 屏高度截断） |
| M6 | canvas-card 子元素之间用 `display:grid;gap:Nvh`，不要靠 `margin/padding` 堆 |
| M7 | 主内容最低处必须停在 `--nav-safe-bottom:8vh` 上方 |
| M7a | 高密度内容页在 `.canvas-card` 内包 `.fit-shell`，长标题加 `.fit-safe-text`；出现 `内容过密` 标记时必须删减/拆页/换低密度版式 |
| M8 | 每个 `<section>` 写 `data-animate="..."`，必须命中 22 个 recipe 名之一（详见 layouts-swiss.md 末） |
| M9 | 7-8 页 deck 至少使用 **6 个不同 S 编号版式** |
| M10 | 不允许连续 3 页使用同一种主体结构 |
| M11 | 单张大图 → **S22**；多图 → S15/S16 的原始网格骨架改造 |
| M12 | **S22** 主图必须 `21:9`（`data-image-slot="s22-hero-21x9"`）+ `object-position:center 35%`（**禁 `top center`**） |
| M13 | S15/S16 多图同组统一 `21:9` 或统一 `16:10`，**同高同宽同背景** |
| M14 | 图片容器用 `.frame-img.r-21x9` 铺满槽位，**禁加 `.fit-contain`**，也**不用固定 `height:Xvh`** 把长图缩小 |
| M15 | 演示最小字号：正文 ≥ 18px / 卡片描述 ≥ 16px / meta ≥ 14px |
| M16 | 同一页内字号越小的元素字重必须 ≥ 字号越大的元素 |
| M17 | 16px 小字拒绝 weight 300，最低 400 |
| M18 | 封面/IKB 反白大标题强调字用 `italic + weight 300`，**不用 accent 色**（蓝压蓝看不见） |
| M19 | 一份 deck 只用一套主题（9 套 accent 预设中选一套，灰阶统一） |
| M20 | SVG 只画几何（圆、线、路径），**禁止 `<text>` 可见标签**，标签改用 HTML |
| M21 | P0 检查：生成后必须 `node scripts/validate-swiss-deck.mjs index.html` 通过 |
| M22 | 必须保留 `B` 切换低功耗模式（`localStorage` 持久化）+ `ESC` 索引页 |
| M23 | 不要用内联 `color:var(--paper)` / `color:var(--ink)` 硬改整页文字；深浅页使用 `slide.dark`、`b-ink`、`b-accent` 等登记 class，由 CSS 保证可读性 |
| M24 | 首页必须是主题色印象页：使用 `S01` 或 `SWISS-COVER-ASCII`，并用 `slide accent` 或大面积 `var(--accent)` 展示所选主题色 |

## 登记版式（22 个）

| ID | 名称 | 必须保留的骨架 | 图片规则 |
|---|------|---------------|---------|
| S01 | Index Cover | `slide.accent` + `.ascii-bg` + 3 行 vertical grid | 无 |
| S02 | Vertical Timeline + KPI | 顶部左对齐标题 + 中部 `.timeline-v` + 底部 `.kpi-row-4` | 无 |
| S03 | Split Statement | `.slide.split` + `.split-half` 双半屏 | 无（标题可居中） |
| S04 | Six Cells | 顶部左对齐标题 + 下方 `.sub-grid-3-2` 六卡 | 可换小图标，不放大图 |
| S05 | Three Layers | 顶部左对齐标题 + 下方 `.stack-row` 三大块 | 无 |
| S06 | KPI Tower | 左标题 + 右说明 + 下方 `.bar-towers` 4 个不等高 KPI | 无 |
| S07 | Horizontal Bar | 左对齐标题 + 横向 `.h-bar-chart` 条形图 | 无 |
| S08 | Duo Compare | `.duo-compare` + 中线 `.vrule` | 无；可 + Map 扩展 |
| S09 | Dot Matrix Statement | 大字 + `.dot-mat`/`.ring-mat`/`.cross-mat` 装饰 | 无（标题可居中） |
| S10 | Split Closing | `.slide.split` 左 accent + 右 takeaway 列表 | 无（标题可居中） |
| S11 | Horizontal Timeline | 横向 4-7 个 `.th-node` + 8px dot | 无 |
| S12 | Manifesto + Ink Banner | 大字 + 底部通栏 `.ink-banner-full` | 无 |
| S13 | Three Forces | 左 `.hero-ink-col` + 右 3 张 `.force-card` | 无 |
| S14 | Loop Form | 左 4 步 + 右 SVG 闭环 | 无；SVG 不含 `<text>` |
| S15 | Matrix + Hero Stat | 顶部左对齐 + 中段 6×2 矩阵 + 底部巨数 | 多图 21:9，`.frame-img.r-21x9` |
| S16 | Multi-card Brief | 顶部左对齐 + 下方 3×2 微卡 | 多图 21:9 |
| S17 | System Diagram | 顶部左小标题 + 中部同心圆 SVG + 底部三列 | 无；SVG 不含 `<text>` |
| S18 | Why Now | 三列递进 + 底部巨数 | 无 |
| S19 | Four Cards | 顶部 80px accent 蓝线 + 4 列均分 | 无 |
| S20 | Stacked KPI Ledger | 纵向 4-6 行 `.ledger-row` 账单 | 无 |
| S21 | Tech Spec Sheet | 大标题 + 3 KPI + 右下 9 根竖线 | 无 |
| S22 | Image Hero | 顶部全宽图（21:9）+ 左上白块 + 下方 3 列 KPI | **主图必 21:9**，`object-position:center 35%` |

## 登记扩展组件

### S08 + Swiss Map Component

详见 [`swiss-map-component.md`](swiss-map-component.md)。

- 使用场景：地理 / 历史 / 城市路线 / 人物住所关系
- 版式身份：仍是 `data-layout="S08"`，**不是**新正文页
- 静态 fallback 必须可读（瓦片失败时仍能看到点位/连线/卡片）

## 图片槽位规则

### S22 · Hero Strip（强制）

- **生成比例：21:9**（不要 16:9、4:3、1:1）
- HTML 容器必用 `.frame-img.r-21x9`
- `<img>` 必带 `data-image-slot="s22-hero-21x9"`
- `object-fit:cover;object-position:center 35%`（**禁 `top center`**）
- 主体在中央安全区，不要截人脸

### S15/S16 · Multi Image Grid

- 同一组图片必须同高、同宽、同一比例（21:9 或 16:10）
- 容器用 `.frame-img.r-21x9` 或 `.frame-img.r-16x10`，**不加** `.fit-contain`
- 不用 `height:Xvh` 短槽把长图缩小

## 禁止清单

| # | 规则 |
|---|---|
| X1 | ❌ `text-align:center` 用于顶部中文大标题（statement 类 S03/S09/S10 / ASCII 例外） |
| X2 | ❌ 把顶部标题写进右侧 7.8fr 栏造成视觉居中 |
| X3 | ❌ 未登记正文页：`P23/P24`（默认禁用，需 `--allow-experimental`） / `Swiss Image Split` / `Evidence Grid` / 三圆图自绘页 |
| X4 | ❌ 图片容器灰底包白底信息图 |
| X5 | ❌ SVG 中出现 `<text>` 作为可见标签 |
| X6 | ❌ 图片默认 `object-position:top center` 用于照片 |
| X7 | ❌ 卡片加 `border-radius`（瑞士风必须直角） |
| X8 | ❌ `.card-accent` 上又加描边（填充类型互斥） |
| X9 | ❌ 自己画 SVG 图标（必须用 `<i data-lucide="...">` 引线上 lucide） |
| X10 | ❌ 时间线 dot 用 `grid justify-self` 对齐虚线（必须用 `tl-node` + `::before` 竖虚线轴） |
| X11 | ❌ 大字号不限高（必须 `min(Xvw, Yvh)` 双约束） |
| X12 | ❌ 标题 + 卡片间距 < 5vh（章节级标题至少 9vh） |
| X13 | ❌ 9px 圆形装饰点（必须 8×8 直角方块 / mono `t-meta` 文字） |
| X14 | ❌ 装饰元素超出页面边距（严格在 grid 内） |
| X15 | ❌ 混搭多 accent 色（例如 IKB 蓝 + 柠檬黄同时出现） |
| X16 | ❌ 把用户主题色散写成 HTML inline hex；明确品牌色必须先生成 deck 专属 `theme.css` |
| X17 | ❌ 改灰阶变量（`--paper/--grey-1/2/3/--ink` 跨主题统一，只换 accent） |
| X18 | ❌ 用渐变（瑞士风拒绝任何渐变，所有色块必须纯色） |
| X19 | ❌ 给 accent 加阴影 / 圆角 / 透明度（直角纯色不透明） |
| X20 | ❌ 所有页用同一个 fade-up recipe（每页必须一个语义化 recipe） |
| X21 | ❌ 编造数据塞入 P6/P7/P18/P20/P21（数据专用版式，无真实数据时禁用） |
| X22 | ❌ 卡片混用填充类型（蓝底+蓝边、灰底+描边等） |
| X23 | ❌ 白底/灰底页写 `color:var(--paper)`，或黑底/accent 色块写 `color:var(--ink)` |
| X24 | ❌ 首页用 `grey/light` 淡化主题色，导致预设或自定义主题色在第一屏不可见 |

## 通用规则

| # | 规则 |
|---|---|
| G1 | 每个 slide 在写代码前先列：`页码 → data-layout → 为什么选它 → 图片槽位` |
| G2 | P0 对齐法则 5 条 + 字号阶梯表 + 中文标题分档表必须每次过 |
| G3 | 动效 recipe 与图形语义耦合（数字 scale 弹入 / bar scaleY / SVG 圆环 stroke-dashoffset / timeline 节点序列） |
| G4 | 缓动：productive 120-240ms / expressive 400-700ms |
| G5 | `body.low-power` 停止 WebGL canvas RAF + Motion 入场动画（`localStorage` 持久化） |
| G6 | `body.dark-bg` 切换 WebGL shader 的 `u_dark=1` |
| G7 | `windows` 平台字重补偿：`body.is-win .name-mega/.num-mega/.kpi-thin{font-weight:300}` |
| G8 | 卡片填充规则：`.card-fill` 灰底中性 / `.card-ink` 黑底反转 / `.card-accent` 单一焦点 / `.card-outlined` 描边锚点 |
| G9 | chrome-min 用 `.tight` 减少底部间距（head 区紧凑场景） |
| G10 | `h-bar-chart` 的 `row-fill` 默认 `var(--ink)`，可通过 `.accent` / `.grey` 切换 |
| G11 | 表格行 / 列表行 / 时间线说明 / caption / 图注必须守住 `16px` 下限 |
| G12 | 一份 deck 主图（`S22` / `S15` / `S16`）≤ 2 个不同槽位比例 |

## 字号阶梯（重要 · 与 editorial 不同）

| 类名 | 字号 | 字重 | 用途 |
|---|---|---|---|
| `.kpi-hero` | 22vw (200 高度) | **800** | 满屏巨数 KPI（最重 + 最大） |
| `.kpi-big` | 11vw | **800** | 中型 KPI 数字 |
| `.kpi-mid` | 6vw | **700** | 卡片 KPI |
| `.kpi-thin` | 14vw (limit 200vh) | **200** | 极细巨数（替代 .kpi-hero 的克制度） |
| `.h-hero` | 11vw (200vh) | **200** | 英文 hero 大字 |
| `.h-xl` | 6vw | **200** | 英文章节标题 |
| `.h-md` | 2.6vw | 300 | 中标题 |
| `.h-sub` | 2.2vw | 400 | 副标题 |
| `.lead` | 1.55vw | 400 | 引语 |
| `.body` | max(18px, 1.08vw) | 400 | 正文 |
| `.t-body` | 18px | 400 | 段落 |
| `.t-body-sm` | 16px | 400 | 列表行 |
| `.t-meta` / `.t-cat` | 14px | 500-600 | 元数据（mono） |
| `.t-helper` | 14px | 400 | 辅助文字 |

**核心原则："越大越细，越小越粗"**——`.kpi-hero` 22vw 但 800 字重（最重）；`.h-hero` 11vw 反而 200 字重（最细）。**字号递减字重递增**。
