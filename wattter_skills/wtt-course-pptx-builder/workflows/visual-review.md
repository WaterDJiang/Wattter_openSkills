---
description: 通过并行子代理对每页按评分细则做视觉自检。在执行器之后、后期处理之前运行。
---

# 视觉自检工作流

> 独立的生成后步骤。目标：通过 AI 子代理按固定评分细则视觉自查每张渲染好的幻灯片，并施加原子化的位置/间距修复，从而减少人工迭代。
>
> 读取 `<project>/svg_output/<page>.svg` 与每页的预渲染 PNG，然后要么施加修复、要么标记 `needs_human`。**绝不触碰** 品牌决策、版式结构或其他文件。
>
> 本工作流**独立运行**——可以在只给出 `<project_path>` 的全新聊天会话里调用，不依赖任何上游会话上下文。

## 定位

这是**可选的辅助循环**，仅在明确请求时启动。主流水线（SKILL.md Step 1–7）不会调用它；仅当用户在导出前明确要求对生成的 SVG 做一轮视觉复检时才触发。

**Token 成本**：每批子代理会重读评分细则 + `design_spec.md` + `spec_lock.md`，并处理 K 对 SVG+PNG。对一个 20 页 deck、K=5 的运行，预计在主生成之外额外消耗 100–150K 输入 token。

## 何时运行

- 执行器（SKILL.md Step 6）已完成所有页面
- `svg_quality_checker.py` 已通过
- 后期处理（`finalize_svg.py`、`svg_to_pptx.py`）**尚未** 运行
- 用户明确要求视觉复检

若 deck 含数据图表，请先运行 [`verify-charts`](./verify-charts.md)——visual-review 关注视觉节奏 / 冲突 / 对齐，不做图表坐标数学。

## 何时不运行

- 项目还没有 `svg_output/<page>.svg` —— 先完成执行器
- `svg_quality_checker.py` 未跑或失败 —— 先修复静态违规
- 用户已经通过 `live-preview` 工作流应用过批注、且处于固定编辑循环 —— 直接描述改动，不要重新触发评分
- 用户未主动要求 —— 不要基于推断的模型能力或 deck 体量自动调用

---

## 前置条件

```bash
# 1. 安装 playwright + chromium（PNG 渲染器）
pip install playwright
python3 -m playwright install chromium

# 2. 为本项目启动 live-preview 服务（提供内联后的 SVG 拉取）
python3 ${SKILL_DIR}/scripts/svg_editor/server.py <project_path> --no-browser
# （每项目单实例——若已在运行，跳过）
```

渲染器（`visual_review.py`）**不会**自动启动 live-preview 服务。它要求服务能在 `http://localhost:5050` 访问到（可用 `--server-url` 覆盖）。

> **为什么用 playwright 而非 cairosvg**：cairo 的文本 API 没有字体回退链，对任何依赖系统字体回退（Microsoft YaHei / PingFang SC 等）的 deck，CJK 字符会渲染成豆腐块。Playwright 驱动真实 chromium，产出与 live-preview 浏览器一致的图像——这是双语 deck 唯一能保留保真度的方案。

---

## Step 1 — 预渲染全部 PNG

```bash
python3 ${SKILL_DIR}/scripts/visual_review.py <project_path>
```

为每页向 `<project_path>/.preview/<page>.png` 写入一份 1280×720 的 PNG，`<use data-icon>` 内联、`<image href>` 解析方式与 live-preview 浏览器看到的一致。渲染通过项目本地的文件锁串行化——可安全并发调用。

退出码：

- `0` —— 全部页面已渲染
- `2` —— live-preview 服务不可达（按前置条件启动）
- `3` —— 未安装 playwright python / chromium（或浏览器启动失败）
- `4` —— 出现一个或多个页面级渲染失败（见 stderr；部分产物已落盘）

若某页 JSON 汇总中带 `"all_background": true`，说明该页渲染成空白——继续之前先排查（`<use>` 引用损坏、图像资源缺失等）。

---

## Step 2 — 组建复检团队

创建团队并派发一个协调代理。协调代理把 N 页按 ≤ K 页一批切分（默认 **K = 5**），并**并行**生成每批一个子代理（单条消息里发出 `ceil(N/K)` 个 `Agent` 调用）。每批子代理把固定输入（评分细则 + `design_spec.md` + `spec_lock.md`）只读一次，然后顺序处理自己分配到的页面。

```text
TeamCreate(team_name="visual-review-<project>", agent_type="orchestrator")
Agent(
  team_name="visual-review-<project>",
  subagent_type="general-purpose",
  name="orchestrator",
  prompt=<orchestrator-prompt>,
)
```

协调代理的 prompt 必须是自包含的，并且是**唯一**一处说明派发形态、批次大小、禁止清单的位置——评分细则（`references/visual-review.md`）定义这些 prompt 必须满足的契约。必填字段（全部使用绝对路径）：

