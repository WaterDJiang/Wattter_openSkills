from abc import ABC, abstractmethod
import asyncio

class LoginRequiredError(Exception):
    """Raised when authentication is required but not detected."""
    pass

class BaseModule(ABC):
    # Common JS helper functions for parsing numbers and text
    JS_PARSERS = """
    const parseNumber = (str) => {
        if (!str) return 0;
        str = str.trim().replace(/,/g, '');
        if (str.includes('万')) return parseFloat(str) * 10000;
        if (str.includes('亿')) return parseFloat(str) * 100000000;
        if (str.includes('K')) return parseFloat(str) * 1000;
        if (str.includes('M')) return parseFloat(str) * 1000000;
        return parseInt(str) || 0;
    };
    """

    def __init__(self, context, config):
        """
        Initialize the module.
        :param context: Playwright browser context
        :param config: Module specific configuration
        """
        self.context = context
        self.config = config

    @abstractmethod
    async def run(self):
        """
        Run the module task.
        :return: List of collected items
        """
        pass

    @property
    @abstractmethod
    def name(self):
        """
        Return module name
        """
        pass

    async def smart_scroll(self, page, max_scrolls=1):
        """
        Scroll the page to trigger infinite loading.
        """
        for _ in range(max_scrolls):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
