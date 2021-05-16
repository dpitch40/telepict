import os
import os.path
import argparse
from datetime import datetime, timedelta

from telepict.db import DB, Game, Player, Stack, Writing, Drawing, PendingGame, Invitation
from telepict.config import Config

def hours_ago(n):
    return datetime.now() - timedelta(hours=n)

def populate_db(d):
    # Players
    david = Player(id_=1, name='david', display_name='DarthMarth', password='12345678')
    nathan = Player(id_=2, name='Nathan', display_name='humcalc', password='you_shall_not_password')
    elwood = Player(id_=3, name='Elwood', display_name='Kalen', password='really good password')
    
    # Games
    game = Game(id_=1, num_rounds=2, players=[david, nathan, elwood])
    long_game = Game(id_=2, num_rounds=4, players=[david, nathan], started=hours_ago(1))
    unfinished_game = Game(id_=3, num_rounds=2, players=[david, elwood, nathan], started=hours_ago(2))
    queue_game = Game(id_=4, players=[david, nathan, elwood], started=hours_ago(3))
    reverse_game = Game(id_=5, pass_left=False, players=[david, nathan, elwood], started=hours_ago(4))
    draw_first_game = Game(id_=6, write_first=False, players=[david, nathan, elwood], started=hours_ago(5))
    partially_done_game = Game(id_=7, players=[david, nathan, elwood], started=hours_ago(6))

    # Pending games
    pending_game_1 = PendingGame(id_=1, pass_left=False,
                                 creator=david, players=[david, nathan, elwood])
    pending_game_2 = PendingGame(id_=2, num_rounds=3, write_first=False,
                                 creator=elwood, players=[david, elwood], created=hours_ago(1))
    pending_game_3 = PendingGame(id_=3, num_rounds=5, write_first=False,
                                 creator=nathan, players=[nathan, elwood], created=hours_ago(2))
    pending_game_4 = PendingGame(id_=4, num_rounds=7,
                                 creator=david, players=[david], created=hours_ago(3))
    invitation = Invitation(recipient=nathan, game=pending_game_2)
    invitation2 = Invitation(recipient=david, game=pending_game_3)
    invitation3 = Invitation(recipient=elwood, game=pending_game_4)

    # Stacks
    yesterday = Stack(id_=1, game=game, owner=david)
    hungry_cat = Stack(id_=2, game=long_game, owner=david)
    olympics = Stack(id_=3, game=unfinished_game, owner=david)
    enders_game = Stack(id_=4, game=game, owner=nathan)
    dediscovering = Stack(id_=5, game=long_game, owner=nathan)
    changing_stack = Stack(id_=6, game=unfinished_game, owner=nathan)
    eiffel_tower = Stack(id_=7, game=game, owner=elwood)
    fire_dice = Stack(id_=8, game=unfinished_game, owner=elwood)

    q_yesterday = Stack(id_=9, game=queue_game, owner=david)
    q_enders_game = Stack(id_=10, game=queue_game, owner=nathan)
    q_eiffel_tower = Stack(id_=11, game=queue_game, owner=elwood)

    d_stack_reverse = Stack(id_=12, game=reverse_game, owner=david)
    n_stack_reverse = Stack(id_=13, game=reverse_game, owner=nathan)
    e_stack_reverse = Stack(id_=14, game=reverse_game, owner=elwood)

    d_stack_drawfirst = Stack(id_=15, game=draw_first_game, owner=david)
    n_stack_drawfirst = Stack(id_=16, game=draw_first_game, owner=nathan)
    e_stack_drawfirst = Stack(id_=17, game=draw_first_game, owner=elwood)

    pd_yesterday = Stack(id_=18, game=partially_done_game, owner=david)
    pd_enders_game = Stack(id_=19, game=partially_done_game, owner=nathan)
    pd_eiffel_tower = Stack(id_=20, game=partially_done_game, owner=elwood)

    # Game
    dw_11 = Writing(id_=1, text="Coming soon: yesterday",
                    stack_pos=0, stack=yesterday, author=david)
    dw_12 = Writing(id_=2, text="Be kind, bake your VHS tapes at 400 degrees for "
                         "20 minutes before returning",
                    stack_pos=2, stack=enders_game, author=david)
    dw_13 = Writing(id_=3, text="The pyramid is sad because it fell over. "
                         "People measure it instead of helping.",
                    stack_pos=4, stack=eiffel_tower, author=david)

    nw_11 = Writing(id_=4, text="Ender's Game",
                    stack_pos=0, stack=enders_game, author=nathan)
    nw_12 = Writing(id_=5, text="The Eiffel Tower is sad that it's being subjected to a linear "
                         "transformation that's stretching in the x direction and "
                         "compressing in the y direction.",
                    stack_pos=2, stack=eiffel_tower, author=nathan)
    nw_13 = Writing(id_=6, text="Daylight Savings starts on Monday the 21st this year "
                         "for some reason.",
                    stack_pos=4, stack=yesterday, author=nathan)

    ew_11 = Writing(id_=7, text="An Awful Eiffel Tower",
                    stack_pos=0, stack=eiffel_tower, author=elwood)
    ew_12 = Writing(id_=8, text="Passing an hour on the fourth Monday.",
                    stack_pos=2, stack=yesterday, author=elwood)
    ew_13 = Writing(id_=9, text="Roomba is ready to vacuum up the shocked TV person's mess",
                    stack_pos=4, stack=enders_game, author=elwood)

    dd_11 = Drawing(id_=1, drawing=open(os.path.join('data', 'drawings', 'dd_11.jpg'), 'rb').read(),
                    stack_pos=1, stack=eiffel_tower, author=david)
    dd_12 = Drawing(id_=2, drawing=open(os.path.join('data', 'drawings', 'dd_12.jpg'), 'rb').read(),
                    stack_pos=3, stack=yesterday, author=david)
    dd_13 = Drawing(id_=3, drawing=open(os.path.join('data', 'drawings', 'dd_13.jpg'), 'rb').read(),
                    stack_pos=5, stack=enders_game, author=david)

    nd_11 = Drawing(id_=4, drawing=open(os.path.join('data', 'drawings', 'nd_11.jpg'), 'rb').read(),
                    stack_pos=1, stack=yesterday, author=nathan)
    nd_12 = Drawing(id_=5, drawing=open(os.path.join('data', 'drawings', 'nd_12.jpg'), 'rb').read(),
                    stack_pos=3, stack=enders_game, author=nathan)
    nd_13 = Drawing(id_=6, drawing=open(os.path.join('data', 'drawings', 'nd_13.jpg'), 'rb').read(),
                    stack_pos=5, stack=eiffel_tower, author=nathan)

    ed_11 = Drawing(id_=7, drawing=open(os.path.join('data', 'drawings', 'ed_11.jpg'), 'rb').read(),
                    stack_pos=1, stack=enders_game, author=elwood)
    ed_12 = Drawing(id_=8, drawing=open(os.path.join('data', 'drawings', 'ed_12.jpg'), 'rb').read(),
                    stack_pos=3, stack=eiffel_tower, author=elwood)
    ed_13 = Drawing(id_=9, drawing=open(os.path.join('data', 'drawings', 'ed_13.jpg'), 'rb').read(),
                    stack_pos=5, stack=yesterday, author=elwood)

    # Long game
    dw_21 = Writing(id_=10, text="A cat (hungry) on a conveyor belt to Mexican Hell. "
                         "Old mice watch.",
                    stack_pos=0, stack=hungry_cat, author=david)
    dw_22 = Writing(id_=11, text="Europeans waiting in line for food and communism",
                    stack_pos=2, stack=hungry_cat, author=david)
    dw_23 = Writing(id_=12, text="Daggers piercing balloons makes for a sunny week.",
                    stack_pos=4, stack=hungry_cat, author=david)
    dw_24 = Writing(id_=13, text="Recursive sunset chainsaw massacre",
                    stack_pos=6, stack=hungry_cat, author=david)

    nw_21 = Writing(id_=14, text="The de-discovering of America. The Europeans were afraid of the colossi.",
                    stack_pos=0, stack=dediscovering, author=nathan)
    nw_22 = Writing(id_=15, text="Elworld. The Elwood,themed theme park",
                    stack_pos=2, stack=dediscovering, author=nathan)
    nw_23 = Writing(id_=16, text="A dinosaur texting his prey.",
                    stack_pos=4, stack=dediscovering, author=nathan)
    nw_24 = Writing(id_=17, text="Dead puppies make new puppies",
                    stack_pos=6, stack=dediscovering, author=nathan)

    dd_21 = Drawing(id_=10, drawing=open(os.path.join('data', 'drawings', 'dd_21.jpg'), 'rb').read(),
                    stack_pos=1, stack=dediscovering, author=david)
    dd_22 = Drawing(id_=11, drawing=open(os.path.join('data', 'drawings', 'dd_22.jpg'), 'rb').read(),
                    stack_pos=3, stack=dediscovering, author=david)
    dd_23 = Drawing(id_=12, drawing=open(os.path.join('data', 'drawings', 'dd_23.jpg'), 'rb').read(),
                    stack_pos=5, stack=dediscovering, author=david)
    dd_24 = Drawing(id_=13, drawing=open(os.path.join('data', 'drawings', 'dd_24.jpg'), 'rb').read(),
                    stack_pos=7, stack=dediscovering, author=david)

    nd_21 = Drawing(id_=14, drawing=open(os.path.join('data', 'drawings', 'nd_21.jpg'), 'rb').read(),
                    stack_pos=1, stack=hungry_cat, author=nathan)
    nd_22 = Drawing(id_=15, drawing=open(os.path.join('data', 'drawings', 'nd_22.jpg'), 'rb').read(),
                    stack_pos=3, stack=hungry_cat, author=nathan)
    nd_23 = Drawing(id_=16, drawing=open(os.path.join('data', 'drawings', 'nd_23.jpg'), 'rb').read(),
                    stack_pos=5, stack=hungry_cat, author=nathan)
    nd_24 = Drawing(id_=17, drawing=open(os.path.join('data', 'drawings', 'nd_24.jpg'), 'rb').read(),
                    stack_pos=7, stack=hungry_cat, author=nathan)

    # Unfinished game
    dw_31 = Writing(id_=18, text="The Olympic hide-and-seek championships",
                    stack_pos=0, stack=olympics, author=david)
    dw_32 = Writing(id_=19, text="1d4, 1d6, 1d8 roasting on an open fire",
                    stack_pos=2, stack=fire_dice, author=david)

    nw_31 = Writing(id_=20, text="Changing the meaning of the stack in Telephone Pictionary",
                    stack_pos=0, stack=changing_stack, author=nathan)
    nw_32 = Writing(id_=21, text="Olympic fan waving",
                    stack_pos=2, stack=olympics, author=nathan)

    ew_31 = Writing(id_=22, text="Fire Dice",
                    stack_pos=0, stack=fire_dice, author=elwood)
    ew_32 = Writing(id_=23, text="Nerd is angry/surprised that things are collating the "
                         "wrong way when printed",
                    stack_pos=2, stack=changing_stack, author=elwood)

    dd_31 = Drawing(id_=18, drawing=open(os.path.join('data', 'drawings', 'dd_31.jpg'), 'rb').read(),
                    stack_pos=1, stack=changing_stack, author=david)
    dd_32 = Drawing(id_=19, drawing=open(os.path.join('data', 'drawings', 'dd_32.jpg'), 'rb').read(),
                    stack_pos=3, stack=olympics, author=david)

    nd_31 = Drawing(id_=20, drawing=open(os.path.join('data', 'drawings', 'nd_31.jpg'), 'rb').read(),
                    stack_pos=1, stack=fire_dice, author=nathan)
    nd_32 = Drawing(id_=21, drawing=open(os.path.join('data', 'drawings', 'nd_32.jpg'), 'rb').read(),
                    stack_pos=3, stack=changing_stack, author=nathan)

    ed_31 = Drawing(id_=22, drawing=open(os.path.join('data', 'drawings', 'ed_31.jpg'), 'rb').read(),
                    stack_pos=1, stack=olympics, author=elwood)
    ed_32 = Drawing(id_=23, drawing=open(os.path.join('data', 'drawings', 'ed_32.jpg'), 'rb').read(),
                    stack_pos=3, stack=fire_dice, author=elwood, created=hours_ago(-1))

    # Queue game
    q_dw = Writing(id_=24, text="Coming soon: yesterday",
                   stack_pos=0, stack=q_yesterday, author=david)
    q_nw = Writing(id_=25, text="Ender's Game",
                   stack_pos=0, stack=q_enders_game, author=nathan)
    q_ew = Writing(id_=26, text="An Awful Eiffel Tower",
                   stack_pos=0, stack=q_eiffel_tower, author=elwood)
    q_nd = Drawing(id_=24, drawing=open(os.path.join('data', 'drawings', 'nd_11.jpg'), 'rb').read(),
                   stack_pos=1, stack=q_yesterday, author=nathan, created=hours_ago(-2))

    # Reverse game
    r_dw = Writing(id_=27, text="Europeans waiting in line for food and communism",
                   stack_pos=0, stack=d_stack_reverse, author=david)
    r_nw = Writing(id_=28, text="Elworld. The Elwood,themed theme park",
                   stack_pos=0, stack=n_stack_reverse, author=nathan)
    r_ew = Writing(id_=29, text="A dinosaur texting his prey.",
                   stack_pos=0, stack=e_stack_reverse, author=elwood)

    # Draw first game
    df_ed = Drawing(id_=25, drawing=open(os.path.join('data', 'drawings', 'nd_21.jpg'), 'rb').read(),
                    stack_pos=0, stack=e_stack_drawfirst, author=elwood)

    # Partially done game
    dw_11_pd = Writing(id_=30, text="Coming soon: yesterday",
                       stack_pos=0, stack=pd_yesterday, author=david)
    dw_12_pd = Writing(id_=31, text="Be kind, bake your VHS tapes at 400 degrees for "
                            "20 minutes before returning",
                       stack_pos=2, stack=pd_enders_game, author=david)

    nw_11_pd = Writing(id_=32, text="Ender's Game",
                       stack_pos=0, stack=pd_enders_game, author=nathan)

    ew_11_pd = Writing(id_=33, text="An Awful Eiffel Tower",
                       stack_pos=0, stack=pd_eiffel_tower, author=elwood)
    ew_12_pd = Writing(id_=34, text="Passing an hour on the fourth Monday.",
                       stack_pos=2, stack=pd_yesterday, author=elwood)

    dd_11_pd = Drawing(id_=26, drawing=open(os.path.join('data', 'drawings', 'dd_11.jpg'), 'rb').read(),
                       stack_pos=1, stack=pd_eiffel_tower, author=david)

    nd_11_pd = Drawing(id_=27, drawing=open(os.path.join('data', 'drawings', 'nd_11.jpg'), 'rb').read(),
                       stack_pos=1, stack=pd_yesterday, author=nathan)

    ed_11_pd = Drawing(id_=28, drawing=open(os.path.join('data', 'drawings', 'ed_11.jpg'), 'rb').read(),
                       stack_pos=1, stack=pd_enders_game, author=elwood)

    with d.session_scope() as session:
        for ent in [david, nathan, elwood, queue_game, reverse_game, draw_first_game,
                    pending_game_1, pending_game_2]:
            session.add(ent)

if __name__ == '__main__':
    confirm = input('This will delete the current database. Continue? (y/n)\n')
    if confirm.lower().strip() != 'y':
        print('Cancelled')
        raise SystemExit

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--populate', action='store_true',
                        help='Populate with test data')
    args = parser.parse_args()

    print('Creating database')
    if os.path.isfile(Config.DBFILE):
        os.remove(Config.DBFILE)
    d = DB()
    d.create_schema()
    if args.populate:
        print('Populating database')
        populate_db(d)
