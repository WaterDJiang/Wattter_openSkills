---
name: wtt-llm-wiki-builder
description: >-
  在任意文件夹内构建、编译、维护一个 LLM 友好的 wiki 知识库。三个模式：(1) Build——目录什么都没有或只是散落的 markdown，从零搭建 raw/wiki/CLAUDE.md 范式并完成首批编译；(2) Compile——已有 wiki 范式，把新资料增量编译进去（不覆盖、标冲突、跨域归并、新旧碰撞判定）；(3) Lint——扫描已有 wiki 健康度（孤儿卡片/索引漂移/链接失效/frontmatter 缺字段/陈旧标记/知识时效），输出修复清单。
  支持四种主语境并列：课程（按模块+知识点组织）、知识库（按主题+概念组织）、个人笔记（按主题/时间线/项目组织）、综合（多种混用）。课程语境可选「四点三线」蜂窝矩阵作为萃取骨架；其他语境切换为对应萃取路径。所有产物用 frontmatter + 多维索引（领域/类型/时间/主题/概念/最近活动）+ log 联动，构建出来即可被 LLM/grep/外部检索工具按维度快速定位，支持来源回溯。知识落盘带时效：knowledge_date（知识发生时间）+ superseded_by（被取代标记）+ 新旧碰撞判定（互补合并/取代标链/并存对比），检索输出带知识时间与状态列。查询产生的综合回答可归档回 wiki（回答即资产，复利累积）。
  触发场景：(1) 用户说"整理这个文件夹/把这些资料整理成知识库/给这个目录建个 wiki"；(2) 用户说"编译/蒸馏/萃取/把这份整理进 wiki/更新知识库"；(3) 用户说"体检/lint/扫描/检查 wiki 健康度/找孤儿卡片/索引对不上"；(4) 用户提到"四点三线/蜂窝矩阵/知识点/卖点笑点特点焦点"（仅课程语境）；(5) 用户给出原始资料（课纲、文章、录音稿、案例、笔记、聊天记录、收藏夹）要求结构化沉淀；(6) 用户在已有 wiki 目录问"哪个最新/有没有被推翻/知识时间/新旧关系"，或要求"把这个回答/对比沉淀进 wiki"。
---

# LLM Wiki Builder — 任意文件夹的知识库构建/编译/维护

把任意文件夹变成 LLM 友好的 wiki 知识库。raw/ 存不可变源，wiki/ 存 LLM 拥有的卡片，indexes/ 维持入口与日志。所有产物用 frontmatter 索引、多维 index 联动、log 留痕。**重点不是 wiki 本身，而是 wiki 能否被快速检索**——索引即检索入口。

> **两条复利原则**（本 skill 的底层理念）：
> 1. **知识只编译一次，之后持续保鲜**——新资料不是索引进去等检索，而是读它、萃取它、更新相关既有卡片、标记与旧结论的矛盾；维护记账（交叉引用/摘要更新/新旧标注）全部由编译器完成，这是人维护 wiki 会弃坑、LLM 维护不会的原因。
> 2. **知识落盘就带时间先后**——每张知识卡有 `knowledge_date`（知识发生时间），新旧碰撞时有取代/互补/并存的显式判定，检索能回答"哪个最新、哪个被推翻"。详见 `references/knowledge-freshness.md`。

> **设计原则**：本 skill 是为通用 wiki 而非课程库设计的。课程只是四种主语境之一。"可检索"是 wiki 的核心使用方式，所以本 skill 重在产出**可被 LLM/grep/外部工具按维度定位**的结构，而不是规定一种特定的萃取方法论。

## 顶层范式

```
{目标目录}/
├── raw/                       # 不可变源（拉取/导入/录音/原文/收藏）
│   ├── articles/
│   ├── transcripts/
│   ├── notes/                 # 个人笔记的原始记录
│   └── assets/
├── wiki/                      # LLM 拥有
│   ├── kps/                   # 知识点卡（课程语境专属）
│   ├── cases/                 # 案例
│   ├── models/                # 模型
│   ├── concepts/              # 抽象概念
│   ├── notes/                 # 通用笔记（不属于上述四类的卡片：个人思考/事件记录/问题清单/观察/摘录）
│   ├── materials/             # 可复用素材
│   └── indexes/
│       ├── index.md           # 多维入口（领域/类型/主题/概念/时间/最近活动）
│       ├── log.md             # 时间轴日志
│       └── mapping.json       # raw→wiki 映射（可选）
└── CLAUDE.md                  # 该目录的 schema 与差异规则
```

