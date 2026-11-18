# PPT Master Toolset

This directory contains user-facing scripts for conversion, project setup, direct PPTX template filling, SVG processing, export, recorded narration, and image generation.

## Directory Layout

- Top-level `scripts/`: runnable entry scripts
- `scripts/source_to_md/`: source-document → Markdown converters (`pdf_to_md.py`, `doc_to_md.py`, `excel_to_md.py`, `ppt_to_md.py`, `web_to_md.py`)
- `scripts/image_backends/`: internal provider implementations used by `image_gen.py`
- `scripts/tts_backends/`: internal TTS provider implementations used by `notes_to_audio.py`
- `scripts/template_import/`: internal PPTX reference-preparation helpers used by `pptx_template_import.py`
- `scripts/svg_finalize/`: internal post-processing helpers used by `finalize_svg.py`
- `scripts/docs/`: topic-focused script documentation
- `scripts/assets/`: static assets consumed by scripts

## Quick Start

Typical end-to-end workflow:

```bash
python3 scripts/source_to_md/pdf_to_md.py <file.pdf>
# or
python3 scripts/source_to_md/ppt_to_md.py <deck.pptx>
python3 scripts/source_to_md/excel_to_md.py <workbook.xlsx>
python3 scripts/project_manager.py init <project_name> --format ppt169 --dir <课程工作区绝对路径>/projects
python3 scripts/project_manager.py import-sources <project_path> <source_files...> --move
python3 scripts/template_page_catalog.py <project_path> validate-project
python3 scripts/validate_asset_usage.py <project_path> --preflight
python3 scripts/validate_mirror_fidelity.py <project_path>
python3 scripts/validate_template_usage.py <project_path>
python3 scripts/validate_content_fidelity.py <project_path>
python3 scripts/validate_asset_usage.py <project_path>
python3 scripts/svg_quality_checker.py <project_path> --mirror-mode --summary-only --format ppt169
python3 scripts/validate_chart_mappings.py <project_path>
python3 scripts/total_md_split.py <project_path>
python3 scripts/finalize_svg.py <project_path>
python3 scripts/animation_config.py scaffold <project_path>  # optional object-level animation overrides
python3 scripts/svg_to_pptx.py <project_path>
```

Repository update:

```bash
python3 scripts/update_repo.py
```

## Script Index

| Area | Primary scripts | Documentation |
|------|-----------------|---------------|
| Conversion | `source_to_md/pdf_to_md.py`, `source_to_md/doc_to_md.py`, `source_to_md/excel_to_md.py`, `source_to_md/ppt_to_md.py`, `source_to_md/web_to_md.py` | [docs/conversion.md](./docs/conversion.md) |
| Project management | `project_manager.py`, `batch_validate.py`, `generate_examples_index.py`, `error_helper.py`, `pptx_template_import.py`, `template_fill_pptx.py` | [docs/project.md](./docs/project.md) |
| Course handoff | `validate_course_handoff.py`, `bind_course_handoff.py`, `validate_content_fidelity.py`, `validate_asset_usage.py` | `../references/course-handoff-protocol.md` |
| SVG pipeline | `validate_mirror_fidelity.py`, `validate_template_usage.py`, `validate_chart_mappings.py`, `validate_pptx_editability.py`, `finalize_svg.py`, `svg_to_pptx.py`, `total_md_split.py`, `svg_quality_checker.py`, `template_page_catalog.py`, `ensure_template_catalogs.py`, `template_capabilities.py`, `animation_config.py`, `notes_to_audio.py` | [docs/svg-pipeline.md](./docs/svg-pipeline.md) |
| Spec maintenance | `update_spec.py` | [docs/update_spec.md](./docs/update_spec.md) |
| Image tools | `image_gen.py`, `latex_render.py`, `analyze_images.py`, `gemini_watermark_remover.py` | [docs/image.md](./docs/image.md) |
| Repo maintenance | `update_repo.py` | README install/update section |
| Troubleshooting | validation, preview, export, dependency issues | [docs/troubleshooting.md](./docs/troubleshooting.md) |

