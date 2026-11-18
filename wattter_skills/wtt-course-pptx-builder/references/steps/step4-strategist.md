---
description: Step 4 detail — Strategist 八项确认 + 公式渲染 + 图层化架构 + spec_lock/locked_values 产出
---

# Step 4：策略师阶段 —— 详细

> 本文件承接 SKILL.md Step 4 的执行细节。SKILL.md 定义前置条件、八项核对与差量确认。

进入本步后，先读角色定义：

```
Read references/strategist.md
```

> ⚠️ **强制闸口**：在写 `design_spec.md` 之前，Strategist 必须 `read_file templates/design_spec_reference.md` 并遵循其完整的 I–XI 节结构。详见 `strategist.md` 第 1 节。
>
> ⚠️ **渐进式 Chart 闸口**：先从 handoff 或内容分析得到 `content_form_hint / relationship / item_count / has_data / image_need / composition`。Deck Route 先用选中 Deck 的 `template_page_catalog.py search --precise-only --image-need <image_need>` 查询精确包内页；返回 `[]` 或没有真正适配的结构时，按页调用 `python3 ${SKILL_DIR}/scripts/match_content_forms.py resolve <form> [--count <N>] --package <选定包名>` 查全局 chart；无 Deck 的 Free Route 去掉 `--package`。形态词表列出的包内变体只是候选，不能仅凭同形态截断 chart。`auto` 下复核 chart 的 Pick/Skip 条件；显式 `template/chart` 偏好按原意执行。确定性脚本可读取完整目录，模型上下文只接收该页的紧凑候选，禁止完整加载 71 个 chart。chart SVG 只借结构，皮肤始终来自当前 route 的 `spec_lock`。

## Course Handoff 快速路径

输入已通过 `validate_course_handoff.py --require-design` 时：

1. 从 contract 继承页数、受众、章节页序和稳定 `page_id`。
2. 先沿用 Step 1 核对过的当前用户请求及 `render_request.md`，再从 design profile 预填未指定的风格语义、`render_mode` 与图片素材策略；profile 是推荐值，不是 builder 的执行契约。用户已选 Deck 时，不得因旧 profile 写着自由风格而退回 Free Route。
3. 根据 Step 3 路由运行一条绑定命令：

   ```bash
   # 显式 Deck：只绑定该 Deck
   python3 ${SKILL_DIR}/scripts/bind_course_handoff.py <bundle> \
     --template-dir <selected-deck> --template-kind decks \
     --out <project_path>/page_binding.json

   # Free Route · layout-led
   python3 ${SKILL_DIR}/scripts/bind_course_handoff.py <bundle> \
     --template-dir <selected-layout> --template-kind layouts \
     --out <project_path>/page_binding.json

   # Free Route · html-led / full-free
   python3 ${SKILL_DIR}/scripts/bind_course_handoff.py <bundle> \
     --free-route html-led \
     --out <project_path>/page_binding.json
   ```

   `full-free` 时把 `html-led` 改为 `full-free`。
4. 按[构图兑现](../composition-realization.md)联读原逐页意图与正文，核对候选能否实现焦点、关系和阅读路径；所有路由适用。再复核顶层 `route`，再复核每页 `resolved_form / layout_reference / chart_reference / confidence / source_scope / fallback_used / skin_source / fallback_reason`。若包内页仅同形态、用途不明或固定槽位/明确构图不合，确认 `auto` 仍检索合格 chart 且审计解释回退；真正精确适配的本地页保持优先。Deck Route 禁止跨包；Free Route 禁止任何 `decks/*`。
5. 内部核对八项及各自来源。用户已确认或委托的值直接采用，有冲突或关键缺项时只提示该差量。
6. 只有 Strategist 复核后，才把绑定结果写入 `spec_lock.route/page_layouts/page_render_modes/page_shell_assets/page_shell_requirements/page_charts/page_assets` 与 `chart_selection.json`。`page_assets` 记录每页实际承诺使用的来源；`page_shell_assets` 直接继承绑定结果的 `shell_assets`；`page_shell_requirements` 直接继承 `shell_requirements` 的角色映射与 `forbid_unlocked_full_bleed`；不得自行猜测文件名或降低角色要求。

权威顺序不变：`spec_lock.md` > `locked_values.json` > `design_spec.md`。`page_binding.json` 只是可删除、可重建的选型审计提案。

Binder 默认对全部 Deck/Layout/Chart SVG 使用 `controlled_rotation`：先满足内容形态、数量、数据、图片和明确构图，再仅在分差不超过 10 的等价候选中轮换；最近 3 个同域资产避免重复，结果由 outline hash 确定性锁定。把顶层 `variant_policy` 与最终 `page_layouts/page_charts` 写入 `spec_lock.md`。Executor 只执行锁定结果，不得再次随机选页。mirror、结构页和唯一候选自动稳定。

