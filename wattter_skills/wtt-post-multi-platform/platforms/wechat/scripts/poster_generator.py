#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import tempfile
import yaml
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright

# 全局临时文件追踪（如果是作为模块被导入，使用主程序的追踪）
temp_files = []
temp_dirs = []
try:
    from __main__ import temp_files as main_temp_files, temp_dirs as main_temp_dirs
    temp_files = main_temp_files
    temp_dirs = main_temp_dirs
except ImportError:
    # 如果是单独运行，自己注册清理
    import atexit

    def cleanup_temp_files():
        """程序退出时清理所有临时文件"""
        for file_path in temp_files:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except:
                pass

        for dir_path in temp_dirs:
            try:
                if os.path.exists(dir_path):
                    for file in os.listdir(dir_path):
                        file_path = os.path.join(dir_path, file)
                        try:
                            if os.path.isfile(file_path):
                                os.unlink(file_path)
                        except:
                            pass
                    os.rmdir(dir_path)
            except:
                pass

    atexit.register(cleanup_temp_files)

# 模板路径
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
POSTER_TEMPLATE_PATH = os.path.join(TEMPLATES_DIR, 'poster-templates.html')

def extract_poster_markers(markdown_content: str) -> List[Dict]:
    """
    从Markdown内容中提取所有海报标记
    标记格式：
    <!-- POSTER:type
    key: value
    -->
    """
    pattern = r'<!--\s*POSTER:(\w+)\s*(.*?)\s*-->'
    matches = re.findall(pattern, markdown_content, re.DOTALL)

    posters = []
    for poster_type, config_str in matches:
        try:
            config = yaml.safe_load(config_str) or {}
            posters.append({
                'type': poster_type,
                'config': config,
                'original': f'<!-- POSTER:{poster_type}\n{config_str}\n-->'
            })
        except Exception as e:
            print(f"警告：解析海报配置失败: {e}")
            continue

    return posters

def generate_poster_html(poster_config: Dict) -> str:
    """根据海报配置生成对应的HTML"""
    poster_type = poster_config['type']
    config = poster_config['config']

    # 读取基础模板
    with open(POSTER_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template_content = f.read()

    # 提取CSS样式部分
    css_match = re.search(r'<style>(.*?)</style>', template_content, re.DOTALL)
    if not css_match:
        raise ValueError("模板中未找到样式部分")
    css = css_match.group(1)

    if poster_type == 'cover':
        # 封面模板
        title = config.get('title', '标题')
        subtitle = config.get('subtitle', '副标题')
        accent_color = config.get('accent_color', '#1E40AF')
        top_left_text = config.get('top_left_text', '')
        top_right_text = config.get('top_right_text', '')
        bottom_left_text = config.get('bottom_left_text', '')
        bottom_right_text = config.get('bottom_right_text', '')
        background_image = config.get('background_image', '')

        # 处理标题中的标点作为强调
        # 如果标题包含逗号，把最后一个逗号作为强调
        if '，' in title:
            parts = title.rsplit('，', 1)
            title_html = f'{parts[0]}<span class="accent">，</span><br>{parts[1]}'
            if '。' in parts[1]:
                parts2 = parts[1].rsplit('。', 1)
                title_html = f'{parts[0]}<span class="accent">，</span><br>{parts2[0]}<span class="accent">。</span>'
        else:
            title_html = title

        # 处理顶部文字
        top_left_html = ''
        if top_left_text:
            lines = [line.strip() for line in top_left_text.strip().split('\n')]
            top_left_html = '<div class="cover-header-left">'
            for i, line in enumerate(lines):
                if i == 0:
                    top_left_html += f'<div class="top-line">{line}</div>'
                else:
                    top_left_html += f'<div class="bottom-line">{line}</div>'
            top_left_html += '</div>'

        top_right_html = ''
        if top_right_text:
            lines = [line.strip() for line in top_right_text.strip().split('\n')]
            top_right_html = '<div class="cover-header-right">'
            for i, line in enumerate(lines):
                if i == 0:
                    top_right_html += f'<div class="top-line">{line}</div>'
                else:
                    top_right_html += f'<div class="bottom-line">{line}</div>'
            top_right_html += '</div>'

        # 处理底部文字
        bottom_left_html = f'<div class="cover-footer-left">{bottom_left_text}</div>' if bottom_left_text else ''
        bottom_right_html = f'<div class="cover-footer-right">{bottom_right_text}</div>' if bottom_right_text else ''

        # 背景图片样式
        background_style = ''
        if background_image:
            background_style = f'background-image: url("{background_image}"); background-size: cover; background-position: center;'

        html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        {css}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Noto Sans SC', sans-serif;
            background: #f5f0e6;
            color: #0a1942;
            line-height: 1.6;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }}
        .accent {{ color: {accent_color} !important; }}
        .highlight {{ color: {accent_color} !important; }}
        .cover-poster {{
            {background_style}
            width: 1200px;
            height: 900px;
            position: relative;
            padding: 80px;
            display: flex;
            flex-direction: column;
            justify-content: center; /* 内容垂直居中 */
        }}
        .cover-header {{
            position: absolute;
            top: 80px;
            left: 80px;
            right: 80px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            font-size: 14px;
            letter-spacing: 2px;
            text-transform: uppercase;
            opacity: 0.8;
        }}
        .cover-header-left .top-line {{
            color: {accent_color};
            font-weight: 700;
            margin-bottom: 4px;
        }}
        .cover-header-left .bottom-line {{
            font-size: 12px;
            opacity: 0.7;
        }}
        .cover-header-right {{
            text-align: right;
        }}
        .cover-header-right .top-line {{
            margin-bottom: 4px;
        }}
        .cover-header-right .bottom-line {{
            font-size: 12px;
            opacity: 0.7;
        }}
        .cover-content-wrapper {{
            text-align: left;
            margin: auto 0; /* 上下自动居中 */
        }}
        .cover-title {{
            font-size: 140px;
            font-weight: 900;
            line-height: 1.1;
            margin-bottom: 60px;
            letter-spacing: -2px;
        }}
        .cover-subtitle {{
            font-size: 36px;
            font-weight: 400;
            margin-bottom: 20px;
        }}
        .cover-footer {{
            position: absolute;
            bottom: 80px;
            left: 80px;
            right: 80px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            opacity: 0.6;
        }}
    </style>
