---
template_name: "GEO 文章独立输出模板"
description: "GEO 文章专用最终输出模板。命中 geo-content-generation.md 后必须叠加本模板，不与 SEO 输出模板或任何垂类 profile 共用 Frontmatter、结构和自检。"
triggers: ["geo-output", "GEO 输出", "GEO 文章模板", "AI 搜索文章输出"]
---

# GEO 文章独立输出模板

GEO 文章的最终输出必须使用本模板。`geo-content-generation.md` 负责内容策略，本文件负责交付形态。

## 1. 输出模式选择

根据发布目标选择一种模式：

| 目标 | 模式 | 说明 |
|---|---|---|
| 知乎 / 公众号 / 外部平台 | `platform_article` | Frontmatter 只保留发布器需要的字段，正文不重复 H1，避免标题在平台里出现两次 |
| 站内博客 / Markdown CMS | `site_article` | Frontmatter 保留完整 GEO 元数据，正文可以包含 H1 |
| 批量选题 / 内容计划 | `batch_plan` | 输出多篇文章的标题、意图、目标引擎、结构和文件名，不直接写全文 |
| 审计 / 方法文档 | `playbook` | 输出步骤、表格、检查清单和报告模板 |

## 2. `platform_article`：外部平台文章

用于知乎、公众号等平台发布。标题由 Frontmatter 提供，正文第一行直接进入开头，不要再写 `# 标题`。

```yaml
---
title: "[平台标题，建议 18-36 字]"
date: YYYY-MM-DD
output_mode: platform_article
target_platform: zhihu
geo_topic: "[主题]"
brand_entity: "[品牌或站点，可留空]"
ai_engines:
  - ChatGPT Search
  - Perplexity
  - Google AI Overviews
geo_goal:
  - citation
  - mention
keywords:
  - GEO
  - 生成式引擎优化
  - AI 搜索
  - "[业务关键词]"
summary: "[80-120 字摘要]"
---
```

正文结构：

```markdown
[场景钩子：具体人、具体问题、具体搜索/AI 提问场景。第一段必须直接点出核心判断。]

## 先说结论

- [一句话结论 1]
- [一句话结论 2]
- [一句话结论 3]

## [问题式 H2：用户真实会问的问题]

[第一句直接回答。后面解释。]

## [对比式 H2：容易混淆的概念]

| 概念 | 解决什么 | 不解决什么 | 对这篇文章的意义 |
|---|---|---|---|

## [操作式 H2：怎么做]

1. [一步一个动作]
2. [一步一个动作]
3. [一步一个动作]

## 常见问题

### [真实问题]
[50-120 字直接回答。]

## 最后

[收束到品牌、方法或行动建议。]

[可选来源归因 / 标签]
```

## 3. `site_article`：站内 GEO 文章

用于 9day.tech、品牌博客或 Markdown CMS。保留完整 Frontmatter，正文可以包含 H1。

```yaml
---
title: "[SEO/GEO 标题]"
icon: search
date: YYYY-MM-DD
category:
  - AI 搜索
  - GEO
tag:
  - GEO
  - 生成式引擎优化
  - AI 搜索
  - AI 引用
  - "[品牌标签，可留空]"
keywords:
  - GEO
  - 生成式引擎优化
  - AI 搜索
  - ChatGPT Search
  - Perplexity
description: "[80-140 字摘要]"
canonical: "[站内 URL，可留空]"
geo:
  output_mode: site_article
  target_engines:
    - ChatGPT Search
    - Perplexity
    - Google AI Overviews
  goal:
    - citation
    - mention
  entity:
    name: "[品牌/产品/站点，可留空]"
    type: Organization
  source_attribution:
    - "GEO Wiki"
sticky: false
star: true
---
```

正文结构：

```markdown
# [核心问题式 H1]

[第一段直接回答问题。]

## 速览

| 问题 | 答案 |
|---|---|

## [概念/机制]

## [操作步骤]

## [平台差异]

## [FAQ]

## 参考与延伸
```

## 4. `batch_plan`：批量 GEO 文章输出

当用户要求“一批 GEO 文章”“选题库”“发 10 篇”时，先输出批量计划，不直接一次性写完所有全文，除非用户明确要求。

```yaml
---
title: "[批量计划标题]"
date: YYYY-MM-DD
output_mode: batch_plan
batch_size: N
brand_entity: "[品牌或站点]"
target_platform: "[zhihu/site/wechat]"
---
```

表格字段：

| # | 标题 | 搜索/AI 提问意图 | 目标引擎 | GEO 目标 | 内容结构 | 关键词 | 文件名 |
|---|---|---|---|---|---|---|---|

每个选题都要有：

- 一个用户真实会问的问题。
- 一个目标引擎或泛 AI 搜索场景。
- 一个 GEO 目标：`citation` / `mention` / `entity_recognition` / `technical_readiness` / `measurement`。
- 一个建议输出模式：`platform_article` 或 `site_article`。

## 5. `playbook`：GEO 方法文档

用于审计、流程、清单和内部 SOP。

```yaml
---
title: "[GEO 方法文档标题]"
date: YYYY-MM-DD
output_mode: playbook
geo_task: "[audit / writing / tracking / technical]"
audience:
  - content
  - engineering
  - marketing
---
```

正文必须包含：

- 输入：需要哪些页面、数据、权限或日志。
- 输出：交付什么报告、表格或改写稿。
- 步骤：编号清楚，一步一个动作。
- 判定标准：通过 / 风险 / 失败。
- 修复方向：每个失败项对应一个动作。

## 6. GEO 输出硬规则

无论哪种模式，必须遵守：

- 不使用 `seo-output.md` 的通用 SEO Frontmatter。
- 不加载任何 profile，除非用户明确提到对应品牌、行业或平台。
- 即使加载 profile，也要保留 GEO 的独立输出字段。
- 不使用命理赛道的 M1/M2/M3/M4 标题公式，除非用户明确要求“命理赛道流量放大”。
- 标题必须能表达 AI 搜索 / GEO / 引用 / 提及 / 可引用性 / 平台差异中的一个具体意图。
- 正文必须区分引用、提及、链接。
- 正文必须至少包含一个 GEO 结构组件：速览、对比表、步骤列表、FAQ、指标表。
- 如果发布到知乎，正文不要重复 H1；标题交给 Frontmatter。
- 如果发布到站内 CMS，正文可以包含 H1，但 H1 必须是问题式标题。

## 7. 文件命名

GEO 文件名统一使用：

```text
YYYY-MM-DD-[english-topic]-geo.md
```

示例：

- `2026-07-06-chatgpt-search-perplexity-geo.md`
- `2026-07-06-brand-ai-search-geo.md`
- `2026-07-06-llms-txt-for-geo.md`

批量计划文件名：

```text
YYYY-MM-DD-geo-content-plan.md
```

## 8. 交付前自检

- [ ] 是否选择了明确的 `output_mode`？
- [ ] 是否避免混用通用 SEO / 9day / 命理赛道输出模板？
- [ ] 是否有 GEO 独立字段：`geo_topic`、`geo_goal`、`ai_engines` 或 `geo`？
- [ ] 是否按目标平台处理 H1？
- [ ] 是否包含至少一个表格、步骤列表、FAQ 或速览？
- [ ] 是否明确区分引用、提及、链接？
- [ ] 是否保留来源归因边界？
