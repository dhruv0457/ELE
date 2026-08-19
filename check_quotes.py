with open(r'D:\ELE\cli\src\widgets\desktop_view.py', 'rb') as f:
    content = f.read()
import re
matches = list(re.finditer(b'"""', content))
print(f'Total triple quotes: {len(matches)}')
for m in matches:
    print(f'  Position {m.start()}: {content[m.start():m.start()+30]}')