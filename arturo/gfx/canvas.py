TILE = "tile"
POLY = "poly"

def triangle(scale):
    return (POLY, 3, scale)

class Canvas(object):
    def __init__(self):
        # TODO: size/etc?
        pass

    def tile(self, *children):
        return (TILE, children)
