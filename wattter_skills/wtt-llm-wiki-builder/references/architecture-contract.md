# 架构契约：目录体检与修复

本文件是第零步「定位与体检」和第零点五步「架构修复」的细则。skill 进入任何「目标目录」时，按此清单逐项核查，再决定是直接编译还是先帮用户修架构。

## 1. 体检清单（第零步）

按顺序执行，每一项的结果写进本次会话的临时记录，最后给用户一份"目录体检报告"。

### 1.1 列结构

```bash
ls -la {目标目录}
# 关注：raw/、wiki/、CLAUDE.md、README.md
```

判定：

| 现象 | 判定 |
|:---|:---|
| 同时有 `raw/` 和 `wiki/` 和 `CLAUDE.md` | ✅ 完整范式，进入语境判定 |
| 有 `wiki/` 没 `raw/` | ⚠️ 半完整：之前编译过但没归档源；建议补 `raw/` |
| 有 `raw/` 没 `wiki/` | ⚠️ 首次编译；本次跑会建立 `wiki/` |
| 都没有，只有散落 markdown | ❌ 未范式化；进入第零点五步全套修复 |

### 1.2 读 schema（CLAUDE.md）

若存在，**完整读取**，重点抽取：

- 该目录定位（案例库 / 模型库 / 课程编译 / 综合）
- 输出形态约定（kp / case / model / concept 哪个是主产）
- frontmatter 字段约定（是否有该目录额外要求的字段，如 `feishu_id`、`reviewer`）
- 命名规范（文件名、子目录名）
- 合并策略（覆盖 / 追加 / 拒绝）
- 与本 skill 默认范式冲突的部分（必须遵循目录 schema，不擅改）

### 1.3 读 log（wiki/indexes/log.md）

若存在，读最近 5–10 条，记录：

- 上次编译日期
- 已编译的源文件（避免重复 ingest）
- 已知冲突 / 未完成项（本次可顺手处理）
- 最近一次的产出规模（用于本次的"是否合理"参照）

### 1.4 读 index（wiki/indexes/index.md）

若存在，读以下段落：

- **领域索引**（已覆盖的 knowledge_domain）
- **类型索引**（已覆盖的 knowledge_type）
- **模块表 / 卡片清单**（用于第十一步去重）

不必通读全文，只取索引段。

### 1.5 输出体检报告

体检完后，给用户一份简短报告（不超过 15 行）：

```
📋 目录体检：{目标目录}
- 范式完整度：✅ / ⚠️ / ❌
- 主语境：课程 / 案例 / 模型 / 综合
- 现有产物：N 个 kp，M 个 case，K 个 concept
- 上次编译：YYYY-MM-DD（{摘要}）
- 本次输入：{资料来源}
- 预计产出：{规模}
- 发现的问题：{列表，可能为空}
- 建议动作：直接编译 / 先修复架构再编译
```

---

## 2. 语境判定规则

按优先级判定本次 compile 的主产物类型。

| 优先级 | 信号 | 判定 |
|:---|:---|:---|
| 1 | CLAUDE.md 明确写了主语境 | 按 CLAUDE.md |
| 2 | 用户在调用时说了关键词（"案例/模型/概念/课程"） | 按用户用词 |
| 3 | 目录名（`01_Cases/` `03_Knowledge/` `02_课程/`） | 按目录名 |
| 4 | 输入资料形态（成体系课纲 → 课程；零散案例 → 案例；理论模型 → 模型） | 按资料形态 |
| 5 | 都不明确 | 询问用户，不擅自决定 |

**默认假设**：当 skill 被显式触发（用户说"四点三线/蜂窝矩阵/知识蒸馏"），主语境是**课程**，主产物是 `wiki/kps/`。

---

## 3. 架构修复建议（第零点五步）

### 3.1 全新目录（什么都没有）

给用户的建议草案：

```
建议目录结构：
{目标目录}/
├── raw/
│   ├── articles/        # 文章/文字稿
│   ├── transcripts/     # 录音转写
│   └── assets/          # 图片/音频/原始附件
├── wiki/
│   ├── {主语境}/        # kps / cases / models 选一
│   ├── concepts/        # 跨语境共享
│   ├── materials/       # 可复用素材
│   └── indexes/
│       ├── index.md
│       ├── log.md
│       └── mapping.json
└── CLAUDE.md            # 该目录的差异 schema
```

