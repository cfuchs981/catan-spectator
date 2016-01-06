"""
module commands provides implementations of the Command interface specified in module undo
which are useful for catan. They are used alongside classes defined in module models.
"""
import states
from undo import Command


class CmdRoll(Command):
    def __init__(self, game, roll):
        self.game = game
        self.roll = roll

        self.prev_last_roll = None
        self.prev_last_player_to_roll = None
        self.prev_state = None

    def do(self):
        # save state
        self.prev_last_roll = self.game.last_roll
        self.prev_last_player_to_roll = self.game.last_player_to_roll
        self.prev_state = self.game.state

        # perform action
        self.game.catanlog.log_player_roll(self.game.get_cur_player(), self.roll)
        self.game.last_roll = self.roll
        self.game.last_player_to_roll = self.game.get_cur_player()
        if int(self.roll) == 7:
            self.game.set_state(states.GameStateMoveRobber(self.game))
        else:
            self.game.set_state(states.GameStateDuringTurnAfterRoll(self.game))

    def undo(self):
        # undo catanlog
        self.game.last_roll = self.prev_last_roll
        self.game.last_player_to_roll = self.prev_last_player_to_roll
        self.game.set_state(self.prev_state)
