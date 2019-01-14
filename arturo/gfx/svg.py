import math
from collections import namedtuple

import svgwrite

from arturo.gfx.canvas import TILE, POLY

Size = namedtuple("Size", "w h")
SIZE = Size(2.75, 4.75)
DPI = 600
SCALE_FACTOR = 1.0

def fmt_unit(value, unit):
    return "{}{}".format(value, unit)

def fmt_size(size, unit):
    return fmt_unit(size.w, unit), fmt_unit(size.h, unit)

DrawContext = namedtuple("DrawContext", "dwg x y")

def draw(ctx, instruction):
    fns = {
        TILE: tile,
        POLY: poly,
    }

    (name, *args) = instruction
    return fns[name](ctx, *args)

def tile(ctx, children):
    # TODO: draw all children, repeat
    draw(ctx, children[0])

def poly(ctx, vertex_count, scale):
    radius = scale * DPI / SCALE_FACTOR
    angle = math.pi / vertex_count
    offset = radius

    # http://mathforum.org/kb/message.jspa?messageID=6700876
    # calculate polygons based on circle connecting verticies
    points = []
    for i in range(1, vertex_count + 1):
        x = ctx.x + offset + radius * math.sin(angle + i * 2 * angle)
        y = ctx.y + offset + radius * math.cos(angle + i * 2 * angle)
        points.append((x, y))

    element = ctx.dwg.polygon(points)
    ctx.dwg.add(element)

def output(canvas, path):
    dwg = svgwrite.Drawing(path, size=fmt_size(SIZE, "in"), debug=True)

    # set user coordinate space
    dwg.viewbox(width=SIZE.w * DPI, height=SIZE.h * DPI)

    ctx = DrawContext(dwg, 0, 0)
    draw(ctx, canvas)

    dwg.save()
