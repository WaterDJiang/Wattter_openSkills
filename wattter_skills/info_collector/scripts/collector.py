import asyncio
import os
import sys
import yaml
import shutil
import importlib
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
from jinja2 import Template

try:
    import jieba
    import jieba.analyse
    JIEBA_AVAILABLE = True
except ImportError:
    print("Warning: jieba not found. Topic analysis will be disabled.")
    JIEBA_AVAILABLE = False

import argparse
from modules.base import LoginRequiredError

class InfoCollector:
    def __init__(self, config_path, template_override=None, keyword=None, target_modules=None, headless_override=None):
        self.skill_dir = Path(__file__).parent.parent
        self.load_config(config_path)
        self.project_dir = Path(config_path).parent.absolute()
        
        self.template_override = template_override
        self.keyword = keyword
        self.target_modules = target_modules
        self.headless_override = headless_override
        self.user_data_dir = self.get_user_data_dir()
        self.context = None
        self.playwright = None

    def load_config(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

    def get_user_data_dir(self):
        # Use project directory for browser data to separate sessions per project
        data_dir = self.project_dir / 'browser_data'
        data_dir.mkdir(parents=True, exist_ok=True)
        return str(data_dir)

    async def init_browser(self):
        self.playwright = await async_playwright().start()
        # Default to True (Headless) as requested
        headless = self.config.get('global', {}).get('browser', {}).get('headless', True)
        
        if self.headless_override is not None:
            headless = self.headless_override
        
        print(f"Launching browser with user data: {self.user_data_dir} (Headless: {headless})")
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=headless,
            channel="chrome",
            args=['--start-maximized'],
            viewport=None
        )

    async def close_browser(self):
        if self.context:
            await self.context.close()
            self.context = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

    async def run_modules(self):
        collected_data = {}
        modules_config = self.config.get('modules', {})

        # Determine which modules to run
        modules_to_run = []
        if self.target_modules:
            # Run specified modules in order
            for m in self.target_modules:
                if m in modules_config:
                    modules_to_run.append(m)
                else:
                    print(f"Warning: Module '{m}' not found in config.")
        else:
            # Run all enabled modules
            modules_to_run = [k for k, v in modules_config.items() if v.get('enabled', False)]

        print(f"Plan to run modules: {modules_to_run}")

        max_retries = 1
        retry_count = 0

        while retry_count <= max_retries:
            try:
                if not self.playwright:
                    await self.init_browser()

                for i, module_key in enumerate(modules_to_run):
                    if module_key in collected_data:
                        continue

                    module_conf = modules_config[module_key].copy()
                    
                    # Determine current headless state
                    current_headless = True
                    if self.headless_override is not None:
                        current_headless = self.headless_override
                    else:
                        current_headless = self.config.get('global', {}).get('browser', {}).get('headless', True)
                    
                    # Inject system info
                    if '_system' not in module_conf:
                        module_conf['_system'] = {}
                    module_conf['_system']['headless'] = current_headless

                    # Inject runtime keyword for xiaohongshu
                    if module_key == 'xiaohongshu' and self.keyword:
                        print(f"ℹ️  Injecting runtime keyword: {self.keyword}")
                        module_conf['keywords'] = [self.keyword]

                    try:
                        # Import module dynamically
                        module_pkg = f"modules.{module_key}"
                        module_lib = importlib.import_module(module_pkg)
                        
                        # Get class
                        class_name = f"{module_key.capitalize()}Module"
                        if hasattr(module_lib, class_name):
                            ModuleClass = getattr(module_lib, class_name)
                            module_instance = ModuleClass(self.context, module_conf)
                            
                            print(f"\n--- Running Module: {module_instance.name} ---")
                            items = await module_instance.run()
                            collected_data[module_key] = items
                            
                            # Add delay between modules if not the last one
                            if i < len(modules_to_run) - 1:
                                print("Waiting before next module...")
                                await asyncio.sleep(2)
                        else:
                            print(f"Error: Class {class_name} not found in {module_pkg}")

                    except ImportError:
                        print(f"Error: Module {module_key} implementation not found.")
                    except LoginRequiredError:
                        # Check current headless state
                        current_headless = True
                        if self.headless_override is not None:
                            current_headless = self.headless_override
                        else:
                            current_headless = self.config.get('global', {}).get('browser', {}).get('headless', True)

                        if current_headless:
                            print(f"⚠️  [System] Login required for {module_key}. Switching to HEADFUL mode...")
                            await self.close_browser()
                            self.headless_override = False # Force headful
                            raise # Re-raise to trigger outer loop
                        else:
                            print(f"❌ [System] Login required for {module_key} but already in headful mode. Please login manually.")
                            # We can wait here or just fail. 
                            # If the module raised LoginRequiredError, it implies it already tried to wait or detected failure.
                            # So we skip this module or fail.
                            print(f"Skipping module {module_key} due to login failure.")
                            collected_data[module_key] = []
                    except Exception as e:
                        print(f"Error running module {module_key}: {e}")
                
                # If we finish the loop, break
                break

            except LoginRequiredError:
                retry_count += 1
                if retry_count > max_restarts:
                    print("❌ [System] Max restarts reached. Aborting.")
                    break
                print("🔄 Restarting browser session...")
                continue
            except Exception as e:
                print(f"❌ [System] Unexpected error in run loop: {e}")
                break

        return collected_data

    def analyze_data(self, data):
        """
        Analyze collected data to extract core topics and investment signals.
        """
        analysis_result = {
            'core_topics': [],
            'investment_signals': []
        }
        
        all_text = ""
        investment_keywords = ["股票", "A股", "美股", "港股", "基金", "行情", "大盘", "指数", "板块", "涨停", "跌停", "抄底", "加仓", "减仓", "牛市", "熊市", "多头", "空头", "趋势", "回调", "反弹", "突破", "支撑", "压力", "估值", "财报", "利好", "利空", "主力", "资金流向", "北向", "南向", "成交量", "K线", "均线", "MACD", "RSI", "纳指", "道指", "标普", "创业板", "科创板"]

        # 1. Aggregate text and filter investment signals
        for module, items in data.items():
            for item in items:
                content = item.get('content', '')
                all_text += content + "\n"
                
                # Check for investment keywords
                matched_keywords = [k for k in investment_keywords if k in content]
                if matched_keywords:
                    # Simple scoring: count of keywords
                    score = len(matched_keywords)
                    analysis_result['investment_signals'].append({
                        'item': item,
                        'score': score,
                        'matched_keywords': matched_keywords,
                        'source_module': module
                    })

        # Sort investment signals by relevance (score)
        analysis_result['investment_signals'].sort(key=lambda x: x['score'], reverse=True)

        # 2. Extract top keywords (Core Topics) using TF-IDF
        if all_text.strip() and JIEBA_AVAILABLE:
            # Exclude common stopwords (simplified list)
            # jieba has built-in stopwords, but we can add more if needed
            keywords = jieba.analyse.extract_tags(all_text, topK=20, withWeight=False, allowPOS=('n', 'vn', 'v'))
            analysis_result['core_topics'] = keywords

        return analysis_result

    def generate_report(self, data):
        # Analyze data first
        analysis = self.analyze_data(data)
        
        # Determine template
        if self.template_override:
            template_path = self.template_override
        else:
            # Auto-select based on data
            if len(data) == 1:
                if 'xiaohongshu' in data:
                    template_path = 'templates/xiaohongshu_report.md'
                    print("ℹ️  Auto-selected template: xiaohongshu_report.md")
                elif 'twitter' in data:
                    template_path = 'templates/twitter_report.md'
                    print("ℹ️  Auto-selected template: twitter_report.md")
                else:
                    template_path = self.config.get('global', {}).get('template', 'templates/summary.md')
            else:
                template_path = self.config.get('global', {}).get('template', 'templates/summary.md')

        # Resolve template path: check project_dir first, then skill_dir
        # If absolute, use as is.
        if not os.path.isabs(template_path):
            # Check project dir
            p_path = self.project_dir / template_path
            if p_path.exists():
                template_path = p_path
            else:
                # Fallback to skill dir
                s_path = self.skill_dir / template_path
                if s_path.exists():
                    template_path = s_path
                else:
                    # Default to skill_dir if neither exists (will likely fail on open)
                    template_path = self.skill_dir / template_path

        with open(template_path, 'r', encoding='utf-8') as f:
            template_str = f.read()

        # Calculate total count
        total_items = sum(len(items) for items in data.values())

        template = Template(template_str)
        report = template.render(
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            data=data,
            analysis=analysis,
            total_items=total_items
        )
        
        print("\n" + "="*50)
        print("Generated Report:")
        print("="*50)
        print(report)
        
        # Save to file
        output_dir_conf = self.config.get('global', {}).get('output_dir', 'outputs')
        if not os.path.isabs(output_dir_conf):
            # Output dir is relative to project_dir
            output_dir = self.project_dir / output_dir_conf
        else:
            output_dir = Path(output_dir_conf)
            
        output_dir.mkdir(exist_ok=True)
        
        # Name report based on collected modules
        module_names = "_".join(data.keys())
        if not module_names:
            module_names = "empty"
            
        output_file = output_dir / f"summary_{module_names}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nReport saved to: {output_file}")

    async def run(self):
        await self.init_browser()
        
        try:
            data = await self.run_modules()
            self.generate_report(data)
        finally:
            if self.context:
                await self.context.close()
            if self.playwright:
                await self.playwright.stop()

