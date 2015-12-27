import logging
import tkinter
from tkinter import messagebox
import math
import itertools
import collections
import functools
import hexgrid

from models import Terrain, Port, Player, HexNumber, Piece, PieceType
import states
import tkinterutils

can_do = {
    True: tkinter.NORMAL,
    False: tkinter.DISABLED,
    None: tkinter.DISABLED
}


class BoardFrame(tkinter.Frame):

    def __init__(self, master, game, *args, **kwargs):
        super(BoardFrame, self).__init__()
        self.master = master
        self.game = game
        self.game.observers.add(self)

        self._board = game.board

        board_canvas = tkinter.Canvas(self, height=800, width=600, background='Royal Blue')
        board_canvas.pack(expand=tkinter.YES, fill=tkinter.BOTH)

        self._board_canvas = board_canvas
        self._center_to_edge = math.cos(math.radians(30)) * self._tile_radius

        self.game.observers.add(self)

    def tile_click(self, event):
        if not self._board.state.hex_change_allowed():
            return

        tag = self._board_canvas.gettags(event.widget.find_closest(event.x, event.y))[0]
        if self.master.setup_options()['hex_resource_selection']:
            self._board.cycle_hex_type(self._tile_id_from_tag(tag))
        if self.master.setup_options()['hex_number_selection']:
            self._board.cycle_hex_number(self._tile_id_from_tag(tag))
        self.redraw()

    def piece_click(self, piece_type, event):
        tag = self._board_canvas.gettags(event.widget.find_closest(event.x, event.y))[0]
        logging.debug('Piece clicked with tag={}'.format(tag))
        if piece_type == PieceType.road:
            self.game.buy_road(self._coord_from_road_tag(tag))
        elif piece_type == PieceType.settlement:
            self.game.buy_settlement(self._coord_from_settlement_tag(tag))
        elif piece_type == PieceType.city:
            self.game.buy_city(self._coord_from_city_tag(tag))
        self.redraw()

    def notify(self, observable):
        self.redraw()

    def draw(self, board):
        """Render the board to the canvas widget.

        Taking the center of the first tile as 0, 0 we follow the path of tiles
        around the graph as given by the board (must be guaranteed to be a
        connected path that visits every tile) and calculate the center of each
        tile as the offset from the last one, based on it's direction from the
        last tile and the radius of the hexagons (and padding etc.)

        We then shift all the individual tile centers so that the board center
        is at 0, 0.
        """
        terrain_centers = self._draw_terrain(board)
        self._draw_numbers(board, terrain_centers)
        self._draw_ports(board, terrain_centers)
        self._draw_pieces(board, terrain_centers)
        if self.game.state.can_place_road():
            self._draw_piece_shadows(PieceType.road, board, terrain_centers)
        elif self.game.state.can_place_settlement():
            self._draw_piece_shadows(PieceType.settlement, board, terrain_centers)
        elif self.game.state.can_place_city():
            self._draw_piece_shadows(PieceType.city, board, terrain_centers)


    def redraw(self):
        self._board_canvas.delete(tkinter.ALL)
        self.draw(self._board)

    def _draw_terrain(self, board):
        logging.debug('Drawing terrain (resource tiles)')
        centers = {}
        last = None
        for tile in board.tiles:
            if not last:
                centers[tile.tile_id] = (0, 0)
                last = tile
                continue

            # Calculate the center of this tile as an offset from the center of
            # the neighboring tile in the given direction.
            ref_center = centers[last.tile_id]
            direction = hexgrid.direction_to_tile(last, tile)
            theta = self._tile_angle_order.index(direction) * 60
            radius = 2 * self._center_to_edge + self._tile_padding
            dx = radius * math.cos(math.radians(theta))
            dy = radius * math.sin(math.radians(theta))
            centers[tile.tile_id] = (ref_center[0] + dx, ref_center[1] + dy)
            last = tile

        centers = self._fixup_terrain_centers(centers)
        for tile_id, (x, y) in centers.items():
            tile = board.tiles[tile_id - 1]
            self._draw_tile(x, y, tile.terrain, tile)
            self._board_canvas.tag_bind(self._tile_tag(tile), '<ButtonPress-1>', func=self.tile_click)

        return dict(centers)

    def _draw_tile(self, x, y, terrain: Terrain, tile):
        self._draw_hexagon(self._tile_radius, offset=(x, y), fill=self._colors[terrain], tags=self._tile_tag(tile))

    def _draw_hexagon(self, radius, offset=(0, 0), rotate=30, fill='black', tags=None):
        points = self._hex_points(radius, offset, rotate)
        a = self._board_canvas.create_polygon(*points, fill=fill, tags=tags)

    def _draw_numbers(self, board, terrain_centers):
        logging.debug('Drawing numbers')
        for tile_id, (x, y) in terrain_centers.items():
            tile = board.tiles[tile_id - 1]
            self._draw_number(x, y, tile.number, tile)

    def _draw_ports(self, board, terrain_centers):
        logging.debug('Drawing ports')
        port_centers = []
        for tile_id, dirn, port in board.ports:
            tile_x, tile_y = terrain_centers[tile_id]
            theta = self._tile_angle_order.index(dirn) * 60
            radius = 2 * self._center_to_edge + self._tile_padding
            dx = radius * math.cos(math.radians(theta))
            dy = radius * math.sin(math.radians(theta))
            #logging.debug('tile_id={}, port={}, x+dx={}+{}, y+dy={}+{}'.format(tile_id, port, tile_x, dx, tile_y, dy))
            port_centers.append((tile_x + dx, tile_y + dy, theta))

        port_centers = self._fixup_port_centers(port_centers)
        for (x, y, angle), port in zip(port_centers, [port for _, _, port in board.ports]):
            # logging.debug('Drawing port={} at ({},{})'.format(port, x, y))
            self._draw_port(x, y, angle, port)

    def _draw_port(self, x, y, angle, port):
        """Draw a equilateral triangle with the top point at x, y and the bottom facing the direction
        given by the angle."""
        points = [x, y]
        for adjust in (-30, 30):
            x1 = x + math.cos(math.radians(angle + adjust)) * self._tile_radius
            y1 = y + math.sin(math.radians(angle + adjust)) * self._tile_radius
            points.extend([x1, y1])
        self._board_canvas.create_polygon(*points, fill=self._colors[port])
        self._board_canvas.create_text(x, y, text=port.value, font=self._hex_font)

    def _draw_pieces(self, board, terrain_centers):
        roads, settlements, cities = self._get_pieces(board)
        for coord, road in roads:
            self._draw_piece(coord, road, terrain_centers)
        logging.debug('Roads drawn: {}'.format(len(roads)))
        for coord, settlement in settlements:
            self._draw_piece(coord, settlement, terrain_centers)
        for coord, city in cities:
            self._draw_piece(coord, city, terrain_centers)

    def _draw_piece(self, coord, piece, terrain_centers, ghost=False):
        x, y, angle = self._get_piece_center(coord, piece, terrain_centers)
        tag = None
        if piece.type == PieceType.road:
            self._draw_road(x, y, coord, piece, angle=angle, ghost=ghost)
            tag = self._road_tag(coord)
        elif piece.type == PieceType.settlement:
            self._draw_settlement(x, y, coord, piece, ghost=ghost)
            tag = self._settlement_tag(coord)
        elif piece.type == PieceType.city:
            self._draw_city(x, y, coord, piece, ghost=ghost)
            tag = self._city_tag(coord)

        if ghost:
            self._board_canvas.tag_bind(tag, '<ButtonPress-1>',
                                        func=functools.partial(self.piece_click, piece.type))

    def _draw_piece_shadows(self, piece_type, board, terrain_centers):
        logging.debug('Drawing piece shadows of type={}'.format(piece_type.value))
        piece = Piece(piece_type, self.game.get_cur_player())
        if piece_type == PieceType.road:
            edges = hexgrid.legal_edge_coords()
            count = 0
            for edge in edges:
                if (hexgrid.EDGE, edge) in board.pieces:
                    logging.debug('Not drawing shadow road at coord={}'.format(edge))
                    continue
                count += 1
                self._draw_piece(edge, piece, terrain_centers, ghost=True)
            logging.debug('Road shadows drawn: {}'.format(count))
        else:
            nodes = hexgrid.legal_node_coords()
            for node in nodes:
                if (hexgrid.NODE, node) in board.pieces:
                    continue
                self._draw_piece(node, piece, terrain_centers, ghost=True)

    def _piece_tkinter_opts(self, coord, piece, **kwargs):
        opts = dict()
        tag_funcs = {
            PieceType.road: self._road_tag,
            PieceType.settlement: self._settlement_tag,
            PieceType.city: self._city_tag,
        }
        opts['tags'] = tag_funcs[piece.type](coord)
        opts['outline'] = piece.owner.color
        opts['fill'] = piece.owner.color
        if 'ghost' in kwargs and kwargs['ghost'] == True:
            opts['fill'] = '' # transparent
            opts['activefill'] = piece.owner.color
        del kwargs['ghost']
        opts.update(kwargs)
        return opts

    def _draw_road(self, x, y, coord, piece, angle, ghost=False):
        opts = self._piece_tkinter_opts(coord, piece, ghost=ghost)
        length = self._tile_radius * 0.7
        height = self._tile_padding * 2.5
        points = [x - length/2, y - height/2] # left top
        points += [x + length/2, y - height/2] # right top
        points += [x + length/2, y + height/2] # right bottom
        points += [x - length/2, y + height/2] # left bottom
        points = tkinterutils.rotate_2poly(angle, points, (x, y))
        logging.debug('Drawing road={} at coord={}, angle={} with opts={}'.format(
            piece, coord, angle, opts
        ))
        self._board_canvas.create_polygon(*points,
                                            **opts)

    def _draw_settlement(self, x, y, coord, piece, ghost=False):
        opts = self._piece_tkinter_opts(coord, piece, ghost=ghost)
        width = 18
        height = 14
        point_height = 8
        points = [x - width/2, y - height/2] # left top
        points += [x, y - height/2 - point_height] # middle point
        points += [x + width/2, y - height/2] # right top
        points += [x + width/2, y + height/2] # right bottom
        points += [x - width/2, y + height/2] # left bottom
        self._board_canvas.create_polygon(*points,
                                          **opts)

    def _draw_city(self, x, y, coord, piece, ghost=False):
        opts = self._piece_tkinter_opts(coord, piece, ghost=ghost)
        self._board_canvas.create_rectangle(x-20, y-20, x+20, y+20,
                                            **opts)

    def _get_pieces(self, board):
        """Returns roads, settlements, and cities on the board
        """
        roads = list()
        settlements = list()
        cities = list()
        for (_, coord), piece in board.pieces.items():
            if piece.type == PieceType.road:
                roads.append((coord, piece))
            elif piece.type == PieceType.settlement:
                settlements.append((coord, piece))
            elif piece.type == PieceType.city:
                cities.append((coord, piece))
        return roads, settlements, cities

    def _get_piece_center(self, piece_coord, piece, terrain_centers):
        """Takes a piece's hex coordinate, the piece itself, and the terrain_centers
        dictionary which maps tile_id->(x,y)

        Returns the piece's center, as an (x,y) pair. Also returns the angle the
        piece should be rotated at, if any
        """
        tile_ids = hexgrid.legal_tile_ids()
        if piece.type == PieceType.road:
            tile_id = hexgrid.nearest_tile_to_edge(tile_ids, piece_coord)
            tile_coord = hexgrid.tile_id_to_coord(tile_id)
            direction = hexgrid.tile_edge_offset_to_direction(piece_coord - tile_coord)
            angle = 60*self._edge_angle_order.index(direction)
            terrain_x, terrain_y = terrain_centers[tile_id]
            dx = math.cos(math.radians(angle)) * self.distance_tile_to_edge()
            dy = math.sin(math.radians(angle)) * self.distance_tile_to_edge()
            return terrain_x + dx, terrain_y + dy, angle + 90
        elif piece.type in [PieceType.settlement, PieceType.city]:
            tile_id = hexgrid.nearest_tile_to_node(tile_ids, piece_coord)
            tile_coord = hexgrid.tile_id_to_coord(tile_id)
            direction = hexgrid.tile_node_offset_to_direction(piece_coord - tile_coord)
            angle = 30 + 60*self._node_angle_order.index(direction)
            terrain_x, terrain_y = terrain_centers[tile_id]
            dx = math.cos(math.radians(angle)) * self._tile_radius
            dy = math.sin(math.radians(angle)) * self._tile_radius
            return terrain_x + dx, terrain_y + dy, 0
        else:
            logging.warning('Unknown piece={}'.format(piece))

    def _fixup_offset(self):
        offx, offy = self._board_center
        radius = 4 * self._center_to_edge + 2 * self._tile_padding
        offx += radius * math.cos(math.radians(240))
        offy += radius * math.sin(math.radians(240))
        return (offx, offy)

    def _fixup_terrain_centers(self, centers):
        offx, offy = self._fixup_offset()
        return dict((tile_id, (x + offx, y + offy)) for tile_id, (x, y) in centers.items())

    def _fixup_port_centers(self, port_centers):
        return [(x, y, angle + 180) for x, y, angle in port_centers]

    def _draw_number(self, x, y, number: HexNumber, tile):
        if number is HexNumber.none:
            return
        # logging.debug('Drawing number={}, HexNumber={}'.format(number.value, number))
        color = 'red' if number.value in (6, 8) else 'black'
        self._board_canvas.create_text(x, y, text=str(number.value), font=self._hex_font, fill=color, tags=self._tile_tag(tile))

    def _hex_points(self, radius, offset, rotate):
        offx, offy = offset
        points = []
        for theta in (60 * n for n in range(6)):
            x = (math.cos(math.radians(theta + rotate)) * radius) + offx
            y = (math.sin(math.radians(theta + rotate)) * radius) + offy
            points += [x, y]
        return points

    def distance_tile_to_edge(self):
        return self._tile_radius * math.cos(math.radians(30)) + 1/2*self._tile_padding

    def _tile_tag(self, tile):
        return 'tile_' + str(tile.tile_id)

    def _road_tag(self, coord):
        return 'road_' + hex(coord)

    def _settlement_tag(self, coord):
        return 'settlement_' + hex(coord)

    def _city_tag(self, coord):
        return 'city_' + hex(coord)

    def _tile_id_from_tag(self, tag):
        return int(tag[len('tile_'):])

    def _coord_from_road_tag(self, tag):
        return int(tag[len('road_0x'):], 16)

    def _coord_from_settlement_tag(self, tag):
        return int(tag[len('settlement_0x'):], 16)

    def _coord_from_city_tag(self, tag):
        return int(tag[len('city_0x'):], 16)

    _tile_radius  = 50
    _tile_padding = 3
    _board_center = (300, 300)
    _tile_angle_order = ('E', 'SE', 'SW', 'W', 'NW', 'NE') # 0 + 60*index
    _edge_angle_order = ('E', 'SE', 'SW', 'W', 'NW', 'NE') # 0 + 60*index
    _node_angle_order = ('SE', 'S', 'SW', 'NW', 'N', 'NE') # 30 + 60*index
    _hex_font     = (('Helvetica'), 18)
    _colors = {
        Terrain.ore: 'gray94',
        Port.ore: 'gray94',
        Terrain.wood: 'forest green',
        Port.wood: 'forest green',
        Terrain.sheep: 'green yellow',
        Port.sheep: 'green yellow',
        Terrain.brick: 'sienna4',
        Port.brick: 'sienna4',
        Terrain.wheat: 'yellow2',
        Port.wheat: 'yellow2',
        Terrain.desert: 'wheat1',
        Port.any: 'gray'}


