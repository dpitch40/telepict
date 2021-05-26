#pylint: disable=no-member

import asyncio
import json
from collections import defaultdict

from ..db import Game, Player, Writing
from ..util.game import get_game_state_full, get_game_summary
from ..util.upload import handle_text
from .handler import WebsocketHandler

class GameHandler(WebsocketHandler):
    endpoints = ['game', 'spectate']

    websockets_by_game = defaultdict(set)

    def register_websocket(self, websocket, endpoint, game_id, player_id):
        super().register_websocket(websocket, endpoint, game_id, player_id)

        self.websockets_by_game[game_id].add(websocket)
        self.logger.debug(f'join game {game_id} ({endpoint}): player {player_id}')

    def deregister_websocket(self, websocket, game_id, player_id):
        super().deregister_websocket(websocket, game_id, player_id)

        self.websockets_by_game[game_id].discard(websocket)
        self.logger.debug(f'leave {game_id}: {player_id}')

    async def update(self, session, websocket, endpoint, game_id, player_id):
        game = session.query(Game).get(game_id)
        player = session.query(Player).get(player_id)
        if endpoint == 'game':
            state = await get_game_state_full(game, player)
        else:
            state = await get_game_state_full(game, None)
        self.logger.debug(f'Sending {state["state"]!s} to {player.name}')
        await websocket.send(json.dumps(state))

    async def update_all(self, session, game_id, _):
        game_summary = get_game_summary(session, game_id)
        self.logger.debug(game_summary)
        aws = [self._update(session, ws) for ws in self.websockets_by_game[game_id]]
        await asyncio.gather(*aws)

    def handle_str(self, session, message, game_id, player_id):
        try:
            data = json.loads(message)
        except json.decoder.JSONDecodeError as exc:
             self.logger.error('Could not decide JSON: %r', message)
        else:
            if data['action'] == 'writing':
                handle_text(session, data['text'], game_id, player_id)
            elif data['action'] == 'update':
                # Don't do anything here, just update everyone
                pass
