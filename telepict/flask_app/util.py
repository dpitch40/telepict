import functools
import json
import asyncio

from flask import current_app, session as flask_session
import websockets

from ..db import Player

def get_current_player(session):
    if 'username' in flask_session:
        current_player = session.query(Player). \
            filter_by(name=flask_session['username']).one_or_none()
    else:
        current_player = None
    return current_player

def inject_current_player(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        with current_app.db.session_scope() as session:
            return func(session, get_current_player(session), *args, **kwargs)
    return wrapped

def websocket_send(game_id, player_id, payload):
    asyncio.run(_websocket_send(game_id, player_id, payload))

async def _websocket_send(game_id, player_id, payload):
    uri = f'ws://{current_app.config["WS_HOST"]}:{current_app.config["WS_PORT"]}/game/{game_id}/{player_id}'
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(payload))
        await websocket.recv()
