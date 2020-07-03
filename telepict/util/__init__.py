import base64
import operator

from ..db import Drawing

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
    stack_dict = {'owner': stack.owner.name,
                  'pages': pages}
    for page in stack.stack:
        page_dict = {'author': page.author.name}
        if isinstance(page, Drawing):
            page_dict['type'] = 'Drawing'
            page_dict['content'] = page.data_url
        else:
            page_dict['type'] = 'Writing'
            page_dict['content'] = page.text
        pages.append(page_dict)
    return stack_dict

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
        # Return all stacks
        stacks = list()
        for stack in game.stacks:
            stacks.append(serialize_stack(stack))
        return {'stacks': stacks,
                'action': 'view',
                'state': 'done'}

    pending_stacks = get_pending_stacks(game, player)
    prev_player = game.get_adjacent_player(player, False)
    if pending_stacks:
        current_stack = pending_stacks[0].stack
        first = not bool(current_stack)
        if first:
            prev = ''
            text = ''
            ent_id = -1
            if game.write_first:
                action = 'write'
            else:
                action = 'draw'
        elif len(current_stack) == game.num_rounds * len(game.players_):
            # This player is done
            return {'action': 'view_own',
                    'stack': serialize_stack(pending_stacks[0]),
                    'state': 'done_own'}
        else:
            ent = current_stack[-1]
            ent_id = ent.id_
            action = 'write' if isinstance(ent, Drawing) else 'draw'
            text = f'{prev_player.name} passed:'

            if action == 'draw':
                prev = ent.text
            else:
                prev = ent.data_url

        return {'prev': prev,
                'action': action,
                'text': text,
                'state': f'{action} {ent_id}'}

    return {'action': 'wait',
            'text': f'Waiting for {prev_player.name} to pass you something',
            'state': 'wait'}
