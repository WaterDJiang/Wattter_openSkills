---
template_name: "GEO 内容生成"
website: "AI search / generative engine content"
description: "基于 GEO Wiki 中文站 104 个页面提炼的生成式引擎优化写作模板。适用于 GEO、AEO、LLMO、AI 搜索、ChatGPT Search、Perplexity、Google AI Overviews、Gemini、AI 引用、品牌提及、llms.txt、AI 爬虫、Schema、可引用性等主题。"
triggers: ["GEO", "生成式引擎优化", "AI 搜索", "AI 引用", "AI Overview", "AI Overviews", "ChatGPT Search", "Perplexity", "Gemini", "AEO", "LLMO", "llms.txt", "AI 爬虫", "Schema", "可引用性", "品牌提及", "零点击"]
sources:
  - "https://geo.wiki/zh"
  - "https://geo.wiki/llms.txt"
  - "https://geo.wiki/llms-full.txt"
  - "https://geo.wiki/sitemap-index.xml"
---

# 内容策略：GEO 内容生成

> 本模板根据 GEO Wiki 中文站全站抓取结果提炼。不要复写原站大段文字；使用其公开概念框架与来源脉络，生成原创、可发布、可被 AI 引用的文章。

## 1. 适用场景

当用户输入包含以下意图时，优先使用本模板：

- 写或改写生成式引擎优化（GEO）、AI 搜索、AI 引用、AI 可见度相关内容。
- 比较 SEO / GEO / AEO / LLMO / AIO。
- 解释 ChatGPT Search、Perplexity、Google AI Overviews、Gemini 等平台差异。
- 生成面向 AI 引用的文章、FAQ、操作手册、审计清单、指标说明。
- 讨论 AI 爬虫、robots.txt、llms.txt、Schema.org、JSON-LD、SSR/CSR、Sitemap、IndexNow。
- 设计 AI 引用追踪、品牌提及追踪、GEO ROI、GEO 指标体系。

## 1.1 深入资料

- 需要更完整的 GEO 方法论、平台、技术、指标与反模式时，读取 `references/geo-core-knowledge.md`。
- 需要设计 GEO 友好网站、知识库、专题页、页面模板或机器可读索引时，读取 `references/geo-web-build-patterns.md`。
- 需要核对来源页和归因边界时，读取 `references/geo-wiki-source-index.md`。

## 2. 核心立场

### 2.1 GEO 的工作定义

GEO 不是“关键词 SEO 改名”。它是在 SEO 地基上叠加一层，让内容在生成式引擎的答案里被检索、采信、引用或提及。

- **SEO 终点**：搜索结果页上的排序链接与点击。
- **GEO 终点**：AI 答案里的引用、提及、链接、来源归属。
- **共同地基**：可抓取、可渲染、结构清晰、真实专业、站外权威。
- **新增差异**：多源合成、零点击、品牌提及与链接分离、段落级可引用性。

写作时不要制造“SEO 已死”的戏剧化结论。正确表达是：GEO 是 SEO 的延伸，不是替代。

### 2.2 Answer Loop 四步

所有 GEO 内容都应围绕生成式引擎的回答循环组织：

1. **查询**：用户真实会怎么问，查询会如何被扩展或扇出。
2. **检索**：引擎能否抓到页面，是否进入候选来源池。
3. **采信**：候选内容是否可信、是否能被整段取用。
4. **生成与署名**：答案是否引用、提及或链接到品牌/页面。

文章里的建议必须能对应到其中一步，否则容易变成空泛“AI 优化”。

## 3. GEO 内容生成结构

本节只定义内容结构。最终 Frontmatter、正文是否包含 H1、批量计划格式、文件命名，必须读取并遵守 `templates/geo-output.md`。GEO 文章不得直接套用 SEO 输出模板或任何 profile 输出习惯；profile 只能补充品牌、语气、关键词和 CTA。

优先使用以下内容结构，除非用户明确要求别的形式：

```markdown
---
title: "[包含 GEO / AI 搜索核心关键词的标题]"
date: YYYY-MM-DD
category:
  - AI 搜索
  - GEO
tag:
  - GEO
  - 生成式引擎优化
  - AI 搜索
  - AI 引用
keywords: [GEO, 生成式引擎优化, AI 搜索, ChatGPT Search, Perplexity]
description: "[80-140 字，直接说明本文回答什么问题，以及读者能得到什么可执行结论]"
---

# [核心问题式 H1]

[第一段直接回答问题。不要铺垫历史，不要先讲“随着 AI 发展”。]

## 速览

- [结论 1：一句话可独立引用]
- [结论 2：一句话可独立引用]
- [结论 3：一句话可独立引用]

## [问题式 H2：用户真实会问的问题]

[第一句给答案，后面解释机制。]

## [操作式 H2：怎么做]

1. [一步一个动作]
2. [一步一个动作]
3. [一步一个动作]

## [对比式 H2：容易混淆的概念]

| 概念 | 解决什么 | 不解决什么 | GEO 意义 |
| --- | --- | --- | --- |

## 常见问题

### [真实问题 1]
[50-120 字直接回答。]

### [真实问题 2]
[50-120 字直接回答。]
```

## 4. 可引用性写作配方

每篇 GEO 文章至少满足第 1、2、7 项；其他项按内容形态选择，不要硬造。

