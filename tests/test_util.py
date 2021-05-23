import pytest

from telepict.util.game import get_pending_stacks, get_game_state, serialize_stack, get_game_overview
from telepict.db import Game, Player, Writing, Drawing, Stack

def test_get_pending_stacks(test_session, david, nathan, elwood):
    # Unfinished game
    unfinished_game = test_session.query(Game).get(3)

    david_pending_stacks = get_pending_stacks(unfinished_game, david)
    nathan_pending_stacks = get_pending_stacks(unfinished_game, nathan)
    elwood_pending_stacks = get_pending_stacks(unfinished_game, elwood)
    assert len(david_pending_stacks) == 1
    assert len(nathan_pending_stacks) == 1
    assert len(elwood_pending_stacks) == 1

    assert david_pending_stacks[0].owner_id == nathan.id_
    assert elwood_pending_stacks[0].owner_id == david.id_
    assert nathan_pending_stacks[0].owner_id == elwood.id_

    # Elwood has a queue game
    queue_game = test_session.query(Game).get(4)

    david_pending_stacks = get_pending_stacks(queue_game, david)
    nathan_pending_stacks = get_pending_stacks(queue_game, nathan)
    elwood_pending_stacks = get_pending_stacks(queue_game, elwood)
    assert len(david_pending_stacks) == 1
    assert len(nathan_pending_stacks) == 0
    assert len(elwood_pending_stacks) == 2

    assert david_pending_stacks[0].owner_id == elwood.id_
    assert elwood_pending_stacks[0].owner_id == nathan.id_
    assert elwood_pending_stacks[1].owner_id == david.id_

    # Reverse game
    reverse_game = test_session.query(Game).get(5)

    david_pending_stacks = get_pending_stacks(reverse_game, david)
    nathan_pending_stacks = get_pending_stacks(reverse_game, nathan)
    elwood_pending_stacks = get_pending_stacks(reverse_game, elwood)
    assert len(david_pending_stacks) == 1
    assert len(nathan_pending_stacks) == 1
    assert len(elwood_pending_stacks) == 1

    assert david_pending_stacks[0].owner_id == nathan.id_
    assert elwood_pending_stacks[0].owner_id == david.id_
    assert nathan_pending_stacks[0].owner_id == elwood.id_

    # Draw first game
    drawfirst_game = test_session.query(Game).get(6)

    david_pending_stacks = get_pending_stacks(drawfirst_game, david)
    nathan_pending_stacks = get_pending_stacks(drawfirst_game, nathan)
    elwood_pending_stacks = get_pending_stacks(drawfirst_game, elwood)
    assert len(david_pending_stacks) == 2
    assert len(nathan_pending_stacks) == 1
    assert len(elwood_pending_stacks) == 0

    assert david_pending_stacks[0].owner_id == david.id_
    assert david_pending_stacks[1].owner_id == elwood.id_
    assert nathan_pending_stacks[0].owner_id == nathan.id_

    # Partially done game
    partially_done_game = test_session.query(Game).get(7)

    david_pending_stacks = get_pending_stacks(partially_done_game, david)
    nathan_pending_stacks = get_pending_stacks(partially_done_game, nathan)
    elwood_pending_stacks = get_pending_stacks(partially_done_game, elwood)
    assert len(david_pending_stacks) == 1
    assert len(nathan_pending_stacks) == 2
    assert len(elwood_pending_stacks) == 0

    assert david_pending_stacks[0].owner_id == david.id_
    assert nathan_pending_stacks[0].owner_id == elwood.id_
    assert nathan_pending_stacks[1].owner_id == nathan.id_

