"""Web Searcher Plugin"""
import asyncio
from typing import Dict, Any, List
from urllib.parse import quote_plus


class WebSearcher:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.engine = self.config.get("default_engine", "duckduckgo")
        self.timeout = self.config.get("timeout_seconds", 30)
        self.max_results = self.config.get("max_results", 10)
        self.browser = None

    async def _get_browser(self):
        if self.browser is None:
            try:
                from playwright.async_api import async_playwright
                self._playwright = await async_playwright().start()
                self.browser = await self._playwright.chromium.launch(headless=True)
            except ImportError:
                raise RuntimeError("Playwright not installed")
        return self.browser

    async def search(self, query: str, num_results: int = None) -> List[Dict[str, Any]]:
        num_results = num_results or self.max_results
        browser = await self._get_browser()
        page = await browser.new_page()

        try:
            if self.engine == "duckduckgo":
                url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
                await page.goto(url, wait_until="networkidle")
                results = await page.query_selector_all(".result__snippet")
                data = []
                for result in results[:num_results]:
                    text = await result.inner_text()
                    data.append({"snippet": text, "source": "duckduckgo"})
                return data
            return []
        finally:
            await page.close()

    async def scrape(self, url: str, selector: str = "body") -> Dict[str, Any]:
        browser = await self._get_browser()
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)
            element = await page.query_selector(selector)
            if element:
                text = await element.inner_text()
                html = await element.inner_html()
                return {"url": url, "text": text, "html": html}
            return {"url": url, "error": "Selector not found"}
        finally:
            await page.close()

    async def screenshot(self, url: str, full_page: bool = False) -> bytes:
        browser = await self._get_browser()
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)
            return await page.screenshot(full_page=full_page)
        finally:
            await page.close()

    async def close(self):
        if self.browser:
            await self.browser.close()
            await self._playwright.stop()


async def initialize(context: Dict[str, Any]) -> WebSearcher:
    return WebSearcher(context.get("config", {}))