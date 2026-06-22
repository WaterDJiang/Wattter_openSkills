---
description: PPTX 模板填充工作流——使用原生 PowerPoint 模板 deck，挑选合适的页面，并把新材料直接回填，无需经过 SVG 转换
---

# 模板填充（PPTX）工作流

> 当用户希望把新内容填进已有 deck 时运行。典型请求包括"用这份 deck 填新内容"、"把这套模板回填"、"复用这份 deck 的设计"。用户提供一份现有 `.pptx` 作为原生模板 deck，再加主题/文字材料，希望在保留该 deck 设计的前提下把内容回填进去，并只挑选适合新故事的页面（一页源页面可被多张输出幻灯片复用）。

本工作流**独立于** SVG 生成流水线。它把源 PPTX 视作原生模板/幻灯片库，保留原始 PowerPoint 设计不动，通过克隆所选源幻灯片并直接在 OOXML 中替换文字来写出一份新的 `.pptx`。

## 何时运行

识别同时涉及"已有 PowerPoint"和"新内容或主题"的请求，例如：

| 模式 | 示例 |
|---|---|
| 已有 `.pptx` + "回填"意图 | "用这份 deck，把附件材料填进去" |
| 已有 `.pptx` + 主题复用 | "围绕新主题重做这份 PPTX" |
| 已有 `.pptx` + 选择性复用 | "不必保留每一页；只用那些合适的幻灯片" |
| 已有 `.pptx` + 文案替换 | "保留原设计，把文字换成这份文本" |
| 原生 PPT 模板填充 | "用这份 PowerPoint 模板套这份内容" |
| 直接措辞 | "用新内容填这份 deck" |

**硬规则**：本工作流**不要**运行 `pptx_to_svg.py`、`pptx_template_import.py`、`finalize_svg.py` 或 `svg_to_pptx.py`。SVG 转换用于演示文稿生成 / 模板创建；本工作流是直接的 PowerPoint 编辑。

---

## Step 1：输入

🚧 **GATE**：用户已提供：

| 输入 | 必需 | 备注 |
|---|---:|---|
| 源 PPTX | 是 | 用作幻灯片库的原始设计 deck |
| 内容材料 | 是 | 用户文字、Markdown、文档、URL 派生的源材料，或清晰的主题简报 |
| 目标输出意图 | 可选 | 受众、页数、语气、必须保留的页面、必须丢弃的页面 |

如果内容材料只是主题、没有支撑事实，先收集或索要源材料。**不要**编造细节性事实。

---

## Step 2：创建项目工作区

在 `projects/` 下创建独立的项目目录。**不要**把产出直接写到 `projects/` 根目录。

```bash
mkdir -p "<project_dir>/sources" "<project_dir>/analysis" "<project_dir>/exports" "<project_dir>/validation"
```

使用如下固定目录布局：

| 路径 | 应包含内容 |
|---|---|
| `<project_dir>/sources/` | 源 PPTX 与用户提供的文字 / Markdown / 转换产物 |
| `<project_dir>/analysis/` | 幻灯片库 JSON、页面挑选理由与最终填充计划 |
| `<project_dir>/exports/` | 仅最终生成的 PPTX |
| `<project_dir>/validation/` | 回读 Markdown、抽取的验证资产与验证备注 |

**硬规则**：模板填充项目就是一个项目，而非散落的输出文件。最终答案必须指向 `<project_dir>/exports/<name>.pptx`，所有中间产物都保留在 `<project_dir>` 内部。

---

## Step 3：抽取幻灯片库

运行：

```bash
python3 ${SKILL_DIR}/scripts/template_fill_pptx.py analyze "<project_dir>/sources/<source.pptx>" -o "<project_dir>/analysis/slide_library.json"
```

读取 `<project_dir>/analysis/slide_library.json` 并识别：

