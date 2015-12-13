import collections
import functools
import itertools
import math
import random
import unittest

Tile = collections.namedtuple('Tile', ['id', 'terrain', 'value'])

class ClassicBoardTests(unittest.TestCase):

    def test_tile_iterator(self):
        options = {
            'randomize_production': False,
            'randomize_ports': False}
        board = Board(options)
        self.assertEqual([t.value for t in board.tiles if t.value], board._numbers)
        hexes = collections.Counter([t.terrain for t in board.tiles])
        self.assertEqual(hexes['F'], 4)
        self.assertEqual(hexes['P'], 4)
        self.assertEqual(hexes['H'], 4)
        self.assertEqual(hexes['M'], 3)
        self.assertEqual(hexes['C'], 3)
        self.assertEqual(hexes['D'], 1)


class Board:

    """Represents a single starting game board.

    Encapsulates the layout of the board (which tiles are connected to which),
    and the values of the tiles (including ports).

    Board.tiles() returns an iterable that gives the tiles in a guaranteed
    connected path that covers every node in the board graph.

    Board.direction(from, to) gives the compass direction you need to take to
    get from the origin tile to the destination tile.
    """

    def __init__(self, options, tiles=None, graph=None, center=1):
        """
        options is a dict names to boolean values.
        tiles and graph are for passing in a pre-defined set of tiles or a
        different graph for testing purposes.
        """
        self.options = options
        if (self.options['generate_empty']):
            self.tiles = self._generate_empty()
        else:
            self.tiles = tiles or self._generate()

        self.center_tile = self.tiles[center or 10]
        if graph:
            self._graph = graph

    def direction(self, from_tile, to_tile):
        return next(e[2] for e in self._edges_for(from_tile)
                               if e[1] == to_tile.id)

    def neighbors_for(self, tile):
        return [self.tiles[e[1] - 1] for e in self._edges_for(tile)]

    def _generate_empty(self):
        self.ports = [(tile, dir, value) for (tile, dir), value in zip(self._port_locations, list(self._ports))]
        empty_terrain = (['D'] * (4+4+4+3+3+1))
        empty_numbers = ([None] * (4+4+4+3+3+1))
        tile_data = list(zip(empty_terrain, empty_numbers))
        return [Tile(id=i, terrain=t, value=v) for i, (t, v) in enumerate(tile_data, 1)]

    def _generate(self):
        while True:
            terrain = list(self._terrain)
            numbers = list(self._numbers)
            ports   = list(self._ports)

            random.shuffle(terrain)
            if self.options['randomize_production']:
                random.shuffle(numbers)
            if self.options['randomize_ports']:
                random.shuffle(ports)

            self.ports = [(tile, dir, value) for (tile, dir), value in zip(self._port_locations, ports)]
            tile_data = list(zip(terrain, numbers))
            tile_data.insert(random.randrange(len(tile_data) + 1), ('D', None))
            if self.options['randomize_production'] and not self._check_red_placement(tile_data):
                continue
            return [Tile(id=i, terrain=t, value=v) for i, (t, v) in enumerate(tile_data, 1)]

    def _check_red_placement(self, tiles):
        for i1, i2, _ in self._graph:
            t1 = tiles[i1 - 1]
            t2 = tiles[i2 - 1]
            if all(t[1] in (6, 8) for t in [t1, t2]):
                return False
        return True

    def _edges_for(self, tile):
        return [e         for e in self._graph if e[0] == tile.id] + \
               [invert(e) for e in self._graph if e[1] == tile.id]

    _terrain = (['F'] * 4 + ['P'] * 4 + ['H'] * 4 + ['M'] * 3 + ['C'] * 3)
    _numbers = [5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11]
    _ports   = ['?', 'O', 'G', '?', 'L', '?', 'B', '?', 'W']
    # Ore, Wool, Grain, Lumber, Brick
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
