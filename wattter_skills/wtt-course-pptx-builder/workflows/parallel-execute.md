---
description: 大规模 deck（页数 ≥ 60）的并行生成工作流——锚点审批后按段切分，每段一个 worktree 会话并行生成，校验+修复+拼接后导出
---

# 并行执行工作流

> **目的**：当 deck 页数 ≥ 60（并行模式阈值）时，把 SVG 生成从"主代理单会话逐页手写"改为"多 worktree 会话向同一组锚点对齐的并行生成"。解决单代理在长 deck 上后期的上下文压缩漂移问题——质量可能**高于**单代理硬扛 500 页。

> **核心思想**：把主代理脑子里"不成文的一致性"显式化成两类可校验产物——`design_system.md`（如何组合的契约）+ 锚点页（5–10 张金标准页）。所有段 agent 向锚点对齐，而非各自凭记忆。

> **与 [`resume-execute.md`](./resume-execute.md) 的关系**：resume-execute 是 Phase A/B 两段切分（≤100 页预期）。本工作流是**段级并行**（500 页预期），在 Phase B 内部进一步切分。两者可叠加：Phase A 完成后，Phase B 用本工作流并行跑。

## 何时运行

| 触发 | 说明 |
|---|---|
| Step 4 八项确认的页数 ≥ 60 | Strategist 在 §6.2 step 5 已产出 `design_system.md` |
| 用户明确要求并行 | 即使 < 60 页，用户可显式要求走并行路径 |

**前置条件（全部满足才能进入）**：

- [ ] `spec_lock.md` + `design_system.md` 已生成（Strategist 阶段 0）
- [ ] `design_spec.md §IX` 内容大纲完整（段 agent 的内容来源）
- [ ] `chart_selection.json` 已生成并通过 `validate_chart_mappings.py`
- [ ] 图像获取（Step 5）已完成——段 agent 不负责生图

若任一缺失，回到对应步骤补齐。

## 流程概览

```
阶段 0 锁定设计系统 → 阶段 1 生成锚点页 + 人工审批 → 阶段 2 分段 → 阶段 3 并行生成 → 阶段 4 段校验 → 阶段 5 修复 → 阶段 6 拼接 + 边界连贯 → 阶段 7 后处理导出
```

---

## 主会话瘦身契约（HARD）

> 200 页 deck 在并行路径上卡死的头号原因，是主会话把自己当生成者——跑 checker、读 SVG、重生页——上下文线性爬升直到爆。本契约把主会话锁回"调度者"角色。

| 主会话**允许** | 主会话**禁止** |
|---|---|
| 读 `generation_state.py status` / `resume` 输出（段级 verdict + 页计数） | ❌ Read 任何 `svg_output/*.svg` 内容（含锚点之外的页） |
| 阶段 0/1 读 `spec_lock.md` / `design_system.md` / `design_spec.md`（仅锚点生成需要） | ❌ 读 `svg_quality_checker.py` / `consistency_checker.py` 的 stdout 明细 |
| 阶段 1 手写 5–10 张锚点 SVG（数量有界，在段会话启动前完成） | ❌ 在主会话里跑这两个 checker |
| 段表元数据操作（`add-segment` / `mark-segment` / `mark-page` 状态写） | ❌ 在主会话里修复 / 重生任何非锚点页 |
| 用文本指令 spawn / supervise 段 / 修复 / 边界连贯 worktree 会话 | ❌ Read 完整 `generation_state.json` 文件（用 `status` / `failed-pages` 子命令代替） |
| 阶段 7 向用户报告最终 `status` 摘要 | |

> **任何页级 SVG 产出动作（生成 / 修复 / 边界重生）必须发生在 worktree 会话内。** 主会话是调度者，不是生成者。锚点是这条规则的唯一例外——数量有界、在所有段会话启动前完成、之后冻结只读。
>
> 阶段转场时主会话只跑一条命令：`python3 ${SKILL_DIR}/scripts/generation_state.py status <project>`。这是它对 deck 进度的唯一权威视图。