| 字段 | 用途 |
|---|---|
| `slides[].page_type` | 封面 / 章节 / 内容 / 结尾候选 |
| `slides[].text_summary` | 源页面当前的语义用途 |
| `slides[].slots[]` | 可替换的文字槽位，含 `slot_id`、`role`、几何信息、段落数与旧文字 |
| `slides[].slots[].role` | 标题 / 正文 / 标签候选提示 |
| `slides[].tables[]` | 原生 PowerPoint 表格，含 `table_id`、行 / 列数，以及逐单元格坐标 + 文字 |
| `slides[].charts[]` | 原生 PowerPoint 图表，含 `chart_id` |

**挑选规则**：按内容契合度挑选页面，而非仅按源顺序挑选。源页面只有在"其可见结构能承载目标信息、无需大幅重设计"时才有用。

一个页面的版式本身就编码了一种修辞结构——单句 hero 陈述、先导-细节分栏、2×2 对比、逐步递进、指标行。把源材料自身的逻辑匹配到结构能表达同样逻辑的页面；不要因为某个槽位是空的就把不相关的内容硬塞进去。当没有所选页面能很好地承载某段内容时，丢掉那个页面或那段内容——硬填会显得呆板。输出页数少于源 deck 页数也是合理的。

**版式优先规划**：把 `slide_library.json` 视作版式清单，而非有序的 deck 大纲。在写 `fill_plan.json` 之前，从 JSON 字段推断每张可复用源页面的承载能力：

| JSON 信号 | 版式规划用法 |
|---|---|
| `slides[].page_type` | 识别封面 / 目录 / 章节 / 结尾候选，但默认不要保留其原始顺序 |
| `slots[].role` 计数 | 推断该页面属于 hero 陈述、对比、多卡列表、时间线、指标行、密集解释中的哪一类 |
| `slots[].geometry` | 估计每个文字槽位是短标签、中等标题、正文块、说明文字还是装饰数字 |
| `slots[].text_metrics.font_size_px` | 结合几何信息估算文字容量；字号越大、安全字数越少 |
| `slots[].text_summary` | 读源页面原本的修辞模式，而不是字面上的占位措辞 |

**硬规则**：目标故事控制输出顺序。源幻灯片可以前移、后移、跳过，也可在版式匹配多个目标信息时被复用多次。除非用户明确要求保留源顺序，否则**不要**把源幻灯片顺序当作默认大纲。

**必需的映射步骤**：在定稿计划之前，在 `<project_dir>/analysis/` 下创建一份简洁的"页面-版式映射理由"。可以是 JSON 或 Markdown，但必须记录：预期的目标幻灯片、所选 `source_slide`、版式理由（例如 `three-column strategy`、`two-problem contrast`、`timeline`、`metric focus`、`chapter divider`）。这是挑选来自模板结构、而非顺序替换的证据。

---

## Step 4：构建填充计划

创建骨架：

```bash
python3 ${SKILL_DIR}/scripts/template_fill_pptx.py scaffold "<project_dir>/analysis/slide_library.json" -o "<project_dir>/analysis/fill_plan.json" --slides "1,3,4"
```

然后根据源材料**手工**编辑 `<project_dir>/analysis/fill_plan.json`。该计划就是单一的执行契约。

**页面可复用**：输出是有序的 `slides` 列表，而非源 deck 的一对一复制。源页面不是单次使用的——把同一个 `source_slide` 按需列出多次，每条记录带各自的 `replacements`，就能从一个优质版式驱动多张输出幻灯片（例如把同一内容版式复用于五张内容页）。同理，你可以完全跳过某些源页面，把选中的页面按任意顺序排列。

**骨架边界**：`scaffold --slides` 只是一个便利起点。如果最终计划需要重复使用源页面，或故事顺序与模板顺序不同，请手工复制/重排 `fill_plan.json` 中的条目，或直接从 `slide_library.json` 生成计划；不要让骨架输出束缚 deck 结构。

计划结构：

