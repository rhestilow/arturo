import math
from collections import namedtuple

import svgwrite

Size = namedtuple("Size", "w h")

DEFAULT_SCALE = 1
DEFAULT_SCALE_FACTOR = 1.0

def fmt_unit(value, unit):
    return "{}{}".format(value, unit)

def fmt_size(size, unit):
    return fmt_unit(size.w, unit), fmt_unit(size.h, unit)

Canvas = namedtuple("Canvas", "width height dpi scale_factor")
DrawContext = namedtuple("DrawContext", "dwg canvas x y")

def draw(ctx, instruction):
    """
    Each primitive instruction maps directly to a function with keyword
    arguments corresponding to specified property names.
    """
    # curry for polygon aliases
    def poly(n):
        return lambda ctx, *a, **k: _draw_poly(ctx, n, *a, **k)

    fns = {
        "tile": _draw_tile,
        "triangle": poly(3),
    }

    return fns[instruction.name](ctx, *instruction.args, **instruction.kwargs)

def _draw_tile(ctx, children):
    # TODO: draw all children, repeat
    draw(ctx, children[0])

def _draw_poly(ctx, vertex_count, scale=DEFAULT_SCALE):
    radius = scale * ctx.canvas.dpi / ctx.canvas.scale_factor
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

def output(script, stream):
    canvas = dict(script.meta["canvas"])
    canvas.setdefault("scale_factor", DEFAULT_SCALE_FACTOR)
    canvas = Canvas(**canvas)

    size = Size(canvas.width, canvas.height)
    dwg = svgwrite.Drawing(size=fmt_size(size, "in"), debug=True)

    # set user coordinate space
    dwg.viewbox(width=size.w * canvas.dpi, height=size.h * canvas.dpi)

    ctx = DrawContext(dwg, canvas, 0, 0)
    draw(ctx, script.layout)

    dwg.write(stream)
