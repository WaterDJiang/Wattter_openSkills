# Course Handoff Protocol v1 / Design Intent v1.2

`wtt.course-handoff` 是课程内容与视觉设计之间的可选机器交接协议。它不要求安装任何其他 skill；普通 Markdown、DOCX、PDF 输入仍然有效。

## 教学分镜与课堂材料

详尽讲师大纲生成新页表时使用 [教学分镜扩展 v1](teaching-contract.md)，保留原文文件哈希、原要求映射、教学动作、材料与揭晓顺序。已有旧 v1 包保持兼容，页表哈希不能证明原大纲实质覆盖。制作前无需完整逐字稿，`speaker_notes_ref` 可先指简短讲师提示；完整稿在页面稳定后扩写。

`slide_text` 仅承载实际可见字段；作者 `raw_markdown` 移到页面顶层。旧嵌套形式只作兼容读取并警告，不纳入逐字上屏要求。

## 文件

```text
course-handoff/
├── course_contract.json
├── pages.jsonl
├── design_profile.json      # 可选：设计阶段新增
└── page_intents.jsonl       # 可选：设计阶段新增
```

## 内容契约

`course_contract.json`：

- `protocol`: `wtt.course-handoff`
- `version`: `1`
- `producer.skill` / `producer.version`
- `course`: `id`、`title`、`duration_minutes`、`audience`、`learning_objectives`
- `outline.hash`: `sha256:<hex>`
- `outline.locked`: 是否已确认内容结构
- `outline.sections[]`: `section_id`、`order`、`title`、`page_ids`
- `page_count`
- `pages_file`: 默认 `pages.jsonl`
- `policies`: `allow_reorder`、`allow_page_count_change`、`allow_scope_expansion`、`allow_operational_cta`
  - `allow_operational_cta=false` 禁止未经授权的营销转化；必要教学操作与材料入口保留。关键词检查仅提示语义复核，不能根据“点击链接”等词自动删除题面或判失败。

`outline.hash` 算法：复制 `outline`，删除顶层 `hash`，使用 UTF-8、按 key 排序、无空白 canonical JSON，计算 SHA-256。

`pages.jsonl` 一页一行：

- `page_id`: 稳定主键
- `sequence`: 从 1 连续递增
- `section_id`
- `page_type`: `cover` / `toc` / `section_opener` / `content` / `case` / `exercise` / `interaction` / `summary` / `closer`
- `outline_title`: 已锁定的内容标题
- `display_title`: 可选的展示标题
- `must_include`: 不可丢失的观点、数据或结论
- `slide_text`: 可见内容，保持结构化 JSON object
- `evidence_refs`: 来源引用
- `speaker_notes_ref`: 逐字稿或讲者备注的文件引用

内容下游不得在未获授权时重排、增删页面或扩展知识范围。完整逐字稿只通过 `speaker_notes_ref` 延迟读取，不复制到设计交接文件。

当 `outline.locked=true` 时，`slide_text` 的所有可见叶文本也是锁定内容。模板槽位不足时必须调整页面适配模式或布局，不得删字、合并观点或用近似文案替代。

## 活动页最小契约

`interaction` 表示讨论/判断，`exercise` 表示练习/操作。两者聚焦当前动作：可见内容保留可读任务与必要题面。内部 `teaching.duration_seconds` 为正的有限数时可省略可见 `timebox`；旧包合法可见计时仍兼容，显示时须为正数加单位。源材料中的必要题面、条件、步骤、产出与材料入口必须保留；答案和反馈按实际揭晓次序呈现，不默认编造 3-5 步。活动页的模板绑定仍归 Builder 决定，但必须保留活动页角色与内部预算，不能自行补上已被省略的时间标记。

### 实际播放页序

