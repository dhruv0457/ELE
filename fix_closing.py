f = open(r'D:\ELE\cli\src\widgets\desktop_view.py', 'r', encoding='utf-8')
lines = f.readlines()
f.close()

# Add the closing triple quotes
lines.append('    """')

with open(r'D:\ELE\cli\src\widgets\desktop_view.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Done')