import models


class GameState(object):
    def __init__(self, game):
        self.game = game

    def __getattr__(self, name):
        """Return false for methods called on GameStates which don't have those methods.
        This should be ok, since __getattr__ is only called as a last resort
        i.e. if there are no attributes in the instance that match the name

        source: http://stackoverflow.com/a/2405617/1817465
        """
        def method(*args):
            return None
        return method

    def is_in_game(self):
        return False


class GameStateNotInGame(GameState):
    """
    All NOT-IN-GAME states inherit from this state.
    """
    def is_in_game(self):
        return False


class GameStateInGame(GameState):
    """
    All IN-GAME states inherit from this state.

    Look at the comments separating the methods below for directions on
    what to override, implement, etc in subclasses.
    """
    def __init__(self, *args, **kwargs):
        super(GameStateInGame, self).__init__(*args, **kwargs)
        self.dev_card_state = DevCardNotPlayedState(self)
        self.is_moving_robber = False
        self.is_stealing = False

    def next_player(self):
        """Compare to GameStatePreGame's implementation, which uses snake draft"""
        return self.game._next_player(snake=False)

    def begin_turn(self):
        """Compare to GameStatePreGame's implementation, which uses GameStatePreGamePlaceSettlement"""
        self.game.set_state(GameStateBeginTurn(self.game))

    def is_in_game(self):
        return True

    def can_play_knight_dev_card(self):
        return self.dev_card_state.can_play_dev_card()

    def can_play_non_knight_dev_card(self):
        return self.has_rolled() and self.dev_card_state.can_play_dev_card()

    def has_rolled(self):
        return self.game.last_player_to_roll == self.game.get_cur_player()

    ##
    # Child states MUST implement methods below
    #

    def can_end_turn(self):
        raise NotImplemented()

    ##
    # Child states CAN implement methods below if they want.
    # Otherwise, these defaults will be used.
    #

    def can_move_robber(self):
        return False

    def can_steal(self):
        return False


class GameStatePreGame(GameStateInGame):
    """
    The pregame is defined as
    - AFTER the board has been laid out
    - BEFORE the first dice roll

    In other words, it is the placing of the initial settlements and roads, in snake draft order.
    """
    def next_player(self):
        return self.game._next_player(snake=True)

    def begin_turn(self):
        self.game.set_state(GameStatePreGamePlaceSettlement(self.game))

    def can_play_knight_dev_card(self):
        """No dev cards in the pregame"""
        return False

    def can_play_non_knight_dev_card(self):
        """No dev cards in the pregame"""
        return False

    def has_rolled(self):
        """No rolling in the pregame"""
        return True

    def can_end_turn(self):
        raise NotImplemented()


class GameStatePreGamePlaceSettlement(GameStatePreGame):
    """
    - AFTER a player's turn has started
    - BEFORE the player has placed an initial settlement
    """
    def can_end_turn(self):
        return False


class GameStatePreGamePlaceRoad(GameStatePreGame):
    """
    - AFTER a player has placed an initial settlement
    - BEFORE the player has placed an initial road
    """
    def can_end_turn(self):
        return False


class GameStatePreGameHasPlacedRoad(GameStatePreGame):
    def can_end_turn(self):
        return True


class GameStateBeginTurn(GameStateInGame):
    """
    The start of the turn is defined as
    - AFTER the previous player ends their turn
    - BEFORE the next player's first action
    """
    def can_end_turn(self):
        return False


class GameStateCanMoveRobber(GameStateInGame):
    """
    Defined as
    - AFTER the rolling of a 7, or the playing of a knight
    - BEFORE the player has begun moving the robber
    """
    def can_move_robber(self):
        return True


class GameStateMovingRobber(GameStateInGame):
    """
    Defined as
    - AFTER the player has begun moving the robber
    - BEFORE the robber has been placed on a tile
    """
    def __init__(self, *args, **kwargs):
        super(GameStateMovingRobber, self).__init__(*args, **kwargs)
        self.is_moving_robber = True

    def move_robber(self):
        self.game.set_state(GameStateStealing(self.game))


class GameStateMovedRobber(GameStateInGame):
    """
    Defined as
    - AFTER the robber has been placed on a tile
    - BEFORE the player has begun to steal
    """
    def can_steal(self):
        return True


class GameStateStealing(GameStateInGame):
    """
    Defined as
    - AFTER the player has begun to steal
    - BEFORE the player has stolen a card
    """
    def __init__(self, *args, **kwargs):
        super(GameStateStealing, self).__init__(*args, **kwargs)
        self.is_stealing = True

    def steal(self):
        self.game.set_state(GameStateNormalTurn(self.game))


class GameStateNormalTurn(GameStateInGame):
    """
    The most common state.

    Defined as
    - AFTER the player's roll
    - BEFORE the player ends their turn
    """
    def can_end_turn(self):
        return True


class DevCardPlayabilityState(object):
    def __init__(self, game):
        self.game = game

    def can_play_dev_card(self):
        raise NotImplemented()


class DevCardNotPlayedState(DevCardPlayabilityState):
    def can_play_dev_card(self):
        return True


class DevCardPlayedState(DevCardPlayabilityState):
    def can_play_dev_card(self):
        return False


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
