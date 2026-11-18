#!/usr/bin/env python3
"""
微信公众号草稿箱 API 发布脚本

使用方式:
    python wechat_draft_poster.py -m /path/to/article.md
    python wechat_draft_poster.py -m /path/to/article.md --title "自定义标题"
"""

import argparse
import json
import sys
import os
import atexit

import requests

# 注册退出时的清理函数
temp_files = []
temp_dirs = []

def cleanup_temp_files():
    """程序退出时清理所有临时文件"""
    # 清理临时文件
    for file_path in temp_files:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except:
            pass

    # 清理临时目录
    for dir_path in temp_dirs:
        try:
            if os.path.exists(dir_path):
                # 先删除目录下的文件
                for file in os.listdir(dir_path):
                    file_path = os.path.join(dir_path, file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except:
                        pass
                # 删除空目录
                os.rmdir(dir_path)
        except:
            pass

# 注册退出钩子
atexit.register(cleanup_temp_files)

# 导入同目录下的模块
from config import get_access_token, get_config, get_thumb_media_id
from markdown_converter import (
    markdown_to_wechat_html,
    extract_title_and_digest,
    read_markdown_file,
    process_poster_markers,
    auto_insert_poster_markers,
)

# API 地址
DRAFT_ADD_API = "https://api.weixin.qq.com/cgi-bin/draft/add"


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="发布 Markdown 到微信公众号草稿箱")
    parser.add_argument("-m", "--markdown", required=True, help="Markdown 文件路径")
    parser.add_argument("-t", "--title", help="自定义标题 (默认从文件提取)")
    parser.add_argument("-a", "--author", help="作者名称")
    parser.add_argument("--digest", help="摘要 (默认自动提取)")
    parser.add_argument(
        "--thumb-media-id", help="封面图片 media_id (必须是永久素材)"
    )
    parser.add_argument(
        "--enable-posters", action="store_true", help="启用海报自动生成功能"
    )
    parser.add_argument(
        "--permanent-posters", action="store_true", help="将海报上传为永久素材（默认临时素材，3天有效）"
    )
    parser.add_argument(
        "--poster-output-dir", help="海报图片保存目录（可选，默认使用临时目录）"
    )
    return parser.parse_args()


def add_to_draft(articles, access_token):
    """调用草稿箱 API"""
    payload = {"articles": articles}
    url = f"{DRAFT_ADD_API}?access_token={access_token}"
    # 使用 data + json.dumps 编码方式，与 curl 行为一致
    response = requests.post(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    return response.json()


def main():
    args = parse_args()

    # 检查配置
    config = get_config()
    if config.get("appid") == "YOUR_APPID_HERE" or not config.get("appid"):
        print("❌ 错误: 请先编辑 config/config.json 中的 wechat 配置填入 appid 和 appsecret")
        sys.exit(1)

    # 自动获取 access_token (每次自动刷新)
    access_token = get_access_token()
    if not access_token:
        print("❌ 错误: 无法获取 access_token，请检查 appid 和 appsecret")
        sys.exit(1)

    # 读取 Markdown 文件
    try:
        markdown_content = read_markdown_file(args.markdown)
    except FileNotFoundError as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

    # 处理海报标记（如果启用）
    poster_media_ids = []
    if args.enable_posters:
        print("🎨 启用海报自动生成功能...")

        # 智能分析内容并自动插入海报标记（仅当没有显式声明时）
        if '<!-- POSTER:' not in markdown_content:
            print("📝 分析文章结构，自动插入海报标记...")
            markdown_content = auto_insert_poster_markers(markdown_content)
        else:
            print("📝 检测到用户已声明海报标记，跳过自动插入")

        try:
            # 处理海报并获取所有生成的海报media_id
            markdown_content, poster_media_ids = process_poster_markers(
                markdown_content,
                access_token,
                output_dir=args.poster_output_dir,
                permanent=args.permanent_posters
            )
        except Exception as e:
            print(f"⚠️  海报处理失败，继续发布: {str(e)}")

    # 提取标题和摘要（在海报处理之后，确保标题不包含海报标记）
    title, auto_digest = extract_title_and_digest(markdown_content)
    title = args.title if args.title else title
    digest = args.digest if args.digest else auto_digest

    if not title:
        print("❌ 错误: 无法提取标题，请使用 --title 指定")
        sys.exit(1)

    # 转换为 HTML
    content_html = markdown_to_wechat_html(markdown_content)

    # 构建文章结构
    article = {
        "article_type": "news",
        "title": title,
        "digest": digest,
        "content": content_html,
        "need_open_comment": 0,
        "only_fans_can_comment": 0,
    }

    if args.author:
        article["author"] = args.author

    # 封面图优先级：命令行参数 > 生成的第一张封面海报 > 配置文件默认值
    thumb_media_id = args.thumb_media_id
    if not thumb_media_id and poster_media_ids:
        # 优先使用第一张cover类型的海报作为封面
        for media_id, poster_type in poster_media_ids:
            if poster_type == 'cover':
                thumb_media_id = media_id
                print(f"📸 自动使用封面海报作为文章封面，media_id: {thumb_media_id}")
                break
        # 如果没有cover类型，使用第一张海报
        if not thumb_media_id:
            thumb_media_id = poster_media_ids[0][0]
            print(f"📸 自动使用第一张海报作为文章封面，media_id: {thumb_media_id}")
    # 否则使用配置文件中的默认值
    if not thumb_media_id:
        thumb_media_id = get_thumb_media_id()

    if thumb_media_id:
        article["thumb_media_id"] = thumb_media_id

    # 调用 API
    print(f"📤 正在发布到草稿箱...")
    print(f"   标题: {title}")

    result = add_to_draft([article], access_token)

    if "media_id" in result:
        print(f"✅ 发布成功!")
        print(f"   media_id: {result['media_id']}")
    else:
        print(f"❌ 发布失败: {result}")
        sys.exit(1)


if __name__ == "__main__":
    main()
