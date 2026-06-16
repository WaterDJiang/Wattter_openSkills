# Lint 规范

本文件定义 Lint 模式的检查项、判定逻辑、修复建议。

## 三档扫描深度

| 档位 | 项数 | 用途 | 耗时 |
|:---|:---|:---|:---|
| **轻量** | 7 项 | Compile 第零步内置自检；日常快查 | 2-3 分钟 |
| **深度** | 16 项（含轻量 7 项）| 周期性大检；发布前；接手别人的 wiki | 5-10 分钟 |
| **聚焦** | 用户点名的 1-3 项 | 已知问题精确排查 | 因项而异 |

## 严重度分级

| 级别 | 定义 | 处置 |
|:---|:---|:---|
| **error** | 影响查询正确性 / 链接可达 / 合并正确性 | 必须修，否则 wiki 不可信 |
| **warning** | 影响一致性 / 可维护性 / 协作 | 建议修，但不修也能用 |
| **info** | 风格 / 优化提示 | 看情况，可忽略 |

---

## 轻量 lint 七项（Compile 第零步内置）

### L1. frontmatter 必需字段缺失 [error]

**判定**：所有 `wiki/kps/**/*.md`（排除 `_module-summary.md` 和 `index.md`）必须有 frontmatter 且包含：`kp_name`、`module`、`knowledge_domain`、`knowledge_type`、`tags`、`source_marking`。

**实现**：grep frontmatter，逐字段检查；若该目录 CLAUDE.md 定义了额外必需字段，一并检查。

**修复**：可自动——按文件内容推断字段值并补齐；推断不出的字段填 `[待补]` 让用户人工 review。

### L2. source_marking 取值非法 [error]

**判定**：`source_marking` 仅允许 `已提取` 或 `AI补全` 两个值。

**修复**：可自动——根据 body 中是否有原文引用判断；二义性用例标 `[待人工裁决]`。

### L3. index.md 漂移 [error]

**判定**：`wiki/indexes/index.md` 的「课程清单 / 领域索引 / 类型索引」段中列出的文件路径，与 `wiki/kps/**` 实际存在的文件做对照：
- index 列了但文件不存在 → 死链
- 文件存在但 index 没列 → 漏录

**实现**：从 index.md 的 markdown 表格里抽链接，与 `find wiki/kps -name "*.md"` 结果对比。

**修复**：可自动——重建 index 的对应段（保留三线/活动等手写段不动）。

### L4. log.md 缺失或格式异常 [warning]

**判定**：`wiki/indexes/log.md` 必须存在，且最近一条记录的格式符合 `references/log-spec.md`（必填字段齐全：源 / 产出 / 路径 / 新增 / 冲突 / 未完成）。

**修复**：可自动——若文件缺失，用 `assets/log-template.md` 初始化空模板；格式异常仅报告，不擅改历史。

### L5. 模块文件夹缺 _module-summary.md [warning]

**判定**：每个 `wiki/kps/*-knowledge-points/{两位序号}-*/` 下必须有 `_module-summary.md`。

**修复**：半自动——列出缺失的模块，用户确认后用 `assets/module-summary-template.md` 生成空骨架，三线和关联段标 `[待补]`。

### L6. 知识点文件命名违规 [warning]

**判定**：
- 不能有序号前缀（如 `01-选题三维度.md` 应为 `选题三维度.md`，原因见 SKILL.md 文件命名规范）
- 不能含空格、不能含 `/`、不能含 emoji
- `.md` 扩展名必须小写

**修复**：半自动——列出违规文件给用户，确认后批量重命名，**同时更新所有引用此文件的 markdown 链接**。

### L7. 跨知识点链接失效 [error]

**判定**：扫描所有 kp 文件的 markdown 链接 `[xxx](./yyy.md)`，对每条做文件存在性检查。

**实现**：用相对路径解析，落到磁盘判断。

**修复**：半自动——失效链接列出，可能的原因有三种：
- 目标文件被改名 → 用户提供新路径后批量替换
- 目标文件被删除 → 链接转为纯文本或删除
- 链接本身写错 → 列出可能匹配的现有文件供用户选

---

## 深度 lint 增补九项（共 16 项）

### L8. 孤儿卡片 [warning]

**判定**：在 `wiki/kps/**` 中，**未被任何 index、_module-summary、其他 kp 链接**的文件。

**实现**：grep 所有 markdown 文件中的链接，构造引用图；孤儿 = 没有任何入边的文件（除 index.md 外）。

**修复**：半自动——孤儿可能是：
- 真的被遗忘了 → 加入对应模块的 _module-summary
- 应该删除 → 删除并 log
- 是临时草稿 → 移到 `wiki/.drafts/`（不在主索引内）

让用户对每个孤儿选一个动作。

### L9. 陈旧 source_marking [info]

**判定**：标记为 `[AI补全]` 但 `wiki/concepts/{同名}.md` 存在或 `raw/` 中已有对应原文的卡片，应该升级为 `[已提取]`。

**实现**：对每张 `[AI补全]` 卡片，搜 raw/ 与 concepts/ 是否有同名/近义内容。

**修复**：半自动——逐张让用户确认是否升级；用户确认后更新 frontmatter（加 `upgraded_at`）和 body 中对应行的标记。

### L10. 冲突块未决 [error]