</head>
<body>
    <div class="poster cover-poster">
        <div class="cover-header">
            {top_left_html}
            {top_right_html}
        </div>
        <div class="cover-content-wrapper">
            <div class="cover-title">{title_html}</div>
            <div class="cover-subtitle">{subtitle.replace('\\n', '<br>')}</div>
        </div>
        <div class="cover-footer">
            {bottom_left_html}
            {bottom_right_html}
        </div>
    </div>
</body>
</html>
        '''

    elif poster_type == 'quote':
        # 金句海报模板
        text = config.get('text', '')
        author = config.get('author', '')
        accent_color = config.get('accent_color', '#1E40AF')

        html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;700;900&display=swap');
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Noto Sans SC', sans-serif;
            background: #f5f0e6;
            color: #0a1942;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }}
        .quote-poster {{
            width: 1200px;
            height: 900px;
            padding: 100px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            position: relative;
        }}
        .quote-text {{
            font-size: 72px;
            font-weight: 700;
            line-height: 1.4;
            margin-bottom: 80px;
            color: #0a1942;
        }}
        .quote-author {{
            font-size: 32px;
            color: {accent_color};
            font-weight: 500;
            align-self: flex-end;
            margin-right: 40px;
        }}
        .quote-mark {{
            position: absolute;
            font-size: 200px;
            color: rgba(200, 46, 46, 0.1);
            font-weight: 900;
        }}
        .quote-mark.left {{
            top: 80px;
            left: 80px;
        }}
        .quote-mark.right {{
            bottom: 80px;
            right: 80px;
        }}
    </style>
</head>
<body>
    <div class="quote-poster">
        <div class="quote-mark left">“</div>
        <div class="quote-text">{text.replace('\\n', '<br>')}</div>
        <div class="quote-author">—— {author}</div>
        <div class="quote-mark right">”</div>
    </div>
</body>
</html>
        '''
    elif poster_type == 'center':
        # 居中标题海报模板
        title = config.get('title', '')
        subtitle = config.get('subtitle', '')
        accent_color = config.get('accent_color', '#1E40AF')

        html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;700;900&display=swap');
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Noto Sans SC', sans-serif;
            background: #f5f0e6;
            color: #0a1942;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }}
        .center-poster {{
            width: 1200px;
            height: 900px;
            padding: 100px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }}
        .center-title {{
            font-size: 96px;
            font-weight: 900;
            color: #0a1942;
            margin-bottom: 40px;
        }}
        .center-subtitle {{
            font-size: 36px;
            color: {accent_color};
            font-weight: 400;
            opacity: 0.8;
        }}
        .center-divider {{
            width: 120px;
            height: 4px;
            background: {accent_color};
            margin: 20px 0;
            border-radius: 2px;
        }}
    </style>