### 卡片类型总览

| 类型 | 目录 | 何时用 | 关键 frontmatter 字段 |
|:---|:---|:---|:---|
| **kp** | `wiki/kps/` | 课程语境的可讲授知识点 | `kp_name, module, knowledge_domain, knowledge_type, tags, knowledge_date` |
| **case** | `wiki/cases/` | 真实业务场景 / 故事 / 经验 | `case_name, industry, scenario, outcome, source_marking, knowledge_date` |
| **model** | `wiki/models/` | 思维模型 / 决策框架 / 理论结构 | `model_name, knowledge_domain, origin, source_marking, knowledge_date` |
| **concept** | `wiki/concepts/` | 跨卡片共享的抽象概念 | `concept_name, knowledge_domain, knowledge_type, appears_in, source_marking, knowledge_date` |
| **note** | `wiki/notes/` | 不属于上述四类的卡片：个人思考、事件记录、问题清单、观察、摘录、引用 | `note_name, note_type, topic, date, source_marking` |
| **material** | `wiki/materials/{类型}/` | 高复用的素材（金句/数据/工具/话术） | `material_name, material_type, source_kp, reusable_in` |

> `knowledge_date` 是知识发生时间（来源资料的时间），与 `last_compiled`（编辑时间）分工不同；note 卡的时间由 `date` 承担。字段定义与新旧碰撞判定 → `references/knowledge-freshness.md`

> 详细字段定义 → `references/non-course-schemas.md`（kp/case/model/concept）+ `references/note-schemas.md`（note）

## 模式判定（必须先做）

进入工作目录，**先不要产出**，按下表判定模式：

| 模式 | 触发信号 | 起点条件 |
|:---|:---|:---|
| **Build** | "整理文件夹/搭建知识库/给目录建 wiki" / 目录还没有 raw 或 wiki | 目录混乱或空 |
| **Compile** | "编译/蒸馏/萃取/把新资料整理进 wiki/更新知识库" | 已有 raw + wiki 范式，要增量加东西 |
| **Lint** | "体检/扫描/检查/找孤儿/索引对不上" | 已有 wiki，需要健康度检查 |

判定不明确时**问用户**：「你是想从零搭建（Build）/把新资料编译进来（Compile）/检查现有 wiki 健康度（Lint）？」

> 三个模式可能在一次对话里前后衔接：Build 完成首次架构后会衔接 Compile 处理首批资料；Compile 第零步内置一次轻量 Lint。**本 skill 不提供 Query/检索模式**——检索由 LLM 读 `wiki/indexes/index.md` + grep frontmatter 完成，是构建产物的"使用方式"而非本 skill 的"模式"。但检索产生的**综合回答要归档回 wiki**（见下方「查询沉淀」）——回答即资产，不归档就消失在聊天记录里，复利链条就断了。

---

## 主语境判定（四选一）

> **第零步之前先做**：明确这个 wiki 服务于哪种语境。语境决定目录结构、萃取步骤、索引组织方式。

| 主语境 | 典型场景 | 主目录 | 萃取骨架 | 索引侧重 |
|:---|:---|:---|:---|:---|
| **课程** | 培训课件/课程开发/教学材料 | `wiki/kps/` + 模块子目录 | 模块 → 知识点 → 四点三线（可选） | 按模块、按领域、按讲次 |
| **知识库** | 团队 wiki/技术文档/产品手册/方法论库 | `wiki/concepts/` + `wiki/models/` | 主题 → 概念/模型/案例 | 按主题、按领域、按更新时间 |
| **个人笔记** | 个人 PKM/读书笔记/会议记录/日常思考 | `wiki/notes/` + 时间线 | 来源 → 笔记/摘录/思考 | 按时间线、按主题、按项目 |
| **综合** | 混合多语境（如既有课程笔记也有个人观察） | 全部目录并存 | 按当前资料语境分支选择 | 多维索引并存 |

