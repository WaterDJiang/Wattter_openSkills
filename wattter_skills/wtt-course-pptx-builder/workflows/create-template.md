---
description: 基于已有项目文件或参考模板生成新的版式或完整 deck 模板
---

# 创建模板工作流

> **调用的角色**：[Template_Designer](../references/template-designer.md)

为**全局模板库**生成一组完整的、可复用的 PPT 模板。

> 本工作流用于**库资产创建**，而非项目级一次性定制。产出必须能被未来的 PPT 项目复用，并能从对应的索引文件里被发现。

> **配套工作流**：仅锁定识别（配色 / 字体 / Logo / 语气，不带 SVG 页面）由 [`create-brand.md`](./create-brand.md) 处理。用户希望"品牌识别 + 自由页面版式"时用 `create-brand.md`；需要固定页面结构时用本工作流。

## Kind 决策——deck（默认）vs layout

本工作流根据源 PPT 是否携带具体品牌识别，产出两种 kind 之一的模板：

| Kind | 何时 | 输出目录 | `design_spec.md` 写入的内容 |
|---|---|---|---|
| **deck**（默认） | 源是某机构的品牌化 PPT（如公司年报、答辩模板）；视觉识别是复刻的一部分 | `templates/decks/<id>/` | 全部段：识别 + 结构 + 中段 |
| **layout** | 源是通用风格模板（无具体品牌）；只应复用其结构骨架；颜色 / 字体由下游按 deck 决定 | `templates/layouts/<id>/` | 仅结构段（画布 / 页面结构 / 页面类型 / SVG 清单）；不含识别段 |

默认走 **deck**，除非用户明确说"只要结构" / "只要版式" / "不要品牌识别"。拿不准时偏向 deck——后面丢掉识别很容易；从 layout 模式里反推识别则不行。完整 kind / schema / 融合模型见 [`docs/zh/templates-architecture.md`](../../../docs/zh/templates-architecture.md)。

## 流程概览

```
参考源采集与分析 → 基于事实的简报提案 → 用户确认闸口 → 创建目录并调用 Template_Designer → 资产校验 → 注册索引 → 输出
```

前 3 步从事实而非猜测中提炼简报。**在 Step 3 发出 `[TEMPLATE_BRIEF_CONFIRMED]` 之前，不得创建任何最终模板目录、不得写模板 SVG / `design_spec.md`。** `pptx_template_import.py` 产生的参考分析中间产物（通常在 `/tmp/pptx_template_import/` 下）**不受**这条闸口约束——它们是给 Step 2 用的临时工作区。

---

## Step 1：参考源采集与分析

按用户提供的参考源类型分叉。本步只产出分析产物——**不**创建最终模板目录、**不**写 `design_spec.md`、**不**碰 `layouts_index.json`。

### 输入源分类

| 类型 | 用户提供 | 工具 / 读取路径 | 可用的复刻模式 |
|------|---------|------------------|----------------|
| **A** `.pptx` 参考 | 一个 `.pptx` 文件路径 | `pptx_template_import.py` → `manifest.json` + `svg/master_*.svg` + `svg/layout_*.svg` + `svg/slide_*.svg` + `svg-flat/slide_*.svg` + `assets/` | `standard` / `fidelity` / `mirror` |
| **B** 已有 SVG 资产 | `projects/<x>/svg_output/`、`templates/layouts/<existing>`，或散放的 `.svg` 文件夹 | `ls` + `Read` 每个 `*.svg`；若有 `design_spec.md` / `spec_lock.md` 一并读取 | `standard` / `fidelity`（AI 视觉聚类） / `mirror`（直接 1:1 复制） |
| **C** 图像 / 视觉参考 | 截图文件夹、单张图片、PDF 页面 | `ls` + `Read` 每个文件（多模态视觉识别） | 仅 `standard` |
| **D** 无参考源 | 仅靠口头描述（"麦肯锡风格"、"科技蓝"、"深色极简"） | — | 仅 `standard` |

