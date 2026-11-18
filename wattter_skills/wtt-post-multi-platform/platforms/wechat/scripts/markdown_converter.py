"""
Markdown 转微信公众号 HTML 格式转换器
生成带内联样式的 HTML，适用于微信草稿箱 API
"""
import re
import os
from pathlib import Path

try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

import datetime
# 海报功能可选依赖
try:
    # 尝试相对导入（模块方式运行）
    from .poster_generator import extract_poster_markers, generate_poster
    from .media_uploader import upload_poster_image
    POSTER_FEATURE_AVAILABLE = True
except ImportError:
    try:
        # 尝试直接导入（脚本方式运行）
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from poster_generator import extract_poster_markers, generate_poster
        from media_uploader import upload_poster_image
        POSTER_FEATURE_AVAILABLE = True
    except ImportError as e:
        POSTER_FEATURE_AVAILABLE = False
        POSTER_IMPORT_ERROR = str(e)


# ==================== 样式常量 ====================
# 参考微信平台的文章样式
STYLES = {
    'primary': '#1E40AF',        # WeChat blue from auto-poster
    'primary_dark': '#0A3C6D',
    'secondary': '#EA4335',
    'accent': '#34A853',
    'warning': '#FBBC04',
    'font_family': '-apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif',
    'font_family_mono': 'Menlo, Monaco, Consolas, "Courier New", monospace',
    'text': '#333333',
    'text_secondary': '#666666',
    'text_light': '#999999',
    'bg': '#FFFFFF',
    'bg_secondary': '#F8F9FA',
    'border': '#E8E8E8',
    'code_bg': '#F6F8FA',
    'code_color': '#c7254e',     # Red for inline code
    'quote_bg': '#f7f7f7',        # Light gray background
    'quote_border': '#1E40AF',    # Primary color
    'hr_color': '#E8E8E8',
}