class SetupGameToolbarFrame(tkinter.Frame):

    def __init__(self, master, game, options=None, *args, **kwargs):
        super(SetupGameToolbarFrame, self).__init__()
        self.master = master
        self.game = game

        self.options = options or dict()
        self.options.update({
            'hex_resource_selection': True,
            'hex_number_selection': False
        })

        tkinter.Label(self, text="Board Setup", anchor=tkinter.W).pack(side=tkinter.TOP, fill=tkinter.X)
        for option in TkinterOptionWrapper(self.options):
            option.callback()
            tkinter.Checkbutton(self, text=option.text, justify=tkinter.LEFT, command=option.callback, var=option.var) \
                .pack(side=tkinter.TOP, fill=tkinter.X)

        tkinter.Label(self, text="Players (name color)", anchor=tkinter.W).pack(side=tkinter.TOP, fill=tkinter.X)
        defaults = ('yurick green', 'josh blue', 'zach orange', 'ross red')
        self.player_entries_vars = [(tkinter.Entry(self), tkinter.StringVar()) for i in range(len(defaults))]
        for (entry, var), default in zip(self.player_entries_vars, defaults):
            var.set(default)
            entry.config(textvariable=var)
            entry.pack(side=tkinter.TOP, fill=tkinter.BOTH)

        btn_start_game = tkinter.Button(self, text='Start Game', command=self.on_start_game)
        btn_start_game.pack(side=tkinter.TOP, fill=tkinter.X)

    def on_start_game(self):
        def get_name(var):
            return var.get().split(' ')[0]

        def get_color(var):
            return var.get().split(' ')[1]

        self.game.start([Player(i, get_name(var), get_color(var))
                         for i, (_, var) in enumerate(self.player_entries_vars, 1)])


