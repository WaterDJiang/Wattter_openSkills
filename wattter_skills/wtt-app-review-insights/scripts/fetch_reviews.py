#!/usr/bin/env python3
"""
App Store 评论抓取脚本

支持双源抓取：
1. Apple RSS（结构化、版本感知、分页）
2. App Store HTML（覆盖更广、多国家补充）

用法：
  python3 fetch_reviews.py --app-id 6448311069 --country us
  python3 fetch_reviews.py --app-id 6448311069 --country cn --max-reviews 200
  python3 fetch_reviews.py --search "ChatGPT" --country us
  python3 fetch_reviews.py --url "https://apps.apple.com/us/app/chatgpt/id6448311069"
"""

import argparse
import json
import re
import sys
import time
from urllib.parse import quote
from datetime import datetime, timezone

import requests

# ============================================================
# 常量
# ============================================================

ITUNES_BASE_URL = "https://itunes.apple.com"
APP_STORE_WEB_URL = "https://apps.apple.com"

MAX_PAGES = 20
MAX_REVIEWS = 500
DEFAULT_COUNTRY = "cn"
MAX_RETRIES = 3
RETRY_DELAY = 1.0
REQUEST_TIMEOUT = 15

HTML_FALLBACK_COUNTRIES = [
    "cn", "us", "hk", "tw", "sg", "jp", "gb", "ca", "au",
    "de", "my", "th", "kr", "in", "br", "ie", "it", "nl", "ch",
]

COUNTRY_NAMES = {
    "us": "美国", "cn": "中国", "jp": "日本", "kr": "韩国",
    "gb": "英国", "de": "德国", "fr": "法国", "it": "意大利",
    "es": "西班牙", "br": "巴西", "in": "印度", "au": "澳大利亚",
    "ca": "加拿大", "mx": "墨西哥", "nl": "荷兰", "se": "瑞典",
    "sg": "新加坡", "my": "马来西亚", "th": "泰国", "id": "印度尼西亚",
    "ph": "菲律宾", "vn": "越南", "tw": "台湾", "hk": "香港",
    "ru": "俄罗斯", "no": "挪威", "dk": "丹麦", "fi": "芬兰",
}


# ============================================================
# App 解析
# ============================================================

def normalize_country(country: str) -> str:
    """标准化国家代码"""
    cleaned = (country or DEFAULT_COUNTRY).strip().lower()
    if cleaned == "uk":
        return "gb"
    return cleaned if re.match(r"^[a-z]{2}$", cleaned) else DEFAULT_COUNTRY


def parse_app_store_url(url: str) -> dict | None:
    """从 App Store URL 解析应用信息"""
    try:
        id_match = re.search(r"id(\d+)", url)
        if not id_match:
            return None
        app_id = id_match.group(1)

        # 提取国家代码
        country = DEFAULT_COUNTRY
        path_match = re.search(r"apple\.com/([a-z]{2})/", url)
        if path_match:
            country = path_match.group(1)

        # 提取应用名称
        name_match = re.search(r"/app/([^/]+)/id\d+", url)
        name = ""
        if name_match:
            name = name_match.group(1).replace("-", " ").replace("+", " ").strip()

        return {"id": app_id, "name": name, "country": country}
    except Exception:
        return None


def lookup_app_by_id(app_id: str, country: str = "cn") -> dict | None:
    """通过 iTunes Lookup API 查找应用"""
    url = f"{ITUNES_BASE_URL}/lookup"
    params = {"id": app_id.strip(), "entity": "software", "country": normalize_country(country)}
    try:
        resp = _fetch_json(url, params=params)
        results = resp.get("results", [])
        if not results:
            return None
        r = results[0]
        return _map_itunes_result(r, normalize_country(country))
    except Exception as e:
        print(f"[WARN] Lookup failed for app {app_id}: {e}", file=sys.stderr)
        return None


def search_apps(term: str, country: str = "cn", limit: int = 5) -> list[dict]:
    """通过 iTunes Search API 搜索应用"""
    url = f"{ITUNES_BASE_URL}/search"
    params = {
        "term": term.strip(),
        "entity": "software",
        "country": normalize_country(country),
        "limit": str(min(max(limit, 1), 10)),
    }
    try:
        resp = _fetch_json(url, params=params)
        return [_map_itunes_result(r, normalize_country(country)) for r in resp.get("results", [])]
    except Exception as e:
        print(f"[WARN] Search failed for '{term}': {e}", file=sys.stderr)
        return []


