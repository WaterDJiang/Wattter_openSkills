---
name: wtt-course-pptx-builder
description: >
  AI 驱动的多格式 SVG 内容生成系统。通过多角色协作，将源文档（PDF / DOCX / URL / Markdown）转换为高质量 SVG 页面并导出为 PPTX。
  支持品牌/版式/Deck 模板、AI 图像生成、网页图像搜索、实时预览编辑、图表校准、动画定制、旁白录制、视觉自检等。
  当用户提出以下需求时使用：(1) "create PPT" / "make presentation" / "生成 PPT" / "做 PPT" / "制作演示文稿"；
  (2) 模板相关："create template" / "create brand" / "创建模板" / "创建品牌"；
  (3) 图像相关："generate image" / "搜索图片" / "AI 生图"；
  (4) 后处理相关："verify charts" / "校准图表" / "customize animations" / "定制动画" / "visual review" / "视觉自检"；
  (5) 导出相关："export PPTX" / "导出 PPT" / "add narration" / "添加旁白"；
  (6) 恢复："继续生成" / "resume execution"
---

# 课程 PPT 构建器技能

> AI 驱动的多格式 SVG 内容生成系统。通过多角色协作将源文档转换为高质量 SVG 页面，并最终导出为 PPTX。

**核心流水线**: `源文档 → 创建项目 → [模板] → 策略师 → [图像生成] → 执行器实时预览 → 质量检查 → 后期处理 → 导出`

> [!CAUTION]
> ## 🚨 全局执行纪律（强制要求）
>
> **本工作流是一条严格的串行流水线。以下规则拥有最高优先级——违反任何一条都视为执行失败：**
>
> 1. **串行执行（SERIAL EXECUTION）** — 各步骤必须按顺序执行；前一步的输出是后一步的输入。一旦前置条件满足，相邻的非 BLOCKING 步骤可以连续进行，无需用户说"继续"
> 2. **BLOCKING = 硬停止（BLOCKING = HARD STOP）** — 标记为 ⛔ BLOCKING 的步骤需要完全停下；AI 必须等待用户明确回复后才能继续，绝不能替用户做任何决定
> 3. **禁止跨阶段打包（NO CROSS-PHASE BUNDLING）** — 跨阶段打包是被禁止的。（注：Step 1 的流程闸口与 Step 4 的八项确认属于 ⛔ BLOCKING——AI 必须先呈现推荐方案并等待用户明确确认后才能继续。一旦用户确认，后续所有非 BLOCKING 步骤——设计规范输出、SVG 生成、讲者备注、后期处理——都可以自动进行，无需再次确认）
> 4. **进入前先过闸（GATE BEFORE ENTRY）** — 每个 Step 顶部都列出了前置条件（🚧 GATE），开始该 Step 前必须先校验
> 5. **禁止投机执行（NO SPECULATIVE EXECUTION）** — 禁止"预先准备"后续 Step 的内容（例如，在 Strategist 阶段就写 SVG 代码）
> 6. **禁止子代理生成 SVG（NO SUB-AGENT SVG GENERATION）** — Executor Step 6 的 SVG 生成是上下文相关的，必须由当前主代理端到端完成。禁止把页面 SVG 生成委派给子代理
> 7. **只允许逐页顺序生成（SEQUENTIAL PAGE GENERATION ONLY）** — 在 Executor Step 6 中，确认全局设计上下文后，SVG 页面必须以一次性连续过程逐页生成。禁止批量生成（例如一次 5 页）
> 8. **每页重读 SPEC_LOCK（SPEC_LOCK RE-READ PER PAGE）** — 在生成每张 SVG 页面之前，Executor 必须 `read_file <project_path>/spec_lock.md`。所有颜色 / 字体 / 图标 / 图片都必须来自该文件——禁止凭记忆或临时编造。Executor 还必须查询当前页的 `page_rhythm`（`anchor` / `dense` / `breathing`）、`page_layouts`（如要继承的模板 SVG）以及 `page_charts`（如要套用的图表模板）。空 / 缺失条目是 Strategist 的有意信号——参见 executor-base.md §2.1。该规则是为了抵御长 deck 上的上下文压缩漂移，并打破"每页都是卡片网格"的统一默认
> 9. **SVG 必须手写，禁止脚本生成（SVG MUST BE HAND-WRITTEN, NOT SCRIPT-GENERATED）** — 每张 SVG 页面都由主代理直接逐页手写（参见规则 6 和 7）。禁止编写或运行 Python / Node / shell 脚本批量产出 SVG 文件——包括循环生成页面、数据模板化、或通过生成器发出——即便以"省 token"、"快速草稿"或"用户赶时间"为借口。脚本生成路径曾在特性分支上试过并被放弃：跨页视觉一致性依赖于带完整上游上下文的逐页手写，生成器脚本无法复现

> [!IMPORTANT]
> ## 🌐 语言与沟通规则
>
> - **回答语言**：与用户输入及源材料保持一致。若用户明确指定（如"请用英文回答"），以用户指定为准。
> - **模板格式**：`design_spec.md` 必须保持其原始英文模板结构（章节标题、字段名），无论对话使用何种语言。内容值可使用用户语言。

> [!IMPORTANT]
> ## 🔌 与通用编码技能的兼容性
>
> - `wtt-course-pptx-builder` 是仓库级工作流，不是通用应用脚手架
> - 默认不要创建 `.worktrees/`、`tests/`、分支工作流或通用工程结构
> - 与通用编码技能冲突时，除非用户明确说明，否则以本技能为准

## 主要流水线脚本

