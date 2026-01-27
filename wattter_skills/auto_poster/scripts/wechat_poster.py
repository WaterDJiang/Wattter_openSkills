import asyncio
import argparse
import os
import sys
import platform
import re
import subprocess
import tempfile
from playwright.async_api import async_playwright

try:
    from utils import parse_markdown, get_browser_user_data_dir
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from utils import parse_markdown, get_browser_user_data_dir

def copy_image_to_clipboard(image_path):
    """
    Copy image to system clipboard.
    Supports Mac (via swift script), Linux (xclip/wl-copy), Windows (PowerShell).
    """
    abs_path = os.path.abspath(image_path)
    if not os.path.exists(abs_path):
        print(f"Error: Image not found: {abs_path}")
        return False

    system = platform.system()
    
    if system == 'Darwin':
        # Use Swift script for reliable image copying on Mac
        swift_source = f"""
import AppKit
import Foundation

let inputPath = "{abs_path}"
let pasteboard = NSPasteboard.general
pasteboard.clearContents()

guard let image = NSImage(contentsOfFile: inputPath) else {{
    FileHandle.standardError.write("Failed to load image\\n".data(using: .utf8)!)
    exit(1)
}}

if !pasteboard.writeObjects([image]) {{
    FileHandle.standardError.write("Failed to write to clipboard\\n".data(using: .utf8)!)
    exit(1)
}}
"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.swift', delete=False) as f:
                f.write(swift_source)
                swift_path = f.name
            
            subprocess.run(['swift', swift_path], check=True)
            os.unlink(swift_path)
            return True
        except Exception as e:
            print(f"Failed to copy image on Mac: {e}")
            return False

    elif system == 'Linux':
        # Try wl-copy first, then xclip
        try:
            subprocess.run(['wl-copy', '--type', 'image/png'], input=open(abs_path, 'rb').read(), check=True)
            return True
        except:
            try:
                subprocess.run(['xclip', '-selection', 'clipboard', '-t', 'image/png', '-i', abs_path], check=True)
                return True
            except:
                print("Failed to copy image on Linux. Install wl-clipboard or xclip.")
                return False
                
    elif system == 'Windows':
        ps_script = f"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$img = [System.Drawing.Image]::FromFile('{abs_path}')
[System.Windows.Forms.Clipboard]::SetImage($img)
$img.Dispose()
"""
        try:
            subprocess.run(['powershell', '-command', ps_script], check=True)
            return True
        except Exception as e:
            print(f"Failed to copy image on Windows: {e}")
            return False
            
    return False