- `<project_path>` —— 项目根目录
- 完整页码列表，每页带 `page_role`（解析 `<project>/design_spec.md` §IX 大纲；若 §IX 不存在，则把每页默认为 `content` 并在最终报告中标注）
- 批次大小 `K`（默认 5；在大型 deck 上做 token 敏感型运行时可提升到 10；短 deck 高保真运行时降到 3——见评分细则 §6.1）
- 每页迭代预算（默认 1；高风险 / 最终交付运行才用 2——见 [附录：迭代循环](#appendix-iteration-loop-opt-in)）
- 评分细则路径：`${SKILL_DIR}/references/visual-review.md`
- 派发契约引用：评分细则 [§6](../references/visual-review.md#6-dispatch--messaging-contract)（批量并行生成、自包含 prompt、空闲时强制 `SendMessage`、匿名名称容忍）
- 子代理禁止清单：不得编辑任何其他页面、`design_spec.md`、`spec_lock.md`、`animations.json`、`image_prompts.json` 或 `images/`

**宿主兼容性**：`TeamCreate` 与 `SendMessage` 是 Claude Code 专属的多代理原语。在没有这些原语的宿主（Cursor、VS Code + Copilot、Codebuddy 等）上，主代理顺序处理各批——同样的切分、同样的每批 prompt、不做并行派发。共享固定输入带来的 token 节省仍然成立；墙钟时间大约按 N/K 倍延长。

---

## Step 3 — 汇总发现

协调代理把汇总的 Markdown 表回传给你（主代理）：

```
| page | role | status | hard_hits | soft_hits | fixes_applied | needs_human_reason |
|------|------|--------|-----------|-----------|---------------|---------------------|
```

状态：

- `ok` —— 页面干净通过，未施加修复
- `fixed` —— 至少施加一次修复，全部 Hard 规则现已通过
- `needs_human` —— 已尝试修复但回滚（规则 §4.2），或违规需要评分细则范围之外的品牌 / 结构决策
- `render_failed` —— 第 0 轮 PNG 健康检查失败（少见；通常意味着渲染器 / 服务问题）
- `prereq_failed` —— 静态检查未运行

加上在 `<project>/.review/brand_review.json` 的品牌 token 汇总（如出现过 §1.1 升级项）——在整轮结束时统一审阅一次，而非逐页审阅。

---

## Step 4 — 决定下一步

对表中每一行：

- `ok` / `fixed` —— 无需动作；SVG 已就地更新（原文件位于 `<project>/.review/backup/<page>.iter<N>.svg`）
- `needs_human` —— 阅读该页 JSON 中的 `needs_human_items[].suggested_fix_summary`，与用户一起决定是否应用或推迟
- `render_failed` —— 仅对该页重跑 `visual_review.py`（`--pages <token>`）；若仍失败，转人工复检
- `prereq_failed` —— 回去跑 `svg_quality_checker.py`

若 `brand_review.json` 非空，那是一次跨 deck 的单点决策（例如把页脚文本色从 `#6E7681` 改成 `#8B949E`——一处改动，全 deck 受益）。做一次即可，然后可选择仅对受影响页面重跑 visual-review。

表格清空后，按 [`SKILL.md`](../SKILL.md) Step 7 继续后期处理：

```bash
python3 ${SKILL_DIR}/scripts/total_md_split.py <project_path>
python3 ${SKILL_DIR}/scripts/finalize_svg.py <project_path>
python3 ${SKILL_DIR}/scripts/svg_to_pptx.py <project_path>
```

---

## 备注与不变量

- **规则唯一权威来源**：[`references/visual-review.md`](../references/visual-review.md)。本工作流文件只是编排——不在这里复述或改写规则。
- **并发**：`visual_review.py` 通过 `<project>/.preview/.render.lock` 串行化渲染。子代理绝不能绕过锁直接调用渲染器。
- **迭代预算**：默认 1 轮迭代。提升到 2 会让渲染成本翻倍、token 成本大致三倍。只在高风险 / 最终交付 deck 上才值得。
- **不可触碰（评分细则 §3）** 由子代理硬性强制。若想让子代理改品牌色之类，**不在本工作流范围**——先手动改，再重新渲染并复检。
- **备份**：每份修改过的 SVG 在 `.review/backup/<page>.iter<N>.svg` 留有回滚锚点。用 `cp` 恢复。
- **评分细则不是设计师**：它捕获冲突、漂移、节奏错误——它不改进一份本就薄弱的版式。若 80%+ 的页都返回 `needs_human`，问题出在设计规范或执行器的版式选择，而非本工作流。
- **Playwright 输出规范**：当某代理直接使用 playwright MCP 工具 `browser_take_screenshot`（在 `visual_review.py` 脚本之外）时，`filename` 参数相对 CWD（通常是仓库根目录）解析——传裸相对路径会在仓库里产生散乱目录。务必传绝对路径：
  - 一次性探测 / 即兴巡检 → `/tmp/probe-<topic>-<n>.png`
  - 项目产物（替代脚本本应产出的文件） → `<project_path>/.preview/<page>.png`（绝对）
  - 绝不写 `<repo>/<anything>.png` 或 `<repo>/<some_dir>/...`——这些会被 `.gitignore` 规则拦下，但清理负担是真实的

  `visual_review.py` 脚本自身能正确处理输出路径；本规则只适用于交互探索或修复期间直接调用 playwright MCP 的场景。

---

## 附录：迭代循环（可选）

默认行为是单轮复检：扫描一次、就地修复、写出报告。[`references/visual-review.md`](../references/visual-review.md) §4.1 中的完整迭代循环支持：

1. 第 1 轮：扫描 + 修复
2. 通过 `visual_review.py --pages <token>` 重新渲染
3. 第 2 轮：复验已修改元素 + 扫描新出现的 Hard 违规
4. 一旦修复引入新的 Hard 违规即回滚

开启方法：在协调代理 prompt 中把迭代预算设为 2（这是对子代理的 prompt 级指令；`visual_review.py` 与 harness 都不会强制）。每多一轮迭代，受影响页的渲染成本大致翻倍、token 成本三倍——仅留给最终交付轮次。