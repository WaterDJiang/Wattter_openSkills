---
template_name: "SEO 文章输出模板"
description: "SEO 文章专用最终输出模板。负责 Frontmatter、正文结构、批量计划和文件命名。"
triggers: ["seo-output", "SEO 输出", "SEO 文章模板", "搜索优化文章输出"]
---

# SEO 文章输出模板

## 1. 输出模式

| 目标 | 模式 | 说明 |
|---|---|---|
| 站内博客 / Markdown CMS | `site_article` | 保留完整 Frontmatter，正文包含 H1 |
| 知乎 / 公众号 / 外部平台 | `platform_article` | 标题由 Frontmatter 提供，正文不重复 H1 |
| 批量选题 / 内容计划 | `batch_plan` | 先输出文章计划，不直接写全文 |
| 内容简报 | `brief` | 输出标题、关键词、结构和写作要求 |

## 2. `site_article`

```yaml
---
title: "[SEO 标题]"
date: YYYY-MM-DD
output_mode: site_article
search_intent: informational
primary_keyword: "[主关键词]"
secondary_keywords:
  - "[次级关键词 1]"
  - "[次级关键词 2]"
category:
  - "[主分类]"
tag:
  - "[标签 1]"
  - "[标签 2]"
keywords:
  - "[主关键词]"
  - "[次级关键词 1]"
description: "[80-140 字摘要]"
canonical: ""
---
```

正文包含一个 H1，H1 必须与搜索意图一致。

## 3. `platform_article`

```yaml
---
title: "[平台标题，建议 18-36 字]"
date: YYYY-MM-DD
output_mode: platform_article
target_platform: zhihu
search_intent: informational
primary_keyword: "[主关键词]"
secondary_keywords:
  - "[次级关键词 1]"
  - "[次级关键词 2]"
summary: "[80-120 字摘要]"
---
```

正文第一行直接进入开头，不重复 `# 标题`。

## 4. `batch_plan`

```yaml
---
title: "[SEO 批量选题计划]"
date: YYYY-MM-DD
output_mode: batch_plan
batch_size: N
target_platform: "[site/zhihu/wechat]"
---
```

表格字段：

| # | 标题 | 搜索意图 | 主关键词 | 次级关键词 | 推荐结构 | 输出模式 | 文件名 |
|---|---|---|---|---|---|---|---|

## 5. 文件命名

SEO 文件名统一使用：

```text
YYYY-MM-DD-[english-topic]-seo.md
```

批量计划文件名：

```text
YYYY-MM-DD-seo-content-plan.md
```

## 6. 输出硬规则

- 不使用 GEO 输出字段，除非走 GEO 路径。
- 不叠加任何 profile，除非用户明确提到对应品牌、行业或平台。
- `title` 用双引号包裹。
- `category`、`tag`、`keywords` 使用 YAML 数组。
- 外部平台正文不重复 H1；站内文章正文保留 H1。
