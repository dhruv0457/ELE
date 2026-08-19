import asyncio
import sys
sys.path.insert(0, '.')

from src import backend as be

async def test():
    print('Backend up:', be.is_backend_up())
    tok = be.login_or_register()
    print('Login OK:', tok['email'])
    async for evt in be.stream_chat('Say hello', tok['access_token']):
        if evt.get('type') in ('final', 'error'):
            content = evt.get('content', evt.get('message', ''))
            print(f'{evt.get("type")}: {content[:100]}')
            break

asyncio.run(test())