---
description: Step 6 detail — Executor 逐页 SVG 生成（三档路径 + serial-with-state + 图层化 + 质量闸口）
---

# Step 6：执行器阶段 —— 详细

> 本文件承接 SKILL.md Step 6 的执行细节。SKILL.md 只保留 GATE + 三档路径表 + 检查点。

进入本步后，读本 deck 已锁定 `mode` + `visual_style` 的执行参考（来自 `spec_lock.md`）：

```
Read references/executor-base.md                  # 必读：通用指南
Read references/shared-standards.md               # 必读：SVG/PPT 技术约束
Read references/modes/<locked-mode>.md            # 叙事骨架（spec_lock.md `mode`）
Read references/visual-styles/<locked-style>.md   # 美学风格（spec_lock.md `visual_style`）
```

> 若 `mode: custom` 或 `visual_style: custom`，跳过该预设文件，改用 `spec_lock.md` 中的 `mode_behavior` / `visual_style_behavior`。不要通配 `modes/` 或 `visual-styles/`。

## 单代理 + 页级状态子模式（serial-with-state）

> **启动条件**：30 ≤ `design_spec.md §IX` 总页数 < 60。该子模式**叠加**于下方全部步骤之上——主代理在任何下游动作之前必须先把页级状态机建好。

**问题陈述**：LLM 在 30+ 页 deck 的同一会话内会因上下文压缩而"忘记"已经生成过哪一页、§IX 里这一页的标题是什么、配色还锁不锁。serial-with-state 子模式把页号权威从"模型记忆"搬到一个 JSON 状态文件，单代理走"读状态 → 生成 → 写状态"循环，从根本上掐掉漏页、跳号、重复。

**核心循环**：

```bash
# 1. 进入 Step 6 立即初始化（Step 4 §IX 的 N 即 design_spec 总页数）
python3 ${SKILL_DIR}/scripts/generation_state.py init <project_path> --total <N> --threshold 60
# 即使 N < 60，parallel_mode 也会自动 = false，segments 留空 → 文件仅承担"页级进度记账"职责

# 2. 每张 SVG 前：
P=$(python3 ${SKILL_DIR}/scripts/generation_state.py next-pending <project_path>)
# P 是权威页号（形如 P<NN>）。在响应文本顶部输出一行：
#   [Page P<NN> of N total | current page execution lock]

# 3. 标记为 generating（写入 svg_output 之前）
python3 ${SKILL_DIR}/scripts/generation_state.py mark-page <project_path> P<NN> generating

# 4. 写入 svg_output/<NN>_<name>.svg 后立即：
python3 ${SKILL_DIR}/scripts/generation_state.py mark-page <project_path> P<NN> done

# 5. 若中途生成失败：
python3 ${SKILL_DIR}/scripts/generation_state.py mark-page <project_path> P<NN> failed

# 6. 单页 ≤3 次仍失败 → 升级 needs-manual，不阻塞 deck：
python3 ${SKILL_DIR}/scripts/generation_state.py mark-page <project_path> P<NN> needs-manual
```

**生成顺序的硬要求（每页前脑里三核对）**——响应文本中显式写出三条核对结论：

- **核对 1**：`current page = generation_state.next-pending` 的输出（不能凭记忆数）
- **核对 2**：`filename = <NN>_<name>.svg`，与上一行 SVG 序号连续递增
- **核对 3**：`<name>` 严格匹配 `design_spec.md §IX` 该页标题

**阶段性 checkpoint（防上下文漂移）**：

| 触发条件 | 动作 |
|---|---|
| 每完成 10 页 done | `generation_state.py status` + `generation_state.py note "<...> done"` |
| 30 页以上 deck 每 5 页 done | 同上（更密） |


**异常处理**：

| 场景 | 第一动作 |
|---|---|
| 对话上下文被压缩 | `status` 后 `next-pending`，从拿到的 P<NN> 续——禁止凭 §IX 顺序重新数 |
| 用户切新会话 `继续生成 projects/<name>` | 走 [`../../workflows/resume-execute.md`](../../workflows/resume-execute.md)；`generation_state.json` 存在则沿用 |
| `next-pending` 与预期不一致（漏页） | 打印 `warning: skipped page detected`，回填缺页再续 |