类型 C / D 不能用 `fidelity` 和 `mirror`——视觉参考与纯口头简报不足以驱动逐页复刻。类型 A 是规范路径：`manifest.json` 的页面类型候选与分层 `svg/` 工作区，能以事实数据锚定聚类检测（fidelity）与逐字复制（mirror）。类型 B 也支持，但有几点注意事项：

- **类型 B 上的 mirror**——直接 1:1 复制。B 的 SVG 已经是自包含的（每页一个文件，等同 `svg-flat/slide_*.svg`）。`<NNN>_<page_type>.svg` 文件名里的 `page_type` 遵循 PPT Master 命名约定时（`01_cover.svg` → `cover`，`03a_content_two_col.svg` → `content`）从源文件名读；否则回退到 `content`。源是 `templates/layouts/<existing>`、用户希望 fork 一份现有模板时，这套约定尤其自然。
- **类型 B 上的 fidelity**——聚类依赖 AI 对 SVG 的视觉判断；没有 `manifest.json.pageTypeCandidates` 来锚定。变体数量与分组更主观，可能需要迭代。如果输入本身就是 PPT Master 模板（`templates/layouts/<existing>`），把既有变体文件名（`03a_content_two_col` 等）当作权威聚类提示来解析，而不是再走一遍视觉聚类。

### 1A. `.pptx` 参考

运行统一的预处理辅助脚本：

```bash
python3 ${SKILL_DIR}/scripts/pptx_template_import.py "<reference_template.pptx>"
```

它在一个工作区里产出：

- `manifest.json`——单一事实来源：幻灯片尺寸、主题色、字体、各 master 的主题摘要、资产清单、占位元数据、SVG 文件路径、逐幻灯片 / 逐版式 / 逐 master 的元数据、页面类型候选
- `summary.md`——由 `manifest.json` 派生的、供快速浏览的简短可读摘要（仅供扫读）
- `assets/`——抽取出的可复用图像资产；`manifest.json` 持有资产名映射，SVG 的 `href` 值复用该映射
- `svg/`——**主视图**（分层模板视图）：
  - `svg/master_*.svg`——deck 中的每个 slide master 渲染一次，包括目前样本页没有引用的 master（模板包常带多于可见样本所引用的 master）
  - `svg/layout_*.svg`——deck 中的每个 slide layout 渲染一次（其自身贡献；master 形状**不会**在此重复）
  - `svg/slide_NN.svg`——每张幻灯片自身的形状与幻灯片局部背景；master / layout 的形状与背景**不会**在此内联
  - `svg/inheritance.json`——记录每张幻灯片消费哪个 layout 与 master
- `svg-flat/`——**伴随视图**（每张幻灯片一个自包含 SVG）：
  - `svg-flat/slide_NN.svg`——把 master + layout + slide 全部画到同一张 SVG，让单独打开任一幻灯片都能像 PowerPoint 一样看到整页。用于预览 / 截图流水线 / "幻灯片实际长啥样"的人工巡检。
- 默认 `--inheritance-mode both` 同时输出两种视图。传 `layered` 跳过 `svg-flat/`；传 `flat` 用于往返场景（旧式：`svg/` 变成不含 master / layout / inheritance 文件的自包含幻灯片）。

导入保真度规则：

- 占位元数据记入 `manifest.json`；master / layout SVG 在 `svg/` 里显示带轻量虚线导引与标签，`svg-flat/` 中不带。
- 图表、SmartArt、示意图与 OLE 对象在 `svg/` 里是类型化占位。在 `svg-flat/` 中，它们使用一张带小徽章的预览图（如有）；否则保持占位可见。表格会被转为真实 SVG。
- 缺失的媒体与外部链接图会让导入失败。EMF / WMF Office 矢量媒体在本地工具链支持时转 PNG 预览；否则导入失败。

它是一个重构辅助工具，**不是**最终的模板直转工具。

**分析期间的读取顺序**（在撰写 Step 2 之前读完所有下列内容）：

