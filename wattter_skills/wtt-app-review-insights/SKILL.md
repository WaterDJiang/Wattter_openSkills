---
name: wtt-app-review-insights
description: App Store 评论洞察分析工具。输入 App 名称、URL 或 App ID，自动抓取评论并通过 AI 深度挖掘产品痛点、机会、正面信号、用户分层、版本风险和行动建议，输出结构化洞察报告。当用户需要以下操作时使用：(1) 分析某个 App 的用户评论或评价，(2) 了解 App Store 应用的用户反馈和痛点，(3) 做竞品评论对比分析，(4) 查看应用评分和版本趋势，(5) 从用户评价中提取产品改进机会，(6) 分析应用差评原因或好评亮点。适用于产品经理、运营人员和竞品分析场景。
---

# App Store 评论洞察 (App Review Insights)

将 App Store 用户评论转化为结构化产品洞察报告。

## 工作流程

1. **解析 App**：从用户输入（URL / App ID / 名称）提取 App ID 和国家
2. **抓取评论**：运行 `scripts/fetch_reviews.py`
3. **统计分析**：运行 `scripts/summarize.py`
4. **AI 洞察挖掘**：按 `references/analysis_prompts.md` 模板执行深度分析

## 步骤 1：解析 App 信息

从用户输入中提取 App ID 和国家代码：
- App Store URL → 自动解析 ID 和国家
- 纯数字 → 作为 App ID 直接使用
- 应用名称 → 调用 iTunes Search API 查找

## 步骤 2：抓取评论

```bash
# App ID + 国家
python3 scripts/fetch_reviews.py --app-id 6448311069 --country us

# 按名称搜索
python3 scripts/fetch_reviews.py --search "ChatGPT" --country us

# App Store URL
python3 scripts/fetch_reviews.py --url "https://apps.apple.com/cn/app/豆包/id6459478672"

# 指定评论数和输出
python3 scripts/fetch_reviews.py --app-id 6448311069 --country cn --max-reviews 200 --output ./reviews.json
```

## 步骤 3：统计分析

```bash
python3 scripts/summarize.py --input ./reviews.json --output ./stats.json
```

## 步骤 4：AI 洞察挖掘

读取评论数据和统计摘要，按 `references/analysis_prompts.md` 中的核心洞察模板执行分析，输出 7 维度结构化洞察：概览摘要、痛点、机会、正面信号、用户分层、版本风险、行动建议。按模板末尾的 Markdown 报告格式输出最终报告。

## 依赖

```bash
pip install -r scripts/../requirements.txt
```

Python 3.8+，仅需 `requests`。无需外部 LLM API（AI 分析由 Claude 自身完成）。

## References

- **`references/analysis_prompts.md`** — AI 洞察挖掘 Prompt 模板和报告模板（**步骤 4 必读**）
- **`references/output_schema.md`** — 脚本输出 JSON Schema 说明（**步骤 3-4 之间读取**，理解 summarize.py 输出结构时使用）
- **`references/methodology.md`** — 方法论和分析框架说明（**可选**，需要深入理解分析逻辑或定制分析维度时读取）