`pages.jsonl` 是锁定基线，`page_intents.jsonl` 中的基线页和插页构成实际播放顺序。制作与固定页补稿按该顺序映射编号和备注。插页可在自己的设计行用 `speaker_notes_ref` 指向包内独立讲师提示。既有无备注插页可读，进入备注导入和课程导出时需补对应讲师提示。活动时间归入原课堂预算，涉及任务、配时或揭晓变化时回分镜更新。具体命令见本 Skill 的制作或固定页入口。

## 设计增量

`design_profile.json`：

- `protocol`: `wtt.course-design-intent`
- `version`: `1.2`（同时兼容旧 `1` / `1.1`，旧包警告未验证正文同步）
- `source_outline_hash`: 必须与内容契约一致
- `render_mode`: `svg` / `image` / `hybrid`，默认 `svg`
- `emit_image_prompt_pack`: 默认 `false`
- `asset_image_policy`: `off` / `selective` / `aggressive`，默认 `off`
- `style_intent`: 语义风格，不放下游私有模板 id
- `page_intents_file`: 默认 `page_intents.jsonl`

`page_intents.jsonl` 一页一行，只追加设计信息：

- `page_id`
- `origin`: `baseline`（默认，可省略）/ `inserted`（设计层插入页）
- `ins_kind`: 仅 `origin=inserted` 必填——`hero` / `interaction` / `case` / `exercise`
- `baseline_ref`: 仅 `origin=inserted` 必填——插入位置紧邻的前一基线 `page_id`
- `ins_content`: 仅 `origin=inserted` 必填——插入页可见文字。`title` 必填；`interaction` / `exercise` 可在插入条目顶层以 `teaching.duration_seconds` 记录正的有限内部用时，或保留旧包合法可见 `timebox`；`body_points` 可选，保留执行活动必需的题面、条件、步骤和材料入口，不为低密度删掉必要内容
- 插入活动页可选 `teaching: {"duration_seconds": 90}`：内部计时，不写入 `ins_content`，不自动渲染；实际用时须有预算归属，影响原教学安排时先更新教学契约。
- `relationship`: `none` / `parallel` / `sequence` / `orthogonal` / `hierarchy` / `cycle` / `comparison` / `temporal` / `composition` / `correlation` / `distribution` / `causal`
- `item_count`: 数量不确定时为 `null`
- `has_data`
- `data_kind`
- `content_form_hint`: 可选提示，不是强制词表
- `content_form_confidence`: `low` / `medium` / `high`
- `content_form_alternatives`: 可选，最多 3 个语义备选
- `story_role`: 本页在叙事中的角色，如 `hook` / `explain` / `prove` / `practice` / `synthesize`
- `composition`: 可选紧凑构图语义：
  - `topology`: 如 `split` / `grid` / `sequence` / `radial` / `layered`
  - `emphasis`: 主视觉或主结论的强调位置
  - `reading_order`: 阅读顺序标签数组
- `data_shape`: 可选数据形态摘要（维度、指标、分类数量），不含图表 id
- `density`: `low` / `medium` / `high`
- `image_need`: `none` / `optional` / `required`
- `editable_requirement`: `required` / `preferred` / `not_required`
- `visual_priority`: `low` / `medium` / `high`
- `visual_description`: 旧v1.1可由有效 `composition` 替代；新设计按下文写紧凑内容映射
- `binding_preference`: `auto` / `template` / `chart` / `hybrid` / `free`

`render_mode=svg` 时，`emit_image_prompt_pack` 必须为 `false`。图片素材仍可按 `asset_image_policy` 单独选择；它不等于整页图片模式。

设计增量必须模板无关：禁止写 `deck_id/template_id/layout_id/chart_id`、模板路径、`page_catalog` reference 或 `.svg` 文件名。Generator 只表达语义，Builder 在当前 route 内自行绑定本地资产。

`composition.topology/emphasis` 只在内容确实需要某种构图时填写；Builder 优先满足它。字段缺失时，Builder 可以在相同 `content_form / item_count / data_shape / density` 的等价结构中受控轮换，但不得因此选择低匹配资产。受控轮换不反向写入 Generator，也不暴露素材 id。

## 渲染请求与设计可执行性