```json
{
  "schema": "template_fill_pptx_plan.v1",
  "source_pptx": "projects/source.pptx",
  "slides": [
    {
      "source_slide": 1,
      "purpose": "cover",
      "notes": "Speaker notes for this filled slide.",
      "transition": "fade",
      "replacements": [
        {
          "slot_id": "s01_sh4",
          "text": "New title"
        }
      ],
      "table_edits": [
        {
          "table_id": "s01_tbl3",
          "cells": [
            {"row": 0, "col": 0, "text": "Metric"},
            {"row": 0, "col": 1, "text": "Value"}
          ]
        }
      ],
      "chart_edits": [
        {
          "chart_id": "s01_ch4",
          "categories": ["A", "B"],
          "series": [
            {"name": "Series 1", "values": [10, 20]}
          ]
        }
      ]
    }
  ]
}
```

**逐幻灯片计划纪律**：

| 决策 | 规则 |
|---|---|
| `source_slide` | 在多条记录中重复同一值，即可把同一源版式复用于多张输出幻灯片；顺序自由，必须按目标故事排，而不是按源 deck 顺序 |
| `notes` | 可选的、口语化的讲者备注——见下文 **讲者备注**；写散文，不要照抄幻灯片上的文字 |
| `transition` | 可选的逐幻灯片切换效果；覆盖 `apply --transition` 默认值。接受效果名（`fade` / `push` / `wipe` / `split` / `strips` / `cover` / `random`），传 `none` 去掉切换，或 `{ "effect": "push", "duration": 0.6 }` |
| `replacements` | 尽量按 `slot_id` 定位；`shape_id` 与 `shape_name` 是兜底选择器 |
| `table_edits` | 可选的原生表格单元格编辑；尽量按 `table_id` 定位，`row` / `col` 从 0 起 |
| `chart_edits` | 可选的原生图表数据编辑；按 `chart_id` 定位，设置 `categories` 并提供一条或多条 `series` |
| 短文字 | 用于标签 / 章节名 / 目录项时，按槽位的几何与字号适配视觉容量；不要只依赖原占位文字长度 |
| 正文文字 | 可以比原文更自由，但段落数、视觉宽度、信息密度应贴近槽位的几何容量 |
| 空槽位 | 仅当源 deck 中存在真正的空占位时才使用 `scaffold --include-empty` |
| 原生表格 | 保持原表格的行 / 列数；本工作流编辑已有单元格，不改表格结构 |
| 原生图表 | 每条 `series` 的 `values` 列表长度必须等于分类数；本工作流编辑图表数据，不改图表样式 |
| 事实 | 每项实质内容都必须来自用户材料 |

**应用前的适配检查**：

- 封面：只替换标题 / 副标题 / 作者。
- 章节页：用短章节标签。
- 密集内容页：把材料压缩成与既有槽位容量匹配的要点。
- 装饰或图多页：避免把长文硬塞进标签大小的槽位。
- 重复源页面：每条重复记录都必须有独立的 purpose 与替换集合；除非重复版式恰好表达同一种修辞模式，否则避免视觉重复。
- 重排的源页面：确认新顺序读起来仍是连贯的故事；模板页码、装饰性章节标记与讲者备注必须同步更新到输出顺序。

**讲者备注（`notes` 字段）**——抽取自主流水线的"逻辑构建阶段"，按每张计划幻灯片压缩成一条：

每条 `notes` 值都是**纯粹的口语叙述**：只写演示者会大声说出来的话，这样即便这份 deck 之后走 `notes_to_audio.py`，同一份文字也仍然可用。备注负责解释和衔接；不能只是把幻灯片上的文字再念一遍。

