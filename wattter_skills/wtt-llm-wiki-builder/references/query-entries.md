# 查询入口设计 — 让 wiki 可被检索

本 skill 的产出必须支持**多维检索**。检索是 wiki 的核心使用方式，但**不是本 skill 的模式**——它由消费方完成（LLM 读 index + grep frontmatter，或 ripgrep / Obsidian / 任何 markdown 检索工具）。

> **设计目标**：本 skill 的产出在以下三种检索方式下都能工作
> 1. **LLM 检索**：读 `wiki/indexes/index.md` 全文 + 单卡 frontmatter
> 2. **grep 检索**：`rg 'knowledge_domain: AI' wiki/` 跨目录查字段
> 3. **工具检索**：Obsidian / Logseq / 任何支持双向链接和 frontmatter 的 markdown 工具
>
> 规模升级路径：wiki 长到数百页、index 段加载变重时，可接本地搜索引擎（如 qmd——BM25+向量混合检索，有 CLI 和 MCP 两种形态）。这是可选升级，中等规模（约百份来源、数百页面）下 index + grep 完全够用。

## 设计原则

1. **index 是入口，不是替代**：index.md 给出"该往哪里找"的指引，但不复制卡片正文
2. **frontmatter 是单点真相**：任何可被检索的字段只放在 frontmatter，不在 body 里复述
3. **目录约定一致**：跨目录查询要靠 grep，所以字段名不能因目录而异
4. **增量更新**：index.md 按段 patch，不整体重写（除非用户说"重建"）

---

## 主语境对应的 index 段

四种主语境共用同一份 `wiki/indexes/index.md`，但**段落按主语境裁剪**：

### 课程语境

```markdown
# {目录名} — 知识库总入口（课程语境）

> 最近编译：{YYYY-MM-DD}　|　课程：N　|　知识点：M　|　模块：K

## 1. 课程清单
| 课程 | 模块数 | 知识点数 | 入口 |
|:---|:---|:---|:---|
| {课程名} | 5 | 32 | [→](../kps/{课程名}-knowledge-points/index.md) |

## 2. 领域索引（按 knowledge_domain）
| 领域 | 知识点数 | 列表（链接） |
|:---|:---|:---|
| AI | 12 | [Prompt 工程](...), ... |

## 3. 类型索引（按 knowledge_type）
| 类型 | 数量 | 列表 |
|:---|:---|:---|
| 框架 | 9 | ... |

## 4. 跨课程同义概念
| 概念 | 出现于 | 入口 |
|:---|:---|:---|

## 5. 共享素材
| 素材类型 | 数量 | 入口 |
|:---|:---|:---|

## 6. 最近活动
| 日期 | 动作 | 摘要 |
|:---|:---|:---|
```

### 知识库语境

```markdown
# {目录名} — 知识库总入口（知识库语境）

> 最近编译：{YYYY-MM-DD}　|　主题：N　|　概念：M　|　模型：K　|　案例：J

## 1. 主题索引
| 主题 | 卡片数 | 入口 |
|:---|:---|:---|
| {主题名} | 12 | [→](../concepts/{主题}.md) |

## 2. 领域索引（按 knowledge_domain）
（同课程语境，但字段来源是 case/model/concept）

## 3. 类型索引（按 knowledge_type）
（含 框架/模型/原则/方法/流程/工具/概念/案例）

## 4. 概念索引（concepts/）
| 概念 | 关联卡片数 | 入口 |
|:---|:---|:---|
| MECE 原则 | 5 | [→](../concepts/MECE原则.md) |

## 5. 共享素材
（必填，wiki 核心是素材可复用）

## 6. 按知识时间排序（同体系归组）
| 知识时间 | 卡片 | 类型 | 状态 |
|:---|:---|:---|:---|
| 2026-08-20 | [RAG 架构](../models/RAG架构.md) | 模型 | ✅ 最新 |
| 2026-05-11 | [检索增强早期实践](../models/检索增强早期实践.md) | 模型 | ⚠️ 已被 [[RAG 架构]] 深化 |

## 7. 最近活动
```

### 个人笔记语境

```markdown
# {目录名} — 知识库总入口（个人笔记语境）

> 最近编译：{YYYY-MM-DD}　|　笔记：N　|　时间跨度：{起始} - {至今}

## 1. 时间线
| 日期 | 笔记 | 类型 | 主题 |
|:---|:---|:---|:---|
| 2026-08-20 | [MECE 的局限](../notes/2026-08-20-MECE的局限.md) | 反思 | 方法论 |
| 2026-08-15 | [《XX 书》读书笔记](../notes/2026-08-15-XX书.md) | 摘录 | 读书 |

## 2. 项目分组
| 项目 | 笔记数 | 入口 |
|:---|:---|:---|
| {项目名} | 8 | [→](../notes/{项目}/index.md) |

## 3. 主题分组
| 主题 | 笔记数 | 列表 |
|:---|:---|:---|
| {主题} | 5 | ... |

## 4. 笔记类型索引（按 note_type）
| 类型 | 数量 | 列表 |
|:---|:---|:---|
| 摘录 | 23 | ... |
| 反思 | 11 | ... |
| 会议 | 8 | ... |
| 观察 | 5 | ... |

## 5. 共享素材
（金句、引用、可复用观察）

## 6. 最近活动
```

