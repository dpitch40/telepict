import os
import os.path
import logging.config
import base64
import operator

from ..db import Drawing

def configure_logging(config_class):
    logging_config = {k: getattr(config_class, k) for k in dir(config_class) if not k.startswith('__')}
    if 'file' in logging_config['handlers']:
        logfile = logging_config['handlers']['file']['filename']
        log_dir = os.path.abspath(os.path.dirname(logfile))
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
    logging.config.dictConfig(logging_config)

def get_pending_stacks(game, player):
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
        else:
            page_dict['type'] = 'Writing'
            page_dict['content'] = page.text
        pages.append(page_dict)
    return stack_dict

def get_game_overview(game, start_player):
    start_index = [player.id_ for player in game.players].index(start_player.id_)
    players_relative = game.players[start_index:] + game.players[:start_index]
    player_ids_relative = list(map(operator.attrgetter('id_'), players_relative))
    if game.write_first:
        start_action, next_action = 'write', 'draw'
    else:
        start_action, next_action = 'draw', 'write'
    circle = list()
    for player in players_relative:
        pending_stacks = get_pending_stacks(game, player)
        player_stacks = list()
        for stack in pending_stacks:
            stack_len = len(stack)
            if stack_len == game.num_rounds * len(game.players_):
                action = 'done'
            elif not stack_len % 2:
                action = start_action
            else:
                action = next_action
            player_stacks.append((len(stack), action, player_ids_relative.index(stack.owner.id_)))
        circle.append((player.display_name, player_stacks))

    return {'clockwise': game.pass_left,
            'num_rounds': game.num_rounds,
            'circle': circle}

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

    if game.complete:
        state = {'action': 'view',
                 'state': 'done'}
    else:
        pending_stacks = get_pending_stacks(game, player)
        prev_player = game.get_adjacent_player(player, False)
        if pending_stacks:
            current_stack = pending_stacks[0].stack
            first = not bool(current_stack)
            if len(current_stack) == game.num_rounds * len(game.players_):
                # This player is done
                state = {'action': 'view_own',
                         'state': 'done_own'}
            elif first:
                action = 'write' if game.write_first else 'draw'
                state = {'action': action,
                         'text': '',
                         'state': f'{action} -1'}
            else:
                ent = current_stack[-1]
                action = 'write' if isinstance(ent, Drawing) else 'draw'
                state = {'action': action,
                         'text': f'{prev_player.display_name} passed:',
                         'state': f'{action} {ent.id_}'}
        else:
            state = {'action': 'wait',
                     'text': f'Waiting for {prev_player.display_name} to pass you something',
                     'state': 'wait'}

    return state

def get_game_state_full(game, player):
    state = get_game_state(game, player)

    if state['state'] == 'done':
        state['stacks'] = [serialize_stack(s) for s in game.stacks]
    elif state['state'] == 'done_own':
        pending_stacks = get_pending_stacks(game, player)
        state['stack'] = serialize_stack(pending_stacks[0])
    elif state['state'] != 'wait':
        pending_stacks = get_pending_stacks(game, player)
        if pending_stacks[0]:
            prev = pending_stacks[0].stack[-1]
            if state['action'] == 'draw':
                state['prev'] = prev.text
            else:
                state['prev'] = prev.data_url
        else:
            state['prev'] = ''
    state['overview'] = get_game_overview(game, player)

    return state
