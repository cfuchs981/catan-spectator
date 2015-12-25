import logging

def direction_to_tile(self, from_tile, to_tile):
    coord_from = tile_id_to_coord(from_tile.tile_id)
    coord_to = tile_id_to_coord(to_tile.tile_id)
    direction = tile_offset_to_direction(coord_to - coord_from)
    # logging.debug('Tile direction: {}->{} is {}'.format(
    #     from_tile.tile_id,
    #     to_tile.tile_id,
    #     direction
    # ))
    return direction

def tile_offset_to_direction(offset):
    try:
        return _tile_offset_to_direction[offset]
    except KeyError:
        logging.critical('Attempted getting direction of non-existent tile offset={:x}'.format(offset))
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

def legal_tile_ids():
    return set(_tile_id_to_coord.keys())

def legal_tile_coords():
    return set(_tile_id_to_coord.values())

_tile_offset_to_direction = {
    -0x20: 'NW',
    -0x22: 'W',
    -0x02: 'SW',
    +0x20: 'SE',
    +0x22: 'E',
    +0x02: 'NE'
}

_tile_id_to_coord = {
    # 1-19 clockwise starting from Top-Left. See JSettlers2 dissertation.
    1: 0x37, 12: 0x59, 11: 0x7B,
    2: 0x35, 13: 0x57, 18: 0x79 , 10: 0x9B,
    3: 0x33, 14: 0x55, 19: 0x77, 17: 0x99, 9: 0xBB,
    4: 0x53, 15: 0x75, 16: 0x97, 8: 0xB9,
    5: 0x73, 6: 0x95, 7: 0xB7
}