**操作**：列出来，问"是否按此初始化？"——用户确认后再 mkdir + 落空模板。

### 3.2 半完整目录（有 wiki/ 没 raw/，或反之）

不要擅自补全。给用户两个选项：

- **选项 A**：把当前输入资料归档到 `raw/{articles|transcripts|assets}/`，建立完整范式
- **选项 B**：本次保持简化，只产 `wiki/`，但记 log 时标注 `raw_missing: true`，后续补归档

让用户选。

### 3.3 缺 CLAUDE.md

按本次语境给一份 schema 草案。下面是各语境的草案模板，根据目录情况二选一或拼接。

#### 3.3.1 课程语境 CLAUDE.md 草案

```markdown
# {目录名} — 课程知识库

## 定位
课程编译输出库。raw/ 存放课纲、录音稿、参考文章；wiki/kps/ 存放按蜂窝矩阵蒸馏的知识点卡片。

## 输出形态
- 主产：`wiki/kps/{课程名}-knowledge-points/`
- 共享：`wiki/concepts/`、`wiki/materials/`
- 索引：`wiki/indexes/{index,log}.md`

## frontmatter 必需字段
kp_name / module / knowledge_domain / knowledge_type / tags / source_marking
可选：source_files / last_compiled / upgraded_at

## 命名
- 模块：`{两位序号}-{模块简称}`
- 知识点：`{知识点名称}.md`
- 概念：`wiki/concepts/{概念名}.md`

## 合并策略
- 同名同义 → 追加；冲突部分用 `> ⚠️` 块标出
- 同名异义 → 加领域后缀
- 跨课程同义 → 抽到 wiki/concepts/

## 编译器
本目录使用 wtt-course-knowledge-distillation 编译。
```

#### 3.3.2 案例库语境 CLAUDE.md 草案

```markdown
# {目录名} — 案例库

## 定位
案例编译输出库。raw/ 存原始案例素材；wiki/cases/ 存结构化案例卡。

## 输出形态
- 主产：`wiki/cases/{案例名}.md`
- 共享：`wiki/concepts/`、`wiki/materials/`

## frontmatter 必需字段
case_name / industry / scenario / outcome / source_marking
可选：feishu_id / reviewer / source_files

## 编译器
本目录使用 wtt-course-knowledge-distillation 编译（案例语境）。
```

#### 3.3.3 模型库语境 CLAUDE.md 草案

```markdown
# {目录名} — 知识模型库

## 定位
理论/模型/框架编译输出库。

## 输出形态
- 主产：`wiki/models/{模型名}.md`
- 共享：`wiki/concepts/`、`wiki/materials/`

## frontmatter 必需字段
model_name / knowledge_domain / origin / source_marking

## 编译器
本目录使用 wtt-course-knowledge-distillation 编译（模型语境）。
```

### 3.4 CLAUDE.md 与本次语境冲突

例：目录 CLAUDE.md 说"只产 cases/"，但用户给的是课程录音稿。

**不擅自改**。把冲突抛给用户：

```
⚠️ 架构冲突：
- 本目录 CLAUDE.md 定位为「案例库」，主产 wiki/cases/
- 但本次输入是课程录音稿，预期主产 wiki/kps/
- 选项：
  A. 在本目录扩展 schema，新增 wiki/kps/ 子目录
  B. 把课程编译到隔壁课程目录（请指定路径）
  C. 把这份录音稿先转化成案例集，按 cases 编译
```

### 3.5 缺 log.md / index.md

**不询问，直接初始化**——这两个文件是无副作用的脚手架，不需要用户决策。用 `assets/log-template.md` 和 `assets/index-template.md` 落盘空模板，第十二步会写入第一条记录。

---

## 4. 何时停下问，何时直接做

| 类型 | 决策 |
|:---|:---|
| 决定主语境（课程/案例/模型） | 不明确时**问** |
| 决定输出路径 | 不明确时**问** |
| 决定合并策略（覆盖/追加） | 必须**问**——一旦覆盖就不可逆 |
| 初始化空 log.md / index.md | 直接做 |
| 创建 raw/ wiki/ 子目录 | 给方案，**问**确认后做 |
| 新增 frontmatter 字段 | **问**——影响下游查询 |
| 调整文件命名 | **问**——影响跨课程引用稳定性 |

**铁律**：不可逆操作（覆盖、删除、重命名）必须问；可逆操作（新建空文件、追加日志）可直接做。
