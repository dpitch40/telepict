#!/usr/bin/env python

import asyncio

import websockets

from .logging import main_logger
from ..config import Config
from .handler import main_handler

def main():
    image_backend = Config.IMAGE_BACKEND.get_instance(**Config.IMAGE_BACKEND_KWARGS)
    start_server = websockets.serve(main_handler, Config.WS_HOST, Config.WS_PORT,
                                    max_size=Config.MAX_WS_MESSAGE_SIZE)
    main_logger.info('Running on ws://%s:%s', Config.WS_HOST, Config.WS_PORT)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    main()
