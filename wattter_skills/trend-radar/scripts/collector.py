import os
import sys
import json
import yaml
import asyncio
import argparse
import datetime
import re
from typing import List, Dict, Any
from collections import Counter
from playwright.async_api import async_playwright

# 路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.yaml")
KEYWORDS_PATH = os.path.join(BASE_DIR, "config", "keywords.txt")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# 确保报告目录存在
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

def load_config() -> Dict[str, Any]:
    """加载 YAML 配置文件"""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}

def load_default_keywords() -> List[str]:
    """从 keywords.txt 加载默认关键词"""
    if os.path.exists(KEYWORDS_PATH):
        with open(KEYWORDS_PATH, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

async def fetch_platform_data(context, p_id: str, platform_config: Dict[str, Any], crawler_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """使用 Playwright 获取指定平台的数据"""
    url = platform_config.get("url")
    name = platform_config.get("name", p_id)
    
    page = await context.new_page()
    try:
        # 遵循 TrendRadar 的做法，模拟真实浏览器行为
        # 尝试直接访问 API，由于是在浏览器上下文中，通常能绕过简单的 Cloudflare 403
        response = await page.goto(url, wait_until="domcontentloaded", timeout=crawler_config.get("timeout", 30) * 1000)
        
        # 检查是否成功获取 JSON
        content = await response.text()
        try:
            data = json.loads(content)
            items = []
            if isinstance(data, dict):
                # 兼容 newsnow 的两种格式: data 字段或 items 字段
                items = data.get("data", data.get("items", []))
            elif isinstance(data, list):
                items = data
            
            # 格式化数据，确保包含来源平台
            formatted_items = []
            for item in items:
                item["platform"] = name
                formatted_items.append(item)
            return formatted_items
        except json.JSONDecodeError:
            # 如果不是 JSON，可能是遇到了 HTML 挑战页面或 403
            return []
    except Exception as e:
        print(f"Error fetching {name}: {e}", file=sys.stderr)
        return []
    finally:
        await page.close()

async def collect_all(target_platforms: List[str], config: Dict[str, Any]) -> Dict[str, Any]:
    """采集所有目标平台的数据"""
    crawler_cfg = config.get("crawler", {})
    platforms_cfg = config.get("platforms", {})
    
    results = {"data": [], "errors": {}}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=crawler_cfg.get("headless", True))
        context = await browser.new_context(
            user_agent=crawler_cfg.get("user_agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        )
        
        # 访问主页以初始化会话（如果有的话）
        try:
            page = await context.new_page()
            await page.goto("https://newsnow.busiyi.world/", wait_until="domcontentloaded", timeout=10000)
            await page.close()
        except:
            pass
            
        tasks = []
        for p_id in target_platforms:
            if p_id in platforms_cfg and platforms_cfg[p_id].get("enabled", True):
                tasks.append(fetch_platform_data(context, p_id, platforms_cfg[p_id], crawler_cfg))
        
        platform_results = await asyncio.gather(*tasks)
        for items in platform_results:
            results["data"].extend(items)
            
        await browser.close()
    return results

def filter_trends(trends: List[Dict[str, Any]], keywords: List[str], max_hours: int = 48) -> List[Dict[str, Any]]:
    """
    根据关键词和时效性筛选热点
    - max_hours: 最大小时数（默认 48 小时）
    """
    now = datetime.datetime.now()
    
    must_include = [kw[1:].lower() for kw in keywords if kw.startswith("+")]
    must_exclude = [kw[1:].lower() for kw in keywords if kw.startswith("!")]
    regular = [kw.lower() for kw in keywords if not kw.startswith("+") and not kw.startswith("!")]
    
    filtered = []
    for item in trends:
        # 1. 时效性检查
        pub_date_str = item.get("pubDate")
        if pub_date_str:
            try:
                # 尝试解析多种可能的日期格式
                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
                    try:
                        pub_date = datetime.datetime.strptime(pub_date_str, fmt)
                        break
                    except:
                        continue
                else:
                    # 如果无法解析，则跳过时效性检查（或视为通过，取决于策略，这里选择通过但标记）
                    pub_date = None
                
                if pub_date:
                    delta = now - pub_date
                    if delta.total_seconds() > max_hours * 3600:
                        continue # 超过 48 小时，跳过
            except:
                pass

        # 2. 关键词筛选
        title = item.get("title", item.get("text", item.get("name", ""))).lower()
        
        # 检查排除词
        if any(ex in title for ex in must_exclude):
            continue
            
        # 检查必须包含词
        if must_include and not all(inc in title for inc in must_include):
            continue
            
        # 检查普通词
        if regular:
            if any(reg in title for reg in regular):
                filtered.append(item)
        else:
            filtered.append(item)
            
    return filtered

def extract_topics(items: List[Dict[str, Any]], top_n=5) -> List[tuple]:
    """提取关键词频率，模拟热点话题聚合"""
    titles = [item.get("title", item.get("text", "")) for item in items]
    text = " ".join(titles)
    # 简单的分词逻辑（针对中文/英文混合）
    words = re.findall(r'[\u4e00-\u9fa5]{2,}|[a-zA-Z]{2,}', text)
    # 排除常见的无意义词（停用词）
    stop_words = {"这个", "什么", "如何", "为什么", "发布", "正式", "应用", "推出", "进行"}
    words = [w for w in words if w not in stop_words]
    return Counter(words).most_common(top_n)

def save_as_markdown(data: Dict[str, Any], custom_path: str = None):
    """将结果保存为更精美的 Markdown 报告"""
    if custom_path:
        filepath = os.path.abspath(custom_path)
        # 如果路径是目录，则在该目录下生成带时间戳的文件
        if os.path.isdir(filepath):
            now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(filepath, f"trend_report_{now}.md")
        # 确保父目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
    else:
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"trend_report_{now}.md"
        filepath = os.path.join(REPORTS_DIR, filename)
    
    # 提取核心话题
    topics = extract_topics(data["items"])
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# 🚀 TrendRadar 全网热点监控报告\n\n")
        
        f.write(f"## 📊 监控概览\n")
        f.write(f"| 项目 | 内容 |\n")
        f.write(f"| :--- | :--- |\n")
        f.write(f"| **生成时间** | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |\n")
        f.write(f"| **监控平台** | {', '.join(data['platforms'])} |\n")
        f.write(f"| **筛选关键词** | `{', '.join(data['keywords']) if data['keywords'] else '全网热搜'}` |\n")
        f.write(f"| **命中数量** | {data['count']} |\n\n")
        
        if topics:
            f.write(f"## 💡 核心话题词云 (模拟分析)\n")
            f.write("> 根据当前采集到的标题，为您提取出现频率最高的话题词：\n\n")
            topic_str = "  ".join([f"`{t[0]}({t[1]})`" for t in topics])
            f.write(f"{topic_str}\n\n")

        f.write(f"## 🔍 实时热点列表 (48h内)\n\n")
        f.write(f"| 排名 | 平台 | 标题 | 时间 | 热度 | 链接 |\n")
        f.write(f"| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        
        for i, item in enumerate(data["items"], 1):
            title = item.get("title", item.get("text", "无标题")).replace("|", "\\|")
            platform = item.get("platform", "未知")
            url = item.get("url", item.get("mobileUrl", "#"))
            pub_date = item.get("pubDate", "-")
            
            # 提取热度值
            hot = item.get("hot", item.get("heat", item.get("score", "-")))
            if isinstance(hot, (int, float)) and hot > 10000:
                hot = f"{hot/10000:.1f}万"
            
            f.write(f"| {i} | {platform} | {title} | {pub_date} | {hot} | [查看详情]({url}) |\n")
        
        f.write(f"\n----- \n")
        f.write(f"*💡 提示：本报告由 TrendRadar 自动生成。如需 AI 深度分析（包括趋势预测、情感洞察等），请直接在对话框中要求我进行分析。*\n")
            
    return filepath

async def main():
    parser = argparse.ArgumentParser(description="TrendRadar Robust Collector (Playwright Edition)")
    parser.add_argument("--keywords", type=str, help="Comma separated keywords to filter trends")
    parser.add_argument("--platforms", type=str, help="Comma separated platform IDs to fetch from")
    parser.add_argument("--output", type=str, help="Custom path to save the markdown report")
    parser.add_argument("--hours", type=int, default=48, help="Max hours since publication (default: 48)")
    
    args = parser.parse_args()
    
    config = load_config()
    
    # 确定要搜索的关键词：优先使用命令行参数，不强制依赖配置文件
    if args.keywords:
        target_keywords = [kw.strip() for kw in args.keywords.split(",")]
    else:
        # 如果没有传入关键词，尝试加载默认文件，但不再强制要求在 config.yaml 中配置
        target_keywords = load_default_keywords()
        
    # 确定要搜索的平台
    platforms_cfg = config.get("platforms", {})
    if args.platforms:
        target_platforms = [p.strip() for p in args.platforms.split(",")]
    else:
        target_platforms = [p for p, cfg in platforms_cfg.items() if cfg.get("enabled", True)]
    
    # 执行采集
    results = await collect_all(target_platforms, config)
    
    # 执行筛选
    filtered_data = filter_trends(results["data"], target_keywords, max_hours=args.hours)
    
    # 按照热度排序
    def get_hot(item):
        hot = item.get("hot", item.get("heat", item.get("score", 0)))
        if isinstance(hot, str):
            if "万" in hot:
                try: return float(hot.replace("万", "")) * 10000
                except: return 0
        try: return float(hot)
        except: return 0

    filtered_data.sort(key=get_hot, reverse=True)
    
    # 输出结果（JSON 格式供 AI 解析）
    max_items = config.get("report", {}).get("max_items_per_platform", 20)
    output = {
        "count": len(filtered_data),
        "platforms": target_platforms,
        "keywords": target_keywords,
        "items": filtered_data[:max_items * len(target_platforms)]
    }
    
    # 保存为 Markdown（支持自定义路径）
    report_path = save_as_markdown(output, custom_path=args.output)
    output["report_path"] = report_path
    
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
