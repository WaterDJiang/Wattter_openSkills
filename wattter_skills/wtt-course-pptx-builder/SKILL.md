---
name: wtt-course-pptx-builder
description: >
  AI 驱动的多格式 SVG 内容生成系统。通过多角色协作，将源文档（PDF / DOCX / URL / Markdown）转换为高质量 SVG 页面并导出为 PPTX。
  支持品牌/版式/Deck 模板、AI 图像生成、网页图像搜索、按需网页预览编辑、图表校准、动画定制、旁白录制、视觉自检等。
  当用户提出以下需求时使用：(1) "create PPT" / "make presentation" / "生成 PPT" / "做 PPT" / "制作演示文稿"；
  (2) 模板相关："create template" / "create brand" / "创建模板" / "创建品牌"；
  (3) 图像相关："generate image" / "搜索图片" / "AI 生图"；
  (4) 后处理相关："verify charts" / "校准图表" / "customize animations" / "定制动画" / "visual review" / "视觉自检"；
  (5) 导出相关："export PPTX" / "导出 PPT" / "add narration" / "添加旁白"；
  (6) 恢复："继续生成" / "resume execution"
---

# 课程 PPT 构建器技能

> AI 驱动的多格式 SVG 内容生成系统。通过多角色协作将源文档转换为高质量 SVG 页面，并最终导出为 PPTX。

**核心流水线**: `源文档 → 创建项目 → [模板] → 策略师(规范 + 公式渲染 + HTML 背景渲染) → [图像获取] → 逐页生成 SVG → 质量检查 → 后期处理 → 导出`

**课程制作入口**：详尽讲师大纲先形成教学分镜和简短讲师提示，PPT 样章稳定后再按固定页扩写逐字稿；已有合法页表直接继承，不要求先写长稿。已有逐页画面说明时按[构图兑现](references/composition-realization.md)落实焦点、正文落位与关系，并检查实际渲染。独立处理大纲时按 [教学分镜扩展](references/teaching-contract.md) 锁原要求、示范、题面/揭晓与材料；只给普通内容源仍可按本流程制作。`spec_lock` 是视觉权威，不覆盖原大纲教学要求及锁定页表内容。

