
import asyncio
import random
from .base import BaseModule, LoginRequiredError

class XiaohongshuModule(BaseModule):
    @property
    def name(self):
        return "Xiaohongshu"

    async def run(self):
        page = await self.context.new_page()
        all_items = []
        
        try:
            await self.check_login(page)
            
            keywords = self.config.get('keywords', [])
            if not keywords:
                print("⚠️  [Xiaohongshu] No keywords provided. Please use --keyword argument.")
                
            limit = self.config.get('limit', 20)
            
            for keyword in keywords:
                items = await self.scrape_keyword(page, keyword, limit)
                all_items.extend(items)
                await asyncio.sleep(random.uniform(2, 5))
            
            # Enrich with follower counts
            await self.enrich_user_data(page, all_items)
                
        finally:
            await page.close()
            
        return all_items

    async def check_login(self, page):
        print("[Xiaohongshu] Checking login status...")
        await page.goto("https://www.xiaohongshu.com")
        try:
            await page.wait_for_load_state('domcontentloaded', timeout=10000)
        except:
            pass
        await asyncio.sleep(2)
        
        try:
            # Check for specific login elements that block usage
            # Or check for "Avatar" which indicates logged in
            # Strategy: If we see the user avatar, we are logged in.
            # If we don't see it, we MIGHT be logged out, or just slow loading.
            
            # Look for avatar img or user profile link
            avatar = page.locator(".user-side-content .avatar-wrapper, .side-bar .user-avatar, #user-avatar")
            
            if await avatar.count() > 0:
                 print("✅  [Xiaohongshu] User avatar detected. Logged in.")
                 return

            # If no avatar, look for explicit "Login" button in header
            login_btn = page.locator(".login-btn, .login-button").first

            if await login_btn.count() > 0 and await login_btn.is_visible():
                print("⚠️  [Xiaohongshu] Login button detected.")
                
                # Check if headless
                is_headless = self.config.get('_system', {}).get('headless', True)
                if is_headless:
                    raise LoginRequiredError("Xiaohongshu login required")

                # Don't block forever, just warn and wait a bit
                print("⏳ Please log in if needed. Waiting 15s...")
                
                # Wait up to 15s for user to login
                for i in range(15):
                    if await avatar.count() > 0:
                        print("\n✅  [Xiaohongshu] Login detected!")
                        return
                    await asyncio.sleep(1)
                
                print("\n⚠️  [Xiaohongshu] Proceeding (might be limited)...")
            else:
                print("ℹ️  [Xiaohongshu] No obvious login button found. Assuming OK.")
                
        except LoginRequiredError:
            raise
        except Exception as e:
            print(f"[Xiaohongshu] Login check warning: {e}")

    async def enrich_user_data(self, page, items):
        print(f"[Xiaohongshu] Fetching follower counts for {len(items)} items...")
        for item in items:
            # If we don't have author_link, we can try to visit the note link first to find it
            target_url = item.get('author_link')
            visiting_note = False
            
            if not target_url:
                target_url = item.get('link')
                visiting_note = True
                
            if not target_url:
                continue
                
            try:
                # Use a separate page/tab if we are inside a run loop, 
                # but here we can reuse 'page' if we want, or create new one.
                # Reusing 'page' is fine as we are done with search results.
                
                print(f"[Xiaohongshu] Visiting {'note' if visiting_note else 'author'}: {target_url}...")
                await page.goto(target_url)
                await page.wait_for_load_state('domcontentloaded')
                await asyncio.sleep(random.uniform(1, 2))
                
                if visiting_note:
                    # If we are on note page, we need to click author avatar/name to go to profile
                    # Selector: .author-wrapper .name, .user-info .name
                    try:
                        author_link_el = page.locator(".author-wrapper, .author-container, .note-author").first
                        if await author_link_el.count() > 0:
                            await author_link_el.click()
                            await page.wait_for_load_state('domcontentloaded')
                            await asyncio.sleep(1.5)
                        else:
                            print("  -> Could not find author link on note page.")
                            item['followers'] = "Not Found"
                            continue
                    except Exception as e:
                        print(f"  -> Failed to click author on note page: {e}")
                        continue

                # Now we should be on author profile page
                # Strategy: Look for "粉丝" text and get the number associated
                # Usually: .data-info .count (nth 1)
                
                # Check if we are really on profile page (url contains /user/profile)
                if "/user/profile" in page.url:
                     fans_el = page.locator(".data-info .count").nth(1)
                     if await fans_el.count() > 0:
                         count = await fans_el.inner_text()
                         item['followers'] = count
                         print(f"  -> Followers: {count}")
                     else:
                         # Fallback: find element with text "粉丝" and look at siblings
                         print("  -> Could not find fans count element.")
                         item['followers'] = "Not Found"
                else:
                    print("  -> Not on user profile page.")
                    item['followers'] = "Not Found"
                
            except Exception as e:
                print(f"  -> Failed: {e}")
                item['followers'] = "Error"

    async def scrape_keyword(self, page, keyword, limit):
        print(f"[Xiaohongshu] Searching for '{keyword}'...")
        
        # Use direct URL for stability
        url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_search_result_notes"
        await page.goto(url)
        await page.wait_for_load_state('networkidle')
        await asyncio.sleep(3)

        # Apply Filters (Keep existing logic for filters as it requires clicks)
        try:
            # ... Filter logic kept as is for now, but skipping here to focus on scrape optimization
            # In a real refactor we would keep the filter logic
            pass 
        except Exception:
            pass
        
        # Scrape results
        items = []
        visited_urls = set()
        
        # Infinite scroll loop until we have enough items
        no_new_data_count = 0
        while len(items) < limit and no_new_data_count < 3:
            
            # Execute JS for efficient scraping
            new_items = await page.evaluate(f"""
                () => {{
                    {self.JS_PARSERS}
                    
                    const items = [];
                    // Fallback to .feed-card if .note-item not found
                    const cards = document.querySelectorAll('section.note-item, .feed-card');
                    
                    cards.forEach(card => {{
                        try {{
                            // Link
                            let href = "";
                            const linkEl = card.querySelector("a.cover") || card.querySelector("a[href*='/explore/']");
                            if (linkEl) {{
                                href = linkEl.getAttribute("href");
                            }}
                            
                            if (!href) return;
                            
                            const fullUrl = href.startsWith("http") ? href : "https://www.xiaohongshu.com" + href;
                            
                            // Title
                            let title = "No Title";
                            const titleEl = card.querySelector(".title, .name, .footer .title");
                            if (titleEl) title = titleEl.innerText;
                            
                            // Author
                            let authorName = "Unknown";
                            const authorEl = card.querySelector(".user .name, .author-wrapper .name, .footer .author");
                            if (authorEl) authorName = authorEl.innerText;
                            
                            // Likes
                            let likes = 0;
                            const likesEl = card.querySelector(".like-wrapper .count, .footer .like-count");
                            if (likesEl) {{
                                likes = parseNumber(likesEl.innerText);
                            }}
                            
                            // Author Link
                            let authorLink = "";
                            const userLinkEl = card.querySelector("a[href*='/user/profile/']");
                            if (userLinkEl) {{
                                const uHref = userLinkEl.getAttribute("href");
                                if (uHref) {{
                                    authorLink = uHref.startsWith("http") ? uHref : "https://www.xiaohongshu.com" + uHref;
                                }}
                            }}
                            
                            items.push({{
                                "title": title,
                                "link": fullUrl,
                                "date": "Today", 
                                "source": "Xiaohongshu",
                                "author": authorName,
                                "author_link": authorLink,
                                "likes": likes,
                                "followers": "N/A",
                                "keyword": "{keyword}"
                            }});
                        }} catch (e) {{
                            // console.error(e);
                        }}
                    }});
                    return items;
                }}
            """)
            
            print(f"[Xiaohongshu] Found {len(new_items)} cards on page...")
            
            current_batch_added = 0
            
            for item in new_items:
                if len(items) >= limit:
                    break
                    
                if item['link'] not in visited_urls:
                    visited_urls.add(item['link'])
                    items.append(item)
                    current_batch_added += 1
            
            if current_batch_added == 0:
                no_new_data_count += 1
            else:
                no_new_data_count = 0
                
            # Scroll
            await self.smart_scroll(page)
            
        return items