1. `manifest.json`（事实元数据：幻灯片尺寸、主题、资产、版式、master、幻灯片页面类型）
2. `svg/master_*.svg` 与 `svg/layout_*.svg`——在任何幻灯片 SVG **之前**读；它们展示 deck 的共享视觉语言（背景、页眉、页脚、装饰条）。新模板的固定结构应当从这里借鉴。
3. `svg/inheritance.json`——确认哪张幻灯片消费哪个 layout / master
4. 导出的 `assets/`
5. 清理后的幻灯片 SVG 引用 `svg/slide_NN.svg`——每张幻灯片独有的内容；掌握 master / layout 的语言之后再查阅
6. `summary.md` 仅作为快速定位的辅助
7. 用户提供的截图或原始 PPTX 仅用于视觉交叉核对

解读规则（延伸到 Step 2 和 Step 4）：

- `manifest.json` 是幻灯片尺寸、主题色、字体、背景继承、可复用资产清单、唯一 layout / master 结构、幻灯片复用关系的事实来源
- `summary.md` 仅供快速扫读；任何不清楚的地方**不要**把它当作权威事实源——回到 `manifest.json`
- 导出的 `assets/` 是规范的可复用图像池——`<svg/>` 里的 `<image>` 引用已直接指向这些文件
- `svg/master_*.svg` / `svg/layout_*.svg` 是**固定结构设计的主要来源**——重复出现的背景、页面 chrome、装饰元素，模板应当保留这些。新模板的 `01_cover` / `02_chapter` / `03_content` / `04_ending` 通常继承这些层的元素。
- `svg/slide_NN.svg` 展示页面专属内容——有助于判断构图节奏与内容密度，**不**用于固定结构。无论数量多少，每张都要读。
- `svg-flat/slide_NN.svg` 供人工预览与截图对照；不要把扁平幻灯片里重复的 master / layout chrome 当成另一组可复用的模板结构。
- 截图对判断构图与风格仍有帮助，但不应覆盖抽取出的事实元数据，除非导入结果明显不完整

**硬读取闸口**（`standard` / `fidelity` 模式——`mirror` 走另一条路，详见下文）：

- Agent **必须**在进入 Step 2 之前读完 `<import_workspace>/svg/` 下每个 `svg/master_*.svg`、`svg/layout_*.svg`、`svg/slide_*.svg`
- Agent **必须**在 Step 2 的简报提案里列出已读的 master / layout / slide 文件名，作为通过闸口的证据

**不要**把导入的 PPTX 或导出的幻灯片 SVG 当成最终模板资产——Step 4 重建为一份干净、可维护的 PPT Master 模板包，**不是** 1:1 的形状翻译。

> **Mirror 模式快速通道**——当用户明确表示要 mirror 复刻（逐字复制每张源幻灯片）：
> - **只**读 `svg-flat/slide_*.svg`（自包含的、"PowerPoint 长这样"的视图）和 `manifest.json`（用于主题色、字体、资产清单）。
> - 跳过 `svg/master_*.svg` / `svg/layout_*.svg` / `svg/inheritance.json`——mirror 模式下 chrome / 内容分离无关紧要（不会插入占位）。
> - Mirror 是一条**显式**的逐字复制流程——每张幻灯片按原样成为模板页。"重建而非翻译"规则仅适用于 `standard` / `fidelity`。

### 1B. 已有 SVG 资产

`ls` 目录并 `Read` 每个 `*.svg`，提取：

- 画布尺寸（根 `<svg>` 上的 `viewBox`）
- 重复出现的颜色（`fill` / `stroke` 值；找出占主导的 2–4 个 hex 码作为候选主题色）
- 字体（`<text>` 上的 `font-family` 属性）
- 占位使用情况（既有 `{{...}}` 字符串，如果有）
- 结构化装饰（重复出现的 `<rect>` 条、`<path>` 母题、嵌入的 `<image>` 引用）

如果 SVG 旁还有 `design_spec.md` 或 `spec_lock.md`，也 `Read`——它的置信度高于单独从 SVG 反推。把你分析笔记中与 `manifest.json` 事实字段对等的内容记下来（无需实际写文件），方便 Step 2 给它们标 `[fact]`。

