#!/usr/bin/env python3
"""
App Store 评论统计摘要 + 诊断分析脚本

读取 fetch_reviews.py 的输出，生成统计摘要和诊断分析。

用法：
  python3 summarize.py --input reviews.json
  python3 summarize.py --input reviews.json --output stats.json
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime


# ============================================================
# 问题主题分类体系
# ============================================================

ISSUE_THEMES = [
    {
        "key": "stability",
        "label": "性能稳定",
        "description": "慢、卡顿、崩溃、加载失败和响应不稳定。",
        "keywords": [
            "slow", "sluggish", "lag", "bug", "bugs", "crash", "freeze",
            "stuck", "loading", "timeout", "卡", "慢", "崩", "闪退", "无响应",
        ],
    },
    {
        "key": "function",
        "label": "功能体验",
        "description": "更新后功能退化、交互不顺、上传/编辑流程失败。",
        "keywords": [
            "update", "feature", "camera", "photo", "image", "upload", "edit",
            "keyboard", "memory", "version", "功能", "更新", "图片", "照片",
            "上传", "键盘", "交互", "记忆",
        ],
    },
    {
        "key": "pricing",
        "label": "价格限制",
        "description": "订阅、付费、额度限制、退款和收费感知。",
        "keywords": [
            "pay", "paid", "plus", "subscription", "limit", "limited", "money",
            "charge", "billing", "refund", "free", "订阅", "付费", "收费",
            "限制", "免费", "退款",
        ],
    },
    {
        "key": "quality",
        "label": "准确质量",
        "description": "回答错误、理解失败、生成质量低和结果不可信。",
        "keywords": [
            "wrong", "inaccurate", "stupid", "dumb", "hallucination", "answer",
            "quality", "accurate", "follow instructions", "错误", "准确", "质量",
            "理解", "回答", "生成",
        ],
    },
    {
        "key": "account",
        "label": "账号权限",
        "description": "登录、账号、权限、隐私和数据访问问题。",
        "keywords": [
            "login", "account", "password", "permission", "privacy", "data",
            "账号", "账户", "登录", "权限", "隐私", "数据",
        ],
    },
    {
        "key": "trust",
        "label": "服务信任",
        "description": "客服、欺骗感、品牌信任、情绪安全和长期满意度。",
        "keywords": [
            "support", "service", "scam", "rip off", "trust", "unsafe",
            "sensitive", "frustrated", "客服", "服务", "欺骗", "信任", "安全", "失望",
        ],
    },
]


# ============================================================
# 统计摘要
# ============================================================

def summarize_reviews(reviews: list[dict]) -> dict:
    """计算评论统计摘要"""
    if not reviews:
        return {
            "totalReviews": 0, "averageRating": 0,
            "ratingDistribution": {}, "versionDistribution": [],
            "negativeShare": 0, "positiveShare": 0,
        }

    rating_dist = defaultdict(int)
    version_buckets = defaultdict(lambda: {"count": 0, "ratingSum": 0})
    rating_sum = 0
    negative_count = 0
    positive_count = 0

    for review in reviews:
        rating = int(review.get("rating", 0) or 0)
        rating_sum += rating
        rating_dist[str(rating)] = rating_dist.get(str(rating), 0) + 1

        if rating <= 2:
            negative_count += 1
        if rating >= 4:
            positive_count += 1

        version = review.get("version") or "Unknown"
        bucket = version_buckets[version]
        bucket["count"] += 1
        bucket["ratingSum"] += rating

    sorted_by_date = sorted(reviews, key=lambda r: r.get("updated", ""), reverse=True)

    version_distribution = sorted(
        [
            {
                "version": v,
                "count": b["count"],
                "averageRating": round(b["ratingSum"] / b["count"], 2) if b["count"] else 0,
            }
            for v, b in version_buckets.items()
        ],
        key=lambda x: x["count"],
        reverse=True,
    )[:8]

    return {
        "totalReviews": len(reviews),
        "averageRating": round(rating_sum / len(reviews), 2),
        "ratingDistribution": dict(sorted(rating_dist.items())),
        "versionDistribution": version_distribution,
        "latestReviewDate": sorted_by_date[0].get("updated") if sorted_by_date else None,
        "oldestReviewDate": sorted_by_date[-1].get("updated") if sorted_by_date else None,
        "negativeShare": round(negative_count / len(reviews), 3),
        "positiveShare": round(positive_count / len(reviews), 3),
    }


def sort_reviews_for_analysis(reviews: list[dict]) -> list[dict]:
    """为 AI 分析排序评论（差评优先，然后按日期）"""
    def sort_key(review):
        rating = int(review.get("rating", 0) or 0)
        updated = review.get("updated", "")
        is_negative = 0 if rating <= 2 else 1
        return (is_negative, updated)

    return sorted(reviews, key=sort_key)


# ============================================================
# 诊断分析
# ============================================================

def _rating_of(review: dict) -> int:
    return int(review.get("rating", 0) or 0)


def _review_text(review: dict) -> str:
    return f"{review.get('title', '')} {review.get('content', '')}".lower()


def _review_day(review: dict) -> str:
    updated = review.get("updated", "")
    if not updated:
        return "未知日期"
    try:
        return updated[:10]
    except Exception:
        return "未知日期"


def _matched_issue_keys(review: dict) -> list[str]:
    """匹配评论的问题主题分类"""
    rating = _rating_of(review)
    if rating > 3:
        return []

    text = _review_text(review)
    keys = [
        theme["key"]
        for theme in ISSUE_THEMES
        if any(kw in text for kw in theme["keywords"])
    ]
    return keys if keys else ["function"]


def build_review_diagnostics(reviews: list[dict]) -> dict:
    """构建诊断分析"""
    if not reviews:
        return {
            "versionTrend": [], "issueThemes": [],
            "issueHeatmap": [], "sentimentTimeline": [],
            "insights": [], "sampleSize": 0,
        }

    # 版本桶
    version_buckets = defaultdict(lambda: {
        "reviewCount": 0, "ratingSum": 0,
        "negativeCount": 0, "neutralCount": 0, "positiveCount": 0,
        "latestTime": "", "issueCounts": {t["key"]: 0 for t in ISSUE_THEMES},
    })

    # 时间线桶
    timeline_buckets = defaultdict(lambda: {
        "ratingSum": 0, "positive": 0, "neutral": 0, "negative": 0, "total": 0,
    })

    for review in reviews:
        rating = _rating_of(review)
        version = review.get("version") or "Unknown"
        vb = version_buckets[version]

        vb["reviewCount"] += 1
        vb["ratingSum"] += rating
        vb["latestTime"] = max(vb["latestTime"], review.get("updated", ""))

        if rating <= 2:
            vb["negativeCount"] += 1
        elif rating >= 4:
            vb["positiveCount"] += 1
        else:
            vb["neutralCount"] += 1

        for key in _matched_issue_keys(review):
            vb["issueCounts"][key] = vb["issueCounts"].get(key, 0) + 1

        day = _review_day(review)
        tb = timeline_buckets[day]
        tb["total"] += 1
        tb["ratingSum"] += rating
        if rating <= 2:
            tb["negative"] += 1
        elif rating >= 4:
            tb["positive"] += 1
        else:
            tb["neutral"] += 1

    # 版本趋势（取最近 8 个版本，按时间排序）
    selected_versions = sorted(
        version_buckets.items(),
        key=lambda x: x[1]["latestTime"],
        reverse=True,
    )[:8]
    selected_versions = sorted(selected_versions, key=lambda x: x[1]["latestTime"])

    version_trend = []
    for version, vb in selected_versions:
        rc = vb["reviewCount"]
        version_trend.append({
            "version": version,
            "reviewCount": rc,
            "averageRating": round(vb["ratingSum"] / rc, 2) if rc else 0,
            "negativeShare": round(vb["negativeCount"] / rc * 100, 1) if rc else 0,
            "positiveShare": round(vb["positiveCount"] / rc * 100, 1) if rc else 0,
            "negativeCount": vb["negativeCount"],
            "neutralCount": vb["neutralCount"],
            "positiveCount": vb["positiveCount"],
        })

    # 问题主题
    issue_themes = [
        {"key": t["key"], "label": t["label"], "description": t["description"]}
        for t in ISSUE_THEMES
    ]

    # 问题热力图
    issue_heatmap = []
    for vi, (version, vb) in enumerate(selected_versions):
        rc = vb["reviewCount"]
        for ti, theme in enumerate(ISSUE_THEMES):
            count = vb["issueCounts"].get(theme["key"], 0)
            issue_heatmap.append({
                "version": version,
                "themeKey": theme["key"],
                "themeLabel": theme["label"],
                "versionIndex": vi,
                "themeIndex": ti,
                "value": round(count / rc * 100, 1) if rc else 0,
                "count": count,
                "total": rc,
            })

    # 情感时间线（最近 21 天）
    sentiment_timeline = sorted(timeline_buckets.items(), key=lambda x: x[0])[-21:]
    sentiment_timeline = [
        {
            "date": day,
            "positive": tb["positive"],
            "neutral": tb["neutral"],
            "negative": tb["negative"],
            "total": tb["total"],
            "averageRating": round(tb["ratingSum"] / tb["total"], 2) if tb["total"] else 0,
        }
        for day, tb in sentiment_timeline
    ]

    # 诊断洞察
    insights = _build_insights(version_trend, issue_heatmap, sentiment_timeline, len(reviews))

    return {
        "versionTrend": version_trend,
        "issueThemes": issue_themes,
        "issueHeatmap": issue_heatmap,
        "sentimentTimeline": sentiment_timeline,
        "insights": insights,
        "sampleSize": len(reviews),
    }


def _build_insights(version_trend, heatmap, timeline, sample_size) -> list[dict]:
    """生成诊断洞察"""
    insights = []

    # 样本覆盖
    insights.append({
        "label": "样本覆盖",
        "value": f"{sample_size} 条",
        "description": "基于当前缓存评论生成版本趋势、痛点密度和时间线。",
        "tone": "zinc",
    })

    # 高风险版本
    enough = [vt for vt in version_trend if vt["reviewCount"] >= 2]
    if enough:
        risky = max(enough, key=lambda x: (x["negativeShare"], -x["averageRating"]))
        insights.append({
            "label": "高风险版本",
            "value": risky["version"],
            "description": f"{risky['reviewCount']} 条评论中差评占比 {risky['negativeShare']}%，适合作为版本复盘入口。",
            "tone": "rose",
        })
    else:
        insights.append({
            "label": "高风险版本",
            "value": "样本不足",
            "description": "版本样本过少，暂不判断单一版本风险。",
            "tone": "zinc",
        })

    # 主导痛点
    if heatmap:
        hottest = max(heatmap, key=lambda x: (x["count"], x["value"]))
        if hottest["count"] > 0:
            insights.append({
                "label": "主导痛点",
                "value": hottest["themeLabel"],
                "description": f"{hottest['version']} 版本中出现 {hottest['count']} 条相关差评，密度 {hottest['value']}%。",
                "tone": "amber",
            })
        else:
            insights.append({
                "label": "主导痛点",
                "value": "暂无集中主题",
                "description": "当前差评主题分散，建议继续扩大样本或更新洞察。",
                "tone": "zinc",
            })

    # 差评峰值 / 正向版本
    if timeline:
        spike = max(timeline, key=lambda x: (x["negative"], x["total"]))
        if spike["negative"] > 0:
            insights.append({
                "label": "差评峰值",
                "value": spike["date"],
                "description": f"出现 {spike['negative']} 条差评，可回看当天更新、故障或策略变化。",
                "tone": "sky",
            })
        elif enough:
            strongest = max(enough, key=lambda x: (x["averageRating"], x["reviewCount"]))
            insights.append({
                "label": "正向版本",
                "value": strongest["version"],
                "description": f"平均评分 {strongest['averageRating']}，可反查该版本保留的体验优势。",
                "tone": "emerald",
            })

    return insights


# ============================================================
# 来源分布
# ============================================================

def build_source_breakdown(reviews: list[dict]) -> dict:
    """构建评论来源分布"""
    source_counts = defaultdict(int)
    country_counts = defaultdict(int)
    for review in reviews:
        source = review.get("source", "unknown")
        source_counts[source] += 1
        country_counts[review.get("country", "unknown")] += 1

    return {
        "bySource": dict(source_counts),
        "byCountry": dict(country_counts),
    }


# ============================================================
# 主流程
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="App Store 评论统计摘要与诊断分析")
    parser.add_argument("--input", required=True, help="评论数据 JSON 文件路径")
    parser.add_argument("--output", help="输出文件路径（默认 stdout）")
    args = parser.parse_args()

    # 读取评论数据
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"错误：无法读取输入文件: {e}", file=sys.stderr)
        sys.exit(1)

    reviews = data.get("reviews", [])
    app_id = data.get("appId", "")
    app_name = data.get("appName", "")
    country = data.get("country", "")

    if not reviews:
        print("警告：没有评论数据", file=sys.stderr)
        output = {
            "appId": app_id, "appName": app_name, "country": country,
            "summary": summarize_reviews([]),
            "diagnostics": build_review_diagnostics([]),
            "sourceBreakdown": build_source_breakdown([]),
        }
    else:
        # 统计摘要
        summary = summarize_reviews(reviews)
        print(f"统计摘要: {summary['totalReviews']} 条评论, 平均评分 {summary['averageRating']}")

        # 诊断分析
        diagnostics = build_review_diagnostics(reviews)
        print(f"诊断分析: {len(diagnostics['versionTrend'])} 个版本, {len(diagnostics['insights'])} 条洞察")

        # 来源分布
        source_breakdown = build_source_breakdown(reviews)

        # 排序评论（差评优先）
        sorted_reviews = sort_reviews_for_analysis(reviews)

        # 构建输出
        output = {
            "appId": app_id,
            "appName": app_name,
            "country": country,
            "summary": summary,
            "diagnostics": diagnostics,
            "sourceBreakdown": source_breakdown,
            "sortedReviewsForAnalysis": [
                {
                    "id": r.get("id", ""),
                    "title": r.get("title", ""),
                    "content": (r.get("content", "") or "")[:700],
                    "rating": r.get("rating", ""),
                    "version": r.get("version", ""),
                    "updated": r.get("updated", ""),
                    "authorName": r.get("authorName", ""),
                    "source": r.get("source", ""),
                }
                for r in sorted_reviews[:100]  # 最多 100 条供 AI 分析
            ],
        }

    # 输出
    output_json = json.dumps(output, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"\n已保存到 {args.output}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
