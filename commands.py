"""
module commands provides implementations of the Command interface specified in module undo
which are useful for catan. They are used alongside classes defined in module models.
"""
import logging
import models
import states
from undo import Command


class GameCmd(Command):
    def __init__(self, game, *args, **kwargs):
        self.game = game
        self.restore_point = None

    def do(self):
        self.restore_point = self.game.copy()

    def undo(self):
        self.game.restore(self.restore_point)


class CmdRoll(GameCmd):
    def __init__(self, game, roll):
        super(CmdRoll, self).__init__(game)
        self.roll = roll

    def do(self):
        super(CmdRoll, self).do()
        self.game.catanlog.log_player_roll(self.game.get_cur_player(), self.roll)
        self.game.last_roll = self.roll
        self.game.last_player_to_roll = self.game.get_cur_player()
        if int(self.roll) == 7:
            self.game.set_state(states.GameStateMoveRobber(self.game))
        else:
            self.game.set_state(states.GameStateDuringTurnAfterRoll(self.game))


class CmdMoveRobber(GameCmd):
    def __init__(self, game, tile):
        super(CmdMoveRobber, self).__init__(game)
        self.tile = tile

    def do(self):
        super(CmdMoveRobber, self).do()
        self.game.state.move_robber(self.tile)


class CmdSteal(GameCmd):
    def __init__(self, game, victim):
        super(CmdSteal, self).__init__(game)
        self.victim = victim

    def do(self):
        super(CmdSteal, self).do()
        if self.victim is None:
            self.victim = models.Player(1, 'nobody', 'nobody')
        self.game.state.steal(self.victim)


class CmdBuyRoad(GameCmd):
    def __init__(self, game, edge):
        super(CmdBuyRoad, self).__init__(game)
        self.edge = edge

    def do(self):
        super(CmdBuyRoad, self).do()
        piece = models.Piece(models.PieceType.road, self.game.get_cur_player())
        self.game.board.place_piece(piece, self.edge)
        self.game.catanlog.log_player_buys_road(self.game.get_cur_player(), self.edge)
        if self.game.state.is_in_pregame():
            self.game.end_turn()
        else:
            self.game.set_state(states.GameStateDuringTurnAfterRoll(self.game))


class CmdBuySettlement(GameCmd):
    def __init__(self, game, node):
        super(CmdBuySettlement, self).__init__(game)
        self.node = node

    def do(self):
        super(CmdBuySettlement, self).do()
        piece = models.Piece(models.PieceType.settlement, self.game.get_cur_player())
        self.game.board.place_piece(piece, self.node)
        self.game.catanlog.log_player_buys_settlement(self.game.get_cur_player(), self.node)
        if self.game.state.is_in_pregame():
            self.game.set_state(states.GameStatePreGamePlaceRoad(self.game))
        else:
            self.game.set_state(states.GameStateDuringTurnAfterRoll(self.game))



