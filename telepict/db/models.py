from datetime import datetime
import operator
import base64

from sqlalchemy import Column, Integer, String, ForeignKey, Text, SmallInteger, \
    Boolean, LargeBinary, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from .base import Base
from ..auth import gen_password_hash_and_salt

def assn(game_class):
    d = {'__tablename__': f'{game_class.__tablename__}_players',
         'player_order': Column('player_order', SmallInteger, nullable=False, default=1),
         'game_id': Column('game_id', Integer, ForeignKey(f'{game_class.__tablename__}.id'),
                           primary_key=True),
         'game': relationship(game_class.__name__, back_populates='players_'),
         'player_id': Column('player_id', Integer, ForeignKey('players.id'), primary_key=True),
         'player': relationship('Player', back_populates=f'{game_class.__tablename__}_'),
         '__repr__':lambda s: f'{s.__class__.__name__}{s.game_id}/'
                              f'{s.player.name}#{s.player_order}'}

    return type(f'{game_class.__name__}PlayerAssn', (Base,), d)


class Game(Base):
    __tablename__ = 'games'

    id_ = Column('id', Integer, primary_key=True)
    started = Column('started', DateTime, default=datetime.utcnow)
    num_rounds = Column('num_rounds', SmallInteger, default=1)
    pass_left = Column('pass_left', Boolean, default=True)
    write_first = Column('write_first', Boolean, default=True)

    players_ = relationship('GamePlayerAssn', back_populates='game', cascade='all')
    stacks_ = relationship('Stack', back_populates='game')

    @ property
    def complete(self):
        target_len = len(self.players_) * self.num_rounds
        return all(len(s.stack) == target_len for s in self.stacks)

    @property
    def players(self):
        return [a.player for a in sorted(self.players_, key=operator.attrgetter('player_order'))]

    @property
    def stacks(self):
        stack_mapping = {s.owner_id: s for s in self.stacks_}
        return [stack_mapping[player.id_] for player in self.players]

    @property
    def last_move(self):
        max_time = None
        for stack in self.stacks:
            for ent in stack.stack:
                if max_time is None or ent.created > max_time:
                    max_time = ent.created
        return max_time

    def get_adjacent_player(self, player, next_=True):
        player_ids = [p.id_ for p in self.players]
        idx = player_ids.index(player.id_)
        if idx is None:
            return None

        target_idx = idx + (1 if self.pass_left else -1) * (1 if next_ else -1)
        return self.players[target_idx % len(self.players_)]

    def player_stack(self, player):
        for s in self.stacks_:
            if s.owner_id == player.id_:
                return s
        return None

    def __init__(self, *args, **kwargs):
        if 'players' in kwargs:
            players = kwargs.pop('players')
            players_ = kwargs['players_'] = list()
            for i, player in enumerate(players):
                players_.append(GamePlayerAssn(player_order=i, player=player, game=self))
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.players}, {self.num_rounds}, ' \
               f'{self.pass_left}, {self.write_first})'


class PendingGame(Base):
    __tablename__ = 'pending_games'

    id_ = Column('id', Integer, primary_key=True)
    created = Column('created', DateTime, default=datetime.utcnow)
    creator_id = Column('creator', Integer, ForeignKey('players.id'), nullable=False)
    creator = relationship('Player')
    num_rounds = Column('num_rounds', SmallInteger, default=1)
    pass_left = Column('pass_left', Boolean, default=True)
    write_first = Column('write_first', Boolean, default=True)

    invitations = relationship('Invitation', back_populates='game', cascade='all')
    players_ = relationship('PendingGamePlayerAssn', back_populates='game',
                            cascade='all')

    @property
    def players(self):
        return [a.player for a in sorted(self.players_, key=operator.attrgetter('player_order'))]

    def __init__(self, *args, **kwargs):
        if 'players' in kwargs:
            players = kwargs.pop('players')
            players_ = kwargs['players_'] = list()
            for i, player in enumerate(players):
                players_.append(PendingGamePlayerAssn(player_order=i, player=player, game=self))
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.players}, {self.num_rounds}, ' \
               f'{self.pass_left}, {self.write_first})'


class Invitation(Base):
    __tablename__ = 'invitations'

    created = Column('created', DateTime, default=datetime.utcnow)
    game_id = Column('game_id', Integer, ForeignKey('pending_games.id'), primary_key=True)
    game = relationship('PendingGame', back_populates='invitations')

    recipient_id = Column('recipient_id', Integer, ForeignKey('players.id'), primary_key=True)
    recipient = relationship('Player', back_populates='invitations')

    def __repr__(self):
        return f'Invitation({self.recipient} -> {self.game})'