> **默认**：用户没说具体语境时，问"这个 wiki 主要用来做什么？"再判定。**不要默认课程**——课程只是四分之一。

---

## 工作流（Build 模式）

**适用**：目录是空的、只有零散文件、或用户明说"从零搭建"。

### B1. 现状扫描

```bash
ls -la {目标目录}
find {目标目录} -type f \( -name "*.md" -o -name "*.pdf" -o -name "*.txt" \) | head -50
```

判定起点形态：
- **空目录** → "全新初始化"路径
- **只有散落文件**（没有 raw/wiki 子目录）→ "半结构化迁移"路径
- **已有 raw 或 wiki 但不完整** → "补全范式"路径

### B2. 与用户对齐定位

不擅自决定。先问 3-4 个关键问题：

1. **主语境是什么？**——课程 / 知识库 / 个人笔记 / 综合（影响 wiki/ 主目录、萃取骨架、索引侧重）
2. **现有散落文件归到 raw/ 哪个子目录？**——按文件类型：articles/transcripts/notes/assets，或保留原结构
3. **检索侧重哪个维度？**——按领域 / 按主题 / 按时间线 / 按类型 / 按概念（影响 index.md 段顺序）
4. **是否需要立刻编译首批内容？**——是 → Build 完接 Compile；否 → 只搭骨架

### B3. 落骨架（用户确认后执行）

```bash
mkdir -p {目标目录}/raw/{articles,transcripts,notes,assets}
mkdir -p {目标目录}/wiki/{kps,cases,models,concepts,notes,materials,indexes}
```

> **目录可裁剪**：主语境明确时，只建用得到的子目录。例如纯个人笔记主语境下，可以不建 `kps/` `models/`，只留 `notes/` `concepts/` `materials/`，避免空目录噪音。

落空模板：
- `wiki/indexes/log.md` ← 用 `assets/log-template.md`
- `wiki/indexes/index.md` ← 用 `assets/index-template.md`（按主语境裁剪段落）
- `CLAUDE.md` ← 按主语境从 `references/architecture-contract.md` 第 3.3 节抽 schema 草案

迁移已有散落文件到 raw/——**保留原文件名和时间戳**（用 `git mv` 或 `cp -p`）。

> **建议 git 化**：若目标目录还不是 git 仓库，问用户一句是否 `git init`——wiki 就是一堆 markdown 文件，进了 git 白得版本历史、diff 和回滚，编译器批量改动时多一层保险。用户不要就跳过，不阻塞。

### B4. 第一条 log

写第一条 `[YYYY-MM-DD HH:MM] init: {目标目录} context={主语境}`，记录初始化动作 + 主语境 + 已迁移到 raw/ 的文件清单。

### B5. 衔接

询问用户：「骨架已搭好，是否立刻编译 raw/ 里的资料？是 → 进入 Compile 模式；否 → 结束。」

> Build 三种起点的完整决策树 → `references/build-mode.md`

---

## 工作流（Compile 模式）

**适用**：已有 raw + wiki 范式，把新资料增量编译进去。

### 第零步：定位与体检（必跑）

1. 识别目标目录
2. 读结构（`ls`/`tree` 确认 raw/wiki/CLAUDE.md 完整度）
3. 读 `CLAUDE.md`：确认本次主语境 + schema 差异规则
4. 读 `wiki/indexes/log.md` 最近 5–10 条
5. 读 `wiki/indexes/index.md` 的多维索引（领域/类型/主题/时间/最近活动）
6. 判定本次资料的**子语境**（在主语境之内，可能更细：课程下的某讲次/知识库下的某主题/个人笔记下的某项目）
7. **跑一次轻量 Lint**：`python3 scripts/scan_wiki.py {目标目录} --light`，把 finding 加进体检报告

> 体检细则与语境判定 → `references/architecture-contract.md`

### 第零点五步：架构修复（条件触发）