</head>
<body>
    <div class="center-poster">
        <div class="center-title">{title}</div>
        <div class="center-divider"></div>
        <div class="center-subtitle">{subtitle}</div>
    </div>
</body>
</html>
        '''
    elif poster_type == 'compare':
        # 对比模板
        title = config.get('title', '对比')
        left_title = config.get('left_title', '输入')
        left_items = config.get('left_items', [])
        right_title = config.get('right_title', '输出')
        right_items = config.get('right_items', [])
        accent_color = config.get('accent_color', '#1E40AF')

        left_items_html = ''
        for i, item in enumerate(left_items, 1):
            left_items_html += f'<li class="card-item"><span class="number">{i:02d}</span> {item}</li>'

        right_items_html = ''
        for i, item in enumerate(right_items, 1):
            # 提取数字作为高亮
            if isinstance(item, str) and item and item[0].isdigit():
                parts = item.split(' ', 1)
                if len(parts) == 2:
                    num, text = parts
                    right_items_html += f'<li class="card-item"><span class="number accent">{num}</span> {text}</li>'
                else:
                    right_items_html += f'<li class="card-item">{item}</li>'
            else:
                right_items_html += f'<li class="card-item">{item}</li>'

        html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;700;900&display=swap');
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Noto Sans SC', sans-serif;
            background: #f5f0e6;
            color: #0a1942;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }}
        .poster {{
            width: 1200px;
            height: 900px;
            padding: 80px;
            position: relative;
        }}
        .compare-title {{
            font-size: 48px;
            font-weight: 900;
            text-align: center;
            margin-bottom: 60px;
            color: #0a1942;
        }}
        .compare-grid {{
            display: flex;
            gap: 40px;
            height: calc(100% - 140px);
        }}
        .card {{
            flex: 1;
            background: #fff;
            border-radius: 16px;
            padding: 40px;
            display: flex;
            flex-direction: column;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }}
        .card-label {{
            font-size: 14px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 2px solid {accent_color};
            color: {accent_color};
        }}
        .card-left .card-label {{ border-bottom-color: #666; color: #666; }}
        .card-list {{
            list-style: none;
            padding: 0;
            margin: 0;
            flex: 1;
        }}
        .card-item {{
            font-size: 24px;
            padding: 16px 0;
            border-bottom: 1px solid #eee;
            display: flex;
            align-items: flex-start;
            gap: 16px;
            line-height: 1.4;
        }}
        .card-item:last-child {{ border-bottom: none; }}
        .number {{
            font-weight: 900;
            font-size: 28px;
            color: #666;
            min-width: 48px;
        }}
        .accent {{ color: {accent_color} !important; }}
    </style>
</head>
<body>
    <div class="poster compare-poster">
        <div class="compare-title">{title.replace('\\n', '<br>')}</div>
        <div class="compare-grid">
            <div class="card card-left">
                <div class="card-label">{left_title}</div>
                <ul class="card-list">{left_items_html}</ul>
            </div>
            <div class="card card-right">
                <div class="card-label">{right_title}</div>
                <ul class="card-list">{right_items_html}</ul>
            </div>
        </div>
    </div>
</body>
</html>
        '''

    elif poster_type == 'timeline':
        # 时间线模板
        title = config.get('title', '时间线')
        items = config.get('items', [])
        accent_color = config.get('accent_color', '#1E40AF')

        # 最多支持4个时间点
        items = items[:4]
        timeline_points_html = ''
        timeline_content_html = ''

        for i, item in enumerate(items):
            is_future = i >= len(items) - 1  # 最后一个点作为未来节点
            point_class = 'timeline-point future' if is_future else 'timeline-point'
            timeline_points_html += f'<div class="{point_class}"></div>'

            date = item.get('date', '')
            event = item.get('event', '')
            desc = item.get('desc', '')

            timeline_content_html += f'''
<div class="timeline-item">
    <div class="timeline-date">{date}</div>
    <div class="timeline-event">{event}</div>
    <div class="timeline-desc">{desc}</div>
</div>
            '''

        html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;700;900&display=swap');
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Noto Sans SC', sans-serif;
            background: #f5f0e6;
            color: #0a1942;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }}
        .poster {{
            width: 1200px;
            height: 900px;
            padding: 80px;
            position: relative;
        }}
        .timeline-header {{
            text-align: center;
            margin-bottom: 60px;
        }}
        .timeline-title {{
            font-size: 48px;
            font-weight: 900;
            color: #0a1942;
        }}
        .timeline {{
            display: flex;
            justify-content: space-between;
            position: relative;
            padding: 0 20px;
            margin-bottom: 40px;
        }}
        .timeline::before {{
            content: '';
            position: absolute;
            top: 20px;
            left: 40px;
            right: 40px;
            height: 4px;
            background: linear-gradient(to right, #ccc, {accent_color}, #ccc);
            border-radius: 2px;
        }}
        .timeline-point {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: {accent_color};
            position: relative;
            z-index: 1;
            box-shadow: 0 0 0 6px #f5f0e6;
        }}
        .timeline-point.future {{
            background: #ccc;
            border: 3px dashed {accent_color};
        }}
        .timeline-content {{
            display: flex;
            gap: 20px;
        }}
        .timeline-item {{
            flex: 1;
            padding: 24px;
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        }}
        .timeline-date {{
            font-size: 18px;
            font-weight: 700;
            color: {accent_color};
            margin-bottom: 12px;
        }}
        .timeline-event {{
            font-size: 20px;
            font-weight: 600;
            color: #0a1942;
            margin-bottom: 8px;
            line-height: 1.3;
        }}
        .timeline-desc {{
            font-size: 16px;
            color: #666;
            line-height: 1.4;
        }}
    </style>