def apply_inline_styles_with_bs4(html_content):
    """
    使用 BeautifulSoup 正确处理 HTML 内联样式
    参考微信平台的文章样式
    """
    if not BS4_AVAILABLE:
        return html_content  # 回退到原始 HTML

    soup = BeautifulSoup(html_content, 'html.parser')

    # 处理标题 - 参考 auto-poster 样式
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4']):
        if tag.name == 'h1':
            tag['style'] = 'display:table;padding:0 1em;border-bottom:2px solid #1E40AF;margin:2em auto 1em;color:#333;font-size:1.2em;font-weight:bold;text-align:center;'
        elif tag.name == 'h2':
            tag['style'] = 'display:table;padding:0 0.2em;margin:1.5em auto;color:#fff;background:#1E40AF;font-size:1.1em;font-weight:bold;text-align:center;border-radius:4px;'
        elif tag.name == 'h3':
            tag['style'] = 'padding-left:8px;border-left:3px solid #1E40AF;margin:2em 8px 0.75em 0;color:#333;font-size:1.05em;font-weight:bold;line-height:1.2;'
        elif tag.name == 'h4':
            tag['style'] = 'margin:2em 8px 0.5em;color:#1E40AF;font-size:1em;font-weight:bold;'

    # 处理段落 - 参考 auto-poster 的 letter-spacing 和 text-align
    for tag in soup.find_all('p'):
        # 跳过已经在 blockquote 内的 p
        if tag.parent and tag.parent.name == 'blockquote':
            continue
        tag['style'] = 'margin:1.5em 8px;letter-spacing:0.05em;color:#333;line-height:1.8;text-align:justify;'

    # 处理链接
    for tag in soup.find_all('a'):
        tag['style'] = 'color:#1E40AF;text-decoration:none;'

    # 处理强调
    for tag in soup.find_all(['strong', 'b']):
        tag['style'] = 'font-weight:bold;'

    for tag in soup.find_all(['em', 'i']):
        tag['style'] = 'font-style:italic;'

    # 处理行内代码 - 参考 auto-poster
    for tag in soup.find_all('code'):
        # 跳过代码块中的 code（带有 language- class）
        if tag.get('class') and any('language-' in c for c in tag.get('class', [])):
            continue
        tag['style'] = 'font-family:Menlo,Monaco,Consolas,"Courier New",monospace;font-size:0.9em;color:#c7254e;background:#f9f2f4;padding:2px 4px;border-radius:4px;'

    # 处理引用块 - 参考 auto-poster
    for tag in soup.find_all('blockquote'):
        tag['style'] = 'font-style:normal;padding:1em;border-left:4px solid #1E40AF;border-radius:6px;color:#333;background:#f7f7f7;margin:1em 8px;'
        # 移除内部的 p 标签样式（保留文本）
        for p in tag.find_all('p'):
            p['style'] = 'margin:0;'
            p.unwrap()

    # 处理列表 - 参考 auto-poster
    for tag in soup.find_all('ul'):
        tag['style'] = 'margin:1.5em 8px;padding-left:2em;'
    for tag in soup.find_all('ol'):
        tag['style'] = 'margin:1.5em 8px;padding-left:2em;'
    for tag in soup.find_all('li'):
        tag['style'] = 'margin-bottom:0.5em;letter-spacing:0.05em;'

    # 处理图片 - 参考 auto-poster
    for tag in soup.find_all('img'):
        tag['style'] = 'display:block;margin:1.5em auto;max-width:100%;border-radius:6px;box-shadow:0 2px 10px rgba(0,0,0,0.1);'

    # 处理分割线
    for tag in soup.find_all('hr'):
        tag['style'] = 'border:none;border-top:1px solid #E8E8E8;margin:2em 0;'

    # 处理表格 - 参考 auto-poster
    for tag in soup.find_all('table'):
        tag['style'] = 'display:block;width:100%;overflow:auto;margin-bottom:1.5em;border-spacing:0;border-collapse:collapse;'
    for tag in soup.find_all('tr'):
        tag['style'] = 'background-color:#fff;border-top:1px solid #c6cbd1;'
    for tag in soup.find_all('tr:nth-child(2n)'):
        tag['style'] = 'background-color:#f6f8fa;'
    for tag in soup.find_all(['th', 'td']):
        tag['style'] = 'padding:6px 13px;border:1px solid #dfe2e5;'
    for tag in soup.find_all('th'):
        tag['style'] = 'font-weight:600;padding:6px 13px;border:1px solid #dfe2e5;'

    # 处理代码块 - Mac 风格深色主题
    for pre in soup.find_all('pre'):
        code = pre.find('code')
        if code:
            mac_svg = '''<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="45" height="13" viewBox="0 0 450 130">
<ellipse cx="50" cy="65" rx="50" ry="52" stroke="rgb(220,60,54)" stroke-width="2" fill="rgb(237,108,96)" />
<ellipse cx="225" cy="65" rx="50" ry="52" stroke="rgb(218,151,33)" stroke-width="2" fill="rgb(247,193,81)" />
<ellipse cx="400" cy="65" rx="50" ry="52" stroke="rgb(27,161,37)" stroke-width="2" fill="rgb(100,200,86)" />
</svg>'''
            # 深色代码块样式
            pre['style'] = 'display:block;padding:1em;margin:1.5em 8px;font-size:0.9em;line-height:1.4;word-break:break-all;word-wrap:break-word;color:#abb2bf;background-color:#282c34;border-radius:6px;overflow-x:auto;'
            # 在 code 前添加 Mac SVG 标签
            mac_span = soup.new_tag('span', attrs={
                'class': 'mac-sign',
                'style': 'display:block;padding:10px 14px 0;'
            })
            mac_span.append(BeautifulSoup(mac_svg, 'html.parser'))
            code.insert_before(mac_span)
            # 设置 code 样式
            code['style'] = 'font-family:Menlo,Monaco,Consolas,monospace;font-size:inherit;color:inherit;white-space:pre-wrap;background-color:transparent;border-radius:0;padding:0;'

    return str(soup)


def markdown_to_wechat_html(markdown_content):
    """
    将 Markdown 内容转换为微信公众号支持的 HTML 格式
    生成带内联样式的 HTML
    """
    if MARKDOWN_AVAILABLE:
        html_content = markdown.markdown(
            markdown_content,
            extensions=['fenced_code', 'tables', 'nl2br', 'extra']
        )
    else:
        html_content = _manual_convert(markdown_content)

    # 使用 BeautifulSoup 应用内联样式
    if BS4_AVAILABLE:
        html_content = apply_inline_styles_with_bs4(html_content)

    return html_content


