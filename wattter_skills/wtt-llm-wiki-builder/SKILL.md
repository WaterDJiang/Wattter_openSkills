---
name: wtt-llm-wiki-builder
description: >-
  在任意文件夹内构建、编译、维护一个 LLM 友好的 wiki 知识库。三个模式：(1) Build——目录什么都没有或只是散落的 markdown，从零搭建 raw/wiki/CLAUDE.md 范式并完成首批编译；(2) Compile——已有 wiki 范式，把新资料增量编译进去（不覆盖、标冲突、跨课程归并）；(3) Lint——扫描已有 wiki 健康度（孤儿卡片/索引漂移/链接失效/frontmatter 缺字段/陈旧标记），输出修复清单。
  课程语境下使用「四点三线」蜂窝矩阵萃取知识点；案例/模型/概念语境切换为对应 schema。所有产物用 frontmatter + index/log/concepts 联动，支持按领域/类型/课程/概念/时间多维查询，支持来源回溯。
  触发场景：(1) 用户说"整理这个文件夹/把这些资料整理成知识库/给这个目录建个 wiki"；(2) 用户说"编译/蒸馏/萃取/把这份整理进 wiki/更新知识库"；(3) 用户说"体检/lint/扫描/检查 wiki 健康度/找孤儿卡片/索引对不上"；(4) 用户提到"四点三线/蜂窝矩阵/知识点/卖点笑点特点焦点"；(5) 用户给出原始资料（课纲、文章、录音稿、案例、笔记）要求结构化沉淀。
---

# LLM Wiki Builder — 任意文件夹的知识库构建/编译/维护

把任意文件夹变成 LLM 友好的 wiki 知识库。raw/ 存不可变源，wiki/ 存 LLM 拥有的卡片，indexes/ 维持入口与日志。所有产物用 frontmatter 索引、index 联动、log 留痕。

## 顶层范式

```
{目标目录}/
├── raw/                       # 不可变源（拉取/导入/录音/原文）
│   ├── articles/
│   ├── transcripts/
│   └── assets/
├── wiki/                      # LLM 拥有
│   ├── kps/                   # 课程语境：知识点卡（四点三线）
│   ├── cases/                 # 案例语境
│   ├── models/                # 模型语境
│   ├── concepts/              # 跨语境共享：抽象概念
│   ├── materials/             # 跨语境共享：可复用素材
│   └── indexes/
│       ├── index.md           # 多维入口
│       ├── log.md             # 时间轴日志
│       └── mapping.json       # raw→wiki 映射（可选）
└── CLAUDE.md                  # 该目录的 schema 与差异规则
```

## 模式判定（必须先做）

进入工作目录，**先不要产出**，按下表判定模式：

| 模式 | 触发信号 | 起点条件 |
|:---|:---|:---|
| **Build** | "整理文件夹/搭建知识库/给目录建 wiki" / 目录还没有 raw 或 wiki | 目录混乱或空 |
| **Compile** | "编译/蒸馏/萃取/把新资料整理进 wiki/更新知识库" | 已有 raw + wiki 范式，要增量加东西 |
| **Lint** | "体检/扫描/检查/找孤儿/索引对不上" | 已有 wiki，需要健康度检查 |

判定不明确时**问用户**：「你是想从零搭建（Build）/把新资料编译进来（Compile）/检查现有 wiki 健康度（Lint）？」

> 三个模式可能在一次对话里前后衔接：Build 完成首次架构后会衔接 Compile 处理首批资料；Compile 第零步内置一次轻量 Lint。

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

不擅自决定。先问 2-3 个关键问题：

1. **主语境是什么？**——课程 / 案例库 / 模型库 / 综合（影响 wiki/ 主目录）
2. **现有散落文件归到 raw/ 哪个子目录？**——articles/transcripts/assets/，或保留原结构
3. **是否需要立刻编译首批内容？**——是 → Build 完接 Compile；否 → 只搭骨架

### B3. 落骨架（用户确认后执行）

```bash
mkdir -p {目标目录}/raw/{articles,transcripts,assets}
mkdir -p {目标目录}/wiki/{kps,cases,models,concepts,materials,indexes}
```

