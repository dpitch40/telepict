#!/usr/bin/env python

import asyncio
from ssl import SSLContext

import websockets

from .logging import main_logger
from ..config import Config
from .handler import main_handler

def main():
    image_backend = Config.IMAGE_BACKEND.get_instance(**Config.IMAGE_BACKEND_KWARGS)
    kwargs = dict()
    protocol = 'ws'
    if Config.WS_CERTFILE is not None and Config.WS_KEYFILE is not None:
        main_logger.info('Setting up SSL: %s, %s', Config.WS_CERTFILE, Config.WS_KEYFILE)
        ssl = SSLContext()
        ssl.load_cert_chain(Config.WS_CERTFILE, Config.WS_KEYFILE)
        kwargs['ssl'] = ssl
        protocol = 'wss'
    start_server = websockets.serve(main_handler, Config.WS_HOST, Config.WS_PORT,
                                    max_size=Config.MAX_WS_MESSAGE_SIZE, **kwargs)
    main_logger.info('Started (%s); running on %s://%s:%s', Config.TELEPICT_ENV,
        protocol, Config.WS_HOST, Config.WS_PORT)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    main()
