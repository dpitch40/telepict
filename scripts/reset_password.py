import argparse

from telepict.db import DB, Player
from telepict.auth import gen_password_hash

db = DB()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('username', help='The username to the account to modify')
    parser.add_argument('password', help='The new password to set')
    args = parser.parse_args()

    name = args.username
    new_password = args.password

    with db.session_scope() as session:
        player = session.query(Player).filter_by(name=name).one_or_none()
        if not player:
            print(f'No player named {name!r}')
        else:
            player.password_hash = gen_password_hash(new_password, player.password_salt)
        session.commit()
        print(f'Password for player {name} updated')