class WeChatPoster:
    def __init__(self, user_data_dir):
        self.user_data_dir = user_data_dir
        self.playwright = None
        self.context = None
        self.page = None

    async def init(self):
        print(f"Launching Chrome with user data dir: {self.user_data_dir}")
        self.playwright = await async_playwright().start()
        
        try:
            # Launch persistent context with local Chrome
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                channel="chrome",  # Use local Chrome
                headless=False,    # Always run in headed mode for user interaction
                viewport=None,     # Disable default viewport
                args=['--start-maximized'],
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
            )
            
            # Get existing page or create new one
            if self.context.pages:
                self.page = self.context.pages[0]
            else:
                self.page = await self.context.new_page()
                
        except Exception as e:
            print("Failed to launch Chrome. Please ensure Google Chrome is installed.")
            print(f"Error: {e}")
            sys.exit(1)

    async def ensure_logged_in(self):
        if not self.page:
            return

        print('Navigating to WeChat Official Account Platform...')
        await self.page.goto('https://mp.weixin.qq.com/', wait_until='domcontentloaded')

        def is_login_page(url):
            # If we don't have a token parameter and we are at root or close to it, we might be logged out.
            # However, mp.weixin.qq.com redirects to /cgi-bin/home?t=home/index&lang=zh_CN&token=... when logged in.
            return 'token=' not in url and ('/cgi-bin/home' not in url)

        # Wait a bit for potential redirect
        await self.page.wait_for_timeout(3000)

        if is_login_page(self.page.url):
            print('Login required. Please scan the QR code to log in.')
            
            # Wait until token appears in URL
            while 'token=' not in self.page.url:
                await self.page.wait_for_timeout(1000)
            
            print('Login detected! Resuming...')
            await self.page.wait_for_timeout(2000)

    async def post(self, title, content, author=None, images=None):
        if not self.page:
            raise Exception('Browser not initialized')

        # --- Step 0: Render content in a local page to get computed styles ---
        print('Rendering content with styles in a local tab...')
        render_page = await self.context.new_page()
        
        # Create a complete HTML document with styles
        # content already contains <style>...</style> from parse_markdown
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Render Preview</title>
        </head>
        <body>
            {content}
        </body>
        </html>
        """
        
        # Load content
        await render_page.set_content(full_html)
        await render_page.wait_for_load_state('networkidle')
        
        # Copy from the rendered page
        # We select the #output element (added by utils.py)
        print('Copying rendered content...')
        await render_page.evaluate("""async () => {
            const element = document.getElementById('output');
            if (!element) throw new Error('Output element not found');
            
            const selection = window.getSelection();
            const range = document.createRange();
            range.selectNodeContents(element);
            selection.removeAllRanges();
            selection.addRange(range);
            
            // Execute copy command
            document.execCommand('copy');
            
            // Clear selection
            selection.removeAllRanges();
        }""")
        
        # Verify clipboard content (optional, but good for debugging)
        # clipboard_content = await render_page.evaluate("navigator.clipboard.readText()")
        # print(f"Clipboard length: {len(clipboard_content)}")
        
        await render_page.close()
        print('Content copied to clipboard.')

        # --- Step 1: Navigate to WeChat ---
        await self.ensure_logged_in()

        # Extract token
        match = re.search(r'token=(\d+)', self.page.url)
        if not match:
            print("Could not find token in URL. Please manually navigate to home page.")
            return
        
        token = match.group(1)
        print(f"Token found: {token}")

        # Construct write URL
        # Updated URL for new draft (Draft Box -> New)
        # action=edit, isNew=1
        write_url = f'https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit&action=edit&type=10&isMul=1&isNew=1&token={token}&lang=zh_CN'
        
        print(f'Navigating to Write page: {write_url}')
        await self.page.goto(write_url, wait_until='domcontentloaded')
        
        # Check for 404 or error
        # Sometimes WeChat redirects to an error page or shows an alert
        await self.page.wait_for_timeout(2000)
        if "系统错误" in await self.page.title() or "404" in await self.page.title():
             print("⚠️ Detected error page. Attempting to navigate to Draft Box...")
             draft_url = f'https://mp.weixin.qq.com/cgi-bin/appmsg?action=list_card&type=10&token={token}&lang=zh_CN'
             await self.page.goto(draft_url, wait_until='domcontentloaded')
             print("👉 Please manually click '新的创作' (New Creation) -> '写新图文' (New Article)")
             print("   The script will wait for the editor to load...")
             
             # Wait for user to navigate to editor
             while True:
                 if "appmsg_edit" in self.page.url:
                     print("✅ Detected editor page!")
                     break
                 await self.page.wait_for_timeout(1000)

        # Wait for editor to load
        # Title input is usually #title or input[id="title"]
        try:
            await self.page.wait_for_selector('#title', state='visible', timeout=10000)
        except:
            print("Could not find title input immediately. Waiting longer...")
            await self.page.wait_for_timeout(5000)

        # 1. Fill Title
        print('Filling title...')
        title_input = self.page.locator('#title')
        if await title_input.count() == 0:
            # Fallback selectors
            title_input = self.page.locator('input[placeholder="请在这里输入标题"]')
        
        if await title_input.count() > 0:
            await title_input.fill(title)
        else:
            print("⚠️ Could not find title input field. Please fill it manually.")

        # 2. Fill Author
        if author:
            print(f'Filling author: {author}')
            author_input = self.page.locator('#author')
            if await author_input.count() > 0:
                await author_input.fill(author)
            else:
                print("⚠️ Could not find author input field.")

        # 3. Fill Content
        print('Writing content...')
        
        # Find editor
        # WeChat editor is often an iframe #ueditor_0 -> body
        # OR a div with contenteditable="true"
        
        editor_frame = None
        editor_body = None
        
        # Check for iframe first
        if await self.page.locator('iframe[id^="ueditor"]').count() > 0:
            print("Found editor iframe.")
            editor_frame = self.page.frame_locator('iframe[id^="ueditor"]').first
            editor_body = editor_frame.locator('body')
        elif await self.page.locator('#js_editor_area').count() > 0:
             # Sometimes it's a div
             print("Found editor div #js_editor_area")
             editor_body = self.page.locator('#js_editor_area')
        elif await self.page.locator('.ProseMirror').count() > 0:
            # Newer editor?
            print("Found ProseMirror editor")
            editor_body = self.page.locator('.ProseMirror')
        else:
            # Generic contenteditable search
            print("Searching for generic contenteditable div...")
            editor_body = self.page.locator('div[contenteditable="true"]').first
        
        if not editor_body:
            print("❌ Could not find editor area. Please paste content manually.")
        else:
            await editor_body.click()
            await self.page.wait_for_timeout(500)
            
            # Since we already copied the rendered content to clipboard in Step 0
            # We just need to paste it here.
            # No need to use navigator.clipboard.write again with raw HTML
            
            print('Pasting content...')
            is_mac = platform.system() == 'Darwin'
            modifier = 'Meta' if is_mac else 'Control'
            
            await self.page.keyboard.press(f'{modifier}+V')
            await self.page.wait_for_timeout(1000)
            
            # Check if paste worked (simple check if text length > 0)
            # This might be hard if inside iframe, but visual check is best.

        print('Content paste action completed.')

        # 4. Process Images
        if images:
            print(f"Processing {len(images)} images...")
            
            # Identify where the editor is for JS execution
            target_frame = self.page
            # We need to get the actual Frame object if it's an iframe
            if await self.page.locator('iframe[id^="ueditor"]').count() > 0:
                 iframe_element = await self.page.locator('iframe[id^="ueditor"]').first.element_handle()
                 if iframe_element:
                     frame = await iframe_element.content_frame()
                     if frame:
                         target_frame = frame
            
            for i, image in enumerate(images):
                placeholder = image['placeholder']
                local_path = image['local_path']
                
                print(f"[{i+1}/{len(images)}] Replacing {placeholder} with image...")
                
                if not os.path.exists(local_path):
                    print(f"  ⚠️ Image not found: {local_path}")
                    continue
                
                # 1. Copy image to clipboard
                if not copy_image_to_clipboard(local_path):
                    print(f"  ⚠️ Failed to copy image to clipboard")
                    continue
                
                # 2. Select placeholder text
                # We need to find the text node containing the placeholder and select it
                # Note: placeholder format is [[IMAGE_PLACEHOLDER_X]]
                found = await target_frame.evaluate(f"""(placeholder) => {{
                    const xpath = `//text()[contains(., '${placeholder}')]`;
                    const result = document.evaluate(xpath, document.body, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                    const textNode = result.singleNodeValue;
                    if (textNode) {{
                        const selection = window.getSelection();
                        const range = document.createRange();
                        range.selectNode(textNode);
                        selection.removeAllRanges();
                        selection.addRange(range);
                        return true;
                    }}
                    return false;
                }}""", placeholder)
                
                if found:
                    # 3. Paste
                    await self.page.wait_for_timeout(500) # Wait for selection to stabilize
                    
                    is_mac = platform.system() == 'Darwin'
                    modifier = 'Meta' if is_mac else 'Control'
                    await self.page.keyboard.press(f'{modifier}+V')
                    
                    # 4. Wait for upload
                    print("  Pasted. Waiting for upload...")
                    # Give it some time to upload and render
                    await self.page.wait_for_timeout(3000) 
                else:
                    print(f"  ⚠️ Placeholder {placeholder} not found in editor.")

    async def close(self):
        pass

async def main():
    parser = argparse.ArgumentParser(description='Auto post to WeChat Official Account')
    parser.add_argument('-m', '--markdown', required=True, help='Path to markdown file')
    
    args = parser.parse_args()
    
    try:
        article = parse_markdown(args.markdown)
    except Exception as e:
        print(e)
        sys.exit(1)

    user_data_dir = get_browser_user_data_dir('wechat')
    poster = WeChatPoster(user_data_dir)

    try:
        await poster.init()
        
        author = article.get('metadata', {}).get('author')
        await poster.post(article['title'], article['content'], author, article.get('images'))
        
        print("\n" + "="*50)
        print("✅ 标题和内容已填写")
        print("👉 请在浏览器中检查内容格式，并手动点击【保存】或【发布】按钮")
        print("⌨️  发布完成后，请在此终端按【回车键】结束程序并关闭浏览器...")
        print("="*50 + "\n")
        
        await asyncio.get_event_loop().run_in_executor(None, input)
        
    finally:
        await poster.close()

if __name__ == "__main__":
    asyncio.run(main())