class GameToolbarFrame(tkinter.Frame):

    def __init__(self, master, game, *args, **kwargs):
        super(GameToolbarFrame, self).__init__()
        self.master = master
        self.game = game

        self.game.observers.add(self)

        self._cur_player = self.game.get_cur_player()
        self._cur_player_name = tkinter.StringVar()
        self.set_cur_player_name()

        label_cur_player_name = tkinter.Label(self, textvariable=self._cur_player_name, anchor=tkinter.W)
        frame_roll = RollFrame(self, self.game)
        frame_robber = RobberFrame(self, self.game)
        frame_build = BuildFrame(self, self.game)
        frame_trade = TradeFrame(self, self.game)
        frame_play_dev = PlayDevCardFrame(self, self.game)
        frame_end_turn = EndTurnFrame(self, self.game)
        frame_end_game = EndGameFrame(self, self.game)

        label_cur_player_name.pack(side=tkinter.TOP, fill=tkinter.X)
        frame_roll.pack(side=tkinter.TOP, fill=tkinter.X)
        frame_robber.pack(side=tkinter.TOP, fill=tkinter.X)
        frame_build.pack(side=tkinter.TOP, fill=tkinter.X)
        frame_trade.pack(side=tkinter.TOP, fill=tkinter.X)
        frame_play_dev.pack(side=tkinter.TOP, fill=tkinter.X)
        frame_end_turn.pack(side=tkinter.TOP, fill=tkinter.X)
        frame_end_game.pack(side=tkinter.BOTTOM, fill=tkinter.BOTH)

    def set_game(self, game):
        self.game = game

    def notify(self, observable):
        if self._cur_player.color != self.game.get_cur_player().color:
            self.set_cur_player_name()

    def set_cur_player_name(self):
        self._cur_player = self.game.get_cur_player()
        self._cur_player_name.set('Current Player: {0} ({1})'.format(
            self._cur_player.color,
            self._cur_player.name
        ))