def test_serialize_stacks(test_session, david, nathan, elwood):
    partially_done_game = test_session.query(Game).get(7)
    david_pending_stacks = get_pending_stacks(partially_done_game, david)
    nathan_pending_stacks = get_pending_stacks(partially_done_game, nathan)

    david_stack = david_pending_stacks[0]
    elwood_stack = nathan_pending_stacks[0]
    nathan_stack = nathan_pending_stacks[1]

    assert serialize_stack(david_stack) == \
        {'owner': 'DarthMarth',
         'pages': [{'author': 'DarthMarth',
                    'type': 'Writing',
                    'content': 'Coming soon: yesterday'},
                   {'author': 'humcalc',
                    'type': 'Drawing',
                    'content': david_stack.drawings[0].data_url},
                   {'author': 'Kalen',
                    'type': 'Writing',
                    'content': 'Passing an hour on the fourth Monday.'}]}
    assert serialize_stack(nathan_stack) == \
        {'owner': 'humcalc',
         'pages': [{'author': 'humcalc',
                    'type': 'Writing',
                    'content': "Ender's Game"},
                   {'author': 'Kalen',
                    'type': 'Drawing',
                    'content': nathan_stack.drawings[0].data_url},
                   {'author': 'DarthMarth',
                    'type': 'Writing',
                    'content': 'Be kind, bake your VHS tapes at 400 degrees for '
                               '20 minutes before returning'}]}
    assert serialize_stack(elwood_stack) == \
        {'owner': 'Kalen',
         'pages': [{'author': 'Kalen',
                    'type': 'Writing',
                    'content': "An Awful Eiffel Tower"},
                   {'author': 'DarthMarth',
                    'type': 'Drawing',
                    'content': elwood_stack.drawings[0].data_url}]}

def test_get_game_overview(test_session, david, nathan, elwood):
    unfinished_game = test_session.query(Game).get(3)

    assert get_game_overview(unfinished_game, david) == \
        {'clockwise': True,
         'num_rounds': 2,
         'circle': [('DarthMarth', [(4, 'write', 2)]),
                    ('Kalen', [(4, 'write', 0)]),
                    ('humcalc', [(4, 'write', 1)])]}
    assert get_game_overview(unfinished_game, elwood) == \
        {'clockwise': True,
         'num_rounds': 2,
         'circle': [('Kalen', [(4, 'write', 2)]),
                    ('humcalc', [(4, 'write', 0)]),
                    ('DarthMarth', [(4, 'write', 1)])]}
    assert get_game_overview(unfinished_game, nathan) == \
        {'clockwise': True,
         'num_rounds': 2,
         'circle': [('humcalc', [(4, 'write', 2)]),
                    ('DarthMarth', [(4, 'write', 0)]),
                    ('Kalen', [(4, 'write', 1)])]}

    drawfirst_game = test_session.query(Game).get(6)

    assert get_game_overview(drawfirst_game, david) == \
        {'clockwise': True,
         'num_rounds': 1,
         'circle': [('DarthMarth', [(0, 'draw', 0),
                                    (1, 'write', 2)]),
                    ('humcalc', [(0, 'draw', 1)]),
                    ('Kalen', [])]}
    assert get_game_overview(drawfirst_game, elwood) == \
        {'clockwise': True,
         'num_rounds': 1,
         'circle': [('Kalen', []),
                    ('DarthMarth', [(0, 'draw', 1),
                                    (1, 'write', 0)]),
                    ('humcalc', [(0, 'draw', 2)])]}
    assert get_game_overview(drawfirst_game, nathan) == \
        {'clockwise': True,
         'num_rounds': 1,
         'circle': [('humcalc', [(0, 'draw', 0)]),
                    ('Kalen', []),
                    ('DarthMarth', [(0, 'draw', 2),
                                    (1, 'write', 1)])]}

    partially_done_game = test_session.query(Game).get(7)

    assert get_game_overview(partially_done_game, david) == \
        {'clockwise': True,
         'num_rounds': 1,
         'circle': [('DarthMarth', [(3, 'done', 0)]),
                    ('humcalc', [(2, 'write', 2),
                                 (3, 'done', 1)]),
                    ('Kalen', [])]}
    assert get_game_overview(partially_done_game, elwood) == \
        {'clockwise': True,
         'num_rounds': 1,
         'circle': [('Kalen', []),
                    ('DarthMarth', [(3, 'done', 1)]),
                    ('humcalc', [(2, 'write', 0),
                                 (3, 'done', 2)])]}
    assert get_game_overview(partially_done_game, nathan) == \
        {'clockwise': True,
         'num_rounds': 1,
         'circle': [('humcalc', [(2, 'write', 1),
                                 (3, 'done', 0)]),
                    ('Kalen', []),
                    ('DarthMarth', [(3, 'done', 2)])]}

