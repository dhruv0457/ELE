with open(r'D:\ELE\cli\src\widgets\desktop_view.py', 'rb') as f:
    content = f.read()

# Find the DEFAULT_CSS section
idx = content.find(b'DEFAULT_CSS')
if idx >= 0:
    start = content.find(b'"""', content.find(b'DEFAULT_CSS'))
    print(f'First """ at {start}')
    # Find the next """
    idx2 = content.find(b'"""', start + 3)
    if idx2 >= 0:
        print(f'First close at {idx2}')
        print(f'CSS content length: {idx2 - start - 3}')
        print(repr(content[start:idx2+3]))
    else:
        print('No closing """ found')
        # Show what comes after
        print(repr(content[start:start+200]))
else:
    print('DEFAULT_CSS not found')