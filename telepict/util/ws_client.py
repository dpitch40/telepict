import json
import asyncio

import websockets

from ..config import Config

async def _websocket_send(game_id, player_id, payload, endpoint='game'):
    uri = f'ws://{Config.WS_HOST}:{Config.WS_PORT}/{endpoint}/{game_id}/{player_id}'
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(payload))
        await websocket.recv()

def websocket_send(game_id, player_id, payload, endpoint='game'):
    asyncio.run(_websocket_send(game_id, player_id, payload, endpoint))

def update_game(game_id):
    return websocket_send(game_id, 0, {'action': 'update'}, 'spectate')