**判定**：grep `> ⚠️ 与上次产出冲突` 块；超过 30 天未处理的冲突视为 error。

**实现**：用 frontmatter 的 `last_compiled` 与今天对比。

**修复**：必须手动——列出所有未决冲突，给修复指引（"二选一保留 / 改写为更通用表述 / 拆为两张卡"），但不动文件。

### L11. 跨课程同义未归并 [warning]

**判定**：扫描所有 kp 的 `kp_name` 字段，做规范化匹配（去标点、统一大小写、去常见后缀如"原则/方法/法则"）；同义聚类 ≥ 2 张但 `wiki/concepts/{}.md` 不存在 → 候选归并。

**实现**：相对昂贵的步骤，仅深度 lint 跑。同义判定用规则匹配 + 用户确认，不依赖嵌入。

**修复**：半自动——列出每组同义簇，用户确认后抽到 `wiki/concepts/`，按 `references/merge-incremental.md` 情况 3 处理。

### L12. frontmatter 字段值越界 [warning]

**判定**：
- `knowledge_type` 不在 `框架/模型/原则/方法/流程/工具/概念` 七选一内
- `knowledge_domain` 在该目录历史值集合中是孤值（仅出现 1 次）→ 可能是手抖错别字

**实现**：枚举所有 kp 的 domain，统计频次；频次=1 的标 info。

**修复**：半自动——列出可疑值，提供该目录的高频 domain/type 列表让用户选。

### L13. 三线缺失或空泛 [warning]

**判定**：
- `_module-summary.md` 缺三线段
- 三线段内容是 `[待补]` 或 `{...}` 占位符
- 三线表述是无信息量的套话（"本模块逻辑递进""情感升华"——靠正则黑名单识别）

**修复**：必须手动——列出缺位的模块，给重写指引，不动文件。

### L14. 关联单边 [warning]

**判定**：A 卡片说"前置依赖：B"，但 B 卡片的关联段没有写"被 A 依赖"。关联应双向（SKILL.md 第八步规定）。

**实现**：扫描所有关联段，构造关联图，找单边。

**修复**：可自动——补上反向关联即可，幂等。

### L15. raw 未编译 [info]

**判定**：对比 `raw/**` 实际文件与 `wiki/indexes/log.md` 中所有"源"字段引用过的文件；raw 中存在但从未被引用的文件 → 可能未编译。

**实现**：grep log.md 的所有 `raw/...` 路径，与 `find raw/` 取差集。

**修复**：仅提示——列出未编译的 raw 文件，建议用户决定：跑 Compile / 标记为参考资料 / 删除。

### L16. mapping.json 与现实不一致 [warning]

**判定**：仅当目录维护了 `wiki/indexes/mapping.json` 时才检查。
- mapping 里的 raw 路径不存在（源被删 / 改名）
- mapping 里的 wiki 路径不存在
- 存在的 wiki kp 在 mapping 中无 raw 来源（source_files 也为空）

**修复**：可自动——重建 mapping。但因为这是机器索引，重建前必须给用户看 diff，确认后再写。

---

## Lint 实现要点

### 不要做的事

- ❌ 不要为了"让数据好看"修改用户写的 body 内容——lint 只动 frontmatter、index 和链接
- ❌ 不要在 lint 模式下动 raw/——raw 永远不可变
- ❌ 不要无差别批量修——error 可批量，warning 必须逐条让用户看
- ❌ 不要把 lint 报告写进 log.md 主流——单独落盘 `lint-{date}.md`，log.md 只在用户确认修复后写一条 `lint-fix` 摘要
- ❌ 不要在 Compile 第零步跑深度 lint——会让"我就想编译一下"变成漫长等待

### 报告文件结构

`wiki/indexes/lint-{YYYY-MM-DD}.md`：

```markdown
# Lint 报告 — {目标目录}

> 时间：{ISO 时间戳}　|　深度：{轻量/深度/聚焦}　|　扫描项：{N}

## 总览

| 严重度 | 数量 |
|:---|:---|
| error | {N} |
| warning | {N} |
| info | {N} |

## 按类别

### L1. frontmatter 必需字段缺失（error，3 处）

| 文件 | 缺失字段 | 修复建议 |
|:---|:---|:---|
| wiki/kps/.../四象限法.md | knowledge_domain, tags | 自动补齐 |

（每个触发的检查项一节，未触发的检查项不出现）

## 修复建议执行顺序

1. 先修 error（3 类，9 处）—— 自动批量
2. 再修 warning（5 类，14 处）—— 半自动逐条
3. info 项（2 类，6 处）—— 看情况

## 用户操作入口

```
# 全部自动修复（仅 error 中可自动的）
"修复所有可自动的 error"

# 逐条审 warning
"过一遍 warning 让我决定"

# 跳过 info
"info 先不管"
```
```

### 关键的"既不太累又不漏"的原则

- **轻量 lint** 是 Compile 第零步必跑的——成本不能高于 5% 编译总时长。所以只查 frontmatter / index / 链接这种**结构性**问题，不查内容。
- **深度 lint** 用户主动跑——可以慢，但要给清楚的进度提示（"扫描中：L11 跨课程同义识别，已分析 124/300 张..."）。
- **聚焦 lint** 用于排障——比如用户说"我感觉 index 不对了"，只跑 L3。
