# 信息收集日报

生成时间：{{ generated_at }}

## 💡 核心内容与投资分析

### 🗣️ 核心话题
> 基于关键词分析提取的高频词汇

{% if analysis.core_topics %}
{{ analysis.core_topics | join(', ') }}
{% else %}
暂无足够数据进行分析。
{% endif %}

### 📈 股票投资影响分析
> 筛选出包含投资相关关键词（如股票、行情、板块等）的内容

{% if analysis.investment_signals %}
{% for signal in analysis.investment_signals %}
- **{{ signal.item.author }}** ({{ signal.item.time }})
  - **关键词**: {{ signal.matched_keywords | join(', ') }}
  - **内容摘要**: {{ signal.item.content | truncate(100) }}
  - [查看原文]({{ signal.item.link }})
{% endfor %}
{% else %}
未检测到明显的直接投资相关信号。
{% endif %}

## 🐦 Twitter 趋势与 AI 内容推荐
> 按照“小白 AI 内容”视角评分排序，筛选高价值内容。

{% if data.twitter %}
{% for item in data.twitter %}
### {{ loop.index }}. {{ item.author }} (推荐指数: {{ item.score }})
> **推荐理由**: {{ item.recommendation_reason }}
> **互动数据**: 💬 {{ item.stats.reply }} | 🔁 {{ item.stats.repost }} | 👍 {{ item.stats.like }} | 🔖 {{ item.stats.bookmark }}
> **发布时间**: {{ item.time }} | [原文链接]({{ item.link }})

{{ item.content }}

---
{% endfor %}
{% else %}
暂无 Twitter 数据。
{% endif %}

## 📦 其他来源内容列表

{% for module_name, items in data.items() %}
{% if module_name != 'twitter' %}
### 来源：{{ module_name|capitalize }}

{% for item in items %}
#### {{ loop.index }}. {{ item.author }} ({{ item.time }})
原文链接：[点击查看]({{ item.link }})

{{ item.content }}

---
{% endfor %}
{% endif %}
{% endfor %}

## 📝 总结
共收集 {{ total_items }} 条信息。
