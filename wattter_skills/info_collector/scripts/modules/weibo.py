
import asyncio
from .base import BaseModule, LoginRequiredError

class WeiboModule(BaseModule):
    @property
    def name(self):
        return "Weibo"

    async def run(self):
        page = await self.context.new_page()
        all_items = []
        
        try:
            await self.check_login(page)
            
            targets = self.config.get('targets', [])
            for target in targets:
                items = await self.scrape_target(page, target)
                all_items.extend(items)
                # Random delay between targets
                await asyncio.sleep(2)
                
        finally:
            await page.close()
            
        return all_items

    async def check_login(self, page):
        print("[Weibo] Checking login status...")
        await page.goto("https://weibo.com")
        # await page.wait_for_load_state('networkidle')
        await page.wait_for_load_state('domcontentloaded')
        await asyncio.sleep(5)
        
        try:
            # Check for "登录/注册" button which indicates logged out state
            login_btn = page.get_by_text("登录/注册")
            if await login_btn.count() > 0 and await login_btn.is_visible():
                print("⚠️  [Weibo] Not logged in.")
                
                # Check if headless
                is_headless = self.config.get('_system', {}).get('headless', True)
                if is_headless:
                    raise LoginRequiredError("Weibo login required")
                
                print("⏳ Waiting for login (max 120s)...")
                
                # Poll for login status
                max_retries = 60 # 60 * 2s = 120s
                for i in range(max_retries):
                    if not (await login_btn.count() > 0 and await login_btn.is_visible()):
                        print("\n✅  [Weibo] Login detected!")
                        return
                    await asyncio.sleep(2)
                    print(".", end="", flush=True)
                
                print("\n❌  [Weibo] Login timeout. Continuing anyway (might fail)...")
            else:
                print("✅  [Weibo] Likely logged in.")
        except LoginRequiredError:
            raise
        except Exception as e:
            print(f"[Weibo] Login check warning: {e}")

    async def scrape_target(self, page, target):
        url = target['url']
        name = target['name']
        limit = target.get('limit', 5)
        
        print(f"[Weibo] Scraping {name} ({url})...")
        await page.goto(url)
        await page.wait_for_load_state('domcontentloaded')
        await asyncio.sleep(5) # Wait for initial render
        
        # Scroll down a bit to ensure feed loads
        await self.smart_scroll(page, max_scrolls=1)

        try:
            # Try waiting for article element which is common in modern Weibo
            await page.wait_for_selector('article, div[class*="wbpro-feed-content"], div[class*="feed_body"]', timeout=10000)
        except:
            print(f"[Weibo] Timeout waiting for feed content on {name}. Saving screenshot...")
            debug_path = f"outputs/debug_{name}.png"
            await page.screenshot(path=debug_path)
            print(f"[Weibo] Saved screenshot to {debug_path}")

        items = []
        collected_ids = set()
        no_new_data_count = 0

        while len(items) < limit and no_new_data_count < 3:
            # Execute JS to scrape items
            new_items = await page.evaluate(f"""
                () => {{
                    {self.JS_PARSERS}
                    
                    const items = [];
                    // Support multiple selector strategies
                    const articles = document.querySelectorAll('article, div[class*="feed_content"], div[class*="wbpro-feed-content"]');
                    
                    articles.forEach(article => {{
                        try {{
                            // Content
                            let content = "";
                            const textEl = article.querySelector('div[class*="wbpro-feed-content"], div[class*="detail_text"], div[class*="content"]');
                            if (textEl) {{
                                content = textEl.innerText;
                            }} else {{
                                content = article.innerText.substring(0, 500);
                            }}
                            
                            if (!content || !content.trim()) return;
                            
                            // Time & Link
                            let timeStr = "Unknown time";
                            let link = "";
                            const timeEl = article.querySelector('a[class*="head_time"], a[class*="head-info_time"], a[href*="/status/"]');
                            
                            if (timeEl) {{
                                timeStr = timeEl.innerText;
                                const href = timeEl.getAttribute('href');
                                if (href) {{
                                    link = href.startsWith('http') ? href : (href.startsWith('//') ? 'https:' + href : 'https://weibo.com' + href);
                                }}
                            }}
                            
                            if (!link) {{
                                // Try to find link in other places if time element failed
                                const anyLink = article.querySelector('a[href*="/status/"]');
                                if (anyLink) {{
                                    const href = anyLink.getAttribute('href');
                                    link = href.startsWith('http') ? href : 'https://weibo.com' + href;
                                }}
                            }}

                            // Stats
                            // Weibo Toolbar: Like, Comment, Repost
                            let likes = 0, comments = 0, reposts = 0;
                            
                            const toolBar = article.querySelector('div[class*="toolbar"], div[class*="feed_action"]');
                            if (toolBar) {{
                                const spans = toolBar.querySelectorAll('span[class*="woo-like-count"], span[class*="text"], em');
                                // This is heuristic; precise selectors depend on exact Weibo version (v6/v7)
                                // We iterate and look for numbers
                                
                                // Better strategy: look for specific icons or structure
                                // Assuming typical order: Repost, Comment, Like
                                const buttons = toolBar.querySelectorAll('a, button, div[role="button"]');
                                if (buttons.length >= 3) {{
                                     // Reverse mapping or just trying to parse any numbers found
                                     // Often: [Share] [Comment] [Like]
                                     
                                     // Try to parse text from buttons
                                     buttons.forEach(btn => {{
                                         const text = btn.innerText;
                                         const num = parseNumber(text);
                                         
                                         // Heuristic based on text or icon class (if we could see it)
                                         // For now, let's just try to grab numbers if available
                                         // This part is tricky without precise selectors for "like" vs "comment"
                                         
                                         // Specific check for like icon/class could be added here
                                     }});
                                }}
                            }}

                            items.push({{
                                'source': 'Weibo',
                                'author': '{name}',
                                'content': content.trim(),
                                'time': timeStr,
                                'link': link,
                                'raw_text': content // For debugging/dedup
                            }});
                        }} catch (e) {{
                            // console.error(e);
                        }}
                    }});
                    return items;
                }}
            """)
            
            new_items_found = False
            for item in new_items:
                if len(items) >= limit:
                    break
                
                # Deduplicate by link (if available) or content hash
                unique_key = item['link'] if item['link'] else hash(item['content'])
                
                if unique_key not in collected_ids:
                    collected_ids.add(unique_key)
                    items.append(item)
                    new_items_found = True
                    print(f"   Collected: {item['content'][:30].replace('\\n', ' ')}...")
            
            if new_items_found:
                no_new_data_count = 0
            else:
                no_new_data_count += 1
            
            # Scroll
            await self.smart_scroll(page)

        return items