### 1C. 图像 / 视觉参考

`ls` 文件夹（或单文件）并 `Read` 每张图 / PDF 页。提取可见信息：

- 粗略的主题色（目测占主导的 2–4 个色相；**不要**把精确 HEX 当作事实）
- 页数（把所提供图像数量当作大致幻灯片数）
- 主导排版风格（无衬线 / 衬线 / 展示字）——**绝不**报告字体名
- 装饰母题与构图节奏

在 Step 2 里显式说明：精确 HEX、字体名、占位结构都是从视觉估算得来的 `[suggested]`，**绝不**是 `[fact]`。

### 1D. 无参考源

跳过分析。Step 2 会把每项 Required 列为 `[decision]`；从根本不存在的源里没有事实可派生。

---

## Step 2：基于事实的简报提案

编写一条消息把每项 Required 简报项都抛给用户，**给每项值标上出处**：

- **`[fact]`**——从 Step 1 分析中抽取（如从 `manifest.json` 得来的主题色）
- **`[suggested]`**——AI 从分析或上下文推断（如语气摘要、适用场景；类型 C 的视觉估算值）
- **`[decision]`**——纯用户选择，分析无法替代（如 `template_id`、复刻模式、category）

要抛出的项：

| 项 | 必需 | 按输入类型的出处 |
|------|----------|--------------------------|
| 新模板 ID | 是 | `[decision]`——用户选 ASCII slug；若为中文品牌名，须文件系统安全且与 `layouts_index.json` 完全一致 |
| 模板显示名 | 是 | `[decision]`（通常取源 deck 标题——类型 A 时为 `[suggested]`，源自 `summary.md`） |
| 分类 | 是 | `[decision]`——`brand` / `general` / `scenario` / `government` / `special` 之一 |
| 适用场景 | 是 | `[suggested]`，源自分析；用户确认 |
| 语气摘要 | 是 | `[suggested]`，源自分析（如 `Modern, restrained, data-driven`） |
| 主题模式 | 是 | A：`[fact]`，源自 `manifest.json` 背景色。B：`[fact]`，源自 SVG `fill`。C：`[suggested]`，源自视觉估算。D：`[decision]` |
| 画布格式 | 是 | A/B：`[fact]`，源自幻灯片尺寸或 SVG `viewBox`。C：`[suggested]`，源自图像长宽比。D：`[decision]`，默认 `ppt169` |
| 复刻模式 | 是 | `[decision]`——`standard` 始终可用；`fidelity` 与 `mirror` 适用于类型 A（规范、由 manifest 锚定）和类型 B（AI 视觉聚类 / 直接 1:1 复制——见 Step 1 注意事项）；类型 C / D 一开始就拒绝 `fidelity` / `mirror` |
| 固定页的视觉保真度 | 有参考源且为 `standard` / `fidelity` 时必需；**`mirror` 不适用**（mirror 默认按字面保留） | `[decision]`——`literal`（原样保留原版几何 / 装饰 / 雪碧图裁切；尤其适用于封面 / 章节 / 结尾）或 `adapted`（参考其语气与结构，但允许设计演进）。不同页面类型可取不同设置 |
| 参考源 | 可选 | 若 Step 1 跑过则已知 |
| 主题色 | 可选 | A：`[fact]`，源自主题 XML。B：`[fact]`，源自主导 SVG `fill`。C：`[suggested]`，源自视觉估算（HEX 为近似）。D：`[decision]` |
| 字体 | 可选 | A：`[fact]`，源自 `manifest.json`。B：`[fact]`，源自 SVG `font-family`。C / D：不可派生——用户若希望自定义则标 `[decision]` |
| 设计风格 | 可选 | `[suggested]`，源自分析 |
| 资产清单 | 可选 | A：`[fact]`，源自 `assets/` 列表；用户挑选要打包的。B / C：按文件标 `[decision]`。D：无 |
| 关键词 | 是 | `[suggested]`，源自分析（3–5 个短标签）；用户确认 |

类型 A 还要在该消息中包含：

