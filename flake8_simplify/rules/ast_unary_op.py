import ast
from collections.abc import Iterator

from flake8_simplify.registry import Violation, rule
from flake8_simplify.utils import get_parent, is_exception_check, to_source


def is_exception_check_parent(node: ast.UnaryOp) -> bool:
    """Check if the node is the condition of ``if ...: raise``."""
    parent = get_parent(node)
    return isinstance(parent, ast.If) and is_exception_check(parent)


@rule("SIM201", ast.UnaryOp)
def get_sim201(node: ast.UnaryOp) -> Iterator[Violation]:
    """
    Get a list of all calls where an unary 'not' is used for an equality.
    """
    SIM201 = "Use '{left} != {right}' instead of 'not {left} == {right}'"
    if (
        not isinstance(node.op, ast.Not)
        or not isinstance(node.operand, ast.Compare)
        or len(node.operand.ops) != 1
        or not isinstance(node.operand.ops[0], ast.Eq)
    ) or is_exception_check_parent(node):
        return
    comparison = node.operand
    left = to_source(comparison.left)
    right = to_source(comparison.comparators[0])
    yield Violation(node, SIM201.format(left=left, right=right))


@rule("SIM202", ast.UnaryOp)
def get_sim202(node: ast.UnaryOp) -> Iterator[Violation]:
    """
    Get a list of all calls where an unary 'not' is used for an quality.
    """
    SIM202 = "Use '{left} == {right}' instead of 'not {left} != {right}'"
    if (
        not isinstance(node.op, ast.Not)
        or not isinstance(node.operand, ast.Compare)
        or len(node.operand.ops) != 1
        or not isinstance(node.operand.ops[0], ast.NotEq)
    ) or is_exception_check_parent(node):
        return
    comparison = node.operand
    left = to_source(comparison.left)
    right = to_source(comparison.comparators[0])
    yield Violation(node, SIM202.format(left=left, right=right))


@rule("SIM203", ast.UnaryOp)
def get_sim203(node: ast.UnaryOp) -> Iterator[Violation]:
    """
    Get a list of all calls where an unary 'not' is used for an in-check.
    """
    SIM203 = "Use '{a} not in {b}' instead of 'not {a} in {b}'"
    if (
        not isinstance(node.op, ast.Not)
        or not isinstance(node.operand, ast.Compare)
        or len(node.operand.ops) != 1
        or not isinstance(node.operand.ops[0], ast.In)
    ) or is_exception_check_parent(node):
        return
    comparison = node.operand
    left = to_source(comparison.left)
    right = to_source(comparison.comparators[0])
    yield Violation(node, SIM203.format(a=left, b=right))


@rule("SIM208", ast.UnaryOp)
def get_sim208(node: ast.UnaryOp) -> Iterator[Violation]:
    """Get a list of all calls of the type "not (not a)"."""
    SIM208 = "Use '{a}' instead of 'not (not {a})'"
    if (
        not isinstance(node.op, ast.Not)
        or not isinstance(node.operand, ast.UnaryOp)
        or not isinstance(node.operand.op, ast.Not)
    ):
        return
    a = to_source(node.operand.operand)
    yield Violation(node, SIM208.format(a=a))
