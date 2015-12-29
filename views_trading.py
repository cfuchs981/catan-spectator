import logging
import tkinter as tk


class TradeFrame(tk.Frame):

    def __init__(self, master, game):
        super(TradeFrame, self).__init__(master)
        self.master = master
        self.game = game
        self.game.observers.add(self)

        ###
        #
        #
        self.title = tk.Label(self.player_frame, text="Trade")
        self.frame = tk.Frame(self)
        self.make_trade = tk.Button(self, text='Make Trade', command=self.on_make_trade)

        self.title.grid()
        self.frame.grid()
        self.make_trade.grid()

        self.set_states()

    def notify(self, observable):
        self.set_states()

    def set_states(self):
        """You can't trade with yourself, and you have to roll before trading"""
        for player, button in zip(self.game.players, self.player_buttons):
            button.configure(state=can_do[self.game.state.can_trade() and player != self.game.get_cur_player()])
        self.btn_31.configure(state=can_do[self.game.state.can_trade()])
        self.btn_21.configure(state=can_do[self.game.state.can_trade()])

    def set_frame(self, frame):
        self.frame.grid_remove()
        self.frame = frame
        self.frame.grid(row=1)

    def on_make_trade(self):
        logging.warning('on make trade not yet implemented in views_trading')


class WithWho(tk.Frame):
    def __init__(self, *args, **kwargs):
        super(WithWhichPort, self).__init__(*args, **kwargs)

        tk.Button(self, text='Player', command=self._on_player).pack(side=tk.LEFT)
        tk.Button(self, text='Port', command=self._on_port).pack(side=tk.right)

    def _on_player(self):
        pass

    def _on_port(self):
        pass


class WithWhichPlayer(tk.Frame):
    def __init__(self, *args, **kwargs):
        super(WithWhichPort, self).__init__(*args, **kwargs)

        tk.Label(self, text='which player').pack()


class WithWhichPort(tk.Frame):
    def __init__(self, *args, **kwargs):
        super(WithWhichPort, self).__init__(*args, **kwargs)

        # grid of buttons
        # x x x
        # x x x
        # 3:1 in topleft, other have text=terrain.value

        tk.Label(self, text='which port').pack()

    def on_three_for_one(self):
        to_port = [(3, self.port_give.get())]
        to_player = [(1, self.port_get.get())]
        self.game.trade_with_port(to_port, Port.any.value, to_player)

    def on_two_for_one(self):
        to_port = [(2, self.port_give.get())]
        to_player = [(1, self.port_get.get())]
        port = Port('{}2:1'.format(self.port_give.get()))
        self.game.trade_with_port(to_port, port.value, to_player)


class WhichResources(tk.Frame):
    def __init__(self, *args, **kwargs):
        super(WithWhichPort, self).__init__(*args, **kwargs)

        tk.Label(self, text='which resources').pack()

# ##
# # Players
# #
# self.player_frame = tk.Frame(self)
#
# self.player_buttons = list()
# for p in self.game.players:
#     button = tk.Button(self.player_frame, text='{0} ({1})'.format(p.color, p.name), state=tk.DISABLED)
#     self.player_buttons.append(button)
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


