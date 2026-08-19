"""Browser Executor using Playwright for web automation"""
import os
import json
import base64
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, field
from urllib.parse import urlparse

import structlog

logger = structlog.get_logger()

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("playwright not available, browser automation disabled")


@dataclass
class BrowserConfig:
    """Browser configuration"""
    headless: bool = False  # Visible by default so user can watch
    confirm_sensitive: bool = True
    allowed_domains: List[str] = field(default_factory=list)  # Empty = all allowed
    blocked_domains: List[str] = field(default_factory=list)
    viewport: Dict[str, int] = field(default_factory=lambda: {"width": 1280, "height": 720})
    timeout: int = 30000  # Default timeout in ms
    user_agent: Optional[str] = None
    stealth: bool = True


@dataclass
class BrowserResult:
    """Result of a browser action"""
    success: bool
    output: Any = None
    error: Optional[str] = None
    screenshot: Optional[str] = None  # Base64 encoded
    url: Optional[str] = None
    title: Optional[str] = None


class BrowserExecutor:
    """Browser automation using Playwright"""
    
    def __init__(self, config: BrowserConfig = None):
        self.config = config or BrowserConfig()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the browser"""
        if self._initialized:
            return True
            
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not available")
            return False
            
        try:
            self.playwright = await async_playwright().start()
            
            launch_options = {
                "headless": self.config.headless,
            }
            
            if self.config.stealth:
                # Use stealth mode to avoid detection
                pass  # playwright-stealth would be applied here if installed
            
            self.browser = await self.playwright.chromium.launch(**launch_options)
            
            context_options = {
                "viewport": self.config.viewport,
            }
            
            if self.config.user_agent:
                context_options["user_agent"] = self.config.user_agent
                
            self.context = await self.browser.new_context(**context_options)
            self.page = await self.context.new_page()
            
            # Set default timeout
            self.page.set_default_timeout(self.config.timeout)
            
            # Add stealth script to avoid detection
            if self.config.stealth:
                await self._apply_stealth()
            
            self._initialized = True
            logger.info("Browser initialized", headless=self.config.headless)
            return True
            
        except Exception as e:
            logger.error("Failed to initialize browser", error=str(e))
            return False
    
    async def _apply_stealth(self):
        """Apply stealth scripts to avoid bot detection"""
        try:
            stealth_script = """
            // Overwrite navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Overwrite navigator.plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Overwrite navigator.languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Overwrite window.chrome
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            
            // Overwrite permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            """
            await self.page.add_init_script(stealth_script)
        except Exception as e:
            logger.warning("Failed to apply stealth", error=str(e))
    
    def _check_domain_allowed(self, url: str) -> bool:
        """Check if URL domain is allowed"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check blocked domains first
            for blocked in self.config.blocked_domains:
                if blocked.lower() in domain:
                    return False
            
            # Check allowed domains (if list is not empty)
            if self.config.allowed_domains:
                for allowed in self.config.allowed_domains:
                    if allowed.lower() in domain:
                        return True
                return False
            
            return True
        except Exception:
            return True  # Default to allow on parse error
    
    async def _confirm_sensitive(self, action: str, details: str) -> bool:
        """Request confirmation for sensitive actions"""
        if not self.config.confirm_sensitive:
            return True
        
        # In CLI mode, we'll log and return True for now
        # In a full implementation, this would prompt the user
        logger.info("Sensitive action requested", action=action, details=details)
        return True
    
    async def navigate(self, url: str, wait_until: str = "networkidle") -> BrowserResult:
        """Navigate to a URL"""
        try:
            if not self._initialized:
                if not await self.initialize():
                    return BrowserResult(success=False, error="Failed to initialize browser")
            
            # Check domain permission
            if not self._check_domain_allowed(url):
                return BrowserResult(success=False, error=f"Domain not allowed: {url}")
            
            # Confirm navigation to new domain
            if not await self._confirm_sensitive("navigate", f"Navigate to {url}"):
                return BrowserResult(success=False, error="Navigation cancelled by user")
            
            response = await self.page.goto(url, wait_until=wait_until)
            
            return BrowserResult(
                success=True,
                output=f"Navigated to {url}",
                url=self.page.url,
                title=await self.page.title()
            )
        except Exception as e:
            logger.error("Navigation failed", url=url, error=str(e))
            return BrowserResult(success=False, error=str(e))
    
    async def click(self, selector: str, timeout: int = 5000) -> BrowserResult:
        """Click an element"""
        try:
            if not self._initialized:
                return BrowserResult(success=False, error="Browser not initialized")
            
            if not await self._confirm_sensitive("click", f"Click element: {selector}"):
                return BrowserResult(success=False, error="Click cancelled by user")
            
            await self.page.click(selector, timeout=timeout)
            
            return BrowserResult(
                success=True,
                output=f"Clicked element: {selector}"
            )
        except Exception as e:
            logger.error("Click failed", selector=selector, error=str(e))
            return BrowserResult(success=False, error=str(e))
    
    async def fill(self, selector: str, value: str, timeout: int = 5000) -> BrowserResult:
        """Fill an input field"""
        try:
            if not self._initialized:
                return BrowserResult(success=False, error="Browser not initialized")
            
            if not await self._confirm_sensitive("fill", f"Fill field {selector}"):
                return BrowserResult(success=False, error="Fill cancelled by user")
            
            await self.page.fill(selector, value, timeout=timeout)
            
            return BrowserResult(
                success=True,
                output=f"Filled {selector} with: {value}"
            )
        except Exception as e:
            logger.error("Fill failed", selector=selector, error=str(e))
            return BrowserResult(success=False, error=str(e))
    
    async def type_text(self, selector: str, text: str, delay: int = 50) -> BrowserResult:
        """Type text into an element (simulates human typing)"""
        try:
            if not self._initialized:
                return BrowserResult(success=False, error="Browser not initialized")
            
            await self.page.type(selector, text, delay=delay)
            
            return BrowserResult(
                success=True,
                output=f"Typed into {selector}"
            )
        except Exception as e:
            logger.error("Type failed", selector=selector, error=str(e))
            return BrowserResult(success=False, error=str(e))
    
    async def extract(self, selector: str, attribute: Optional[str] = None) -> BrowserResult:
        """Extract text or attribute from elements"""
        try:
            if not self._initialized:
                return BrowserResult(success=False, error="Browser not initialized")
            
            elements = await self.page.query_selector_all(selector)
            
            results = []
            for elem in elements:
                if attribute:
                    value = await elem.get_attribute(attribute)
                else:
                    value = await elem.inner_text()
                results.append(value)
            
            return BrowserResult(
                success=True,
                output=results if len(results) > 1 else (results[0] if results else "")
            )
        except Exception as e:
            logger.error("Extract failed", selector=selector, error=str(e))
            return BrowserResult(success=False, error=str(e))
    
    async def screenshot(self, full_page: bool = False, path: Optional[str] = None) -> BrowserResult:
        """Take a screenshot"""
        try:
            if not self._initialized:
                return BrowserResult(success=False, error="Browser not initialized")
            
            screenshot_bytes = await self.page.screenshot(
                full_page=full_page,
                path=path
            )
            
            # Encode as base64 for transmission
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            return BrowserResult(
                success=True,
                output=f"Screenshot captured ({len(screenshot_bytes)} bytes)",
                screenshot=screenshot_b64
            )
        except Exception as e:
            logger.error("Screenshot failed", error=str(e))
            return BrowserResult(success=False, error=str(e))
    
    async def evaluate_js(self, script: str) -> BrowserResult:
        """Execute JavaScript in the page context"""
        try:
            if not self._initialized:
                return BrowserResult(success=False, error="Browser not initialized")
            
            if not await self._confirm_sensitive("javascript", f"Execute JS: {script[:100]}"):
                return BrowserResult(success=False, error="JS execution cancelled by user")
            
            result = await self.page.evaluate(script)
            
            return BrowserResult(
                success=True,
                output=result
            )
        except Exception as e:
            logger.error("JS evaluation failed", error=str(e))
            return BrowserResult(success=False, error=str(e))
    
    async def wait_for_selector(self, selector: str, timeout: int = 30000, state: str = "visible") -> BrowserResult:
        """Wait for an element to appear"""
        try:
            if not self._initialized:
                return BrowserResult(success=False, error="Browser not initialized")
            
            await self.page.wait_for_selector(selector, timeout=timeout, state=state)
            
            return BrowserResult(
                success=True,
                output=f"Element found: {selector}"
            )
        except Exception as e:
            logger.error("Wait for selector failed", selector=selector, error=str(e))
            return BrowserResult(success=False, error=str(e))
    
    async def hover(self, selector: str) -> BrowserResult:
        """Hover over an element"""
        try:
            if not self._initialized:
                return BrowserResult(success=False, error="Browser not initialized")
            
            await self.page.hover(selector)
            
            return BrowserResult(
                success=True,
                output=f"Hovered over: {selector}"
            )
        except Exception as e:
            logger.error("Hover failed", selector=selector, error=str(e))
            return BrowserResult(success=False, error=str(e))
    
    async def select_option(self, selector: str, value: str) -> BrowserResult:
        """Select an option from a dropdown"""
        try:
            if not self._initialized:
                return BrowserResult(success=False, error="Browser not initialized")
            
            await self.page.select_option(selector, value=value)
            
            return BrowserResult(
                success=True,
                output=f"Selected option: {value}"
            )
        except Exception as e:
            logger.error("Select option failed", selector=selector, error=str(e))
            return BrowserResult(success=False, error=str(e))
    
    async def wait_for_navigation(self, timeout: int = 30000) -> BrowserResult:
        """Wait for navigation to complete"""
        try:
            if not self._initialized:
                return BrowserResult(success=False, error="Browser not initialized")
            
            await self.page.wait_for_load_state("networkidle", timeout=timeout)
            
            return BrowserResult(
                success=True,
                output="Navigation complete",
                url=self.page.url,
                title=await self.page.title()
            )
        except Exception as e:
            logger.error("Wait for navigation failed", error=str(e))
            return BrowserResult(success=False, error=str(e))
    
    async def get_cookies(self) -> BrowserResult:
        """Get all cookies"""
        try:
            if not self._initialized:
                return BrowserResult(success=False, error="Browser not initialized")
            
            cookies = await self.context.cookies()
            
            return BrowserResult(
                success=True,
                output=cookies
            )
        except Exception as e:
            logger.error("Get cookies failed", error=str(e))
            return BrowserResult(success=False, error=str(e))
    
    async def set_cookies(self, cookies: List[Dict]) -> BrowserResult:
        """Set cookies"""
        try:
            if not self._initialized:
                return BrowserResult(success=False, error="Browser not initialized")
            
            await self.context.add_cookies(cookies)
            
            return BrowserResult(
                success=True,
                output=f"Set {len(cookies)} cookies"
            )
        except Exception as e:
            logger.error("Set cookies failed", error=str(e))
            return BrowserResult(success=False, error=str(e))
    
    async def go_back(self) -> BrowserResult:
        """Go back in history"""
        try:
            if not self._initialized:
                return BrowserResult(success=False, error="Browser not initialized")
            
            await self.page.go_back()
            await self.page.wait_for_load_state("networkidle")
            
            return BrowserResult(
                success=True,
                output="Navigated back",
                url=self.page.url,
                title=await self.page.title()
            )
        except Exception as e:
            logger.error("Go back failed", error=str(e))
            return BrowserResult(success=False, error=str(e))
    
    async def go_forward(self) -> BrowserResult:
        """Go forward in history"""
        try:
            if not self._initialized:
                return BrowserResult(success=False, error="Browser not initialized")
            
            await self.page.go_forward()
            await self.page.wait_for_load_state("networkidle")
            
            return BrowserResult(
                success=True,
                output="Navigated forward",
                url=self.page.url,
                title=await self.page.title()
            )
        except Exception as e:
            logger.error("Go forward failed", error=str(e))
            return BrowserResult(success=False, error=str(e))
    
    async def reload(self) -> BrowserResult:
        """Reload the current page"""
        try:
            if not self._initialized:
                return BrowserResult(success=False, error="Browser not initialized")
            
            await self.page.reload()
            await self.page.wait_for_load_state("networkidle")
            
            return BrowserResult(
                success=True,
                output="Page reloaded",
                url=self.page.url,
                title=await self.page.title()
            )
        except Exception as e:
            logger.error("Reload failed", error=str(e))
            return BrowserResult(success=False, error=str(e))
    
    async def get_page_content(self) -> BrowserResult:
        """Get full page HTML content"""
        try:
            if not self._initialized:
                return BrowserResult(success=False, error="Browser not initialized")
            
            content = await self.page.content()
            
            return BrowserResult(
                success=True,
                output=content
            )
        except Exception as e:
            logger.error("Get content failed", error=str(e))
            return BrowserResult(success=False, error=str(e))
    
    async def get_page_text(self) -> BrowserResult:
        """Get visible page text"""
        try:
            if not self._initialized:
                return BrowserResult(success=False, error="Browser not initialized")
            
            text = await self.page.inner_text("body")
            
            return BrowserResult(
                success=True,
                output=text
            )
        except Exception as e:
            logger.error("Get text failed", error=str(e))
            return BrowserResult(success=False, error=str(e))
    
    async def close(self):
        """Close the browser"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            self._initialized = False
            logger.info("Browser closed")
        except Exception as e:
            logger.error("Error closing browser", error=str(e))
    
    def is_ready(self) -> bool:
        """Check if browser is ready"""
        return self._initialized and self.page is not None
    
    async def get_page_info(self) -> Dict[str, Any]:
        """Get current page info"""
        if not self._initialized:
            return {"url": None, "title": None}
        
        return {
            "url": self.page.url,
            "title": await self.page.title()
        }


