# 页级视觉契约 v1.2

新生成和视觉更新使用 design_profile.version=1.2。沿用 pages.jsonl 唯一正文与原 page_id；在 page_intents 中加入 visual_contract，保留既有 relationship/item_count/composition/visual_description 给兼容消费者。旧 v1/v1.1 只做结构兼容，校验会提示未验证正文同步；不能把旧包的通过用作本协议验收。

## 生成顺序

- 先读当前页、原要求、相邻页与题答关联，不改已确认正文、页序、配时或备注。
- 写本页教学目的和核心结论。题页结论可以是“依据材料完成判断”，设计说明不能把未揭示答案转成屏幕焦点。
- 区分主关系与支持内容：并行任务、因果、操作步骤、中性对比、评价量规、示范状态、练习动作分别设计。公共计算、分支、完成判据不自动计入步骤。只按主关系对象计数，不按数组长度猜关系。
- 用 JSON Pointer 引用实际字段（如 `/slide_text/tasks/0`）；引用叶字段，不复制正文。scope_refs 可以引用数组/对象，表示完整关系范围，objects 逐对象列出参与该关系的叶字段。数组新增叶项会触发范围/对象不一致。
- 每个正文叶字段都有区域落位与阅读阶段；支持字段也必须落位。主区/侧栏/底带是相对位置，不是私有模板。每个阅读阶段是一组引用，同时读的甲乙选择放同一阶段。
- 写具体 visual_description 和 composition：哪一字段为什么占主焦点、对象如何对应、支持字段贴近哪里、先看与后看什么。不得用“逐行顺读”“图文结合”代替。
- 在题页明确 separate_page 与后续 answer_page_ids；后续页 teaching.reveal_after 必须指回题页。中性选择等色、等大小、等权重，焦点包含全部选项；不能用红绿/优劣或强调正确项提前揭答。静态题页没有答案字段；不靠口头承诺或未实现动画隐藏答案。
- 对量规按原套数分别列出 scope_ref、逐行 dimension_ref/score_ref/standard_ref 和 total_ref；三字段来自同一原行，总分引用对应原量规，不计算或合并不同总分。原文无分值/总分则记 gap，不发明分数。源尚无可执行的计分字段时保持 draft，不填伪数据使严格校验通过。
- 未给步骤、软件界面或演练结果不能生成事实。设计只描述原字段；真实 UI 未核实照旧记 gap。示范与练习按原 mode、材料和揭示时机分开。

## 字段（全部在 visual_contract 内）

| 字段 | 约束 |
|---|---|
| source_page_hash | 用 inspect 取得 `visual-sha256:` 指纹。覆盖原页、教学行为、配时及 `teaching.material_refs` 的文件内容。口播与备注引用独立维护。旧 `sha256:` 仍按原规则校验 |
| teaching_purpose / core_conclusion | 本页具体教学任务和核心结论，不额外上屏 |
| focus_refs | 第一眼焦点叶字段引用；中性选择包括全部选项 |
| relation.kind | none / parallel / causal / steps / comparison / rubric / demonstration / practice |
| relation.scope_refs | 主关系的完整原字段范围；容器引用展开为叶项 |
| relation.objects | 一对象一组叶字段引用；不重叠，其并集恰好等于 scope_refs 展开值 |
| placements | `{region: "主区左列", refs: [...]}` 数组；全部正文叶项恰好落位一次 |
| reading_order | 叶字段引用数组的数组；全部正文恰好一次；同组同时看 |
| timing | `{mode, question_refs, answer_refs, answer_page_ids}`；非题答页 mode=not_applicable 且三个数组为空；揭晓页 mode=immediate、answer_refs 引用答案 |
| choice_style | 中性题页必填 `{equal_color:true,equal_size:true,equal_weight:true}`，timing.neutral_choices=true |
| rubrics | kind=rubric 必填：每套 `{scope_ref, rows:[{dimension_ref,score_ref,standard_ref}], total_ref}`；无原总分才填 null |

kind 与 relationship/composition 必须一致：parallel→parallel/grid或columns；causal→causal/cause_effect或branch；steps→sequence/sequence；comparison→comparison/split或table；rubric→orthogonal/table或matrix；demonstration→sequence/sequence。practice 按实际题面选择主关系，说明学员动作与材料；none 仅单对象无关系页。composition 及 visual_description 是同一个设计的摘要，不另立方案。题页不能选择 pros_cons。

简单页也有目的、结论、焦点、落位、阅读与时机，relation 可以是一个对象。v1.2 的 item_count 必须是 objects 实际长度，不能 null；源对象未定时交 draft/gap，不继承旧数字。

## 内容更新后的交接

Builder 按已确认的页面和材料制作。正文、约束、配时或引用材料内容变化时，将具体受影响页交回分镜复核，沿用其他页。纯口播使用[备注回写](steps/step7-export.md)；原有备注指纹的旧包可先按分镜流程迁移。

## 下游

Builder 自带同版本校验器，无需安装 Generator。先通过 v1.2 闸口，直接消费 pages 与 page_intents.visual_contract；visual_description 仍是给逐页制作者的自然语言提示，字段落位与题答时机不可因模板选型被丢弃。失败报 page_id/字段，不能回原大纲再生成正文。

机器验证检查引用、覆盖、计数、结构冲突、内容指纹与题答关联；不能证明人工关系标注符合原义、所有措辞无泄答、画面可读或量规教学合理。交接前仍双向比对原文和具体设计；PPT 实际兑现另外验收。
