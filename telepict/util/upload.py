"""Defines backend for handling uploads of text and images.
"""

import io

from flask import current_app
from PIL import Image

from . import get_pending_stacks
from .image import flatten_rgba_image
from ..config import Config
from ..db.models import Game, Player, Writing, Drawing, Pass

def add_to_stack(stack, item):
    if isinstance(item, Writing):
        stack.writings.append(item)
    elif isinstance(item, Drawing):
        stack.drawings.append(item)
    session.add(item)

    # Add passes until the next player is still in the game, or the stack is complete
    game = stack.game
    target_len = game.target_len
    if len(stack) <= target_len:
        for player_assn in game.players_assns_after(item.author):
            if not player_assn.left_game:
                break

            # Player has left the game, add a pass
            pass_ = Pass(author=player_assn.player, stack=stack)
            stack.passes.append(stack, pass_)
            session.add(pass_)

            if len(stack) == target_len:
                break

def handle_text(data, game_id, player_id):
    with current_app.db.session_scope(expire_on_commit=False) as session:
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
                add_to_stack(stack, writing)
                session.commit()
        else:
            logger.error('%s trying to add a drawing with no pending stacks', player.name)

def handle_image(img_file, game_id, player_id):
    with current_app.db.session_scope() as session:
        game = session.query(Game).get(game_id)
        player = session.query(Player).get(player_id)
        pending_stacks = get_pending_stacks(game, player)

        if pending_stacks:
            stack = pending_stacks[0]
            if isinstance(stack.last, Drawing):
                current_app.logger.error('%s trying to add a drawing to stack %d when '
                                         'it already ended with a drawing', player.name, stack.id_)
            else:
                image = Image.open(img_file)
                if image.mode == 'RGBA':
                    image = flatten_rgba_image(image)
                # Scale image if necessary
                width_factor = image.size[0] / current_app.config['MAX_IMAGE_WIDTH']
                height_factor = image.size[1] / current_app.config['MAX_IMAGE_HEIGHT']
                max_factor = max(height_factor, width_factor)
                if max_factor > 1:
                    target_size = (int(image.size[0] // max_factor),
                                   int(image.size[1] // max_factor))
                    image = image.resize(target_size)

                bio = io.BytesIO()
                image.save(bio, format='JPEG', quality=Config.JPEG_QUALITY)

                drawings = Drawing(author=player, stack=stack, drawing=bio.getvalue())
                add_to_stack(stack, drawing)
                session.commit()
        else:
            current_app.logger.error('%s trying to add a drawing with no pending stacks',
                                     player.name)

def handle_pass(game, player):
    pending_stacks = get_pending_stacks(game, player)
    if pending_stacks:
        stack = pending_stacks[0]
        else:
            pass_ = Pass(author=player, stack=stack)
            add_to_stack(stack, pass_)
    else:
        logger.error('%s trying to pass with no pending stacks', player.name)