**视觉构建阶段结束前对齐校验**：

```bash
python3 ${SKILL_DIR}/scripts/generation_state.py status <project_path>
python3 ${SKILL_DIR}/scripts/svg_quality_checker.py <project_path> --summary-only   # 批量用 summary 模式省 token
```

主代理额外做"三方对齐"显式核验（响应中列一张表）：`spec_lock.md page_rhythm` PNN 列表 vs `generation_state.json pages` PNN 列表 vs `svg_output/<NN>_*.svg` 实际文件。不一致则补齐。

**与并行路径的关系**：本子模式不创建分段design-system锚点（课程内容样章仍按[逐页落实](../page-realization.md)冻结）、**不**调用 `design_system.md`、**不**分 `segments`。`parallel-execute.md` 不受本子模式影响。

**实现说明**：
- `mark-page` 的所有权校验在 `parallel_mode=False AND segments=[]` 时自动绕过，无需 `--segment`。
- `next-pending` 同时输出 `pending` 与 `failed` 页——失败页可循环重试。
- `note <project> "<message>"` 子命令写带时间戳的 checkpoint 备注。

## 设计参数确认 / 预读 / 逐页生成

**设计参数确认（强制）**：在生成第一张 SVG 之前，从规范中输出关键设计参数（画布尺寸、配色方案、字体方案、正文字号）。详见 [`../executor-base.md`](../executor-base.md) §2。

**生成前批量预读（强制）**：先读 `page_binding.route` 与 `chart_selection.json`，再批量预读 `spec_lock.page_layouts/page_charts/page_assets` 已选中的不同 SVG，以及 Strategist 在本项目执行计划中复核过的同 Deck 视觉参考。后者不等于精确版式绑定。不得预读完整 `page_catalog`、备用 chart、其他 Deck 或未选中的 Layout。Chart SVG 只取结构；配色/字体/效果全来自已锁定的主题。详见 [`../executor-base.md`](../executor-base.md) §1.0。

`variant_policy` 只解释 Strategist 为什么选择这些 SVG；Executor 不消费候选池，也不在生成阶段重新轮换。每页必须严格使用 `spec_lock.page_layouts/page_charts` 的最终值。

**模板落实证据**：按本页 `page_realization.json` 保留层级、对应关系和阅读路径。源 SVG 与成品证据由检查器生成审阅视图。无课程交接时可继续用简短模板使用记录。

**构图兑现（所有路由）**：存在原分镜画面说明时，按[构图兑现](../composition-realization.md)逐页读取本页正文、原意图与已锁计划；生成后在现有审查记录补实际证据，不能只核对模板名。

**逐页读取锁值**：运行 `python3 ${SKILL_DIR}/scripts/extract_locked_values.py <project> --page <page_id>`。只用返回的共用样式与当前页条目，按需补读锁和源 SVG。

> ⚠️ **仅主代理**：SVG 生成必须留在当前主代理——页面设计依赖完整上游上下文。不要委派给子代理。
> ⚠️ **生成节奏**：在同一连续上下文中逐页、逐张、按顺序生成。不要批量（例如 5 张一组）。

**图层化生成（按 route）**：Deck Route 使用选定包及锁定模式的背景/视觉壳，禁止引入 HTML Background；`themed_rebuild` 可用原生形状重建同 Deck 视觉语言，不能冒称资产保真。Free Route 中使用 HTML 背景的页面为 [全幅 HTML-PNG 背景层（`<image>` 首子元素，包在 `<g id="bg-<template>">`）] + [SVG 文字/内容层叠加]；PNG 来自 `spec_lock.html_backgrounds`。这些页的 cover/ending/chapter 文字按 manifest `text_slots` 放置（见 [`../executor-base.md`](../executor-base.md) §3.3）；其他页面按锁定背景和内容关系构建。详见 [`../shared-standards.md`](../shared-standards.md) §4。

**视觉构建阶段**：SVG 页面在一次连续过程中逐页生成 → `<project_path>/svg_output/`

## 质量检查闸口（强制）

所有 SVG 生成完毕后、批注处理与讲者备注之前：

