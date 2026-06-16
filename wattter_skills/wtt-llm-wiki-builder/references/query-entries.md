# 查询入口设计

本 skill 的产出必须支持**多维查询**。Karpathy LLM Wiki 的 Query 环节在本编译器里通过「目录级 index.md 的多段索引 + frontmatter 字段」来实现——不需要专用查询工具，LLM 读 index 就能定位。

## 两层 index 的职责区分

| 文件 | 范围 | 主用途 |
|:---|:---|:---|
| `wiki/indexes/index.md` | 整个目标目录 | 跨课程/跨语境的总入口；多维索引 |
| `wiki/kps/{课程名}-knowledge-points/index.md` | 单个课程 | 该课程的模块表、三线、跨模块关联 |

每次 compile 后，**两个 index 都要更新**。

## 目录级 index.md 必备段落

```markdown
# {目录名} — 知识库总入口

> 最近编译：{YYYY-MM-DD}　|　课程：N　|　知识点：M　|　案例：K　|　概念：J

---

## 1. 课程清单

| 课程 | 模块数 | 知识点数 | 入口 |
|:---|:---|:---|:---|
| {课程名} | 5 | 32 | [→](./../kps/课程名-knowledge-points/index.md) |

## 2. 领域索引（按 knowledge_domain）

| 领域 | 知识点数 | 知识点列表（链接） |
|:---|:---|:---|
| AI | 12 | [Prompt 工程](...), [RAG](...), ... |
| 营销 | 8 | ... |
| 通用方法论 | 15 | [MECE](...), [金字塔](...), ... |

## 3. 类型索引（按 knowledge_type）

| 类型 | 数量 | 列表 |
|:---|:---|:---|
| 框架 | 9 | ... |
| 模型 | 7 | ... |
| 原则 | 11 | ... |
| 方法 | 14 | ... |
| 流程 | 5 | ... |
| 工具 | 8 | ... |
| 概念 | 6 | ... |

## 4. 跨课程同义概念（concepts/）

| 概念 | 出现于 | 入口 |
|:---|:---|:---|
| MECE 原则 | 选题方法论 / 咨询基础 / 高效汇报 | [→](./../concepts/MECE原则.md) |

## 5. 共享素材（materials/）

| 素材类型 | 数量 | 入口 |
|:---|:---|:---|
| 案例 | 23 | [→](./../materials/cases/) |
| 数据 | 11 | ... |

## 6. 三线总览（跨课程汇总）

> 仅当目录定位为综合知识库时填；纯单课程目录此段省略。

## 7. 最近活动

> 取自 log.md 最近 5 条。

| 日期 | 动作 | 摘要 |
|:---|:---|:---|
```

## 查询场景与对应入口

| 用户问 | LLM 行动 |
|:---|:---|
| "这个目录里关于 AI 的知识点有哪些？" | 读 index.md 第 2 段（领域索引），列出 AI 行 |
| "所有的框架类知识点？" | 读 index.md 第 3 段（类型索引），列出 框架 行 |
| "MECE 原则在哪些课程出现过？" | 读 index.md 第 4 段，或直接读 wiki/concepts/MECE原则.md 的 `appears_in` 字段 |
| "选题方法论这门课的整体结构？" | 读 wiki/kps/选题方法论-knowledge-points/index.md（课程级） |
| "这条原则的原文出处？" | 读对应 kp 文件的 frontmatter `source_files` |
| "上次编译是什么时候、做了什么？" | 读 wiki/indexes/log.md 最近一条 |
| "哪些 raw 文件还没被编译？" | 对比 mapping.json 的 key 与 raw/ 实际文件列表 |
| "AI 领域的框架类知识点有哪些？" | 读 index.md 第 2 段交叉第 3 段；或 grep frontmatter `knowledge_domain: AI` AND `knowledge_type: 框架` |

## 编译时如何更新 index 段落

第十二步执行时，按段落分别 patch：

| 段 | 更新方式 |
|:---|:---|
| 1. 课程清单 | 新课程→新增一行；老课程→更新模块数/知识点数 |
| 2. 领域索引 | 把本次新 kp 按 domain 插入对应行末；新 domain 新增一行 |
| 3. 类型索引 | 同上，按 type |
| 4. 跨课程同义概念 | 仅当本次产生 concepts/ 卡时新增一行 |
| 5. 共享素材 | 仅当 wiki/materials/ 有新增时更新计数 |
| 6. 三线总览 | 综合库才更新；单课程目录跳过 |
| 7. 最近活动 | 把本次 log 条目摘要前置插入，保留前 5 条 |

**原则**：增量 patch，不重写整个 index.md。除非用户显式说"重建 index"。

## 多维查询的 frontmatter 契约

为了让 LLM 仅靠 grep + frontmatter 就能完成大多数查询，所有 kp 文件必须有：

```yaml
kp_name: <唯一>
module: <所属模块>
knowledge_domain: <单选，从领域表取>
knowledge_type: <单选：框架/模型/原则/方法/流程/工具/概念>
tags: [<细粒度，自由>]
source_marking: <已提取/AI补全>
```

可选字段：

```yaml
source_files: [<raw 路径>]      # 来源回溯查询
last_compiled: <YYYY-MM-DD>     # 时间轴查询
upgraded_at: <YYYY-MM-DD>       # 标记升级查询
appears_in: [<kp 路径>]         # 仅 concept 卡片
```

## 反例：不要这样做

- ❌ 把所有查询逻辑塞进 index.md 一段巨表——分段是为了让 LLM 部分加载
- ❌ 用 JSON 当主索引——markdown 表格对 LLM 更友好且能直接渲染
- ❌ 让 frontmatter 字段名因目录而异——跨目录查询会断链
- ❌ 在 kp body 里复述 frontmatter 里的字段——单点真相只放在 frontmatter