| 脚本 | 用途 |
|--------|---------|
| `${SKILL_DIR}/scripts/source_to_md/pdf_to_md.py` | PDF 转 Markdown |
| `${SKILL_DIR}/scripts/source_to_md/doc_to_md.py` | 各类文档转 Markdown — DOCX/HTML/EPUB/IPYNB 用原生 Python；.doc/.odt/.rtf/.tex/.rst/.org/.typ 等遗留格式走 pandoc 兜底 |
| `${SKILL_DIR}/scripts/source_to_md/excel_to_md.py` | Excel 工作簿转 Markdown — 支持 .xlsx/.xlsm；旧版 .xls 需另存为 .xlsx |
| `${SKILL_DIR}/scripts/source_to_md/ppt_to_md.py` | PowerPoint 转 Markdown |
| `${SKILL_DIR}/scripts/source_to_md/web_to_md.py` | 网页转 Markdown（通过 `curl_cffi` 支持微信公众号） |
| `${SKILL_DIR}/scripts/project_manager.py` | 项目初始化 / 校验 / 管理 |
| `${SKILL_DIR}/scripts/analyze_images.py` | 图像分析 |
| `${SKILL_DIR}/scripts/latex_render.py` | LaTeX 公式渲染（基于清单生成 PNG 资源） |
| `${SKILL_DIR}/scripts/image_gen.py` | AI 图像生成（多 provider） |
| `${SKILL_DIR}/scripts/svg_quality_checker.py` | SVG 质量校验 |
| `${SKILL_DIR}/scripts/total_md_split.py` | 讲者备注拆分 |
| `${SKILL_DIR}/scripts/finalize_svg.py` | SVG 后期处理（统一入口） |
| `${SKILL_DIR}/scripts/svg_to_pptx.py` | 导出为 PPTX |
| `${SKILL_DIR}/scripts/update_spec.py` | 在所有已生成 SVG 间传播 `spec_lock.md` 的颜色 / font_family 变更 |

完整工具文档请参见 `${SKILL_DIR}/scripts/README.md`。

> **Windows 提示**：若 `python3 ...` 命令失败（python.org 安装版本常见，只提供 `python.exe` 而无 `python3.exe`），请改用 `python` 重跑同一命令。

## 模板索引

| 索引 | 路径 | 用途 |
|-------|------|---------|
| 版式模板 | `${SKILL_DIR}/templates/layouts/layouts_index.json` | 查询可用的页面版式模板 |
| 品牌预设 | `${SKILL_DIR}/templates/brands/brands_index.json` | 查询可用的品牌识别预设（颜色 / 字体 / Logo / 语气） |
| 完整 Deck | `${SKILL_DIR}/templates/decks/decks_index.json` | 查询可用的完整 PPT 复刻模板（识别 + 结构 + 资源） |
| 可视化模板 | `${SKILL_DIR}/templates/charts/charts_index.json` | 查询可用的 SVG 可视化模板（图表、信息图、示意图、框架图） |
| 图标库 | `${SKILL_DIR}/templates/icons/` | 参见 `${SKILL_DIR}/templates/icons/README.md`；按需用 `ls ${SKILL_DIR}/templates/icons/<library>/ \| grep <keyword>` 搜索图标 |

> 三个模板索引（brands / layouts / decks）的每条条目都自带 `kind` 与 `path` 字段，供 Step 3 流程 1 的统一菜单与"有哪些模板？"带外问答共用。新模板经 `register_template.py` 注册后自动出现在索引与流程 1 菜单中。

## 独立工作流

| 工作流 | 路径 | 用途 |
|----------|------|---------|
| `topic-research` | `workflows/topic-research.md` | 流水线前——当用户只提供主题而没有源文件时，先抓取网络资料 |
| `template-fill` | `workflows/template-fill-pptx.md` | 给定原生 PPTX 模板与源材料；挑选合适页面（一页可复用于多张输出幻灯片）并直接回填文字，无需 SVG 转换 |
| `use-user-template` | `workflows/use-user-template.md` | 流程 2 入口——用户提供 `.pptx` 模板，分析其设计身份后落到当前项目 `templates/`，可选入库 |
| `create-template` | `workflows/create-template.md` | 独立版式模板创建工作流（入库供未来流程 1 复用） |
| `create-brand` | `workflows/create-brand.md` | 独立品牌模板创建（识别预设；不含 SVG 页面清单；入库） |
| `resume-execute` | `workflows/resume-execute.md` | 阶段 B 入口——在另一个会话完成阶段 A（Step 1–5）后，在新会话中恢复执行（分阶段模式） |
| `verify-charts` | `workflows/verify-charts.md` | 图表坐标校准——若 deck 含数据图表，在 SVG 生成后运行 |
| `customize-animations` | `workflows/customize-animations.md` | 对象级 PPTX 动画定制——仅当用户明确要求调整动画顺序/效果/时机时运行 |
| `live-preview` | `workflows/live-preview.md` | 基于浏览器的实时预览——生成过程中自动启动，并在用户提到"live preview"、"preview"、"看效果"或希望点击/选中幻灯片元素时随时可重新进入 |
| `visual-review` | `workflows/visual-review.md` | 基于评分细则的逐页可视化自检——仅当用户明确要求在生成的 SVG 上做一轮视觉复检时（位于 Executor 与后期处理之间）运行。仅作为可选步骤，主流水线不会主动调用。 |

---

## 工作流

### Step 1：流程确认与源内容处理

🚧 **GATE**：用户已提供初始需求（主题 / 源文件 / 模板文件 / 文字描述——任何形式均可）。

#### 1a. 流程确认（三选一闸口）

⛔ **BLOCKING（仅当歧义时）**：向用户呈现三条流程并等待选择。若用户开场消息已隐含某条流程，则预选并在同一轮内确认，无需单独追问。

| 流程 | 含义 | 触发信号 |
|---|---|---|
| **流程 1 · 用 skill 库模板** | 从本 skill 自带模板库选一个或多个，渐进式加载后走后续生成 | 用户提到库中已知模板名 / 问"有哪些模板" / 想复用已有模板 |
| **流程 2 · 用用户提供的模板** | 用户以 `.pptx` 文件形式提供模板，skill 分析其设计身份后构建 | 用户附带 `.pptx` 模板 + 内容材料 / 说"套这份 pptx 模板" |
| **流程 3 · 自由构建**（默认） | 不用任何模板，Strategist 全程自由设计 | 其余情况——纯主题 / 纯内容材料 / 无模板意图 |

**推荐信号**：附 `.pptx` 模板 → 推荐流程 2；提及库中模板名或明确要复用 → 推荐流程 1；其余 → 推荐流程 3。无信号或歧义时才 BLOCKING 三选一。