> [!CAUTION]
> ## 🚨 全局执行纪律（强制要求）
>
> **本工作流是一条严格的串行流水线。以下规则拥有最高优先级——违反任何一条都视为执行失败：**
>
> 1. **串行执行（SERIAL EXECUTION）** — 各步骤必须按顺序执行；前一步的输出是后一步的输入。一旦前置条件满足，相邻的非 BLOCKING 步骤可以连续进行，无需用户说"继续"
> 2. **BLOCKING = 硬停止（BLOCKING = HARD STOP）** — 标记为 ⛔ BLOCKING 的步骤需要完全停下；AI 必须等待用户明确回复后才能继续，绝不能替用户做任何决定
> 3. **只暂停未授权的关键取舍** — Step 1 路由有歧义或 Step 4 有影响成品的冲突及缺项时，暂停受影响工作。已授权方案沿用，明确委托的设计决定记录采用值后继续。
> 4. **进入前先过闸（GATE BEFORE ENTRY）** — 每个 Step 顶部都列出了前置条件（🚧 GATE），开始该 Step 前必须先校验
> 5. **禁止投机执行（NO SPECULATIVE EXECUTION）** — 禁止"预先准备"后续 Step 的内容（例如，在 Strategist 阶段就写 SVG 代码）
> 6. **禁止子代理生成 SVG（NO SUB-AGENT SVG GENERATION）** — Executor Step 6 的 SVG 生成是上下文相关的，必须由当前主代理端到端完成。禁止把页面 SVG 生成委派给子代理。**例外（大规模并行模式）**：当页数 ≥ 60 且满足 `design_system.md` + 锚点页（经人工审批）+ `generation_state.json` 段表 + `consistency_checker.py` 闸口全部齐备时，允许段级 worktree 会话并行生成（见 [`workflows/parallel-execute.md`](workflows/parallel-execute.md)）。此例外之所以成立，是因为 design_system + 锚点 + 一致性校验三者共同替代了单代理连续上下文所提供的跨页一致性。三者缺一，例外失效，回退单代理
> 7. **只允许逐页顺序生成（SEQUENTIAL PAGE GENERATION ONLY）** — 在 Executor Step 6 中，确认全局设计上下文后，SVG 页面必须以一次性连续过程逐页生成。禁止批量生成（例如一次 5 页）。**大规模并行模式下**：每段会话内部仍逐页顺序生成（段内不批量）；跨段并行由 worktree 隔离与段 disjoint 页集保证安全
> 8. **逐页读取执行锁** — 每张 SVG 前运行 `python3 ${SKILL_DIR}/scripts/extract_locked_values.py <project> --page <page_id>`，读取共用视觉值及本页锁定条目。首页、缺所需字段或检测到漂移时检查 `spec_lock.md` 对应内容，修改锁后重建缓存。
> 9. **SVG 必须手写，禁止脚本生成（SVG MUST BE HAND-WRITTEN, NOT SCRIPT-GENERATED）** — 每张 SVG 页面都由主代理直接逐页手写（参见规则 6 和 7）。禁止编写或运行 Python / Node / shell 脚本批量产出 SVG 文件——包括循环生成页面、数据模板化、或通过生成器发出——即便以"省 token"、"快速草稿"或"用户赶时间"为借口。脚本生成路径曾在特性分支上试过并被放弃：跨页视觉一致性依赖于带完整上游上下文的逐页手写，生成器脚本无法复现。**大规模并行模式下**：每张 SVG 仍由段会话（主代理级，非脚本）逐页手写——`design_system.md` 的骨架片段是"供复制粘贴的冻结片段"，不是"脚本模板"；段 agent 粘贴片段后仍逐页手写内容。脚本批量产出的禁令在两种模式下都不变
> 10. **页面禁止营销转化引导（NO MARKETING CTA ON SLIDES）** — 扫码进营销群、关注账号、转发有礼、报名咨询等推广文案移至讲者备注。教学任务所需的打开练习材料、复制示范链接、点击软件控件、提交作业、同伴分享必须保留在页面或随课材料；不能因为它们是祈使句就删除。`svg_quality_checker.py` check #12 仅报告疑似关键词，Executor 按教学目的复核：必要操作和主题讨论保留，营销转化移出页面。用户明确指定的转化页须在 `spec_lock.md` 声明。
> 11. **CHART 只借结构、不借皮肤（CHART STRUCTURE ONLY）** — `templates/charts/*.svg` 只提供图表 / 信息图的几何结构、标签与图例位置、关系表达和系列编码。只要前面已经选定品牌、layouts、deck 或用户模板，chart 的原始 `fill` / `stroke` / `stop-color` / 字体 / 渐变 / 阴影全部视为占位值；Executor 必须用 `spec_lock.colors`、`spec_lock.typography` 与 `spec_lock.visual_style` 重新着色和重构效果。禁止把 chart 默认配色带入成品。

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
| `${SKILL_DIR}/scripts/html_render.py` | HTML 背景渲染（图层化架构：HTML→PNG 背景层，基于清单，Playwright/Chromium） |
| `${SKILL_DIR}/scripts/image_gen.py` | AI 图像生成（多 provider） |
| `${SKILL_DIR}/scripts/svg_quality_checker.py` | SVG 质量校验（单页 spec_lock 合规；mirror 项目使用 `--mirror-mode`） |
| `${SKILL_DIR}/scripts/template_page_catalog.py` | 模板页面语义检索、canonical reference 解析、目录与项目 `page_layouts` 硬校验 |
| `${SKILL_DIR}/scripts/ensure_template_catalogs.py` | 为全部 Deck/Layout 生成或验证轻量 `page_catalog.json` 基线，不改原 SVG |
| `${SKILL_DIR}/scripts/variant_selection.py` | 为全部 Deck/Layout/Chart SVG 推导通用变体画像，并在语义等价候选中做可复现受控轮换 |
| `${SKILL_DIR}/scripts/template_capabilities.py` | 确定性分析 deck/layout 的位图角色、原生可编辑对象、文字容量、组件组与共享资产，生成通用能力 sidecar |
| `${SKILL_DIR}/scripts/validate_chart_mappings.py` | 校验 chart 全目录读取、逐页选型、SVG 映射、内容形态↔模板维度冲突、模板主题重着色契约 |
| `${SKILL_DIR}/scripts/validate_mirror_fidelity.py` | 逐页 mirror 保真硬闸口：仅允许修改文字内容，非文字结构、几何与图片身份发生变化即失败 |
| `${SKILL_DIR}/scripts/validate_template_usage.py` | `brand_shell` 角色级资产复用与背景 full-bleed 硬闸口 |
| `${SKILL_DIR}/scripts/validate_content_fidelity.py` | Handoff 可见文本保真硬闸口：锁定大纲不得缺项 |
| `${SKILL_DIR}/scripts/validate_asset_usage.py` | 校验 Deck/Free Route 隔离与 `page_assets` 实际来源标记 |
| `${SKILL_DIR}/scripts/match_content_forms.py` | 内容形态→模板查表匹配（`resolve` 列候选；chart 全局 / 页面变体 `--package` 包内）；词表 `templates/charts/content_forms.json` |
| `${SKILL_DIR}/scripts/validate_course_handoff.py` | 校验标准内容契约与可选设计增量，阻止页数、页序和 outline hash 漂移 |
| `${SKILL_DIR}/scripts/validate_teaching_contract.py` | 校验原大纲来源、要求映射、材料、备注与揭晓顺序；`--ready-for-class` 阻止缺材料却宣称可上课 |
| `${SKILL_DIR}/scripts/update_pptx_notes.py` | 固定页完成后把确认的讲稿写入现有 PPTX 副本，逐页验证备注、原生页面和页序 |
| `${SKILL_DIR}/scripts/import_course_notes.py` | 按 page_id 与实际 SVG 文件名导入既有讲师提示/逐字稿，保持教学动作与反馈 |
| `${SKILL_DIR}/scripts/bind_course_handoff.py` | 把语义设计意图绑定到已选模板包 canonical SVG 与全局 chart，输出审计提案 |
| `${SKILL_DIR}/scripts/derive_content_forms.py` | 从文件名+page_catalog 派生 layouts/decks 页面变体的内容形态，复核后并入 content_forms.json |
| `${SKILL_DIR}/scripts/consistency_checker.py` | 跨页一致性校验（比对锚点检测漂移；大规模并行路径用） |
| `${SKILL_DIR}/scripts/generation_state.py` | 页级进度管理（大规模并行路径的段/页状态与断点续传） |
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
| 完整 Deck | `${SKILL_DIR}/templates/decks/decks_index.json` | 仅在用户明确指定/要求查看 Deck 时查询；选中后只读该包 |
| 页面语义目录 | `<template_dir>/page_catalog.json` | 按用途 / 结构 / 数量 / 内容槽位查找页面，并取得可写入 `page_layouts` 的 canonical reference |
| 可视化模板 | `${SKILL_DIR}/templates/charts/charts_index.json` | 查询可用的 SVG 可视化模板（图表、信息图、示意图、框架图） |
| 图标库 | `${SKILL_DIR}/templates/icons/` | 参见 `${SKILL_DIR}/templates/icons/README.md`；按需用 `ls ${SKILL_DIR}/templates/icons/<library>/ \| grep <keyword>` 搜索图标 |
| HTML 背景风格 | `${SKILL_DIR}/templates/html-background-styles/_index.md` | 查询可用的 HTML 背景风格预设（图层化架构的背景层模板：cover/ending/chapter/theme） |
| 主题色板 | `${SKILL_DIR}/references/theme-palettes/_index.md` | 查询可用的 HEX 种子主题色板（HTML 背景 + SVG 文字层色源） |