# Backwards compatible functions for CLI compatibility
async def get_browser_executor(config: BrowserConfig = None) -> BrowserExecutor:
    """Get or create browser executor"""
    return BrowserExecutor(config)


async def run_browser_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """Run a browser task from a dict"""
    executor = BrowserExecutor()
    
    try:
        if not await executor.initialize():
            return {"success": False, "error": "Failed to initialize browser"}
        
        action = task.get("action")
        params = task.get("params", {})
        
        if action == "navigate":
            result = await executor.navigate(params.get("url", ""))
        elif action == "click":
            result = await executor.click(params.get("selector", ""))
        elif action == "fill":
            result = await executor.fill(params.get("selector", ""), params.get("value", ""))
        elif action == "extract":
            result = await executor.extract(params.get("selector", ""))
        elif action == "screenshot":
            result = await executor.screenshot(params.get("full_page", False))
        elif action == "evaluate":
            result = await executor.evaluate_js(params.get("script", ""))
        elif action == "click":
            result = await executor.click(params.get("selector", ""))
        elif action == "fill":
            result = await executor.fill(params.get("selector", ""), params.get("value", ""))
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
        
        return {
            "success": result.success,
            "output": result.output,
            "error": result.error,
            "screenshot": result.screenshot,
            "url": result.url,
            "title": result.title
        }
    finally:
        await executor.close()


if __name__ == "__main__":
    # Test the browser executor
    async def test():
        executor = BrowserExecutor(BrowserConfig(headless=False))
        if await executor.initialize():
            result = await executor.navigate("https://example.com")
            print(f"Navigate result: {result}")
            
            result = await executor.screenshot()
            print(f"Screenshot: {result.success}")
            
            result = await executor.extract("h1")
            print(f"Extract result: {result}")
            
            await executor.close()
    
    asyncio.run(test())