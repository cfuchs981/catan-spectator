import collections
import functools
import itertools
import math
import tkinter

from board import Board


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
        'hex_resource_selection': 'Cycle hex resource type',
        'hex_number_selection': 'Cycle number on hex'
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
            self._opts[name] = self.Option(self._descriptions[name], var, cb)

    def __getattr__(self, name):
        attr = self.__dict__.get(name)
        if '_opts' in self.__dict__ and not attr:
            attr = self._opts.get(name)
        return attr

    def __iter__(self):
        for opt in self._opts.values():
            yield opt


class BoardUI(tkinter.Frame):

    def __init__(self, master, options, *args, **kwargs):
        super(BoardUI, self).__init__(master, *args, **kwargs)
        self.options = options

        self._board = Board(self.options)

        canvas = tkinter.Canvas(self, height=600, width=600, background='Royal Blue')

        cb_frame = tkinter.Frame(self)
        for option in TkinterOptionWrapper(options):
            option.callback()
            tkinter.Checkbutton(cb_frame, text=option.text, command=option.callback, var=option.var) \
                   .pack(side=tkinter.TOP, fill=tkinter.X)
        btn_start_game = tkinter.Button(cb_frame, text='Start Game', command=self.redraw)
        btn_start_game.pack(side=tkinter.TOP, fill=tkinter.BOTH)

        cb_frame.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        canvas.pack(side=tkinter.TOP, expand=tkinter.YES, fill=tkinter.BOTH)

        self._canvas = canvas
        self._btn_start_game = btn_start_game
        self._center_to_edge = math.cos(math.radians(30)) * self._tile_radius

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

        centers = {}
        last = None

        for tile in board.tiles:
            if not last:
                centers[tile.id] = (0, 0)
                last = tile
                continue

            # Calculate the center of this tile as an offset from the center of
            # the neighboring tile in the given direction.
            ref_center = centers[last.id]
            direction = board.direction(last, tile)
            theta = self._angle_order.index(direction) * 60
            radius = 2 * self._center_to_edge + self._tile_padding
            dx = radius * math.cos(math.radians(theta))
            dy = radius * math.sin(math.radians(theta))
            centers[tile.id] = (ref_center[0] + dx, ref_center[1] + dy)
            last = tile

        port_centers = []
        for tile_id, dirn, value in board.ports:
            ref_center = centers[tile_id]
            theta = self._angle_order.index(dirn) * 60
            radius = 2 * self._center_to_edge + self._tile_padding
            dx = radius * math.cos(math.radians(theta))
            dy = radius * math.sin(math.radians(theta))
            port_centers.append((ref_center[0] + dx, ref_center[1] + dy, theta))

        offx, offy = self._board_center

        # Temporary hack to center the board. Not generic to different board types.
        radius = 4 * self._center_to_edge + 2 * self._tile_padding
        offx += radius * math.cos(math.radians(240))
        offy += radius * math.sin(math.radians(240))

        centers = dict((tile_id, (x + offx, y + offy)) for tile_id, (x, y) in centers.items())
        for tile_id, (x, y) in centers.items():
            tile = board.tiles[tile_id - 1]
            self._draw_tile(x, y, tile.terrain, tile.value, tile)
            self._canvas.tag_bind(self._tile_tag(tile), '<ButtonPress-1>', func=self.tile_click)

        port_centers = [(x + offx, y + offy, t + 180) for x, y, t in port_centers]
        for (x, y, t), value in zip(port_centers, [v for _, _, v in board.ports]):
            self._draw_port(x, y, t, value)

    def redraw(self):
        self._canvas.delete(tkinter.ALL)
        self.draw(self._board)

    def tile_click(self, event):
        tag = self._canvas.gettags(event.widget.find_closest(event.x, event.y))[0]
        if self.options.get('hex_resource_selection'):
            self._board.cycle_hex_type(self._tile_id_from_tag(tag))
        if self.options.get('hex_number_selection'):
            self._board.cycle_hex_number(self._tile_id_from_tag(tag))
        self.redraw()

    def _hex_points(self, radius, offset, rotate):
        offx, offy = offset
        points = []
        for theta in (60 * n for n in range(6)):
            x = (math.cos(math.radians(theta + rotate)) * radius) + offx
            y = (math.sin(math.radians(theta + rotate)) * radius) + offy
            points.append((x, y))
        return points

    def _draw_hexagon(self, radius, offset=(0, 0), rotate=30, fill='black', tags=None):
        points = self._hex_points(radius, offset, rotate)
        a = self._canvas.create_polygon(*itertools.chain.from_iterable(points), fill=fill, tags=tags)

    def _tile_tag(self, tile):
        return 'tile_' + str(tile.id)

    def _tile_id_from_tag(self, tag):
        return int(tag[len('tile_'):])

    def _draw_tile(self, x, y, terrain, value, tile):
        self._draw_hexagon(self._tile_radius, offset=(x, y), fill=self._colors[terrain], tags=self._tile_tag(tile))
        if value:
            color = 'red' if value in (6, 8) else 'black'
            self._canvas.create_text(x, y, text=str(value), font=self._hex_font, fill=color)

    def _draw_port(self, x, y, angle, value):
        """Draw a equilateral triangle with the top point at x, y and the bottom facing the direction
        given by the angle."""
        points = [x, y]
        for adjust in (-30, 30):
            x1 = x + math.cos(math.radians(angle + adjust)) * self._tile_radius
            y1 = y + math.sin(math.radians(angle + adjust)) * self._tile_radius
            points.extend([x1, y1])
        self._canvas.create_polygon(*points, fill=self._colors[value])
        self._canvas.create_text(x, y, text=value, font=self._hex_font)

    _tile_radius  = 50
    _tile_padding = 3
    _board_center = (300, 300)
    _angle_order  = ('E', 'SE', 'SW', 'W', 'NW', 'NE')
    _hex_font     = (('Sans'), 18)
    _colors = {
        'M': 'gray94',
        'O': 'gray94',
        'F': 'forest green',
        'L': 'forest green',
        'P': 'green yellow',
        'W': 'green yellow',  # wool
        'C': 'sienna4',
        'B': 'sienna4',
        'H': 'yellow2',  # wheat
        'G': 'yellow2',
        'D': 'wheat1',
        '?': 'gray'}
