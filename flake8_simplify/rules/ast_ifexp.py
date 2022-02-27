# Core Library
import ast
from typing import List, Tuple

# First party
from flake8_simplify.constants import BOOL_CONST_TYPES
from flake8_simplify.utils import is_same_expression, to_source


def get_sim210(node: ast.IfExp) -> List[Tuple[int, int, str]]:
    """Get a list of all calls of the type "True if a else False"."""
    SIM210 = "SIM210 Use 'bool({cond})' instead of 'True if {cond} else False'"
    errors: List[Tuple[int, int, str]] = []
    if (
        not isinstance(node.body, BOOL_CONST_TYPES)
        or node.body.value is not True
        or not isinstance(node.orelse, BOOL_CONST_TYPES)
        or node.orelse.value is not False
    ):
        return errors
    cond = to_source(node.test)
    errors.append((node.lineno, node.col_offset, SIM210.format(cond=cond)))
    return errors


def get_sim211(node: ast.IfExp) -> List[Tuple[int, int, str]]:
    """Get a list of all calls of the type "False if a else True"."""
    SIM211 = "SIM211 Use 'not {cond}' instead of 'False if {cond} else True'"
    errors: List[Tuple[int, int, str]] = []
    if (
        not isinstance(node.body, BOOL_CONST_TYPES)
        or node.body.value is not False
        or not isinstance(node.orelse, BOOL_CONST_TYPES)
        or node.orelse.value is not True
    ):
        return errors
    cond = to_source(node.test)
    errors.append((node.lineno, node.col_offset, SIM211.format(cond=cond)))
    return errors


def get_sim212(node: ast.IfExp) -> List[Tuple[int, int, str]]:
    """
    Get a list of all calls of the type "b if not a else a".

    IfExp(
        test=UnaryOp(
            op=Not(),
            operand=Name(id='a', ctx=Load()),
        ),
        body=Name(id='b', ctx=Load()),
        orelse=Name(id='a', ctx=Load()),
    )
    """
    SIM212 = (
        "SIM212 Use '{a} if {a} else {b}' instead of '{b} if not {a} else {a}'"
    )
    errors: List[Tuple[int, int, str]] = []
    if not (
        isinstance(node.test, ast.UnaryOp)
        and isinstance(node.test.op, ast.Not)
        and is_same_expression(node.test.operand, node.orelse)
    ):
        return errors
    a = to_source(node.test.operand)
    b = to_source(node.body)
    errors.append((node.lineno, node.col_offset, SIM212.format(a=a, b=b)))
    return errors
