import ast
from collections.abc import Iterator

from flake8_simplify.registry import Violation, rule
from flake8_simplify.utils import (
    body_contains_continue,
    get_next_sibling,
    get_parent,
    get_returned_bool,
    in_same_block,
    is_constant_increase,
    negate_source,
    to_source,
)


@rule("SIM104", ast.For)
def get_sim104(node: ast.For) -> Iterator[Violation]:
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
    RULE = "Use 'yield from {iterable}'"
    if (
        len(node.body) != 1
        or not isinstance(node.body[0], ast.Expr)
        or not isinstance(node.body[0].value, ast.Yield)
        or not isinstance(node.target, ast.Name)
        or not isinstance(node.body[0].value.value, ast.Name)
        or node.target.id != node.body[0].value.value.id
        or node.orelse != []
    ):
        return

    # Async generators cannot use "yield from"
    parent = get_parent(node)
    while parent is not None:
        if isinstance(parent, ast.AsyncFunctionDef):
            return
        parent = get_parent(parent)
    iterable = to_source(node.iter)
    yield Violation(node, RULE.format(iterable=iterable))


def _get_return_in_loop(node: ast.For) -> tuple[ast.If, bool] | None:
    """
    Find the "for-if-return, return" pattern that any / all could replace.

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

    Returns the if-statement and the constant it returns inside the loop.
    """
    if not (
        len(node.body) == 1
        and isinstance(node.body[0], ast.If)
        and node.body[0].orelse == []
        and node.orelse == []
    ):
        return None
    returned_in_loop = get_returned_bool(node.body[0].body)

    # The loop must be followed by returning the opposite constant
    after_loop = get_next_sibling(node)
    if not (
        isinstance(after_loop, ast.Return) and in_same_block(node, after_loop)
    ):
        return None
    returned_after_loop = get_returned_bool([after_loop])

    if (
        returned_in_loop is None
        or returned_after_loop is None
        or returned_in_loop == returned_after_loop
    ):
        return None
    return node.body[0], returned_in_loop


@rule("SIM110", ast.For)
def get_sim110(node: ast.For) -> Iterator[Violation]:
    """Check if any(...) could be used."""
    SIM110 = "Use 'return any({check} for {target} in {iterable})'"
    match = _get_return_in_loop(node)
    if match is None or match[1] is not True:
        return
    check = to_source(match[0].test)
    target = to_source(node.target)
    iterable = to_source(node.iter)
    yield Violation(
        node, SIM110.format(check=check, target=target, iterable=iterable)
    )


@rule("SIM111", ast.For)
def get_sim111(node: ast.For) -> Iterator[Violation]:
    """Check if all(...) could be used."""
    SIM111 = "Use 'return all({check} for {target} in {iterable})'"
    match = _get_return_in_loop(node)
    if match is None or match[1] is not False:
        return
    check = negate_source(match[0].test)
    target = to_source(node.target)
    iterable = to_source(node.iter)
    yield Violation(
        node, SIM111.format(check=check, target=target, iterable=iterable)
    )


@rule("SIM113", ast.For)
def get_sim113(node: ast.For) -> Iterator[Violation]:
    """
    Find loops in which "enumerate" should be used.

        For(
            target=Name(id='el', ctx=Store()),
            iter=Name(id='iterable', ctx=Load()),
            body=[
                Expr(
                    value=Constant(value=Ellipsis, kind=None),
                ),
                AugAssign( -- argument and assign, aka "+= 1"
                    target=Name(id='idx', ctx=Store()),
                    op=Add(),
                    value=Constant(value=1, kind=None),
                ),
            ],
            orelse=[],
            type_comment=None,
        ),
    """
    variable_candidates = []
    if body_contains_continue(node.body):
        return

    # Find variables that might just count the iteration of the current loop
    for expression in node.body:
        if (
            isinstance(expression, ast.AugAssign)
            and is_constant_increase(expression)
            and isinstance(expression.target, ast.Name)
        ):
            variable_candidates.append(expression.target)
    str_candidates = [to_source(x) for x in variable_candidates]

    older_siblings = []
    for older_sibling in getattr(get_parent(node), "body", []):
        if older_sibling is node:
            break
        older_siblings.append(older_sibling)

    matches = [
        n.targets[0]
        for n in older_siblings
        if isinstance(n, ast.Assign)
        and len(n.targets) == 1
        and isinstance(n.targets[0], ast.Name)
        and to_source(n.targets[0]) in str_candidates
    ]
    if len(matches) == 0:
        return

    for match in matches:
        variable = to_source(match)
        yield Violation(match, f"Use enumerate for '{variable}'")