class Player(Base):
    __tablename__ = 'players'

    id_ = Column('id', Integer, primary_key=True)
    created = Column('created', DateTime, default=datetime.utcnow)
    name = Column('name', String(64), nullable=False, unique=True, index=True)
    display_name = Column('display_name', String(64), nullable=False)
    password_hash = Column('password_hash', LargeBinary(64), nullable=False)
    password_salt = Column('password_salt', LargeBinary(64), nullable=False)
    timezone = Column('timezone', String(32), nullable=False, default='UTC')

    games_ = relationship('GamePlayerAssn', back_populates='player', cascade='all')
    pending_games_ = relationship('PendingGamePlayerAssn', back_populates='player', cascade='all')
    invitations = relationship('Invitation', back_populates='recipient', cascade='all')

    @property
    def games(self):
        return sorted([a.game for a in self.games_], key=operator.attrgetter('id_'))

    @property
    def pending_games(self):
        return sorted([a.game for a in self.pending_games_], key=operator.attrgetter('id_'))

    def __init__(self, *args, **kwargs):
        if 'password' in kwargs:
            # Convert password to hash and salt
            pwd = kwargs.pop('password')
            hash_, salt = gen_password_hash_and_salt(pwd)
            kwargs.update({'password_hash': hash_, 'password_salt': salt})
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'{self.name}({self.display_name})'

    def __eq__(self, other):
        return isinstance(other, Player) and self.id_ == other.id_

GamePlayerAssn = assn(Game)
PendingGamePlayerAssn = assn(PendingGame)


class Stack(Base):
    __tablename__ = 'stacks'

    id_ = Column('id', Integer, primary_key=True)

    game_id = Column('game_id', Integer, ForeignKey('games.id'), nullable=False)
    game = relationship('Game', back_populates='stacks_')
    owner_id = Column('owner_id', Integer, ForeignKey('players.id'), nullable=False)
    owner = relationship('Player')

    writings = relationship('Writing', back_populates='stack', cascade='all')
    drawings = relationship('Drawing', back_populates='stack', cascade='all')

    @staticmethod
    def _sort(stk):
        return sorted(stk, key=operator.attrgetter('stack_pos'))

    @property
    def stack(self):
        return self._sort(self.writings + self.drawings)

    @property
    def last(self):
        last_writing = self._sort(self.writings)[-1] if self.writings else None
        last_drawing = self._sort(self.drawings)[-1] if self.drawings else None
        if last_writing is None:
            return last_drawing
        if last_drawing is None:
            return last_writing
        return last_writing if last_writing.stack_pos > last_drawing.stack_pos \
            else last_drawing

    def __len__(self):
        return len(self.writings) + len(self.drawings)

    def __repr__(self):
        return f'Stack({self.owner.name}, {self.stack!s})'


class PaperMixin:
    id_ = Column('id', Integer, primary_key=True)
    created = Column('created', DateTime, default=datetime.utcnow)
    @declared_attr
    def author_id(self):
        return Column('author_id', Integer, ForeignKey('players.id'), nullable=False)
    @declared_attr
    def author(self):
        return relationship('Player')
    stack_pos = Column('stack_pos', SmallInteger)

    @declared_attr
    def stack_id(self):
        return Column('stack', Integer, ForeignKey('stacks.id'))

    @property
    def game(self):
        return self.stack.game


class Writing(Base, PaperMixin):
    __tablename__ = 'writings'

    stack = relationship('Stack', back_populates='writings')
    text = Column('text', Text, nullable=False)

    def __init__(self, *args, **kwargs):
        if 'stack' in kwargs and 'stack_pos' not in kwargs:
            kwargs['stack_pos'] = len(kwargs['stack'])
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'Writing({self.author.name}, {self.text!r}, pos={self.stack_pos})'


class Drawing(Base, PaperMixin):
    __tablename__ = 'drawings'

    stack = relationship('Stack', back_populates='drawings')
    drawing = Column('drawing', LargeBinary, nullable=False)

    @property
    def data_url(self):
        img_data = base64.b64encode(self.drawing).decode('utf8')
        return f'data:image/jpeg;base64,{img_data}'

    def __init__(self, *args, **kwargs):
        if 'stack' in kwargs and 'stack_pos' not in kwargs:
            kwargs['stack_pos'] = len(kwargs['stack'])
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'Drawing({self.author.name}, pos={self.stack_pos})'