def resolve_app_query(query: str, country: str = "cn") -> dict:
    """解析用户输入，返回 App 信息（支持 URL / ID / 名称）"""
    trimmed = query.strip()
    if not trimmed:
        raise ValueError("请输入 App Store 链接、App ID 或应用名称")

    # 尝试解析 URL
    parsed = parse_app_store_url(trimmed)
    if parsed:
        app = lookup_app_by_id(parsed["id"], parsed["country"])
        if app:
            return {**app, "source": "url", "candidates": [app]}
        return {
            "id": parsed["id"], "name": parsed["name"],
            "country": parsed["country"], "artistName": "",
            "artworkUrl": "", "source": "url", "candidates": [],
        }

    # 尝试作为 App ID
    if re.match(r"^\d+$", trimmed):
        app = lookup_app_by_id(trimmed, country)
        if not app:
            raise ValueError(f"没有在 {normalize_country(country).upper()} 区找到 App ID {trimmed}")
        return {**app, "source": "id", "candidates": [app]}

    # 按名称搜索
    candidates = search_apps(trimmed, country, 6)
    if not candidates:
        raise ValueError(f"没有找到 \"{trimmed}\" 对应的 iOS App")
    return {**candidates[0], "source": "search", "candidates": candidates}


def _map_itunes_result(r: dict, country: str) -> dict:
    """映射 iTunes API 返回结果"""
    artwork = r.get("artworkUrl512") or r.get("artworkUrl100") or ""
    artwork = re.sub(r"/\d+x\d+bb\.(png|jpg|jpeg)$", r"/512x512bb.\1", artwork)
    return {
        "id": str(r.get("trackId", "")),
        "name": r.get("trackName", ""),
        "country": country,
        "artistName": r.get("artistName", ""),
        "artworkUrl": artwork,
        "trackViewUrl": r.get("trackViewUrl", ""),
        "averageUserRating": r.get("averageUserRating"),
        "userRatingCount": r.get("userRatingCount"),
        "primaryGenreName": r.get("primaryGenreName", ""),
        "version": r.get("version", ""),
        "currentVersionReleaseDate": r.get("currentVersionReleaseDate", ""),
    }


# ============================================================
# 评论抓取 — Apple RSS
# ============================================================

def fetch_rss_reviews(app_id: str, country: str, max_pages: int = MAX_PAGES) -> list[dict]:
    """通过 Apple RSS Feed 抓取评论（尽量多抓，后续统一截取）"""
    all_reviews = []

    for page in range(1, max_pages + 1):
        urls = _build_rss_urls(app_id, country, page)
        page_reviews = []

        for url in urls:
            try:
                data = _fetch_json(url, max_retries=1)  # RSS 分页不重试，快速跳过
                feed = data.get("feed", {})
                entries = feed.get("entry", [])
                if not entries:
                    continue
                for entry in entries:
                    review = _parse_rss_entry(entry, app_id, country)
                    if review:
                        page_reviews.append(review)
                if page_reviews:
                    break  # 第一个成功的 URL 就够了
            except Exception as e:
                print(f"[DEBUG] RSS page {page} URL failed: {e}", file=sys.stderr)
                continue

        if not page_reviews:
            break

        all_reviews.extend(page_reviews)
        print(f"  RSS page {page}: 获取 {len(page_reviews)} 条评论 (累计 {len(all_reviews)})")

        time.sleep(0.5)

    return all_reviews


def _build_rss_urls(app_id: str, country: str, page: int) -> list[str]:
    """构建 RSS 评论 URL（多格式尝试）"""
    return [
        f"{ITUNES_BASE_URL}/{country}/rss/customerreviews/id={app_id}/page={page}/json",
        f"{ITUNES_BASE_URL}/{country}/rss/customerreviews/page={page}/id={app_id}/sortBy=mostRecent/json",
        f"{ITUNES_BASE_URL}/{country}/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json",
    ]


