#!/usr/bin/env python

import asyncio

import websockets

from .logging import logger
from ..config import Config
from .handler import main_handler

def main():
    start_server = websockets.serve(main_handler, Config.WS_HOST, Config.WS_PORT,
                                    max_size=Config.MAX_WS_MESSAGE_SIZE)
    logger.info('Running on ws://%s:%s', Config.WS_HOST, Config.WS_PORT)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    main()
