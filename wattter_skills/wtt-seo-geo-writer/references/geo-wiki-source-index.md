# GEO Wiki 来源索引

本文件记录本次升级 `wtt-seo-content-writer` 时抓取与提炼的 GEO Wiki 来源。抓取时间：2026-07-07。用途：帮助后续 agent 回溯 GEO 模板的知识来源，而不是把原站全文作为 skill 上下文加载。

核心知识已落到：

- `references/geo-core-knowledge.md`：GEO 定义、内容方法、技术边界、平台差异、指标、审计和追踪。
- `references/geo-web-build-patterns.md`：GEO 友好网站的信息架构、页面结构、机器可读索引、前端渲染和网页构建思路。

## 抓取范围

- 入口页：`https://geo.wiki/zh?ref=aihottoday`
- Sitemap：`https://geo.wiki/sitemap-index.xml` -> `https://geo.wiki/sitemap-0.xml`
- LLM 索引：`https://geo.wiki/llms.txt`、`https://geo.wiki/llms-full.txt`
- 中文 `/zh...` URL：104 个
- 抽取正文总量：约 385,660 字符
- 许可页声明：GEO Wiki 编辑内容采用 CC BY 4.0。使用时保留来源归因。

## 核心来源

### 基础概念

- [生成式引擎优化（GEO）](https://geo.wiki/zh/generative-engine-optimization) — GEO 是让内容在 ChatGPT、Perplexity、Google AI Overviews、Gemini 的答案里被引用或提及；它是 SEO 之上叠加的一层，而非替代。
- [生成式引擎](https://geo.wiki/zh/generative-engine) — 生成式引擎接收查询、检索来源，再由 LLM 合成答案；与搜索引擎的差异是输出单位从文档变成答案。
- [答案循环](https://geo.wiki/zh/answer-loop) — 生成式引擎回答每个查询都运行“查询 -> 检索 -> 采信 -> 生成”的循环，GEO 的动作应落在这四步。
- [SEO vs GEO](https://geo.wiki/zh/seo-vs-geo) — SEO 与 GEO 地基相同，终点不同：SEO 要点击排序，GEO 要答案中的引用或提及。
- [AEO vs GEO](https://geo.wiki/zh/aeo-vs-geo) — AEO 和 GEO 在实操上高度重叠，AEO 来自抽取式答案时代，GEO 更贴近生成式合成。
- [LLMO vs GEO](https://geo.wiki/zh/llmo-vs-geo) — LLMO 与 GEO 多数场景目标相同，区别更多是观察角度；训练语料优化不是 GEO 的核心边界。
- [零点击搜索](https://geo.wiki/zh/zero-click-search) — 用户在结果页或 AI 答案里直接获得答案，价值从点击转向引用与提及。
- [引用 vs 提及 vs 链接](https://geo.wiki/zh/citation-vs-mention) — AI 答案对品牌/来源的归功形态不同，不能把引用、提及、链接混为一个指标。

### 内容与可信度

- [可引用性](https://geo.wiki/zh/citability) — 可引用性是内容被检索后能否被原样取用、进入 AI 答案的结构属性，和来源可信度正交。
- [E-E-A-T](https://geo.wiki/zh/e-e-a-t) — E-E-A-T 是可信度框架，在 GEO 中判断来源是否值得支撑答案，不是算法分数。
- [AI 内容识别](https://geo.wiki/zh/ai-content-detection) — AI 引擎惩罚的是低质量、规模化、无实质的内容模式，不是“用了 AI”本身。
- [品牌提及](https://geo.wiki/zh/brand-mentions) — 无链接品牌提及是 GEO 信号，能强化实体先验并影响后续答案。
- [实体识别](https://geo.wiki/zh/entity-recognition) — 实体识别决定一次提及、引用或 schema 断言是否归到正确实体节点。
- [知识图谱存在度](https://geo.wiki/zh/knowledge-graph-presence) — Wikipedia、Wikidata、Google Knowledge Graph 等站外权威节点是实体解析的放大器，不可靠自我声明生成。
- [多语言 GEO](https://geo.wiki/zh/multilingual-geo) — GEO 跨语言时来源池、实体绑定、内容块形状、信任池都会变化。
- [多模态信号](https://geo.wiki/zh/multimodal-signals) — 2026 年 Web 检索场景仍以文本通道为主，图片/视频/音频应提供 alt、caption、transcript、schema。

### 技术 GEO

- [AI 爬虫](https://geo.wiki/zh/ai-crawlers) — AI 爬虫按用途分训练、检索、用户触发，访问决策应按类别做，避免为挡训练牺牲引用。
- [robots.txt](https://geo.wiki/zh/robots-txt) — robots.txt 是自愿请求，不是访问控制；具名 bot 分组和通配规则容易写错。
- [llms.txt](https://geo.wiki/zh/llms-txt) — llms.txt 是低成本、向前兼容的 Markdown 导览约定，引擎端是否读取尚未被主流厂商确认。
- [面向 AI 的 Schema.org](https://geo.wiki/zh/schema-org-for-ai) — Schema.org 用于实体消歧和机器可读，不是排名或引用信号。
- [JSON-LD](https://geo.wiki/zh/json-ld) — JSON-LD 是 Schema.org 的常见序列化；索引型 AI 可能作为结构化数据处理，实时抓取型聊天机器人可能只当纯文本读。
- [Sitemap 与 IndexNow](https://geo.wiki/zh/sitemap-and-indexnow) — sitemap 和 IndexNow 对 AI 搜索的作用通常经宿主搜索索引中转，不是所有 AI 引擎的直接入口。
- [Core Web Vitals](https://geo.wiki/zh/core-web-vitals) — Core Web Vitals 是 Google 排名信号，对 AI Overviews 更直接，对其他 AI 引擎影响有限。

### 平台

- [ChatGPT Search](https://geo.wiki/zh/platforms/chatgpt-search) — 检索增强对话型引擎，按需联网，引用更稀疏；OAI-SearchBot 影响 Search 可见度，GPTBot 不是主要抓手。
- [Perplexity AI](https://geo.wiki/zh/platforms/perplexity-ai) — 原生答案引擎，默认实时检索并带编号引用，是引用密度高、可测量性强的 GEO 基线。
- [Google AI Overviews](https://geo.wiki/zh/platforms/google-ai-overviews) — SERP 内嵌型引擎，基于 Google 搜索索引；Googlebot 决定资格，Google-Extended 不是 AIO 控制项。
- [Google Gemini](https://geo.wiki/zh/platforms/google-gemini) — Google 技术栈上的检索增强对话型引擎；Google-Extended 在 Gemini/Vertex 的使用控制上更关键。

### 操作手册

- [GEO 审计](https://geo.wiki/zh/playbooks/geo-audit) — 六层依赖阶梯：访问、渲染、结构、内容、站外权威、结果；必须自下而上审。
- [可引用性审计](https://geo.wiki/zh/playbooks/citability) — 逐段做内容块抽取测试，判断段落能否被 AI 答案整段取用。
- [面向 AI 引用的写作](https://geo.wiki/zh/playbooks/writing-for-ai-citation) — 七项改写配方：自包含内容块、倒金字塔、问答标题、步骤列表、自标注表格、标题层级、可整段引述句。
- [AI 引用追踪](https://geo.wiki/zh/playbooks/ai-citation-tracking) — 固定 prompt 集、手工基准、自动化采样、核验 URL、归一指标。
- [品牌提及追踪](https://geo.wiki/zh/playbooks/brand-mention-tracking) — 别名、消歧、去重单位、情感标签、SOV 口径都要版本化。

### 指标与研究

- [GEO 指标](https://geo.wiki/zh/geo-metrics) — 10 项 KPI 及厂商口径差异，包括 Visibility Score、Citation Rate、SOV、Mention Frequency、Answer Inclusion Rate 等。
- [GEO ROI 模型](https://geo.wiki/zh/geo-roi) — 在点击和价值脱钩后，用引用、替代流量、品牌权威三类价值建模。
- [Aggarwal et al. 2024](https://geo.wiki/zh/papers/aggarwal-geo-benchmark-2024) — KDD 2024 论文首创 GEO 术语，提出 GEO-bench 与可见度指标；内容改写提升应作为方向证据而非普遍承诺。
- [Wan et al. 2024](https://geo.wiki/zh/papers/what-evidence-convincing-2024) — LLM 在冲突来源中更受相关性影响，科学引用和中立语气并不总是强信号；提示 GEO 写作不能只靠表面权威装饰。

## 使用边界

- 本索引只保留概念提炼和来源 URL，不保存 GEO Wiki 全文。
- 生成文章时应原创表达；若沿用 Answer Loop、七项可引用性信号、六层审计阶梯等框架，应说明参考 GEO Wiki。
- GEO 领域变化快；涉及平台爬虫、官方政策、API、厂商指标定义时，优先联网核验最新官方文档。