class RollFrame(tkinter.Frame):

    def __init__(self, master, game, *args, **kwargs):
        super(RollFrame, self).__init__(master)
        self.master = master
        self.game = game
        self.game.observers.add(self)

        self.roll = tkinter.StringVar()
        self.spinner = tkinter.Spinbox(self, values=(2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), textvariable=self.roll)
        self.button = tkinter.Button(self, text="Roll", command=self.on_roll)

        self.set_states()

        self.spinner.pack(side=tkinter.LEFT)
        self.button.pack(side=tkinter.RIGHT)

    def notify(self, observable):
        self.set_states()

    def set_states(self):
        self.spinner.configure(state=can_do[self.game.state.can_roll()])
        self.button.configure(state=can_do[self.game.state.can_roll()])

    def on_roll(self):
        self.button.configure(state=tkinter.DISABLED)
        self.spinner.configure(state=tkinter.DISABLED)
        self.game.roll(self.roll.get())


class RobberFrame(tkinter.Frame):

    def __init__(self, master, game):
        super(RobberFrame, self).__init__(master)
        self.master = master
        self.game = game
        self.game.observers.add(self)

        self.move_robber = tkinter.Button(self, text="Move Robber", state=tkinter.DISABLED, command=self.on_move_robber)
        self.steal = tkinter.Button(self, text="Steal", state=tkinter.DISABLED, command=self.on_steal)

        self.set_states()

        self.move_robber.pack(side=tkinter.LEFT, fill=tkinter.X, expand=True)
        self.steal.pack(side=tkinter.RIGHT, fill=tkinter.X, expand=True)

    def notify(self, observable):
        self.set_states()

    def set_states(self):
        self.move_robber.configure(state=can_do[self.game.state.can_move_robber()])
        self.steal.configure(state=can_do[self.game.state.can_steal()])

    def on_move_robber(self):
        self.game.move_robber(None)

    def on_steal(self):
        self.game.steal(None)