> 三个模板索引的每条条目都自带 `kind` 与 `path`。索引按路由渐进读取：Free Route 不读 `decks_index.json`；Deck Route 只用它解析用户指定的一个 id。带语义页面目录的条目会暴露 `page_catalog` 路径；页面候选优先通过 `template_page_catalog.py ... search --compact` 查询，不把全目录灌入上下文。同一内容形态存在多个 SVG 时，明确的 `composition.topology/emphasis` 优先；未明确时只在语义等价池内做确定性受控轮换。mirror 与结构页不轮换。

## 独立工作流

按是否落在默认路径上分两层。默认 deck（无模板 / <60 页 / 有源材料）只会碰到第一组；第二组是边缘场景，按触发条件进入。

**主干——默认路径会触及**

| 工作流 | 路径 | 用途 |
|----------|------|---------|
| `live-preview` | `workflows/live-preview.md` | 仅在用户明确要求用网页预览 SVG 或在浏览器编辑时启动；也可按请求应用已提交的批注 |
| `resume-execute` | `workflows/resume-execute.md` | 阶段 B 入口——在另一个会话完成阶段 A（Step 1–5）后，在新会话中恢复执行（分阶段模式；仅当用户选了分阶段模式才进入） |
| `verify-charts` | `workflows/verify-charts.md` | 图表坐标校准——**仅当 deck 含数据图表**时，在 SVG 生成后运行；无图表页跳过 |