```bash
python3 ${SKILL_DIR}/scripts/validate_mirror_fidelity.py <project_path>
python3 ${SKILL_DIR}/scripts/validate_template_usage.py <project_path>
python3 ${SKILL_DIR}/scripts/validate_content_fidelity.py <project_path>
python3 ${SKILL_DIR}/scripts/validate_asset_usage.py <project_path>
python3 ${SKILL_DIR}/scripts/validate_chart_mappings.py <project_path>
python3 ${SKILL_DIR}/scripts/svg_quality_checker.py <project_path> --summary-only   # 批量看摘要；单页 fail 去掉 flag 看明细
# replication_mode: mirror 时，上一条 SVG checker 改为：
python3 ${SKILL_DIR}/scripts/svg_quality_checker.py <project_path> --mirror-mode --summary-only
# 大规模并行路径额外跑跨页一致性检查：
python3 ${SKILL_DIR}/scripts/consistency_checker.py <project_path> --against-anchors
```

- `validate_mirror_fidelity.py` 仅检查 `page_render_modes=mirror` 的页面；旧项目缺失该段时维持整本 mirror 的兼容行为。
- `validate_template_usage.py` 按 `page_shell_requirements` 检查 `brand_shell` 的全部必需角色；`background` 必须使用锁定模板资产并 full-bleed，禁止用通用背景加角标冒充模板壳。缺少任一必需角色时必须修页或改用 `themed_rebuild`。
- `validate_content_fidelity.py` 检查 handoff `slide_text` 的结构化可见叶文本；旧 `raw_markdown` 作者说明跳过并警告，其他缺项仍硬失败。输入明确有 handoff 时 `SKIP` 是发现失败，先修路径。
- 课程教学分镜同时运行 `validate_teaching_contract.py <bundle>`；按 source_coverage.md 对原要求逐条阅读实际页/示范/练习证据。页号和文字命中不等于原教学目标兑现。导出课堂交付版另加 `--ready-for-class`；缺口只允许交付注明 draft 的样稿。
- `validate_asset_usage.py` 检查 Deck/Free Route 隔离，并核对 `page_assets` 声明与 SVG 的 `data-wtt-source` 标记；声明了模板/chart 资产却未实际使用时硬失败。
- 存在分镜画面说明时，所有路由按[构图兑现](../composition-realization.md)核对实际页面。Deck Route 另逐页查看实际渲染与逐页结构计划：先检查代表性的示范、操作或练习页，再完成全套检查；最终用 Step 7 的实际 PPTX 渲染补齐证据。核对第一眼焦点、文本层级、动作/产出定位和阅读顺序，不能把同尺寸文本框堆叠或页头换色当作模板优化通过。结构检查通过不代替此项；未取得真实渲染时写明视觉未验证。
- `--mirror-mode` 保留 XML、画布、图片引用、动画与 CTA 检查，但不要求 canonical 模板改造成通用分层背景；必须与 mirror fidelity validator 配套，不能单独替代保真闸口。
- 任何 `error`（mirror 结构漂移、chart 映射 / 主题继承错误、禁用 SVG 特性、viewBox 不匹配、spec_lock 漂移等）必须先修复——回到视觉构建阶段重生成该页再跑检查。
- `consistency_checker` flagged 页（漂移超阈值）：大规模并行路径下进修复循环（≤3 次，超限 `needs-manual`）；单代理路径下能修则修。
- `warning`（低分辨率图、不安全字体尾部等）：能修就修，否则放行。
- 针对 `svg_output/` 运行（不要在 `finalize_svg.py` 之后——finalize 会重写 SVG 并掩盖违规）。

**讲者备注阶段**：有上游备注用 `import_course_notes.py <bundle> <project_path>` 导入，保留动作与反馈；仅有简短分镜提示时先用于样稿，完整稿按稳定页面后补。无上游稿的普通演示才生成摘要，见 executor-base §8。

## 课程逐页结构硬闸口

课程 Deck/Layout 按[逐页结构与成品验收](../page-realization.md)执行本页结构计划。生成后运行 `validate_page_realization.py <project> --summary-only --out <evidence.json>`。完整练习、示范、长句比较、多步流程和量规用实际内容样章验证，沿用已有有效审批。
