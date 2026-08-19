with open(r'D:\ELE\cli\src\widgets\desktop_view.py', 'r', encoding='utf-8') as f:
    source = f.read()

# Find the DEFAULT_CSS section
idx = source.find('DEFAULT_CSS')
if idx >= 0:
    start = source.find('"""', source.find('DEFAULT_CSS'))
    if start >= 0:
        end = source.find('"""', start + 3)
        print(f'CSS starts at {source.find("DEFAULT_CSS")}')
        print(f'First """ at {start}')
        print(f'End """ at {end}')
        print('CSS content:')
        print(repr(source[start:end+3]))
    else:
        print('No opening """ found')
else:
    print('DEFAULT_CSS not found')