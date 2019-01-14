import collections.abc
import yaml

import arturo.ast as ast

def _parse_layout_element(element):
    """
    Layout elements can either be strings or single-element dicts with
    property dicts nested underneath:

    - element

    or

    - element:
            property: here
            another: etc
    """
    if element in ast.PRIMITIVES:
        return ast.Instruction(element, args=[], kwargs={})
    elif len(element) == 1:
        (name, kwargs) = element.items()[0]
        return ast.Instruction(name, args=[], kwargs=kwargs)

def _parse_layout(name, body):
    """
    A layout is just a layout name with a list of elements under it.

    layout:
        - element
        - element

    You can also specify properties for the layout, in which case the
    list of elements must be qualified with `do`:

    layout:
        style: fancy
        do:
            - element
            - another
            - etc

    Currently layouts are toplevel only, and only one may be specified.
    """
    if isinstance(body, collections.abc.Mapping):
        properties = dict(body)
        elements = body.pop("do")
    else:
        properties = {}
        elements = body

    children = [ _parse_layout_element(element) for element in elements ]
    return ast.Instruction(name, args=[ children ], kwargs=properties)

def parse(stream):
    tree = yaml.load(stream)

    meta = {}
    layout = None

    for (toplevel, value) in tree.items():
        if toplevel in ast.META:
            meta[toplevel] = value
        elif toplevel in ast.LAYOUTS:
            if layout:
                raise ParseError("Only one layout may be specified")

            layout = _parse_layout(toplevel, value)
        else:
            raise ParseError("Unknown toplevel: {}".format(toplevel))

    return ast.Script(meta, layout)