def _parse_rss_entry(entry: dict, app_id: str, country: str) -> dict | None:
    """解析单条 RSS 评论"""
    try:
        entry_id = entry.get("id", {})
        if isinstance(entry_id, dict):
            entry_id = entry_id.get("label", "")
        if not entry_id:
            return None

        updated = entry.get("updated", {})
        if isinstance(updated, dict):
            updated = updated.get("label", "")

        title = entry.get("title", {})
        if isinstance(title, dict):
            title = title.get("label", "")

        content = entry.get("content", {})
        if isinstance(content, dict):
            content = content.get("label", "")

        rating = entry.get("im:rating", {})
        if isinstance(rating, dict):
            rating = rating.get("label", "0")

        version = entry.get("im:version", {})
        if isinstance(version, dict):
            version = version.get("label", "Unknown")

        author = entry.get("author", {})
        if isinstance(author, dict):
            author_name = author.get("name", {})
            if isinstance(author_name, dict):
                author_name = author_name.get("label", "")
            else:
                author_name = str(author_name)
        else:
            author_name = ""

        vote_count = entry.get("im:voteCount", {})
        if isinstance(vote_count, dict):
            vote_count = vote_count.get("label", "0")

        if not title and not content:
            return None

        return {
            "id": str(entry_id),
            "updated": updated or datetime.now(timezone.utc).isoformat(),
            "rating": str(rating),
            "version": version or "Unknown",
            "title": title or "",
            "content": content or "",
            "authorName": author_name or "App Store 用户",
            "voteCount": str(vote_count),
            "appId": app_id,
            "country": country,
            "source": "apple-rss",
        }
    except Exception as e:
        print(f"[WARN] Failed to parse RSS entry: {e}", file=sys.stderr)
        return None


# ============================================================
# 评论抓取 — App Store HTML
# ============================================================

def fetch_html_reviews(app_id: str, country: str, max_reviews: int = 100) -> list[dict]:
    """通过 App Store HTML 页面抓取补充评论"""
    countries = _build_html_countries(country)
    all_reviews = []
    seen_ids = set()

    for fallback_country in countries:
        url = f"{APP_STORE_WEB_URL}/{fallback_country}/app/id{app_id}"
        try:
            html = _fetch_text(url)
            reviews = _parse_html_reviews(html, app_id, fallback_country)
            added = 0
            for review in reviews:
                if review["id"] not in seen_ids:
                    seen_ids.add(review["id"])
                    all_reviews.append(review)
                    added += 1
            print(f"  HTML {fallback_country}: 解析 {len(reviews)} 条, 新增 {added} 条 (累计 {len(all_reviews)})")
            if len(all_reviews) >= max_reviews:
                break
        except Exception as e:
            print(f"[DEBUG] HTML fallback failed for {fallback_country}: {e}", file=sys.stderr)
        time.sleep(0.15)

    return all_reviews[:max_reviews]


def _build_html_countries(country: str) -> list[str]:
    """构建 HTML 抓取的国家列表（指定国家优先）"""
    normalized = country.lower()
    countries = [normalized]
    for c in HTML_FALLBACK_COUNTRIES:
        if c != normalized:
            countries.append(c)
    return countries


def _parse_html_reviews(html: str, app_id: str, country: str) -> list[dict]:
    """解析 App Store HTML 页面中的评论"""
    match = re.search(
        r'<script type="application/json" id="serialized-server-data">(.*?)</script>',
        html, re.DOTALL,
    )
    if not match:
        return []

    try:
        payload = json.loads(match.group(1))
    except json.JSONDecodeError:
        return []

    reviews = []
    seen_ids = set()
    _walk_for_reviews(payload, app_id, country, reviews, seen_ids)
    return reviews


def _walk_for_reviews(obj, app_id: str, country: str, reviews: list, seen_ids: set):
    """递归遍历 JSON 树，提取 Review 对象"""
    if isinstance(obj, list):
        for item in obj:
            _walk_for_reviews(item, app_id, country, reviews, seen_ids)
        return

    if not isinstance(obj, dict):
        return

    if obj.get("$kind") == "Review":
        review = _parse_web_review(obj, app_id, country)
        if review and review["id"] not in seen_ids:
            seen_ids.add(review["id"])
            reviews.append(review)

    for value in obj.values():
        if isinstance(value, (dict, list)):
            _walk_for_reviews(value, app_id, country, reviews, seen_ids)


def _parse_web_review(review: dict, app_id: str, country: str) -> dict | None:
    """解析单条 HTML 评论"""
    rid = review.get("id")
    title = review.get("title")
    contents = review.get("contents")
    rating = review.get("rating")
    if not rid or not title or not contents or not rating:
        return None

    return {
        "id": str(rid),
        "updated": review.get("date") or datetime.now(timezone.utc).isoformat(),
        "rating": str(rating),
        "version": "Unknown",
        "title": title,
        "content": contents,
        "authorName": review.get("reviewerName") or "App Store 用户",
        "voteCount": "0",
        "appId": app_id,
        "country": country,
        "source": "app-store-html",
    }


# ============================================================
# 去重
# ============================================================

def deduplicate_reviews(reviews: list[dict]) -> list[dict]:
    """基于评论 ID 去重"""
    seen = set()
    unique = []
    for review in reviews:
        rid = review.get("id", "")
        if rid and rid not in seen:
            seen.add(rid)
            unique.append(review)
    return unique


# ============================================================
# 主流程
# ============================================================

