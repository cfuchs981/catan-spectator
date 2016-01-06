"""
module tkinterutils provides methods useful in tkinter graphics programming

Currently, it provides
- polygon rotation methods
- OptionMenu refresh-ability
"""
import math
import tkinter


def rotate_2poly(angle, coords, origin):
    """
    Rotates a list of 2D coords about the origin.
    :param angle: cw from E, in degrees
    :param coords: iterable of coordinates, eg [x1, y1, x2, y2, .. xn, yn]
    :param origin: [x0, y0]
    :return: Rotated list of coordinates
    """
    xs = coords[0::2]
    ys = coords[1::2]
    if len(xs) != len(ys):
        raise Exception('Malformed 2poly={}'.format(coords))
    return rotate_poly(angle, zip(xs, ys), origin)


def rotate_poly(angle, points, origin):
    """
    Rotates an iterable of points about the origin.
    :param angle: cw from E, in degrees
    :param points: iterable of points, eg [[x1, y1], [x2, y2], .. [xn, yn]]
    :param origin: [x0, y0]
    :return: Rotated list of points
    """
    return list(rotate_point(angle, point, origin) for point in points)


def rotate_rect(angle, top_left, bottom_right, origin):
    """
    Rotates a rectangle about the origin.
    :param angle: cw from E, in degrees
    :param top_left: [x, y]
    :param bottom_right: [x, y]
    :param origin: [x0, y0]
    :return: Rotated list of points to draw as a polygon, eg [[x1, y1], [x2, y2], ...[xn, yn]]
    """
    points = top_left.copy()
    points.extend(bottom_right)
    return rotate_poly(angle, points, origin)


def rotate_point(angle, point, origin):
    """
    Rotates a point about the origin.

    Used from http://stackoverflow.com/q/8948001/1817465 mramazingguy asked Jan 20 '12 at 21:20

    :param angle: cw from E, in degrees
    :param point: [x, y]
    :param origin: [x0, y0]
    :return: The point, rotated about the origin.
    """
    sinT = math.sin(math.radians(angle))
    cosT = math.cos(math.radians(angle))
    return (origin[0] + (cosT * (point[0] - origin[0]) - sinT * (point[1] - origin[1])),
            origin[1] + (sinT * (point[0] - origin[0]) + cosT * (point[1] - origin[1])))


def refresh_option_menu(option_menu, var, new_options):
    """http://stackoverflow.com/a/17581364/1817465"""
    option_menu['menu'].delete(0, 'end')

    # Insert list of new options (tk._setit hooks them up to var)
    for choice in new_options:
        option_menu['menu'].add_command(label=choice, command=tkinter._setit(var, choice))