**按需——边缘场景触发**

| 工作流 | 路径 | 触发条件 |
|----------|------|---------|
| `topic-research` | `workflows/topic-research.md` | 用户只给主题、无源文件时，流水线前先抓网络资料 |
| `use-user-template` | `workflows/use-user-template.md` | 流程 2 入口——用户提供 `.pptx` 模板，分析设计身份后落到项目 `templates/`，可选入库 |
| `template-fill` | `workflows/template-fill-pptx.md` | 给定原生 PPTX 模板与源材料，直接 OOXML 回填文字，不走 SVG 转换 |
| `parallel-execute` | `workflows/parallel-execute.md` | **页数 ≥ 60** 时的大规模并行入口（锚点审批 + 分段 + worktree 并行 + 段校验） |
| `customize-animations` | `workflows/customize-animations.md` | **仅当用户明确要求**调整对象级动画顺序/效果/时机 |
| `visual-review` | `workflows/visual-review.md` | **仅当用户明确要求**逐页视觉复检；主流水线不主动调用 |
| `create-template` | `workflows/create-template.md` | 库资产创建——新建版式模板入库供未来流程 1 复用（非项目级使用） |
| `create-brand` | `workflows/create-brand.md` | 库资产创建——新建品牌预设入库（非项目级使用） |

---

## 工作流

### Step 1：流程确认与源内容处理

已有 PPTX、固定页基线和已完成的讲稿，且任务仅为回填讲师备注时，直接使用 `update_pptx_notes.py <source.pptx> <fixed_pages.json> --out <with-notes.pptx>`。这条入口从现有 PPTX 生成新副本，并核对原生页面、页序与备注。

🚧 **GATE**：用户已提供初始需求（主题 / 源文件 / 模板文件 / 文字描述——任何形式均可）。

⛔ **BLOCKING（仅当歧义时）**：显式 Deck 名称/路径 → 隔离的 Deck Route；附 `.pptx` → 用户模板流程；其余（含无模板信号/"都行"）→ Free Route。Free Route 不读取 Deck 索引，可在 `layout-led` / `html-led` / `full-free` 中按需选择。只有“想用模板但对象不明确”时追问。

**做什么**：先检测 `course_contract.json`；存在则按 `references/course-handoff-protocol.md` 校验并保留为内容真源。随后 1a 选三条流程之一；1b 把其他非 Markdown 源转成 Markdown。普通源材料仍可独立运行。

```
Read references/steps/step1-source.md
```

**✅ 检查点 —— 确认流程已选定、源内容就绪后，进入 Step 2。**

---

### Step 2：项目初始化

🚧 **GATE**：Step 1 已完成；源内容已就绪（Markdown 文件、用户提供的文字、或对话中描述的需求均为有效）。

**做什么**：`project_manager.py init --dir <课程工作区绝对路径>/projects` 建项目，记录返回的绝对路径；普通转换中间文件按 Step 2 导入。课程 handoff 整包复制到 `sources/course-handoff/`，保留源文件、材料和备注相对路径，验证复制后的包；不移动用户原始课程文件。无源文件（纯对话内容）跳过导入。

课程在批量制作前按[渲染运行环境](references/render-runtime.md)锁定 Skill/项目/Python 绝对路径并运行 `render_course_pptx.py --check`；字体配置确定后重验，不把依赖发现推迟到导出后。

