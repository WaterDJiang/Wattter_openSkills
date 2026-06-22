---
description: 项目级用户 PPTX 模板工作流——用户以 .pptx 形式提供模板，skill 分析其设计身份后落到当前项目的 templates/，不入库；末尾可选入库
---

# 使用用户模板工作流

> **目的**：用户在 SKILL.md Step 1 流程闸口选了**流程 2**（使用用户提供的模板），或开场附带一份 `.pptx` 模板 + 内容材料。本工作流分析该 PPTX 的设计身份，按用户选择的深度落到 `<project>/templates/`，供下游 Strategist + Executor 使用。产物**默认不入库**——末尾可选地保存为可复用库模板。

> **与 [`create-template.md`](./create-template.md) 的区别**：`create-template.md` 为**全局库**生成可复用模板（产物落 `templates/<kind>/<id>/`，强制注册索引，带 `[TEMPLATE_BRIEF_CONFIRMED]` 闸口）。本工作流是**项目级一次性**使用——产物落 `<project>/templates/`，不污染库，不入库除非用户明确要求。复刻深度由用户按项目选择。

> **调用的角色**：身份+结构路径调 [Template_Designer](../references/template-designer.md)（项目模式）；仅身份路径由当前主代理直接写身份段。

## 何时运行

| 触发 | 示例 |
|---|---|
| Step 1 流程闸口选了流程 2 | "用流程 2" / "用我提供的模板" |
| 开场附 `.pptx` + 内容材料 | "用这份 pptx 做模板，内容是附件 report.pdf" |
| 用户给出 `.pptx` 路径 + "套这份模板"语义 | "套这份公司模板做新产品介绍" |

**前置条件**：用户已提供一份 `.pptx` 模板文件（在 Step 2 `import-sources` 时随内容源一起进入 `<project>/sources/`）。`.pptx` 是**设计参考**，不是内容源——内容源单独走 SKILL.md Step 1 的源转换。

---

## Step 1：PPTX 设计分析

🚧 **GATE**：`<project>/sources/` 中已有用户提供的 `.pptx` 模板文件。

运行统一的 PPTX 分析脚本（与 `create-template.md` type-A 同一工具）：

```bash
python3 ${SKILL_DIR}/scripts/pptx_template_import.py "<project_path>/sources/<user_template>.pptx"
```

产物（默认落在 `/tmp/pptx_template_import/` 下的临时工作区）：

- `manifest.json`——**事实来源**：幻灯片尺寸、主题色（`a:clrScheme`）、字体（`a:fontScheme` major/minor Latin + EastAsia）、各 master 主题摘要、资产清单、占位元数据、SVG 文件路径、页面类型候选
- `summary.md`——快速扫读摘要（不作为权威事实源）
- `assets/`——抽取的可复用图像资产
- `svg/master_*.svg` / `svg/layout_*.svg`——deck 共享视觉语言（背景、页眉页脚、装饰条）
- `svg/slide_NN.svg`——每张幻灯片独有内容
- `svg-flat/slide_NN.svg`——自包含预览视图

**读取顺序**（进入 Step 2 前读完）：

1. `manifest.json`（事实元数据：尺寸、主题色、字体、资产、版式、master）
2. `svg/master_*.svg` 与 `svg/layout_*.svg`——共享视觉语言，先于幻灯片 SVG 读
3. `svg/inheritance.json`——幻灯片 ↔ layout/master 对应关系
4. 导出的 `assets/`
5. `svg/slide_NN.svg`——页面专属内容（构图节奏、密度）
6. `summary.md` 仅作快速定位；不清楚处回到 `manifest.json`

> ⚠️ **永久不要直接读取/打开图像文件**——所有图像信息来自 `manifest.json` 的资产清单或 `assets/` 列表。

**✅ 检查点**：已读完 manifest + master/layout SVG，掌握了主题色、字体、装饰母题、画布尺寸。进入 Step 2。

---

## Step 2：复刻深度子选择

