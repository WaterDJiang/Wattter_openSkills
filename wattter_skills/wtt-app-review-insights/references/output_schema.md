# 输出 JSON Schema 说明

本文件定义了各脚本输出的 JSON 数据结构，供 AI 助手理解和处理。

---

## 1. fetch_reviews.py 输出

```json
{
  "appId": "6448311069",
  "appName": "ChatGPT",
  "country": "us",
  "countryName": "美国",
  "fetchedAt": "2026-06-16T10:00:00Z",
  "totalReviews": 160,
  "appInfo": {
    "id": "6448311069",
    "name": "ChatGPT",
    "country": "us",
    "artistName": "OpenAI",
    "artworkUrl": "https://...",
    "trackViewUrl": "https://...",
    "averageUserRating": 4.5,
    "userRatingCount": 1500000,
    "primaryGenreName": "Productivity",
    "version": "1.2024.150",
    "currentVersionReleaseDate": "2024-06-01T00:00:00Z"
  },
  "reviews": [
    {
      "id": "1234567890",
      "updated": "2024-06-15T08:30:00-07:00",
      "rating": "1",
      "version": "1.2024.150",
      "title": "Very slow",
      "content": "The app is extremely slow...",
      "authorName": "User123",
      "voteCount": "5",
      "appId": "6448311069",
      "country": "us",
      "source": "apple-rss"           // 或 "app-store-html"
    }
  ]
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `appId` | string | App Store 应用 ID |
| `appName` | string | 应用名称 |
| `country` | string | 国家代码（2 位小写） |
| `fetchedAt` | string | 抓取时间（ISO 8601） |
| `totalReviews` | number | 评论总数 |
| `reviews[].id` | string | 评论唯一 ID |
| `reviews[].rating` | string | 评分 1-5 |
| `reviews[].version` | string | 评论对应的 App 版本 |
| `reviews[].source` | string | 数据来源：`apple-rss` 或 `app-store-html` |

---

## 2. summarize.py 输出

```json
{
  "appId": "6448311069",
  "appName": "ChatGPT",
  "country": "us",
  "summary": {
    "totalReviews": 160,
    "averageRating": 3.85,
    "ratingDistribution": {"1": 25, "2": 15, "3": 20, "4": 35, "5": 65},
    "versionDistribution": [
      {"version": "1.2024.150", "count": 40, "averageRating": 3.5},
      {"version": "1.2024.140", "count": 30, "averageRating": 4.1}
    ],
    "latestReviewDate": "2024-06-15T08:30:00-07:00",
    "oldestReviewDate": "2024-03-10T12:00:00-07:00",
    "negativeShare": 0.25,
    "positiveShare": 0.625
  },
  "diagnostics": {
    "versionTrend": [
      {
        "version": "1.2024.140",
        "reviewCount": 30,
        "averageRating": 4.1,
        "negativeShare": 16.7,
        "positiveShare": 73.3,
        "negativeCount": 5,
        "neutralCount": 3,
        "positiveCount": 22
      }
    ],
    "issueThemes": [
      {"key": "stability", "label": "性能稳定", "description": "..."},
      {"key": "function", "label": "功能体验", "description": "..."}
    ],
    "issueHeatmap": [
      {
        "version": "1.2024.150",
        "themeKey": "stability",
        "themeLabel": "性能稳定",
        "versionIndex": 0,
        "themeIndex": 0,
        "value": 15.0,
        "count": 6,
        "total": 40
      }
    ],
    "sentimentTimeline": [
      {
        "date": "2024-06-14",
        "positive": 5,
        "neutral": 2,
        "negative": 3,
        "total": 10,
        "averageRating": 3.4
      }
    ],
    "insights": [
      {
        "label": "高风险版本",
        "value": "1.2024.150",
        "description": "40 条评论中差评占比 37.5%",
        "tone": "rose"
      }
    ],
    "sampleSize": 160
  },
  "sourceBreakdown": {
    "bySource": {"apple-rss": 120, "app-store-html": 40},
    "byCountry": {"us": 130, "cn": 30}
  },
  "sortedReviewsForAnalysis": [
    {
      "id": "123",
      "title": "Very slow",
      "content": "The app is extremely slow after the latest update...",
      "rating": "1",
      "version": "1.2024.150",
      "updated": "2024-06-15T08:30:00-07:00",
      "authorName": "User123",
      "source": "apple-rss"
    }
  ]
}
```

### 关键字段说明

| 字段 | 说明 |
|------|------|
| `summary.negativeShare` | 差评（1-2 星）占比，0-1 之间 |
| `summary.positiveShare` | 好评（4-5 星）占比，0-1 之间 |
| `diagnostics.versionTrend` | 版本趋势，最多 8 个版本，按时间排序 |
| `diagnostics.issueHeatmap` | 问题热力图：版本 × 问题主题的交叉分析 |
| `diagnostics.insights` | 诊断洞察，tone 值：rose(风险)/amber(警告)/emerald(正面)/sky(信息)/zinc(中性) |
| `sortedReviewsForAnalysis` | 排序后的评论样本（差评优先），最多 100 条 |

---

## 3. AI 分析输出 Schema

AI 完成分析后，应输出以下 JSON 结构：

```json
{
  "executiveSummary": "3-5 句中文总结...",
  "painPoints": [
    {
      "title": "≤14字痛点标题",
      "summary": "1句影响说明",
      "evidence": "原评论短证据≤60字",
      "priority": "high|medium|low"
    }
  ],
  "opportunities": [
    {
      "title": "≤14字机会标题",
      "summary": "1句说明",
      "evidence": "原评论短证据≤60字",
      "priority": "high|medium|low"
    }
  ],
  "positiveSignals": [
    {
      "title": "≤14字正面信号标题",
      "summary": "1句说明",
      "evidence": "原评论短证据≤60字",
      "priority": "high|medium|low"
    }
  ],
  "userSegments": [
    {
      "title": "≤14字用户群标题",
      "summary": "1句说明",
      "evidence": "原评论短证据≤60字",
      "priority": "high|medium|low"
    }
  ],
  "versionRisks": [
    {
      "title": "≤14字风险标题",
      "summary": "1句说明",
      "evidence": "原评论短证据≤60字",
      "priority": "high|medium|low"
    }
  ],
  "actionPlan": [
    {
      "title": "≤14字可执行动作",
      "summary": "一句可执行动作",
      "evidence": "为什么要做≤60字",
      "priority": "high|medium|low"
    }
  ],
  "queryAngles": ["后续深挖问题1", "后续深挖问题2"]
}
```

### 优先级定义

| 优先级 | 含义 | 选择标准 |
|--------|------|----------|
| `high` | 紧急/高影响 | 高频出现 + 严重影响用户体验 |
| `medium` | 重要/中影响 | 有一定频率 + 有明确改进空间 |
| `low` | 观察/低影响 | 低频出现 + 影响有限 |
