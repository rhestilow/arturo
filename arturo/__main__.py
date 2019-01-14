import argparse
import sys

import arturo.gfx as gfx
import arturo.gfx.svg as svg

def draw():
    return gfx.Canvas().tile(
        gfx.triangle(1),
    )

def main():
    parser = argparse.ArgumentParser(description="Art scripting language")
    parser.add_argument("dest", metavar="DEST", help="file to output to")
    args = parser.parse_args()

    canvas = draw()
    svg.output(canvas, args.dest)

if __name__ == "__main__":
    main()
