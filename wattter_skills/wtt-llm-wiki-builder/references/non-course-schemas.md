# 非课程语境的卡片 schema

课程语境用 `assets/kp-template.md`（四点三线）。本文档定义其他三种语境的卡片格式。

## 1. 案例卡（wiki/cases/）

适用：单一商业案例、用户故事、复盘、事件。

### 必填 frontmatter

```yaml
---
case_name: "{案例名}"
industry: "{行业，如 SaaS/电商/教育/制造}"
scenario: "{场景一句话，如 '冷启动 0-1 用户'}"
outcome: "{结果一句话，如 '6 个月 MAU 10w'}"
knowledge_domain: "{所属领域}"
tags: [{补充标签}]
source_marking: "{已提取/AI补全}"
# 可选
source_files: []
last_compiled: ""
feishu_id: ""              # 飞书来源时填
reviewer: ""               # 审稿人
---
```

### Body 结构（L2/L3 渐进式披露）

```markdown
# {案例名}

> {一句话核心}

## 概览
| 维度 | 内容 |
|:---|:---|
| **场景** | {上下文/起点} |
| **动作** | {关键决策与执行} |
| **结果** | {可量化产出} |
| **教训** | {可迁移的 1-2 条原则} |

## 时间线
{按时间排列的关键事件，可选}

## 数据
{用到的具体数字/指标，可选}

## 边界追问
| 前提假设 | 适用边界 | 反例/盲区 |
|:---|:---|:---|

## 关联
| 关系 | 关联 |
|:---|:---|
| **类似案例** | [...](...) |
| **相关概念** | [...](../concepts/...) |
| **相关模型** | [...](../models/...) |
```

---

## 2. 模型卡（wiki/models/）

适用：理论模型、方法论框架、心智模型、行业框架。

### 必填 frontmatter

```yaml
---
model_name: "{模型名}"
knowledge_domain: "{领域}"
knowledge_type: "框架/模型/原则"
origin: "{出处，如 '麦肯锡《金字塔原理》'}"
tags: [{补充标签}]
source_marking: "{已提取/AI补全}"
# 可选
source_files: []
last_compiled: ""
---
```

### Body 结构

```markdown
# {模型名}

> {一句话定义}

## 概览
| 维度 | 内容 |
|:---|:---|
| **核心结构** | {2-5 句话讲明白这个模型的组成} |
| **解决什么问题** | {适用场景} |
| **关键洞察** | {为什么 work} |

## 步骤/组成
{如果是流程类模型用编号；如果是结构类模型用表} 

## 适用边界
| 前提假设 | 适用场景 | 不适用场景 | 反例 |
|:---|:---|:---|:---|

## 实例
{1-3 个具体应用，链接到 wiki/cases/}

## 关联
| 关系 | 关联 |
|:---|:---|
| **同类竞品** | [...](...) （不同模型解决类似问题） |
| **底层概念** | [...](../concepts/...) |
| **常用素材** | [...](../materials/...) |
```

---

## 3. 概念卡（wiki/concepts/）

适用：跨课程/跨案例/跨模型出现的抽象概念，做单点真相。

### 必填 frontmatter

```yaml
---
concept_name: "{概念名}"
knowledge_domain: "{领域}"
knowledge_type: "概念/原则"
appears_in:                # 关键字段：跨课程引用回溯
  - "wiki/kps/课程A-knowledge-points/01-xx/某kp.md"
  - "wiki/kps/课程B-knowledge-points/02-yy/某kp.md"
source_marking: "{已提取/AI补全}"
---
```

### Body 结构

```markdown
# {概念名}

> {通用定义，与具体课程脱钩}

## 不同视角下的侧重

| 出现于 | 视角侧重 | 链回 |
|:---|:---|:---|
| 课程 A | {该课程怎么用这个概念} | [→](../kps/课程A-.../...md) |
| 课程 B | {该课程怎么用这个概念} | [→](../kps/课程B-.../...md) |

## 核心要点
{3-5 个 bullet，提炼跨视角的共同点}

## 边界
{这个概念什么时候不成立 / 容易误用}

## 关联
{相关概念、底层概念、对立概念}
```

### 概念卡产生时机

只在第十一步「合并模式」中产生——同一概念在 ≥ 2 个课程独立出现且语义一致时抽出。**不要预先创建概念卡**——通用定义没有具体应用支撑时容易写空。

---

## 4. 素材卡（wiki/materials/）

适用：跨知识点复用的案例片段、数据、练习题、话术、工具。

### 路径约定

```
wiki/materials/
├── cases/         # 微案例（比 wiki/cases/ 颗粒度更小）
├── data/          # 关键数据点
├── exercises/     # 练习题
├── scripts/       # 话术
└── tools/         # 工具/链接
```

### 必填 frontmatter

```yaml
---
material_name: "{素材名}"
material_type: "案例/数据/练习/话术/工具"
used_by:                    # 哪些 kp/case/model 引用了此素材
  - "wiki/kps/.../某kp.md"
source_marking: "{已提取/AI补全}"
tags: [...]
---
```

### Body 极简

```markdown
# {素材名}

{素材本体——可以是一段案例、一组数据、一道题、一段话术}

## 适用场景
- {场景 1}
- {场景 2}
```

素材卡的 body 应当**短、独立、可直接嵌入其他卡片**。

### 素材外提的判定

知识点中的素材，**满足以下任一条件**就外提：

- 同一素材在 ≥ 2 个 kp 中重复出现
- 素材本身有独立价值（如一组重要数据），未来可能被新 kp 引用
- 素材篇幅大（> 200 字），内嵌会让 kp 冗长

不满足时直接内嵌在 kp 的「可用素材」段。

---

## 跨语境一致性

不论哪种卡片类型，**这些字段名是稳定的**（保证跨语境查询）：

- `knowledge_domain`
- `knowledge_type`
- `tags`
- `source_marking`
- `source_files`（可选）
- `last_compiled`（可选）

**这些字段是语境特化的**：

- 课程语境：`kp_name`, `module`
- 案例语境：`case_name`, `industry`, `scenario`, `outcome`
- 模型语境：`model_name`, `origin`
- 概念语境：`concept_name`, `appears_in`
- 素材语境：`material_name`, `material_type`, `used_by`

LLM 查询时通过 `*_name` 模式匹配卡片标识，通过 `knowledge_domain` 等通用字段做交叉查询。
