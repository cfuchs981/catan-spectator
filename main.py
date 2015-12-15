"""Record a game of Settlers of Catan.

TODO: Allow ports to be selected during pregame
TODO: Control size adjustment with resizing of window
TODO: Simplify the algorithm for red placement now there is a connected path through
      the graph that visits every node.
TODO: Docstrings and unittests.
"""

import tkinter
import collections

import views
import models
import states
import recording


class CatanGameRecorder(tkinter.Frame):

    def __init__(self, options=None, *args, **kwargs):
        super(CatanGameRecorder, self).__init__()
        self.options = options or {
            'hex_resource_selection': True,
            'hex_number_selection': False
        }
        self.game = models.Game(list(), models.Board(), recording.GameRecord())
        self.game.observers.add(self)
        self._ingame_before = self.game.state.is_in_game()

        board_frame = views.BoardFrame(self, self.game, options=self.options)
        toolbar_frame = views.PregameToolbarFrame(self, self.game, options=self.options)

        board_frame.pack(side=tkinter.LEFT, fill=tkinter.Y)
        toolbar_frame.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        board_frame.redraw()

        self._board_frame = board_frame
        self._toolbar_frame = toolbar_frame

        self.lift()

    def notify(self, observable):
        if self._ingame_before and not self.game.state.is_in_game():
            self._toolbar_frame.destroy()
            self._toolbar_frame = views.PregameToolbarFrame(self, self.game)
            self._toolbar_frame.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        elif not self._ingame_before and self.game.state.is_in_game():
            self._toolbar_frame.destroy()
            self._toolbar_frame = views.GameToolbarFrame(self, self.game)
            self._toolbar_frame.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self._ingame_before = self.game.state.is_in_game()


def main():
    app = CatanGameRecorder()
    app.mainloop()


if __name__ == "__main__":
    main()