---

## 阶段 0：锁定设计系统

🚧 **GATE**：Strategist 已完成八项确认；`spec_lock.md` + `design_system.md` + `design_spec.md` + `chart_selection.json` 已就位。

由 SKILL.md Step 4 Strategist 产出（见 [`strategist.md`](../references/strategist.md) §6.2 step 5）。本工作流不重新生成，只校验存在性：

```bash
ls <project_path>/spec_lock.md <project_path>/design_system.md <project_path>/design_spec.md <project_path>/chart_selection.json
python3 ${SKILL_DIR}/scripts/validate_chart_mappings.py <project_path>
```

**✅ 检查点** —— 三份契约就绪，进入阶段 1。

---

## 阶段 1：生成锚点页（⛔ 人工审批硬闸口）

主代理**手写** 5–10 张锚点页——每类页面类型一张代表页。这些是"金标准"，所有段 agent 向它们对齐。

**锚点选择**（覆盖 deck 的全部页面类型）：

| 锚点 | 数量 | 选取 |
|---|---|---|
| 封面 | 1 | `01_cover.svg` |
| 章节页 | 1 | 任一章节代表 |
| 密集内容代表 | 1–2 | 最典型的 dense 页（卡片网格/KPI/图表） |
| 呼吸页代表 | 1 | 最典型的 breathing 页 |
| 结尾页 | 1 | `NN_ending.svg` |
| 其他特殊版式 | 按需 | 如 deck 有独特版式（quote/全图/数据仪表盘），各加 1 张 |

主代理按 [`executor-base.md`](../references/executor-base.md) §1–§3 的单代理规则手写这些锚点——逐页、Read `design_system.md` + `spec_lock.md`、遵循 layout shell。

**写完后初始化进度并申请审批**：

```bash
python3 ${SKILL_DIR}/scripts/generation_state.py init <project_path> --total <N> --threshold 60
# 逐页标记锚点为 done（主代理已生成）
python3 ${SKILL_DIR}/scripts/generation_state.py mark-page <project_path> P01 done
# ...
```

⛔ **BLOCKING — 人工审批**：用页面渲染图呈现锚点页，等待明确批准。批准后冻结锚点：

```bash
python3 ${SKILL_DIR}/scripts/generation_state.py approve-anchors <project_path> --pages 01_cover 02_chapter 05_dense_repr 12_breathing_repr 50_ending
```

**锚点不可变**：审批后冻结。若后续发现锚点有问题，触发人工决策——不自动修，段 agent 也不改。

**✅ 检查点** —— 锚点经用户批准、`generation_state.json` 的 `anchors.approved=true`，进入阶段 2。

---

## 阶段 2：分段

按**章节边界**切 deck 为段。规则：

| 规则 | 原因 |
|---|---|
| 每段 20–40 页 | 平衡 worktree 会话的上下文负载与调度开销 |
| 段边界对齐章节 | 章节内叙事连贯，跨段边界处的视觉断层最小 |
| 呼吸页随前段 | breathing 页常是章节收束，随所属章节 |
| 图表簇不拆 | 同一图表的连续页（如多页数据展开）留在同一段，避免跨段图表风格漂移 |
| 段数 ≤ 12 | 控制并发会话数（8–12 为宜；更多段串行批次跑） |

为主项目建立段表：

```bash
python3 ${SKILL_DIR}/scripts/generation_state.py add-segment <project_path> --id seg_01 --pages P01-P28 --worktree .claude/worktrees/seg_01
python3 ${SKILL_DIR}/scripts/generation_state.py add-segment <project_path> --id seg_02 --pages P29-P55
# ...
```

`generation_state.py` 强制段 disjoint——重叠页会被拒绝。

**✅ 检查点** —— 段表建立、所有页恰好属于一段、无重叠，进入阶段 3。

---

## 阶段 3：并行生成（每段一个 worktree 会话）

主会话是**调度者**。对每个未完成段：

### 3.1 启动段会话

