---
description: Phase B 入口——在新的聊天会话中恢复 PPT 执行，此时 Phase A（SKILL.md Step 1–5）已在上一会话中完成。从磁盘读取项目状态并运行 Step 6 + Step 7，不携带 Phase A 的上下文。
---

# 恢复执行工作流

> 独立的 Phase B 入口。当 Phase A（SKILL.md Step 1–5）已在上一会话中完成，用户希望继续推进 SVG 生成 + 导出时运行。从磁盘加载项目状态，在干净的会话中执行 Step 6 + Step 7。

本工作流**独立运行**：它从一次全新的聊天开始负责 Phase B——不需要上游会话上下文。通过把 SVG 生成隔离到独立会话，模型可以省下 20–40K 的上下文预算，因为不必再携带 Phase A 的八项确认对话、图像搜索/抓取结果、以及策略师参考资料。

## 何时运行

用户打开一次新的聊天，给出一个包含项目路径并表达"继续"语义的短语。识别以下任一模式：

| 模式 | 示例 |
|---|---|
| `"继续生成 projects/<project_name>"` | `"继续生成 projects/ppt169_joe_hisaishi"` |
| `"resume execution projects/<project_name>"` | `"resume execution projects/ppt169_joe_hisaishi"` |
| 项目路径 + 任一 `"继续 / 恢复 / 继续做 / 接着做"` 语义 | `"把 projects/ppt169_joe_hisaishi 继续做完"` |

**前置条件**：Phase A 必须在指定项目中已经完成。在 Step 1 通过文件存在性校验；当状态缺失时**不要**自动触发 Phase A。

---

## Step 1：健全性检查

在做任何事之前，先校验项目的 Phase A 产物：

| 文件 / 目录 | 何时必需 | 原因 |
|---|---|---|
| `<project_path>/spec_lock.md` | 始终 | 策略师的执行契约；执行器按页读取 |
| `<project_path>/design_spec.md` | 始终 | §IX 页面大纲；执行器交叉引用 |
| `<project_path>/images/` | `spec_lock images` 引用了任意图片时 | 图片必须存在才能嵌入 |
| `<project_path>/templates/` | `spec_lock page_layouts` / `page_charts` 引用了任意资源时 | 版式 / 图表 SVG 在批量预读时需要 |

若任何必需产物缺失 → 报告是哪些并停止。**不要**自动回退到 Phase A；用户必须在原会话中完成 Phase A，或明确重启。

---

## Step 2：加载 SKILL.md，从 Step 6 继续

```
Read ${SKILL_DIR}/SKILL.md
```

然后跳转到 `### Step 6：执行器阶段`，按文档流水线运行：

- 阅读参考资料（`executor-base` + `shared-standards` + `modes/` 下已锁定的 `mode` 文件 + `visual-styles/` 下已锁定的 `visual_style` 文件 + `image-layout-spec` + `svg-image-embedding`）
- 设计参数确认
- 生成前批量预读（`spec_lock` 引用的每一个版式 / 图表 SVG）
- 逐页重读 `spec_lock` + 顺序生成页面
- 质量检查闸口
- 讲者备注生成
- Step 7：后期处理与导出（`total_md_split` → `finalize_svg` → `svg_to_pptx`）

新会话会承担重新阅读参考资料的成本（~14K tokens），但通过丢弃 Phase A 的累积上下文，能换回多得多的预算。综合下来，无论窗口压力还是每页的推理预算都更宽裕。

**源材料**：Phase B 是全新会话；`<project_path>/sources/<file>.md` 不在上下文中。执行器在制作逐页内容时**应当**读取相关 `sources/` 文件——其中保存着让骨架大纲变成有血有肉的幻灯片所需的具体事实、引语、姓名和细节。`design_spec.md §IX` 只承载每页意图；源材料承载质感。Phase A → Phase B 的拆分正是为了腾出上下文预算，专门服务于此类高质量润色。

> 注意：本工作流不复制 Step 6 / Step 7 的内容。SKILL.md 才是权威流程；resume-execute 只增加恢复入口（上述"何时运行" + Step 1 健全性检查）以及上面的源材料指引。

---

## Step 3：交回

当 Step 7 完成且 `exports/<project_name>_<timestamp>.pptx` 生成后，工作流结束。向用户报告导出路径。

如果 deck 包含数据图表，按 SKILL.md 文档说明，[`verify-charts`](verify-charts.md) 工作流会在 Step 6 与 Step 7 之间运行——恢复模式与连续模式的处理方式相同。