- 已读的精确 `svg/master_*.svg`、`svg/layout_*.svg`、`svg/slide_*.svg` 文件名（硬读取闸口的证据）
- 一句话总结你从 master / layout 结构中抽取的内容

用户会回复更正、补充、或"全部可以"。

> **把简报持久化到 `design_spec.md`**。当 Template_Designer 在 Step 4 写 `design_spec.md` 时，在顶部声明一个 YAML frontmatter 块，把确认后的简报写进去（`template_id`、`category`、`summary`、`keywords`、`primary_color`、`canvas_format`、`replication_mode` 等）。`register_template.py` 在 Step 6 读取它，所以简报直接流入索引，AI 不用再从散文里反推。推荐的前置元数据形状见 Step 6。

---

## Step 3：用户确认闸口

**强制的交互闸口——此步阻塞 Step 4 及其后续。**

1. 把最终定稿的简报（更正之后）用一条消息回显给用户
2. 在单独一行上发出标记 `[TEMPLATE_BRIEF_CONFIRMED]`

跳过本闸口——包括从参考源、打开的 IDE 文件或先前对话里悄悄推断值——构成工作流违规。即便用户一开始就说了"用这份 .pptx 做模板"，你也**必须**在 Step 2 里把出处标签标出来，并在此处获得显式确认。参考源只能为简报提供信息，不能替代简报。

**Step 3 的必需结果**（在发出 `[TEMPLATE_BRIEF_CONFIRMED]` 之前必须全部成立）：

- [ ] 用户已看到 Step 2 中每项 Required 及其出处标签
- [ ] 用户已回复值或显式接受建议默认值
- [ ] 模板被明确归位为**全局库模板**
- [ ] 画布格式在 SVG 生成之前已固定
- [ ] 复刻模式与输入类型一致（A 与 B 可用 `fidelity` / `mirror`，并标注 B 的注意事项；C / D 禁用）
- [ ] 模板元数据足够完整，可以注册到 `layouts_index.json`
- [ ] 回显简报之后，单独一行发出 `[TEMPLATE_BRIEF_CONFIRMED]` 标记

在当前会话里发出 `[TEMPLATE_BRIEF_CONFIRMED]` 之前，Step 4 **不得**运行。

---

## Step 4：创建模板目录并调用 Template_Designer

> **前置条件**：Step 3 已发出 `[TEMPLATE_BRIEF_CONFIRMED]`。否则回到 Step 3。

创建最终模板目录：

```bash
mkdir -p "${SKILL_DIR}/templates/layouts/<template_id>"
```

> **输出位置**：全局模板写到 `${SKILL_DIR}/templates/layouts/`；项目模板写到 `projects/<project>/templates/`
>
> 生成的目录名必须与 `layouts_index.json` 中最终的模板 ID 一致。

**切换到 Template_Designer 角色**并按角色定义生成内容。角色输入是 Step 3 的最终简报加上 Step 1 的分析包。

若输入源是类型 A，向角色传入以下内部包：

- Step 3 的最终简报
- `manifest.json`
- `summary.md`（仅供定位）
- 导出的 `assets/`
- 从 `svg/` 清理后的幻灯片 SVG 引用
- 可选的截图（如有）

类型 B：传入 SVG 文件清单、任何伴随的 `design_spec.md` / `spec_lock.md` 以及分析笔记。
类型 C：传入图像文件清单与视觉分析笔记。
类型 D：仅传入最终简报。

角色用分析包来锚定主题色、字体、可复用背景、共有品牌资产等客观事实，然后把最终 SVG 模板重建为一份简化、可维护的形式。

**应用 Step 3 的视觉保真度决策**：标 `literal` 的页（通常是封面 / 章节 / 结尾）必须按原样复刻参考版的几何、装饰与雪碧图裁切——"简化、可维护的形式"仅适用于真正冗余的结构，**不**适用于承载布局重量的部分。标 `adapted` 的页可以参考其语气与结构节奏，但允许设计演进。