- `EnterWorktree name=seg_01`（或用户在 FleetView 开新会话指定 worktree 路径）
- worktree 内只读拷入契约（worktree 只隔离生成上下文，契约从主项目读）：
  - `design_system.md` + `spec_lock.md` + `design_spec.md`（或仅该段 §IX 切片）
  - 锚点 SVG（从主项目 `svg_output/` 读，不拷贝）
  - 该段涉及的 `templates/` 模板 SVG

### 3.2 段会话生成指令

段会话（segment agent）按 [`executor-base.md`](../references/executor-base.md) §3.2 的"大规模并行路径"执行：

```
你是段 seg_01 的生成 agent。任务：生成 P01–P28 共 28 张 SVG 页面。

1. 批量 Read（段开始，仅一次）：
   - <project>/design_system.md
   - design_system.md §V 列出的每个锚点 SVG（从 <project>/svg_output/ 读）
   - <project>/spec_lock.md
   - <project>/design_spec.md §IX 中 P01–P28 的内容切片
   - spec_lock.page_layouts / page_charts 中本段页面引用的模板 SVG

2. 对每一页 P<NN>：
   a. 用 `extract_locked_values.py <project> --page <page_id>` 读取本页与共有视觉锁
   b. 查询本页的 page_rhythm / page_layouts / page_charts
   c. 继承 design_system.md §IV 对应的 layout shell
   d. 粘贴 §II 骨架片段（header/footer/card 等），verbatim
   e. 填入 §IX 的内容
   f. 应用 spec_lock 的颜色/字体/图标
   g. 视觉气质对齐同类型的锚点 SVG
   h. 写入 <project>/svg_output/<NN>_<name>.svg（主项目，非 worktree）
   i. python3 scripts/generation_state.py mark-page <project> P<NN> done --segment seg_01

3. 锚点只读不可改。若发现锚点有误，emit warning 并用最近似解释继续，不编辑锚点。

4. 只能写本段 pages 数组里的页。generation_state.py 会拒绝跨段标记。
```

### 3.3 并发与产出汇总

- 多段会话并行（8–12 个 worktree）；超过 12 段则分批
- 段会话产出 SVG **直接回写主项目** `svg_output/`（worktree 不留产出）
- 段会话每完成一页，更新 `generation_state.json`（atomic write，见 `generation_state.py`）

**✅ 检查点** —— 所有段会话完成、`generation_state.py status` 显示全部页 `done` 或 `needs-manual`，进入阶段 4。

---

## 阶段 4：段校验（在段会话内并行）

> ⚠️ **checker 必须在段会话内运行**，主会话不跑 checker、不读 stdout。主会话对本阶段的唯一视图是 `generation_state.py status`（段级 verdict + 页计数）。

每段在自己的 worktree 会话内独立校验（段会话跑完生成后接着跑，不回主会话）：

```bash
# 1. Chart 映射与主题继承契约——段会话内跑
python3 ${SKILL_DIR}/scripts/validate_chart_mappings.py <project_path>

# 2. 单页 spec_lock 合规（现有 checker）——段会话内跑
python3 ${SKILL_DIR}/scripts/svg_quality_checker.py <project_path>

# 3. 跨页一致性（新 checker，按段 + 比对锚点）——段会话内跑
python3 ${SKILL_DIR}/scripts/consistency_checker.py <project_path> --segment seg_01 --against-anchors
```

**判定**（段会话内决断，写回 state）：

| 结果 | 段会话动作 |
|---|---|
| quality checker 0 error + consistency 0 flagged | `mark-segment seg_01 done` |
| 有 error 或 flagged 页 | 不标 done；进阶段 5（段会话自修复或主会话 spawn 修复会话） |
| 段反复修复失败 | `mark-segment seg_01 degraded`，交主会话 spawn 修复会话兜底 |

```bash
python3 ${SKILL_DIR}/scripts/generation_state.py mark-segment <project_path> seg_01 done
```

