#!/usr/bin/env python

import asyncio

import websockets

from ..config import Config
from .handler import main_handler

def main():
    start_server = websockets.serve(main_handler, "0.0.0.0", Config.WS_PORT,
                                    max_size=Config.MAX_WS_MESSAGE_SIZE)
    print(f'Running on ws://0.0.0.0:{Config.WS_PORT}')

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    main()
