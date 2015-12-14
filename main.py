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

import views
import models
import gamestates


class CatanGameRecorder(tkinter.Frame):

    def __init__(self, options, *args, **kwargs):
        super(CatanGameRecorder, self).__init__()
        self.options = options
        self.players = set()
        self.board = models.Board(self.options)

        board_frame = views.BoardFrame(self, self.options, self.board)
        toolbar_frame = views.PregameToolbarFrame(self, self.options)

        board_frame.pack(side=tkinter.LEFT, fill=tkinter.Y)
        toolbar_frame.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        board_frame.draw(models.Board(options))

        self._board_frame = board_frame
        self._toolbar_frame = toolbar_frame

        self.lift()

    def start_game(self):
        self.board.state = gamestates.GameStateInGame(self.board)

        self._toolbar_frame.pack_forget()
        self._toolbar_frame = views.GameToolbarFrame(self, {
            'blue': True,
            'red': False,
            'green': False,
            'white': False
        })
        self._toolbar_frame.pack(side=tkinter.RIGHT, fill=tkinter.Y)

    def end_game(self):
        self.board.state = gamestates.GameStatePreGame(self.board)

        self._toolbar_frame.pack_forget()
        self._toolbar_frame = views.PregameToolbarFrame(self, {
            'hex_resource_selection': True,
            'hex_number_selection': False
        })
        self._toolbar_frame.pack(side=tkinter.RIGHT, fill=tkinter.Y)


def main():
    app = CatanGameRecorder(options={
        'hex_resource_selection': True,
        'hex_number_selection': False
    })
    app.mainloop()


def test():
    unittest.main(exit=False)


if __name__ == "__main__":
    main()