> **显式路径逃生口**：用户若直接给出一个模板目录路径（如 `templates/decks/招商银行/`），视为流程 1 预选该模板，跳过 Step 3 的菜单选择，一轮确认即进入 Step 4。

确认后，所选流程决定 Step 3 的获取方式；Step 2 及之后的生成流水线三条流程完全一致。

#### 1b. 源内容处理

> **没有源内容怎么办？** 当用户只提供主题名或需求，没有任何文件或实质性描述时，请先运行 [`topic-research`](workflows/topic-research.md) 工作流，再回到此处以其产物作为输入。

若用户提供的是非 Markdown 内容，请立即转换：

| 用户提供 | 命令 |
|---------------|---------|
| PDF 文件 | `python3 ${SKILL_DIR}/scripts/source_to_md/pdf_to_md.py <file>` |
| DOCX / Word / Office 文档 | `python3 ${SKILL_DIR}/scripts/source_to_md/doc_to_md.py <file>` |
| XLSX / XLSM / Excel 工作簿 | `python3 ${SKILL_DIR}/scripts/source_to_md/excel_to_md.py <file>` |
| CSV / TSV | 直接以纯文本表格源读取 |
| PPTX / PowerPoint 演示文稿 | `python3 ${SKILL_DIR}/scripts/source_to_md/ppt_to_md.py <file>` |
| EPUB / HTML / LaTeX / RST / 其他 | `python3 ${SKILL_DIR}/scripts/source_to_md/doc_to_md.py <file>` |
| 网页链接 | `python3 ${SKILL_DIR}/scripts/source_to_md/web_to_md.py <URL>` |
| 微信 / 高安全站点 | `python3 ${SKILL_DIR}/scripts/source_to_md/web_to_md.py <URL>`（需要 `curl_cffi`，已包含在 `requirements.txt` 中） |
| Markdown | 直接读取 |

> **流程 2 的 `.pptx` 模板文件不是内容源**——它是设计参考。在 Step 2 `import-sources` 时随内容源一起进入 `sources/`，但 Step 1b 不对它做内容转换；它的设计分析发生在 Step 3 流程 2。

> **来自 DOCX/PPTX 源中的 Office 矢量资源（EMF/WMF）**：
> `doc_to_md.py` / `ppt_to_md.py` 会提取内嵌的 Office 矢量图像（.emf/.wmf）
> 与位图一起被导出。`import-sources` 后，这些资源会落到 `images/` 目录中，
> 与 `image_manifest.json` 一起作为 §VIII 图像资源清单中的一等资源。
>
> **不要把 EMF/WMF 转成 PNG。** 课程 PPT 构建器流水线将它们作为外部引用保留
> （`finalize_svg.py` 会跳过它们），`svg_to_pptx.py` 通过
> `image/x-emf` / `image/x-wmf` MIME 嵌入为 PPTX 原生媒体——PowerPoint 以全矢量保真度渲染。
> 通过 LibreOffice/Inkscape 转换会引入 CJK 字体替换漂移以及
> 栅格化损失；原始 EMF/WMF 始终比转换后的 PNG 保真度更高。
>
> 基于浏览器的实时预览无法渲染 EMF（会显示空白）——这是预期行为；
> PPTX 输出才是最终标准。

**✅ 检查点 —— 确认流程已选定、源内容就绪后，进入 Step 2。**

---

### Step 2：项目初始化

🚧 **GATE**：Step 1 已完成；源内容已就绪（Markdown 文件、用户提供的文字、或对话中描述的需求均为有效）。

```bash
python3 ${SKILL_DIR}/scripts/project_manager.py init <project_name> --format <format>
```

格式选项：`ppt169`（默认）、`ppt43`、`xhs`、`story` 等。完整格式列表请见 `references/canvas-formats.md`。

导入源内容（按情况选择）：

| 情况 | 操作 |
|-----------|--------|
| 有源文件（PDF/MD 等） | `python3 ${SKILL_DIR}/scripts/project_manager.py import-sources <project_path> <source_files...> --move` |
| 用户直接在对话中提供文字 | 无需导入——内容已在对话上下文中；后续步骤可直接引用 |

> ⚠️ **必须使用 `--move`**（而不是拷贝）：所有源文件——Step 1 生成的 Markdown、原始 PDF / MD / 图片——都会通过 `import-sources --move` 进入 `sources/`。执行完毕后，原始位置将不再保留。中间产物（如 `_files/`）会自动处理。

**✅ 检查点 —— 确认项目结构创建成功，`sources/` 包含所有源文件，转换材料就绪。进入 Step 3。**

---

### Step 3：模板获取（按流程分支）

🚧 **GATE**：Step 2 已完成；项目目录结构就绪。按 Step 1a 选定的流程分支获取模板。

> **三条流程共用同一生成流水线**——差异只在模板如何到达 `<project>/templates/`。无论哪条流程，一旦 `<project>/templates/design_spec.md` 就位，Step 4 Strategist 的读取与锁定逻辑完全一致。

---

#### 流程 1 · 用 skill 库模板（渐进式目录）

**Tier 1 — 读索引渲染菜单**：读取三个 `*_index.json`（条目已含 `kind` / `path`，轻量），合并为统一菜单呈现给用户：

```
Read templates/brands/brands_index.json
Read templates/layouts/layouts_index.json
Read templates/decks/decks_index.json
```

每条展示：`id` / `kind` / `summary` / `primary_color`（brand、deck）/ `canvas_format` / `page_count`（layout、deck）。用户按编号或 id 选**一个或多个**（可跨 kind 融合，见下方"多选融合"）。

> **兼容新增模板**：`register_template.py` 自动把新模板注册进 `*_index.json`；本菜单实时读索引，新模板零代码改动即出现。不要在 skill 任何地方硬编码模板列表。

> **"有哪些模板？"属于带外问答**——通过列出索引条目及其 `path` 回答。仅列举不推进流水线；用户必须在流程 1 的菜单里选定才能推进。

**Tier 2 — 选定后加载模板**：用户选定后，按各条目的 `path` 字段定位目录，`cp -r <selected_dir>/* <project_path>/templates/`（多选则先融合，见下）。选定前**不**读模板的 `design_spec.md` 或 SVG——渐进式加载，省 token。

