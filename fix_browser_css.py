import re

with open(r'D:\ELE\cli\src\widgets\browser_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the DEFAULT_CSS block with inline colors
new_css_block = '''    DEFAULT_CSS = """
    BrowserView {
        layout: vertical;
        height: 1fr;
        background: #ffffff;
        border: solid #1e88e5;
    }
    
    .browser-toolbar {
        height: 3;
        background: #f8f9fa;
        border-bottom: solid #e0e4ec;
        padding: 0 1;
    }

    .url-input {
        width: 100%;
        margin-right: 1;
    }

    .toolbar-btn {
        width: 8;
        height: 3;
    }

    .browser-viewport {
        height: 100%;
        background: #ffffff;
        border: none;
        overflow: hidden;
    }

    .viewport-content {
        height: 100%;
        width: 100%;
    }

    .browser-console {
        height: 10;
        background: #1a1a2e;
        border-top: solid #e0e4ec;
        padding: 0 1;
    }
    """'''

new_css_block = '''    DEFAULT_CSS = """
    BrowserView {
        layout: vertical;
        height: 1fr;
        background: #ffffff;
        border: solid #1e88e5;
    }
    
    .browser-toolbar {
        height: 3;
        background: #f8f9fa;
        border-bottom: solid #e0e4ec;
        padding: 0 1;
    }

    .url-input {
        width: 100%;
        margin-right: 1;
    }

    .toolbar-btn {
        width: 8;
        height: 3;
    }

    .browser-viewport {
        height: 100%;
        background: #ffffff;
        border: none;
        overflow: hidden;
    }

    .viewport-content {
        height: 100%;
        width: 100%;
    }

    .browser-console {
        height: 10;
        background: #1a1a2e;
        border-top: solid #e0e4ec;
        padding: 0 1;
    }
    """'''

import re
with open(r'D:\ELE\cli\src\widgets\browser_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the DEFAULT_CSS block
pattern = r'(    DEFAULT_CSS = """[\s\S]*?""")'
new_css_block = '''    DEFAULT_CSS = """
    BrowserView {
        layout: vertical;
        height: 1fr;
        background: #ffffff;
        border: solid #1e88e5;
    }
    
    .browser-toolbar {
        height: 3;
        background: #f8f9fa;
        border-bottom: solid #e0e4ec;
        padding: 0 1;
    }

    .url-input {
        width: 100%;
        margin-right: 1;
    }

    .toolbar-btn {
        width: 8;
        height: 3;
    }

    .browser-viewport {
        height: 100%;
        background: #ffffff;
        border: none;
        overflow: hidden;
    }

    .viewport-content {
        height: 100%;
        width: 100%;
    }

    .browser-console {
        height: 10;
        background: #1a1a2e;
        border-top: solid #e0e4ec;
        padding: 0 1;
    }
    """'''

new_content = re.sub(r'(    DEFAULT_CSS = """[\s\S]*?""")', 
                     '''    DEFAULT_CSS = """
    BrowserView {
        layout: vertical;
        height: 1fr;
        background: #ffffff;
        border: solid #1e88e5;
    }
    
    .browser-toolbar {
        height: 3;
        background: #f8f9fa;
        border-bottom: solid #e0e4ec;
        padding: 0 1;
    }

    .url-input {
        width: 100%;
        margin-right: 1;
    }

    .toolbar-btn {
        width: 8;
        height: 3;
    }

    .browser-viewport {
        height: 100%;
        background: #ffffff;
        border: none;
        overflow: hidden;
    }

    .viewport-content {
        height: 100%;
        width: 100%;
    }

    .browser-console {
        height: 10;
        background: #1a1a2e;
        border-top: solid #e0e4ec;
        padding: 0 1;
    }
    """''', 
                     content, flags=re.DOTALL)

with open(r'D:\ELE\cli\src\widgets\browser_view.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Done')