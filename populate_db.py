import os
import os.path

from db import DB, Directions, Game, Player, Stack, Writing, Drawing, PendingGame, Invitation
from config import Config

def populate_db(d):
    # Players
    david = Player(name='david', display_name='DarthMarth', password='12345678')
    nathan = Player(name='Nathan', display_name='humcalc', password='you_shall_not_password')
    elwood = Player(name='Elwood', display_name='Kalen', password='really good password')
    
    # Games
    game = Game(id_=1, num_rounds=2, players=[david, nathan, elwood])
    long_game = Game(id_=2, num_rounds=4, players=[david, nathan])
    unfinished_game = Game(id_=3, num_rounds=2, players=[david, elwood, nathan])
    queue_game = Game(id_=4, players=[david, nathan, elwood])
    reverse_game = Game(id_=5, direction=Directions.right, players=[david, nathan, elwood])
    draw_first_game = Game(id_=6, write_first=False, players=[david, nathan, elwood])

    # Pending games
    pending_game_1 = PendingGame(id_=1, direction=Directions.right,
                                 players=[david, nathan, elwood])
    pending_game_2 = PendingGame(id_=2, num_rounds=3, write_first=False,
                                 players=[david, elwood])
    invitation = Invitation(recipient=nathan, game=pending_game_2)

    # Stacks
    yesterday = Stack(game=game, owner=david)
    hungry_cat = Stack(game=long_game, owner=david)
    olympics = Stack(game=unfinished_game, owner=david)
    enders_game = Stack(game=game, owner=nathan)
    dediscovering = Stack(game=long_game, owner=nathan)
    changing_stack = Stack(game=unfinished_game, owner=nathan)
    eiffel_tower = Stack(game=game, owner=elwood)
    fire_dice = Stack(game=unfinished_game, owner=elwood)

    q_yesterday = Stack(game=queue_game, owner=david)
    q_enders_game = Stack(game=queue_game, owner=nathan)
    q_eiffel_tower = Stack(game=queue_game, owner=elwood)

    d_stack_reverse = Stack(game=reverse_game, owner=david)
    n_stack_reverse = Stack(game=reverse_game, owner=nathan)
    e_stack_reverse = Stack(game=reverse_game, owner=elwood)

    d_stack_drawfirst = Stack(game=draw_first_game, owner=david)
    n_stack_drawfirst = Stack(game=draw_first_game, owner=nathan)
    e_stack_drawfirst = Stack(game=draw_first_game, owner=elwood)

    # Game
    dw_11 = Writing(text="Coming soon: yesterday",
                    stack_pos=0, stack=yesterday, author=david)
    dw_12 = Writing(text="Be kind, bake your VHS tapes at 400 degrees for "
                         "20 minutes before returning",
                    stack_pos=2, stack=enders_game, author=david)
    dw_13 = Writing(text="The pyramid is sad because it fell over. "
                         "People measure it instead of helping.",
                    stack_pos=4, stack=eiffel_tower, author=david)

    nw_11 = Writing(text="Ender's Game",
                    stack_pos=0, stack=enders_game, author=nathan)
    nw_12 = Writing(text="The Eiffel Tower is sad that it's being subjected to a linear "
                         "transformation that's stretching in the x direction and "
                         "compressing in the y direction.",
                    stack_pos=2, stack=eiffel_tower, author=nathan)
    nw_13 = Writing(text="Daylight Savings starts on Monday the 21st this year "
                         "for some reason.",
                    stack_pos=4, stack=yesterday, author=nathan)

    ew_11 = Writing(text="An Awful Eiffel Tower",
                    stack_pos=0, stack=eiffel_tower, author=elwood)
    ew_12 = Writing(text="Passing an hour on the fourth Monday.",
                    stack_pos=2, stack=yesterday, author=elwood)
    ew_13 = Writing(text="Roomba is ready to vacuum up the shocked TV person's mess",
                    stack_pos=4, stack=enders_game, author=elwood)

    dd_11 = Drawing(drawing=open(os.path.join('data', 'drawings', 'dd_11.jpg'), 'rb').read(),
                    stack_pos=1, stack=eiffel_tower, author=david)
    dd_12 = Drawing(drawing=open(os.path.join('data', 'drawings', 'dd_12.jpg'), 'rb').read(),
                    stack_pos=3, stack=yesterday, author=david)
    dd_13 = Drawing(drawing=open(os.path.join('data', 'drawings', 'dd_13.jpg'), 'rb').read(),
                    stack_pos=5, stack=enders_game, author=david)

    nd_11 = Drawing(drawing=open(os.path.join('data', 'drawings', 'nd_11.jpg'), 'rb').read(),
                    stack_pos=1, stack=yesterday, author=nathan)
    nd_12 = Drawing(drawing=open(os.path.join('data', 'drawings', 'nd_12.jpg'), 'rb').read(),
                    stack_pos=3, stack=enders_game, author=nathan)
    nd_13 = Drawing(drawing=open(os.path.join('data', 'drawings', 'nd_13.jpg'), 'rb').read(),
                    stack_pos=5, stack=eiffel_tower, author=nathan)

    ed_11 = Drawing(drawing=open(os.path.join('data', 'drawings', 'ed_11.jpg'), 'rb').read(),
                    stack_pos=1, stack=enders_game, author=elwood)
    ed_12 = Drawing(drawing=open(os.path.join('data', 'drawings', 'ed_12.jpg'), 'rb').read(),
                    stack_pos=3, stack=eiffel_tower, author=elwood)
    ed_13 = Drawing(drawing=open(os.path.join('data', 'drawings', 'ed_13.jpg'), 'rb').read(),
                    stack_pos=5, stack=yesterday, author=elwood)

    # Long game
    dw_21 = Writing(text="A cat (hungry) on a conveyor belt to Mexican Hell. "
                         "Old mice watch.",
                    stack_pos=0, stack=hungry_cat, author=david)
    dw_22 = Writing(text="Europeans waiting in line for food and communism",
                    stack_pos=2, stack=hungry_cat, author=david)
    dw_23 = Writing(text="Daggers piercing balloons makes for a sunny week.",
                    stack_pos=4, stack=hungry_cat, author=david)
    dw_24 = Writing(text="Recursive sunset chainsaw massacre",
                    stack_pos=6, stack=hungry_cat, author=david)

    nw_21 = Writing(text="The de-discovering of America. The Europeans were afraid of the colossi.",
                    stack_pos=0, stack=dediscovering, author=nathan)
    nw_22 = Writing(text="Elworld. The Elwood,themed theme park",
                    stack_pos=2, stack=dediscovering, author=nathan)
    nw_23 = Writing(text="A dinosaur texting his prey.",
                    stack_pos=4, stack=dediscovering, author=nathan)
    nw_24 = Writing(text="Dead puppies make new puppies",
                    stack_pos=6, stack=dediscovering, author=nathan)

    dd_21 = Drawing(drawing=open(os.path.join('data', 'drawings', 'dd_21.jpg'), 'rb').read(),
                    stack_pos=1, stack=dediscovering, author=david)
    dd_22 = Drawing(drawing=open(os.path.join('data', 'drawings', 'dd_22.jpg'), 'rb').read(),
                    stack_pos=3, stack=dediscovering, author=david)
    dd_23 = Drawing(drawing=open(os.path.join('data', 'drawings', 'dd_23.jpg'), 'rb').read(),
                    stack_pos=5, stack=dediscovering, author=david)
    dd_24 = Drawing(drawing=open(os.path.join('data', 'drawings', 'dd_24.jpg'), 'rb').read(),
                    stack_pos=7, stack=dediscovering, author=david)

    nd_21 = Drawing(drawing=open(os.path.join('data', 'drawings', 'nd_21.jpg'), 'rb').read(),
                    stack_pos=1, stack=hungry_cat, author=nathan)
    nd_22 = Drawing(drawing=open(os.path.join('data', 'drawings', 'nd_22.jpg'), 'rb').read(),
                    stack_pos=3, stack=hungry_cat, author=nathan)
    nd_23 = Drawing(drawing=open(os.path.join('data', 'drawings', 'nd_23.jpg'), 'rb').read(),
                    stack_pos=5, stack=hungry_cat, author=nathan)
    nd_24 = Drawing(drawing=open(os.path.join('data', 'drawings', 'nd_24.jpg'), 'rb').read(),
                    stack_pos=7, stack=hungry_cat, author=nathan)

    # Unfinished game
    dw_31 = Writing(text="The Olympic hide-and-seek championships",
                    stack_pos=0, stack=olympics, author=david)
    dw_32 = Writing(text="1d4, 1d6, 1d8 roasting on an open fire",
                    stack_pos=2, stack=fire_dice, author=david)

    nw_31 = Writing(text="Changing the meaning of the stack in Telephone Pictionary",
                    stack_pos=0, stack=changing_stack, author=nathan)
    nw_32 = Writing(text="Olympic fan waving",
                    stack_pos=2, stack=olympics, author=nathan)

    ew_31 = Writing(text="Fire Dice",
                    stack_pos=0, stack=fire_dice, author=elwood)
    ew_32 = Writing(text="Nerd is angry/surprised that things are collating the "
                         "wrong way when printed",
                    stack_pos=2, stack=changing_stack, author=elwood)

    dd_31 = Drawing(drawing=open(os.path.join('data', 'drawings', 'dd_31.jpg'), 'rb').read(),
                    stack_pos=1, stack=changing_stack, author=david)
    dd_32 = Drawing(drawing=open(os.path.join('data', 'drawings', 'dd_32.jpg'), 'rb').read(),
                    stack_pos=3, stack=olympics, author=david)

    nd_31 = Drawing(drawing=open(os.path.join('data', 'drawings', 'nd_31.jpg'), 'rb').read(),
                    stack_pos=1, stack=fire_dice, author=nathan)
    nd_32 = Drawing(drawing=open(os.path.join('data', 'drawings', 'nd_32.jpg'), 'rb').read(),
                    stack_pos=3, stack=changing_stack, author=nathan)

    ed_31 = Drawing(drawing=open(os.path.join('data', 'drawings', 'ed_31.jpg'), 'rb').read(),
                    stack_pos=1, stack=olympics, author=elwood)
    ed_32 = Drawing(drawing=open(os.path.join('data', 'drawings', 'ed_32.jpg'), 'rb').read(),
                    stack_pos=3, stack=fire_dice, author=elwood)

    # Queue game
    q_dw = Writing(text="Coming soon: yesterday",
                   stack_pos=0, stack=q_yesterday, author=david)
    q_nw = Writing(text="Ender's Game",
                   stack_pos=0, stack=q_enders_game, author=nathan)
    q_ew = Writing(text="An Awful Eiffel Tower",
                   stack_pos=0, stack=q_eiffel_tower, author=elwood)
    q_nd = Drawing(drawing=open(os.path.join('data', 'drawings', 'nd_11.jpg'), 'rb').read(),
                   stack_pos=1, stack=q_yesterday, author=nathan)

    # Reverse game
    r_dw = Writing(text="Europeans waiting in line for food and communism",
                   stack_pos=0, stack=d_stack_reverse, author=david)
    r_nw = Writing(text="Elworld. The Elwood,themed theme park",
                   stack_pos=0, stack=n_stack_reverse, author=nathan)
    r_ew = Writing(text="A dinosaur texting his prey.",
                   stack_pos=0, stack=e_stack_reverse, author=elwood)

    # Draw first game
    df_ed = Drawing(drawing=open(os.path.join('data', 'drawings', 'nd_21.jpg'), 'rb').read(),
                    stack_pos=0, stack=e_stack_drawfirst, author=elwood)

    with d.session_scope() as session:
        for ent in [david, nathan, elwood, queue_game, reverse_game, draw_first_game,
                    pending_game_1, pending_game_2]:
            session.add(ent)

if __name__ == '__main__':
    if os.path.isfile(Config.DBFILE):
        os.remove(Config.DBFILE)
    d = DB()
    d.create_schema()
    populate_db(d)
