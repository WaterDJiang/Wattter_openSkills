# 截图美化语义规则

> 本文件由 `guizang-ppt-skill` 的同名参考文档迁移而来,已按 wtt-magazine-deck v2 架构改写。原文末段的"Style A / Style B"对应本 skill 的 `editorial` / `swiss` 两种风格(对外展示名:杂志叙事型 / 瑞士信息型)。

用于把用户提供的产品截图、网页截图、代码截图、设计稿截图处理成符合模板比例的图片资产。目标是类似 CleanShot X 的"截图居中 + 背景填充 + 统一比例",而不是默认让 GPT 重新画截图。

## 优先级

1. **程序化适配优先**:截图内容、文字、UI 细节需要保真时,不要重画;创建目标比例画布,把原截图等比缩放后放入画布。
2. **GPT 只做重构**:只有原图过长、过窄、信息太乱、需要 UI 情景化或概念化表达时,才使用"截图再设计 / UI 情景图"(参考 `references/image-prompts.md`)。
3. **模板槽位先行**:先确定 slide 版式和图片槽位比例,再决定截图适配参数。

## 开始前询问

在主流程 Step 1 中,只要用户可能提供截图,就先问清楚:

- 截图在哪个文件夹?是否包含网页、App、代码、dashboard、设计稿或旧 PPT?
- 这批截图要**保真展示**、**统一美化**、**重新设计成 UI 情景图**,还是混合处理?
- 最终要放进哪些槽位:21:9 顶图(S22)、16:10 主图、4:3 侧图、1:1 方图、还是多图网格(S15/S16)?
- 是否必须保留所有文字和数据?是否需要隐藏账号、头像、项目名等敏感信息?
- 构图希望居中、左上、右下,还是根据页面内容自动判断?

## 处理链路

1. **先匹配版式**:根据内容选择模板 layout,确定截图槽位尺寸和比例。
2. **再选处理方式**:
   - 要保真:程序化适配,不重画截图。
   - 要统一视觉但不改内容:程序化适配 + 主题背景。
   - 原图不可用或需要解释概念:再走 GPT 截图再设计(见 `image-prompts.md`)。
3. **再选择背景**:优先使用内置背景资产(下方表格),不应该每张截图临时生成一种风格。
4. **最后合成截图**:创建目标比例画布,背景 cover 铺满,截图等比缩放后按 `padding` 和 `alignment` 放入。

默认不要裁掉截图内容。只有截图已经按目标槽位重新生成,或者用户明确允许裁切时,才使用 cover 裁切。

## 语义参数

每次处理截图前,先确定这 7 个参数:

| 参数 | 可选值 | 判断方式 |
|---|---|---|
| `ratio` | `21:9` / `16:10` / `16:9` / `4:3` / `1:1` | 跟随模板图片槽位(S22 用 21:9,S15/S16 多图统一 21:9 或 16:10),不要跟随原截图比例 |
| `background` | `plain` / `gradient` / `wallpaper` / `blurred` / `grid` / `paper` | 跟随当前 PPT 风格和主题 |
| `padding` | `compact` / `standard` / `spacious` | 普通截图 standard;文字密集或高截图 spacious;小图组 compact |
| `inset` | `none` / `subtle` / `balanced` | 截图需要从背景中浮出来时用 balanced;瑞士风多用 none/subtle |
| `shadow` | `none` / `soft` / `editorial` | editorial 可 soft/editorial;swiss 默认 none |
| `corners` | `square` / `small` / `medium` | swiss square;editorial small/medium(由 `--img-radius` 控制) |
| `alignment` | `center` / `top-left` / `top-right` / `bottom-left` / `bottom-right` | 跟随页面构图,不是永远居中 |

## 风格映射

### 杂志叙事型 (editorial)