def _manual_convert(markdown_content):
    """
    手动 Markdown 转换（当 markdown 库不可用时使用）
    """
    lines = markdown_content.split("\n")
    html_parts = []
    in_code_block = False
    code_buffer = []
    code_language = ""

    for line in lines:
        if line.strip().startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_language = line.strip()[3:]
                code_buffer = []
            else:
                in_code_block = False
                code_html = _format_code_block("\n".join(code_buffer), code_language)
                html_parts.append(code_html)
            continue

        if in_code_block:
            code_buffer.append(line)
            continue

        processed = _process_line(line)
        if processed:
            html_parts.append(processed)

    return "\n".join(html_parts)


def _process_line(line):
    """处理单行内容"""
    line = line.strip()

    if not line:
        return ""

    heading = re.match(r"^(#{1,6})\s+(.+)$", line)
    if heading:
        level = len(heading.group(1))
        text = heading.group(2)
        return f"<h{level}>{_process_inline(text)}</h{level}>"

    if re.match(r"^(-{3,}|\*{3,}|_{3,})$", line):
        return "<hr/>"

    if line.startswith(">"):
        quote_content = re.sub(r"^>\s?", "", line)
        return f"<blockquote><p>{_process_inline(quote_content)}</p></blockquote>"

    list_match = re.match(r"^[-*+]\s+(.+)$", line)
    if list_match:
        item_text = list_match.group(1)
        return f"<li>{_process_inline(item_text)}</li>"

    numbered_match = re.match(r"^\d+\.\s+(.+)$", line)
    if numbered_match:
        item_text = numbered_match.group(1)
        return f"<li>{_process_inline(item_text)}</li>"

    img_match = re.search(r"!\[([^\]]*)\]\(([^\)]+)\)", line)
    if img_match:
        alt_text = img_match.group(1)
        src = img_match.group(2)
        return f'<img src="{src}" alt="{alt_text}" />'

    if line:
        return f"<p>{_process_inline(line)}</p>"

    return ""