**显式路径逃生口**：若用户在 Step 1a 已直接给出目录路径（或在流程 1 中直接给路径），跳过菜单，等价于预选该路径，直接 `cp`。AI 不应"贴心"地把裸名字解析成路径——用户必须走菜单或给路径。

**三种模板类型**（架构上有三个相互独立的参考包；完整 schema 见 [`docs/zh/templates-architecture.md`](../../docs/zh/templates-architecture.md)）：

| 类型 | 物理目录 | 包含 | Frontmatter |
|---|---|---|---|
| **brand** | `templates/brands/<id>/` | 仅识别段：颜色 / 字体 / Logo / 语气 / 图标风格 | `kind: brand` |
| **layout** | `templates/layouts/<id>/` | 仅结构段：画布 / 页面结构 / 页面类型 / SVG 清单 | `kind: layout` |
| **deck** | `templates/decks/<id>/` | 完整复刻：识别 + 结构 + 中段（模板概览） | `kind: deck` |

**单选派发**（按所选条目的 `kind`）：

| `kind` | Step 3 操作 |
|---|---|
| `kind: brand` | 复制 `design_spec.md` + Logo 文件 + 资源子目录（`images/` / `illustrations/` / `icons/`）到 `<project>/templates/`。Strategist 把识别段锁定为权威，结构保持自由。 |
| `kind: layout` | 复制 `design_spec.md` + SVG 清单 + 资源文件到 `<project>/templates/`。Strategist 锁定结构；识别在八项确认 e–g 中决定。 |
| `kind: deck` | 复制全部内容（`design_spec.md` + SVG + Logo + 资源）到 `<project>/templates/`。Strategist 锁定所有段；八项确认收窄到 deck 内容字段（受众 / 页数 / 大纲 / 语气微调）。 |

```bash
TEMPLATE_DIR=<selected path from index>
cp -r ${TEMPLATE_DIR}/* <project_path>/templates/
```

一行复制对三种类型都够用——spec 中的 `kind` 字段会告诉 Strategist 如何读取；下游代码不做区分。

**多选融合**——当用户选了两个或以上**不同 kind** 的模板时，Step 3 将它们融合成单个 `<project>/templates/design_spec.md`。**默认粒度是段级整体替换**——识别 / 结构 / 中段这些整段内容从该段优先级最高的来源取，不做隐式的字段级混搭。

**段的归属**（决定融合覆盖优先级）：

| 段 | 子章节 | 融合时的所有者 kind |
|---|---|---|
| 识别（Identity） | 配色 / 字体 / Logo / 语气 / 图标风格 | brand |
| 结构（Structure） | 画布 / 页面结构 / 页面类型 / SVG 清单 | layout |
| 中段（Middle） | 模板概览（使用场景 / 设计意图） | deck（其他 kind 不会写这段） |

按段的覆盖优先级：

| 组合 | 识别来自 | 结构来自 | 中段来自 |
|---|---|---|---|
| 仅 brand | brand | （自由设计） | （无） |
| 仅 layout | （自由设计） | layout | （无） |
| 仅 deck | deck | deck | deck |
| brand + layout | brand | layout | （无） |
| brand + deck | brand（覆盖 deck） | deck | deck |
| layout + deck | deck | layout（覆盖 deck） | deck |
| brand + layout + deck | brand | layout | deck |

字段级微调（例如"用 anthropic brand 但主色改为 #FF0000"）**不**属于 Step 3 融合的范畴——它会作为普通用户请求流入 Strategist 的八项确认 e–g。

**同 kind 多选——冲突解决**：当用户选了两个**同 kind** 的模板（例如 `brands/anthropic` + `brands/google`）时，Step 3 会在融合前弹出一个冲突提示——类似于解决 git 合并冲突：

```
AI: 你选了两个 brand，检测到段级冲突：
    - 配色（Anthropic 橙红 vs Google 多色）
    - 字体（Styrene/AnthropicSans vs GoogleSans/Roboto）
    - Logo（Anthropic 标 vs Google 标）
    - 语气（克制 vs 友好）
    - 图标风格（描边 vs 填充）

    要 (a) 全部按 Anthropic / (b) 全部按 Google / (c) 逐段挑？
```

规则：
- 默认：不做隐式排序——任何跨来源的段差异都报告为冲突
- 仅当用户选择 `(c)` 时，AI 才会逐段过一遍
- 字段级冲突不在范围内——只做段级
- 三个或以上同 kind 选择不支持——请用户收敛到最多两个

**融合后 spec 的来源说明**：当发生融合时（任何多选情况），生成的 `<project>/templates/design_spec.md` 会在其 H1 标题正下方带一个来源说明块：

```markdown
> **融合来源：**
> - deck: `templates/decks/招商银行/` （基底）
> - brand: `templates/brands/anthropic/` （识别覆盖）
> - layout: `templates/layouts/academic_defense/` （结构覆盖）
> - 已解决冲突：配色取自 anthropic（用户选了 a）
```

单选的 Step 3 **不会**添加来源说明（来源从被复制的文件中一目了然）。

**✅ 检查点 —— 模板已复制（或融合）到 `<project_path>/templates/`，进入 Step 4。**

---

#### 流程 2 · 用用户提供的模板

用户在 Step 1a 选了流程 2，或在开场附带 `.pptx` 模板 + 内容材料。本流程是独立工作流 [`use-user-template`](workflows/use-user-template.md) 的入口：

```
切换到 workflows/use-user-template.md
```

该工作流：
1. 运行 `pptx_template_import.py` 分析 `<project>/sources/` 中的用户 `.pptx`（主题色 / 字体 / 尺寸 / SVG 视图 / `manifest.json`）
2. ⛔ BLOCKING 子选择：**身份+结构复刻**（调 Template_Designer 项目模式，重建 SVG 版式清单 + 完整 `design_spec.md`）或**仅身份提取**（只写识别段 `design_spec.md`，结构留给 Strategist 自由设计）
3. 产物落 `<project>/templates/`（默认不入库）
4. 末尾可选入库（保存到 `templates/<kind>/<id>/` + `register_template.py` 注册，供未来流程 1 复用）

