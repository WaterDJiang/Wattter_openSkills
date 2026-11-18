---
description: Step 7 detail — 三命令流水线 + 动画/旁白可选 + 批注应用窗口
---

# Step 7：后期处理与导出 —— 详细

> 本文件承接 SKILL.md Step 7 的执行细节。

## 图像就绪 GATE

当 Step 5 把 ai 行留在 `Needs-Manual` 时：运行 7.1 之前，每个预期文件都必须存在于 `project/images/<filename>`。

> 若文件缺失：暂停，列出缺失文件名，让用户查看 `images/image_prompts.md`（每个 `### Image N:` 块直接可粘贴到 ChatGPT / Gemini / Midjourney；从 `image_prompts.json` 自动生成）以及放置位置 `project/images/<filename>`。全部到位后才继续 7.1。`finalize_svg.py` 和 `svg_to_pptx.py` 不检测缺失文件——带缺口继续会产出图片引用破损的 deck。

> ⚠️ 三个子步骤**一次只跑一个**——上一步必须成功再跑下一步。
> ❌ **绝不要**合并到单个代码块或 shell 调用里。

## 模板与内容导出硬闸口

所有项目在 7.1 前再次运行：

```bash
python3 ${SKILL_DIR}/scripts/validate_mirror_fidelity.py <project_path>
python3 ${SKILL_DIR}/scripts/validate_template_usage.py <project_path>
python3 ${SKILL_DIR}/scripts/validate_content_fidelity.py <project_path>
```

随后运行 SVG 通用检查；只有模板 `replication_mode: mirror` 时加 `--mirror-mode`：

```bash
python3 ${SKILL_DIR}/scripts/svg_quality_checker.py <project_path> --summary-only
# mirror template:
python3 ${SKILL_DIR}/scripts/svg_quality_checker.py <project_path> --mirror-mode --summary-only
```

复核用于捕获 SVG 的结构、品牌资产或内容漂移。没有适用契约的 validator 会自动 `SKIP`；任何 error 都必须回到 Executor 修复，禁止继续导出。

课程已声明 handoff 却返回 `SKIP` 时，先修复发现路径，不得跳过。正式课堂交付还运行 `validate_teaching_contract.py <bundle> --ready-for-class`，并按原大纲阅读实际教学证据；缺口未清的文件只可命名为 `_draft.pptx` 并附具体 gaps，不能报告“可直接上课”。仅回填已确认的讲师备注时，使用 `update_pptx_notes.py <source.pptx> <fixed_pages.json> --out <with-notes.pptx>`。保持原课件，核对逐页备注和原生页面。涉及教学约束或屏幕变更时回到分镜及制作链更新。不要因导出成功自动把 readiness 改为 ready。

存在分镜画面说明时，导出后按[构图兑现](../composition-realization.md)查看实际PPTX渲染并补审查证据；SVG预览、文字保真和可编辑性通过分别报告。

有 `teaching.reveal_after` 时，按锁定的独立题页/揭晓页实现并检查成品顺序；默认自动入场动画不能充当等学员回答后的揭晓。

## 三命令流水线（对应 [`../shared-standards.md`](../shared-standards.md) §5）

**7.0** —— 课程先按实际播放顺序导入来源备注。插页使用其设计行的 speaker_notes_ref。已有短讲师提示可先用于样章，补写后按同一页序重新导入。
```bash
python3 ${SKILL_DIR}/scripts/import_course_notes.py <course-handoff> <project_path>
```

**7.1** —— 拆分讲者备注：
```bash
python3 ${SKILL_DIR}/scripts/total_md_split.py <project_path>
```

**7.2** —— SVG 后期处理（图标嵌入 / 图片裁剪并嵌入 / 文字打平 / 圆角矩形转 path）：
```bash
python3 ${SKILL_DIR}/scripts/finalize_svg.py <project_path>
```

**7.3** —— 导出 PPTX（默认嵌入讲者备注）：
```bash
python3 ${SKILL_DIR}/scripts/svg_to_pptx.py <project_path>
# 输出（默认流模式）：
#   exports/<project_name>_<timestamp>.pptx           ← 原生 pptx（标准输出，读取 svg_output/）
#   exports/<project_name>_<timestamp>.pptx.editability.json ← 原生对象验收报告
#   backup/<timestamp>/svg_output/                    ← Executor SVG 源备份（始终写入）
#
# 加入 --svg-snapshot 可额外输出 SVG 图片预览版 pptx：
#   exports/<project_name>_<timestamp>_preview_noneditable.pptx ← 不可编辑视觉预览（读取 svg_final/）
```