class BuildFrame(tkinter.Frame):

    def __init__(self, master, game):
        super(BuildFrame, self).__init__(master)
        self.master = master
        self.game = game
        self.game.observers.add(self)

        self.label = tkinter.Label(self, text="Build", anchor=tkinter.W)
        self.road = tkinter.Button(self, text="Road", command=self.on_buy_road)
        self.settlement = tkinter.Button(self, text="Settlement", command=self.on_buy_settlement)
        self.city = tkinter.Button(self, text="City", command=self.on_buy_city)
        self.dev_card = tkinter.Button(self, text="Dev Card", command=self.on_buy_dev_card)

        self.set_states()

        self.label.pack(fill=tkinter.X)
        self.road.pack(fill=tkinter.X, expand=True)
        self.settlement.pack(fill=tkinter.X, expand=True)
        self.city.pack(fill=tkinter.X, expand=True)
        self.dev_card.pack(fill=tkinter.X, expand=True)

    def notify(self, observable):
        self.set_states()

    def set_states(self):
        self.road.configure(state=can_do[self.game.state.can_buy_road()])
        self.settlement.configure(state=can_do[self.game.state.can_buy_settlement()])
        self.city.configure(state=can_do[self.game.state.can_buy_city()])
        self.dev_card.configure(state=can_do[self.game.state.can_buy_dev_card()])

    def on_buy_road(self):
        # actual road purchase and catanlog happens in the piece onclick in BoardFrame
        if self.game.state.is_in_pregame():
            self.game.set_state(states.GameStatePreGamePlacingPiece(self.game, PieceType.road))
        else:
            self.game.set_state(states.GameStatePlacingPiece(self.game, PieceType.road))

    def on_buy_settlement(self):
        # see on_buy_road
        if self.game.state.is_in_pregame():
            self.game.set_state(states.GameStatePreGamePlacingPiece(self.game, PieceType.settlement))
        else:
            self.game.set_state(states.GameStatePlacingPiece(self.game, PieceType.settlement))

    def on_buy_city(self):
        # see on_buy_road
        if self.game.state.is_in_pregame():
            self.game.set_state(states.GameStatePreGamePlacingPiece(self.game, PieceType.city))
        else:
            self.game.set_state(states.GameStatePlacingPiece(self.game, PieceType.city))

    def on_buy_dev_card(self):
        logging.warning('Buying dev cards not yet implemented')
        #self.game.buy_dev_card()