def _process_inline(text):
    """处理行内元素"""
    text = re.sub(r"\[([^\]]+)\]\(([^\)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^\*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^\*]+)\*", r"<em>\1</em>", text)
    text = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", text)
    text = re.sub(r"_([^_]+)_", r"<em>\1</em>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def _format_code_block(code, language):
    """格式化代码块"""
    import html
    escaped_code = html.escape(code)
    escaped_code = escaped_code.replace("\n", "<br/>")
    escaped_code = escaped_code.strip()
    return f'<pre><code>{escaped_code}</code></pre>'


def _parse_yaml_frontmatter_title(markdown_content: str) -> str | None:
    """
    从 YAML frontmatter 中提取 title 字段。
    返回 None 表示没有 frontmatter 或其中没有 title。
    """
    lines = markdown_content.split("\n")
    if not lines or lines[0].strip() != "---":
        return None

    # 找到闭合的 ---
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return None

    # 在 frontmatter 区域内查找 title:
    for i in range(1, end_idx):
        line = lines[i].strip()
        # 匹配 title: value 或 title: "value" 或 title: 'value'
        m = re.match(r'^title:\s*["\']?(.+?)["\']?\s*$', line)
        if m:
            return m.group(1).strip()

    return None


def extract_title_and_digest(markdown_content):
    """
    从 Markdown 中提取标题和摘要。
    优先从 YAML frontmatter 中读取 title，其次使用 #  一级 Markdown 标题。
    """
    lines = markdown_content.split("\n")
    title = ""

    # 优先从 YAML frontmatter 提取标题
    title = _parse_yaml_frontmatter_title(markdown_content) or ""

    # fallback: #  一级 Markdown 标题
    if not title:
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith("# "):
                title = line[2:].strip()
                break

    content_lines = []
    in_code_block = False
    for line in lines:
        line = line.strip()
        if line.startswith("#"):
            continue
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if re.match(r"^[-*+]\s+", line) or re.match(r"^\d+\.\s+", line):
            continue
        if re.match(r"^[-*_]{3,}$", line):
            continue
        if line.startswith("!") or line.startswith("["):
            continue
        if line:
            content_lines.append(line)
            break

    digest_text = "\n".join(content_lines)
    if len(digest_text) > 64:
        digest = digest_text[:64] + "..."
    else:
        digest = digest_text

    return title, digest


def read_markdown_file(file_path):
    """读取 Markdown 文件"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def process_poster_markers(markdown_content: str, access_token: str, output_dir: str = None, permanent: bool = False) -> tuple[str, list]:
    """
    处理Markdown中的海报标记，生成图片并上传到微信素材库，替换为<img>标签

    Args:
        markdown_content: 原始Markdown内容
        access_token: 微信API access_token
        output_dir: 海报图片保存目录（可选，默认使用临时目录）
        permanent: 是否上传为永久素材

    Returns:
        tuple: (处理后的Markdown内容, 生成的海报media_id列表 [(media_id, poster_type), ...])
    """
    if not POSTER_FEATURE_AVAILABLE:
        print(f"警告：海报功能不可用，跳过海报处理: {POSTER_IMPORT_ERROR}")
        return markdown_content, []

    posters = extract_poster_markers(markdown_content)
    if not posters:
        return markdown_content, []

    # 创建输出目录
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        import tempfile
        output_dir = tempfile.mkdtemp()

    processed_content = markdown_content
    poster_media_ids = []

    # 获取当前日期，格式：YYYY · MM · DD
    current_date = datetime.datetime.now().strftime("%Y · %m · %d")

    for poster in posters:
        try:
            print(f"正在生成{poster['type']}类型海报...")

            # 自动注入当前日期到右上角，如果用户没有自定义的话
            if poster['type'] == 'cover' and 'top_right_text' not in poster['config']:
                # 默认右上角：第一行日期，第二行标识
                poster['config']['top_right_text'] = f"{current_date}\nPOSTER · 原创"

            # 生成海报图片
            image_path = generate_poster(poster, output_dir)
            print(f"海报已生成: {image_path}")

            # 上传到微信素材库
            print("正在上传到微信素材库...")
            upload_result = upload_poster_image(image_path, access_token, permanent)
            media_id = upload_result['media_id']
            print(f"上传成功，media_id: {media_id}")

            # 记录media_id和海报类型
            poster_media_ids.append((media_id, poster['type']))

            # 替换标记为图片标签，保留原始标记，不修改用户其他内容
            # 微信公众号文章中的图片使用<img>标签，不需要特殊样式，后续转换会自动添加
            img_tag = f'{poster["original"]}\n\n<img src="{upload_result["url"]}" alt="海报" style="display: block; margin: 2em auto; max-width: 100%; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);" />\n\n'
            processed_content = processed_content.replace(poster['original'], img_tag)

            # 清理临时文件（默认不保存本地）
            if not output_dir:
                try:
                    if os.path.exists(image_path):
                        os.unlink(image_path)
                except Exception as e:
                    print(f"⚠️  清理临时图片失败: {str(e)}")

        except Exception as e:
            print(f"警告：处理海报失败，跳过该海报: {str(e)}")
            continue

    # 清理临时目录（如果使用的是临时目录）
    if not output_dir and os.path.exists(output_dir):
        try:
            # 先删除目录下可能残留的文件
            for file in os.listdir(output_dir):
                file_path = os.path.join(output_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except:
                    pass
            # 再删除空目录
            os.rmdir(output_dir)
        except Exception as e:
            print(f"⚠️  清理临时目录失败: {str(e)}")

    return processed_content, poster_media_ids


# ==================== 自动插入海报标记 ====================

def analyze_content_structure(markdown_content: str) -> dict:
    """
    分析 Markdown 内容结构，返回结构化信息用于智能插入海报

    Returns:
        dict: {
            'title': str,           # 文章标题
            'subtitle': str,        # 副标题/引言
            'sections': [           # 各章节
                {
                    'level': int,      # 标题级别 (1, 2, 3)
                    'title': str,      # 标题文本
                    'start_line': int,
                    'content': str,    # 章节原始内容
                    'quotes': [...],   # 发现的引用块
                    'lists': [...],    # 发现的列表
                    'dividers': [...], # 发现的分割线位置
                }
            ],
            'total_length': int,   # 总字符数
        }
    """
    lines = markdown_content.split('\n')

    # 优先从 YAML frontmatter 提取标题
    title = _parse_yaml_frontmatter_title(markdown_content) or ""
    subtitle = ""
    sections = []

    current_section = None
    current_content_lines = []
    in_code_block = False

    for i, line in enumerate(lines):
        # 跟踪代码块状态
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            current_content_lines.append(line)
            continue

        if in_code_block:
            current_content_lines.append(line)
            continue

        # 检测标题
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()

            # 保存当前章节
            if current_section:
                current_section['content'] = '\n'.join(current_content_lines)
                current_section['end_line'] = i - 1
                sections.append(current_section)

            # 开始新章节
            current_section = {
                'level': level,
                'title': heading_text,
                'start_line': i,
                'content': '',
                'quotes': [],
                'lists': [],
                'dividers': [],
            }
            current_content_lines = [line]

            # 提取文章标题
            if level == 1 and not title:
                title = heading_text.strip('*_')
            continue

        # 检测分割线
        if re.match(r'^[*\-_]{3,}$', line.strip()):
            if current_section:
                current_section['dividers'].append(i)
            current_content_lines.append(line)
            continue

        # 检测引用块
        if line.strip().startswith('>'):
            if current_section:
                quote_text = re.sub(r'^>\s?', '', line.strip())
                if len(quote_text) > 15:  # 超过15字才记录
                    current_section['quotes'].append({
                        'line': i,
                        'text': quote_text,
                    })
            current_content_lines.append(line)
            continue

        # 检测列表
        list_match = re.match(r'^[-*+]\s+(.+)$', line.strip())
        if list_match:
            if current_section:
                current_section['lists'].append({
                    'line': i,
                    'text': list_match.group(1),
                })
            current_content_lines.append(line)
            continue

        # 普通内容行
        current_content_lines.append(line)

    # 保存最后一个章节
    if current_section:
        current_section['content'] = '\n'.join(current_content_lines)
        current_section['end_line'] = len(lines) - 1
        sections.append(current_section)

    # 提取副标题：从第一个非标题段落中获取
    for section in sections:
        if section['level'] == 1:
            continue
        content = section['content']
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('```') and len(line) > 10:
                subtitle = line.strip('*_')[:60]
                break
        break

    return {
        'title': title,
        'subtitle': subtitle,
        'sections': sections,
        'total_length': len(markdown_content),
    }


def auto_insert_poster_markers(markdown_content: str, max_posters: int = 5) -> str:
    """
    分析 Markdown 内容，智能插入海报标记

    Args:
        markdown_content: 原始 Markdown 内容
        max_posters: 最大海报数量（默认5张，避免文章过于图片化）

    Returns:
        str: 插入海报标记后的 Markdown 内容
    """
    # 如果已有显式海报标记，不自动插入
    if '<!-- POSTER:' in markdown_content:
        return markdown_content

    # 分析内容结构
    structure = analyze_content_structure(markdown_content)

    if not structure['title']:
        print("⚠️  无法提取文章标题，跳过自动海报插入")
        return markdown_content

    # 收集要插入的海报
    insertions = []  # [(line_number, poster_config), ...]

    # 1. Cover 海报：插入到第一个 ## 之前
    first_h2_line = None
    for section in structure['sections']:
        if section['level'] == 2:
            first_h2_line = section['start_line']
            break

    if first_h2_line:
        cover_config = {
            'type': 'cover',
            'config': {
                'title': structure['title'],
                'subtitle': structure['subtitle'] or '点击阅读',
            }
        }
        insertions.append((first_h2_line, cover_config))
    else:
        # 没有 H2，直接在正文前插入
        cover_config = {
            'type': 'cover',
            'config': {
                'title': structure['title'],
                'subtitle': structure['subtitle'] or '点击阅读',
            }
        }
        insertions.append((1, cover_config))

    # 2. 分析每个 H2 章节，决定是否插入海报
    quote_count = 0
    center_count = 0

    for section in structure['sections']:
        if section['level'] != 2:
            continue

        section_title = section['title']
        section_content = section['content']

        # 跳过太短的章节
        if len(section_content) < 200:
            continue

        # 检测是否是"关键观点"类章节 → 插入 quote
        quote_indicators = ['决定', '关键', '核心', '最重要', '本质', '真正的', '结论', '总结', '记住', '本质']
        is_key_point = any(indicator in section_title for indicator in quote_indicators)

        # 检测是否有长引用
        has_long_quote = len(section.get('quotes', [])) > 0

        if is_key_point and has_long_quote and quote_count < 2:
            quote = section['quotes'][0]
            # 尝试从内容中提取更完整的引用
            full_quote = _extract_full_quote(section_content, quote['text'])
            insertions.append((quote['line'], {
                'type': 'quote',
                'config': {
                    'text': full_quote,
                    'author': '',
                }
            }))
            quote_count += 1
            continue

        # 检测是否是"对比"类章节 → 插入 compare
        compare_indicators = ['误区', '对比', '两种', '差异', '区别', '差距', '输入', '输出', 'Before', 'After']
        has_compare_structure = _detect_compare_structure(section.get('lists', []))

        if any(indicator in section_title for indicator in compare_indicators) and has_compare_structure:
            lists = section.get('lists', [])
            left_items, right_items = _split_list_for_compare(lists)
            if left_items and right_items:
                insertions.append((section['start_line'] + 1, {
                    'type': 'compare',
                    'config': {
                        'title': section_title,
                        'left_title': '一方面',
                        'left_items': left_items[:5],
                        'right_title': '另一方面',
                        'right_items': right_items[:5],
                    }
                }))
                continue

        # 检测是否是"步骤/时间线"类章节 → 插入 timeline
        timeline_indicators = ['步骤', '流程', '阶段', '时间线', '先后', '首先', '然后', '最后', '第', '一、二', '三步']
        list_count = len(section.get('lists', []))

        if (any(indicator in section_title for indicator in timeline_indicators) and list_count >= 3) or list_count >= 5:
            lists = section.get('lists', [])
            timeline_items = []
            for i, item in enumerate(lists[:4]):
                text = item['text']
                # 尝试分离日期/步骤和描述
                parts = re.split(r'[·:：\-\–\—]', text, 1)
                if len(parts) == 2:
                    date_event = parts[0].strip()
                    desc = parts[1].strip()
                else:
                    date_event = f"步骤{i+1}"
                    desc = text[:30]
                timeline_items.append({
                    'date': date_event,
                    'event': desc[:30],
                    'desc': '',
                })

            if timeline_items:
                insertions.append((section['start_line'] + 1, {
                    'type': 'timeline',
                    'config': {
                        'title': section_title,
                        'items': timeline_items,
                    }
                }))
                continue

        # 默认：章节标题后插入 center 海报（章节过渡）
        if center_count < 2:
            insertions.append((section['start_line'] + 1, {
                'type': 'center',
                'config': {
                    'title': section_title,
                    'subtitle': '',
                }
            }))
            center_count += 1

    # 限制总海报数量
    if len(insertions) > max_posters:
        # 优先保留 cover，剩下按位置均匀选择
        cover_insert = insertions[0]
        remaining = insertions[1:]
        step = len(remaining) / (max_posters - 1)
        selected = [cover_insert]
        for i in range(max_posters - 1):
            idx = int((i + 1) * step)
            if idx < len(remaining):
                selected.append(remaining[idx])
        insertions = selected

    # 按行号排序（从后往前插入，避免行号偏移）
    insertions.sort(key=lambda x: x[0], reverse=True)

    # 执行插入
    lines = markdown_content.split('\n')
    for line_num, poster_config in insertions:
        marker = _build_poster_marker(poster_config)
        lines.insert(line_num, marker)

    return '\n'.join(lines)


def _extract_full_quote(section_content: str, short_quote: str) -> str:
    """从章节内容中提取完整引用"""
    # 尝试找到引用块的完整内容
    quote_lines = []
    in_quote = False

    for line in section_content.split('\n'):
        if line.strip().startswith('>'):
            in_quote = True
            quote_lines.append(re.sub(r'^>\s?', '', line.strip()))
        elif in_quote and not line.strip():
            break
        elif in_quote:
            break

    if quote_lines:
        full = ' '.join(quote_lines)
        if len(full) > len(short_quote):
            return full[:100]

    return short_quote[:100]


def _detect_compare_structure(lists: list) -> bool:
    """检测是否存在对比结构（成对出现的列表项）"""
    if len(lists) < 4:
        return False

    # 检测对称性：是否有成对的相似长度项
    items = [item['text'] for item in lists]

    # 简单启发式：检查前后项是否有相似的结构词
    indicators_left = ['输入', '原因', '问题', 'Before', '过去', '表面', '劣势']
    indicators_right = ['输出', '结果', '方案', 'After', '现在', '本质', '优势']

    left_count = sum(1 for t in items if any(ind in t for ind in indicators_left))
    right_count = sum(1 for t in items if any(ind in t for ind in indicators_right))

    return left_count >= 2 and right_count >= 2


def _split_list_for_compare(lists: list) -> tuple:
    """将列表分成左右两部分用于对比海报"""
    if len(lists) < 4:
        return [], []

    items = [item['text'] for item in lists]
    mid = len(items) // 2

    indicators_left = ['输入', '原因', '问题', 'Before', '过去', '表面', '劣势', '误区', '无用', '错']
    indicators_right = ['输出', '结果', '方案', 'After', '现在', '本质', '优势', '正确', '有用', '对']

    left_items = []
    right_items = []

    for item in items:
        if any(ind in item for ind in indicators_left):
            left_items.append(item)
        elif any(ind in item for ind in indicators_right):
            right_items.append(item)
        else:
            # 均匀分配
            if len(left_items) <= len(right_items):
                left_items.append(item)
            else:
                right_items.append(item)

    # 如果分配不均匀，前后半段分
    if not left_items or not right_items:
        mid = len(items) // 2
        left_items = items[:mid]
        right_items = items[mid:]

    return left_items[:5], right_items[:5]


def _build_poster_marker(poster_config: dict) -> str:
    """构建海报标记字符串"""
    poster_type = poster_config['type']
    config = poster_config['config']

    if poster_type == 'cover':
        lines = ['<!-- POSTER:cover']
        lines.append(f"title: {config.get('title', '')}")
        subtitle = config.get('subtitle', '')
        if subtitle:
            lines.append(f"subtitle: {subtitle}")
        lines.append("-->")
        return '\n'.join(lines)

    elif poster_type == 'quote':
        lines = ['<!-- POSTER:quote']
        lines.append(f"text: {config.get('text', '')}")
        author = config.get('author', '')
        if author:
            lines.append(f"author: {author}")
        lines.append("-->")
        return '\n'.join(lines)

    elif poster_type == 'compare':
        lines = ['<!-- POSTER:compare']
        lines.append(f"title: {config.get('title', '')}")
        lines.append(f"left_title: {config.get('left_title', '输入')}")
        for item in config.get('left_items', []):
            lines.append(f"  - {item}")
        lines.append(f"right_title: {config.get('right_title', '输出')}")
        for item in config.get('right_items', []):
            lines.append(f"  - {item}")
        lines.append("-->")
        return '\n'.join(lines)

    elif poster_type == 'timeline':
        lines = ['<!-- POSTER:timeline']
        lines.append(f"title: {config.get('title', '')}")
        lines.append("items:")
        for item in config.get('items', []):
            lines.append(f"  - date: {item.get('date', '')}")
            lines.append(f"    event: {item.get('event', '')}")
            if item.get('desc'):
                lines.append(f"    desc: {item.get('desc', '')}")
        lines.append("-->")
        return '\n'.join(lines)

    elif poster_type == 'center':
        lines = ['<!-- POSTER:center']
        lines.append(f"title: {config.get('title', '')}")
        subtitle = config.get('subtitle', '')
        if subtitle:
            lines.append(f"subtitle: {subtitle}")
        lines.append("-->")
        return '\n'.join(lines)

    return ''
