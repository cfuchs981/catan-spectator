"""
module boardbuilder is responsible for creating starting board layouts.

It can create a variety of boards by supplying various options.

Use #build to build a new board with the passed options.

Use #modify to modify an existing board instead of building a new one.
This will reset the board. #reset is an alias.
"""
import states
from models import Board, Terrain, HexNumber, Tile, NUM_TILES

def get_opts(opts):
    _opts = { # defaults
              'terrain': 'empty', # random|empty|default
              'numbers': 'empty', # random|empty|default
              'ports': 'default', # random|empty|default
              }
    _opts.update(opts)
    return _opts

def build(opts=None):
    board = Board()
    opts = get_opts(opts)
    board.tiles = _generate_tiles(opts['terrain'], opts['numbers'])
    board.ports = _generate_ports(opts['ports'])
    board.state = states.BoardStateModifiable(board)
    return board

def reset(board, opts=None):
    modify(board, opts)

def modify(board, opts=None):
    opts = get_opts(opts)
    board.tiles = _generate_tiles(opts['terrain'], opts['numbers'])
    board.ports = _generate_ports(opts['ports'])
    board.state = states.BoardStateModifiable(board)

def _generate_tiles(terrain_opts, numbers_opts):
    terrain = None
    numbers = None
    tiles = None

    if terrain_opts == 'empty':
        terrain = ([Terrain.desert] * NUM_TILES)


    if numbers_opts == 'empty':
        numbers = ([HexNumber.none] * NUM_TILES)

    tile_data = list(zip(terrain, numbers))
    tiles = [Tile(i, t, n) for i, (t, n) in enumerate(tile_data, 1)]

    return tiles

def _generate_ports(port_opts):
    if port_opts == 'default':
        return [(tile, dir, port) for (tile, dir), port in zip(self._port_locations, list(self._default_ports))]

def _check_red_placement(tiles):
    for i1, i2, _ in _graph:
        t1 = tiles[i1 - 1]
        t2 = tiles[i2 - 1]
        if all(t[1] in (6, 8) for t in [t1, t2]):
            return False
    return True