落空模板：
- `wiki/indexes/log.md` ← 用 `assets/log-template.md`
- `wiki/indexes/index.md` ← 用 `assets/index-template.md`
- `CLAUDE.md` ← 按主语境从 `references/architecture-contract.md` 第 3.3 节抽 schema 草案

迁移已有散落文件到 raw/——**保留原文件名和时间戳**（用 `git mv` 或 `cp -p`）。

### B4. 第一条 log

写第一条 `[YYYY-MM-DD HH:MM] init: {目标目录}`，记录初始化动作 + 已迁移到 raw/ 的文件清单。

### B5. 衔接

询问用户：「骨架已搭好，是否立刻编译 raw/ 里的资料？是 → 进入 Compile 模式；否 → 结束。」

> Build 三种起点的完整决策树 → `references/build-mode.md`

---

## 工作流（Compile 模式）

**适用**：已有 raw + wiki 范式，把新资料增量编译进去。

### 第零步：定位与体检（必跑）

1. 识别目标目录
2. 读结构（`ls`/`tree` 确认 raw/wiki/CLAUDE.md 完整度）
3. 读 `CLAUDE.md`：作为本次差异规则
4. 读 `wiki/indexes/log.md` 最近 5–10 条
5. 读 `wiki/indexes/index.md` 的领域/类型索引
6. 判定本次主语境（课程/案例/模型/概念）
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

### 第一至十步：内容萃取（语境特化）

| 步 | 课程语境 | 案例/模型/概念语境 |
|:---|:---|:---|
| 1 | 识别输入类型（主题/自由文本/课纲/完整文章） | 同左 |
| 2 | 拆解模块（3-7 个） | 拆卡片单位（每条独立成卡） |
| 3 | 拆解知识点（独立可讲授） | 不适用 |
| 4 | 萃取四点（焦点→卖点→特点→笑点） | 案例/模型有各自的字段 |
| 4.5 | 打标签（domain/type/tags） | 同左 |
| 5 | 质疑边界（前提/适用/反例） | 同左 |
| 6 | 标记素材（高复用外提到 materials/） | 同左 |
| 7 | 模块级三线 | 不适用 |
| 8 | 卡片关联（必须双向写回） | 同左 |
| 9 | 课程级总三线 | 不适用 |
| 10 | 标记来源 [已提取]/[AI补全] | 同左 |

> 课程语境四点三线方法论 → `references/methodology.md`
> 案例/模型/概念的卡片字段 → `references/non-course-schemas.md`

### 第十一步：合并模式（增量 ingest）

如果第零步发现 wiki/ 已有同名/同义产物，**不覆盖**：

| 情况 | 处理 |
|:---|:---|
| 同名同义 | 追加新发现，加 `last_compiled`，冲突用 `> ⚠️` 块并存 |
| 同名异义 | 加领域后缀，互相 `跨域类比` |
| 跨课程同义 | 抽到 `wiki/concepts/{概念名}.md`，各 kp 改为引用 |
| source_marking 升级 | 更新标记 + `upgraded_at` |

> 完整合并规则 → `references/merge-incremental.md`

### 第十二步：写 log + 更新 index（必跑）

1. 追加 `wiki/indexes/log.md`：本次 compile 摘要
2. 更新 `wiki/indexes/index.md`：增量 patch 课程清单/领域索引/类型索引/最近活动段
3. 更新 `wiki/indexes/mapping.json`（如目录已有）

> log 字段约定 → `references/log-spec.md`
> index 段落规范 → `references/query-entries.md`

---

## 工作流（Lint 模式）

**Lint 只读 wiki/，不动 raw/，默认不写 wiki/，只输出修复清单**。

### L1. 定位与扫描深度

询问扫描深度：
- **轻量**（默认）：7 项结构性检查，2-3 分钟
- **深度**：16 项含语义类，5-10 分钟
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
| 半自动（source_marking 升级、跨课程归并） | 逐条让用户确认 |
| 必须手动（冲突未决、孤儿归属、三线空泛） | 仅给修复指引，不动文件 |

修复完成后，写一条 log，语境标 `lint-fix`。

> 16 项检查定义 + 报告格式 + 修复模板 → `references/lint-spec.md`