| 缺位 | 处理 |
|:---|:---|
| 没有 `raw/` | 询问资料在哪，建议归档（保留原文件名） |
| 没有 `wiki/` | 切到 Build 模式 B3 落骨架 |
| 没有 `wiki/indexes/log.md` 或 `index.md` | 用模板初始化（无副作用，可直接做） |
| 没有 `CLAUDE.md` | 给草案让用户审阅 |
| `CLAUDE.md` 与本次语境冲突 | 不擅改，列出冲突让用户决定 |

### 第一至十步：内容萃取（按主语境分支）

> **核心原则**：课程语境的"拆模块→拆知识点→四点三线"是**课程专属路径**，不是通用动作。其他语境走对应骨架。**不要默认走课程路径**。

| 步 | 课程语境 | 知识库语境 | 个人笔记语境 | 综合语境 |
|:---|:---|:---|:---|:---|
| 1 | 识别输入类型（课纲/讲次/完整文章） | 识别输入类型（主题/文档/手册/方法论） | 识别输入类型（读书/会议/聊天/收藏/日记） | 逐份判定子语境 |
| 2 | 拆解模块（3-7 个） | 拆解主题（2-5 个一级主题） | 按来源/时间/项目归档 | 按子语境分支 |
| 3 | 拆解知识点（独立可讲授） | 拆解概念/模型/案例 | 拆解笔记/摘录/思考 | 同左 |
| 4 | 萃取四点（焦点→卖点→特点→笑点）**或** 简版要点 | 萃取概念定义 + 适用范围 + 反例 | 萃取关键洞察 + 可行动项 + 待澄清问题 | 按子语境分支 |
| 4.5 | 打标签（domain/type/tags） | 同左 | 打时间/项目/主题标签 | 同左 |
| 5 | 质疑边界（前提/适用/反例） | 质疑边界（同左，更严格） | 标记待跟进 / 待验证 | 按子语境分支 |
| 6 | 标记素材（高复用外提到 materials/） | 同左（更常用，wiki 核心是素材可复用） | 标记高复用素材 / 金句 | 同左 |
| 7 | 模块级三线（可选） | 主题级总览（3 句话） | 时间线 / 项目节点（可选） | 按子语境分支 |
| 8 | 卡片关联（必须双向写回） | 同左 | 同左（关联更松散） | 同左 |
| 9 | 课程级总三线（可选） | 主题索引更新 | 个人索引更新 | 多维索引更新 |
| 10 | 标记来源 [已提取]/[AI补全] | 同左 | 同左 | 同左 |

> 课程语境四点三线方法论 → `references/methodology.md`
> 案例/模型/概念卡片字段 → `references/non-course-schemas.md`
> 通用 note 卡片字段 → `references/note-schemas.md`
> 主语境判定细则 → `references/context-judging.md`

> **深度萃取（可选）**：当用户要求"高质量萃取"/"严格筛选"/"避免水卡"时，按 `references/extraction-quality-gate.md` 启用三重验证 + 原文出处强制 + 边界反场景。不启用时维持上面十步的轻量流程。

### 第十一步：合并模式（增量 ingest）

如果第零步发现 wiki/ 已有同名/同义产物，**不覆盖**：

| 情况 | 处理 |
|:---|:---|
| 同名同义 | 追加新发现，加 `last_compiled`，冲突用 `> ⚠️` 块并存 |
| 同名异义 | 加领域后缀，互相 `跨域类比` |
| 跨语境同义 | 抽到 `wiki/concepts/{概念名}.md`，各卡片改为引用 |
| 跨时间补充 | 个人笔记语境特有：同一主题多次思考 → 追加时间线，不覆盖 |
| source_marking 升级 | 更新标记 + `upgraded_at` |

> **波及面检查**：一份新资料往往不只牵动新卡——既有相关卡片的关联、素材、概念页 `appears_in` 都要回写。只产新卡不回写旧卡的编译是半成品。

> 完整合并规则 → `references/merge-incremental.md`

### 第十一点五步：新旧碰撞判定（知识时效，必做）

新知识 vs 已有同体系知识（**不只是同名**——名字完全不同但语义演进的也要抓），语义判定后四分类：