```
Read references/steps/step2-init.md
```

**✅ 检查点 —— 确认项目结构创建成功，`sources/` 包含所有源文件，转换材料就绪。进入 Step 3。**

---

### Step 3：模板获取（按流程分支）

🚧 **GATE**：Step 2 已完成；项目目录结构就绪。按 Step 1a 选定的流程分支获取模板。

**三流程一句话**：
- **流程 1（库资产）**：显式 Deck id/路径 → 只读取并复制该 Deck，禁止读取或混用其他 Deck、Layout、HTML Background；包内页须精确匹配内容形态、教学用途和固定槽位，缺少合适结构时从全局 charts/icons 借结构并按该 Deck 重着色。非 Deck 请求只读所需 Layout/Brand/HTML Background 索引。
- **流程 2（用户 `.pptx`）**：⛔ BLOCKING 子选择（身份+结构复刻 / 仅身份提取），切到 [`use-user-template`](workflows/use-user-template.md) 工作流。
- **流程 3（Free Route，默认）**：不读取 Deck；按内容采用 `layout-led`、`html-led` 或 `full-free`，charts/icons 按需渐进检索。

> 三条流程一旦 `<project>/templates/design_spec.md` 就位，Step 4 起合流。选定前不读模板 design_spec/SVG（渐进式省 token）。

```
Read references/steps/step3-template.md
```

**✅ 检查点 —— 模板已复制（或融合/分析/跳过）到 `<project_path>/templates/`，进入 Step 4。**

---

### Step 4：策略师阶段（强制要求——不可跳过）

🚧 **GATE**：Step 3 已完成；已采用默认自由设计路径，或（若触发）模板文件已复制到项目中。

内部核对画布、页数、关键信息、风格、配色、图标、字体和用图。优先继承当前授权、已确认的交接和所选模板规范。⛔ **BLOCKING（仅差量）**：只有会改变成品且现有授权无法解决的选择才合并询问。用户委托设计取舍时记录采用值和来源后继续。

**做什么**：如有 handoff，在 Step 3 确定模板后先运行 `bind_course_handoff.py` 产出 `page_binding.json` 提案；Strategist 复核提案与差量确认，再产出 `design_spec.md` + `spec_lock.md` + `locked_values.json` + `chart_selection.json`。`page_binding.json` 不是新权威，`spec_lock.md` 仍唯一权威。

```
Read references/steps/step4-strategist.md
```

**✅ 检查点 —— 阶段交付物完成，自动进入下一步**：
```markdown
## ✅ 策略师阶段完成
- [x] 八项已核对，已授权值继承，关键差量已解决
- [x] 高级选项提示行已附加（分阶段 / 精修规范，默认关闭）
- [x] 设计规范与内容大纲已生成
- [x] 执行契约（spec_lock.md）已生成
- [x] Chart 选型审计（chart_selection.json）已生成并通过校验
- [ ] **下一步**：自动进入 [图像生成 / 执行器] 阶段
```

---

### Step 5：图像获取阶段（条件性）

🚧 **GATE**：Step 4 已完成；设计规范与内容大纲已生成且用户已确认。任何公式行已经带 `Acquire Via: formula` 和 `Status: Rendered`。仅当 Free Route 明确锁定了 HTML 背景页时，要求对应 `images/bg_*.png` 已就位、`html_background_manifest.json` 全 `Rendered-HTML`（或 `Fallback-Solid`）；缺失时先按下方补跑。Deck Route 使用本包资产或锁定的原生重建，不要求 HTML manifest。

**显式门控（省 ~60K token）**：若所有 §VIII 行都是 `user`/`formula`/`html`/`placeholder`（方案 A / 无 ai·web 图），**跳过整个 Step 5**——不读 image-base/image-generator/image-searcher/image-layout-* 这 5 个文件。仅当存在 `ai` 或 `web` 行才进入。

**做什么**：① 仅为明确锁定 HTML 背景的 Free Route 页面运行 `html_render.py`，其背景在 Step 6 前就位；其他页面跳过此项，Deck Route 禁止引入 HTML Background。② 若有 ai/web 行：读 `image-base.md` + 按需 `image-generator.md`/`image-searcher.md`，跑 `image_gen.py --manifest` / `image_search.py`，每行到终止状态。

