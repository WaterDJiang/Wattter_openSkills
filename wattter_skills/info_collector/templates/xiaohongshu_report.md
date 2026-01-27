# 小红书调研报告

生成时间：{{ generated_at }}

## 📊 数据概览
{% if data.xiaohongshu %}
- 关键词：{{ data.xiaohongshu[0].keyword }}
- 采集数量：{{ data.xiaohongshu | length }}
{% else %}
未采集到数据。
{% endif %}

## 📑 详细清单

| 标题 | 作者 | 粉丝数 | 点赞数 | 关键词 | 链接 |
|---|---|---|---|---|---|
{% for item in data.xiaohongshu %}
| [{{ item.title }}]({{ item.link }}) | {{ item.author }} | {{ item.followers }} | {{ item.likes }} | {{ item.keyword }} | [查看]({{ item.link }}) |
{% endfor %}
