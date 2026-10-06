import ast

from flake8_simplify.utils import Assign, expression_uses_variable, to_source


def _in_same_block(first: ast.stmt, second: ast.stmt) -> bool:
    """
    Check that both statements are part of the same statement list.

    Siblings are linked across the fields of a node, so the last statement of
    ``body`` has the first statement of ``orelse`` as next sibling.
    """
    parent = getattr(first, "parent", None)
    if parent is None:
        return True
    for _, value in ast.iter_fields(parent):
        if isinstance(value, list) and first in value:
            return second in value
    return True


def get_sim904(node: ast.Assign) -> list[tuple[int, int, str]]:
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
    RULE = "SIM904 Initialize dictionary '{dict_name}' directly"
    errors: list[tuple[int, int, str]] = []
    n2 = node.next_sibling  # type: ignore
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
        return errors

    dict_name = to_source(node.targets[0])
    # Capture cases where the assigned value uses another dictionary value
    if expression_uses_variable(n2.value, dict_name):
        return errors

    errors.append(
        (
            node.lineno,
            node.col_offset,
            RULE.format(dict_name=dict_name),
        )
    )
    return errors


def get_sim909(node: Assign) -> list[tuple[int, int, str]]:
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
    RULE = "SIM909 Remove reflexive assignment '{code}'"
    errors: list[tuple[int, int, str]] = []

    names = []
    if isinstance(node.value, (ast.Name, ast.Subscript, ast.Tuple)):
        names.append(to_source(node.value))
    for target in node.targets:
        names.append(to_source(target))

    if len(names) == len(set(names)):
        return errors

    if isinstance(node.parent, ast.ClassDef):
        return errors

    code = to_source(node.orig)

    errors.append(
        (
            node.lineno,
            node.col_offset,
            RULE.format(code=code),
        )
    )
    return errors
