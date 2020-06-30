import secrets

from flask import Blueprint, render_template, request, current_app, flash, session as flask_session, \
    url_for
from db import Player
from auth import gen_password_hash, gen_password_hash_and_salt
from .exceptions import FlashedError
from .util import redirect_page

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        name, password = request.form['name'], request.form['password']
        with current_app.db.session_scope() as session:
            player = session.query(Player).filter_by(name=name).one_or_none()
            # TODO: Log failed login attempts
            if player is None:
                raise FlashedError('Bad username')
            player_hash = player.password_hash
            input_hash = gen_password_hash(password, player.password_salt)
            if not secrets.compare_digest(player_hash, input_hash):
                raise FlashedError('Bad password')
        flask_session['username'] = name
        return redirect_page('Login Successful',
                             'You have logged in successfully. Redirecting in {delay} seconds...',
                             url_for('index'))

@bp.route('/logout')
def logout():
    flask_session.pop('username', None)
    return redirect_page('Logout Successful',
                         'You have been logged out. Redirecting in {delay} seconds...',
                         url_for('index'))

@bp.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'GET':
        return render_template('create_account.html')
    else:
        name, dispname, password = request.form['name'], request.form['dispname'], \
            request.form['password']
        with current_app.db.session_scope() as session:
            player = session.query(Player).filter_by(name=name).one_or_none()
            if player is not None:
                raise FlashedError('Username already exists')
            player = Player(name=name, display_name=dispname, password=password)
            session.add(player)
            session.commit()
        flash(f'Account {name} created successfully!')
        return render_template('login.html')