- 背景: `paper` / `blurred` / 低饱和 `gradient`
- 质感:纸张、墨水、胶片颗粒、暖白、低对比
- 截图:可用小圆角和轻微阴影,但不要像 SaaS 营销卡片
- 背景资产:优先使用 `assets/screenshot-backgrounds/editorial/` 下对应主题的 16:9 crop-safe WebP,截图合成时按槽位裁切
- 推荐语义:

```text
ratio:16:10, background:paper, padding:standard, inset:balanced, shadow:editorial, corners:small, alignment:center
```

### 瑞士信息型 (swiss)

- 背景: `plain` / `grid` / `dot-matrix`
- 色彩:只允许当前锚点色作为极低占比强调;不要大面积亮色块
- 截图:直角、无阴影、无圆角、少量 hairline 或顶部 accent 线
- 背景资产:优先使用 `assets/screenshot-backgrounds/swiss/` 下对应主题色的 16:9 crop-safe WebP,只用当前 accent,不要混色
- 推荐语义:

```text
ratio:21:9, background:grid, padding:standard, inset:subtle, shadow:none, corners:square, alignment:center
```

## 背景强度规则

截图背景是"托底",不是主视觉。

- 如果 `alignment` 不确定,背景中心和四角都必须安静,不要放显眼色块。
- 如果截图要放在右下角,右下角不能有强色块;其他位置同理。
- 瑞士风锚点色只做 `5%-8%` 视觉占比的淡线、点阵或极浅几何场,不要生成高亮蓝条、大色块、霓虹渐变。
- 背景不能有文字、logo、图标、人物、设备、边框、明显主体或方向性构图。
- 背景必须 crop-safe:裁成 `21:9`、`16:10`、`4:3`、`1:1` 都不能暴露"被裁掉"的痕迹。

## 内置主题背景资产

本 skill 已经内置一组预生成背景。处理截图时**优先使用这些资产**,不要实时调用 GPT 重新生成背景。只有用户明确要求新风格、现有主题缺失,或背景与内容明显不匹配时,才生成新的背景。

背景图之后由程序复用到每张截图中。不要把背景当作单张 slide 来画,背景图内部不能有标题、页脚、边框、logo、人物或明显主体。

### 杂志叙事型 (editorial) · 5 套主题背景

| 主题 | 内置资产 | 背景语义 |
|---|---|---|
| 墨水经典 `ink-classic` | `assets/screenshot-backgrounds/editorial/ink-classic.webp` | 黑白灰纸张纹理、柔和阴影、细颗粒 |
| 靛蓝瓷 `indigo-porcelain` | `assets/screenshot-backgrounds/editorial/indigo-porcelain.webp` | 靛蓝低饱和墨色、纸感渐变、轻微噪点 |
| 森林墨 `forest-ink` | `assets/screenshot-backgrounds/editorial/forest-ink.webp` | 模糊植物阴影、低饱和绿色、纸张颗粒 |
| 牛皮纸 `kraft-paper` | `assets/screenshot-backgrounds/editorial/kraft-paper.webp` | 暖纸色、淡墨阴影、复古印刷颗粒 |
| 沙丘 `dune` | `assets/screenshot-backgrounds/editorial/dune.webp` | 沙色/灰调柔和渐变、低对比、留白安静 |

### 瑞士信息型 (swiss) · 4 套主题背景

| 主题色 | 内置资产 | 背景语义 |
|---|---|---|
| 克莱因蓝 `ikb-blue` | `assets/screenshot-backgrounds/swiss/ikb-blue.webp` | 点阵 + 低对比蓝色渐变,避免亮蓝大色块 |
| 柠檬黄 `lemon-yellow` | `assets/screenshot-backgrounds/swiss/lemon-yellow.webp` | 纯网格 + 稀疏点阵,黄色只做低透明细线/点 |
| 柠檬绿 `lemon-green` | `assets/screenshot-backgrounds/swiss/lemon-green.webp` | 点阵 + 阴影场,绿色只做轻微光感 |
| 安全橙 `safety-orange` | `assets/screenshot-backgrounds/swiss/safety-orange.webp` | 模块化半调点阵 + 暗部阴影,橙色低占比 |