## High-Frequency Commands

Conversion:

```bash
python3 scripts/source_to_md/pdf_to_md.py <file.pdf>
python3 scripts/source_to_md/ppt_to_md.py <deck.pptx>
python3 scripts/source_to_md/doc_to_md.py <file.docx>
python3 scripts/source_to_md/excel_to_md.py <workbook.xlsx>
python3 scripts/source_to_md/web_to_md.py <url>
```

Project setup:

```bash
python3 scripts/project_manager.py init <project_name> --format ppt169 --dir <课程工作区绝对路径>/projects
python3 scripts/project_manager.py import-sources <project_path> <source_files...> --move
python3 scripts/project_manager.py validate <project_path>
```

Template source import:

```bash
python3 scripts/pptx_template_import.py <template.pptx>
python3 scripts/pptx_template_import.py <template.pptx> --manifest-only
python3 scripts/pptx_template_import.py <template.pptx> --inheritance-mode both
```

Semantic template pages:

```bash
python3 scripts/template_page_catalog.py <template_dir> validate
python3 scripts/ensure_template_catalogs.py --write
python3 scripts/template_capabilities.py <template_dir> --write
python3 scripts/template_capabilities.py templates --all --validate
python3 scripts/template_page_catalog.py <template_dir> search "五阶段实施流程" \
  --page-type content --content-form flow_linear --item-count 5 \
  --topology sequence --emphasis directional --compact --limit 3
python3 scripts/template_page_catalog.py <project_path> validate-project
python3 scripts/validate_mirror_fidelity.py <project_path>
python3 scripts/validate_template_usage.py <project_path>
python3 scripts/validate_asset_usage.py <project_path>
```

`template_capabilities.py` 为所有 deck/layout 生成统一能力描述。Schema v3 保留 `asset_roles` 与 `shell_contract`，并新增逐图 `image_assets`、`content_raster_refs`、`native_editability`。`validate-project` 检查 canonical 引用；两个 template validator 分别检查 exact mirror 与 role-aware brand shell。`brand_shell` 的必需背景必须 full-bleed，且不能用未锁定的通用背景替代。必须在 Executor 完成后和导出前运行。

Course Handoff:

```bash
python3 scripts/validate_course_handoff.py <course-handoff> --require-design
# 显式 Deck：隔离使用该包
python3 scripts/bind_course_handoff.py <course-handoff> \
  --template-package <deck_id> --template-kind decks
# Free Route：不读取 Deck
python3 scripts/bind_course_handoff.py <course-handoff> --free-route full-free
# Free Route：单一 Layout 主导
python3 scripts/bind_course_handoff.py <course-handoff> \
  --template-package 科技蓝商务 --template-kind layouts
```

绑定器只写 `page_binding.json` v2 提案（含顶层 `route/variant_policy` 与逐页 `variant_selection/source_scope/fallback_used/skin_source`）；Strategist 复核后才写 `spec_lock.md`。`variant_selection.py` 覆盖全部内置 Deck/Layout/Chart SVG：明确构图优先，未明确时只在语义等价池做 outline-hash 驱动的受控轮换。Deck 仅显式启用且不混用其他 Deck/Layout/HTML Background；Free Route 禁止引用任何 Deck。`validate_asset_usage.py --preflight` 先查路由，Executor 完成后再无参数运行以核对实际来源标记。

Template fill (direct PPTX, no SVG conversion):

```bash
mkdir -p <project_path>/sources <project_path>/analysis <project_path>/exports <project_path>/validation
python3 scripts/template_fill_pptx.py analyze <project_path>/sources/<source.pptx> -o <project_path>/analysis/slide_library.json
python3 scripts/template_fill_pptx.py scaffold <project_path>/analysis/slide_library.json -o <project_path>/analysis/fill_plan.json --slides "1,3,4"
python3 scripts/template_fill_pptx.py check-plan <project_path>/analysis/slide_library.json <project_path>/analysis/fill_plan.json -o <project_path>/analysis/check_report.json
python3 scripts/template_fill_pptx.py apply <project_path>/sources/<source.pptx> <project_path>/analysis/fill_plan.json -o <project_path>/exports/filled.pptx
```

