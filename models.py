import collections
import states
import recording
from enum import Enum


class Game(object):

    def __init__(self, players: list, board, record: recording.GameRecord):
        self.players = players
        self.board = board
        self.record = record
        self._cur_player = None # set in #set_players
        self.last_roll = None # set in #roll

        self.state = states.GameStatePreGame(self)
        self.observers = set()
        self.board.observers.add(self)

    def notify(self, observable):
        self.notify_observers()

    def notify_observers(self):
        for obs in self.observers.copy():
            obs.notify(self)

    def reset(self):
        self.players = list()
        self.board.reset()
        self.record = recording.GameRecord()
        self.set_state(states.GameStatePreGame(self))

    def set_state(self, game_state: states.GameState):
        self.state = game_state
        if game_state.is_in_game():
            self.board.state = states.BoardStateLocked(self.board)
        else:
            self.board.state = states.BoardStateModifiable(self.board)
        self.notify_observers()

    def _set_dev_card_state(self, dev_state: states.DevCardPlayabilityState):
        self.state.dev_card_state = dev_state
        self.notify_observers()

    def start(self, players):
        self.set_players(players)
        self.set_state(states.GameStateInGame(self))

        terrain = list()
        numbers = list()
        ports = list()
        for tile in self.board.tiles:
            terrain.append(tile.terrain)
            numbers.append(tile.number)
        for _, _, port in self.board.ports:
            ports.append(port)
        self.record.record_pregame(self.players, terrain, numbers, ports)

    def end(self):
        self.set_state(states.GameStatePostGame(self))
        self.record.record_player_wins(self._cur_player)

    def get_cur_player(self):
        return Player(self._cur_player.seat, self._cur_player.name, self._cur_player.color)

    def set_players(self, players):
        self.players = list(players)
        self._cur_player = self.players[0]
        self.notify_observers()

    def roll(self, roll):
        self.record.record_player_roll(self._cur_player, roll)
        self.last_roll = roll
        self.set_state(states.GameStateRolled(self))

    def move_robber(self):
        # TODO actually move the robber instead of pretending
        self.set_state(states.GameStateMovedRobber(self))

    def steal(self):
        # TODO actually steal instead of pretending
        self.set_state(states.GameStateMovedRobberAndStole(self))

    def end_turn(self):
        self.record.record_player_ends_turn(self._cur_player)
        self._cur_player = self._next_player()
        self.set_state(states.GameStateTurnStart(self))
        self._set_dev_card_state(states.DevCardNotPlayedState(self))

    def _next_player(self):
        return self.players[self._cur_player.seat % len(self.players)]


class Tile(object):
    """
    Tiles are arranged in counter-clockwise order, spiralling inwards.
    The first tile is the top-left tile.
    """
    def __init__(self, tile_id, terrain, number):
        self.tile_id = tile_id
        self.terrain = terrain
        self.number = number

NUM_TILES = 3+4+5+4+3


class Terrain(Enum):
    wood = 'wood'
    brick = 'brick'
    wheat = 'wheat'
    sheep = 'sheep'
    ore = 'ore'
    desert = 'desert'


class HexNumber(Enum):
    none = None
    two = 2
    three = 3
    four = 4
    five = 5
    six = 6
    eight = 8
    nine = 9
    ten = 10
    eleven = 11
    twelve = 12


class Port(Enum):
    any = '3:1'
    wood = 'wood2:1'
    brick = 'brick2:1'
    wheat = 'wheat2:1'
    sheep = 'sheep2:1'
    ore = 'ore2:1'


class Player(object):
    """class Player represents a single player on the game board.
    :param seat: integer, with 1 being top left, and increasing clockwise
    :param name: will be lowercased, spaces will be removed
    :param color: will be lowercased, spaces will be removed
    """

    def __init__(self, seat, name, color):
        if not (1 <= seat <= 4):
            raise Exception("Seat must be on [1,4]")
        self.seat = seat

        self.name = name.lower().replace(' ', '')
        self.color = color.lower().replace(' ', '')

    def __eq__(self, other):
        return (self.color == other.color
                and self.name == other.name
                and self.seat == other.seat)


