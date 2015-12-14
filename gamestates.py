import models


##
# Abstract state class to inherit concrete game states from
#
class GameState(object):
    def __init__(self, board):
        self.board = board

    def hex_change_allowed(self):
        return self.hex_number_change_allowed() and self.hex_type_change_allowed()

    def cycle_hex_type(self, tile_id):
        if self.hex_type_change_allowed():
            old_tile = self.board.tiles[tile_id - 1]
            new_terrain_idx = (self.board._terrain_codes.index(old_tile.terrain) + 1) % len(self.board._terrain_codes)
            new_terrain = self.board._terrain_codes[new_terrain_idx]
            self.board.tiles[tile_id - 1] = models.Tile(id=tile_id, terrain=new_terrain, value=old_tile.value)

    def cycle_hex_number(self, tile_id):
        if self.hex_number_change_allowed():
            old_tile = self.board.tiles[tile_id - 1]
            new_number_idx = (self.board._number_codes.index(old_tile.value) + 1) % len(self.board._number_codes)
            new_number = self.board._number_codes[new_number_idx]
            self.board.tiles[tile_id - 1] = models.Tile(id=tile_id, terrain=old_tile.terrain, value=new_number)

    ##
    # Begin methods to implement in concrete states
    #
    def hex_number_change_allowed(self):
        raise NotImplemented()

    def hex_type_change_allowed(self):
        raise NotImplemented()


class GameStatePreGame(GameState):
    def hex_number_change_allowed(self):
        return True

    def hex_type_change_allowed(self):
        return True


class GameStateInGame(GameState):
    def hex_number_change_allowed(self):
        return False

    def hex_type_change_allowed(self):
        return False