完成后回到主线，进入 Step 4。

> ❌ 流程 2 **不要**运行 `template_fill_pptx.py`（那是 [`template-fill-pptx.md`](workflows/template-fill-pptx.md) 的 OOXML 文本回填，不是设计身份分析）。

**✅ 检查点 —— 用户模板已分析并落到 `<project_path>/templates/`，进入 Step 4。**

---

#### 流程 3 · 自由构建（默认）

不用任何模板。直接进入 Step 4，Strategist 全程自由设计。

**✅ 检查点 —— 跳过模板获取，直接进入 Step 4。**

---

> 若要新建版式或 deck 入库供未来流程 1 使用，请阅读 [`workflows/create-template.md`](workflows/create-template.md)。若要新建品牌入库，请阅读 [`workflows/create-brand.md`](workflows/create-brand.md)。这两个是**库资产创建**工作流，与流程 1/2 的**项目级使用**不同。

---

### Step 4：策略师阶段（强制要求——不可跳过）

🚧 **GATE**：Step 3 已完成；已采用默认自由设计路径，或（若触发）模板文件已复制到项目中。

首先，阅读角色定义：
```
Read references/strategist.md
```

> ⚠️ **强制闸口**：在写 `design_spec.md` 之前，Strategist 必须 `read_file templates/design_spec_reference.md` 并遵循其完整的 I–XI 节结构。详见 `strategist.md` 第 1 节。

**八项确认**（完整模板：`templates/design_spec_reference.md`）：

⛔ **BLOCKING**：将八项确认作为一份打包的推荐方案呈现给用户，并**等待用户明确确认或修改**后再输出设计规范与内容大纲。这是唯一的核心确认点——一旦确认，所有后续步骤将自动进行。

1. 画布格式
2. 页数范围
3. 目标受众
4. 风格目标
5. 配色方案
6. 图标使用方式
7. 字体方案（含公式渲染策略）
8. 图像使用方式

**强制 —— 分阶段模式提示**（不是第九项确认）：在列出八项确认后，你必须追加一行短句（用用户的语言、前缀 💡）说明生成模式。根据 Phase A 信号做定性判断来选择变体——推荐页数、源材料体量、是否运行了 `topic-research` 并累积了大量网络抓取内容：

| 信号判断 | 行内容 |
|---|---|
| 较重（页数多 / 源材料厚 / 网络抓取累积多） | 说明预估页数与较大的源材料量；建议在 Step 5 之后切换到 [分阶段模式](workflows/resume-execute.md)——停止此对话，开一个新窗口输入 `继续生成 projects/<project_name>` 进入 Phase B（SVG 生成 + 导出）；无回复或说"继续" = 默认连续模式。 |
| 正常（默认） | 说明规模适中，默认连续模式一次性生成；若中途希望切换窗口，可在 Step 5 之后输入 `继续生成 projects/<project_name>` 切换到 [分阶段模式](workflows/resume-execute.md)。 |

此行每次运行都必须输出——用户必须始终看到模式选项的存在。如何决定由用户做主。

**强制 —— 规范精修提示**（不是第九项确认）：在分阶段模式行之后，你必须追加一行短句（用用户的语言、前缀 💡）告诉用户可以**先精修规范**——Strategist 将产出完整的设计规范，然后在任何生成开始前停下等待用户审阅/修改任意部分，方法是走 [refine-spec](workflows/refine-spec.md) 工作流。默认关闭：无请求 → 规范一次性写完，流水线照常自动推进。仅当用户明确请求（例如"先精修规范"）时，[refine-spec](workflows/refine-spec.md) 工作流才会在八项确认之后介入。该行与分阶段模式行一样，每次运行都必须输出——用户必须看到选项的存在；是否使用由用户决定。

**公式渲染策略位于第 7 项（字体方案）内部**：

| 策略 | 行为 |
|---|---|
| `mixed`（默认） | Strategist 将复杂、值得作为公式的表达式渲染为 PNG 资源；简单内联表达式保持可编辑文字 / Unicode |
| `render-all` | Strategist 把所有值得作为公式的表达式都渲染为 PNG 资源 |
| `text-only` | 不做公式渲染；公式保持可编辑文字 / Unicode |

在八项确认通过之后、**输出 `design_spec.md` / `spec_lock.md` 之前**，若已确认的公式策略为 `mixed` 或 `render-all` 且内容中包含值得作为公式的表达式，Strategist 必须：

1. 识别显式的 LaTeX 以及源中任何应当严格作为公式呈现的表达式。
2. 写出 `<project_path>/images/formula_manifest.json`，仅包含被选中渲染的公式。
3. 运行：
   ```bash
   python3 ${SKILL_DIR}/scripts/latex_render.py <project_path>
   ```
4. 在 `design_spec.md §VIII 图像资源清单` 中，把渲染好的公式 PNG 作为 `Acquire Via: formula`、`Status: Rendered`、`Type: Latex Formula` 的行加入；同时在 `spec_lock.md images` 中以 `| no-crop` 列出。

公式渲染器默认使用 provider 回退链：`codecogs,quicklatex,mathpad,wikimedia`。前三者支持自定义颜色；Wikimedia 是可用性兜底。公式 PNG 默认透明：清单中的 `background` 是临时渲染底色和去透明参考色，并非最终保留背景，除非该项设置了 `transparent: false`。不要在 `spec_lock.md` 中扫描 `$...$` 或 `$$...$$`。源材料中用美元符号包围的数学内容仅作为 Strategist 的信号；渲染器读取的是显式清单。

若用户提供了图像或已经渲染好公式 PNG，请在**输出设计规范之前**运行分析：
```bash
python3 ${SKILL_DIR}/scripts/analyze_images.py <project_path>/images
```

> ⚠️ **图像处理**：永远不要直接读取 / 打开 / 查看图像文件（`.jpg`、`.png` 等）。所有图像信息都来自 `analyze_images.py` 的输出或设计规范中的图像资源清单。

