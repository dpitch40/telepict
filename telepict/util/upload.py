"""Defines backend for handling uploads of text and images.
"""

import logging

from flask import current_app, abort

from .game import get_pending_stacks
from .image import convert_image
from ..db import Game, Player, Writing, Drawing, Pass

logger = logging.getLogger('Telepict.upload')

def add_to_stack(session, stack, item):
    session.add(item)

    # Add passes until the next player is still in the game, or the stack is complete
    game = stack.game
    target_len = game.target_len
    if len(stack) <= target_len:
        for player_assn in game.player_assns_after(item.author):
            if not player_assn.left_game:
                break

            # Player has left the game, add a pass
            pass_ = Pass(author=player_assn.player, stack=stack)
            stack.passes.append(stack, pass_)
            session.add(pass_)

            if len(stack) == target_len:
                break

def handle_text(session, data, game_id, player_id):
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
            add_to_stack(session, stack, writing)
            session.commit()
    else:
        logger.error('%s trying to add a writing with no pending stacks', player.name)

def handle_image(session, img_file, game_id, player_id):
    game = session.query(Game).get(game_id)
    player = session.query(Player).get(player_id)
    pending_stacks = get_pending_stacks(game, player)

    if pending_stacks:
        stack = pending_stacks[0]
        if isinstance(stack.last, Drawing):
            logger.error('%s trying to add a drawing to stack %d when '
                         'it already ended with a drawing', player.name, stack.id_)
        else:
            try:
                image_bytes = convert_image(img_file)
            except ValueError as exc:
                abort(str(exc), 400)
            drawing = Drawing(author=player, stack=stack, drawing=image_bytes)
            add_to_stack(session, stack, drawing)
            session.commit()
            drawing.save_image()
    else:
        logger.error('%s trying to add a drawing with no pending stacks',
                     player.name)

def handle_pass(session, game, player):
    pending_stacks = get_pending_stacks(game, player)
    if pending_stacks:
        stack = pending_stacks[0]
        pass_ = Pass(author=player, stack=stack)
        add_to_stack(session, stack, pass_)
    else:
        logger.error('%s trying to pass with no pending stacks', player.name)
