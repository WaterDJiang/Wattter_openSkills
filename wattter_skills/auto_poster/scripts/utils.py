import os
import re
import markdown
import frontmatter
from pathlib import Path
import urllib.request
import hashlib
import ssl

def get_mac_code_block_svg():
    return """
    <svg xmlns="http://www.w3.org/2000/svg" version="1.1" x="0px" y="0px" width="45px" height="13px" viewBox="0 0 450 130">
        <ellipse cx="50" cy="65" rx="50" ry="52" stroke="rgb(220,60,54)" stroke-width="2" fill="rgb(237,108,96)" />
        <ellipse cx="225" cy="65" rx="50" ry="52" stroke="rgb(218,151,33)" stroke-width="2" fill="rgb(247,193,81)" />
        <ellipse cx="400" cy="65" rx="50" ry="52" stroke="rgb(27,161,37)" stroke-width="2" fill="rgb(100,200,86)" />
    </svg>
    """

def download_image(url, temp_dir):
    try:
        hash_name = hashlib.md5(url.encode('utf-8')).hexdigest()
        ext = os.path.splitext(url)[1] or '.png'
        # Handle query parameters in extension
        if '?' in ext:
            ext = ext.split('?')[0]
            
        local_path = os.path.join(temp_dir, f"remote_{hash_name}{ext}")
        
        if not os.path.exists(local_path):
            print(f"Downloading image: {url}")
            # Add user agent to prevent 403
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(url, local_path)
            
        return local_path
    except Exception as e:
        print(f"Failed to download image {url}: {e}")
        return None

def process_images(content, base_dir, temp_dir):
    """
    Replace images with placeholders and return image mapping
    """
    images = []
    
    def replace_image(match):
        alt = match.group(1)
        src = match.group(2)
        
        # Determine local path
        local_path = None
        if src.startswith(('http://', 'https://')):
            local_path = download_image(src, temp_dir)
        elif os.path.isabs(src):
            local_path = src
        else:
            local_path = os.path.abspath(os.path.join(base_dir, src))
            
        if local_path and os.path.exists(local_path):
            placeholder = f"[[IMAGE_PLACEHOLDER_{len(images)}]]"
            images.append({
                'placeholder': placeholder,
                'local_path': local_path,
                'src': src,
                'alt': alt
            })
            return placeholder
        else:
            print(f"Warning: Image not found: {src}")
            return match.group(0) # Keep original if not found

    # Regex for standard markdown images ![alt](src)
    processed_content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, content)
    return processed_content, images

def post_process_html(html):
    """
    Add Mac styling to code blocks and other tweaks
    """
    # 1. Wrap <pre><code>...</code></pre> with Mac styling
    mac_svg = get_mac_code_block_svg()
    
    def wrap_code_block(match):
        code_content = match.group(1)
        return f'<pre class="hljs code__pre"><span class="mac-sign" style="padding: 10px 14px 0;">{mac_svg}</span>{code_content}</pre>'
        
    # Markdown produces <pre><code>...</code></pre> or <pre><code class="...">...</code></pre>
    # We want to target the outer <pre>
    html = re.sub(r'<pre>(<code.*?>.*?</code>)</pre>', wrap_code_block, html, flags=re.DOTALL)
    
    return html

def parse_markdown(file_path, theme='wechat'):
    """
    Parse markdown file to get title and html content
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)
    
    # Setup temp dir for images
    import tempfile
    temp_dir = os.path.join(tempfile.gettempdir(), 'auto-poster-images')
    os.makedirs(temp_dir, exist_ok=True)
    base_dir = os.path.dirname(os.path.abspath(file_path))
    
    # Process images first
    processed_content, images = process_images(post.content, base_dir, temp_dir)
    
    # Use extensions for better rendering
    # extra extension supports markdown inside HTML blocks
    html_content = markdown.markdown(processed_content, extensions=['fenced_code', 'tables', 'nl2br', 'extra'])
    
    # Post process HTML (Mac code blocks)
    html_content = post_process_html(html_content)
    
    # Apply theme
    if theme:
        try:
            # Resolve theme path relative to this script
            script_dir = Path(__file__).parent
            theme_path = script_dir / 'assets' / f'{theme}.css'
            
            if theme_path.exists():
                with open(theme_path, 'r', encoding='utf-8') as f:
                    css = f.read()
                
                # Wrap content with styles and structure
                # Note: We put styles in a <style> block. 
                # Ideally, for WeChat, styles should be inline, but this is a best-effort approach
                # that works if the browser computes styles before copy.
                html_content = f"""
                <section id="output">
                    <style>
                    {css}
                    </style>
                    {html_content}
                </section>
                """
        except Exception as e:
            print(f"Failed to apply theme {theme}: {e}")
    
    # Get title from frontmatter or filename
    title = post.metadata.get('title')
    if not title:
        title = Path(file_path).stem
        
    return {
        'title': title,
        'content': html_content,
        'raw': post.content,
        'metadata': post.metadata,
        'images': images
    }

def get_browser_user_data_dir(platform_name):
    """
    Get persistent user data directory
    """
    home_dir = Path.home()
    base_dir = home_dir / '.auto-poster'
    browser_data_dir = base_dir / 'browser_data' / platform_name
    
    try:
        browser_data_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Failed to create browser data dir at {browser_data_dir}: {e}")
        # Fallback to temp dir
        import tempfile
        return Path(tempfile.gettempdir()) / 'auto-poster' / platform_name
        
    return str(browser_data_dir)