### Lint 与 Compile 协同

| 场景 | 动作 |
|:---|:---|
| Compile 第零步轻量 Lint 报 error | 体检报告高亮，问"先修复再编译，还是接受现状继续？" |
| Lint 修复涉及新增/合并卡片 | 切回 Compile 第十一步 |
| 累计 5 次 compile 没跑深度 lint | 编译器主动建议"跑一次深度 lint" |

---

## 输出契约（所有模式必须遵守）

### 文件命名

- 模块文件夹：`{两位序号}-{简称}`，如 `01-选题破题`
- 知识点文件：`{知识点名称}.md`（不加序号前缀，跨课程引用稳定）
- 模块概要：`_module-summary.md`（下划线前缀排首位）
- 概念卡：`wiki/concepts/{概念名}.md`
- 素材卡：`wiki/materials/{类型}/{素材名}.md`

### Frontmatter（按卡片类型选 schema）

| 卡片类型 | 必填字段 | 模板 |
|:---|:---|:---|
| 知识点（kp） | kp_name, module, knowledge_domain, knowledge_type, tags, source_marking | `assets/kp-template.md` |
| 案例 | case_name, industry, scenario, outcome, source_marking | `references/non-course-schemas.md` |
| 模型 | model_name, knowledge_domain, origin, source_marking | 同上 |
| 概念 | concept_name, knowledge_domain, knowledge_type, appears_in, source_marking | 同上 |

可选字段（增量编译用）：`source_files`、`last_compiled`、`upgraded_at`

### 渐进式披露 L1/L2/L3

每张卡片：L1 frontmatter（索引用）→ L2 一句话描述 + 概览表（扫读用）→ L3 边界/素材/关联（深读用）

### 多维查询入口

通过 `wiki/indexes/index.md` 的分段实现：课程清单 / 领域索引 / 类型索引 / 跨课程同义概念 / 共享素材 / 最近活动。LLM 仅靠读 index + grep frontmatter 即可完成查询。

> 详细 → `references/query-entries.md`

---

## 质量自检（输出前必跑）

**架构层**
- [ ] 进入目录后判定了模式（Build/Compile/Lint）？
- [ ] 第零步：读了结构、CLAUDE.md、log、index？跑了轻量 lint？
- [ ] 架构有缺位时，与用户确认了修复方案再继续？
- [ ] 输出路径在 `wiki/{语境}/` 之下，不是目标目录根？

**内容层（编译后）**
- [ ] 每张卡片 frontmatter 完整、字段值合法？
- [ ] 每张卡片有 L1+L2+L3 三层？
- [ ] 卡片间关联是否双向？
- [ ] 跨语境同义是否抽到 concepts/？高复用素材是否外提到 materials/？
- [ ] `[已提取]/[AI补全]` 标注准确？

**收尾层**
- [ ] log.md 已追加？index.md 已更新（按段增量 patch，不重写）？
- [ ] 不可逆操作（覆盖/重命名/批量归并）已经用户确认？

---

## References / Assets / Scripts 索引

**references/**（按需加载，不要全读）
- `architecture-contract.md` — 体检清单 + 各语境 schema 草案
- `build-mode.md` — Build 模式三种起点（空/散落/半完整）的完整决策树
- `methodology.md` — 课程语境四点三线方法论 + 标签表 + 质疑指南 + 素材外提
- `non-course-schemas.md` — 案例/模型/概念卡片的字段与模板
- `merge-incremental.md` — 第十一步合并的四种情况 + 增量边界
- `lint-spec.md` — 16 项检查定义 + 三档深度 + 报告格式 + 修复分级
- `log-spec.md` — log.md 字段约定 + 各场景写法
- `query-entries.md` — 两层 index 区分 + frontmatter 查询契约

**assets/**（输出时复制使用）
- `kp-template.md` — 知识点卡模板
- `index-template.md` — 课程级 index 模板
- `module-summary-template.md` — 模块概要模板
- `log-template.md` — log.md 初始化模板

**scripts/**（直接执行，不读入上下文）
- `scan_wiki.py` — 体检/lint 扫描器，输出 JSON 给 LLM 翻译为报告
