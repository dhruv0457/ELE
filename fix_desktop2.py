import re

with open(r'D:\ELE\cli\src\widgets\desktop_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The new CSS block as a raw string
new_css = r'''    DEFAULT_CSS = """
    DesktopView {
        layout: vertical;
        height: 1fr;
        background: #ffffff;
        border: solid #1e88e5;
    }
    
    .desktop-toolbar {
        height: 3;
        background: #f8f9fa;
        border-bottom: solid #e0e4ec;
        padding: 0 1;
    }
    
    .desktop-title {
        text-style: bold;
        color: #1e88e5;
        margin: 1 0;
    }
    
    .desktop-section {
        height: 1fr;
        layout: horizontal;
    }
    
    .desktop-sidebar {
        width: 32;
        background: #f8f9fa;
        border-right: solid #e0e4ec;
        padding: 1;
        height: 1fr;
        overflow-y: auto;
    }
    
    .desktop-main {
        width: 1fr;
        layout: vertical;
        height: 1fr;
        background: #ffffff;
    }
    
    .tool-group {
        margin: 1 0;
        padding: 1;
        border: solid #e0e4ec;
        background: #ffffff;
    }
    
    .tool-title {
        text-style: bold;
        color: #1e88e5;
        margin: 1 0;
    }
    
    .tool-btn {
        width: 1fr;
        margin: 0 0 1 0;
    }
    
    .desktop-main {
        width: 1fr;
        layout: vertical;
        height: 1fr;
        background: #ffffff;
    }
    
    #viewport {
        height: 1fr;
        background: #ffffff;
        border: solid #e0e4ec;
        margin: 1;
    }
    
    #input_bar {
        height: auto;
        min-height: 4;
        background: #f8f9fa;
        border-top: solid #e0e4ec;
        padding: 0 2;
    }
    
    .input-row {
        height: 3;
        align: center middle;
    }
    
    #input_area {
        background: #ffffff;
        border: solid #e0e4ec;
        height: 3;
        max-height: 6;
    }
    
    #input_area:focus {
        border: solid #1e88e5;
    }
    
    #voice_btn {
        background: transparent;
        color: #8a8aa0;
        border: none;
        width: 5;
        height: 3;
        content-align: center middle;
    }
    
    #voice_btn:hover {
        background: #e0e4ec;
        color: #1e88e5;
    }
    
    #voice_btn.-active {
        color: #ef4444;
    }
    
    #send_btn {
        background: #1e88e5;
        color: #ffffff;
        border: none;
        width: 12;
        height: 3;
    }
    
    #send_btn:hover {
        background: #1565c0;
    }
    
    #voice_btn {
        background: transparent;
        color: #8a8aa0;
        border: none;
        width: 5;
        height: 3;
        content-align: center middle;
    }
    
    #voice_btn:hover {
        background: #e0e4ec;
        color: #1e88e5;
    }
    
    #voice_btn.-active {
        color: #ef4444;
    }
    
    #send_btn {
        background: #1e88e5;
        color: #ffffff;
        border: none;
        width: 12;
        height: 3;
    }
    
    #send_btn:hover {
        background: #1565c0;
    }
    
    #status_line {
        color: #8a8aa0;
        text-style: dim;
        height: 1;
        padding: 0 2;
        background: #ffffff;
        border-bottom: solid #e0e4ec;
    }
"""

with open(r'D:\ELE\cli\src\widgets\desktop_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the DEFAULT_CSS block
import re
pattern = r'(    DEFAULT_CSS = """[\s\S]*?""")'
new_content = re.sub(r'(    DEFAULT_CSS = """[\s\S]*?""")', 
                     '''    DEFAULT_CSS = """
    DesktopView {
        layout: vertical;
        height: 1fr;
        background: #ffffff;
        border: solid #1e88e5;
    }
    
    .desktop-toolbar {
        height: 3;
        background: #f8f9fa;
        border-bottom: solid #e0e4ec;
        padding: 0 1;
    }
    
    .desktop-title {
        text-style: bold;
        color: #1e88e5;
        margin: 1 0;
    }
    
    .desktop-section {
        height: 1fr;
        layout: horizontal;
    }
    
    .desktop-sidebar {
        width: 32;
        background: #f8f9fa;
        border-right: solid #e0e4ec;
        padding: 1;
        height: 1fr;
        overflow-y: auto;
    }
    
    .desktop-main {
        width: 1fr;
        layout: vertical;
        height: 1fr;
        background: #ffffff;
    }
    
    .tool-group {
        margin: 1 0;
        padding: 1;
        border: solid #e0e4ec;
        background: #ffffff;
    }
    
    .tool-title {
        text-style: bold;
        color: #1e88e5;
        margin: 1 0;
    }
    
    .tool-btn {
        width: 1fr;
        margin: 0 0 1 0;
    }
    
    .desktop-main {
        width: 1fr;
        layout: vertical;
        height: 1fr;
        background: #ffffff;
    }
    
    #viewport {
        height: 1fr;
        background: #ffffff;
        border: solid #e0e4ec;
        margin: 1;
    }
    
    #input_bar {
        height: auto;
        min-height: 4;
        background: #f8f9fa;
        border-top: solid #e0e4ec;
        padding: 0 2;
    }
    
    .input-row {
        height: 3;
        align: center middle;
    }
    
    #input_area {
        background: #ffffff;
        border: solid #e0e4ec;
        height: 3;
        max-height: 6;
    }
    
    #input_area:focus {
        border: solid #1e88e5;
    }
    
    #voice_btn {
        background: transparent;
        color: #8a8aa0;
        border: none;
        width: 5;
        height: 3;
        content-align: center middle;
    }
    
    #voice_btn:hover {
        background: #e0e4ec;
        color: #1e88e5;
    }
    
    #voice_btn.-active {
        color: #ef4444;
    }
    
    #send_btn {
        background: #1e88e5;
        color: #ffffff;
        border: none;
        width: 12;
        height: 3;
    }
    
    #send_btn:hover {
        background: #1565c0;
    }
    
    #voice_btn {
        background: transparent;
        color: #8a8aa0;
        border: none;
        width: 5;
        height: 3;
        content-align: center middle;
    }
    
    #voice_btn:hover {
        background: #e0e4ec;
        color: #1e88e5;
    }
    
    #voice_btn.-active {
        color: #ef4444;
    }
    
    #send_btn {
        background: #1e88e5;
        color: #ffffff;
        border: none;
        width: 12;
        height: 3;
    }
    
    #send_btn:hover {
        background: #1565c0;
    }
    
    #status_line {
        color: #8a8aa0;
        text-style: dim;
        height: 1;
        padding: 0 2;
        background: #ffffff;
        border-bottom: solid #e0e4ec;
    }''', content, flags=re.DOTALL)

with open(r'D:\ELE\cli\src\widgets\desktop_view.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Done')