**保留雪碧图（不可简化掉）**：PPTX 导出的资产常常是雪碧图——一张又高又大的图被多张幻灯片引用，每张通过嵌套 `<svg ... viewBox="...">` 包裹 `<image width="1" height="1">` 来裁取不同区域。这种嵌套是**承载布局的几何**，不是冗余结构。重建时务必为每个图像保留准确的 `viewBox` 裁切与外层 `<svg>` 定位；不要压扁成单个带直接 `x/y/width/height` 的 `<image>`。抽样验证：如果某资产的像素宽高与页面上显示的宽高比不一致，那就是雪碧图，外层包装必须保留。

**Mirror 模式覆盖**（类型 A 或 B）：当 `Replication mode: mirror` 时，本步是**逐字复制**而非重建。Template_Designer 角色：

1. **原样复制**源页到模板目录——不做任何修改——不插占位、不简化装饰、不重排 chrome / 内容。模板里发行的 SVG 与源页逐字节相同（文件名变化与资产路径改写除外）。
   - 类型 A：源是 `<import_workspace>/svg-flat/slide_NN.svg`
   - 类型 B：源是输入目录里的每个 `*.svg`（已是自包含）
2. **重命名**每个文件，使用"源序优先"的约定 `<NNN>_<page_type>.svg`，其中 `<NNN>` 是按源序补 0 到 3 位的索引，`<page_type>` 通常为 `cover` / `toc` / `chapter` / `content` / `ending`（类型无法可靠判定时回退到 `content`）。示例：`001_cover.svg`、`002_toc.svg`、`003_content.svg`、……、`050_ending.svg`。
   - 类型 A：从 `manifest.json.pageTypeCandidates` 派生 `<page_type>`
   - 类型 B：当源文件名遵循 PPT Master 约定时（`01_cover.svg` → `cover`，`03a_content_two_col.svg` → `content`）从源文件名派生 `<page_type>`；否则按页内容推断或回退到 `content`
3. **复制打包的资产**到模板目录，并把每份复制 SVG 里 `<image href="...">` 的路径改为指向本地副本。资产文件可改用语义名（`brand_emblem.png` 而非 `image3.png`），但改写在每张页面之间必须保持一致。
   - 类型 A：资产来自 `<import_workspace>/assets/`
   - 类型 B：把源 `<image href="...">` 中的相对路径按源 SVG 所在位置解析，复制每个唯一资产；若源已遵循 PPT Master 约定（资产与 SVG 位于同一目录），整组资产一起复制后再改写路径
4. 按 [template-designer.md](../references/template-designer.md) §1 写 `design_spec.md`——**§V Page Roster 中的逐页描述是承重的产物**，因为 mirror 没有可宣示每页契约的占位；下游 Strategist 只能从这些描述挑选页面。

Mirror 模式**不**走"重建为干净 SVG"路径。雪碧图保留规则仍然适用（扁平 SVG 已包含原始雪碧图包装——复制时不要压扁）。

**本步的预期产出**（完整规范见 [template-designer.md](../references/template-designer.md)）：

