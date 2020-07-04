from telepict.db import Game, GamePlayerAssn, Player, Stack, Drawing, Writing, PendingGame
from telepict.auth import gen_password_hash

def test_games(test_session, david, nathan, elwood):
    games = test_session.query(Game).all()
    assert len(games) == 6

    game, long_game, unfinished_game, queue_game, reverse_game, draw_first_game = games
    assert game.num_rounds == 2
    assert long_game.num_rounds == 4
    assert unfinished_game.num_rounds == 2
    assert queue_game.num_rounds == reverse_game.num_rounds == draw_first_game.num_rounds == 1

    assert game.pass_left is True
    assert reverse_game.pass_left is False

    assert long_game.write_first is True
    assert draw_first_game.write_first is False

    assert [p.id_ for p in game.players] == [david.id_, nathan.id_, elwood.id_]
    assert [p.id_ for p in long_game.players] == [david.id_, nathan.id_]
    assert [p.id_ for p in unfinished_game.players] == [david.id_, elwood.id_, nathan.id_]

    assert game.complete
    assert long_game.complete
    assert not unfinished_game.complete
    assert not queue_game.complete
    assert not reverse_game.complete
    assert not draw_first_game.complete

    assert game.get_adjacent_player(david).id_ == nathan.id_
    assert game.get_adjacent_player(nathan).id_ == elwood.id_
    assert game.get_adjacent_player(david, False).id_ == elwood.id_

    assert long_game.get_adjacent_player(david).id_ == nathan.id_
    assert long_game.get_adjacent_player(nathan).id_ == david.id_
    assert long_game.get_adjacent_player(david, False).id_ == nathan.id_

    assert reverse_game.get_adjacent_player(david).id_ == elwood.id_
    assert reverse_game.get_adjacent_player(nathan).id_ == david.id_
    assert reverse_game.get_adjacent_player(david, False).id_ == nathan.id_

    assert all([len(g.players_) == len(g.stacks) for g in games])

def test_pending_games(test_session, david, nathan, elwood):
    games = test_session.query(PendingGame).all()
    assert len(games) == 4

    game1, game2, game3, game4 = games

    assert [p.id_ for p in game1.players] == [david.id_, nathan.id_, elwood.id_]
    assert [p.id_ for p in game2.players] == [david.id_, elwood.id_]
    assert [p.id_ for p in game3.players] == [nathan.id_, elwood.id_]
    assert [p.id_ for p in game4.players] == [david.id_]

    assert game1.pass_left is False
    assert game1.num_rounds == 1
    assert game1.write_first is True

    assert game2.pass_left is True
    assert game2.num_rounds == 3
    assert game2.write_first is False

    assert game3.pass_left is True
    assert game3.num_rounds == 5
    assert game3.write_first is False

    assert game4.pass_left is True
    assert game4.num_rounds == 7
    assert game4.write_first is True

def test_invitation(test_session, david, nathan, elwood):
    assert len(david.invitations) == 1
    assert len(nathan.invitations) == 1
    assert len(elwood.invitations) == 1

    inv = nathan.invitations[0]
    assert inv.recipient_id == nathan.id_
    assert inv.game_id == 2

    inv = david.invitations[0]
    assert inv.recipient_id == david.id_
    assert inv.game_id == 3

    inv = elwood.invitations[0]
    assert inv.recipient_id == elwood.id_
    assert inv.game_id == 4

def test_players(test_session, david, nathan, elwood):
    assert david.password_hash == gen_password_hash('12345678', david.password_salt)
    assert nathan.password_hash == gen_password_hash('you_shall_not_password', nathan.password_salt)
    assert elwood.password_hash == gen_password_hash('really good password', elwood.password_salt)

    assert len(david.games) == 6
    assert len(nathan.games) == 6
    assert len(elwood.games) == 5
    assert [g.id_ for g in david.games] == [1, 2, 3, 4, 5, 6]
    assert [g.id_ for g in elwood.games] == [1, 3, 4, 5, 6]

    assert len(david.pending_games) == 3
    assert len(nathan.pending_games) == 2
    assert len(elwood.pending_games) == 3
    assert [g.id_ for g in david.pending_games] == [1, 2, 4]
    assert [g.id_ for g in nathan.pending_games] == [1, 3]
    assert [g.id_ for g in elwood.pending_games] == [1, 2, 3]

def test_assn(test_session, david, nathan, elwood):
    assns = test_session.query(GamePlayerAssn).filter_by(game_id=1). \
        order_by(GamePlayerAssn.player_order).all()

    assert len(assns) == 3
    assert assns[0].player_order == 0
    assert assns[0].player_id == david.id_
    assert assns[1].player_order == 1
    assert assns[1].player_id == nathan.id_
    assert assns[2].player_order == 2
    assert assns[2].player_id == elwood.id_

    assns = test_session.query(GamePlayerAssn).filter_by(game_id=2). \
        order_by(GamePlayerAssn.player_order).all()

    assert len(assns) == 2
    assert assns[0].player_order == 0
    assert assns[0].player_id == david.id_
    assert assns[1].player_order == 1
    assert assns[1].player_id == nathan.id_

    assns = test_session.query(GamePlayerAssn).filter_by(game_id=3). \
        order_by(GamePlayerAssn.player_order).all()

    assert assns[0].player_order == 0
    assert assns[0].player_id == david.id_
    assert assns[1].player_order == 1
    assert assns[1].player_id == elwood.id_
    assert assns[2].player_order == 2
    assert assns[2].player_id == nathan.id_

def test_stacks(test_session, david, nathan, elwood):
    games = test_session.query(Game).all()

    for game in games:
        for player, stack in zip(game.players, game.stacks):
            assert player is stack.owner
            assert stack.game is game
            assert (len(stack.stack) == len(game.players_) * game.num_rounds) or not game.complete

    for game in games:
        for stack in game.stacks:
            for i, ent in enumerate(stack.stack):
                assert ent.stack_pos == i
                if game.write_first:
                    assert isinstance(ent, Drawing if (i % 2 != 0) else Writing)
                else:
                    assert isinstance(ent, Writing if (i % 2 != 0) else Drawing)
    game, long_game, unfinished_game = games[:3]
    david_stack_1, nathan_stack_1, elwood_stack_1 = game.stacks
    david_sstack_1, nathan_sstack_1, elwood_sstack_1 = [s.stack for s in game.stacks]
    assert david_sstack_1[0].author.id_ == david.id_
    assert david_sstack_1[1].author.id_ == nathan.id_
    assert david_sstack_1[2].author.id_ == elwood.id_
    assert david_sstack_1[0].text == 'Coming soon: yesterday'