**✅ 检查点（主会话）** —— `generation_state.py status <project>` 显示所有段 `done` 或 `degraded`，进入阶段 5（仅未过段）或直接阶段 6。主会话**不读** checker 明细、**不读** SVG——只看段 verdict。

---

## 阶段 5：修复（在修复 worktree 会话内）

> ⚠️ **修复绝不发生在主会话。** 主会话读 `status` 发现有 `degraded` 段或有 `failed`/`needs-manual` 页 → spawn 修复 worktree 会话 → 等 `status` 收口。修复会话是生成者，主会话是调度者。

主会话的调度动作（仅这两步）：

```bash
# 1. 看哪些段还有未过页
python3 ${SKILL_DIR}/scripts/generation_state.py status <project_path>
# 2. 对每个 degraded 段，给修复会话一条指令（含目标页清单命令）
```

**修复 worktree 会话**的指令模板（主会话用文本 spawn，不读产物）：

```
你是段 seg_01 的修复 agent。任务：修复本段未通过校验的页。

1. 拿目标页清单（一句话，不读完整 state 文件）：
   python3 ${SKILL_DIR}/scripts/generation_state.py failed-pages <project> seg_01

2. 对清单里每一页 P<NN>（≤3 次重试）：
   a. 用 `extract_locked_values.py <project> --page <page_id>` 读取本页与共有视觉锁
   b. read 当前 SVG + checker 报告（仅该页）定位违规
   c. 重生该页，写入 <project>/svg_output/<NN>_<name>.svg
   d. 重跑两个 checker（仅本段），确认通过
   e. python3 scripts/generation_state.py mark-page <project> P<NN> done --segment seg_01

3. 某页 3 次仍未过 → 写虚线占位 SVG + mark-page P<NN> needs-manual：
   python3 scripts/generation_state.py mark-page <project> P<NN> needs-manual --segment seg_01
   占位 SVG 由你（修复会话）写，不是主会话：
   <svg viewBox="0 0 1280 720"><rect width="1280" height="720" fill="#FFFFFF"/><rect x="540" y="320" width="200" height="80" fill="none" stroke="#999" stroke-dasharray="8,4"/><text x="640" y="365" text-anchor="middle" font-size="16" fill="#999">P<NN> — needs manual</text></svg>

4. 整段重跑后若仍有 needs-manual → mark-segment seg_01 degraded（兜底信号）。
```

deck 照常导出，单页超预算不阻塞整 deck。

**✅ 检查点（主会话）** —— `generation_state.py status` 显示所有页 `done` 或 `needs-manual`，无 `pending`/`failed`/`generating` 残留，进入阶段 6。主会话全程未读 SVG、未跑 checker。

---

## 阶段 6：拼接 + 边界连贯

> 主会话仍不读 SVG、不重生页。两件事都 spawn 专用 worktree 会话干。

### 6.1 段间边界连贯（spawn 边界连贯 worktree 会话）

主会话**不亲自扫描边界**——读 SVG 比较会让 200 页的边界对回流进上下文。改为 spawn 一个边界连贯会话，文本指令：

```
你是边界连贯 agent。任务：检查相邻段末页+首页的视觉/叙事断层。

1. 对每对相邻段 (seg_i 末页, seg_{i+1} 首页)：
   a. read 这两张 SVG（仅这两张）
   b. 判定：叙事过渡是否自然 / 视觉气质是否断层 / 装饰母题是否连贯
   c. 若断层 → 重生边界页（按 executor-base §3.2 段会话规则，read spec_lock），
      重跑两个 checker（仅该页），mark-page P<NN> done
   d. 无断层 → 跳过

2. 全部边界对处理完，append note：'boundary-coherence done, regen=<页号清单>'
```

主会话只读 `generation_state.py status` 确认无新增 `failed`/`needs-manual`（边界会话的 note 也会出现在 state 里）。

### 6.2 讲者备注生成