⛔ **BLOCKING**：向用户呈现两个深度选项并等待明确选择。这是本工作流唯一的硬确认点。

| 选项 | 行为 | 产物 | 适合 |
|---|---|---|---|
| **A. 身份+结构复刻** | 调 Template_Designer（项目模式）重建 SVG 版式清单 + 完整 `design_spec.md` | `<project>/templates/design_spec.md` + `01_cover.svg` / `02_chapter.svg` / `03_content.svg` / `04_ending.svg` 等 | 用户希望保留原 PPTX 的版式骨架，Executor 继承结构 |
| **B. 仅身份提取** | 主代理直接写身份段 `design_spec.md`（配色/字体/Logo/语气/图标风格） | `<project>/templates/design_spec.md`（仅识别段，无 SVG 清单） | 用户只要原 PPTX 的"视觉气质"，版式由 Strategist 自由设计 |

**推荐信号**：

- 原 PPTX 版式精致、用户明确要"保留版式" → 推荐 A
- 原 PPTX 只是参考气质、内容结构差异大、或用户要"灵活构建" → 推荐 B
- 拿不准 → 推荐 B（更轻、更快，后续仍可走 `create-template.md` 入库做完整复刻）

用户选定后进入对应 Step 3a 或 3b。

---

## Step 3a：身份+结构复刻（选项 A）

> **前置条件**：Step 2 选了 A。

切换到 Template_Designer 角色（**项目模式**）：

```markdown
## [角色切换：Template_Designer（项目模式）]
📖 阅读角色定义：references/template-designer.md
📋 当前任务：基于 Step 1 分析包，为当前项目重建 SVG 版式清单 + design_spec.md，产物落 <project>/templates/
```

**项目模式与库模式的关键差异**（见 [`template-designer.md`](../references/template-designer.md) §角色范围的项目模式说明）：

- **输出位置**：`<project>/templates/`，**不是** `templates/<kind>/<id>/`
- **不调 `register_template.py`**——入库由 Step 4 的可选步骤决定
- **不强制 `[TEMPLATE_BRIEF_CONFIRMED]` 闸口**——Step 2 的深度选择已是对方向的确认；但仍需在生成前向用户呈现简报（主题色/字体/复刻模式/页面清单）并获确认，复刻模式默认 `standard`
- **其余生成逻辑不变**：复用 `create-template.md` Step 4 的 standard/fidelity/mirror 复刻规则、雪碧图保留规则、`design_spec.md` 仅性格骨架

向角色传入 Step 1 的分析包（最终简报 + `manifest.json` + `assets/` + `svg/` 引用）。

**产出**：

- `<project>/templates/design_spec.md`——完整 spec（识别 + 结构 + 页面清单）
- `<project>/templates/01_cover.svg`、`02_chapter.svg`、`03_content.svg`、`04_ending.svg` 等——SVG 版式清单

**校验**（在 `<project>/templates/` 上跑）：

```bash
python3 ${SKILL_DIR}/scripts/svg_quality_checker.py "<project_path>/templates" --template-mode --format <canvas_format>
```

`error` 必须修复；`warning` 能修则修。

**✅ 检查点**：SVG 版式清单 + `design_spec.md` 已落到 `<project>/templates/` 并通过校验。进入 Step 4。

---

## Step 3b：仅身份提取（选项 B）

> **前置条件**：Step 2 选了 B。

主代理直接写一份身份段 `design_spec.md` 到 `<project>/templates/`。结构对齐 [`templates/design_spec_reference.md`](../templates/design_spec_reference.md) 的识别段，但**只写识别部分**（配色 / 字体 / Logo / 语气 / 图标风格），不含结构段（画布/页面结构/SVG 清单）——结构留给 Strategist 在 SKILL.md Step 4 自由设计。

**身份段内容**（全部源自 Step 1 的事实，不凭空编造）：

