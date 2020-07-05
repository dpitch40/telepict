import asyncio

from ..db import DB

ENDPOINT_HANDLERS = dict()

class HandlerMeta(type):
    endpoint = None

    def __init__(cls, *args, **kwargs):
        super(HandlerMeta, cls).__init__(*args, **kwargs)
        if cls.endpoint is not None:
            ENDPOINT_HANDLERS[cls.endpoint] = cls()

class WebsocketHandler(metaclass=HandlerMeta):
    endpoint = None

    def __init__(self):
        self.db = DB()
        self.socket_args = dict()

    def parse_args(self, *args):
        return args

    def register_websocket(self, websocket, *args):
        self.socket_args[websocket] = args

    def deregister_websocket(self, websocket, *args):
        self.socket_args.pop(websocket, None)

    async def update(self, websocket, *args):
        pass

    async def _update(self, websocket):
        await self.update(websocket, *self.socket_args[websocket])

    async def update_all(self, *args):
        aws = [self._update(ws) for ws in self.socket_args]
        await asyncio.gather(*aws)

    def handle_str(self, message, *args):
        pass

    def handle_bytes(self, message, *args):
        pass

    async def handle(self, websocket, *args):
        args = self.parse_args(*args)
        self.register_websocket(websocket, *args)
        try:
            await self._update(websocket)
            async for message in websocket:
                if isinstance(message, str):
                    self.handle_str(message, *args)
                else:
                    self.handle_bytes(message, *args)

                # Update all players
                await self.update_all(*args)
        finally:
            self.deregister_websocket(websocket, *args)


async def main_handler(websocket, path):
    endpoint, *args = path.strip('/').split('/')
    if endpoint in ENDPOINT_HANDLERS:
        await ENDPOINT_HANDLERS[endpoint].handle(websocket, *args)
