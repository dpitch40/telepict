from util import get_pending_stacks, _get_game_state
from db import Game, Player, Writing, Drawing

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

def test__get_game_state(test_session, david, nathan, elwood):
    # Game
    game = test_session.query(Game).get(1)

    david_state = _get_game_state(game, david)
    assert david_state['action'] == 'view'
    assert len(david_state['stacks']) == 3
    nathan_state = _get_game_state(game, nathan)
    assert nathan_state['action'] == 'view'
    assert all([ns is ds for ns, ds in zip(nathan_state['stacks'], david_state['stacks'])])
    elwood_state = _get_game_state(game, elwood)
    assert elwood_state['action'] == 'view'
    assert all([es is ds for es, ds in zip(elwood_state['stacks'], david_state['stacks'])])

    # Long games
    long_game = test_session.query(Game).get(2)

    david_state = _get_game_state(long_game, david)
    assert david_state['action'] == 'view'
    assert len(david_state['stacks']) == 2
    nathan_state = _get_game_state(long_game, nathan)
    assert nathan_state['action'] == 'view'
    assert all([ns is ds for ns, ds in zip(nathan_state['stacks'], david_state['stacks'])])

    # Unfinished game
    unfinished_game = test_session.query(Game).get(3)

    david_state = _get_game_state(unfinished_game, david)
    assert david_state['action'] == 'write'
    assert isinstance(david_state['prev'], Drawing)
    assert david_state['prev'].author_id == nathan.id_
    assert david_state['prev'].stack_pos == 3
    nathan_state = _get_game_state(unfinished_game, nathan)
    assert nathan_state['action'] == 'write'
    assert isinstance(nathan_state['prev'], Drawing)
    assert nathan_state['prev'].author_id == elwood.id_
    assert nathan_state['prev'].stack_pos == 3
    elwood_state = _get_game_state(unfinished_game, elwood)
    assert elwood_state['action'] == 'write'
    assert isinstance(elwood_state['prev'], Drawing)
    assert elwood_state['prev'].author_id == david.id_
    assert elwood_state['prev'].stack_pos == 3

    # Elwood has a queue game
    queue_game = test_session.query(Game).get(4)

    david_state = _get_game_state(queue_game, david)
    assert david_state['action'] == 'draw'
    assert isinstance(david_state['prev'], Writing)
    assert david_state['prev'].author_id == elwood.id_
    assert david_state['prev'].stack_pos == 0
    nathan_state = _get_game_state(queue_game, nathan)
    assert nathan_state == {'action': 'wait'}
    elwood_state = _get_game_state(queue_game, elwood)
    assert elwood_state['action'] == 'draw'
    assert isinstance(elwood_state['prev'], Writing)
    assert elwood_state['prev'].author_id == nathan.id_
    assert elwood_state['prev'].stack_pos == 0

    # Reverse game
    reverse_game = test_session.query(Game).get(5)

    david_state = _get_game_state(reverse_game, david)
    assert david_state['action'] == 'draw'
    assert isinstance(david_state['prev'], Writing)
    assert david_state['prev'].author_id == nathan.id_
    assert david_state['prev'].stack_pos == 0
    nathan_state = _get_game_state(reverse_game, nathan)
    assert nathan_state['action'] == 'draw'
    assert isinstance(nathan_state['prev'], Writing)
    assert nathan_state['prev'].author_id == elwood.id_
    assert nathan_state['prev'].stack_pos == 0
    elwood_state = _get_game_state(reverse_game, elwood)
    assert elwood_state['action'] == 'draw'
    assert isinstance(elwood_state['prev'], Writing)
    assert elwood_state['prev'].author_id == david.id_
    assert elwood_state['prev'].stack_pos == 0

    # Draw first game
    drawfirst_game = test_session.query(Game).get(6)

    david_state = _get_game_state(drawfirst_game, david)
    assert david_state['action'] == 'draw'
    assert david_state['prev'] is None
    nathan_state = _get_game_state(drawfirst_game, nathan)
    assert nathan_state['action'] == 'draw'
    assert nathan_state['prev'] is None
    elwood_state = _get_game_state(drawfirst_game, elwood)
    assert elwood_state == {'action': 'wait'}