def test_get_game_state(test_session, david, nathan, elwood):
    # Game
    game = test_session.query(Game).get(1)

    assert get_game_state(game, david) ==  {'action': 'view',
                                            'state': 'done'}
    assert get_game_state(game, nathan) ==  {'action': 'view',
                                             'state': 'done'}
    assert get_game_state(game, elwood) ==  {'action': 'view',
                                             'state': 'done'}

    # Long games
    long_game = test_session.query(Game).get(2)

    assert get_game_state(long_game, david) ==  {'action': 'view',
                                                 'state': 'done'}
    assert get_game_state(long_game, nathan) ==  {'action': 'view',
                                                  'state': 'done'}
    assert get_game_state(long_game, elwood) ==  {'action': 'view',
                                                  'state': 'done'}

    # Unfinished game
    unfinished_game = test_session.query(Game).get(3)

    assert get_game_state(unfinished_game, david) == {'action': 'write',
                                                      'state': 'write 21',
                                                      'text': 'humcalc passed:'}    
    assert get_game_state(unfinished_game, nathan) == {'action': 'write',
                                                       'state': 'write 23',
                                                       'text': 'Kalen passed:'}
    assert get_game_state(unfinished_game, elwood) == {'action': 'write',
                                                       'state': 'write 19',
                                                       'text': 'DarthMarth passed:'}

    # Elwood has a queue game
    # queue_game = test_session.query(Game).get(4)

    # david_state = get_game_state(queue_game, david)
    # assert david_state['action'] == 'draw'
    # assert isinstance(david_state['prev'], Writing)
    # assert david_state['prev'].author_id == elwood.id_
    # assert david_state['prev'].stack_pos == 0
    # nathan_state = get_game_state(queue_game, nathan)
    # assert nathan_state == {'action': 'wait'}
    # elwood_state = get_game_state(queue_game, elwood)
    # assert elwood_state['action'] == 'draw'
    # assert isinstance(elwood_state['prev'], Writing)
    # assert elwood_state['prev'].author_id == nathan.id_
    # assert elwood_state['prev'].stack_pos == 0

    # # Reverse game
    # reverse_game = test_session.query(Game).get(5)

    # david_state = get_game_state(reverse_game, david)
    # assert david_state['action'] == 'draw'
    # assert isinstance(david_state['prev'], Writing)
    # assert david_state['prev'].author_id == nathan.id_
    # assert david_state['prev'].stack_pos == 0
    # nathan_state = get_game_state(reverse_game, nathan)
    # assert nathan_state['action'] == 'draw'
    # assert isinstance(nathan_state['prev'], Writing)
    # assert nathan_state['prev'].author_id == elwood.id_
    # assert nathan_state['prev'].stack_pos == 0
    # elwood_state = get_game_state(reverse_game, elwood)
    # assert elwood_state['action'] == 'draw'
    # assert isinstance(elwood_state['prev'], Writing)
    # assert elwood_state['prev'].author_id == david.id_
    # assert elwood_state['prev'].stack_pos == 0

    # # Draw first game
    # drawfirst_game = test_session.query(Game).get(6)

    # david_state = get_game_state(drawfirst_game, david)
    # assert david_state['action'] == 'draw'
    # assert david_state['prev'] is None
    # nathan_state = get_game_state(drawfirst_game, nathan)
    # assert nathan_state['action'] == 'draw'
    # assert nathan_state['prev'] is None
    # elwood_state = get_game_state(drawfirst_game, elwood)
    # assert elwood_state == {'action': 'wait'}

