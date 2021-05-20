from flask import Blueprint, current_app, request, jsonify

from .auth import require_logged_in
from ..util.upload import handle_image

bp = Blueprint('image', __name__)

@bp.route('/img_upload', methods=['POST'])
@require_logged_in
def image_upload():
    game_id = int(request.form['game_id'])
    player_id = int(request.form['player_id'])
    with current_app.db.session_scope(expire_on_commit=False) as session:
        handle_image(session, request.files['file'], game_id, player_id)

    return jsonify({})
