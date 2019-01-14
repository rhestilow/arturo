from collections import namedtuple

META = { "canvas" }
LAYOUTS = { "tile" }
PRIMITIVES = { "triangle" }

Script = namedtuple("Script", "meta layout")
Instruction = namedtuple("Instruction", "name args kwargs")