class Board(object):
    """Represents a single game board.

    Encapsulates
    - the layout of the board (which tiles are connected to which),
    - the values of the tiles (including ports)

    Board.tiles() returns an iterable that gives the tiles in a guaranteed
    connected path that covers every node in the board graph.

    Board.direction(from, to) gives the compass direction you need to take to
    get from the origin tile to the destination tile.
    """

    def __init__(self, tiles=None, ports=None, graph=None, center=1):
        """
        options is a dict names to boolean values.
        tiles and graph are for passing in a pre-defined set of tiles or a
        different graph for testing purposes.
        """
        self.tiles = None
        self.ports = None
        self.state = None
        self.reset(tiles=tiles, ports=ports)
        self.observers = set()

        self.center_tile = self.tiles[center or 10]
        if graph:
            self._graph = graph

    def notify_observers(self):
        for obs in self.observers:
            obs.notify(self)

    def reset(self, tiles=None, ports=None):
        self.tiles = tiles or self._generate_empty_tiles()
        self.ports = ports or self._generate_default_ports()
        self.state = states.BoardStateModifiable(self)

    def direction(self, from_tile, to_tile):
        return next(e[2] for e in self._edges_for(from_tile)
                    if e[1] == to_tile.tile_id)

    def neighbors_for(self, tile):
        return [self.tiles[e[1] - 1] for e in self._edges_for(tile)]

    def cycle_hex_type(self, tile_id):
        self.state.cycle_hex_type(tile_id)
        self.notify_observers()

    def cycle_hex_number(self, tile_id):
        self.state.cycle_hex_number(tile_id)
        self.notify_observers()

    def _generate_empty_tiles(self):
        empty_terrain = ([Terrain.desert] * NUM_TILES)
        empty_numbers = ([HexNumber.none] * NUM_TILES)
        tile_data = list(zip(empty_terrain, empty_numbers))
        return [Tile(i, t, n) for i, (t, n) in enumerate(tile_data, 1)]

    def _generate_default_ports(self):
        return [(tile, dir, port) for (tile, dir), port in zip(self._port_locations, list(self._default_ports))]

    def _check_red_placement(self, tiles):
        for i1, i2, _ in self._graph:
            t1 = tiles[i1 - 1]
            t2 = tiles[i2 - 1]
            if all(t[1] in (6, 8) for t in [t1, t2]):
                return False
        return True

    def _edges_for(self, tile):
        return [e         for e in self._graph if e[0] == tile.tile_id] + \
               [invert(e) for e in self._graph if e[1] == tile.tile_id]

    _default_ports = [Port.any, Port.ore, Port.any, Port.sheep, Port.any, Port.wood, Port.brick, Port.any, Port.wheat]
    _graph = [(1,  2,  'SW'), (1,  12, 'E' ), (1,  13, 'SE'),
              (2,  3,  'SW'), (2,  13, 'E' ), (2,  14, 'SE'),
              (3,  4,  'SE'), (3,  14, 'E' ),
              (4,  5,  'SE'), (4,  14, 'NE'), (4,  15, 'E' ),
              (5,  6,  'E' ), (5,  15, 'NE'),
              (6,  7,  'E' ), (6,  15, 'NW'), (6,  16, 'NE'),
              (7,  8,  'NE'), (7,  16, 'NW'),
              (8,  9,  'NE'), (8,  16, 'W' ), (8,  17, 'NW'),
              (9,  10, 'NW'), (9,  17, 'W' ),
              (10, 11, 'NW'), (10, 17, 'SW'), (10, 18, 'W' ),
              (11, 12, 'W' ), (11, 18, 'SW'),
              (12, 13, 'SW'), (12, 18, 'SE'),
              (13, 14, 'SW'), (13, 18, 'E' ), (13, 19, 'SE'),
              (14, 15, 'SE'), (14, 19, 'E' ),
              (15, 16, 'E' ), (15, 19, 'NE'),
              (16, 17, 'NE'), (16, 19, 'NW'),
              (17, 18, 'NW'), (17, 19, 'W' ),
              (18, 19, 'SW')]
    _port_locations = [(1, 'NW'), (2,  'W'),  (4,  'W' ),
                       (5, 'SW'), (6,  'SE'), (8,  'SE'),
                       (9, 'E' ), (10, 'NE'), (12, 'NE')]

_direction_pairs = {
    'E': 'W', 'SW': 'NE', 'SE': 'NW',
    'W': 'E', 'NE': 'SW', 'NW': 'SE'}


def invert(edge):
    return (edge[1], edge[0], _direction_pairs[edge[2]])