### 瑞士信息型 (swiss) · 5 套新主题(无内置 webp)

以下 5 套 v2 新增主题**没有预生成 webp 背景**,处理截图时请走 `image-prompts.md` 的"Swiss 主题扩展"小节即时生成背景,或继续使用纯色 plain 底色。

| 主题色 | 状态 | 处理建议 |
|---|---|---|
| 爱马仕橙 `hermes-orange` | ⚠ 无内置 | 走 image-prompts.md 即时生成背景,或 plain 底色 |
| 银行红 `bank-red` | ⚠ 无内置 | 同上 |
| 蒂芙尼蓝 `tiffany-blue` | ⚠ 无内置 | 同上 |
| 华伦天奴粉 `valentino-pink` | ⚠ 无内置 | 同上 |
| 宝缇嘉绿 `bottega-green` | ⚠ 无内置 | 同上 |

> 这 5 套 ⚠ 行不是漏图,是 v2 架构的有意决定:注册 9 套主题是为了让 `scripts/make-custom-theme.mjs` 能复用 swiss 灰阶 + accent 注入流程,而不是为每套主题预生成 GPT 背景。背景统一由运行时根据所选主题的 accent 通过 prompt 生成(参见 `references/image-prompts.md`「Swiss 主题扩展」一节)。

内置背景都是 1920×1080 级别的 16:9 WebP。程序化合成时,先把背景 cover 到目标画布,再裁成 `21:9` / `16:10` / `4:3` / `1:1` 等截图槽位。背景必须四角安静,因为截图可能居中、左上、右下或被裁成不同尺寸。

## 截图类型决策

| 原始素材 | 推荐处理 |
|---|---|
| 普通网页 / App / 桌面截图 | 程序化适配到目标比例 |
| 产品 UI 细节很重要 | 程序化适配,使用 `figure-frame` + `fit-contain`,不重画 |
| 长网页截图 | 截关键区域或拆成 2-3 张同尺寸面板 |
| 极窄 / 极高截图 | 先尝试 `spacious + side alignment`;仍太小时再重构 |
| 代码截图 | editorial 用纸感背景;swiss 用浅网格背景;文字必须可读 |
| 概念解释用的 UI 情景图 | 可以用 GPT 重新设计(走 `image-prompts.md` 的"截图再设计"模板) |

## 组件契约

本文件描述的所有截图处理结果,落地到 slide 时都属于 `figure-frame` 组件(见 `references/required-components.md`),不要发明 `screenshot-callout` 之类的顶层组件。截图落位时使用 `assets/core/components.css` 已经实现的 `.frame-img` / `.figure-frame` / `.fit-contain` / `.swiss-img-grid` 等既有 class。

## 生成背景图提示词

只有需要新增背景资产时才使用本节。常规截图美化不要实时生成背景,直接使用上方内置资产。

### editorial 背景

```text
16:9 crop-safe screenshot background for an editorial magazine / e-ink PPT system. Warm off-white paper texture, subtle ink wash, fine film grain, low contrast, quiet center and quiet corners, no text, no logo, no objects, no border, no focal subject. Suitable for cropping to 21:9, 16:10, 4:3, or 1:1.
```

### swiss 背景

```text
16:9 crop-safe screenshot background for a Swiss International Style PPT system. Pure off-white base, ultra-subtle 16-column grid and sparse dot matrix, one accent color only: [theme color], used at very low opacity as thin lines or tiny dots, no large bright color blocks. Quiet center and quiet corners, no text, no logo, no objects, no border, no focal subject. Suitable for cropping to 21:9, 16:10, 4:3, or 1:1.
```

`[theme color]` 可替换为 9 套 swiss 主题中的任意一个;只有 4 套基色(ikb-blue / lemon-yellow / lemon-green / safety-orange)已有内置 webp,其余 5 套走 prompt 即时生成。
