"""
module commands provides implementations of the Command interface specified in module undo
which are useful for catan. They are used alongside classes defined in module models.
"""
import logging
import models
import states
from undo import Command


class CmdRoll(Command):
    def __init__(self, game, roll):
        self.game = game
        self.roll = roll
        self.restore_point = None

    def do(self):
        self.restore_point = self.game.copy()
        self.game.catanlog.log_player_roll(self.game.get_cur_player(), self.roll)
        self.game.last_roll = self.roll
        self.game.last_player_to_roll = self.game.get_cur_player()
        if int(self.roll) == 7:
            self.game.set_state(states.GameStateMoveRobber(self.game))
        else:
            self.game.set_state(states.GameStateDuringTurnAfterRoll(self.game))

    def undo(self):
        self.game.restore(self.restore_point)


class CmdMoveRobber(Command):
    def __init__(self, game, tile):
        self.game = game
        self.tile = tile
        self.restore_point = None

    def do(self):
        self.restore_point = self.game.copy()
        self.game.state.move_robber(self.tile)

    def undo(self):
        self.game.restore(self.restore_point)


class CmdSteal(Command):
    def __init__(self, game, victim):
        self.game = game
        self.victim = victim
        self.restore_point = None

    def do(self):
        self.restore_point = self.game.copy()
        if self.victim is None:
            self.victim = models.Player(1, 'nobody', 'nobody')
        self.game.state.steal(self.victim)

    def undo(self):
        self.game.restore(self.restore_point)


class CmdBuyRoad(Command):
    def __init__(self, game, edge):
        self.game = game
        self.edge = edge
        self.restore_point = None

    def do(self):
        self.restore_point = self.game.copy()
        piece = models.Piece(models.PieceType.road, self.game.get_cur_player())
        self.game.board.place_piece(piece, self.edge)
        self.game.catanlog.log_player_buys_road(self.game.get_cur_player(), self.edge)
        if self.game.state.is_in_pregame():
            self.game.end_turn()
        else:
            self.game.set_state(states.GameStateDuringTurnAfterRoll(self.game))

    def undo(self):
        self.game.restore(self.restore_point)
