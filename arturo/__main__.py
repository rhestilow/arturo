import argparse
import sys

import arturo.parser
import arturo.gfx.svg

def main():
    parser = argparse.ArgumentParser(description="Art scripting language")
    parser.add_argument("src", metavar="SRC", help="file to read from",
            type=argparse.FileType("r"), default=sys.stdin, nargs="?")
    parser.add_argument("--out", "-o", metavar="DEST", help="file to output to",
            type=argparse.FileType("w"), default=sys.stdout)
    args = parser.parse_args()

    script = arturo.parser.parse(args.src)

    with args.out:
        arturo.gfx.svg.output(script, args.out)

if __name__ == "__main__":
    main()
