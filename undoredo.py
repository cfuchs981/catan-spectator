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
        self.command_stack = list()

    def do(self, command):
        self.command_stack.append(command)
        command.do()
        logging.debug('{}.do() called, stack now={}'.format(type(command), self.command_stack))

    def can_undo(self):
        return len(self.command_stack) > 0

    def undo(self):
        if len(self.command_stack) < 1:
            raise Exception('Cannot perform undo, command stack is empty')
        command = self.command_stack.pop()
        command.undo()
        logging.debug('{}.undo() called, stack now={}'.format(type(command), self.command_stack))


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


