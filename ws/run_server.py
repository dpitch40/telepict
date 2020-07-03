#!/usr/bin/env python

# WS server that sends messages at random intervals

import asyncio
import datetime
import random
import json
import io
from collections import defaultdict

import websockets
import numpy as np
from PIL import Image

from config import Config, env
from db import DB, Game, Player, Writing, Drawing
from util import get_game_state, get_pending_stacks

db = DB()

players_by_game = defaultdict(set)
sockets_by_player = dict()

def handle_text(data, game_id, player_id):
    with db.session_scope(expire_on_commit=False) as session:
        game = session.query(Game).get(game_id)
        player = session.query(Player).get(player_id)
        pending_stacks = get_pending_stacks(game, player)
        if pending_stacks:
            stack = pending_stacks[0]
            writing = Writing(author=player, stack=stack, text=data.strip())
            stack.writings.append(writing)
            session.add(writing)
            session.commit()

def decompress_image(compressed_array):
    array = np.zeros((Config.CANVAS_HEIGHT, Config.CANVAS_WIDTH, 4), dtype=np.uint8)
    for x, y, r, g, b, a in compressed_array:
        array[y][x] = [r, g, b, a]
    return array

def handle_image(data, game_id, player_id):
    with db.session_scope(expire_on_commit=False) as session:
        game = session.query(Game).get(game_id)
        player = session.query(Player).get(player_id)
        pending_stacks = get_pending_stacks(game, player)

        compressed_array = np.frombuffer(data, dtype=np.uint16).reshape([-1, 6])
        array = decompress_image(compressed_array)
        image = Image.fromarray(array, mode='RGBA')
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])

        bio = io.BytesIO()
        background.save(bio, format='JPEG', quality=Config.JPEG_QUALITY)
        print(f'{len(bio.getvalue())} bytes')

        if pending_stacks:
            stack = pending_stacks[0]
            drawings = Drawing(author=player, stack=stack, drawing=bio.getvalue())
            stack.drawings.append(drawings)
            session.add(drawings)
            session.commit()

def join_game(websocket, game_id, player_id):
    players_by_game[game_id].add(player_id)
    sockets_by_player[player_id] = websocket
    print(f'join {game_id}: {player_id}')

def leave_game(game_id, player_id):
    players_by_game[game_id].discard(player_id)
    sockets_by_player.pop(player_id, None)
    print(f'leave {game_id}: {player_id}')

async def send_state(game_id, player_id):
    with db.session_scope(expire_on_commit=False) as session:
        game = session.query(Game).get(game_id)
        player = session.query(Player).get(player_id)
        state = get_game_state(game, player)
        # for stack in game.stacks:
        #     print(stack)
        print(f'Sending {state["state"]!s} to {player.name}')
    await sockets_by_player[player_id].send(json.dumps(state))

async def handler(websocket, path):
    # register(websocket) sends user_event() to websocket
    game_id, player_id = path.strip('/').split('/')
    game_id, player_id = int(game_id), int(player_id)
    join_game(websocket, game_id, player_id)
    try:
        await send_state(game_id, player_id)
        async for message in websocket:
            if isinstance(message, str):
                _, message = message.split(':', 1)
                # This check could probably be better
                handle_text(message, game_id, player_id)
            else:
                handle_image(message, game_id, player_id)
            # Update all players
            aws = [send_state(game_id, pid)
                   for pid in players_by_game[game_id]]
            await asyncio.gather(*aws)
    finally:
        leave_game(game_id, player_id)

def main():
    start_server = websockets.serve(handler, "localhost", Config.WS_PORT)
    print(f'Running on ws://localhost:{Config.WS_PORT}')

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    main()