```
Read references/steps/step5-image.md
```

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

**路径分支（按页数三档）**：

| 条件 | 路径 |
|---|---|
| 页数 ≥ 60 且 `design_system.md` 已生成 | **大规模并行**——切到 [`parallel-execute`](workflows/parallel-execute.md) 工作流（锚点审批→分段→worktree 并行→段校验→修复→拼接→导出；纪律 6/7 并行例外生效） |
| **30 ≤ 页数 < 60** | **序贯 + 页级状态（serial-with-state）**——单代理逐页手写，每页前后读写 `generation_state.json` 作权威页号（详见 step6-executor.md §serial-with-state） |
| 页数 < 30，或 `design_system.md` 缺失 | **单代理无状态**（默认）——逐页生成 |

**做什么**：读适用执行参考并按锁定路由预读选中的模板与图表。每页读取当前页锁值、教学分镜及结构计划，按路由制作 SVG，通过内容、教学材料、模板资产及 SVG 闸口后导入讲师提示。

> ⚠️ 仅主代理、逐页顺序生成、不批量——见全局纪律 Rule 6/7/9。

```
Read references/steps/step6-executor.md
```

**✅ 检查点 —— 确认所有 SVG 与备注均已完整生成并通过质量检查。直接进入 Step 7 后期处理**：
```markdown
## ✅ 执行器阶段完成
- [x] 所有 SVG 已生成到 svg_output/
- [x] svg_quality_checker.py 通过（0 错误）
- [x] 讲者备注已生成到 notes/total.md
```

> **图表页？** 若本 deck 含数据图表（柱状 / 折线 / 饼图 / 雷达 等），在 Step 7 之前运行独立 [`verify-charts`](workflows/verify-charts.md) 工作流进行坐标校准。AI 模型在把数据映射到像素位置时常常引入 10–50 px 的误差；verify-charts 可消除这一类错误。无图表页则跳过。

> **可视化自检（可选）？** 仅当用户明确要求在 SVG 上做逐页视觉复检（"跑一下视觉自检 / 视觉回看"、"visual review"、"check pages visually" 等）时，在 Step 7 之前运行独立 [`visual-review`](workflows/visual-review.md) 工作流。不要默认运行，也不要基于推断的模型能力或 deck 体量主动推荐——触发条件仅为用户请求。

---

### Step 7：后期处理与导出

🚧 **GATE**：Step 6 已完成；所有 SVG 已生成到 `svg_output/`；讲者备注 `notes/total.md` 已生成。

🚧 **图像就绪 GATE**（Step 5 有 `Needs-Manual` ai 行时）：每个预期文件必须存在于 `project/images/`；缺失则暂停让用户补，再继续——`finalize_svg.py`/`svg_to_pptx.py` 不检测缺失。

**做什么**：课程先导入来源备注，再执行三命令流水线，**一次只跑一个**（❌ 禁止合并）：
1. **7.1** `total_md_split.py`（拆讲者备注）
2. **7.2** `finalize_svg.py`（图标/图片嵌入、文字打平、圆角转 path）——❌ 禁用 `cp` 代替
3. **7.3** `svg_to_pptx.py`（导出原生可编辑 pptx，自动生成 `.editability.json` 并拒绝整页图片化 deck；默认嵌备注 + 入场动画）

> ❌ 正式交付禁止 `--only legacy`。`--svg-snapshot` 只生成文件名带 `preview_noneditable` 的视觉预览，不能作为可编辑 PPTX 交付。导出后若用户要应用批注，走 [`live-preview`](workflows/live-preview.md) Step 2。

```
Read references/steps/step7-export.md
```

**✅ 检查点 —— PPTX 已导出到 `exports/<project>_<timestamp>.pptx`，同目录 editability 报告 `ok=true`。课程还须按[逐页结构与成品闸口](references/page-realization.md)通过原生字段/结构/备注与实际Office渲染复核，才能报告交付通过。**

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

- **故障排查**：遇到生成问题（布局溢出、导出错误、图像空白等）时，查阅 [`scripts/docs/troubleshooting.md`](scripts/docs/troubleshooting.md) 中的已知解决方案