</head>
<body>
    <div class="poster timeline-poster">
        <div class="timeline-header">
            <div class="timeline-title">{title}</div>
        </div>
        <div class="timeline">
            {timeline_points_html}
        </div>
        <div class="timeline-content">
            {timeline_content_html}
        </div>
    </div>
</body>
</html>
        '''

    else:
        raise ValueError(f"不支持的海报类型: {poster_type}")

    return html

def html_to_image(html_content: str, output_path: Optional[str] = None, width: int = 1200, height: int = 900) -> str:
    """
    将HTML内容转换为PNG图片
    返回生成的图片路径
    """
    temp_file_created = False
    if output_path is None:
        # 创建临时文件
        fd, output_path = tempfile.mkstemp(suffix='.png')
        os.close(fd)
        temp_file_created = True

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': width, 'height': height})
            page.set_content(html_content)
            # 等待字体加载完成
            page.wait_for_timeout(500)
            page.screenshot(path=output_path, full_page=False)
            browser.close()
    except Exception as e:
        # 如果生成失败，删除临时文件
        if temp_file_created and os.path.exists(output_path):
            try:
                os.unlink(output_path)
            except:
                pass
        raise e

    return output_path

def generate_poster(poster_config: Dict, output_dir: Optional[str] = None) -> str:
    """
    生成海报图片
    返回图片路径
    """
    html = generate_poster_html(poster_config)

    output_path = None
    temp_file_created = False
    if output_dir:
        # 只有指定输出目录时才保存到本地
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'poster_{poster_config["type"]}_{os.urandom(4).hex()}.png')
    else:
        # 创建临时文件
        fd, output_path = tempfile.mkstemp(suffix='.png')
        os.close(fd)
        temp_file_created = True
        # 追踪临时文件
        temp_files.append(output_path)

    try:
        image_path = html_to_image(html, output_path)
    except Exception as e:
        # 生成失败，清理临时文件
        if temp_file_created and os.path.exists(output_path):
            try:
                os.unlink(output_path)
                if output_path in temp_files:
                    temp_files.remove(output_path)
            except:
                pass
        raise e

    return image_path
