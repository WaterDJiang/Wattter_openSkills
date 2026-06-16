# Twitter 趋势与 AI 内容推荐报告

生成时间：{{ generated_at }}

## 📊 数据概览
{% if data.twitter %}
- 采集数量：{{ data.twitter | length }}
- 最高推荐指数：{{ data.twitter[0].score }} ({{ data.twitter[0].author }})
{% else %}
未采集到数据。
{% endif %}

## 📑 详细清单

| 排名 | 推荐指数 | 作者 | 互动数据 (💬/🔁/👍/🔖) | 内容摘要 | 链接 |
|---|---|---|---|---|---|
{% for item in data.twitter %}
| {{ loop.index }} | **{{ item.score }}** | {{ item.author }} | {{ item.stats.reply }} / {{ item.stats.repost }} / {{ item.stats.like }} / {{ item.stats.bookmark }} | {{ item.content | truncate(50) }} | [查看]({{ item.link }}) |
{% endfor %}

## 💡 推荐理由详情
{% for item in data.twitter[:5] %}
### Top {{ loop.index }}: {{ item.author }} (Score: {{ item.score }})
- **推荐理由**: {{ item.recommendation_reason }}
- **完整内容**:
> {{ item.content }}
{% endfor %}
