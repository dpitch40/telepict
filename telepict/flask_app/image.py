import io

from flask import Blueprint, current_app, request, jsonify
from PIL import Image

from .auth import require_logged_in
from ..config import Config
from ..util import get_pending_stacks
from ..util.image import flatten_rgba_image
from ..db import Game, Player, Drawing

bp = Blueprint('image', __name__)

@bp.route('/img_upload', methods=['POST'])
@require_logged_in
def image_upload():
    game_id = int(request.form['game_id'])
    player_id = int(request.form['player_id'])

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
                f = request.files['file']
                image = Image.open(f)
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
                stack.drawings.append(drawings)
                session.add(drawings)
                session.commit()
        else:
            current_app.logger.error('%s trying to add a drawing with no pending stacks',
                                     player.name)

    return jsonify({})