## 逐页模板落实（Deck Route）

先读实际选中的源 SVG。课程项目把页 ID、源路径、结构组、适配原因和字段落位一次写入 `page_realization.json`。验收时由检查器生成审阅记录。无课程交接契约的独立演示可沿用简短的 `template_usage.md`。

- 设计特征必须能在图上指出：如目标主卡与动作区的主次关系、证据和判断的对照、步骤连接及交付区、三阶段行动与证据的对应。只记录模板名、配色或页头色条，不算模板结构已经落实。
- 页数、教学用途、固定槽位、文字容量和图片需求精确匹配才可锁 `mirror`。不匹配时允许沿用**同一 Deck**的页头、空间层级及视觉语言，按实际内容关系重建；无可验证的 shell 资产时如实锁 `themed_rebuild`。不能为匹配模板凑条目、删题面、虚构界面或调整教学顺序。
- 非精确页仍按上面的 Chart 闸口查找合格关系结构；可将其与同 Deck 的视觉壳组合。记录哪些特征继承、哪些关系重建及原因，不能把视觉参考伪报为精确 `page_layouts` 绑定或 `mirror`。`brand_shell` 仍须满足已有资产与角色契约，Deck Route 不混其他 Deck、Layout 或 HTML Background。
- 逐页说明第一眼焦点、主次内容与阅读路径。练习须让目标、动作、产出、时限容易定位；操作须区分可验证界面、操作示意和待补材料；示范须让输入、生成结果与核查证据能对应。缺失的真实材料继续记入 readiness，不用装饰补足事实。

## 背景架构（按 route）

Deck 含 `background_catalog.json` 时，Binder 按页型和内容分配不重复的底图，`background_variant` 记录场景和文字留白。把选中的文件写入该页的壳资产与来源，并按留白摆放文字。候选不足时，按 `fallback_reason` 使用可编辑形状铺底。非标准交接没有 Binder 时，按包内清单为整套课预先分配底图，再逐页锁定。SVG 使用验收会检查库内整页背景是否跨页重复。

Free Route 按锁定策略选用 HTML-PNG、AI 或原生背景；仅明确选用 HTML 的页面执行 HTML 背景契约。Deck Route 采用选中 Deck 自带的背景/品牌壳，或按锁定的 `themed_rebuild` 用原生形状重建该 Deck 视觉语言，禁止加载 HTML Background。八项确认中：
- 第 5 项（配色方案）含**主题色板**（`theme_palette`）选择——见 [`../theme-palettes/_index.md`](../theme-palettes/_index.md)，作为 HTML 背景 + SVG 文字层的 HEX 种子。
- 第 8 项（图像使用方式）：Free Route 可选 **HTML 背景风格**（`style`）——见 [`../../templates/html-background-styles/_index.md`](../../templates/html-background-styles/_index.md)；Deck Route 跳过该索引，背景来源写入 `page_shell_assets/page_assets`。

Free Route 在写 `design_spec.md`/`spec_lock.md` 后，仅为明确锁定的 html 背景页写 `images/html_background_manifest.json` 并运行 `html_render.py`；没有此类页则跳过。Deck Route 不生成该 manifest；必需壳资产来自选中 Deck 并通过资产来源校验，原生重建不冒称资产保真。

## 高级选项提示（默认关闭，不是第九项确认）

确有关键差量须确认时，附一行可选模式提示。其余情况按用户授权连续执行：

- **分阶段模式**：较重 deck（页数多 / 源材料厚 / 网络抓取累积多）可在 Step 5 之后切换——停止此对话，开新窗口输入 `继续生成 projects/<project_name>` 进入 Phase B（见 [`../../workflows/resume-execute.md`](../../workflows/resume-execute.md)）。正常规模默认连续模式一次性生成。
- **先精修规范**：可让 Strategist 产出完整规范后、生成开始前停下等用户审阅/修改任意部分（走 [`../../workflows/refine-spec.md`](../../workflows/refine-spec.md) 工作流）。无请求则规范一次性写完、流水线自动推进。

用户明确选择相应模式时进入该路径。

## 公式渲染策略（第 7 项内部）

| 策略 | 行为 |
|---|---|
| `mixed`（默认） | Strategist 将复杂、值得作为公式的表达式渲染为 PNG 资源；简单内联表达式保持可编辑文字 / Unicode |
| `render-all` | Strategist 把所有值得作为公式的表达式都渲染为 PNG 资源 |
| `text-only` | 不做公式渲染；公式保持可编辑文字 / Unicode |

在八项已核对且关键差量解决之后、**输出 `design_spec.md` / `spec_lock.md` 之前**，若已确认的公式策略为 `mixed` 或 `render-all` 且内容中包含值得作为公式的表达式，Strategist 必须：

