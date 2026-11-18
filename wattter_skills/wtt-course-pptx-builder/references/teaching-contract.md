# 教学分镜扩展 v1

详尽讲师大纲进入制作时，先保留原目标、教学深度、示范、活动及产出，再形成页面。课程原大纲是教学要求来源；确认页表是屏幕内容来源；Builder 的 spec_lock 只锁视觉执行。原材料存在事实或软件版本问题时列差异和待核项，不通过复述旧说法冒充核实。

## 独立交接与字段

沿用 `wtt.course-handoff` version=1。旧包无此扩展仍可制作，但不能据此宣称课堂材料齐套。各 Skill 自带相同检查脚本，无需安装另外两个 Skill。

在 course_contract.json 增加可选 `teaching_contract`：

```json
{
  "version": 1,
  "source_outline": {"path": "source_outline.md", "sha256": "原文件的64位SHA-256"},
  "requirements": [
    {"id": "O-01", "text": "原大纲的具体要求和深度", "page_ids": ["P001", "P002"]}
  ]
}
```

原文件须复制到包内、保持内容不改。文件哈希用脚本计算；它不同于重排后页表的 `outline.hash`。新增教学要求须单独记录为变更，不冒充原纲条目。

启用扩展时，每个 pages.jsonl 条目增加 `teaching`：

```json
{
  "requirement_ids": ["O-01"],
  "mode": "demo",
  "duration_seconds": 240,
  "learner_action": "观察示范并定位输入、操作与结果",
  "instructor_action": "用材料卡完成一次操作，展示结果与失败重试",
  "material_refs": ["materials/demo.md"],
  "reveal_after": null
}
```

- `mode`：`explain` / `demo` / `practice` / `feedback` / `transition`；以实际教学动作判断，操作示范不能仅靠原则讲解替代。
- `duration_seconds`：含该页口播、演示、等待和学员操作的全部用时。翻页揭晓若不额外占时可为 0；各页合计须等于课程分钟数，禁止对同一活动重复计时。
- 内部配时与学员可见计时分开：活动页的 `teaching.duration_seconds` 为正的有限数；`slide_text.timebox` 按任务与用户要求可省略，显示时须为正数加单位。旧包只有合法可见时间仍兼容，但不据此声称课堂就绪；无配时依据列缺口，不凭隐藏时间放宽预算。
- `material_refs`：相对 bundle 的本地材料路径，可为空；需要材料的活动必须引用实际文件。屏幕、讲师提示、练习纸各司其职，屏幕简洁不能靠未交付的纸卡补齐。
- `reveal_after`：答案/反馈页引用前面的题目 page_id；普通页为 null。静态 PPT 默认题目和揭晓分为两页，同一教学时间内展示，不把备注里的“稍后揭晓”当实际实现。自动入场动画不等于延迟到学员作答以后。
- `speaker_notes_ref`：可先引用简短讲师提示文件，PPT 页表稳定后再扩写同页讲稿；不要求制作前写完长稿。路径以 bundle 为基准；`#P001` 等片段必须能定位到唯一页面标题。
- 设计阶段保持这些教学字段不变；既有页数已锁时，题答分离或材料补页需求先记变更，不能由下游擅自插页。

## 可见文字与作者说明

`slide_text` 只放实际可见的 title/body_points/timebox/数据/题面。关系、排版、讲师动作、素材待办不得混入。`raw_markdown` 如需留存放页面顶层作为作者记录；旧版 slide_text.raw_markdown 被检查器忽略并警告，其他可见字段照常严格检查。不能把实际必显内容移入 raw_markdown 来通过验收。

## 两份短验收文件

- `source_coverage.md`：逐项列原要求 → 实际页面及讲解/示范/练习正文证据 → 材料 → 差异与待办。标题提到、ID 对上、写“已覆盖”都不能代替证据。实际演练、工具演示和本人经验的来源性质必须保留。
- `readiness.json`：`{"status":"draft","gaps":["手机端演示步骤未按授课环境验证"]}`；完整时 status 为 ready、gaps 为空。缺材料/未核实入口/未做示范如实登记，不能用空壳文件或假截图消除待办。试讲和真实软件成功是单独证据。

```bash
python3 scripts/validate_course_handoff.py /path/to/course-handoff
python3 scripts/validate_teaching_contract.py /path/to/course-handoff --json
python3 scripts/validate_teaching_contract.py /path/to/course-handoff --ready-for-class
```

默认检查结构、原文件哈希、映射、时间和揭晓顺序；材料/备注/审阅文件缺失报告 draft 警告。`--ready-for-class` 把这些缺口作为失败。允许导出明确标注 draft 的样稿继续评审，不宣称可直接上课。无扩展的外部页表也能独立使用，先按原大纲人工核对再添加扩展。

机器只能检查可追溯性与文件齐套，不能判断“七页原则讲解”是否替代了原定跟做，也不能证明真实课堂时间。须另读实际页、备注与材料，检查教学语义及演示证据。
