"""Desktop Automation Executor - System-level mouse, keyboard, screen control"""
import os
import asyncio
import base64
import io
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import structlog

logger = structlog.get_logger()

try:
    import pyautogui
    import pygetwindow as gw
    PYGUI_AVAILABLE = True
except ImportError:
    PYGUI_AVAILABLE = False
    logger.warning("pyautogui/pygetwindow not available")

try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False

try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


@dataclass
class DesktopConfig:
    """Desktop automation configuration"""
    mouse_speed: float = 1.0
    click_delay: float = 0.1
    type_interval: float = 0.05
    confirm_sensitive: bool = True
    screenshot_quality: int = 80
    ocr_enabled: bool = True


@dataclass
class DesktopResult:
    success: bool
    output: Any = None
    error: Optional[str] = None
    screenshot: Optional[str] = None
    coordinates: Optional[Tuple[int, int]] = None


class WindowManager:
    """Window management utilities"""
    
    @staticmethod
    def get_all_windows() -> List[Dict[str, Any]]:
        """Get all visible windows"""
        if not PYGUI_AVAILABLE:
            return []
        
        windows = []
        try:
            for win in gw.getAllWindows():
                if win.visible and win.title:
                    windows.append({
                        "title": win.title,
                        "handle": win._hWnd if hasattr(win, '_hWnd') else None,
                        "left": win.left,
                        "top": win.top,
                        "width": win.width,
                        "height": win.height,
                        "active": win.isActive
                    })
        except Exception as e:
            logger.warning("Failed to get windows", error=str(e))
        return windows
    
    @staticmethod
    def find_window(title: str) -> Optional[object]:
        """Find window by title (partial match)"""
        if not PYGUI_AVAILABLE:
            return None
        try:
            windows = gw.getWindowsWithTitle(title)
            return windows[0] if windows else None
        except Exception:
            return None
    
    @staticmethod
    def focus_window(window) -> bool:
        """Bring window to front and focus"""
        try:
            if hasattr(window, 'activate'):
                window.activate()
            elif hasattr(window, 'restore'):
                window.restore()
                window.activate()
            return True
        except Exception as e:
            logger.error("Failed to focus window", error=str(e))
            return False


class ScreenCapture:
    """Screen capture and OCR"""
    
    def __init__(self, config: DesktopConfig):
        self.config = config
        self.sct = mss.mss() if MSS_AVAILABLE else None
    
    async def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> DesktopResult:
        """Capture screenshot"""
        if not self.sct:
            return DesktopResult(success=False, error="mss not available")
        
        try:
            if region:
                monitor = {"left": region[0], "top": region[1], 
                          "width": region[2], "height": region[3]}
                screenshot = self.sct.grab(monitor)
            else:
                screenshot = self.sct.grab(self.sct.monitors[0])
            
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format="PNG", quality=self.config.screenshot_quality)
            img_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return DesktopResult(
                success=True,
                output="Screenshot captured",
                screenshot=img_b64
            )
        except Exception as e:
            logger.error("Screenshot failed", error=str(e))
            return DesktopResult(success=False, error=str(e))
    
    async def capture_region(self, x: int, y: int, width: int, height: int) -> DesktopResult:
        """Capture specific region"""
        return await self.capture_screen((x, y, width, height))
    
    async def get_text_at(self, x: int, y: int, radius: int = 50) -> DesktopResult:
        """OCR text around coordinates"""
        if not OCR_AVAILABLE or not self.config.ocr_enabled:
            return DesktopResult(success=False, error="OCR not available")
        
        try:
            result = await self.capture_region(x - radius, y - radius, radius * 2, radius * 2)
            if not result.success:
                return result
            
            img_data = base64.b64decode(result.screenshot)
            img = Image.open(io.BytesIO(img_data))
            text = pytesseract.image_to_string(img)
            
            return DesktopResult(success=True, output=text.strip())
        except Exception as e:
            logger.error("OCR failed", error=str(e))
            return DesktopResult(success=False, error=str(e))


