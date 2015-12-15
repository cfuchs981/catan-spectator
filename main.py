"""Record a game of Settlers of Catan.

TODO: Allow ports to be selected during pregame
TODO: Left align checkbox text
TODO: Control size adjustment with resizing of window
TODO: Simplify the algorithm for red placement now there is a connected path through
      the graph that visits every node.
TODO: Docstrings and unittests.
"""

import tkinter
import unittest
import collections

import views
import models
import gamestates
import recording


class CatanGameRecorder(tkinter.Frame):

    def __init__(self, options=None, *args, **kwargs):
        super(CatanGameRecorder, self).__init__()
        self.options = options or {
            'hex_resource_selection': True,
            'hex_number_selection': False
        }
        self.players = list()
        self.board = models.Board(self.options)

        self.record = recording.GameRecord(auto_flush=True, use_stdout=True)

        board_frame = views.BoardFrame(self, self.options, self.board)
        toolbar_frame = views.PregameToolbarFrame(self, self.options)

        board_frame.pack(side=tkinter.LEFT, fill=tkinter.Y)
        toolbar_frame.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        board_frame.draw(models.Board(options))

        self._board_frame = board_frame
        self._toolbar_frame = toolbar_frame

        self.lift()

    def start_game(self, players):
        self.board.state = gamestates.GameStateInGame(self.board)
        self.players = players

        terrain = [tile.terrain for tile in self.board.tiles]
        numbers = [tile.number for tile in self.board.tiles]
        ports = [port for _, _, port in self.board.ports]

        self.record.record_pregame(players, terrain, numbers, ports)

        self._toolbar_frame.pack_forget()
        self._toolbar_frame = views.GameToolbarFrame(self, self.players, self.record)
        self._toolbar_frame.pack(side=tkinter.RIGHT, fill=tkinter.Y)

    def end_game(self):
        self.board.state = gamestates.GameStatePreGame(self.board)

        # self.record.record_player_wins(winner)

        self._toolbar_frame.pack_forget()
        self._toolbar_frame = views.PregameToolbarFrame(self)
        self._toolbar_frame.pack(side=tkinter.RIGHT, fill=tkinter.Y)


def main():
    app = CatanGameRecorder()
    app.mainloop()


if __name__ == "__main__":
    main()