| 规则 | 细节 |
|---|---|
| 长度 | 2–5 句自然语句，承载本页核心信息；封面 / 章节 / 结尾页可以只写一两句 |
| 过渡 | 用自然散文把页面之间的衔接写在开篇句里（如"在明确了背景之后……" / "Having framed X, let's turn to Y"）——严禁方括号标签如 `[过渡]` / `[Transition]` |
| 纯散文 | 不写 `#` 标题行，不写 `- ` 项目符号列表，不写 `要点：① …` / `Key points:` 之类的小标题行，不写 `时长：2分钟` / `Duration:` 之类的标注——嵌入备注会逐字保留，TTS 也会把它们念出来 |
| 数字可读性 | 当 TTS 直接读出拗口时改用文字（中文"百分之六十八"比"68%"更顺；纯英文整数与百分号没问题） |
| 单一语言 | 与 deck 语言一致；不要在一段备注里混用语言 |
| 绑定来源 | 每项实质内容都来自用户材料，与 `replacements` 同源 |

中文内容页的 `notes` 示例：

```json
"notes": "在看清整体市场格局之后，我们把镜头拉近到成都二手房的头部板块。当前挂牌均价同比上涨约百分之十二，但成交周期反而拉长到九十天以上，说明买方观望情绪在加重。这组数据是后面定价策略的基础，请重点留意。"
```

---

## Step 5：检查文字容量

在应用计划前运行基于数据的容量检查：

```bash
python3 ${SKILL_DIR}/scripts/template_fill_pptx.py check-plan "<project_dir>/analysis/slide_library.json" "<project_dir>/analysis/fill_plan.json" -o "<project_dir>/analysis/check_report.json"
```

解读报告：

| 警告类型 | 处理 |
|---|---|
| 短标签超出视觉宽度 | 改写得更短，或挑一个标签槽位更大的版式；默认不要缩小字号 |
| 标题过长 | 先尝试改写；只有最后手段才调字号 |
| 正文远长于源槽位 | 压缩、拆到另一张选中的页面，或挑一张更大的源页面 |
| 找不到目标 | 修复 `slot_id` / `shape_id`；**不要**应用该计划 |

**默认适配策略**：按视觉容量而非原始字符数来检查适配度。CJK 字符、拉丁字母、数字与标点占的视觉宽度都不同；旧占位文字只是弱信号。在 `capacity_visual_width` 存在时结合 `slots[].geometry` 与 `slots[].text_metrics.font_size_px` 一起判断，决定改写、拆分，还是换一张源版式。**不要**把"逐项缩小字号"当作默认策略——它会破坏模板的一致性。

---

## Step 6：应用计划

运行：

```bash
python3 ${SKILL_DIR}/scripts/template_fill_pptx.py apply "<project_dir>/sources/<source.pptx>" "<project_dir>/analysis/fill_plan.json" -o "<project_dir>/exports/<output.pptx>"
```

默认情况下 `apply` 会给每张克隆幻灯片一个 `fade` 切换（`0.5s`），因为大多数原生模板自带的 `<p:transition/>` 是空的——渲染出来就是"无动效"。用 `--transition <effect>`（`fade` / `push` / `wipe` / `split` / `strips` / `cover` / `random`）与 `--transition-duration <seconds>` 覆盖默认；传 `--transition none` 表示无动效；传 `--transition keep` 保留每张源幻灯片已有的切换。计划里某张幻灯片的 `transition` 字段会覆盖 CLI 为该幻灯片选定的值。

`apply` 会自动在文件名后追加时间戳。例如 `-o "<project_dir>/exports/demo.pptx"` 实际写入 `demo_YYYYMMDD_HHMMSS.pptx`。如果文件名已以 `_YYYYMMDD_HHMMSS` 结尾，则保持原样。

脚本行为：