**输出**：
- `<project_path>/design_spec.md` —— 人类可读的设计叙事
- `<project_path>/spec_lock.md` —— 机器可读的执行契约（骨架：`templates/spec_lock_reference.md`）；Executor 在每页之前会重新读取

**✅ 检查点 —— 阶段交付物完成，自动进入下一步**：
```markdown
## ✅ 策略师阶段完成
- [x] 八项确认已完成（用户已确认）
- [x] 分阶段模式提示已附加在八项之后（较重或正常变体）
- [x] 规范精修可选行已附加（默认关闭；只有用户明确请求才进入 refine-spec 工作流）
- [x] 设计规范与内容大纲已生成
- [x] 执行契约（spec_lock.md）已生成
- [ ] **下一步**：自动进入 [图像生成 / 执行器] 阶段
```

---

### Step 5：图像获取阶段（条件性）

🚧 **GATE**：Step 4 已完成；设计规范与内容大纲已生成且用户已确认。任何公式行已经带 `Acquire Via: formula` 和 `Status: Rendered`。

> **触发条件**：资源清单中至少有一行 `Acquire Via: ai` 和/或 `Acquire Via: web`。若所有行都是 `user`、`formula` 或 `placeholder`，则跳过 Step 6。

**始终先加载通用框架**：

```
Read references/image-base.md
```

然后**按需懒加载**路径专属参考：

| 获取方式 | 加载参考（仅当存在该类行时） | 运行 |
|---|---|---|
| `ai` | `references/image-generator.md` | `python3 ${SKILL_DIR}/scripts/image_gen.py --manifest <project_path>/images/image_prompts.json` |
| `web` | `references/image-searcher.md` | `python3 ${SKILL_DIR}/scripts/image_search.py ...` |
| `user` / `placeholder` | （跳过） | （跳过） |

只含 `ai` 行的 deck 永远不加载 `image-searcher.md`；只含 `web` 行的 deck 永远不加载 `image-generator.md`。混合 deck 两者都加载，各自行使自己的路径处理，输出 `image_prompts.json` 与 `image_sources.json`。

> ⚠️ **流水线内的 ai 路径必须用清单模式**——即便只有 1 行 ai 也一样。先写 `images/image_prompts.json`，再跑 `image_gen.py --manifest`，再跑 `image_gen.py --render-md` 生成 `image_prompts.md` 边车文件。位置参数形式（`image_gen.py "prompt" ...`）仅供**流水线外一次性测试 / 单图修补**——它跳过清单 + 边车，不留审计痕迹。

工作流：

1. 从设计规范中提取所有 `Status: Pending` 且 `Acquire Via ∈ {ai, web}` 的行
2. 按 [image-base.md](references/image-base.md) §2 派发表为 ai 行生成提示词，为 web 行执行搜索
3. 确认每行达到终止状态：`Generated`（ai 成功）、`Sourced`（web 成功）或 `Needs-Manual`

**✅ 检查点 —— 确认对每一行都尝试了获取**：
```markdown
## ✅ 图像获取阶段完成
- [x] 已创建 image_prompts.json（处理过任何 ai 行时）
- [x] 已渲染 image_prompts.md 边车（处理过任何 ai 行时）
- [x] 已创建 image_sources.json（处理过任何 web 行时）
- [x] 每一行：状态为 `Generated` / `Sourced` / `Needs-Manual`（无 `Pending` 剩余）
```

**默认 —— 自动进入 Step 6。** 仅当用户在 Step 4 的回复中明确选择了分阶段模式（针对可选提示），才输出下面的 Phase A 交接块并停止对话：

  ```markdown
  ## ✅ Phase A 完成
  - [x] 规范：`design_spec.md`、`spec_lock.md`
  - [x] 资源：`sources/`、`images/`、`templates/`
  - [ ] **下一步**：打开新聊天窗口，输入 `继续生成 projects/<project_name>`，通过 [`resume-execute`](workflows/resume-execute.md) 工作流进入 Phase B。
  ```

> 获取失败时不要停下——遵循 [image-base.md](references/image-base.md) §5 中的失败处理规则：重试一次，然后把该行标记为 `Needs-Manual`，向用户报告，并继续到上面的检查点。

---

### Step 6：执行器阶段

🚧 **GATE**：Step 4（以及被触发的 Step 5）已完成；所有前置交付物已就绪。

阅读本 deck 已锁定 `mode` + `visual_style` 的执行参考（来自 `spec_lock.md`）：
```
Read references/executor-base.md                  # 必读：通用指南
Read references/shared-standards.md               # 必读：SVG/PPT 技术约束
Read references/modes/<locked-mode>.md            # 叙事骨架（spec_lock.md `mode`）
Read references/visual-styles/<locked-style>.md   # 美学风格（spec_lock.md `visual_style`）
```

> 阅读 executor-base + shared-standards + 对应的 mode 文件 + 对应的 visual-style 文件。若 `mode: custom` 或 `visual_style: custom`，跳过该预设文件，改用 `spec_lock.md` 中的 `mode_behavior` / `visual_style_behavior`。不要通配 `modes/` 或 `visual-styles/`。

**设计参数确认（强制）**：在生成第一张 SVG 之前，从规范中输出关键设计参数（画布尺寸、配色方案、字体方案、正文字号）。详见 executor-base.md §2。

**实时预览自动启动（强制）**：在生成第一张 SVG 之前，自动以 live 模式启动浏览器编辑器，并在 Executor + Step 7 导出期间持续运行：
```bash
python3 ${SKILL_DIR}/scripts/svg_editor/server.py <project_path> --live
```
- Executor 一开始就立即启动；此时 `svg_output/` 可能为空。编辑器在 `http://localhost:5050` 打开；端口冲突 → `--port <其他>` 并报告实际 URL。
- 把它作为长时运行的旁路进程/会话；不要等它退出再生成 SVG 页面。启动后不要等待用户确认。
- **服务必须保持运行**，直到以下任一情况：(a) 用户在浏览器中点击 **Exit preview**，或 (b) 用户在对话中明确要求停止。即使用户关闭了编辑器，生成也会继续。
- **生成期间不要读取或应用已提交的批注。** 用户可以随时批注，但 Executor 在不触碰它们的情况下继续。批注的应用窗口只在 Step 7 完成后打开——见 [`workflows/live-preview.md`](workflows/live-preview.md)。
- 编辑器还支持**分阶段的直接编辑**（文本内容 + SVG 元素属性立即预览，仅当用户点击 **Apply changes** 时才写入 `svg_output/`；`Ctrl+Z` / 撤销可丢弃分阶段编辑），与批注并行；重新导出仍由对话驱动。完整范围与编辑器细节：见 [`workflows/live-preview.md`](workflows/live-preview.md) Notes。

