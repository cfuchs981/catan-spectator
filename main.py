"""Create a random starting board for Settlers of Catan.

TODO: Center the board using a bounding box
TODO: Draw the sea tiles, and allow them to be randomized
TODO: Left align checkbox text
TODO: Control size adjustment with resizing of window
TODO: Simplify the algorithm for red placement now there is a connected path through
      the graph that visits every node.
TODO: Docstrings and unittests.
TODO: Images and patterns
"""

import tkinter
import unittest

import views
import models


def main():
    mainWindow = tkinter.Tk()
    mainWindow.lift()
    options = {
        'hex_resource_selection': True,
        'hex_number_selection': False
    }
    boardFrame = views.BoardFrame(mainWindow, options)
    boardFrame.pack()
    boardFrame.draw(models.Board(options))
    mainWindow.mainloop()


def test():
    unittest.main(exit=False)


if __name__ == "__main__":
    main()
