#!/usr/bin/python3
import asyncio, sys
from bot import Portland

if __name__ == '__main__':
    # https://github.com/encode/httpx/issues/914#issuecomment-622586610
    if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    global config
    client = Portland()