class InputController:
    """Mouse and keyboard control"""
    
    def __init__(self, config: DesktopConfig):
        self.config = config
        if PYGUI_AVAILABLE:
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = config.click_delay
    
    async def move_to(self, x: int, y: int, duration: float = None) -> DesktopResult:
        """Move mouse to coordinates"""
        if not PYGUI_AVAILABLE:
            return DesktopResult(success=False, error="pyautogui not available")
        
        try:
            dur = duration or (0.5 / self.config.mouse_speed)
            pyautogui.moveTo(x, y, duration=dur)
            return DesktopResult(success=True, output=f"Moved to ({x}, {y})", coordinates=(x, y))
        except Exception as e:
            return DesktopResult(success=False, error=str(e))
    
    async def click(self, x: int = None, y: int = None, button: str = "left", 
                    clicks: int = 1, interval: float = None) -> DesktopResult:
        """Click at coordinates"""
        if not PYGUI_AVAILABLE:
            return DesktopResult(success=False, error="pyautogui not available")
        
        try:
            if x is not None and y is not None:
                await self.move_to(x, y)
            
            interval = interval or self.config.click_delay
            pyautogui.click(x=x, y=y, button=button, clicks=clicks, interval=interval)
            
            return DesktopResult(success=True, output=f"Clicked {button} at ({x}, {y})")
        except Exception as e:
            return DesktopResult(success=False, error=str(e))
    
    async def double_click(self, x: int = None, y: int = None) -> DesktopResult:
        return await self.click(x, y, clicks=2)
    
    async def right_click(self, x: int = None, y: int = None) -> DesktopResult:
        return await self.click(x, y, button="right")
    
    async def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, 
                   duration: float = 1.0) -> DesktopResult:
        """Drag from start to end"""
        if not PYGUI_AVAILABLE:
            return DesktopResult(success=False, error="pyautogui not available")
        
        try:
            await self.move_to(start_x, start_y)
            pyautogui.dragTo(end_x, end_y, duration=duration, button='left')
            return DesktopResult(success=True, output=f"Dragged from ({start_x},{start_y}) to ({end_x},{end_y})")
        except Exception as e:
            return DesktopResult(success=False, error=str(e))
    
    async def type_text(self, text: str, interval: float = None) -> DesktopResult:
        """Type text"""
        if not PYGUI_AVAILABLE:
            return DesktopResult(success=False, error="pyautogui not available")
        
        try:
            interval = interval or self.config.type_interval
            pyautogui.write(text, interval=interval)
            return DesktopResult(success=True, output=f"Typed {len(text)} characters")
        except Exception as e:
            return DesktopResult(success=False, error=str(e))
    
    async def press_key(self, key: str, presses: int = 1, interval: float = 0.1) -> DesktopResult:
        """Press a key"""
        if not PYGUI_AVAILABLE:
            return DesktopResult(success=False, error="pyautogui not available")
        
        try:
            for _ in range(presses):
                pyautogui.press(key)
                await asyncio.sleep(interval)
            return DesktopResult(success=True, output=f"Pressed {key} {presses}x")
        except Exception as e:
            return DesktopResult(success=False, error=str(e))
    
    async def hotkey(self, *keys) -> DesktopResult:
        """Press key combination (e.g., 'ctrl', 'c')"""
        if not PYGUI_AVAILABLE:
            return DesktopResult(success=False, error="pyautogui not available")
        
        try:
            pyautogui.hotkey(*keys)
            return DesktopResult(success=True, output=f"Hotkey: {'+'.join(keys)}")
        except Exception as e:
            return DesktopResult(success=False, error=str(e))
    
    async def scroll(self, clicks: int = 3, x: int = None, y: int = None) -> DesktopResult:
        """Scroll mouse wheel"""
        if not PYGUI_AVAILABLE:
            return DesktopResult(success=False, error="pyautogui not available")
        
        try:
            if x is not None and y is not None:
                await self.move_to(x, y)
            pyautogui.scroll(clicks)
            return DesktopResult(success=True, output=f"Scrolled {clicks} clicks")
        except Exception as e:
            return DesktopResult(success=False, error=str(e))


