import logging

def direction_to_tile(from_tile, to_tile):
    coord_from = tile_id_to_coord(from_tile.tile_id)
    coord_to = tile_id_to_coord(to_tile.tile_id)
    direction = tile_tile_offset_to_direction(coord_to - coord_from)
    # logging.debug('Tile direction: {}->{} is {}'.format(
    #     from_tile.tile_id,
    #     to_tile.tile_id,
    #     direction
    # ))
    return direction

def tile_tile_offset_to_direction(offset):
    try:
        return _tile_tile_offsets[offset]
    except KeyError:
        logging.critical('Attempted getting direction of non-existent tile-tile offset={:x}'.format(offset))
        return 'ZZ'

def tile_node_offset_to_direction(offset):
    try:
        return _tile_node_offsets[offset]
    except KeyError:
        logging.critical('Attempted getting direction of non-existent tile-node offset={:x}'.format(offset))
        return 'ZZ'

def tile_edge_offset_to_direction(offset):
    try:
        return _tile_edge_offsets[offset]
    except KeyError:
        logging.critical('Attempted getting direction of non-existent tile-edge offset={:x}'.format(offset))
        return 'ZZ'

def tile_id_to_coord(tile_id):
    try:
        return _tile_id_to_coord[tile_id]
    except KeyError:
        logging.critical('Attempted conversion of non-existent tile_id={}'.format(tile_id))
        return -1

def tile_id_from_coord(coord):
    for i, c in _tile_id_to_coord.items():
        if c == coord:
            return i
    raise Exception('Tile id lookup failed, coord={} not found in map'.format(hex(coord)))

def nearest_tile_to_node(tile_ids, node_coord):
    """Takes a list of tile ids and a node coordinate.
    Returns the id of a tile which is touching the node"""
    for tile_id in tile_ids:
        if node_coord - tile_id_to_coord(tile_id) in _tile_node_offsets.keys():
            return tile_id

def nodes_touching_tile(tile_id):
    """Takes a tile id, returns a list of node coordinates touching the tile"""
    coord = tile_id_to_coord(tile_id)
    nodes = _tile_node_offsets.keys()
    for node in nodes:
        node += coord
    logging.debug('tile_id={}, nodes touching={}'.format(
        tile_id, nodes
    ))
    return nodes

def legal_node_coords():
    """Returns all legal node coordinates on the hexgrid"""
    nodes = set()
    for tile_id in legal_tile_ids():
        nodes.add(*nodes_touching_tile(tile_id))
    logging.debug('Legal node coords={}'.format(
        nodes
    ))
    return nodes

def legal_tile_ids():
    """Returns all legal tile ids on the hexgrid. 1-19"""
    return set(_tile_id_to_coord.keys())

def legal_tile_coords():
    """Returns all legal tile coordinates on the hexgrid"""
    return set(_tile_id_to_coord.values())

_tile_tile_offsets = {
    -0x20: 'NW',
    -0x22: 'W',
    -0x02: 'SW',
    +0x20: 'SE',
    +0x22: 'E',
    +0x02: 'NE',
}

_tile_node_offsets = {
    +0x01: 'N',
    -0x10: 'NW',
    -0x01: 'SW',
    +0x10: 'S',
    +0x21: 'SE',
    +0x12: 'NE',
}

_tile_edge_offsets = {
    -0x10: 'NW',
    -0x11: 'W',
    -0x01: 'SW',
    +0x10: 'SE',
    +0x11: 'E',
    +0x01: 'NE',
}

_tile_id_to_coord = {
    # 1-19 clockwise starting from Top-Left. See JSettlers2 dissertation.
    1: 0x37, 12: 0x59, 11: 0x7B,
    2: 0x35, 13: 0x57, 18: 0x79 , 10: 0x9B,
    3: 0x33, 14: 0x55, 19: 0x77, 17: 0x99, 9: 0xBB,
    4: 0x53, 15: 0x75, 16: 0x97, 8: 0xB9,
    5: 0x73, 6: 0x95, 7: 0xB7
}


