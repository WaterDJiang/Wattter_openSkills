import asyncio
import argparse
import os
import sys
import platform
from playwright.async_api import async_playwright

try:
    from utils import parse_markdown, get_browser_user_data_dir
except ImportError:
    # Allow running from parent directory or if utils is in same dir
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from utils import parse_markdown, get_browser_user_data_dir

# --- Poster ---

class ZhihuPoster:
    def __init__(self, user_data_dir):
        self.user_data_dir = user_data_dir
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def init(self, cdp_url=None):
        self.playwright = await async_playwright().start()
        
        if cdp_url:
            print(f"Connecting to existing Chrome via CDP: {cdp_url}")
            try:
                self.browser = await self.playwright.chromium.connect_over_cdp(cdp_url)
                if self.browser.contexts:
                    self.context = self.browser.contexts[0]
                else:
                    self.context = await self.browser.new_context()
                self.page = await self.context.new_page()
            except Exception as e:
                print(f"Failed to connect to existing Chrome at {cdp_url}")
                print(f"Error: {e}")
                sys.exit(1)
            return

        print(f"Launching Chrome with user data dir: {self.user_data_dir}")
        try:
            self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                channel="chrome",
                headless=False,
                viewport=None,
                args=['--start-maximized'],
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
            )
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

        def is_login_page(url):
            return 'signin' in url or 'passport.zhihu.com' in url

        if is_login_page(self.page.url):
            print('Login required. Please log in manually in the opened browser window.')
            
            # Wait until not on login page
            while is_login_page(self.page.url):
                await self.page.wait_for_timeout(1000)
            
            print('Login detected! Resuming...')
            # Wait for stability
            await self.page.wait_for_timeout(2000)
            
            if 'zhuanlan.zhihu.com/write' not in self.page.url:
                print('Redirecting to write page...')
                await self.page.goto('https://zhuanlan.zhihu.com/write', wait_until='domcontentloaded')

    async def post(self, title, content):
        if not self.page:
            raise Exception('Browser not initialized')

        print('Navigating to Zhihu Write page...')
        await self.page.goto('https://zhuanlan.zhihu.com/write', wait_until='domcontentloaded')

        await self.ensure_logged_in()

        # Ensure we are on the write page
        if 'zhuanlan.zhihu.com/write' not in self.page.url:
             print(f"Current URL is {self.page.url}, redirecting to write page...")
             await self.page.goto('https://zhuanlan.zhihu.com/write', wait_until='domcontentloaded')
             await self.page.wait_for_timeout(3000)

        print('Writing content...')

        # Try multiple selectors for title
        # Update: Zhihu placeholder might contain "（最多 100 个字）"
        title_selectors = [
            'textarea[placeholder^="请输入标题"]', 
            'input[placeholder^="请输入标题"]',
            'label[aria-label="标题"]',
            '.WriteIndex-titleInput input',
            '.WriteIndex-titleInput textarea',
            '[class*="Input-wrapper"] input',
            '[class*="Input-wrapper"] textarea',
            '[placeholder="标题"]'
        ]

        title_input = None
        for selector in title_selectors:
            try:
                el = self.page.locator(selector).first
                await el.wait_for(state='visible', timeout=5000)
                title_input = el
                print(f"Found title input using selector: {selector}")
                break
            except:
                continue

        if not title_input:
            print('Could not find title input. Dumping page title and URL for debug.')
            print(f"Page Title: {await self.page.title()}")
            print(f"Page URL: {self.page.url}")
            raise Exception('Could not find title input field')

        await title_input.fill(title)

        # Editor content
        editor = self.page.locator('.public-DraftEditor-content')
        await editor.click()
        
        # Ensure editor is focused
        await editor.focus()
        await self.page.wait_for_timeout(1000)

        # Grant permissions
        await self.context.grant_permissions(['clipboard-read', 'clipboard-write'])

        # Write to clipboard using browser API
        # Use a more robust way to set clipboard content
        print('Setting clipboard content...')
        await self.page.evaluate("""async (htmlContent) => {
            const type = "text/html";
            const blob = new Blob([htmlContent], { type });
            const data = [new ClipboardItem({ [type]: blob })];
            await navigator.clipboard.write(data);
            console.log('Clipboard content set via navigator.clipboard');
        }""", content)
        
        # Double check with a simple copy to ensure permission is active
        # And try to trigger a paste event manually if shortcut fails
        
        print('Pasting content...')
        is_mac = platform.system() == 'Darwin'
        modifier = 'Meta' if is_mac else 'Control'
        
        # Method 1: Keyboard shortcut
        await self.page.keyboard.press(f'{modifier}+V')
        await self.page.wait_for_timeout(1000)
        
        # Method 2: Check if content is empty, if so, try execCommand
        # Zhihu editor might not react to keyboard shortcut if not fully focused or in some states
        # Verify content length in editor
        content_length = await editor.evaluate('el => el.textContent.length')
        if content_length == 0:
            print('Keyboard paste failed, trying document.execCommand("paste")...')
            # Note: execCommand('paste') is restricted in many contexts, but worth a try or use alternative
            # Since we can't easily force paste via JS security model, we try focusing and pressing again
            await editor.click()
            await self.page.wait_for_timeout(500)
            await self.page.keyboard.press(f'{modifier}+V')

        print('Content paste action completed. Please check editor.')

    async def close(self):
        # Never close automatically as we need user to review and publish
        pass

async def main():
    parser = argparse.ArgumentParser(description='Auto post to Zhihu')
    parser.add_argument('-m', '--markdown', required=True, help='Path to markdown file')
    parser.add_argument('--use-existing-chrome', action='store_true')
    parser.add_argument('--cdp-url', default=os.getenv('AUTO_POSTER_CDP_URL'))
    
    args = parser.parse_args()
    
    try:
        article = parse_markdown(args.markdown)
    except Exception as e:
        print(e)
        sys.exit(1)

    user_data_dir = get_browser_user_data_dir('zhihu')
    poster = ZhihuPoster(user_data_dir)
    cdp_url = args.cdp_url or ('http://127.0.0.1:9222' if args.use_existing_chrome else None)

    try:
        await poster.init(cdp_url=cdp_url)
        await poster.post(article['title'], article['content'])
        
        print("\n" + "="*50)
        print("✅ 标题和内容已填写")
        print("👉 请在浏览器中检查内容格式，并手动点击【发布】按钮")
        print("⌨️  发布完成后，请在此终端按【回车键】结束程序并关闭浏览器...")
        print("="*50 + "\n")
        
        await asyncio.get_event_loop().run_in_executor(None, input)
        
    finally:
        await poster.close()

if __name__ == "__main__":
    asyncio.run(main())