**生成前批量预读（强制）**：在生成第一张 SVG 之前，批量预读 `spec_lock.page_layouts` 中引用的每个不同版式 SVG，以及 `spec_lock.page_charts` 中引用的每个不同图表 SVG（加上任何 §VII 备用图表）。每个文件预读一次，预先完成——在生成过程中不要重新读取这些文件。详见 executor-base.md §1.0。

**每页重读 spec_lock（强制）**：在**每一张**SVG 页面之前，`read_file <project_path>/spec_lock.md`，仅使用其中的颜色 / 字体 / 图标 / 图片，加上按页的 `page_rhythm` / `page_layouts` / `page_charts` 查询结果（解析到上面批量预读中已加载的模板 SVG）。抵御长 deck 的上下文压缩漂移。详见 executor-base.md §2.1。

> ⚠️ **仅主代理**：SVG 生成必须留在当前主代理——页面设计依赖完整的上游上下文。不要委派给子代理。
> ⚠️ **生成节奏**：在同一连续上下文中逐页、逐张、按顺序生成。不要批量（例如 5 张一组）。

**视觉构建阶段**：SVG 页面在一次连续过程中逐页、逐张、按顺序生成 → `<project_path>/svg_output/`

**质量检查闸口（强制）**——所有 SVG 生成完毕之后，批注处理与讲者备注之前：
```bash
python3 ${SKILL_DIR}/scripts/svg_quality_checker.py <project_path>
```
- 任何 `error`（禁用 SVG 特性、viewBox 不匹配、spec_lock 漂移等）必须先修复才能继续——回到视觉构建阶段，重新生成该页，再次跑检查。
- `warning` 项（低分辨率图片、不安全的字体尾部等）：能修就修，否则承认并放行。
- 针对 `svg_output/` 运行（不要在 `finalize_svg.py` 之后——finalize 会重写 SVG 并掩盖违规）。

**逻辑构建阶段**：生成讲者备注 → `<project_path>/notes/total.md`

**✅ 检查点 —— 确认所有 SVG 与备注均已完整生成并通过质量检查。直接进入 Step 7 后期处理**：
```markdown
## ✅ 执行器阶段完成
- [x] 实时预览已启动，并在所报告 URL 持续可用
- [x] 所有 SVG 已生成到 svg_output/
- [x] svg_quality_checker.py 通过（0 错误）
- [x] 讲者备注已生成到 notes/total.md
```

> **图表页？** 若本 deck 含数据图表（柱状 / 折线 / 饼图 / 雷达 等），在 Step 7 之前运行独立 [`verify-charts`](workflows/verify-charts.md) 工作流进行坐标校准。AI 模型在把数据映射到像素位置时常常引入 10–50 px 的误差；verify-charts 可消除这一类错误。无图表页则跳过。

> **可视化自检（可选）？** 仅当用户明确要求在 SVG 上做逐页视觉复检（"跑一下视觉自检 / 视觉回看"、"visual review"、"check pages visually" 等）时，在 Step 7 之前运行独立 [`visual-review`](workflows/visual-review.md) 工作流。不要默认运行，也不要基于推断的模型能力或 deck 体量主动推荐——触发条件仅为用户请求。

---

### Step 7：后期处理与导出

🚧 **GATE**：Step 6 已完成；所有 SVG 已生成到 `svg_output/`；讲者备注 `notes/total.md` 已生成。

🚧 **图像就绪 GATE**（当 Step 5 把 ai 行留在 `Needs-Manual` 时）：运行 7.1 之前，每个预期文件都必须存在于 `project/images/<filename>`。

> 若文件缺失：暂停，列出缺失的文件名，让用户查看 `images/image_prompts.md`（每个 `### Image N:` 块都直接可粘贴到 ChatGPT / Gemini / Midjourney；从 `image_prompts.json` 自动生成）以及所需放置位置 `project/images/<filename>`。只有所有预期文件到位后，才继续 Step 7.1。`finalize_svg.py` 和 `svg_to_pptx.py` 在该层不会检测缺失文件——带着缺口继续会产出图片引用破损的 deck。

> ⚠️ 三个子步骤**一次只跑一个**——上一步必须成功完成再跑下一步。
> ❌ **绝不要**把它们合并到单个代码块或 shell 调用里。

规范的三命令流水线（对应 `references/shared-standards.md` §5）：

**Step 7.1** —— 拆分讲者备注：
```bash
python3 ${SKILL_DIR}/scripts/total_md_split.py <project_path>
```

**Step 7.2** —— SVG 后期处理（图标嵌入 / 图片裁剪并嵌入 / 文字打平 / 圆角矩形转 path）：
```bash
python3 ${SKILL_DIR}/scripts/finalize_svg.py <project_path>
```

**Step 7.3** —— 导出 PPTX（默认嵌入讲者备注）：
```bash
python3 ${SKILL_DIR}/scripts/svg_to_pptx.py <project_path>
# 输出（默认流模式）：
#   exports/<project_name>_<timestamp>.pptx           ← 原生 pptx（标准输出，读取 svg_output/）
#   backup/<timestamp>/svg_output/                    ← Executor SVG 源备份（始终写入）
#
# 加入 --svg-snapshot 可在原生 pptx 之外额外输出 SVG 图片预览版 pptx：
#   exports/<project_name>_<timestamp>_svg.pptx      ← SVG 预览版 pptx（读取 svg_final/）
```