@pytest.mark.skip
def test_get_game_state_ful(test_session, david, nathan, elwood):
    # Game
    game = test_session.query(Game).get(1)

    david_state = get_game_state(game, david)
    assert david_state['action'] == 'view'
    assert len(david_state['stacks']) == 3
    nathan_state = get_game_state(game, nathan)
    assert nathan_state['action'] == 'view'
    assert all([ns is ds for ns, ds in zip(nathan_state['stacks'], david_state['stacks'])])
    elwood_state = get_game_state(game, elwood)
    assert elwood_state['action'] == 'view'
    assert all([es is ds for es, ds in zip(elwood_state['stacks'], david_state['stacks'])])

    # Long games
    long_game = test_session.query(Game).get(2)

    david_state = get_game_state(long_game, david)
    assert david_state['action'] == 'view'
    assert len(david_state['stacks']) == 2
    nathan_state = get_game_state(long_game, nathan)
    assert nathan_state['action'] == 'view'
    assert all([ns is ds for ns, ds in zip(nathan_state['stacks'], david_state['stacks'])])

    # Unfinished game
    unfinished_game = test_session.query(Game).get(3)

    david_state = get_game_state(unfinished_game, david)
    assert david_state['action'] == 'write'
    assert isinstance(david_state['prev'], Drawing)
    assert david_state['prev'].author_id == nathan.id_
    assert david_state['prev'].stack_pos == 3
    nathan_state = get_game_state(unfinished_game, nathan)
    assert nathan_state['action'] == 'write'
    assert isinstance(nathan_state['prev'], Drawing)
    assert nathan_state['prev'].author_id == elwood.id_
    assert nathan_state['prev'].stack_pos == 3
    elwood_state = get_game_state(unfinished_game, elwood)
    assert elwood_state['action'] == 'write'
    assert isinstance(elwood_state['prev'], Drawing)
    assert elwood_state['prev'].author_id == david.id_
    assert elwood_state['prev'].stack_pos == 3

    # Elwood has a queue game
    queue_game = test_session.query(Game).get(4)

    david_state = get_game_state(queue_game, david)
    assert david_state['action'] == 'draw'
    assert isinstance(david_state['prev'], Writing)
    assert david_state['prev'].author_id == elwood.id_
    assert david_state['prev'].stack_pos == 0
    nathan_state = get_game_state(queue_game, nathan)
    assert nathan_state == {'action': 'wait'}
    elwood_state = get_game_state(queue_game, elwood)
    assert elwood_state['action'] == 'draw'
    assert isinstance(elwood_state['prev'], Writing)
    assert elwood_state['prev'].author_id == nathan.id_
    assert elwood_state['prev'].stack_pos == 0

    # Reverse game
    reverse_game = test_session.query(Game).get(5)

    david_state = get_game_state(reverse_game, david)
    assert david_state['action'] == 'draw'
    assert isinstance(david_state['prev'], Writing)
    assert david_state['prev'].author_id == nathan.id_
    assert david_state['prev'].stack_pos == 0
    nathan_state = get_game_state(reverse_game, nathan)
    assert nathan_state['action'] == 'draw'
    assert isinstance(nathan_state['prev'], Writing)
    assert nathan_state['prev'].author_id == elwood.id_
    assert nathan_state['prev'].stack_pos == 0
    elwood_state = get_game_state(reverse_game, elwood)
    assert elwood_state['action'] == 'draw'
    assert isinstance(elwood_state['prev'], Writing)
    assert elwood_state['prev'].author_id == david.id_
    assert elwood_state['prev'].stack_pos == 0

    # Draw first game
    drawfirst_game = test_session.query(Game).get(6)

    david_state = get_game_state(drawfirst_game, david)
    assert david_state['action'] == 'draw'
    assert david_state['prev'] is None
    nathan_state = get_game_state(drawfirst_game, nathan)
    assert nathan_state['action'] == 'draw'
    assert nathan_state['prev'] is None
    elwood_state = get_game_state(drawfirst_game, elwood)
    assert elwood_state == {'action': 'wait'}