按段并行生成讲者备注（每段会话写自己段的 `notes/<NN>_*.md`），最后主会话合并为 `notes/total.md`（按页序）。或主会话串行批量写 `notes/total.md` 保证叙事连贯（500 页备注本身也是重输出，可分章并行）。

```bash
# 合并后跑现有拆分脚本
python3 ${SKILL_DIR}/scripts/total_md_split.py <project_path>
```

**✅ 检查点** —— `svg_output/` 完整 + 边界连贯 + `notes/total.md` 就绪，进入阶段 7。

---

## 阶段 7：后处理与导出

沿用现有三命令流水线（天然批量，500 页只是更长耗时）：

```bash
python3 ${SKILL_DIR}/scripts/total_md_split.py <project_path>
python3 ${SKILL_DIR}/scripts/finalize_svg.py <project_path>
python3 ${SKILL_DIR}/scripts/svg_to_pptx.py <project_path>
```

**导出后透明报告**：

```bash
python3 ${SKILL_DIR}/scripts/generation_state.py status <project_path>
```

输出 `X done / Y needs-manual / Z repaired` 清单。`needs-manual` 页在 PPTX 中为虚线占位，用户可手动补。

**✅ 检查点 —— 并行执行完成**：
```markdown
## ✅ 并行生成完成
- [x] design_system + 锚点已就绪且锚点经人工审批
- [x] 段表建立（N 段，disjoint）
- [x] 并行生成完成（M 页 done / K 页 needs-manual）
- [x] 段校验 + 修复完成
- [x] 边界连贯 + 讲者备注合并
- [x] PPTX 已导出
- [ ] **下一步**：向用户报告 needs-manual 清单（若有）
```

---

## 容错机制（故障层，从细到粗）

1. **逐页进度** — `generation_state.json` 记录每页状态；任意点崩溃可续（见阶段 8 resume）
2. **段级检查点** — 段通过校验即 `done`，不回滚已验证成果
3. **修复预算** — 每页 3 次修复尝试；超限升级
4. **升级降级** — 段反复失败 → `degraded` → 主会话 spawn 修复 worktree 会话兜底，不影响其他段
5. **锚点不可变** — 审批后冻结；锚点问题触发人工决策
6. **一致性评分** — 每页漂移分超阈值进修复
7. **边界连贯扫描** — 段间末页+首页由**边界连贯 worktree 会话**复核（不回主会话）
8. **不阻塞整 deck** — 单页超预算 → `needs-manual` + 占位 SVG → deck 照常导出
9. **透明报告** — 导出后 `generation_state.py status` 输出完整清单

## 阶段 8：中断恢复

任意阶段崩溃后，新会话输入 `继续生成 projects/<name>`（见 [`resume-execute.md`](./resume-execute.md)）。若 `generation_state.json` 存在，按 state 续点：

```bash
python3 ${SKILL_DIR}/scripts/generation_state.py resume <project_path>
```

输出未完成段/页清单——只补生成缺失部分，已完成段不重跑。

## 硬规则

- ❌ **段 disjoint** — 两段不得写同一 `P<NN>`；`generation_state.py` 强制拒绝
- ❌ **锚点只读** — 段 agent 不得编辑锚点 SVG；有疑问 emit warning
- ❌ **产出回写主项目** — 段会话产出落主项目 `svg_output/`，不留在 worktree
- ❌ **不绕过校验** — 段必须过 quality + consistency 双 checker 才能 `done`
- ❌ **主会话不生成 SVG（除锚点）** — 页级产出（生成 / 修复 / 边界重生）只在 worktree 会话内；主会话不读 SVG 内容、不跑 checker、不读完整 state 文件（见 §主会话瘦身契约）。与 SKILL.md Rule 6 的并行例外同源：design_system + 锚点 + consistency_checker 三者替代了主会话连续上下文
- ⚠️ **页数 < 60 不走本工作流** — 小 deck 用单代理流程（SKILL.md Step 6 默认路径），纪律不变
- ⚠️ **条件放开需齐备** — design_system + 锚点 + consistency_checker 三者缺一，回退单代理
