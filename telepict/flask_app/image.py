from flask import Blueprint, current_app, request, jsonify, abort, make_response
from cryptography.fernet import InvalidToken

from ..db.models import Drawing, Game
from .auth import require_logged_in
from .util import decrypt_with_secret_key
from ..util.upload import handle_image
from ..util.ws_client import update_game

bp = Blueprint('image', __name__)

@bp.route('/image/<encrypted_game_id>/<int:image_id>')
def get_image(encrypted_game_id, image_id):
    with current_app.db.session_scope() as session:
        # Require encrypted game ID for security
        try:
            game_id = int(decrypt_with_secret_key(encrypted_game_id).decode('utf8'))
        except InvalidToken:
            abort(404)
        game = session.query(Game).get(game_id)
        if game is None:
            abort(404)

        drawing = session.query(Drawing).get(image_id)
        if drawing is None:
            abort(404)
        else:
            response = make_response(drawing.drawing)
            response.headers['Content-Type'] = 'image/jpeg'
            return response


@bp.route('/img_upload', methods=['POST'])
@require_logged_in
def image_upload():
    game_id = int(request.form['game_id'])
    player_id = int(request.form['player_id'])
    with current_app.db.session_scope(expire_on_commit=False) as session:
        handle_image(session, request.files['file'], game_id, player_id)

    update_game(game_id)

    return '', 204
