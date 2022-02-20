# Core Library
import ast
from typing import List, Tuple

# First party
from flake8_simplify.constants import BOOL_CONST_TYPES
from flake8_simplify.utils import (
    body_contains_continue,
    is_constant_increase,
    to_source,
)

SIM104 = "SIM104 Use 'yield from {iterable}'"
SIM110 = "SIM110 Use 'return any({check} for {target} in {iterable})'"
SIM111 = "SIM111 Use 'return all({check} for {target} in {iterable})'"
SIM113 = "SIM113 Use enumerate instead of '{variable}'"


def get_sim104(node: ast.For) -> List[Tuple[int, int, str]]:
    """
    Get a list of all "iterate and yield" patterns.

    for item in iterable:
        yield item

    which is

        For(
            target=Name(id='item', ctx=Store()),
            iter=Name(id='iterable', ctx=Load()),
            body=[
                Expr(
                    value=Yield(
                        value=Name(id='item', ctx=Load()),
                    ),
                ),
            ],
            orelse=[],
            type_comment=None,
        ),

    """
    errors: List[Tuple[int, int, str]] = []
    if (
        len(node.body) != 1
        or not isinstance(node.body[0], ast.Expr)
        or not isinstance(node.body[0].value, ast.Yield)
        or not isinstance(node.target, ast.Name)
        or not isinstance(node.body[0].value.value, ast.Name)
        or node.target.id != node.body[0].value.value.id
        or node.orelse != []
    ):
        return errors
    if isinstance(node.parent, ast.AsyncFunctionDef):  # type: ignore
        return errors
    iterable = to_source(node.iter)
    errors.append(
        (node.lineno, node.col_offset, SIM104.format(iterable=iterable))
    )
    return errors


def get_sim110_sim111(node: ast.For) -> List[Tuple[int, int, str]]:
    """
    Check if any / all could be used.

    For(
        target=Name(id='x', ctx=Store()),
        iter=Name(id='iterable', ctx=Load()),
        body=[
            If(
                test=Call(
                    func=Name(id='check', ctx=Load()),
                    args=[Name(id='x', ctx=Load())],
                    keywords=[],
                ),
                body=[
                    Return(
                        value=Constant(value=True, kind=None),
                    ),
                ],
                orelse=[],
            ),
        ],
        orelse=[],
        type_comment=None,
    ),
    Return(value=Constant(value=False, kind=None))
    """
    errors: List[Tuple[int, int, str]] = []
    if not (
        len(node.body) == 1
        and isinstance(node.body[0], ast.If)
        and len(node.body[0].body) == 1
        and isinstance(node.body[0].body[0], ast.Return)
        and isinstance(node.body[0].body[0].value, BOOL_CONST_TYPES)
    ):
        return errors
    if not hasattr(node.body[0].body[0].value, "value"):
        return errors
    if isinstance(node.next_sibling, ast.Raise):  # type: ignore
        return errors
    check = to_source(node.body[0].test)
    target = to_source(node.target)
    iterable = to_source(node.iter)
    if node.body[0].body[0].value.value is True:
        errors.append(
            (
                node.lineno,
                node.col_offset,
                SIM110.format(check=check, target=target, iterable=iterable),
            )
        )
    elif node.body[0].body[0].value.value is False:
        is_compound_expression = " and " in check or " or " in check

        if is_compound_expression:
            check = f"not ({check})"
        else:
            if check.startswith("not "):
                check = check[len("not ") :]
            else:
                check = f"not {check}"
        errors.append(
            (
                node.lineno,
                node.col_offset,
                SIM111.format(check=check, target=target, iterable=iterable),
            )
        )
    return errors


def get_sim113(node: ast.For) -> List[Tuple[int, int, str]]:
    """
    Find loops in which "enumerate" should be used.

        For(
            target=Name(id='el', ctx=Store()),
            iter=Name(id='iterable', ctx=Load()),
            body=[
                Expr(
                    value=Constant(value=Ellipsis, kind=None),
                ),
                AugAssign(
                    target=Name(id='idx', ctx=Store()),
                    op=Add(),
                    value=Constant(value=1, kind=None),
                ),
            ],
            orelse=[],
            type_comment=None,
        ),
    """
    errors: List[Tuple[int, int, str]] = []
    variable_candidates = []
    if body_contains_continue(node.body):
        return errors
    for expression in node.body:
        if (
            isinstance(expression, ast.AugAssign)
            and is_constant_increase(expression)
            and isinstance(expression.target, ast.Name)
        ):
            variable_candidates.append(expression.target)

    for candidate in variable_candidates:
        errors.append(
            (
                candidate.lineno,
                candidate.col_offset,
                SIM113.format(variable=to_source(candidate)),
            )
        )
    return errors
