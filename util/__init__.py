from db import Directions, Drawing

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
    step = -1 if game.direction is Directions.left else 1
    stacks_ordered = stacks[player_order::step] + stacks[:player_order:step]
    return [stack for i, stack in enumerate(stacks_ordered) if
            (i - len(stack.stack)) % num_players == 0]

def get_game_state(game, player):
    """Used to load the state of a game for a player for displaying on the page.

    If the game is complete, returns all stacks for enjoyment.

    If the game is incomplete and the player hasn't written/drawn anything yet, prompts them to start.

    If the game is incomplete and the player has at least one pending stack, returns the next pending
    stack for the user to respond to by drawing/writing.

    If the game is incomplete and the player has no pending stacks, returns nothing
    (displays a wait message).
    """

    if game.complete:
        # Return all stacks
        return {'stacks': game.stacks,
                'action': 'view'}
    else:
        pending_stacks = get_pending_stacks(game, player)
        if pending_stacks:
            current_stack = pending_stacks[0].stack
            if not current_stack:
                ent = None
                if game.write_first:
                    action = 'write'
                else:
                    action = 'draw'
            else:
                ent = current_stack[-1]
                action = 'write' if isinstance(ent, Drawing) else 'draw'

            return {'prev': ent,
                    'action': action}
        else:
            return {'action': 'wait'}
