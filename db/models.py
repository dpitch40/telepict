import enum
from datetime import datetime
import operator

from sqlalchemy import Table, Column, Integer, String, ForeignKey, Text, SmallInteger, Enum, \
    Boolean, LargeBinary, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from db.base import Base
from auth import gen_password_hash_and_salt

class Directions(enum.Enum):
    left = 1
    right = 2

def Assn(game_class):
    d = {'__tablename__': f'{game_class.__tablename__}_players',
         'player_order': Column('player_order', SmallInteger, nullable=False, default=1),
         'game_id': Column('game_id', Integer, ForeignKey(f'{game_class.__tablename__}.id'), primary_key=True),
         'game': relationship(game_class.__name__, back_populates='players_'),
         'player_id': Column('player_id', Integer, ForeignKey('players.id'), primary_key=True),
         'player': relationship('Player', back_populates=f'{game_class.__tablename__}_'),
         '__repr__': lambda s: f'{s.__class__.__name__}{s.game_id}/{s.player.name}#{s.player_order}'}

    return type(f'{game_class.__name__}PlayerAssn', (Base,), d)

class Game(Base):
    __tablename__ = 'games'

    id_ = Column('id', Integer, primary_key=True)
    started = Column('started', DateTime, default=datetime.now)
    num_rounds = Column('num_rounds', SmallInteger, default=1)
    direction = Column('direction', Enum(Directions), default=Directions.left)
    write_first = Column('write_first', Boolean, default=True)

    players_ = relationship('GamePlayerAssn', back_populates='game')

    @property
    def players(self):
        return [a.player for a in sorted(self.players_, key=operator.attrgetter('player_order'))]

    stacks_ = relationship('Stack', back_populates='game')

    @property
    def stacks(self):
        stack_mapping = {s.owner_id: s for s in self.stacks_}
        return [stack_mapping[player.id_] for player in self.players]

    @property
    def last_move(self):
        max_time = datetime(1970, 1, 1, 0, 0, 0)
        for stack in self.stacks:
            for ent in stack.stack:
                if ent.created > max_time:
                    max_time = ent.created
        return max_time

    def player_stack(self, player):
        for s in self.stacks_:
            if s.owner_id == player.id_:
                return s

    @ property
    def complete(self):
        target_len = len(self.players_) * self.num_rounds
        return all([len(s.stack) == target_len for s in self.stacks])

    def __init__(self, *args, **kwargs):
        if 'players' in kwargs:
            players = kwargs.pop('players')
            players_ = kwargs['players_'] = list()
            for i, player in enumerate(players):
                players_.append(GamePlayerAssn(player_order=i, player=player, game=self))
        return super(Game, self).__init__(*args, **kwargs)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.players}, {self.num_rounds}, ' \
               f'{self.direction}, {self.write_first})'

class PendingGame(Base):
    __tablename__ = 'pending_games'

    id_ = Column('id', Integer, primary_key=True)
    created = Column('created', DateTime, default=datetime.now)
    num_rounds = Column('num_rounds', SmallInteger, default=1)
    direction = Column('direction', Enum(Directions), default=Directions.left)
    write_first = Column('write_first', Boolean, default=True)

    invitations = relationship('Invitation', back_populates='game')

    players_ = relationship('PendingGamePlayerAssn', back_populates='game')

    @property
    def players(self):
        return [a.player for a in sorted(self.players_, key=operator.attrgetter('player_order'))]

    def __init__(self, *args, **kwargs):
        if 'players' in kwargs:
            players = kwargs.pop('players')
            players_ = kwargs['players_'] = list()
            for i, player in enumerate(players):
                players_.append(PendingGamePlayerAssn(player_order=i, player=player, game=self))
        return super(PendingGame, self).__init__(*args, **kwargs)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.players}, {self.num_rounds}, ' \
               f'{self.direction}, {self.write_first})'

class Invitation(Base):
    __tablename__ = 'invitations'

    id_ = Column('id', Integer, primary_key=True)
    created = Column('created', DateTime, default=datetime.now)
    game_id = Column('game_id', Integer, ForeignKey('pending_games.id'), nullable=False)
    game = relationship('PendingGame', back_populates='invitations')

    recipient_id = Column('recipient_id', Integer, ForeignKey('players.id'), nullable=False)
    recipient = relationship('Player', back_populates='invitations')

    def __repr__(self):
        return f'Invitation({self.player} -> {self.game})'

class Player(Base):
    __tablename__ = 'players'

    id_ = Column('id', Integer, primary_key=True)
    created = Column('created', DateTime, default=datetime.now)
    name = Column('name', String(64), nullable=False, unique=True, index=True)
    display_name = Column('display_name', String(64), nullable=False)
    password_hash = Column('password_hash', LargeBinary(64), nullable=False)
    password_salt = Column('password_salt', LargeBinary(64), nullable=False)
    # email = Column('email', String(128), nullable=False)

    games_ = relationship('GamePlayerAssn', back_populates='player')
    @property
    def games(self):
        return sorted([a.game for a in self.games_], key=operator.attrgetter('id_'))

    pending_games_ = relationship('PendingGamePlayerAssn', back_populates='player')
    @property
    def pending_games(self):
        return sorted([a.game for a in self.pending_games_], key=operator.attrgetter('id_'))

    invitations = relationship('Invitation', back_populates='recipient')
    
    def __init__(self, *args, **kwargs):
        if 'password' in kwargs:
            # Convert password to hash and salt
            pwd = kwargs.pop('password')
            hash_, salt = gen_password_hash_and_salt(pwd)
            kwargs.update({'password_hash': hash_, 'password_salt': salt})
        return super(Player, self).__init__(*args, **kwargs)

    def __repr__(self):
        return f'{self.name}({self.display_name})'

GamePlayerAssn = Assn(Game)
PendingGamePlayerAssn = Assn(PendingGame)

class Stack(Base):
    __tablename__ = 'stacks'

    id_ = Column('id', Integer, primary_key=True)

    game_id = Column('game_id', Integer, ForeignKey('games.id'), nullable=False)
    game = relationship('Game', back_populates='stacks_')

    owner_id = Column('owner_id', Integer, ForeignKey('players.id'), nullable=False)
    owner = relationship('Player')

    writings = relationship('Writing', back_populates='stack')
    drawings = relationship('Drawing', back_populates='stack')

    @property
    def stack(self):
        return sorted(self.writings + self.drawings, key=operator.attrgetter('stack_pos'))

    def __repr__(self):
        return f'Stack({self.owner.name}, {len(self.stack)})'

class PaperMixin:
    id_ = Column('id', Integer, primary_key=True)
    created = Column('created', DateTime, default=datetime.now)
    @declared_attr
    def author_id(self):
        return Column('author_id', Integer, ForeignKey('players.id'), nullable=False)
    @declared_attr
    def author(self):
        return relationship('Player')
    stack_pos = Column('stack_pos', SmallInteger, nullable=False)

    @declared_attr
    def stack_id(self):
        return Column('stack', Integer, ForeignKey('stacks.id'), nullable=False)

    @property
    def game(self):
        return self.stack.game

class Writing(Base, PaperMixin):
    __tablename__ = 'writings'

    stack = relationship('Stack', back_populates='writings')
    text = Column('text', Text, nullable=False)

class Drawing(Base, PaperMixin):
    __tablename__ = 'drawing'

    stack = relationship('Stack', back_populates='drawings')
    drawing = Column('drawing', LargeBinary, nullable=False)