| 判定 | 处理 |
|:---|:---|
| **互补**（新深化旧，不推翻） | 走合并追加；不标取代 |
| **取代**（新推翻旧的地位） | 旧卡标 `superseded_by: "[[新卡]]"` + 新卡加「演进史」段回链写差异；旧卡保留展示，不改写不删除 |
| **并存**（同主题不同角度/场景） | 不标取代；两卡互写关联 + 边界对比 |
| **拿不准** | 列成候选表**问用户**，本次不标 |

每张新卡落盘时写 `knowledge_date`（推断规则：source_files 文件名日期前缀最早 → raw mtime → 已有时间字段兜底）。

> **铁律：不擅自标 superseded_by**——字面相似 ≠ 知识演进。完整判定流程、检索时效呈现、存量回填 → `references/knowledge-freshness.md`

### 第十二步：写 log + 更新 index（必跑）

1. 追加 `wiki/indexes/log.md`：本次 compile 摘要（格式见 `references/log-spec.md`，统一 `## [时间] 操作: 主体` 前缀，保证 `grep "^## \[" log.md` 可解析）
2. 更新 `wiki/indexes/index.md`：按主语境**增量 patch 对应段**
   - 课程语境 → 课程清单 / 模块索引 / 最近活动
   - 知识库语境 → 主题索引 / 概念索引 / 类型索引 / 按知识时间排序 / 最近活动
   - 个人笔记语境 → 时间线 / 主题分组 / 项目分组 / 最近活动
   - 综合语境 → 按需多维
   - 时间段里的知识卡片带「知识时间」；同体系新旧卡并存时，最新标 ✅、旧版标 ⚠️ 已被 [[X]] 深化（保留展示）
3. 更新 `wiki/indexes/mapping.json`（如目录已有）

> log 字段约定 → `references/log-spec.md`
> index 段落规范与可检索性 → `references/query-entries.md`

---

## 工作流（Lint 模式）

**Lint 只读 wiki/，不动 raw/，默认不写 wiki/，只输出修复清单**。

### L1. 定位与扫描深度

询问扫描深度：
- **轻量**（默认）：8 项结构性检查（含知识时效字段 L17），2-3 分钟
- **深度**：18 项（含新旧体系健康 L18），外加 LLM 语义检查 S1-S5（矛盾/过时结论/概念缺页/数据空洞/下一步提议），5-10 分钟
- **聚焦**：用户指定单项

### L2. 执行扫描

```bash
python3 scripts/scan_wiki.py {目标目录} --light            # 轻量
python3 scripts/scan_wiki.py {目标目录} --deep             # 深度
python3 scripts/scan_wiki.py {目标目录} --check L8         # 聚焦
```

脚本输出 JSON。LLM 读 JSON，把 finding 翻译成自然语言报告。

### L3. 输出修复报告

落盘 `wiki/indexes/lint-{YYYY-MM-DD}.md`，给终端摘要：error / warning / info 数量 + 按类别分组 + 详细报告路径。

### L4. 修复（用户确认后才做）

| 类别 | 修复方式 |
|:---|:---|
| 可自动（index 漂移、frontmatter 补齐、双向关联补全） | 用户一句"全部修"批量执行 |
| 半自动（source_marking 升级、跨语境归并） | 逐条让用户确认 |
| 必须手动（冲突未决、孤儿归属、三线空泛） | 仅给修复指引，不动文件 |

修复完成后，写一条 log，操作标 `lint-fix`。

> 18 项检查定义 + LLM 语义检查 S1-S5 + 报告格式 + 修复模板 → `references/lint-spec.md`
> 时效类检查细则与存量回填 → `references/knowledge-freshness.md`

### 深度 lint 的收尾：下一步提议

深度 lint 结束时，报告末尾给一节「下一步」：值得追问的新问题、值得去找的新资料、值得建页的高频概念。wiki 的健康不只是"没有坏卡"，还包括"知道下一步该长什么"。

---

## 查询沉淀（回答归档，可选但默认提议）

用户在已有 wiki 目录里提问，LLM 检索回答之后：