Builder按[构图兑现](composition-realization.md)把原意图带入选型复核、逐页执行与成品渲染检查；Binder的语义匹配不能代替实现。新生成的逐页设计用既有 `visual_description` 说明主视觉对象、原 `slide_text` 字段到区域的映射、关系作用范围和需要的状态/核查；不复制正文或增加 JSON 字段。`composition` 可紧凑表达空间约束，但空对象、单一 topology 或“纵向排列”不构成可执行设计。只有真正在该关系内的对象计入 `item_count`；同数组中的条件、示例和完成判据不自动成为流程节点。旧 v1/v1.1 文件继续可读，结构通过不代表这些视觉决定已经落实。

`render_request.md` 单独保留用户请求：原样引用模板要求，另列已授权的画布、风格、字体、图像范围及其来源，未指定项如实标记。后续请求替代旧视觉约束时写明替代关系。用户原话中的模板名称/路径可在此保留，不属于 Generator 自行指定私有布局；上述私有 ID 禁令仍适用于机器设计字段。不得将明确的模板请求降为配色建议或自由路线。Builder 读取此文件后在自己的模板目录绑定资产，并记录实际保留的结构及适配证据。旧包没有此文件时继续按其已确认渲染要求消费，不把缺文件当作用户选择自由路线。

v1.1 的结构检查至少要求非空 `visual_description`，或含有效 `topology/emphasis/reading_order` 的 `composition`；空对象、空阅读序列或仅未知字段不能代替设计意图。已有非空紧凑构图仍兼容；机器只检查最低结构，不证明视觉质量。

## 消费规则

1. 先运行本 skill 自带的 `scripts/validate_course_handoff.py`。
2. 协议未知或验证失败时明确报错；若同时有普通源文档，可回退独立流程，但不得猜字段。
3. 只消费自己理解的标准字段。`content_form_hint`、`style_intent` 等提示字段允许忽略。
4. 外部 skill 可以只生产内容契约，也可以只在合法内容契约上追加设计增量。
5. 模板绑定是 builder 私有增量：`page_binding.json` v2 可输出逐页 `mirror / brand_shell / themed_rebuild`；schema v3 capability 同时输出角色级 `shell_requirements` 与 `native_editability`，核心内容锁在位图时不得进入 mirror。Builder 写入自己的 `spec_lock`，不得反向改写 v1 内容契约。
6. Executor 完成后运行 `validate_content_fidelity.py`；无 handoff 项目自动跳过，锁定 handoff 缺项硬失败。

```bash
python3 scripts/validate_course_handoff.py /path/to/course-handoff
python3 scripts/validate_course_handoff.py /path/to/course-handoff --require-design --json
```


## v1.2 页级视觉闸口

page_intents.visual_contract 保留教学目的、核心结论、主焦点、原字段主关系范围/对象、完整区域落位、阅读阶段、题答显示时机与源页指纹。Builder 自带 scripts/visual_contract.py，不依赖 Generator 安装；bind_course_handoff.py 在选型前调用同版校验，失败报 page_id 和字段。完整字段定义见 [视觉契约](visual-contract.md)。

逐页执行同时读取唯一 pages.slide_text 和 visual_contract：scope_refs 限定主关系范围，objects 决定对象数；placements 的支持字段不能丢失或强塞为流程节点；reading_order 规定先后与同看，neutral_choices/choice_style 要求题页等色、等大小、等权重；rubrics 的原维度、分值、标准和各总分分别对应。关系与内容不因本地模板改变。不能重生成正文，也不能将教学焦点替换为模板装饰。

正文、教学约束或相关材料变化后回生产方复核视觉并更新差量。新视觉指纹允许独立回写讲师备注，旧指纹走原包校验与受影响页迁移；Builder 不直接刷新旧计数或补通用描述。新契约失败不自动降为 v1.1 绕过。旧包继续消费，但结构通过不代表视觉同步已经验证；实际画面、投影可读性与语义原义仍需另验。
