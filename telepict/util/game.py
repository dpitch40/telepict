import base64
import operator

from ..db import Drawing, Writing, Game
from .text_table import ascii_table

def get_pending_stacks(game, player):
    """Gets a player's "queue" of stacks in the current game, in order of increasing size
    """
    player_order = None
    for assn in game.players_:
        if assn.player_id == player.id_:
            player_order = assn.player_order
            break
    else:
        raise ValueError(f'Player {player} is not in {game}')

    stacks = game.stacks
    num_players = len(game.players_)
    # Order the stacks backwards--starting with the current player
    step = -1 if game.pass_left else 1
    stacks_ordered = stacks[player_order::step] + stacks[:player_order:step]
    # Pending stacks are any stacks whose height is equal to their place in the order
    # list, mod the number of players--e.g. a player's own empty stack, or a stack of height 1
    # passed by the previous player, and so on
    pending_stacks = [stack for i, stack in enumerate(stacks_ordered) if
                      (i - len(stack.stack)) % num_players == 0]

    # Order by increasing size
    pending_stacks.sort(key=operator.methodcaller('__len__'))
    return pending_stacks

def serialize_stack(stack):
    pages = list()
    stack_dict = {'owner': stack.owner.display_name,
                  'pages': pages}
    for page in stack.stack:
        page_dict = {'author': page.author.display_name}
        if isinstance(page, Drawing):
            page_dict['type'] = 'Drawing'
            page_dict['content'] = page.data_url
        elif isinstance(page, Writing):
            page_dict['type'] = 'Writing'
            page_dict['content'] = page.text
        else:
            page_dict['type'] = 'Pass'
            page_dict['content'] = None
        pages.append(page_dict)
    return stack_dict

def get_game_overview(game, start_player):
    """Generates an overview of the game for display in the game widget, centered on start_player.

    Return format:
    {
        'clockwise': boolean, whether the pass direction is left
        'num_rounds': number of times around
        'circle': list of 3-tuples for each player:
            (player display name,
             boolean if the player has left the game,
             list of the player's pending stacks; each is a 3-tuple:
             (stack height, action to take, relative index of the stack owner)
            )
    }
    """
    start_action = 'write' if game.write_first else 'draw'
    if start_player is None:
        start_index = 0
    else:
        start_index = [player.id_ for player in game.players].index(start_player.id_)
    player_assns = game.player_assns
    player_assns_relative = player_assns[start_index:] + player_assns[:start_index]
    player_ids_relative = list(map(operator.attrgetter('player.id_'), player_assns_relative))
    circle = list()
    for assn in player_assns_relative:
        player = assn.player
        pending_stacks = get_pending_stacks(game, player)
        player_stacks = list()
        for stack in pending_stacks:
            stack_len = len(stack)
            last = stack.last
            if stack_len == game.target_len:
                action = 'done'
            elif not last:
                action = start_action
            elif isinstance(last, Writing):
                action = 'draw'
            else:
                action = 'write'
            player_stacks.append((len(stack), action, player_ids_relative.index(stack.owner.id_)))
        circle.append((player.display_name, assn.left_game, player_stacks))

    overview = {'clockwise': game.pass_left,
                'num_rounds': game.num_rounds,
                'circle': circle}
    return overview

def get_game_state(game, player):
    """Used to load the state of a game for a player for displaying on the page.

    If the game is complete, returns all stacks for enjoyment.

    If the game is incomplete and the player hasn't written/drawn anything yet, prompts them
    to start.

    If the game is incomplete and the player has at least one pending stack, returns the next
    pending stack for the user to respond to by drawing/writing.

    If the game is incomplete and the player has no pending stacks, returns nothing
    (displays a wait message).
    """

    if player is None: # Spectator
        num_pages = sum(len(stack) for stack in game.stacks)
        state = {'action': 'view',
                 'state': f'spectate {num_pages}'}
    elif game.complete:
        state = {'action': 'view',
                 'state': 'done'}
    else:
        pending_stacks = get_pending_stacks(game, player)
        prev_player = game.get_adjacent_player(player, False)
        if pending_stacks:
            current_stack = pending_stacks[0]
            last = current_stack.last
            first = last is None
            if len(current_stack) == game.target_len:
                # This player is done
                state = {'action': 'view_own',
                         'state': 'done_own'}
            elif first:
                action = 'write' if game.write_first else 'draw'
                state = {'action': action,
                         'text': '',
                         'state': f'{action} -1'}
            else:
                action = 'write' if isinstance(last, Drawing) else 'draw'
                state = {'action': action,
                         'text': f'{prev_player.display_name} passed:',
                         'state': f'{action} {last.id_}'}
        else:
            state = {'action': 'wait',
                     'text': f'Waiting for {prev_player.display_name} to pass you something',
                     'state': 'wait'}
    return state

def get_game_state_full(game, player):
    state = get_game_state(game, player)

    if state['state'] == 'done' or state['state'].startswith('spectate'):
        state['stacks'] = [serialize_stack(s) for s in game.stacks]
    elif state['state'] == 'done_own':
        pending_stacks = get_pending_stacks(game, player)
        state['stack'] = serialize_stack(pending_stacks[0])
    elif state['state'] != 'wait':
        pending_stacks = get_pending_stacks(game, player)
        if pending_stacks[0]:
            prev = pending_stacks[0].last
            if state['action'] == 'draw':
                state['prev'] = prev.text
            else:
                state['prev'] = prev.data_url
        else:
            state['prev'] = ''
    state['overview'] = get_game_overview(game, player)

    return state

def get_game_summary(session, game_id, max_width=120):
    """Generates a text summary of the entire game for debugging purposes.
    """
    game = session.query(Game).get(game_id)
    players = game.players

    l = [['Player', 'Stack', 'Stack Owner', 'Contents']]

    for player in players:
        pending_stacks = get_pending_stacks(game, player)
        for i, stack in enumerate(pending_stacks):
            stack_repr = repr(stack)
            stack_items = stack.stack

            if stack_items:
                if i == 0:
                    l.append([repr(player), f'{stack.id_} ({len(stack)})', repr(stack.owner),
                              stack_items[0]])
                else:
                    l.append(['', f'{stack.id_} ({len(stack)})', repr(stack.owner),
                              stack_items[0]])
                l.extend([['', '', '', w] for w in stack_items[1:]])
            else:
                l.append([repr(player), f'{stack.id_} ({len(stack)})', repr(stack.owner), ''])
        if not pending_stacks:
                l.append([repr(player), '', '', ''])

    return '\n' + ascii_table(l)