1. `design_spec.md`——**仅性格**。必需章节：模板概览、配色方案、标志性设计元素、页面清单（与磁盘上实际的 SVG 文件匹配）。若仅复述默认值则跳过 Typography / Assets / Placeholder Overrides。为 `register_template.py` 声明简报 frontmatter。**不要**复述通用 SVG 约束、版式模式库、字号比例带、规范占位表或内容方法论——这些源自 `shared-standards.md` / `design_spec_reference.md` / `strategist.md`，已在下游读者的上下文中。完整范围规则与骨架：[template-designer.md §1](../references/template-designer.md#1-must-generate-design_specmd)。
2. 页面清单——各模式（`standard` / `fidelity` / `mirror`）的清单、变体命名、TOC 处理见 [Page Roster](../references/template-designer.md#page-roster)
3. 占位词表——页面应在合适时采用规范命名（`{{TITLE}}`、`{{CONTENT_AREA}}` 等）。完整参考：[Placeholder Reference](../references/template-designer.md#4-placeholder-reference-canonical-convention-overridable-per-template)。当模板风格确实需要不同词表（咨询 → `{{KEY_MESSAGE}}`，品牌封面 → `{{BRAND_LOGO}}`），在 `design_spec.md` frontmatter 声明 `placeholders:` 块，让注册器与质量检查器把它当作模板的权威契约。**避免**一次性索引族（如 `{{CHAPTER_01_TITLE}}`）——改用索引化的 TOC 模式。
4. 模板资产（可选）——与模板包一起打包的 Logo / PNG / JPG / 参考 SVG

---

## Step 5：校验模板资产

```bash
# 把 <kind_dir> 替换成 "decks" 或 "layouts"，取决于上面决定的 kind
ls -la "${SKILL_DIR}/templates/<kind_dir>/<template_id>"
```

在模板目录上跑 SVG 校验：

```bash
python3 ${SKILL_DIR}/scripts/svg_quality_checker.py "${SKILL_DIR}/templates/<kind_dir>/<template_id>" --template-mode --format <canvas_format>
```

`--template-mode` 让检查器：

- 直接在模板目录里 glob `*.svg`（模板不在 `svg_output/` 之下）
- 跳过 `spec_lock.md` 漂移检查（模板不附带 spec_lock）
- 把清单 ↔ `design_spec.md` 一致性当作 **error**（孤立文件 / 缺失文件会让 `layouts_index.json` 失败）
- 当页面缺少规范占位时发出**告警**级提示——这是提示而非失败。在 `design_spec.md` frontmatter 声明 `placeholders:` 块，当模板故意使用不同词表时，可以消除这些告警

**检查清单**：

- [ ] `design_spec.md` 遵循"仅性格"骨架（概览 / 配色 / 标志性 / 页面清单）；不复述通用约束（SVG 规则、模式库、比例带、规范占位表）。§V Page Roster 列出每张已生成的页面
- [ ] `design_spec.md §V Page Roster` 中声明的每页都作为 SVG 文件存在于模板目录中（反之亦然——没有孤立文件）
- [ ] 变体文件名遵循字母后缀约定（如 `03a_content_two_col.svg`）；变体通常复用父类型的占位集，除非 spec frontmatter 另行声明
- [ ] 若含 TOC，占位模式使用规范的索引化形式
- [ ] SVG viewBox 与所选画布格式一致（`ppt169`：`0 0 1280 720`）
- [ ] 占位名在适用处遵循规范约定；模板故意使用不同词表（如 `{{KEY_MESSAGE}}` 而非 `{{PAGE_TITLE}}`）应在 frontmatter 声明 `placeholders:` 块以消除告警
- [ ] SVG 引用的资产文件确实存在于模板包中
- [ ] `fidelity` 模式：每个雪碧图资产保留其嵌套 `<svg viewBox=...>` 裁切包装；任何文件宽高比与页面上显示宽高比不一致的图像都不能被压扁成裸 `<image>`
- [ ] `mirror` 模式：文件数等于源页数（类型 A：`ls templates/layouts/<id>/*_*.svg | wc -l` 与 `<import_workspace>/svg-flat/slide_*.svg | wc -l` 一致；类型 B：与源 SVG 数一致）；文件名遵循 `<NNN>_<page_type>.svg` 约定；**复制后的 SVG 中不出现任何 `{{...}}` 占位字符串**（`grep -l "{{" templates/layouts/<id>/*.svg` 应无输出——若类型 B 源本身就含占位，用户应改用 `standard` 模式而非 mirror）；`design_spec.md` 的 §V Page Roster 列出每个已生成文件，附一句话描述页面内容与适配的内容槽位

本步是**硬闸口**。在校验通过之前不要把模板注册到库索引。

---

## Step 6：在库索引中注册模板

运行统一的注册脚本并加上 kind 标志；它从 `design_spec.md`（若有 frontmatter 则优先用，否则回退到散文）加上实际 SVG 文件列表派生对应的索引条目：

```bash
# deck（默认）
python3 ${SKILL_DIR}/scripts/register_template.py <template_id> --kind deck

# layout
python3 ${SKILL_DIR}/scripts/register_template.py <template_id> --kind layout
```

按 kind 输出（JSON 索引是单一事实来源——README 用散文描述 kind 但不枚举模板）：

| `--kind` | 更新的索引 |
|---|---|
| `deck` | `templates/decks/decks_index.json` |
| `layout` | `templates/layouts/layouts_index.json` |
| `brand` | `templates/brands/brands_index.json` |

完成卡片的文件清单通过对模板目录 glob `*.svg` 来收集。

索引文件是一个**发现索引**——它填充 SKILL.md Step 3 流程 1 的菜单，并让 AI 能通过列出名字和路径来回答"有哪些可用模板？"。**不**会仅凭列出就推进流水线。Step 3 在用户经流程 1 菜单选定（或给出显式目录路径作为快捷）时使用模板，与是否注册无关。未经 `register_template.py` 运行的模板目录，只要用户给出路径也能正常工作；只是不会出现在流程 1 菜单里。

> **新模板推荐做法**：在 `design_spec.md` 顶部声明 YAML frontmatter 块。注册器优先采用 frontmatter，而非散文抽取：
>
> ```yaml
> # deck 示例
> ---
> deck_id: my_deck
> kind: deck
> summary: ...
> canvas_format: ppt169
> page_count: 5
> primary_color: "#005587"
> ---
>
> # layout 示例
> ---
> layout_id: my_layout
> kind: layout
> summary: ...
> canvas_format: ppt169
> page_count: 5
> page_types: [cover, toc, chapter, content, ending]
> ---
> ```

> 想一次性重建全部条目（如批量编辑了多个 spec 之后），运行：
>
> ```bash
> python3 ${SKILL_DIR}/scripts/register_template.py --kind deck --rebuild-all
> python3 ${SKILL_DIR}/scripts/register_template.py --kind layout --rebuild-all
> ```

README 文件仅用散文描述每个 kind——不列举模板。发现走 JSON 索引；注册器不碰 README。

---

## Step 7：输出确认

`register_template.py` 在 Step 6 已经打印了一张"Template Creation Complete"卡片——逐字复制到对话里。卡片含模板名、路径、分类、主色、索引状态，以及完整的 SVG 文件清单（自动从磁盘收集，`fidelity` 模式的变体页与 TOC 页能正确列出，无需手工编辑）。

standard 模式模板的卡片长这样：

```markdown
## Template Creation Complete

**Template Name**: <template_id> (<display_name>)
**Kind**: deck | layout
**Template Path**: `templates/<kind_dir>/<template_id>/`
**Primary Color**: <hex>  ← deck only; omit for layout
**Index Registration**: Done

### Files Included

| File | Status |
|------|--------|
| `01_cover.svg` | Done |
| `02_chapter.svg` | Done |
| `02_toc.svg` | Done |
| `03_content.svg` | Done |
| `04_ending.svg` | Done |
```

---

## 配色速查

| 风格 | 主色 | 适用场景 |
|-------|---------------|-----------|
| 科技蓝 | `#004098` | 认证、评估 |
| 麦肯锡 | `#005587` | 战略咨询 |
| 政府蓝 | `#003366` | 政府项目 |
| 商务灰 | `#2C3E50` | 一般商务 |

---

## 备注

1. **SVG 技术约束**：见 [shared-standards.md](../references/shared-standards.md)——不要在模板的 `design_spec.md` 中复述
2. **配色一致性**：所有 SVG 文件必须与 `design_spec.md §II 配色方案` 保持同一套配色
3. **占位约定**：仅使用 `{{}}` 格式；默认命名见 [Placeholder Reference](../references/template-designer.md#4-placeholder-reference-canonical-convention-overridable-per-template)。模板需要时可在 frontmatter 用 `placeholders:` 覆盖。
4. **发现要求**：模板目录只有在用 `register_template.py`（Step 6）跑过之后才会出现在发现列表里

> **完整角色规范**：[template-designer.md](../references/template-designer.md)
