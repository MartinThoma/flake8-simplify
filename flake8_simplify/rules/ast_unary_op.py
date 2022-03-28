# Core Library
import ast
from typing import List, Tuple

# First party
from flake8_simplify.utils import UnaryOp, is_exception_check, to_source


def get_sim201(node: UnaryOp) -> List[Tuple[int, int, str]]:
    """
    Get a list of all calls where an unary 'not' is used for an equality.
    """
    SIM201 = (
        "SIM201 Use '{left} != {right}' instead of 'not {left} == {right}'"
    )
    errors: List[Tuple[int, int, str]] = []
    if (
        (
            not isinstance(node.op, ast.Not)
            or not isinstance(node.operand, ast.Compare)
            or len(node.operand.ops) != 1
            or not isinstance(node.operand.ops[0], ast.Eq)
        )
        or isinstance(node.parent, ast.If)
        and is_exception_check(node.parent)
    ):
        return errors
    comparison = node.operand
    left = to_source(comparison.left)
    right = to_source(comparison.comparators[0])
    errors.append(
        (node.lineno, node.col_offset, SIM201.format(left=left, right=right))
    )

    return errors


def get_sim202(node: UnaryOp) -> List[Tuple[int, int, str]]:
    """
    Get a list of all calls where an unary 'not' is used for an quality.
    """
    SIM202 = (
        "SIM202 Use '{left} == {right}' instead of 'not {left} != {right}'"
    )
    errors: List[Tuple[int, int, str]] = []
    if (
        (
            not isinstance(node.op, ast.Not)
            or not isinstance(node.operand, ast.Compare)
            or len(node.operand.ops) != 1
            or not isinstance(node.operand.ops[0], ast.NotEq)
        )
        or isinstance(node.parent, ast.If)
        and is_exception_check(node.parent)
    ):
        return errors
    comparison = node.operand
    left = to_source(comparison.left)
    right = to_source(comparison.comparators[0])
    errors.append(
        (node.lineno, node.col_offset, SIM202.format(left=left, right=right))
    )

    return errors


def get_sim203(node: UnaryOp) -> List[Tuple[int, int, str]]:
    """
    Get a list of all calls where an unary 'not' is used for an in-check.
    """
    SIM203 = "SIM203 Use '{a} not in {b}' instead of 'not {a} in {b}'"
    errors: List[Tuple[int, int, str]] = []
    if (
        (
            not isinstance(node.op, ast.Not)
            or not isinstance(node.operand, ast.Compare)
            or len(node.operand.ops) != 1
            or not isinstance(node.operand.ops[0], ast.In)
        )
        or isinstance(node.parent, ast.If)
        and is_exception_check(node.parent)
    ):
        return errors
    comparison = node.operand
    left = to_source(comparison.left)
    right = to_source(comparison.comparators[0])
    errors.append(
        (node.lineno, node.col_offset, SIM203.format(a=left, b=right))
    )

    return errors


def get_sim208(node: ast.UnaryOp) -> List[Tuple[int, int, str]]:
    """Get a list of all calls of the type "not (not a)"."""
    SIM208 = "SIM208 Use '{a}' instead of 'not (not {a})'"
    errors: List[Tuple[int, int, str]] = []
    if (
        not isinstance(node.op, ast.Not)
        or not isinstance(node.operand, ast.UnaryOp)
        or not isinstance(node.operand.op, ast.Not)
    ):
        return errors
    a = to_source(node.operand.operand)
    errors.append((node.lineno, node.col_offset, SIM208.format(a=a)))
    return errors
