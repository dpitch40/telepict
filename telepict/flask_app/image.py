from flask import Blueprint, current_app, request, jsonify, abort, make_response

from ..db.models import Drawing
from .auth import require_logged_in
from ..util.upload import handle_image
from ..util.ws_client import update_game

bp = Blueprint('image', __name__)

@bp.route('/image/<int:image_id>')
@require_logged_in
def get_image(image_id):
    with current_app.db.session_scope() as session:
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