| 回答形态 | 是否提议归档 |
|:---|:---|
| 单卡转述（"X 是什么"直接读一张卡回答） | 否——卡片已是资产 |
| **跨卡综合 / 对比表 / 新连接 / 分析判断**（"对比 A 和 B""X 领域哪个模型最新"） | **是**——回答完问一句：「要把这个回答沉淀进 wiki 吗？」 |

归档动作（用户同意才做）：

1. 回答落卡：对比/分析 → `wiki/notes/`（note_type: 分析）或升级为 model/concept 卡；临时结论 → note
2. 卡内回链本次引用的所有来源卡片
3. index 对应段 + log 追加一条 `query:` 记录

> **为什么不默认跳过**：人做的一次对比、一个发现的关联，和摄入的资料一样有价值——不归档就消失，归档了就让每次探索都在给 wiki 增厚。时效呈现规则（同体系归组、✅/⚠️ 状态）→ `references/query-entries.md`

### Lint 与 Compile 协同

| 场景 | 动作 |
|:---|:---|
| Compile 第零步轻量 Lint 报 error | 体检报告高亮，问"先修复再编译，还是接受现状继续？" |
| Lint 修复涉及新增/合并卡片 | 切回 Compile 第十一步 |
| 累计 5 次 compile 没跑深度 lint | 编译器主动建议"跑一次深度 lint" |

---

## 输出契约（所有模式必须遵守）

### 文件命名

- 模块文件夹：`{两位序号}-{简称}`，如 `01-选题破题`（课程语境专属）
- 知识点文件：`{知识点名称}.md`（不加序号前缀，跨课程引用稳定）
- 主题文件夹：`{主题名}/`（知识库语境，子目录按需）
- 笔记文件：`{YYYY-MM-DD}-{简称}.md` 或 `{来源}-{简称}.md`（个人笔记语境）
- 模块/主题概要：`_module-summary.md` / `_topic-summary.md`（下划线前缀排首位）
- 概念卡：`wiki/concepts/{概念名}.md`
- 通用笔记：`wiki/notes/{note_type}/{简称}.md`
- 素材卡：`wiki/materials/{类型}/{素材名}.md`

### Frontmatter（按卡片类型选 schema）

| 卡片类型 | 必填字段 | 模板 |
|:---|:---|:---|
| 知识点（kp） | kp_name, module, knowledge_domain, knowledge_type, tags, source_marking, knowledge_date | `assets/kp-template.md` |
| 案例 | case_name, industry, scenario, outcome, source_marking, knowledge_date | `references/non-course-schemas.md` |
| 模型 | model_name, knowledge_domain, origin, source_marking, knowledge_date | 同上 |
| 概念 | concept_name, knowledge_domain, knowledge_type, appears_in, source_marking, knowledge_date | 同上 |
| 通用笔记（note） | note_name, note_type, topic, date, source_marking | `references/note-schemas.md` |
| 素材 | material_name, material_type, source_kp, reusable_in | `references/non-course-schemas.md` |

可选字段（增量编译用）：`source_files`、`last_compiled`、`upgraded_at`；时效用：`knowledge_date_basis`（近似回填标记）、`superseded_by`（被取代时，用户确认后填）

### 渐进式披露 L1/L2/L3

每张卡片：L1 frontmatter（索引用）→ L2 一句话描述 + 概览表（扫读用）→ L3 边界/素材/关联（深读用）

### 多维查询入口（**这是 wiki 的核心使用方式**）

通过 `wiki/indexes/index.md` 的分段实现多维可检索。**LLM 仅靠读 index + grep frontmatter 即可完成查询**——grep 友好是设计目标，不只是 LLM 友好。

按主语境裁剪段：

| 段 | 课程语境 | 知识库语境 | 个人笔记语境 | 综合语境 |
|:---|:---|:---|:---|:---|
| 主题/模块索引 | ✅（模块） | ✅（主题） | ✅（项目/主题） | ✅ |
| 领域索引 | ✅ | ✅ | 可选 | ✅ |
| 类型索引 | ✅ | ✅ | ✅ | ✅ |
| 概念索引 | ✅ | ✅（必填） | ✅ | ✅ |
| 时间线 | 可选 | ✅（按知识时间） | ✅（必填） | ✅ |
| 最近活动 | ✅ | ✅ | ✅ | ✅ |
| 跨语境同义概念 | ✅ | ✅ | 可选 | ✅ |
| 共享素材 | ✅ | ✅（必填） | ✅ | ✅ |