1. 识别显式的 LaTeX 以及源中任何应当严格作为公式呈现的表达式。
2. 写出 `<project_path>/images/formula_manifest.json`，仅包含被选中渲染的公式。
3. 运行：
   ```bash
   python3 ${SKILL_DIR}/scripts/latex_render.py <project_path>
   ```
4. 在 `design_spec.md §VIII 图像资源清单` 中，把渲染好的公式 PNG 作为 `Acquire Via: formula`、`Status: Rendered`、`Type: Latex Formula` 的行加入；同时在 `spec_lock.md images` 中以 `| no-crop` 列出。

公式渲染器默认使用 provider 回退链：`codecogs,quicklatex,mathpad,wikimedia`。前三者支持自定义颜色；Wikimedia 是可用性兜底。公式 PNG 默认透明：清单中的 `background` 是临时渲染底色和去透明参考色，并非最终保留背景，除非该项设置了 `transparent: false`。不要在 `spec_lock.md` 中扫描 `$...$` 或 `$$...$$`。源材料中用美元符号包围的数学内容仅作为 Strategist 的信号；渲染器读取的是显式清单。

## 统一图像分析（单次）

当用户提供了图像（图像方案 B）或已渲染公式 PNG 时，在**输出设计规范之前**跑**一次** `analyze_images.py`——这次跑在公式渲染和用户图导入都完成之后，把两者一并纳入清单，不重复跑：
```bash
python3 ${SKILL_DIR}/scripts/analyze_images.py <project_path>/images
```

> ⚠️ **图像处理**：尺寸、格式等元数据通过 `analyze_images.py` 或资源清单读取，不靠目测估算。素材内容、裁切效果及实际 SVG/PPTX 渲染仍须查看像素；元数据检查不能代替视觉复核。

> 💡 **页面类型背景默认**：仅对 Free Route 中已选择 HTML 背景的页面，按页型预填 `cover / ending / chapter / theme` 及 §VIII 的 `html` 行，运行 `html_render.py`。不因内容页或 A（无图）方案而强制新增 HTML 背景。Deck Route 保留本包背景/资产或锁定的原生重建；其他 Free 页沿用自己的背景契约。页型识别和 HTML Reference 写法见 [`../strategist.md`](../strategist.md) §页面类型配图默认。

## 输出与校验

课程字体方案确定后，按[渲染运行环境](../render-runtime.md)使用已锁定的 Python 执行 `render_course_pptx.py --check --fontconfig <已核对配置> --out <新的attempt目录>`。不需要自定义fontconfig时省略该参数；首批样章仍核对实际字体。预检失败先处理环境，再进入批量生成。

- `<project_path>/design_spec.md` —— 人类可读的设计叙事
- `<project_path>/spec_lock.md` —— 机器可读的执行契约（骨架：`templates/spec_lock_reference.md`）
- `<project_path>/locked_values.json` —— 由 `extract_locked_values.py` 生成，逐页通过 `--page` 查询。
- `<project_path>/chart_selection.json` —— 机器可读的逐页 chart 选型审计（骨架：`templates/chart_selection_reference.json`）；记录 catalog read、选中结构、无匹配回退、备选项，以及 `structure_only` 主题继承策略
- `<project_path>/page_binding.json` —— 仅 handoff 快速路径生成；语义模板/图表绑定提案，不是权威锁
- `<project_path>/page_realization.json` —— 课程 Deck/Layout 的逐页执行计划。验收时可派生 `template_usage.md`。

三个 markdown/json 写完后必须运行：
```bash
python3 ${SKILL_DIR}/scripts/extract_locked_values.py <project_path>   # 产出 locked_values.json
python3 ${SKILL_DIR}/scripts/template_page_catalog.py <project_path> validate-project
python3 ${SKILL_DIR}/scripts/validate_chart_mappings.py <project_path>
python3 ${SKILL_DIR}/scripts/validate_asset_usage.py <project_path> --preflight
```
任何错误都必须先修复。尤其是路由越界、`page_layouts` 引用了不存在的 SVG、未登记 reference 或旧 alias，以及 `page_charts` 与 `chart_selection.json` 不一致、chart key / SVG 不存在、layout + chart 冲突，或 chart skin 未声明从 `spec_lock` 继承时，不得进入 Executor。

## 课程结构执行计划

课程Deck/Layout逐页模板落实使用[机器化结构计划](../page-realization.md)，把真实源结构id、原字段落位、容量理由、复用方式写入page_realization.json；themed_rebuild同样适用。关系范围和分镜计数与正文有矛盾时明确报错，不擅自删项。已有有效设计/样章审批引用并沿用，只确认缺失差量。
