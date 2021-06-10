import asyncio
import logging
import traceback

import websockets.exceptions

from ..db import DB
from ..config import Config

ENDPOINT_HANDLERS = dict()

class HandlerMeta(type):
    endpoints = None

    def __init__(cls, *args, **kwargs):
        super(HandlerMeta, cls).__init__(*args, **kwargs)
        if cls.endpoints is not None:
            inst = cls()
            for endpoint in cls.endpoints:
                ENDPOINT_HANDLERS[endpoint] = inst

class WebsocketHandler(metaclass=HandlerMeta):
    endpoints = None

    def __init__(self):
        self.db = DB()
        self.socket_args = dict()
        self.logger = logging.getLogger(','.join(self.endpoints))
        self.logger.setLevel(Config.LOG_LEVEL)

    def parse_args(self, *args): # pylint: disable=no-self-use
        return args

    def register_websocket(self, websocket, *args):
        self.socket_args[websocket] = args

    def deregister_websocket(self, websocket, *args): # pylint: disable=unused-argument
        self.socket_args.pop(websocket, None)

    async def update(self, session, websocket, *args):
        pass

    async def _update(self, session, websocket):
        await self.update(session, websocket, *self.socket_args[websocket])

    async def update_all(self, session, *args): # pylint: disable=unused-argument
        aws = [self._update(session, ws) for ws in self.socket_args]
        await asyncio.gather(*aws)

    def handle_str(self, session, message, *args):
        pass

    def handle_bytes(self, session, message, *args):
        pass

    async def handle(self, websocket, endpoint, *args):
        args = self.parse_args(*args)
        self.register_websocket(websocket, endpoint, *args)
        try:
            with self.db.session_scope(expire_on_commit=False) as session:
                await self._update(session, websocket)
            try:
                async for message in websocket:
                    self.logger.debug('Handling message: %r', message)
                    with self.db.session_scope(expire_on_commit=False) as session:
                        if isinstance(message, str):
                            self.handle_str(session, message, *args)
                        else:
                            self.handle_bytes(session, message, *args)

                        # Update all players
                        await self.update_all(session, *args)
            except websockets.exceptions.ConnectionClosedError as exc:
                self.logger.warning('Error receiving message from websocket %r', websocket)
        finally:
            self.deregister_websocket(websocket, *args)


async def main_handler(websocket, path):
    endpoint, *args = path.strip('/').split('/')
    if endpoint in ENDPOINT_HANDLERS:
        await ENDPOINT_HANDLERS[endpoint].handle(websocket, endpoint, *args)