class AppController:
    """Application control"""
    
    def __init__(self, config: DesktopConfig):
        self.config = config
    
    async def launch(self, app: str, args: List[str] = None) -> DesktopResult:
        """Launch application"""
        try:
            if os.name == 'nt':
                cmd = [app] + (args or [])
                proc = await asyncio.create_subprocess_exec(*cmd)
            else:
                cmd = [app] + (args or [])
                proc = await asyncio.create_subprocess_exec(*cmd)
            
            return DesktopResult(success=True, output=f"Launched {app}", coordinates=(proc.pid,))
        except Exception as e:
            return DesktopResult(success=False, error=str(e))
    
    async def focus(self, title: str) -> DesktopResult:
        """Focus window by title"""
        if not PYGUI_AVAILABLE:
            return DesktopResult(success=False, error="pygetwindow not available")
        
        win = WindowManager.find_window(title)
        if not win:
            return DesktopResult(success=False, error=f"Window not found: {title}")
        
        if WindowManager.focus_window(win):
            return DesktopResult(success=True, output=f"Focused: {title}")
        return DesktopResult(success=False, error="Failed to focus")
    
    async def close(self, title: str) -> DesktopResult:
        """Close window by title"""
        if not PYGUI_AVAILABLE:
            return DesktopResult(success=False, error="pygetwindow not available")
        
        win = WindowManager.find_window(title)
        if not win:
            return DesktopResult(success=False, error=f"Window not found: {title}")
        
        try:
            win.close()
            return DesktopResult(success=True, output=f"Closed: {title}")
        except Exception as e:
            return DesktopResult(success=False, error=str(e))
    
    async def get_window_info(self, title: str = None) -> DesktopResult:
        """Get window information"""
        windows = WindowManager.get_all_windows()
        if title:
            windows = [w for w in windows if title.lower() in w["title"].lower()]
        return DesktopResult(success=True, output=windows)


class DesktopExecutor:
    """Unified desktop automation executor"""
    
    def __init__(self, config: DesktopConfig = None):
        self.config = config or DesktopConfig()
        self.window_manager = WindowManager()
        self.screen_capture = ScreenCapture(self.config)
        self.input = InputController(self.config)
        self.app_control = AppController(self.config)
        self._initialized = False
    
    async def initialize(self):
        """Initialize desktop automation"""
        if not PYGUI_AVAILABLE:
            logger.warning("pyautogui not available, desktop automation limited")
        else:
            self._initialized = True
            logger.info("Desktop automation initialized")
    
    async def execute(self, action: str, params: Dict[str, Any]) -> DesktopResult:
        """Execute desktop action"""
        if not self._initialized:
            await self.initialize()
        
        try:
            if action == "move_mouse":
                return await self.input.move_to(params.get("x", 0), params.get("y", 0))
            elif action == "click":
                return await self.input.click(params.get("x"), params.get("y"), 
                                             params.get("button", "left"), 
                                             params.get("clicks", 1))
            elif action == "double_click":
                return await self.input.double_click(params.get("x"), params.get("y"))
            elif action == "right_click":
                return await self.input.right_click(params.get("x"), params.get("y"))
            elif action == "drag":
                return await self.input.drag(params["start_x"], params["start_y"], 
                                             params["end_x"], params["end_y"],
                                             params.get("duration", 1.0))
            elif action in ("type", "type_text"):
                return await self.input.type_text(params["text"])
            elif action == "press_key":
                return await self.input.press_key(params["key"], params.get("presses", 1))
            elif action == "hotkey":
                return await self.input.hotkey(*params["keys"])
            elif action == "scroll":
                return await self.input.scroll(params.get("clicks", 3), params.get("x"), params.get("y"))
            elif action == "screenshot":
                return await self.screen_capture.capture_screen()
            elif action == "screenshot_region":
                return await self.screen_capture.capture_region(params["x"], params["y"], 
                                                                params["width"], params["height"])
            elif action == "ocr":
                return await self.screen_capture.get_text_at(params["x"], params["y"], 
                                                             params.get("radius", 50))
            elif action == "launch_app":
                app_name = params.get("app") or params.get("name")
                return await self.app_control.launch(app_name, params.get("args", []))
            elif action == "focus_window":
                return await self.app_control.focus(params["title"])
            elif action == "close_window":
                return await self.app_control.close(params["title"])
            elif action == "list_windows":
                return await self.app_control.get_window_info()
            elif action == "get_window_info":
                return await self.app_control.get_window_info(params.get("title"))
            elif action == "ocr_region":
                return await self.screen_capture.get_text_at(params["x"], params["y"], 
                                                              params.get("radius", 50))
            elif action == "capture_region":
                return await self.screen_capture.capture_region(params["x"], params["y"],
                                                                params["width"], params["height"])
            elif action == "click_at":
                return await self.input.click(params["x"], params["y"])
            elif action == "drag_drop":
                return await self.input.drag(params["start_x"], params["start_y"], 
                                             params["end_x"], params["end_y"],
                                             params.get("duration", 1.0))
            else:
                return DesktopResult(success=False, error=f"Unknown action: {action}")
        except Exception as e:
            logger.error(f"Desktop action failed: {action}", error=str(e))
            return DesktopResult(success=False, error=str(e))


# Register desktop executor in registry
async def get_desktop_executor(config: DesktopConfig = None) -> DesktopExecutor:
    executor = DesktopExecutor(config)
    await executor.initialize()
    return executor