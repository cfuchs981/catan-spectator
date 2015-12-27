import math

def rotate_2poly(angle, coords, origin):
    """
    Rotates a 2-dimensional polygon about the origin.
    :param angle: cw from E, in degrees
    :param coords: List of coordinates, eg [x1, y1, x2, y2, .. xn, yn]
    :param origin: [x0, y0]
    :return: Rotated list of coordinates
    """
    xs = coords[0::2]
    ys = coords[1::2]
    if len(xs) != len(ys):
        raise Exception('Malformed 2poly={}'.format(coords))
    return rotate_poly(angle, zip(xs, ys), origin)


def rotate_poly(angle, points, origin):
    return list(rotate_point(angle, point, origin) for point in points)

def rotate_rect(angle, top_left, bottom_right, origin):
    points = top_left.copy()
    points.extend(bottom_right)
    return rotate_poly(angle, points, origin)


def rotate_point(angle, point, origin):
    """http://stackoverflow.com/q/8948001/1817465 mramazingguy asked Jan 20 '12 at 21:20
    """
    sinT = math.sin(math.radians(angle))
    cosT = math.cos(math.radians(angle))
    return (origin[0] + (cosT * (point[0] - origin[0]) - sinT * (point[1] - origin[1])),
            origin[1] + (sinT * (point[0] - origin[0]) + cosT * (point[1] - origin[1])))