### 综合语境

四种段都保留，按目录实际内容裁剪：

```markdown
# {目录名} — 知识库总入口（综合语境）

> 最近编译：{YYYY-MM-DD}　|　课程：N　|　主题：M　|　笔记：K　|　概念：J

## 1. 主题/课程/项目索引（合并）
| 类别 | 名称 | 卡片数 | 入口 |
|:---|:---|:---|:---|
| 课程 | {课程名} | 32 | [→]... |
| 主题 | {主题名} | 12 | [→]... |
| 项目 | {项目名} | 5 | [→]... |

## 2. 领域索引
（同上）

## 3. 类型索引
（同上）

## 4. 概念索引（必填）
（同知识库语境）

## 5. 共享素材
（同知识库语境）

## 6. 时间线（如有个人笔记）
（同个人笔记语境）

## 7. 最近活动
```

---

## 单课程 / 单主题的二级 index

`wiki/indexes/index.md` 是总入口。**当主语境下有子结构**（一门课程/一个主题/一个项目），在子目录再放一份 `index.md` 作为二级入口：

```
wiki/kps/{课程名}-knowledge-points/index.md   # 课程语境
wiki/concepts/{主题}/index.md                 # 知识库语境
wiki/notes/{项目}/index.md                    # 个人笔记语境
```

| 文件 | 范围 | 主用途 |
|:---|:---|:---|
| `wiki/indexes/index.md` | 整个目标目录 | 总入口；按主语境多维索引 |
| `wiki/{语境}/{子结构}/index.md` | 单个课程/主题/项目 | 该子结构的内部模块表、笔记列表、跨节关联 |

每次 compile 后，**两层 index 都要更新**（或仅更新有改动的层）。

---

## 检索场景与对应入口

| 用户问 | LLM/grep 行动 |
|:---|:---|
| "这个 wiki 里关于 AI 的卡片有哪些？" | 读 `wiki/indexes/index.md` 领域段；或 `rg 'knowledge_domain: AI' wiki/` |
| "所有框架类的卡片？" | 读类型索引段；或 `rg 'knowledge_type: 框架' wiki/` |
| "MECE 原则在哪些地方出现过？" | 读 `wiki/concepts/MECE原则.md` 的 `appears_in` 字段；或 `rg 'MECE' wiki/concepts/ wiki/kps/ wiki/models/` |
| "这门课的整体结构？" | 读 `wiki/kps/{课程}-knowledge-points/index.md`（二级 index） |
| "上次关于 X 的笔记是什么时候的？" | 个人笔记语境下读时间线段；或 `rg -l 'X' wiki/notes/ \| head` |
| "这条原则的原文出处？" | 读对应卡片的 frontmatter `source_files` + `source_quote` |
| "X 领域哪个模型/说法最新？" | 读 index「按知识时间排序」段（同体系归组）；或 `rg 'knowledge_date' wiki/models/` 排序 |
| "X 还成立吗 / 有没有被推翻？" | `rg 'superseded_by' wiki/` 查 X；被标 → 读新卡「演进史」给演进链；未标 → 按知识时间给最新结论并注明判断依据 |
| "X 和 Y 什么关系（新旧）？" | 读两卡 `knowledge_date` + 互相的关联/演进史；标注时间先后与地位关系（取代/互补/并存） |
| "上次编译是什么时候、做了什么？" | 读 `wiki/indexes/log.md` 最近一条 |
| "wiki 演化的时间线？" | `grep "^## \[" wiki/indexes/log.md`——统一前缀保证 unix 工具可解析 |
| "哪些 raw 文件还没被编译？" | 对比 `mapping.json` 的 key 与 `raw/` 实际文件列表 |
| "跨主题找某个概念的定义" | 读 `wiki/concepts/{概念}.md`（概念卡是跨主题入口） |
| "AI 领域的框架类卡片有哪些？" | 交叉查：grep `knowledge_domain: AI` AND `knowledge_type: 框架`；或读 index 两段交叉 |

---

## 检索输出的时效呈现规则（知识卡片必守）

只要输出涉及知识卡片清单（回答、对比、盘点），时效呈现按 `references/knowledge-freshness.md` 第 5 节执行：

1. **带「知识时间」列**——用 `knowledge_date`，不用 `last_compiled`（编辑时间会误导"哪个新"）
2. **同体系归组**——同一谱系的卡片放一起按时间升序（旧→新，演进链可读）；跨体系按时间倒序（新→旧，最新优先）
3. **状态标注**——最新标 ✅ 优先使用；被取代的标 `⚠️ 已被 [[新卡]] 深化`，**保留展示**（旧版有历史与语境价值，不隐藏）
4. **grep 直查**——`rg -l 'superseded_by'` 一步拿到全部被取代卡；`rg 'knowledge_date: 2026-0[6-8]'` 按时间段过滤

## 回答归档（Query → Archive）

