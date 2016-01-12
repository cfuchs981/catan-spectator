"""
module undo provides class definitions useful for undo/redo functionality in catan.
"""
import logging


class UndoManager(object):
    """
    class UndoManager manages a stack of Command objects for the purpose of
    implementing undo/redo functionality.

    Usage:
        undo_manager = UndoManager()
        undo_manager.do(CmdXYZ(params...))
        undo_manager.undo()
    """
    def __init__(self):
        self._undo_stack = list()
        self._redo_stack = list()

    def do(self, command):
        self._redo_stack.clear()
        self._undo_stack.append(command)
        command.do()
        logging.debug('{}.do() called, stack now={}'.format(type(command), self._undo_stack))

    def can_undo(self):
        return len(self._undo_stack) > 0

    def can_redo(self):
        return len(self._redo_stack) > 0

    def undo(self):
        if len(self._undo_stack) < 1:
            raise Exception('Cannot perform undo, undo stack is empty')
        command = self._undo_stack.pop()
        self._redo_stack.append(command)
        command.undo()
        logging.debug('{}.undo() called, undo stack now={}'.format(type(command), self._undo_stack))

    def redo(self):
        if len(self._redo_stack) < 1:
            raise Exception('Cannot perform redo, redo stack is empty')
        command = self._redo_stack.pop()
        self._undo_stack.append(command)
        command.do()
        logging.debug('{}.redo() called, redo stack now={}'.format(type(command), self._redo_stack))



class Command(object):
    """
    class Command describes an interface which all commands must implement.

    Commands must be doable and undoable. The actual method of do/undo is left
    up to the implementing class.
    """
    def __init__(self, game, do_method, *args):
        self.game = game
        self.do_method = do_method
        self.args = list(args)

        self.restore_point = None

    def do(self):
        self.restore_point = self.game.copy()
        self.do_method(self.game, *self.args)

    def undo(self):
        self.game.restore(self.restore_point)


def undoable(method):
    """
    decorator undoable allows a Game method to be undone.

    It does this by wrapping the method call as a Command, then game.do()ing
    the command.
    """
    def undoable_method(self, *args):
        self.do(Command(self, method, *args))
    return undoable_method