`apply` automatically writes `filled_YYYYMMDD_HHMMSS.pptx` unless the output stem already ends with a timestamp. It applies a `fade` page transition by default; `--transition <effect>` (fade/push/wipe/split/strips/cover/random, `--transition-duration` in seconds) changes it, `--transition none` removes it, `--transition keep` preserves the source transitions, and a per-slide `transition` field in the plan overrides whatever the CLI selects.

Post-processing and export:

```bash
python3 scripts/total_md_split.py <project_path>
python3 scripts/finalize_svg.py <project_path>
python3 scripts/svg_to_pptx.py <project_path>
```

Image generation:

```bash
python3 scripts/latex_render.py <project_path>
python3 scripts/latex_render.py <project_path> --providers codecogs,quicklatex,mathpad,wikimedia
python3 scripts/image_gen.py "A modern futuristic workspace"
python3 scripts/image_gen.py --list-backends
python3 scripts/analyze_images.py <project_path>/images
```

Repository update:

```bash
python3 scripts/update_repo.py
python3 scripts/update_repo.py --skip-pip
```

## Recommendations

- Keep one user-facing entry point per workflow at the top level of `scripts/`
- Move provider-specific or helper internals into subdirectories
- Prefer the unified entry points `project_manager.py`, `finalize_svg.py`, and `image_gen.py`
- Prefer `svg_final/` over `svg_output/` when exporting

## Related Docs

- [Conversion Tools](./docs/conversion.md)
- [Project Tools](./docs/project.md)
- [SVG Pipeline Tools](./docs/svg-pipeline.md)
- [Image Tools](./docs/image.md)
- [Troubleshooting](./docs/troubleshooting.md)
- [Skill Entry](../SKILL.md)

_Last updated: 2026-07-28_

## 教学分镜交接与备注

- `python3 scripts/validate_teaching_contract.py <bundle> [--ready-for-class] [--json]`：原纲哈希、映射、时间、材料/备注与揭晓顺序检查。默认允许带明确缺口的草稿，课堂交付模式拒绝缺口；不替代语义评审。
- `python3 scripts/import_course_notes.py <bundle> <project>`：按现有 SVG 页序导入短提示或固定页完整讲稿到 notes/total.md，保留示范与反馈；失败不覆盖已有备注。
- 字段与就绪口径见 [教学分镜扩展](../references/teaching-contract.md)。

## 课程模板结构与成品回归

- `validate_page_realization.py <project> [--pptx <pptx>] [--delivery] --summary-only --out <新attempt文件>`：终端输出状态与错误，完整逐页证据保存到 JSON；省略 `--summary-only` 时沿用完整 JSON 标准输出。
- `render_course_pptx.py --check --out <new-dir>`：批量制作前检查当前Python/PyMuPDF、LibreOffice、输出权限；可加PPT路径与`--fontconfig`，保存runtime.json，失败非零退出。
- `render_course_pptx.py <pptx> --out <new-dir> [--fontconfig <file>] [--timeout 120]`：LibreOffice实际PPT渲染，重验环境与页数，保存PDF/PNG/文字/hash、失败日志和带来源的警告；成功仍待视觉复核。需要同一Python中的PyMuPDF。
- `prepare_render_fonts.py <font-file> ... --out <new-dir>`：只复制字体内容，校验SHA-256并保存来源；不复制系统元数据或自动替换字体。详见[运行环境](../references/render-runtime.md)。
- `freeze_course_anchors.py <project> --selection <json> --approval-ref <真实审批>`：真实内容样章冻结；已有有效审批只验证并沿用。
- `python3 -m pytest scripts/test_page_realization.py scripts/test_course_handoff.py -q`：六页原生fixture及结构/备注/计数/hash负例。
- 执行与文件格式：[逐页结构契约](../references/page-realization.md)。课程旧项目显式 `--course-draft -o <name>_draft.pptx` 才可缺结构计划迁移，备注仍须完整；正式交付还须Office渲染复核。
