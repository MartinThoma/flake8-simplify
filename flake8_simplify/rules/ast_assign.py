import ast
from collections.abc import Iterator

from flake8_simplify.registry import Violation, rule
from flake8_simplify.utils import (
    expression_uses_variable,
    get_next_sibling,
    get_parent,
    to_source,
)


def _in_same_block(first: ast.stmt, second: ast.stmt) -> bool:
    """
    Check that both statements are part of the same statement list.

    Siblings are linked across the fields of a node, so the last statement of
    ``body`` has the first statement of ``orelse`` as next sibling.
    """
    parent = get_parent(first)
    if parent is None:
        return True
    for _, value in ast.iter_fields(parent):
        if isinstance(value, list) and first in value:
            return second in value
    return True


@rule("SIM904", ast.Assign)
def get_sim904(node: ast.Assign) -> Iterator[Violation]:
    """
    Assign values to dictionary directly at initialization.

    Example
    -------
    Code:
        # Bad
        a = { }
        a['b] = 'c'

        # Good
        a = {'b': 'c'}
    Bad AST:
        [
            Assign(
                targets=[Name(id='a', ctx=Store())],
                value=Dict(keys=[], values=[]),
                type_comment=None,
            ),
            Assign(
                targets=[
                    Subscript(
                        value=Name(id='a', ctx=Load()),
                        slice=Constant(value='b', kind=None),
                        ctx=Store(),
                    ),
                ],
                value=Constant(value='c', kind=None),
                type_comment=None,
            ),
        ]
    """
    RULE = "Initialize dictionary '{dict_name}' directly"
    n2 = get_next_sibling(node)
    if not (
        isinstance(node.value, ast.Dict)
        and isinstance(n2, ast.Assign)
        and len(n2.targets) == 1
        and len(node.targets) == 1
        and isinstance(n2.targets[0], ast.Subscript)
        and isinstance(n2.targets[0].value, ast.Name)
        and isinstance(node.targets[0], ast.Name)
        and n2.targets[0].value.id == node.targets[0].id
        and _in_same_block(node, n2)
    ):
        return

    dict_name = to_source(node.targets[0])
    # Capture cases where the assigned value uses another dictionary value
    if expression_uses_variable(n2.value, dict_name):
        return

    yield Violation(node, RULE.format(dict_name=dict_name))


@rule("SIM909", ast.Assign)
def get_sim909(node: ast.Assign) -> Iterator[Violation]:
    """
    Avoid reflexive assignments

    Example
    -------
    Code:
        # Bad
        foo = foo

        # Good: Just remove them
    Bad AST:
        [
            Assign(
                targets=[Name(id='foo', ctx=Store())],
                value=Name(id='foo', ctx=Load()),
                type_comment=None,
            ),
        ]
    """
    RULE = "Remove reflexive assignment '{code}'"

    names = []
    if isinstance(node.value, (ast.Name, ast.Subscript, ast.Tuple)):
        names.append(to_source(node.value))
    for target in node.targets:
        names.append(to_source(target))

    if len(names) == len(set(names)):
        return

    if isinstance(get_parent(node), ast.ClassDef):
        return

    code = to_source(node)

    yield Violation(node, RULE.format(code=code))