def init_workspace(target_dir, skill_dir):
    """Initialize a new workspace with config and readme."""
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"Creating workspace at: {target_dir}")
    
    # Copy config
    src_config = skill_dir / "config.yaml"
    dst_config = target_dir / "config.yaml"
    if src_config.exists():
        if not dst_config.exists():
            shutil.copy2(src_config, dst_config)
            print(f"Created config file: {dst_config}")
        else:
            print(f"Config file already exists: {dst_config}")
    else:
        print(f"Warning: Source config not found at {src_config}")
        
    # Copy README
    src_readme = skill_dir / "README.md"
    dst_readme = target_dir / "README.md"
    if src_readme.exists():
        if not dst_readme.exists():
            shutil.copy2(src_readme, dst_readme)
            print(f"Created README: {dst_readme}")
        else:
            print(f"README already exists: {dst_readme}")
    else:
        print(f"Warning: Source README not found at {src_readme}")

if __name__ == "__main__":
    # Add script directory to python path to allow module imports
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    parser = argparse.ArgumentParser(description='Info Collector')
    parser.add_argument('--config', '-c', type=str, help='Path to config file')
    parser.add_argument('--template', type=str, help='Path to custom template file')
    parser.add_argument('--keyword', '-k', type=str, help='Search keyword for Xiaohongshu')
    parser.add_argument('--modules', nargs='+', help='Specific modules to run (e.g. weibo xiaohongshu)')
    
    # Headless mode control
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--headless', action='store_true', help='Run in headless mode (hidden browser)')
    group.add_argument('--headful', action='store_true', help='Run in headful mode (visible browser)')
    
    args = parser.parse_args()

    # Determine headless override
    headless_override = None
    if args.headless:
        headless_override = True
    elif args.headful:
        headless_override = False

    # Path logic
    skill_dir = Path(__file__).parent.parent
    cwd = Path.cwd()
    
    # Determine config path
    if args.config:
        config_path = Path(args.config)
    else:
        # Default behavior:
        # 1. Check if we are running INSIDE the skill directory (dev mode)
        if cwd.resolve() == skill_dir.resolve():
            config_path = skill_dir / "config.yaml"
        else:
            # 2. Check if "info-collector" folder exists in CWD
            workspace_dir = cwd / "info-collector"
            config_path = workspace_dir / "config.yaml"
            
            # If config doesn't exist, initialize workspace
            if not config_path.exists():
                print("No configuration found. Initializing new workspace...")
                init_workspace(workspace_dir, skill_dir)
                print("\nWorkspace initialized.")
                print("Please configure 'info-collector/config.yaml' before running.")
                print("Continuing with default configuration...")
                # Continue execution with the newly created config
                
    
    collector = InfoCollector(
        config_path, 
        template_override=args.template, 
        keyword=args.keyword, 
        target_modules=args.modules,
        headless_override=headless_override
    )
    asyncio.run(collector.run())
