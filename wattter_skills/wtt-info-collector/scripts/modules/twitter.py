
import asyncio
import random
from .base import BaseModule, LoginRequiredError

class TwitterModule(BaseModule):
    @property
    def name(self):
        return "Twitter"

    async def run(self):
        page = await self.context.new_page()
        all_items = []

        try:
            # 1. Open Twitter and Check Login
            await self.check_login(page)

            # 2. Open "My List"
            # Strategy: Go to Lists page, pick the first one
            await self.open_my_list(page)

            # 3. Collect Tweets
            limit = self.config.get('limit', 20)
            all_items = await self.collect_tweets(page, limit)

            # 4. Calculate Scores
            self.calculate_scores(all_items)

            # 5. Sort by Score
            all_items.sort(key=lambda x: x.get('score', 0), reverse=True)

        finally:
            await page.close()

        return all_items

    async def check_login(self, page):
        print("[Twitter] Checking login status...")
        await page.goto("https://x.com/home")
        try:
            await page.wait_for_load_state('networkidle', timeout=10000)
        except:
            pass

        # Check for login indicators (e.g., account menu, tweet composer)
        # "Account menu" aria-label or data-testid="SideNav_AccountSwitcher_Button"
        
        try:
            is_logged_in = False
            for _ in range(3): # Try a few times
                if await page.locator('[data-testid="SideNav_AccountSwitcher_Button"]').count() > 0:
                    is_logged_in = True
                    break
                if await page.locator('[data-testid="AppTabBar_Profile_Link"]').count() > 0:
                    is_logged_in = True
                    break
                await asyncio.sleep(2)
            
            if is_logged_in:
                print("✅ [Twitter] Logged in.")
                return

            print("⚠️ [Twitter] Not logged in detected.")
            
            # Check if headless
            is_headless = self.config.get('_system', {}).get('headless', True)
            if is_headless:
                raise LoginRequiredError("Twitter login required")

            print("⏳ Waiting 120s for manual login...")
            # Wait for user to login
            await page.wait_for_selector('[data-testid="SideNav_AccountSwitcher_Button"]', timeout=120000)
            print("✅ [Twitter] Login detected!")

        except LoginRequiredError:
            raise
        except Exception as e:
            print(f"⚠️ [Twitter] Login check warning: {e}")

    async def open_my_list(self, page):
        list_url_override = self.config.get('list_url')
        
        if list_url_override:
            print(f"[Twitter] Navigating to configured list: {list_url_override}")
            try:
                await page.goto(list_url_override)
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)
                print("✅ [Twitter] Opened list.")
                return
            except Exception as e:
                print(f"❌ [Twitter] Error opening configured list: {e}")
                # Fallback to auto-discovery if needed, or just return
                return

        print("[Twitter] Navigating to Lists...")
        # Option 1: Click "Lists" in sidebar
        try:
            # Try to find the Lists link. It might be under "More" or directly visible.
            # Direct URL is safer: https://x.com/i/lists
            await page.goto("https://x.com/i/lists")
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)

            # Find the first list in "Pinned Lists" or "Your Lists"
            # These are usually links with href containing "/lists/"
            # We want to avoid "Discover new Lists" section if possible.
            # Usually the user's lists are at the top.
            
            # Selector for list items. 
            # Often: div[data-testid="cellInnerDiv"] a[href*="/lists/"]
            
            print("[Twitter] Looking for lists...")
            # Wait a bit for content
            await asyncio.sleep(3)
            
            lists = page.locator('div[data-testid="cellInnerDiv"] a[href*="/lists/"]')
            count = await lists.count()
            
            if count > 0:
                # Pick the first one (often the most recently used or pinned)
                first_list = lists.first
                list_name = await first_list.get_attribute("aria-label") or "Unknown List"
                list_url = await first_list.get_attribute("href")
                
                print(f"[Twitter] Found list: {list_url}")
                await first_list.click()
                await page.wait_for_load_state('networkidle')
                print(f"✅ [Twitter] Opened list.")
            else:
                print("❌ [Twitter] No lists found! Staying on current page.")

        except Exception as e:
            print(f"❌ [Twitter] Error opening list: {e}")

    async def collect_tweets(self, page, limit):
        print(f"[Twitter] Collecting {limit} tweets...")
        items = []
        collected_ids = set()
        
        # Scroll and collect
        no_new_data_count = 0
        
        while len(items) < limit and no_new_data_count < 5:
            # Use evaluate to execute JS for efficient parsing, referencing x-tweet-feed logic
            new_items = await page.evaluate("""
                () => {
                    const items = [];
                    const articles = document.querySelectorAll('article[data-testid="tweet"]');
                    
                    articles.forEach(article => {
                        try {
                            // Extract Link & ID
                            const timeLink = article.querySelector('time')?.parentElement;
                            if (!timeLink) return;
                            
                            const tweetUrl = timeLink.href;
                            const tweetId = tweetUrl.split('/status/')[1]?.split('?')[0];
                            if (!tweetId) return;

                            // Extract Text
                            const textElement = article.querySelector('[data-testid="tweetText"]');
                            const tweetText = textElement?.innerText || '';
                            if (!tweetText) return;

                            // Extract Author
                            const userLink = article.querySelector('[data-testid="User-Name"] a');
                            const userParts = (article.querySelector('[data-testid="User-Name"]')?.innerText || '').split('\\n');
                            const displayName = userParts[0] || '';
                            const username = userParts[1] || '';

                            // Extract Time
                            const timeElement = article.querySelector('time');
                            const timeStr = timeElement?.getAttribute('datetime') || '';

                            // Helper: Parse Numbers (including K, M, 万)
                            const parseNumber = (str) => {
                                if (!str) return 0;
                                str = str.trim().replace(/,/g, '');
                                if (str.includes('万')) return parseFloat(str) * 10000;
                                if (str.includes('K')) return parseFloat(str) * 1000;
                                if (str.includes('M')) return parseFloat(str) * 1000000;
                                return parseInt(str) || 0;
                            };

                            let replies = 0, retweets = 0, likes = 0, views = 0;
                            
                            // Extract Stats
                            const buttons = article.querySelectorAll('button[data-testid], a[href*="/analytics"]');
                            buttons.forEach(btn => {
                                const testId = btn.getAttribute('data-testid');
                                const ariaLabel = btn.getAttribute('aria-label') || '';
                                const btnText = btn.innerText.trim();
                                
                                const extractNum = (text) => {
                                    const match = text.match(/(\\d+(?:[,.]\\d+)?(?:[K|M|万])?)/);
                                    return match ? parseNumber(match[0]) : 0;
                                };

                                if (testId === 'reply') {
                                    replies = extractNum(ariaLabel) || parseNumber(btnText);
                                } else if (testId === 'retweet') {
                                    retweets = extractNum(ariaLabel) || parseNumber(btnText);
                                } else if (testId === 'like') {
                                    likes = extractNum(ariaLabel) || parseNumber(btnText);
                                } else if (ariaLabel.includes('View') || ariaLabel.includes('查看') || ariaLabel.includes('观看') || btn.href?.includes('/analytics')) {
                                    views = extractNum(ariaLabel) || parseNumber(btnText);
                                }
                            });

                            items.push({
                                source: 'twitter',
                                id: tweetId,
                                author: displayName,
                                handle: username,
                                content: tweetText,
                                link: tweetUrl,
                                time: timeStr,
                                stats: {
                                    reply: replies,
                                    repost: retweets,
                                    like: likes,
                                    view: views
                                }
                            });
                        } catch (e) {
                            // ignore error
                        }
                    });
                    return items;
                }
            """)
            
            new_items_found = False
            
            for item in new_items:
                if len(items) >= limit:
                    break
                    
                if item['link'] not in collected_ids:
                    items.append(item)
                    collected_ids.add(item['link'])
                    new_items_found = True
                    print(f"   Collected: {item['content'][:30].replace('\\n', ' ')}... (L:{item['stats']['like']}, V:{item['stats']['view']})")
            
            if new_items_found:
                no_new_data_count = 0
            else:
                no_new_data_count += 1
            
            # Optimized Scrolling: Scroll to bottom
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
        return items

    def calculate_scores(self, items):
        # Perspective: "AI Content for Beginners" (小白的 ai 内容)
        keywords = [
            "AI", "GPT", "LLM", "Prompt", "Cursor", "Trae", "Claude", "Gemini",
            "教程", "指南", "入门", "小白", "学习", "怎么", "如何", 
            "Tutorial", "Guide", "Beginner", "How to", "Introduction", "Tips",
            "工具", "神器", "推荐", "整理", "汇总", "Agent", "RAG"
        ]
        
        for item in items:
            text = item['content'].lower()
            stats = item['stats']
            
            # 1. Keyword Score
            kw_score = 0
            for kw in keywords:
                if kw.lower() in text:
                    kw_score += 1
            
            # 2. Engagement Score
            # Weight: Like=1, Repost=2, Reply=1, View=0.001
            # View weight is small because it's usually much larger than others
            eng_score = (stats['like'] * 1) + (stats['repost'] * 2) + (stats['reply'] * 1) + (stats.get('view', 0) * 0.001)
            
            # Final Score
            final_score = (kw_score * 50) + (eng_score / 100)
            
            item['score'] = round(final_score, 2)
            item['recommendation_reason'] = f"Keywords: {kw_score}, Engagement: {eng_score:.1f}"
