"""
module boardbuilder is responsible for creating starting board layouts.

It can create a variety of boards by supplying various options.

Use #build to build a new board with the passed options.

Use #modify to modify an existing board instead of building a new one.
This will reset the board. #reset is an alias.
"""
import logging
from enum import Enum
import pprint
import random
import hexgrid
import states
from models import Board, Terrain, HexNumber, Port, Tile, NUM_TILES, Piece, PieceType, Player


class Opts(Enum):
    empty = 'empty'
    random = 'random'
    preset = 'preset'
    debug = 'debug'

    def __repr__(self):
        return 'opt:{}'.format(self.value)


def get_opts(opts):
    defaults = {
        'terrain': Opts.empty,
        'numbers': Opts.empty,
        'ports': Opts.preset,
        'pieces': Opts.preset,
    }
    _opts = defaults.copy()
    if opts is None:
        opts = dict()
    try:
        for key, val in opts.copy().items():
            opts[key] = Opts(val)
        _opts.update(opts)
    except Exception:
        raise ValueError('Invalid options={}'.format(opts))
    logging.debug('used defaults=\n{}\n on opts=\n{}\nreturned total opts=\n{}'.format(
        pprint.pformat(defaults),
        pprint.pformat(opts),
        pprint.pformat(_opts)))
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
    board.pieces = _generate_pieces(board.tiles, board.ports, opts['pieces'])

def _generate_tiles(terrain_opts, numbers_opts):
    terrain = None
    numbers = None

    if terrain_opts == Opts.empty:
        terrain = ([Terrain.desert] * NUM_TILES)
    elif terrain_opts in (Opts.random, Opts.debug):
        terrain = ([Terrain.desert] +
                   [Terrain.brick] * 3 +
                   [Terrain.ore] * 3 +
                   [Terrain.wood] * 4 +
                   [Terrain.sheep] * 4 +
                   [Terrain.wheat] * 4)
        random.shuffle(terrain)
    elif terrain_opts == Opts.preset:
        terrain = ([Terrain.desert] * NUM_TILES)
        logging.warning('Preset terrain option not yet implemented')

    if numbers_opts == Opts.empty:
        numbers = ([HexNumber.none] * NUM_TILES)
    elif numbers_opts in (Opts.random, Opts.debug):
        numbers = ([HexNumber.two] +
                   [HexNumber.three]*2 + [HexNumber.four]*2 +
                   [HexNumber.five]*2 + [HexNumber.six]*2 +
                   [HexNumber.eight]*2 + [HexNumber.nine]*2 +
                   [HexNumber.ten]*2 + [HexNumber.eleven]*2 +
                   [HexNumber.twelve])
        random.shuffle(numbers)
        numbers.insert(terrain.index(Terrain.desert), HexNumber.none)
    elif numbers_opts == Opts.preset:
        numbers = ([HexNumber.none] * NUM_TILES)
        logging.warning('Preset numbers option not yet implemented')

    assert len(numbers) == NUM_TILES
    assert len(terrain) == NUM_TILES

    tile_data = list(zip(terrain, numbers))
    tiles = [Tile(i, t, n) for i, (t, n) in enumerate(tile_data, 1)]

    return tiles

def _generate_ports(port_opts):
    if port_opts in [Opts.preset, Opts.debug]:
        return [(tile, dir, port) for (tile, dir), port in zip(_default_port_locations, list(_default_ports))]
    elif port_opts in ['empty, random']:
        logging.warning('{} option not yet implemented'.format(port_opts))
        return []

def _generate_pieces(tiles, ports, pieces_opts):
    if pieces_opts == Opts.empty:
        return dict()
    elif pieces_opts == Opts.debug:
        josh = Player(1, 'josh', 'blue')
        ross = Player(2, 'ross', 'red')
        yuri = Player(3, 'yuri', 'green')
        zach = Player(4, 'zach', 'orange')
        return {
            (hexgrid.NODE, 0x23): Piece(PieceType.settlement, josh),
            (hexgrid.EDGE, 0x22): Piece(PieceType.road, josh),
            (hexgrid.NODE, 0x67): Piece(PieceType.settlement, ross),
            (hexgrid.EDGE, 0x98): Piece(PieceType.road, ross),
            (hexgrid.NODE, 0x87): Piece(PieceType.settlement, yuri),
            (hexgrid.EDGE, 0x89): Piece(PieceType.road, yuri),
            (hexgrid.EDGE, 0xA9): Piece(PieceType.road, zach),
            (hexgrid.TILE, 0x77): Piece(PieceType.robber, None),
        }
    elif pieces_opts in (Opts.preset, ):
        desert = filter(lambda tile: tile.terrain == Terrain.desert, tiles)[0]
        coord = hexgrid.tile_id_to_coord(desert.tile_id)
        return {
            (hexgrid.TILE, coord): Piece(PieceType.robber, None)
        }
    elif pieces_opts in (Opts.random, ):
        logging.warning('{} option not yet implemented'.format(pieces_opts))

def _check_red_placement(tiles):
    logging.warning('"Check red placement" not yet implemented')

_default_port_locations = [(1, 'NW'), (2,  'W'),  (4,  'W' ),
                           (5, 'SW'), (6,  'SE'), (8,  'SE'),
                           (9, 'E' ), (10, 'NE'), (12, 'NE')]
_default_ports = [Port.any, Port.ore, Port.any, Port.sheep, Port.any, Port.wood, Port.brick, Port.any, Port.wheat]