| # | 信号 | 写法 | 避免 |
|---|---|---|---|
| 1 | 自包含内容块 | 每段重新点明主语，代词在段内解决 | “如上所述”“前者”“这种方式”悬空 |
| 2 | 直接答案块 | 每个 H2/H3 的第一句就是结论 | 先铺 2-3 段背景再给答案 |
| 3 | 问答结构 | H2/H3 对齐真实搜索/AI 提问 | 凭空编造 FAQ 或没人会问的标题 |
| 4 | 步骤列表 | 编号、祈使、一动作为一步 | 把流程埋进散文 |
| 5 | 自标注表格 | 表格有标题，表头是完整名词短语，每行能独立读懂 | 离开正文就读不懂的表 |
| 6 | 标题层级 | 一份 H1，H2 -> H3 干净嵌套 | 跳级、重复 H1、装饰性标题 |
| 7 | 可整段引述句 | 每节至少一句独立成立的短断言 | 含糊、多重从句、无法署名的句子 |

## 5. 平台差异速查

| 平台 | 类型 | 关键抓手 | 写作侧重点 |
|---|---|---|---|
| ChatGPT Search | 检索增强对话型，按需联网 | OAI-SearchBot 影响 Search 可见度；GPTBot 主要不是 Search 抓手 | 直接答案、强实体、可被稀疏引用的高密度段落 |
| Perplexity | 原生答案引擎，默认实时检索 | PerplexityBot / Perplexity-User；引用密度高 | 自包含段落、来源清晰、表格/步骤/FAQ 更容易被引用 |
| Google AI Overviews | SERP 内嵌型，基于 Google 搜索索引 | Googlebot 决定资格；Google-Extended 不是 AIO 控制项 | 保持经典 SEO 地基、覆盖子主题、结构化答案 |
| Google Gemini | 检索增强对话型，使用 Google Search grounding | Googlebot 建索引，Google-Extended 对 Gemini/Vertex 的使用控制更关键 | 覆盖查询扇出后的相邻问题，强化实体与来源可信度 |

## 6. 技术与基础设施边界

写到技术 GEO 时，必须保持边界清楚：

- **robots.txt**：是自愿请求，不是访问控制；按训练、检索、用户触发三类爬虫分别决策。
- **llms.txt**：是低成本、向前兼容的精选导览；尚不能承诺主流引擎一定读取，更不能承诺发布后就会被引用。
- **Schema.org / JSON-LD**：用于实体消歧和机器可读，不是直接排名或引用信号；标记必须对应页面可见内容。
- **Sitemap / IndexNow**：主要通过宿主搜索索引间接影响 AI 搜索；不要说它们能直连所有 AI 引擎。
- **SSR / SSG 优先**：主体内容应在 HTML 首屏可读；不要把关键答案只放在客户端渲染之后。
- **多模态内容**：图片、视频、音频仍要配 alt、caption、transcript、表格说明等文本通道。

## 7. 指标与追踪口径

写 GEO 指标时，不要只说“排名”。优先使用以下口径，并在文章里说明定义：

- **Visibility Score / AI 可见度**：品牌或域名在监测回答中出现的整体存在度，各工具口径不同。
- **Citation Rate / 引用率**：监测回答中显式引用目标域名的比例。
- **Citation Share / 引用份额**：同一话题下目标来源在所有被引用来源中的占比。
- **Share of Voice / 声量份额**：目标品牌在竞品集合中的提及或引用占比，需说明是否曝光加权。
- **Mention Frequency / 提及频次**：品牌正文提及次数，需说明句级、整答级或短语级去重。
- **Answer Inclusion Rate / 回答包含率**：答案里是否出现目标品牌/实体的二值比例。
- **Average Position / 平均位置**：需说明按来源列表位置、正文首次出现位置，还是折叠前可见位置。
- **Sentiment / 情感**：正向、负向、中性、对比式提及要分开。
- **Source Diversity / 来源多样性**：多少引擎或查询类型引用了目标来源。

报告任何数字时必须带上：提问集版本、引擎集、时间窗、算引用还是提及、位置定义。

## 8. 反模式

生成 GEO 内容时必须避开：

- 把 GEO 写成“买关键词”“堆 schema”“发 llms.txt 就能被引用”。
- 把 AI 内容识别写成“用了 AI 就降权”；真正风险是低质量、规模化、无来源的内容模式。
- 为了挡训练爬虫，一刀切屏蔽所有 AI 爬虫，导致检索/引用也被挡掉。
- 用大量 FAQ、表格、定义块伪装专业，但没有原创事实、来源、案例或经验。
- 把不同厂商的 Visibility、SOV、Citation Rate 数字直接横向比较。
- 把 Aggarwal et al. 2024 的“最高提升约 40%”写成普遍承诺；它只能作为方向性证据。

## 9. 输出自检

交付前逐项检查：

- [ ] 是否已经读取并应用 `templates/geo-output.md`？
- [ ] 是否明确选择了 `output_mode`？
- [ ] H1 是否是用户会问的核心问题，而不是空泛概念名？
- [ ] 首段是否直接回答问题，并自然包含核心关键词？
- [ ] 每个 H2/H3 第一段是否可独立引用？
- [ ] 是否至少包含一个表格或步骤列表，用于提高机器可读性？
- [ ] 是否区分引用、提及、链接？
- [ ] 是否说明平台差异，而不是笼统写“AI 引擎”？
- [ ] 是否说明技术措施的边界，避免过度承诺？
- [ ] 是否保留真实叙事风格：用具体业务场景解释抽象 GEO 概念？
- [ ] 是否避免加载无关 profile，保持 GEO 框架通用？

## 10. 来源归因

本模板提炼自 GEO Wiki 中文站公开页面。需要在长文底部可选加入：

> 参考：GEO Wiki（https://geo.wiki/zh），CC BY 4.0。

如果文章直接借用了具体术语框架（例如 Answer Loop、七项可引用性信号、六层 GEO 审计阶梯），正文中应以自然语言说明“参考 GEO Wiki 的相关框架”，避免把外部框架伪装成原创。
