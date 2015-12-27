import models
import logging


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
        logging.debug('Method {0} not found'.format(name))
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
    def next_player(self):
        """Compare to GameStatePreGame's implementation, which uses snake draft"""
        logging.warning('turn={}, players={}'.format(
            self.game._cur_turn,
            self.game.players
        ))
        return self.game.players[(self.game._cur_turn + 1) % len(self.game.players)]

    def begin_turn(self):
        """Compare to GameStatePreGame's implementation, which uses GameStatePreGamePlaceSettlement"""
        self.game.set_state(GameStateBeginTurn(self.game))

    def is_in_game(self):
        return True

    def is_in_pregame(self):
        return False

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

    def can_roll(self):
        return not self.has_rolled()

    def can_move_robber(self):
        return False

    def can_steal(self):
        return False

    def can_buy_road(self):
        return self.has_rolled()

    def can_buy_settlement(self):
        return self.has_rolled()

    def can_buy_city(self):
        return self.has_rolled()

    def can_place_road(self):
        return False

    def can_place_settlement(self):
        return False

    def can_place_city(self):
        return False

    def can_buy_dev_card(self):
        return self.has_rolled()

    def can_trade(self):
        return self.has_rolled()

    def can_play_knight(self):
        return self.game.dev_card_state.can_play_dev_card()

    def can_play_monopoly(self):
        return self.has_rolled() and self.game.dev_card_state.can_play_dev_card()

    def can_play_road_builder(self):
        return self.has_rolled() and self.game.dev_card_state.can_play_dev_card()

    def can_play_victory_point(self):
        return True


class GameStatePreGame(GameStateInGame):
    """
    The pregame is defined as
    - AFTER the board has been laid out
    - BEFORE the first dice roll

    In other words, it is the placing of the initial settlements and roads, in snake draft order.
    """
    def is_in_pregame(self):
        return True

    def next_player(self):
        snake = self.game.players.copy()
        snake += list(reversed(snake))
        try:
            return snake[self.game._cur_turn + 1]
        except IndexError:
            self.game.set_state(GameStateBeginTurn(self.game))
            return self.game.state.next_player()

    def begin_turn(self):
        self.game.set_state(GameStatePreGamePlaceSettlement(self.game))

    def can_play_knight(self):
        """No dev cards in the pregame"""
        return False

    def can_play_monopoly(self):
        """No dev cards in the pregame"""
        return False

    def can_play_road_builder(self):
        """No dev cards in the pregame"""
        return False

    def can_play_victory_point(self):
        """No dev cards in the pregame"""
        return False

    def can_roll(self):
        """No rolling in the pregame"""
        return False

    def can_buy_road(self):
        raise NotImplemented()

    def can_buy_settlement(self):
        raise NotImplemented()

    def can_buy_city(self):
        """No cities in the pregame"""
        return False

    def can_buy_dev_card(self):
        """No dev cards in the pregame"""
        return False

    def can_end_turn(self):
        raise NotImplemented()

    def can_trade(self):
        """No trading in the pregame"""
        return False


class GameStatePreGamePlaceSettlement(GameStatePreGame):
    """
    - AFTER a player's turn has started
    - BEFORE the player has placed an initial settlement
    """
    def can_buy_settlement(self):
        return True

    def can_buy_road(self):
        return False

    def can_end_turn(self):
        return False


class GameStatePreGamePlaceRoad(GameStatePreGame):
    """
    - AFTER a player has placed an initial settlement
    - BEFORE the player has placed an initial road
    """
    def can_buy_settlement(self):
        return False

    def can_buy_road(self):
        return True

    def can_end_turn(self):
        return False


class GameStatePreGamePlacingPiece(GameStatePreGame):
    """
    - AFTER a player has selected to place a piece
    - WHILE the player is choosing where to place it
    - BEFORE the player has placed it
    """
    def __init__(self, game, piece_type):
        super(GameStatePreGamePlacingPiece, self).__init__(game)
        self.piece_type = piece_type

    def can_buy_settlement(self):
        return False

    def can_buy_road(self):
        return False

    def can_end_turn(self):
        return False

    def can_place_road(self):
        return self.piece_type == models.PieceType.road

    def can_place_settlement(self):
        return self.piece_type == models.PieceType.settlement

    def can_place_city(self):
        return self.piece_type == models.PieceType.city

    def place_road(self, node_from, node_to):
        if not self.can_place_road():
            logging.warning('Attempted to place road in illegal state={} with piece_type={}'.format(
                self.__class__.__name__,
                self.piece_type
            ))
        self.game.buy_road(node_from, node_to)

    def place_settlement(self, node):
        if not self.can_place_settlement():
            logging.warning('Attempted to place settlement in illegal state={} with piece_type={}'.format(
                self.__class__.__name__,
                self.piece_type
            ))
        self.game.buy_settlement(node)

    def place_city(self, node):
        if not self.can_place_city():
            logging.warning('Attempted to place city in illegal state={} with piece_type={}'.format(
                self.__class__.__name__,
                self.piece_type
            ))
        self.game.buy_city(node)

class GameStateBeginTurn(GameStateInGame):
    """
    The start of the turn is defined as
    - AFTER the previous player ends their turn
    - BEFORE the next player's first action
    """
    def can_end_turn(self):
        return False


class GameStateMoveRobber(GameStateInGame):
    """
    Defined as
    - AFTER the rolling of a 7
    - BEFORE the player has moved the robber
    """
    def can_end_turn(self):
        return False

    def can_move_robber(self):
        return True

    def move_robber(self, tile):
        self.game.robber_tile = tile
        self.game.set_state(GameStateSteal(self.game))

    def can_roll(self):
        return False

    def can_buy_road(self):
        return False

    def can_buy_settlement(self):
        return False

    def can_buy_city(self):
        return False

    def can_buy_dev_card(self):
        return False

    def can_trade(self):
        return False

    def can_play_knight(self):
        return False

    def can_play_monopoly(self):
        return False

    def can_play_road_builder(self):
        return False


class GameStateMoveRobberUsingKnight(GameStateMoveRobber):
    """
    Defined as
    - AFTER the playing of a knight
    - BEFORE the player has moved the robber
    """
    def move_robber(self, tile):
        self.game.robber_tile = tile
        self.game.set_state(GameStateStealUsingKnight(self.game))


class GameStateSteal(GameStateInGame):
    """
    Defined as
    - AFTER the player has moved the robber
    - BEFORE the player has stolen a card
    """
    def can_end_turn(self):
        return False

    def can_steal(self):
        return True

    def steal(self, victim):
        self.game.log.log_player_moves_robber_and_steals(
            self.game.get_cur_player(),
            self.game.robber_tile,
            victim
        )
        self.game.set_state(GameStateDuringTurnAfterRoll(self.game))

    def can_roll(self):
        return False

    def can_buy_road(self):
        return False

    def can_buy_settlement(self):
        return False

    def can_buy_city(self):
        return False

    def can_buy_dev_card(self):
        return False

    def can_trade(self):
        return False

    def can_play_knight(self):
        return False

    def can_play_monopoly(self):
        return False

    def can_play_road_builder(self):
        return False


class GameStateStealUsingKnight(GameStateSteal):
    """
    Defined as
    - AFTER the player has moved the robber using the knight
    - BEFORE the player has stolen a card using the knight
    """
    def steal(self, victim):
        self.game.log.log_player_plays_dev_knight(
            self.game.get_cur_player(),
            self.game.robber_tile,
            victim
        )
        self.game.set_state(GameStateDuringTurnAfterRoll(self.game))


class GameStateDuringTurnAfterRoll(GameStateInGame):
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
