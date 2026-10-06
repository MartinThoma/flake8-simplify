import ast
from collections.abc import Iterator

from flake8_simplify.registry import Violation, rule
from flake8_simplify.utils import is_same_expression, to_source


@rule("SIM210", ast.IfExp)
def get_sim210(node: ast.IfExp) -> Iterator[Violation]:
    """Get a list of all calls of the type "True if a else False"."""
    SIM210 = "Use 'bool({cond})' instead of 'True if {cond} else False'"
    if (
        not isinstance(node.body, ast.Constant)
        or node.body.value is not True
        or not isinstance(node.orelse, ast.Constant)
        or node.orelse.value is not False
    ):
        return
    cond = to_source(node.test)
    yield Violation(node, SIM210.format(cond=cond))


@rule("SIM211", ast.IfExp)
def get_sim211(node: ast.IfExp) -> Iterator[Violation]:
    """Get a list of all calls of the type "False if a else True"."""
    SIM211 = "Use 'not {cond}' instead of 'False if {cond} else True'"
    if (
        not isinstance(node.body, ast.Constant)
        or node.body.value is not False
        or not isinstance(node.orelse, ast.Constant)
        or node.orelse.value is not True
    ):
        return
    cond = to_source(node.test)
    yield Violation(node, SIM211.format(cond=cond))


@rule("SIM212", ast.IfExp)
def get_sim212(node: ast.IfExp) -> Iterator[Violation]:
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
    SIM212 = "Use '{a} if {a} else {b}' instead of '{b} if not {a} else {a}'"
    if not (
        isinstance(node.test, ast.UnaryOp)
        and isinstance(node.test.op, ast.Not)
        and is_same_expression(node.test.operand, node.orelse)
    ):
        return
    a = to_source(node.test.operand)
    b = to_source(node.body)
    yield Violation(node, SIM212.format(a=a, b=b))
