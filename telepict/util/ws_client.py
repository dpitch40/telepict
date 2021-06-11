import json
import asyncio
import pprint

import websockets
import websockets.exceptions
from flask import current_app

from ..config import Config

async def _websocket_send(game_id, player_id, payload, endpoint='game'):
    uri = f'ws://{Config.WS_HOST}:{Config.WS_PORT}/{endpoint}/{game_id}/{player_id}'
    try:
        async with websockets.connect(uri, max_size=Config.MAX_WS_MESSAGE_SIZE) as websocket:
            await websocket.recv()
            await websocket.send(json.dumps(payload))
            await websocket.recv()
    except websockets.exceptions.WebSocketException as exc:
        current_app.logger.error("Error occurred sending payload %r to %s", payload, uri, exc_info=exc)

def websocket_send(game_id, player_id, payload, endpoint='game'):
    asyncio.run(_websocket_send(game_id, player_id, payload, endpoint))

def update_game(game_id):
    return websocket_send(game_id, 0, {'action': 'update'}, 'spectate')