| 行为 | 结果 |
|---|---|
| 克隆所选源幻灯片 | 在 PowerPoint 支持的范围内保留原始幻灯片设计、关系、图像、版式与动画 |
| 替换文字节点 | 文本框在 PowerPoint 中仍可编辑 |
| 写入 `notes` 字段 | 讲者备注嵌入为原生 PowerPoint 备注页 |
| 应用 `--transition` / 逐幻灯片 `transition` | 把原生 PowerPoint 页面切换写入每张幻灯片的 `<p:transition>` |
| 重建演示文稿幻灯片列表 | 输出 deck 仅包含计划中的幻灯片顺序 |
| 给 PPTX 文件名追加时间戳 | 与主 SVG→PPTX 导出约定保持一致 |
| 丢弃孤立的源部件 | 输出仅含所选页面及其仍引用的版式 / 媒体 / 图表（可达性剪枝） |

**动画策略**：模板填充会保留每张克隆幻灯片已有的对象动画 XML（本工作流不套用 SVG 流水线生成的对象动画默认）。页面切换是本工作流直接写入的唯一动效层；`apply` 默认加 `fade` 切换，避免填充后的 deck 沿用模板空白的"无动效"状态。可通过 `apply --transition` / 计划里逐幻灯片 `transition` 字段修改，或用 `--transition keep`（保留源）或 `--transition none`（去掉切换）选择退出。如果用户要求改对象级动画顺序 / 时机 / 效果，把它视作另一项独立的 PPTX 动画定制任务。

---

## Step 7：校验输出

运行一次轻量的可读性检查：

```bash
python3 ${SKILL_DIR}/scripts/source_to_md/ppt_to_md.py "<project_dir>/exports/<output.pptx>"
```

把回读的 Markdown 与抽取出的文件搬入 `<project_dir>/validation/`，让 `exports/` 仅保留最终交付物。

校验：

| 检查项 | 期望 |
|---|---|
| 输出文件名 | 以 `_YYYYMMDD_HHMMSS.pptx` 结尾 |
| 幻灯片数 | 等于 `len(fill_plan.slides)` |
| 关键标题文字 | 出现在抽取出的 Markdown 里 |
| 原生表格单元格 | 更新后的值出现在抽取出的 Markdown 表格里 |
| 原生图表数据 | 克隆图表的 XML 中含有更新后的标签 / 值 |
| 多行正文 | 保留期望的换行 / 段落断行 |
| 讲者备注 | `ppt_to_md.py` 能读取生成的 PPTX 而不报备注相关错误 |
| 找不到目标错误 | `template_fill_pptx.py apply` 未报此类错误 |

如果抽取出的文字正确但视觉溢出风险高，回到 Step 4 减少 `fill_plan.json` 中的文字量，再跑一次。

```markdown
## ✅ 模板填充完成

- [x] 从源 PPTX 抽取出 `slide_library.json`
- [x] `fill_plan.json` 仅挑选适合目标故事的页面
- [x] 运行了 `check-plan`，容量警告已解决或明确接受
- [x] 通过直接 OOXML 文字替换生成输出 PPTX
- [x] 当 `notes` 字段存在时，讲者备注已嵌入
- [x] `ppt_to_md.py` 可读性检查通过
```

---

## 当前边界

| 能力 | 状态 |
|---|---|
| 选择 / 重排 / 重复源幻灯片 | 支持 |
| 替换既有文本框中的文字 | 支持 |
| 编辑原生 PowerPoint 表格的单元格文字 | 支持 |
| 编辑原生 PowerPoint 图表的分类 / 系列数据 | 支持 |
| 保留原始视觉设计 | 通过直接克隆幻灯片部件支持 |
| 页面切换 | 通过 `apply --transition` 或逐幻灯片 `transition` 支持 |
| 替换图像 | v1 暂不支持 |
| 对象级入场动画 | v1 暂不支持；仅保留源中已有动画；改动画作为独立任务处理 |
| 编辑图表格式 / 坐标轴 / 图例布局 | v1 暂不支持 |
| 深度编辑 SmartArt | v1 暂不支持 |
| 自动视觉溢出检测 | v1 暂不支持；用幻灯片库槽位的文字容量判断代替 |