检索回答本身也是知识资产——**好的回答该归档回 wiki**，否则它消失在聊天记录里，复利链条断裂。

| 回答形态 | 处理 |
|:---|:---|
| 单卡转述（读一张卡即可回答） | 不归档——卡片已是资产 |
| 跨卡综合 / 对比表 / 新连接 / 分析判断 | 回答后**提议归档**：「要把这个回答沉淀进 wiki 吗？」用户同意才做 |

归档动作：

1. 回答落卡——综合分析 → `wiki/notes/`（note_type: 分析）；反复被用的对比框架 → 升级为 model 卡；跨卡共享的结论 → concept 卡
2. 卡内回链本次引用的所有来源卡片（关联双向写回）
3. index 对应段补条目；log 追加 `query: {问题摘要}（已归档 → 路径）`

> 归档是"提议后执行"，不是"静默执行"——用户只想要个答案时，不要强行产卡。

---

## 编译时如何更新 index 段落

第十二步执行时，按段落分别 patch：

| 段 | 更新方式 |
|:---|:---|
| 主题/课程/项目清单 | 新增 → 加一行；已有 → 更新卡片数 |
| 领域索引 | 把本次新卡片按 domain 插入对应行末；新 domain 新增一行 |
| 类型索引 | 同上，按 type |
| 概念索引 | 仅当本次产生/更新 concepts/ 卡时操作 |
| 共享素材 | 仅当 `wiki/materials/` 有新增时更新计数 |
| 时间线 | 仅个人笔记/综合语境 |
| 最近活动 | 把本次 log 条目摘要前置插入，保留前 5 条 |

**原则**：增量 patch，不重写整个 index.md。除非用户显式说"重建 index"。

---

## 多维检索的 frontmatter 契约

为了让 LLM / grep 都能完成大多数查询，frontmatter 字段名**跨目录必须一致**：

### 通用必填字段

```yaml
# 所有卡片共有的索引字段
name: <唯一>                     # 卡片唯一名（与文件名一致）
type: <kp/case/model/concept/note/material>
knowledge_date: <YYYY-MM-DD>      # 知识发生时间（知识卡片必填；note 卡由 date 承担）
created: <YYYY-MM-DD>             # 创建时间（个人笔记语境必填）
last_compiled: <YYYY-MM-DD>       # 最后编译时间（编辑时间，不承担时效语义）
source_marking: <[已提取]/[AI补全]>
```

### 课程语境字段（kp/case/model/concept）

```yaml
kp_name: <唯一>                   # kp 卡片
module: <所属模块>
knowledge_domain: <单选>
knowledge_type: <单选>
tags: [<细粒度，自由>]
source_files: [<raw 路径>]
source_quote: |                   # 可选（深度萃取启用时）
  "..."
```

### 知识库语境字段（case/model/concept）

```yaml
case_name: <唯一>                 # case 卡片
industry: <行业>
scenario: <场景>
outcome: <结果>

model_name: <唯一>                # model 卡片
origin: <来源/出处>

concept_name: <唯一>              # concept 卡片
appears_in: [<卡片路径>]
```

### 个人笔记语境字段（note）

```yaml
note_name: <唯一>
note_type: <摘录/反思/会议/观察/问题清单/日记/引用/思考>
topic: <主题/项目>
date: <YYYY-MM-DD>
related: [<其他笔记路径>]         # 笔记间关联（松散即可）
```

### 可选字段（所有卡片）

```yaml
source_files: [<raw 路径>]
source_quote: |                   # 深度萃取启用时
  "..."
upgraded_at: <YYYY-MM-DD>         # 标记升级查询
confidence: <high/medium/low>     # AI 补全时的把握度
knowledge_date_basis: <exact/approximate>  # 近似回填标记（精确推断不写）
superseded_by: "[[新卡名]]"        # 被取代时填（用户确认后），检索时可 grep
```

---

## grep 友好的额外规则

为了让外部 grep 工具能跨目录检索：

| 规则 | 原因 |
|:---|:---|
| frontmatter 字段名不因目录而异 | 跨目录 grep 必须靠统一字段名 |
| 标签用 kebab-case 或 snake_case | 避免空格/中文标点导致 grep 难匹配 |
| 路径用相对路径 | wiki 移动/重命名时链接不断 |
| 不在 body 里复述 frontmatter 字段 | 单一真相原则；grep 时不重复计数 |
| 中文主题加英文别名 | 跨语言检索时更稳 |

---

## 反例：不要这样做

- ❌ 把所有查询逻辑塞进 index.md 一段巨表——分段是为了让 LLM 部分加载
- ❌ 用 JSON 当主索引——markdown 表格对 LLM 更友好且能直接渲染
- ❌ 让 frontmatter 字段名因目录而异——跨目录 grep 会断链
- ❌ 在卡片 body 里复述 frontmatter 里的字段——单点真相只放在 frontmatter
- ❌ 默认只有"课程清单"段（这是课程语境的特例，其他语境用对应段）
- ❌ 把个人笔记的时间线写在卡片 body 里——应该在 frontmatter `date` + index.md 时间线段