| 段 | 内容 | 来源 |
|---|---|---|
| 配色方案 | 主色/辅色/强调色/中性色 HEX | `manifest.json` 主题色 + `svg/master_*.svg` 主导 fill |
| 字体方案 | 标题/正文字体栈（PPT-safe 收尾） | `manifest.json` 字体；若非预装字体，按 `strategist.md §g` 映射到最近预装族并标注 |
| Logo / 品牌资产 | 若 `assets/` 中有 Logo，复制到 `<project>/templates/` 并引用 | `assets/` |
| 语气 | 一句话描述（如"稳重、克制、数据驱动"） | 主代理从视觉语言推断，用户可在 Step 4 修订 |
| 图标风格 | 描边/填充/双色调，单一库 | 主代理从视觉语言推断 |

**frontmatter**（供下游 Strategist 识别这是身份段）：

```yaml
---
kind: brand
brand_id: <project_name>_user_template
summary: <一句话，源自原 PPTX 视觉气质>
primary_color: "<HEX>"
source: user-provided-pptx
---
```

> `kind: brand` 使 Strategist 把识别段锁定为权威、结构保持自由——与 SKILL.md Step 3 的 brand 派发行为一致。

**✅ 检查点**：`<project>/templates/design_spec.md` 仅含识别段，所有 HEX/字体来自 Step 1 事实。进入 Step 4。

---

## Step 4：可选入库

> **前置条件**：Step 3a 或 3b 已完成，产物在 `<project>/templates/`。

询问用户是否把这份模板保存为**可复用库模板**供未来项目使用。

| 用户选择 | 操作 |
|---|---|
| 入库 | 选 kind（3a→deck/layout，3b→brand）→ `cp -r <project>/templates/* ${SKILL_DIR}/templates/<kind_dir>/<id>/` → `python3 ${SKILL_DIR}/scripts/register_template.py <id> --kind <kind>` → 该模板随后出现在流程 1 菜单 |
| 不入库 | 跳过；产物留在 `<project>/templates/`，仅当前项目使用 |

**入库时的 kind 选择**：

- Step 3a 产物（含 SVG 版式清单）：`deck`（含识别）或 `layout`（仅结构，若识别段不通用）
- Step 3b 产物（仅身份）：`brand`

**入库时的 id**：询问用户一个 ASCII slug 或中文品牌名（文件系统安全）；若用户未指定，用 `<project_name>_user_template`。

> 入库后，该模板即被 `register_template.py` 注册到对应 `*_index.json`，未来在流程 1 的统一菜单中可选。

**✅ 检查点 —— 本工作流完成，回到主流水线 SKILL.md Step 4（策略师）**：
```markdown
## ✅ 用户模板工作流完成
- [x] PPTX 已分析（manifest + master/layout SVG）
- [x] 复刻深度已确认（A 身份+结构 / B 仅身份）
- [x] 产物已落到 <project>/templates/
- [x] 入库选项已处理（入库 / 不入库）
- [ ] **下一步**：自动进入 SKILL.md Step 4（策略师阶段）
```

---

## 硬规则

- ❌ **不要**运行 `template_fill_pptx.py`——那是 OOXML 文本回填（[`template-fill-pptx.md`](./template-fill-pptx.md)），不是设计身份分析
- ❌ **不要**运行 `pptx_to_svg.py` 直接把 PPTX 转成 SVG 当模板——`pptx_template_import.py` 的产物是**分析参考**，Template_Designer（3a）或主代理（3b）重建为干净模板，不逐字翻译
- ❌ **不要**凭空编造主题色/字体——所有身份字段必须源自 `manifest.json` 或 `svg/master_*.svg` 的事实
- ⚠️ **PPT-safe 字体收尾**：身份段的字体栈必须以预装字体收尾（Microsoft YaHei / SimHei / Arial / Georgia 等），否则 PPTX 降级到 Calibri——见 [`strategist.md §g`](../references/strategist.md)
- ⚠️ **EMF/WMF 矢量资源**：若原 PPTX 含 EMF/WMF，`pptx_template_import.py` 会按本地工具链能力处理；分析阶段若失败，向用户报告并建议改用 3b 仅身份路径