class TradeFrame(tkinter.Frame):

    def __init__(self, master, game):
        super(TradeFrame, self).__init__(master)
        self.master = master
        self.game = game
        self._cur_player = self.game.get_cur_player()
        self.game.observers.add(self)

        self.label_player = tkinter.Label(self, text="Trade with Player")
        self.player_buttons = list()
        for p in self.game.players:
            button = tkinter.Button(self, text='{0} ({1})'.format(p.color, p.name), state=tkinter.DISABLED)
            self.player_buttons.append(button)

        self.set_states(self._cur_player)

        self.label_port = tkinter.Label(self, text="Trade with Port")
        self.port_buttons = list()
        for p in list(Port):
            button = tkinter.Button(self, text='{0}'.format(p.value), state=tkinter.DISABLED)
            self.port_buttons.append(button)

        ##
        # Place elements in frame
        #

        row = 0
        self.label_player.grid(row=row, sticky=tkinter.W)
        row += 1

        for i, button in enumerate(self.player_buttons):
            button.grid(row=row + i // 2, column=i % 2, sticky=tkinter.EW)
        row += 2

        self.label_port.grid(row=row, sticky=tkinter.W)
        row += 1

        for i, button in enumerate(self.port_buttons):
            button.grid(row=row + i // 2, column=i % 2, sticky=tkinter.EW)
        row += 2

    def notify(self, observable):
        # You can't trade with yourself
        self._cur_player = self.game.get_cur_player()
        self.set_states(self._cur_player)

    def set_states(self, current_player):
        """You can't trade with yourself, and you have to roll before trading"""
        for player, button in zip(self.game.players, self.player_buttons):
            if self.game.state.can_trade() and player != current_player:
                button.configure(state=tkinter.NORMAL)
            else:
                button.configure(state=tkinter.DISABLED)


class PlayDevCardFrame(tkinter.Frame):

    def __init__(self, master, game):
        super(PlayDevCardFrame, self).__init__(master)
        self.master = master
        self.game = game
        self.game.observers.add(self)

        self.label = tkinter.Label(self, text="Play Dev Card", anchor=tkinter.W)
        self.knight = tkinter.Button(self, text="Knight", command=self.on_knight)
        self.monopoly = tkinter.Button(self, text="Monopoly", command=self.on_monopoly)
        self.road_builder = tkinter.Button(self, text="Road Builder", command=self.on_road_builder)
        self.victory_point = tkinter.Button(self, text="Victory Point", command=self.on_victory_point)

        self.set_states()

        self.label.pack(fill=tkinter.X)
        self.knight.pack(fill=tkinter.X, expand=True)
        self.monopoly.pack(fill=tkinter.X, expand=True)
        self.road_builder.pack(fill=tkinter.X, expand=True)
        self.victory_point.pack(fill=tkinter.X, expand=True)

    def notify(self, observable):
        self.set_states()

    def set_states(self):
        self.knight.configure(state=can_do[self.game.state.can_play_knight()])
        self.monopoly.configure(state=can_do[self.game.state.can_play_monopoly()])
        self.road_builder.configure(state=can_do[self.game.state.can_play_road_builder()])
        self.victory_point.configure(state=can_do[self.game.state.can_play_victory_point()])

    def on_knight(self):
        self.game.play_knight()

    def on_monopoly(self):
        resource = Terrain.brick # todo get resource from dropdown dialog
        self.game.play_monopoly(resource)

    def on_road_builder(self):
        # todo UI for choosing where both roads go, pass them to Game
        self.game.play_road_builder(None, None, None, None)

    def on_victory_point(self):
        self.game.play_victory_point()


class EndTurnFrame(tkinter.Frame):

    def __init__(self, master, game):
        super(EndTurnFrame, self).__init__(master)
        self.master = master
        self.game = game
        self.game.observers.add(self)

        self.label = tkinter.Label(self, text='--')
        self.end_turn = tkinter.Button(self, text='End Turn', state=tkinter.DISABLED, command=self.on_end_turn)

        self.set_states()

        self.label.pack()
        self.end_turn.pack(side=tkinter.TOP, fill=tkinter.X)

    def notify(self, observable):
        self.set_states()

    def set_states(self):
        if self.game.state.can_end_turn():
            self.end_turn.configure(state=tkinter.NORMAL)
        else:
            self.end_turn.configure(state=tkinter.DISABLED)

    def on_end_turn(self):
        self.game.end_turn()


class EndGameFrame(tkinter.Frame):

    def __init__(self, master, game):
        super(EndGameFrame, self).__init__(master)
        self.master = master
        self.game = game

        self.end_game = tkinter.Button(self, text='End Game', state=tkinter.NORMAL, command=self.on_end_game)
        self.end_game.pack(side=tkinter.TOP, fill=tkinter.X)

    def on_end_game(self):
        title = 'End Game Confirmation'
        message = 'End Game? ({0} ({1}) wins)'.format(
            self.game.get_cur_player().color, self.game.get_cur_player().name
        )
        if messagebox.askyesno(title, message):
            self.game.end()


class TkinterOptionWrapper:
    """Dynamically hook up the board options to tkinter checkbuttons.

    Tkinter checkbuttons use a tkinter 'var' object to store the checkbutton
    value, so dynamically create those vars based on the board options and
    keep them here, along with callbacks to update the board options when the
    checkbutton is checked/unchecked.

    Also stores the option description text. That should probably belong to the
    board option 'class', but at the moment there's no reason not to keep that
    a simple dict.

    Parameters
    ----------

    options : A dict of option identifier (name) to option value

    The wrapper will dynamically update the value of the option in the
    option_dict when the user checks or unchecks the corresponding checkbutton
    in the UI.
    """

    Option = collections.namedtuple('_Option', ['text', 'var', 'callback'])
    _descriptions = {
        'hex_resource_selection': 'Cycle hex resource',
        'hex_number_selection': 'Cycle hex number'
    }

    def __init__(self, option_dict):
        self._opts = {}

        # Can't define this as a closure inside the following for loop as each
        # definition will become the value of cb which has a scope local to the
        # function, not to the for loop.  Use functools.partial in the loop to
        # create a specific callable instance.
        def cb_template(name, var):
            option_dict[name] = var.get()
        for name, value in option_dict.items():
            var = tkinter.BooleanVar()
            var.set(value)
            cb = functools.partial(cb_template, name, var)
            self._opts[name] = self.Option(self._descriptions.get(name) or name, var, cb)

    def __getattr__(self, name):
        attr = self.__dict__.get(name)
        if '_opts' in self.__dict__ and not attr:
            attr = self._opts.get(name)
        return attr

    def __iter__(self):
        for opt in sorted(self._opts.values()):
            yield opt