> 原生 pptx 直接消费 `svg_output/`，以便转换器保留高保真图元（图标 `<use>` 占位、图片 `preserveAspectRatio` → `srcRect`、圆角矩形 `rx/ry` → `prstGeom roundRect`）。导出器随后检查 OOXML 中的原生形状、文本、组合和图片；整页图片化比例超过 50% 时硬失败。`svg_output/` 在 `backup/<timestamp>/` 的快照始终写入。`preview_noneditable` 只用于冻结视觉参考，不得交付为可编辑 PPTX。

> **段落可编辑性 vs 行保真度** —— 默认可合并的 dy 堆叠段落会合并为一个含多个 `<a:p>` 的可编辑 PowerPoint 文本框，提升正文编辑与 resize/reflow。仅当用户明确要求严格行布局保真或版式紧凑页面必须逐行独立文本框时，才加 `--no-merge`。合并检测器保守；混合版式文本回退为逐行独立文本框。

## 可选动画标志

默认已启用丰富的入场动画——仅当用户要求不同效果时调整：

- `-t <effect>` —— 页面切换。默认 `fade`。可选：`fade`/`push`/`wipe`/`split`/`strips`/`cover`/`random`/`none`。
- `-a <effect>` —— 元素级入场。默认 `auto`（按组 id 映射：chart→wipe，card-/step-/pillar-→fly，title/takeaway→fade；类图片 id `hero`/`figure-`/`image`/`img-`/`kpi` 在更丰富效果池 zoom/dissolve/circle/box/diamond/wheel 中循环）。传 `none` 禁用，传具体效果，或 `mixed` 启用旧 16 效果循环。需顶层 `<g id="...">` 组（Executor 已要求）。
- `--animation-trigger {on-click,with-previous,after-previous}` —— 启动方式（PowerPoint 动画窗格"开始"下拉）。默认 `after-previous`。
- `--animation-config <path>` —— 对象级边车文件。默认：存在 `<project_path>/animations.json` 时使用。
- `--auto-advance <seconds>` —— kiosk 自动播放。

## 可选自定义动画 / 旁白

**自定义动画**（用户要求为特定对象调整顺序/效果/时机时）：运行独立 [`../../workflows/customize-animations.md`](../../workflows/customize-animations.md)。默认导出已带全局入场动画；除非请求对象级定制，否则不创建 `animations.json`。

**录制旁白**（用户要求带旁白/视频导出时）：运行独立 [`../../workflows/generate-audio.md`](../../workflows/generate-audio.md)。AI 选旁白后端（默认 `edge`，或云端 provider），一次性问用户（后端+声音+语速+是否嵌入），执行 `notes_to_audio.py`，嵌入时用 `--recorded-narration audio` 重新导出。不要绕过工作流直接调 `notes_to_audio.py`——`--voice`/`--voice-id` 必需，工作流给出与语言/provider 相关的推荐。

完整效果列表、锚定逻辑与限制：[`../animations.md`](../animations.md)。

## 红线

> ❌ **绝不要**用 `cp` 代替 `finalize_svg.py`——finalize 执行多个关键处理步骤。
> ❌ **绝不要**为旧版/预览版 pptx 强制 `-s output`（PowerPoint 内部 SVG 解析器丢弃图标和圆角）。默认 auto-split 已提供高保真源。
> ❌ **绝不要**用 `--only`（抑制两个输出文件之一）。

## 导出后批注窗口

若用户提交了批注并要求应用（引用浏览器提示 `Changes saved to svg_output...` 或说 "apply my annotations" / "应用注解"）：运行 [`../../workflows/live-preview.md`](../../workflows/live-preview.md) Step 2 应用并重新导出。

**浏览器直接编辑**：用户可在预览中对文本/SVG 属性做分阶段编辑，仅点 **Apply changes** 后落到 `svg_output/`。若他们应用后要求 "re-export"，直接重跑 7.2–7.3。

**按需打开网页**：用户明确要求用网页预览 SVG 或在浏览器编辑时，运行 [`../../workflows/live-preview.md`](../../workflows/live-preview.md) Step 1。已运行则直接给 URL。

## 正式课程成品闸口

沿用[运行环境](../render-runtime.md)记录的解释器与绝对路径。实际渲染会重验环境；依赖失败、转换失败和渲染警告分别报告并保留原文，字体隔离使用 prepare_render_fonts.py，不临时使用 copy2。切换解释器或恢复任务时重新执行 --check。

按[逐页结构与成品验收](../page-realization.md)运行 `validate_page_realization.py --pptx --summary-only --out <新attempt文件>`，再用 `render_course_pptx.py` 渲染实际导出的PPT，逐页检查字体、换行、遮挡、裁切、越界，写render_review并用同一摘要选项运行 `--pptx --delivery`。0 error才可交付；任何缺失或未验证明确报告，SVG预览不能替代。修复重跑受影响页，旧证据保留。
