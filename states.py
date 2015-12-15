import models


class GameState(object):
    def __init__(self, game):
        self.game = game

    def is_in_game(self):
        return False


class GameStatePreGame(GameState):
    """
    All PRE-GAME states inherit from this state.

    Child states should follow the rules defined by GameStateInGame.
    """
    def is_in_game(self):
        return False


class GameStatePostGame(GameState):
    """
    All POST-GAME states inherit from this state.

    Child states should follow the rules defined by GameStateInGame.
    """
    def is_in_game(self):
        return False


class GameStateInGame(GameState):
    """
    All IN-GAME states inherit from this state.

    Child in-game states MUST NOT define methods other than those defined here.

    Methods defined in this base class return default values.
    If a state requires a non-default value, override the method and implement it yourself.

    Again, this base class must define a default implementation for ALL methods which any subclass defines.
    """
    def is_in_game(self):
        return True

    def end_turn_allowed(self):
        if self.can_move_robber() or self.can_steal():
            return False

        return True

    def can_move_robber(self):
        return False

    def can_steal(self):
        return False


class GameStateTurnStart(GameStateInGame):
    def end_turn_allowed(self):
        return False


class GameStateRolled(GameStateInGame):
    def can_move_robber(self):
        return int(self.game.last_roll) == 7


class GameStateMovedRobber(GameStateInGame):
    def can_steal(self):
        return True


class GameStateMovedRobberAndStole(GameStateInGame):
    def end_turn_allowed(self):
        return True


##
# Abstract state class to inherit concrete states from
#
class BoardState(object):
    def __init__(self, board):
        self.board = board

    def hex_change_allowed(self):
        return self.hex_number_change_allowed() and self.hex_type_change_allowed()

    def cycle_hex_type(self, tile_id):
        if self.hex_type_change_allowed():
            tile = self.board.tiles[tile_id - 1]
            next_idx = (list(models.Terrain).index(tile.terrain) + 1) % len(models.Terrain)
            next_terrain = list(models.Terrain)[next_idx]
            tile.terrain = next_terrain

    def cycle_hex_number(self, tile_id):
        if self.hex_number_change_allowed():
            tile = self.board.tiles[tile_id - 1]
            next_idx = (list(models.HexNumber).index(tile.number) + 1) % len(models.HexNumber)
            next_hex_number = list(models.HexNumber)[next_idx]
            tile.number = next_hex_number

    ##
    # Begin methods to implement in concrete states
    #
    def hex_number_change_allowed(self):
        raise NotImplemented()

    def hex_type_change_allowed(self):
        raise NotImplemented()


class BoardStateModifiable(BoardState):
    def hex_number_change_allowed(self):
        return True

    def hex_type_change_allowed(self):
        return True


class BoardStateLocked(BoardState):
    def hex_number_change_allowed(self):
        return False

    def hex_type_change_allowed(self):
        return False