def fetch_all_reviews(app_id: str, country: str, max_reviews: int = MAX_REVIEWS) -> list[dict]:
    """完整抓取流程：RSS + HTML，去重"""
    print(f"开始抓取 App {app_id} ({COUNTRY_NAMES.get(country, country.upper())} 区) 的评论...")

    # 1. RSS 抓取（尽量多抓，后续统一截取）
    print("\n[1/2] Apple RSS 抓取...")
    rss_reviews = fetch_rss_reviews(app_id, country, max_pages=MAX_PAGES)
    print(f"  RSS 共获取 {len(rss_reviews)} 条评论")

    # 2. HTML 补充（仅在 RSS 数量不足时）
    html_reviews = []
    if len(rss_reviews) < max_reviews:
        remaining = max_reviews - len(rss_reviews)
        print(f"\n[2/2] App Store HTML 补充 (还需 {remaining} 条)...")
        html_reviews = fetch_html_reviews(app_id, country, max_reviews=remaining)
        print(f"  HTML 共获取 {len(html_reviews)} 条评论")
    else:
        print("\n[2/2] RSS 已满足数量需求，跳过 HTML 补充")

    # 3. 合并去重
    all_reviews = rss_reviews + html_reviews
    unique_reviews = deduplicate_reviews(all_reviews)
    result = unique_reviews[:max_reviews]

    print(f"\n抓取完成: 共 {len(result)} 条评论 (RSS {len(rss_reviews)} + HTML {len(html_reviews)}, 去重前 {len(all_reviews)})")

    return result


# ============================================================
# 网络请求
# ============================================================

def _fetch_json(url: str, params: dict | None = None, max_retries: int = MAX_RETRIES) -> dict:
    """带重试的 JSON 请求"""
    headers = {
        "User-Agent": "AppReviewInsights/1.0",
        "Accept": "application/json",
    }
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if attempt < max_retries - 1:
                delay = RETRY_DELAY * (attempt + 1)
                print(f"[RETRY] 请求失败 ({attempt + 1}/{max_retries}): {e}, {delay}s 后重试", file=sys.stderr)
                time.sleep(delay)
            else:
                raise


def _fetch_text(url: str) -> str:
    """带重试的文本请求"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAY * (attempt + 1)
                print(f"[RETRY] 请求失败 ({attempt + 1}/{MAX_RETRIES}): {e}, {delay}s 后重试", file=sys.stderr)
                time.sleep(delay)
            else:
                raise


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="App Store 评论抓取工具")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--app-id", help="App ID（纯数字）")
    group.add_argument("--search", help="应用名称（通过 iTunes Search API 查找）")
    group.add_argument("--url", help="App Store URL")
    parser.add_argument("--country", default=DEFAULT_COUNTRY, help="国家代码（默认 cn）")
    parser.add_argument("--max-reviews", type=int, default=MAX_REVIEWS, help=f"最大评论数（默认 {MAX_REVIEWS}）")
    parser.add_argument("--output", help="输出文件路径（默认 stdout）")

    args = parser.parse_args()

    # 解析 App 信息
    if args.url:
        parsed = parse_app_store_url(args.url)
        if not parsed:
            print("错误：无法解析 App Store URL", file=sys.stderr)
            sys.exit(1)
        app_id = parsed["id"]
        country = normalize_country(parsed["country"])
        app_name = parsed["name"]
    elif args.search:
        try:
            app_info = resolve_app_query(args.search, args.country)
            app_id = app_info["id"]
            country = normalize_country(app_info.get("country", args.country))
            app_name = app_info.get("name", args.search)
            print(f"找到应用: {app_name} (ID: {app_id})")
        except ValueError as e:
            print(f"错误：{e}", file=sys.stderr)
            sys.exit(1)
    else:
        app_id = args.app_id
        country = normalize_country(args.country)
        app_name = ""

    # 尝试获取应用详情
    app_info = lookup_app_by_id(app_id, country)
    if app_info:
        app_name = app_info["name"]
        print(f"应用: {app_name}")
        print(f"开发者: {app_info.get('artistName', 'N/A')}")
        print(f"评分: {app_info.get('averageUserRating', 'N/A')} ({app_info.get('userRatingCount', 'N/A')} 个评分)")

    # 抓取评论
    reviews = fetch_all_reviews(app_id, country, args.max_reviews)

    # 构建输出
    output = {
        "appId": app_id,
        "appName": app_name,
        "country": country,
        "countryName": COUNTRY_NAMES.get(country, country.upper()),
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
        "totalReviews": len(reviews),
        "reviews": reviews,
    }

    if app_info:
        output["appInfo"] = app_info

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
