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

from ui import BoardUI
from board import Board


def main():
    root = tkinter.Tk()
    root.lift()
    options = {
        'hex_resource_selection': True,
        'hex_number_selection': False
    }
    boardUI = BoardUI(root, options)
    boardUI.pack()
    boardUI.draw(Board(options))
    root.mainloop()


def test():
    unittest.main(exit=False)

if __name__ == "__main__":
    main()
