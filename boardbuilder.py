"""
module boardbuilder is responsible for creating starting board layouts.

It can create a variety of boards by supplying various options.

Use #build to build a new board with the passed options.

Use #modify to modify an existing board instead of building a new one.
This will reset the board. #reset is an alias.
"""
import logging
import random
import states
from models import Board, Terrain, HexNumber, Port, Tile, NUM_TILES, Piece, PieceType, Player


def get_opts(opts):
    _opts = { # defaults
              'terrain': 'empty', # random|empty|default
              'numbers': 'empty', # random|empty|default
              'ports': 'default', # random|empty|default
              'pieces': None
              }
    _opts.update(opts)
    return _opts

def build(opts=None):
    board = Board()
    modify(board, opts)
    return board

def reset(board, opts=None):
    modify(board, opts)

def modify(board, opts=None):
    opts = get_opts(opts)
    board.tiles = _generate_tiles(opts['terrain'], opts['numbers'])
    board.ports = _generate_ports(opts['ports'])
    board.state = states.BoardStateModifiable(board)
    board.pieces = _generate_pieces(opts['pieces'])

def _generate_tiles(terrain_opts, numbers_opts):
    terrain = None
    numbers = None

    if terrain_opts == 'empty':
        terrain = ([Terrain.desert] * NUM_TILES)
    elif terrain_opts in ['random', 'debug']:
        terrain = ([Terrain.desert] +
                   [Terrain.brick] * 3 +
                   [Terrain.ore] * 3 +
                   [Terrain.wood] * 4 +
                   [Terrain.sheep] * 4 +
                   [Terrain.wheat] * 4)
        random.shuffle(terrain)

    if numbers_opts == 'empty':
        numbers = ([HexNumber.none] * NUM_TILES)
    elif numbers_opts in ['random', 'debug']:
        numbers = ([HexNumber.two] +
                   [HexNumber.three]*2 + [HexNumber.four]*2 +
                   [HexNumber.five]*2 + [HexNumber.six]*2 +
                   [HexNumber.eight]*2 + [HexNumber.nine]*2 +
                   [HexNumber.ten]*2 + [HexNumber.eleven]*2 +
                   [HexNumber.twelve])
        random.shuffle(numbers)
        numbers.insert(terrain.index(Terrain.desert), HexNumber.none)

    assert len(numbers) == NUM_TILES
    assert len(terrain) == NUM_TILES

    tile_data = list(zip(terrain, numbers))
    tiles = [Tile(i, t, n) for i, (t, n) in enumerate(tile_data, 1)]

    return tiles

def _generate_ports(port_opts):
    if port_opts in ['default', 'debug']:
        return [(tile, dir, port) for (tile, dir), port in zip(_default_port_locations, list(_default_ports))]

def _generate_pieces(pieces_opts):
    if pieces_opts == 'empty':
        return dict()
    elif pieces_opts == 'debug':
        josh = Player(1, 'josh', 'blue')
        ross = Player(2, 'ross', 'red')
        yuri = Player(3, 'yuri', 'green')
        zach = Player(4, 'zach', 'orange')
        return {
            0x23: Piece(PieceType.settlement, josh),
            0x67: Piece(PieceType.settlement, ross),
            0x87: Piece(PieceType.settlement, yuri),
            0xA9: Piece(PieceType.city, zach),
        }

def _check_red_placement(tiles):
    logging.warning('"Check red placement" not yet implemented')

_default_port_locations = [(1, 'NW'), (2,  'W'),  (4,  'W' ),
                           (5, 'SW'), (6,  'SE'), (8,  'SE'),
                           (9, 'E' ), (10, 'NE'), (12, 'NE')]
_default_ports = [Port.any, Port.ore, Port.any, Port.sheep, Port.any, Port.wood, Port.brick, Port.any, Port.wheat]