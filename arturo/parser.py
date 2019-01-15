import collections.abc
import yaml

import arturo.ast as ast

def _parse_layout_element(element):
    """
    """
    if element in ast.PRIMITIVES:
        return ast.Instruction(element, args=[], kwargs={})
    elif len(element) == 1:
        (name, kwargs) = element.items()[0]
        return ast.Instruction(name, args=[], kwargs=kwargs)

def _parse_instruction(node):
    """
    Each instruction has a name, args, and kwargs.

    An instruction can be simply a string, in which case args and kwargs are empty:

    instruction_name

    Or it can be a single-element dict with a list under it, in which case kwargs is empty:

    instruction_name:
        - arg0
        - arg1

    Or it can be a single-element dict with another dict under it. In that case,
    the args are specified by the `do` keyword:

    instruction_name:
        kwarg0: "value0"
        kwarg1: "value1"
        do:
            - arg0
            - arg1
            - arg2
    """
    if isinstance(node, collections.abc.Mapping):
        # TODO: error out if not single element dict
        name, body = list(node.items())[0]
    else:
        name = node
        body = []

    if isinstance(body, collections.abc.Mapping):
        properties = dict(body)
        elements = properties.pop("do")
    else:
        properties = {}
        elements = body

    children = [ _parse_instruction(element) for element in elements ]
    return ast.Instruction(name, args=children, kwargs=properties)

def parse(stream):
    tree = yaml.load(stream)

    return _parse_instruction({ast.ROOT: tree})
