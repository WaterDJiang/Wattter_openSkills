# 逐页模板结构与成品闸口

课程使用 Deck/Layout 时，Strategist 直接写项目 `page_realization.json`，作为逐页结构计划。它不产生正文、改变页序或覆盖 `spec_lock.md`；全部文字用 `slide_text` 字段路径引用。其他课程路由也可用同一闸口记录图表来源。

## 计划与执行

每页记录 `page_id/sequence`、`source_template: {path, sha256}`（项目内复制的真实 SVG）、`reuse_mode`（mirror/adapt_structure/themed_rebuild）、`capacity_reason`、`regions`、`required_features` 与 `relationships`。

- `regions` 每项是 `{id, bounds:[x,y,width,height], fields:["slide_text.title", ...]}`，坐标使用 SVG viewBox。实际SVG用相同id的g包裹该区文本及结构。每个原字段恰好落入一区；保留标点、数字、分值、原顺序，不重写或删材料。
- `required_features` 每项含 `source_ids`（源模板结构组id）、`output_structure_ids`（实际输出结构组id）、`reason`（保留/适配了什么）、`kind`、`regions`。源组和输出组均须含结构图元，原生PPT须含同组原生结构对象。流程/纠错需要连接时写 `require_connectors:true`。不能引用只有文字的id、页头或配色冒充内容结构。优先选中包的教学结构；容量不够先改区比例/换行/构图。合法重建仍须保留可指认的主卡、旁栏、对应行或流程，不得整稿降为一种文字条。
- `relationships` 使用相同的 `kind/regions`。`items_path` 指向原正文的实际条目数组，`count` 写分镜宣称数量；二者不等必须报错。若一个body_points混合动作、条件与说明，按实际范围建关系，不把整个数组猜成流程。缺少明确范围时逐页读原分镜核对，不删项补数。
- `parallel`：并列同轴、分区无重叠；`sequential`：区域阅读方向保持原步骤顺序。
- `main_sidebar`：示范主文档区大于重点旁栏，文本与旁栏对应。
- `paired_rows`：偏差→规则同一行，`columns:2`；逐对保留原文。
- `branch`：流程整体区域与独立条件说明分区，不将分支混成第五步。
- `neutral_compare`：甲乙同尺寸、同色、同字号与字重，不提前用正确/错误颜色揭答。
- `rubric`：默认三列或显式columns，维度、原分值、检查标准逐行对齐；不得合并分值或省略标准。

生成每页时查询本页执行锁和结构计划，读取本页真源，必要时补读已选源 SVG。完成页先运行下方SVG闸口；导出再检查原生PPT中的实际文字框落位、备注关联与结构，marker和绑定成功不构成通过证据。

```bash
python3 ${SKILL_DIR}/scripts/validate_page_realization.py <project> --summary-only --out <project>/evidence/attempt-01-svg.json
python3 ${SKILL_DIR}/scripts/validate_page_realization.py <project> --pptx <actual.pptx> --summary-only --out <project>/evidence/attempt-01-native.json
```

旧项目迁移仅可显式使用 `svg_to_pptx.py --course-draft -o <name>_draft.pptx`，备注闸口不放宽；正式交付须补逐页计划；缺文件不得记SKIP成功。已有mirror/shell/content闸口仍运行，本工具不能替代精确mirror保真。

## 内容锚点

样章从真实正文选页，覆盖完整练习、示范、长句对比、多步流程与评价量规；同一页可覆盖多项。封面/章节页只验证结构页质量。小课也执行，不与长deck分段状态绑定。

批准后写 `anchors.json`：`approval_ref` 引用本会话明确批准或可核验既有审批；`pages` 每项含page_id、covers、svg/image路径及各自sha256。covers使用exercise/demo/long_compare/multi_step/rubric。冻结前不得伪造批准；已有同内容同视觉审批直接沿用。生成/恢复与最终闸口校验hash，改变锚点后将受影响页置待复核，不能悄悄刷新hash延续旧审批。

批准后运行 `python3 ${SKILL_DIR}/scripts/freeze_course_anchors.py <project> --selection <anchor-selection.json> --approval-ref <真实审批引用>`。selection是page_id与covers的列表，必须来自实际内容页与通过的成品渲染。已有anchors时工具只验hash并沿用，不改写审批。生成/恢复先运行同一命令（已有冻结只需project参数），变更会报错并保留旧记录。

## 成品验收

逐步串联：既有备注导入→total_md_split→finalize_svg→原生导出→原生结构/正文/备注→Office渲染→逐页目视复核。导出器对课程或有total.md的项目硬拒缺失拆分页/备注偏离来源；备注用slide→notesSlide关系核对，不能只数notes XML。

```bash
"$PYTHON_BIN" "$SKILL_DIR/scripts/render_course_pptx.py" <actual.pptx> --out <project>/evidence/render-attempt-01 --fontconfig <verified-fonts.conf>
```

使用[运行环境预检](render-runtime.md)锁定的 Python 与绝对路径；需要复制字体时用 prepare_render_fonts.py 的内容复制与 hash 校验。仅实际LibreOffice/PowerPoint/Keynote渲染可作为成品像素证据；PPT→自制SVG不是Office渲染。工具保存环境、命令、字体配置hash、原PPT hash、PDF、逐页PNG/文字与自动边界异常；转换页数必须与PPT页数一致。缺字/裁切/遮挡仍须查看每页像素，自动检查不能证明未遮挡。diagnostics.json 保留带来源的警告；rendered_requires_review 不等于视觉验收通过，未知警告须核对影响后记录。

查看之后写项目 `render_review.json`：`manifest`指向实际渲染manifest；`pages`按原page_id顺序，每页font/wrapping/occlusion/cropping/bounds/structure分别为pass或fail，另写具体observation。不允许未查看就批量填写pass。

```bash
python3 ${SKILL_DIR}/scripts/validate_page_realization.py <project> --pptx <actual.pptx> --delivery --summary-only --out <project>/evidence/attempt-01-delivery.json --usage-md <project>/template_usage.md
```

0 error 才可交付。`--usage-md` 从通过校验的结构计划与实际成品证据生成 Markdown。需要在 SVG 阶段预看时也可使用，Office 渲染栏标待复核。PPT或图像hash改变会使记录失效；修复重新导出、渲染与复核受影响页，保留所有旧attempt/失败原文，未改页可引用同hash证据。不能改检测阈值消除真实问题。

单行框若某Office忽略wrap=none而换行，可在SVG text写 `data-text-width`，其值来自已核对的区域或真实字体测量。转换保持文字、字号、锚点对齐和字体声明；固定宽度不自动缩字。长段按原文换行而不拆成无关系的标签。字体替代仅在已确认跨平台字体策略或渲染fontconfig中记录原因、来源和hash；不凭估算统一改字体或扩框越界。
