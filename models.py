import logging
import states
import recording
from enum import Enum


class Game(object):

    def __init__(self, players=None, board=None, record=None):
        self.observers = set()
        self.players = players or list()
        self.board = board or Board()
        self.record = record or recording.GameRecord()

        self.state = None
        self._cur_player = None # set in #set_players
        self.last_roll = None # set in #roll
        self.last_player_to_roll = None # set in #roll
        self._cur_turn = 0 # incremented in #end_turn
        self.robber_tile = None # set in #move_robber

        self.board.observers.add(self)

        self.set_state(states.GameStateNotInGame(self))
        self.set_dev_card_state(states.DevCardNotPlayedState(self))

    def notify(self, observable):
        self.notify_observers()

    def notify_observers(self):
        for obs in self.observers.copy():
            obs.notify(self)

    def reset(self):
        self.players = list()
        self.board.reset()
        self.record = recording.GameRecord()
        self.state = None

        self.last_roll = None
        self.last_player_to_roll = None
        self._cur_player = None
        self._cur_turn = 0

        self.set_state(states.GameStateNotInGame(self))

    def set_state(self, game_state: states.GameState):
        logging.info('now {0}, was {1}'.format(
            type(game_state).__name__,
            type(self.state).__name__
        ))
        self.state = game_state
        if game_state.is_in_game():
            self.board.state = states.BoardStateLocked(self.board)
        else:
            self.board.state = states.BoardStateModifiable(self.board)
        self.notify_observers()

    def set_dev_card_state(self, dev_state: states.DevCardPlayabilityState):
        self.dev_card_state = dev_state
        self.notify_observers()

    def start(self, players):
        self.set_players(players)
        self.set_state(states.GameStatePreGamePlaceSettlement(self))

        terrain = list()
        numbers = list()
        ports = list()
        for tile in self.board.tiles:
            terrain.append(tile.terrain)
            numbers.append(tile.number)
        for _, _, port in self.board.ports:
            ports.append(port)
        self.record.record_initial_game_info(self.players, terrain, numbers, ports)

    def end(self):
        self.set_state(states.GameStateNotInGame(self))
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
        self.last_player_to_roll = self._cur_player
        if int(roll) == 7:
            self.set_state(states.GameStateMoveRobber(self))
        else:
            self.set_state(states.GameStateDuringTurnAfterRoll(self))

    def move_robber(self, tile):
        self.state.move_robber(tile)

    def steal(self, victim):
        victim = Player(1, "name", "color") # todo use real victim
        self.state.steal(victim)

    def buy_road(self, node_from, node_to):
        #self.assert_legal_road(node_from, node_to)
        self.record.record_player_buys_road(self._cur_player, node_from, node_to)
        if self.state.is_in_pregame():
            self.end_turn()

    def buy_settlement(self, node):
        #self.assert_legal_settlement(node)
        self.record.record_player_buys_settlement(self._cur_player, node)
        if self.state.is_in_pregame():
            self.set_state(states.GameStatePreGamePlaceRoad(self))

    def buy_city(self, node):
        self.record.record_player_buys_city(self._cur_player, node)

    def buy_dev_card(self):
        self.record.record_player_buys_dev_card(self._cur_player)

    def play_knight(self):
        self.set_dev_card_state(states.DevCardPlayedState(self))
        self.set_state(states.GameStateMoveRobberUsingKnight(self))

    def play_monopoly(self, resource):
        self.set_dev_card_state(states.DevCardPlayedState(self))
        self.record.record_player_plays_dev_monopoly(self._cur_player, resource)

    def play_road_builder(self, node_a1, node_a2, node_b1, node_b2):
        self.set_dev_card_state(states.DevCardPlayedState(self))
        self.record.record_player_plays_dev_road_builder(self._cur_player,
                                                         node_a1, node_a2,
                                                         node_b1, node_b2)

    def play_victory_point(self):
        self.set_dev_card_state(states.DevCardPlayedState(self))
        self.record.record_player_plays_dev_victory_point(self._cur_player)

    def end_turn(self):
        self.record.record_player_ends_turn(self._cur_player)
        self._cur_player = self.state.next_player()
        self._cur_turn += 1

        self.set_dev_card_state(states.DevCardNotPlayedState(self))
        if self.state.is_in_pregame():
            self.set_state(states.GameStatePreGamePlaceSettlement(self))
        else:
            self.set_state(states.GameStateBeginTurn(self))


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
        if other is None:
            return False
        return (self.color == other.color
                and self.name == other.name
                and self.seat == other.seat)

    def __repr__(self):
        return '{} ({})'.format(self.color, self.name)


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
    def __init__(self, terrain=None, ports=None, pieces=None, center=1):
        """
        method Board creates a new board.
        :param tiles:
        :param ports:
        :param graph:
        :param center:
        :return:
        """
        self.tiles = None
        self.ports = None
        self.state = None
        self.pieces = None
        self.reset(terrain=terrain, ports=ports, pieces=pieces)
        self.observers = set()

        self.center_tile = self.tiles[center or 10]

    def notify_observers(self):
        for obs in self.observers:
            obs.notify(self)

    def reset(self, terrain=None, numbers=None, ports=None, pieces=None):
        import boardbuilder
        boardbuilder.reset(self, opts={
            'terrain': terrain or 'empty', # random|empty|default
            'numbers': numbers or 'empty', # random|empty|default
            'ports': ports or 'default', # random|empty|default
        })

    def place_piece(self, piece, coord):
        logging.warning('"Place piece" not implemented')

    def cycle_hex_type(self, tile_id):
        self.state.cycle_hex_type(tile_id)
        self.notify_observers()

    def cycle_hex_number(self, tile_id):
        self.state.cycle_hex_number(tile_id)
        self.notify_observers()

    def direction_to_tile(self, from_tile, to_tile):
        coord_from = self._tile_id_to_coord[from_tile.tile_id]
        coord_to = self._tile_id_to_coord[to_tile.tile_id]
        offset = coord_to - coord_from
        return self._tile_offset_map[offset]

    def adjacent_tiles(self, tile):
        coord = self.tile_coord(tile)
        # clockwise from top-left. See Appendix A of JSettlers2 dissertation
        adjacent_coords = [coord-0x20, coord-0x22, coord-0x02,
                           coord+0x20, coord+0x22, coord+0x02]
        legal_coords = self._legal_tile_coords()
        adjacent_coords = [coord for coord in adjacent_coords
                           if coord in legal_coords]
        adjacent_tiles = map(self._tile_id_from_coord, adjacent_coords)
        logging.debug('tile={}, adjacent_tiles={}'.format(tile, adjacent_tiles))
        return adjacent_tiles

    def adjacent_nodes(self, tile):
        coord = self.tile_coord(tile)
        # clockwise from top. See Appendix A of JSettlers2 dissertation
        adjacent_coords = [coord+0x01, coord-0x10, coord-0x01,
                           coord+0x10, coord+0x21, coord+0x12]
        return adjacent_coords

    def _legal_tile_coords(self):
        return set(self._tile_id_to_coord.values())

    def tile_coord(self, tile):
        if tile.tile_id not in self._tile_id_to_coord:
            raise Exception('Tile coord conversion failed, tile_id={} not found in map'.format(
                tile.tile_id
            ))
        return self._tile_id_to_coord[tile.tile_id]

    def _tile_id_from_coord(self, coord):
        for i, c in self._tile_id_to_coord.items():
            if c == coord:
                return i
        raise Exception('Tile id lookup failed, coord={} not found in map'.format(
            hex(coord)
        ))

    _tile_offset_map = {
        -0x20: 'NW',
        -0x22: 'W',
        -0x02: 'SW',
        +0x20: 'SE',
        +0x22: 'E',
        +0x02: 'NE'
    }

    # 1-19 clockwise starting from Top-Left. See JSettlers2 dissertation.
    _tile_id_to_coord = {
        1: 0x37, 12: 0x59, 11: 0x7B,
        2: 0x35, 13: 0x57, 18: 0x79 , 10: 0x9B,
        3: 0x33, 14: 0x55, 19: 0x77, 17: 0x99, 9: 0xBB,
        4: 0x53, 15: 0x75, 16: 0x97, 8: 0xB9,
        5: 0x73, 6: 0x95, 7: 0xB7
    }