> 详细 → `references/query-entries.md`

---

## 质量自检（输出前必跑）

**架构层**
- [ ] 进入目录后判定了模式（Build/Compile/Lint）？
- [ ] 判定了主语境（课程/知识库/个人笔记/综合）？
- [ ] 第零步：读了结构、CLAUDE.md、log、index？跑了轻量 lint？
- [ ] 架构有缺位时，与用户确认了修复方案再继续？
- [ ] 输出路径在 `wiki/{语境}/` 之下，不是目标目录根？
- [ ] **检索就绪性**：能用 grep / LLM 读 index 在不打开单卡片的前提下定位到目标？

**内容层（编译后）**
- [ ] 每张卡片 frontmatter 完整、字段值合法？
- [ ] 每张知识卡片有 `knowledge_date`（note 卡有 `date`）？
- [ ] 同体系新旧知识做了碰撞判定？取代关系的两侧都写了（旧卡 superseded_by + 新卡演进史回链）？拿不准的是否列成候选问了用户？
- [ ] 每张卡片有 L1+L2+L3 三层？
- [ ] 卡片间关联是否双向？
- [ ] 跨语境同义是否抽到 concepts/？高复用素材是否外提到 materials/？
- [ ] 通用笔记（非四类卡片）是否归到 `wiki/notes/` 而非混入 kps/cases？
- [ ] `[已提取]/[AI补全]` 标注准确？

**收尾层**
- [ ] log.md 已追加（带操作前缀）？index.md 已更新（按主语境对应段增量 patch，不重写）？
- [ ] 本次回答若有跨卡综合/对比，是否提议过归档回 wiki？
- [ ] 不可逆操作（覆盖/重命名/批量归并）已经用户确认？

---

## References / Assets / Scripts 索引

**references/**（按需加载，不要全读）
- `architecture-contract.md` — 体检清单 + 各语境 schema 草案
- `build-mode.md` — Build 模式三种起点（空/散落/半完整）的完整决策树
- `context-judging.md` — 主语境判定细则（课程/知识库/个人笔记/综合的边界与切换）
- `methodology.md` — 课程语境四点三线方法论 + 标签表 + 质疑指南 + 素材外提
- `non-course-schemas.md` — 案例/模型/概念/素材卡片的字段与模板
- `note-schemas.md` — 通用 note 卡片字段与模板（个人思考/事件/问题清单/摘录）
- `knowledge-freshness.md` — **知识时效机制**：knowledge_date/superseded_by 字段、新旧碰撞判定、检索时效呈现、存量回填
- `extraction-quality-gate.md` — **可选深度萃取**：三重验证 + 原文出处 + 边界反场景（用户要求高质量时启用）
- `merge-incremental.md` — 第十一步合并的情况 + 新旧碰撞 + 增量边界
- `lint-spec.md` — 18 项检查定义 + LLM 语义检查 S1-S5 + 三档深度 + 报告格式 + 修复分级
- `log-spec.md` — log.md 格式（统一操作前缀，grep 可解析）+ 各场景写法
- `query-entries.md` — 多维 index 设计 + grep 友好 + 时效呈现 + 回答归档

**assets/**（输出时复制使用）
- `kp-template.md` — 知识点卡模板（课程语境）
- `note-template.md` — 通用笔记卡模板（个人笔记语境）
- `index-template.md` — 多维 index 模板
- `module-summary-template.md` — 模块概要模板
- `log-template.md` — log.md 初始化模板

**scripts/**（直接执行，不读入上下文）
- `scan_wiki.py` — 体检/lint 扫描器（轻量 8 项/深度 18 项，含时效 L17/L18），输出 JSON 给 LLM 翻译为报告
- `backfill_knowledge_date.py` — 存量库批量回填 knowledge_date（先 `--dry-run`，幂等可重跑）
