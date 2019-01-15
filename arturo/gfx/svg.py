import math
from collections import namedtuple
from contextlib import contextmanager
from functools import wraps

import svgwrite

import arturo.ast as ast

Size = namedtuple("Size", "w h")
Canvas = namedtuple("Canvas", "width height dpi scale_factor")
DrawContext = namedtuple("DrawContext", "dwg canvas x y")

DEFAULT_SCALE = 1

_ops = {}

def fmt_unit(value, unit):
    return "{}{}".format(value, unit)

def fmt_size(size, unit):
    return fmt_unit(size.w, unit), fmt_unit(size.h, unit)

def _impl(op, **additional_kwargs):
    def wrapper(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            kwargs.update(additional_kwargs)
            return fn(*args, **kwargs)

        _ops[op] = inner
        return inner

    return wrapper

class Engine(object):
    def __init__(self):
        self.stack = []

    @property
    def ctx(self):
        return self.stack[-1]

    @contextmanager
    def absolute(self, *args, **kwargs):
        """
        Create a new DrawContext with absolute positoning and push it on the
        stack for the duration of the context manager.
        """
        ctx = DrawContext(*args, **kwargs)
        self.stack.append(ctx)
        yield
        self.stack.pop()

    @contextmanager
    def relative(self, dx, dy):
        """
        Create a new DrawContext at a relative offset from the
        current DrawContext and push it on the stack for the duration
        of the context manager.
        """
        ctx = DrawContext(self.ctx.dwg, self.ctx.canvas, x + dx, y + dy)
        with self.abs_ctx(ctx):
            yield

    def draw(self, instruction):
        """
        Each primitive instruction maps directly to a function with keyword
        arguments corresponding to specified property names.
        """
        return _ops[instruction.name](self, *instruction.args, **instruction.kwargs)

    @_impl("tile")
    def draw_tile(self, children):
        # TODO: draw all children, repeat
        self.draw(children[0])

    @_impl("triangle", n=3)
    @_impl("poly")
    def draw_poly(self, n, scale=DEFAULT_SCALE):
        ctx = self.ctx
        radius = scale * ctx.canvas.dpi / ctx.canvas.scale_factor
        angle = math.pi / n
        offset = radius

        # http://mathforum.org/kb/message.jspa?messageID=6700876
        # calculate polygons based on circle connecting verticies
        points = []
        for i in range(1, n + 1):
            x = ctx.x + offset + radius * math.sin(angle + i * 2 * angle)
            y = ctx.y + offset + radius * math.cos(angle + i * 2 * angle)
            points.append((x, y))

        element = ctx.dwg.polygon(points)
        ctx.dwg.add(element)

    @_impl(ast.ROOT)
    def start_draw(self, *children, width=8.5, height=11, dpi=600, scale_factor=1.0):
        # TODO: add defaults
        canvas = Canvas(width, height, dpi, scale_factor)
        size = Size(canvas.width, canvas.height)
        dwg = svgwrite.Drawing(size=fmt_size(size, "in"), debug=True)

        # set user coordinate space
        dwg.viewbox(width=size.w * canvas.dpi, height=size.h * canvas.dpi)

        with self.absolute(dwg, canvas, 0, 0):
            for child in children:
                self.draw(child)

        return dwg

def output(script, stream):
    engine = Engine()
    dwg = engine.draw(script)
    dwg.write(stream)
