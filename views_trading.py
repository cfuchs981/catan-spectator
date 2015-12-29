import functools
import logging
import tkinter as tk
import math
from models import Port
from trading import CatanTrade

can_do = {
    True: tk.NORMAL,
    False: tk.DISABLED,
    None: tk.DISABLED
}


class TradeFrame(tk.Frame):

    def __init__(self, master, game):
        super(TradeFrame, self).__init__(master)
        self.master = master
        self.game = game
        self.game.observers.add(self)

        self.trade = CatanTrade(giver=self.game.get_cur_player())

        self.title = tk.Label(self, text="Trade")
        self.frame = WithWhoFrame(self)
        self.make_trade = tk.Button(self, text='Make Trade', state=tk.DISABLED, command=self.on_make_trade)
        self.cancel = tk.Button(self, text='Cancel', state=tk.DISABLED, command=self.on_cancel)

        self.title.grid(sticky=tk.W)
        self.frame.grid()
        self.make_trade.grid(row=2, column=0, sticky=tk.EW)
        self.cancel.grid(row=2, column=1, sticky=tk.EW)

        self.set_states()

    def notify(self, observable):
        self.set_states()

    def set_states(self):
        self.make_trade.configure(state=can_do[self.can_make_trade()])
        self.cancel.configure(state=can_do[self.can_cancel()])

    def set_frame(self, frame):
        self.frame.grid_remove()
        self.frame = frame
        self.frame.grid(row=1)
        self.notify(None)

    def can_make_trade(self):
        return self.frame.can_make_trade()

    def can_cancel(self):
        return self.frame.can_cancel()

    def on_make_trade(self):
        logging.warning('make trade not implemented yet in views_trading')

    def on_cancel(self):
        self.set_frame(WithWhoFrame(self))


class WithWhoFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super(WithWhoFrame, self).__init__(*args, **kwargs)
        self.master.game.observers.add(self)

        self.player = tk.Button(self, text='Player', command=self.on_player)
        self.port = tk.Button(self, text='Port', command=self.on_port)

        self.player.pack(side=tk.LEFT)
        self.port.pack(side=tk.RIGHT)

        self.set_states()

    def notify(self, observable):
        self.set_states()

    def set_states(self):
        self.player.configure(state=can_do[self.master.game.state.can_trade()])
        self.port.configure(state=can_do[self.master.game.state.can_trade()])

    def on_player(self):
        self.master.set_frame(WithWhichPlayerFrame(self.master))

    def on_port(self):
        self.master.set_frame(WithWhichPortFrame(self.master))

    def can_make_trade(self):
        return False

    def can_cancel(self):
        return False


class WithWhichPlayerFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super(WithWhichPlayerFrame, self).__init__(*args, **kwargs)
        self.master.game.observers.add(self)

        self.player_btns = list()
        count = 0
        for p in self.master.game.players.copy():
            b = tk.Button(self, text='{}'.format(p), state=tk.DISABLED, command=functools.partial(self.on_player, p))
            b.grid(row=count // 2, column=count % 2, sticky=tk.NSEW)
            self.player_btns.append(b)
            count += 1

        self.set_states()

    def notify(self, observable):
        self.set_states()

    def set_states(self):
        for player_btn, player in zip(self.player_btns, self.master.game.players.copy()):
            state = (self.master.game.state.can_trade()
                     and self.master.game.get_cur_player() != player)
            player_btn.configure(state=can_do[state])

    def can_make_trade(self):
        return False

    def can_cancel(self):
        return True

    def on_player(self, player):
        logging.debug('trade: player={} selected'.format(player))
        self.master.trade.set_getter(player)
        self.master.set_frame(WhichResourcesFrame(self.master))


class WithWhichPortFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super(WithWhichPortFrame, self).__init__(*args, **kwargs)
        self.master.game.observers.add(self)

        # grid of buttons
        # x x x
        # x x x
        # 3:1 in topleft, other have text=terrain.value

        tk.Label(self, text='which port').pack()

        self.set_states()

    def notify(self, observable):
        self.set_states()

    def set_states(self):
        pass

    def on_three_for_one(self):
        to_port = [(3, self.port_give.get())]
        to_player = [(1, self.port_get.get())]
        self.game.trade_with_port(to_port, Port.any.value, to_player)

    def on_two_for_one(self):
        to_port = [(2, self.port_give.get())]
        to_player = [(1, self.port_get.get())]
        port = Port('{}2:1'.format(self.port_give.get()))
        self.game.trade_with_port(to_port, port.value, to_player)

    def can_make_trade(self):
        return False

    def can_cancel(self):
        return True


class WhichResourcesFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super(WhichResourcesFrame, self).__init__(*args, **kwargs)
        self.master.game.observers.add(self)

        tk.Label(self, text='which resources').pack()

        self.set_states()

    def notify(self, observable):
        self.set_states()

    def set_states(self):
        pass

    def can_make_trade(self):
        return True

    def can_cancel(self):
        return True

# ##
# # Players
# #
# self.player_frame = tk.Frame(self)
#

#
# ##
# # Ports
# #
# self.port_frame = tk.Frame(self)
# resources = list(t.value for t in Terrain if t != Terrain.desert)
# tk.Label(self.port_frame, text="Trade: Ports").grid(row=0, column=0, sticky=tk.W)
# self.port_give = tk.StringVar(value=resources[0])
# self.port_get = tk.StringVar(value=resources[1])
# tk.OptionMenu(self.port_frame, self.port_give, *resources).grid(row=1, column=0, sticky=tk.NSEW)
# tk.OptionMenu(self.port_frame, self.port_get, *resources).grid(row=1, column=1, sticky=tk.NSEW)
# self.btn_31 = tk.Button(self.port_frame, text='3:1', command=self.on_three_for_one)
# self.btn_31.grid(row=1, column=2, sticky=tk.NSEW)
# self.btn_21 = tk.Button(self.port_frame, text='2:1', command=self.on_two_for_one)
# self.btn_21.grid(row=1, column=3, sticky=tk.NSEW)
#
# ##
# # Place elements in frame
# #
# self.label_player.grid(row=0, sticky=tk.W)
# for i, button in enumerate(self.player_buttons):
#     button.grid(row=1 + i // 2, column=i % 2, sticky=tk.EW)
#
# self.player_frame.pack(anchor=tk.W)
# self.port_frame.pack(anchor=tk.W)


