#pylint: disable=no-member

import asyncio
import json
from collections import defaultdict

from .logging import logger
from ..db import Game, Player, Writing
from ..util import get_game_state_full, get_pending_stacks
from .handler import WebsocketHandler

class GameHandler(WebsocketHandler):
    endpoint = 'game'

    websockets_by_game = defaultdict(set)

    def register_websocket(self, websocket, game_id, player_id):
        super(GameHandler, self).register_websocket(websocket, game_id, player_id)

        self.websockets_by_game[game_id].add(websocket)
        print(f'join {game_id}: {player_id}')

    def deregister_websocket(self, websocket, game_id, player_id):
        super(GameHandler, self).deregister_websocket(websocket, game_id, player_id)

        self.websockets_by_game[game_id].discard(websocket)
        print(f'leave {game_id}: {player_id}')

    async def update(self, websocket, game_id, player_id):
        with self.db.session_scope(expire_on_commit=False) as session:
            game = session.query(Game).get(game_id)
            player = session.query(Player).get(player_id)
            state = get_game_state_full(game, player)
            print(f'Sending {state["state"]!s} to {player.name}')
        await websocket.send(json.dumps(state))

    async def update_all(self, game_id, _):
        aws = [self._update(ws) for ws in self.websockets_by_game[game_id]]
        await asyncio.gather(*aws)

    def handle_text(self, data, game_id, player_id):
        with self.db.session_scope(expire_on_commit=False) as session:
            game = session.query(Game).get(game_id)
            player = session.query(Player).get(player_id)
            pending_stacks = get_pending_stacks(game, player)
            if pending_stacks:
                stack = pending_stacks[0]
                if isinstance(stack.last, Writing):
                    logger.error('%s trying to add a writing to stack %d when '
                                 'it already ended with a writing', player.name, stack.id_)
                else:
                    writing = Writing(author=player, stack=stack, text=data.strip())
                    stack.writings.append(writing)
                    session.add(writing)
                    session.commit()
            else:
                logger.error('%s trying to add a drawing with no pending stacks', player.name)

    def handle_str(self, message, game_id, player_id):
        data = json.loads(message)
        if data['action'] == 'writing':
            self.handle_text(data['text'], game_id, player_id)
        elif data['action'] == 'update':
            # Don't do anything here, just update everyone
            pass