> 原生 pptx 直接消费 `svg_output/`，以便转换器能保留
> 高保真图元（图标 `<use>` 占位、图片 `preserveAspectRatio`
> → `srcRect`、圆角矩形 `rx/ry` → `prstGeom roundRect`）。`svg_output/`
> 在 `backup/<timestamp>/` 中的快照始终会写入，方便项目在
> 冻结的 SVG 源上重新导出，而无需重跑 LLM。SVG 渲染的
> 预览版 pptx 通过 `--svg-snapshot` 启用——实时预览已经提供了
> SVG 视觉参考，因此仅在需要单个自包含文件分享时才需要预览版。
> 若需强制单一来源，传入 `-s output` 或 `-s final`。

> **段落可编辑性 vs 行保真度** —— 默认情况下，可合并的 dy 堆叠
> 段落块会合并为一个包含多个 `<a:p>` 的可编辑 PowerPoint 文本框，
> 提升正文编辑与 resize/reflow 行为。仅当用户明确要求严格的行布局保真
> 或版式紧凑的页面必须把每条 dy 堆叠行保留为独立文本框时，才加 `--no-merge`。
> 合并检测器是保守的；混合版式的文本会回退为逐行独立文本框。


**可选动画标志**（默认已启用丰富的入场动画——仅当用户要求不同效果时才调整）：
- `-t <effect>` —— 页面切换效果。默认 `fade`。可选：`fade` / `push` / `wipe` / `split` / `strips` / `cover` / `random` / `none`。
- `-a <effect>` —— 元素级入场动画。默认 `auto`（按组 id 映射效果：chart→wipe，card-/step-/pillar-→fly，title/takeaway→fade；类图片 id `hero` / `figure-` / `image` / `img-` / `kpi` 在更丰富的效果池——zoom / dissolve / circle / box / diamond / wheel——中循环，使 deck 中多张图片效果各异）。传 `none` 禁用，传具体效果（如 `fade`），或传 `mixed` 启用旧的 16 效果循环。需要顶层 `<g id="...">` 组（Executor 已要求）。
- `--animation-trigger {on-click,with-previous,after-previous}` —— 启动方式（对应 PowerPoint 动画窗格中的"开始"下拉）。默认 `after-previous`（无点击级联；通过 `--animation-stagger` 控制节奏）。演示者节奏揭示用 `on-click`，一次性全部触发用 `with-previous`。
- `--animation-config <path>` —— 可选的对象级边车文件。默认：存在 `<project_path>/animations.json` 时使用。
- `--auto-advance <seconds>` —— kiosk 风格自动播放。

**可选的自定义动画**（仅当用户要求为特定对象调整动画顺序/效果/时机时）：

运行独立 [`customize-animations`](workflows/customize-animations.md) 工作流。默认导出已带全局入场动画；除非请求对象级定制，否则不要创建 `animations.json`。

**可选的录制旁白**（仅当用户要求带旁白/视频导出时）：

运行独立 [`generate-audio`](workflows/generate-audio.md) 工作流。AI 选择旁白后端（默认 `edge`，或已配置的云端 provider 如 ElevenLabs / MiniMax / Qwen / CosyVoice，用于高质量或克隆声音），一次性询问用户（后端 + 声音 + 语速/设置 + 是否嵌入，均提供推荐值），然后执行 `notes_to_audio.py`，并在用户选择嵌入时用 `--recorded-narration audio` 重新导出 PPTX。

不要绕过工作流直接调用 `notes_to_audio.py`——`--voice` / `--voice-id` 是必需的，工作流会给出与语言环境/provider 相关的推荐，让选择更有意义。

完整效果列表、锚定逻辑与限制：[`references/animations.md`](references/animations.md)。

> ❌ **绝不要**用 `cp` 代替 `finalize_svg.py`——finalize 会执行多个关键的处理步骤
> ❌ **绝不要**为旧版/预览版 pptx 强制 `-s output`（PowerPoint 的内部 SVG 解析器会丢弃图标和圆角）。默认的 auto-split 已为原生提供所需的高保真源，无需触碰旧版。
> ❌ **绝不要**用 `--only`（它会抑制两个输出文件之一）

> **导出后批注窗口**：Step 6 的预览服务在导出后通常仍保持运行。若用户在浏览器中（Executor 期间或导出后）提交了批注，现在要求应用——他们可能引用浏览器提示（`Changes saved to svg_output...` / `修改已保存到 svg_output...`），或说 "apply my annotations" / "应用注解" / 同义表达——运行 [`live-preview`](workflows/live-preview.md) Step 2 来应用并重新导出。生成期间提交的批注也在这里处理，不在更早阶段。

> **浏览器中的直接编辑**：用户还可以在预览中对文本 / SVG 属性做分阶段编辑。这些内容只有在用户点击 **Apply changes** 后才会落到 `svg_output/`。如果他们在应用这些编辑后要求 "re-export" / "重新导出"，直接重跑 Step 7.2–7.3（finalize + export）；除非他们同时保存了 AI 需要的批注，否则无需运行批注应用步骤。

> **预览未运行？** 任何时候用户提到 "live preview"、"preview"、"看效果"，或希望选择/点击幻灯片元素而服务未运行，请运行 [`live-preview`](workflows/live-preview.md) Step 1 启动它。若服务已运行，直接把 URL 指给他们——不要重启。

---

## 角色切换协议

在切换角色之前，**必须先阅读**对应的参考文件。输出标记：

```markdown
## [角色切换：<角色名称>]
📖 阅读角色定义：references/<filename>.md
📋 当前任务：<简要描述>
```

---

## 参考资源

| 资源 | 路径 |
|----------|------|
| 共享技术约束 | `references/shared-standards.md` |
| 画布格式规范 | `references/canvas-formats.md` |
| 图文布局模式（主结构 + 修饰层——可自由组合） | `references/image-layout-patterns.md` |
| 图像布局尺寸（并列容器尺寸计算） | `references/image-layout-spec.md` |
| SVG 图像嵌入 | `references/svg-image-embedding.md` |
| 图标库 | `templates/icons/README.md` |

---

## 备注

- 本地预览：`python3 -m http.server -d <project_path>/svg_final 8000`
- **故障排查**：遇到生成问题（布局溢出、导出错误、图像空白等）时，查阅 `docs/faq.md` 中的已知解决方案
