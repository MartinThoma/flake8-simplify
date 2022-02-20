# Core Library
import ast
from typing import List, Tuple

# First party
from flake8_simplify.utils import expression_uses_variable, to_source

SIM904 = "SIM904 Initialize dictionary '{dict_name}' directly"


def _get_sim904(node: ast.Assign) -> List[Tuple[int, int, str]]:
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
    errors: List[Tuple[int, int, str]] = []
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
            SIM904.format(dict_name=dict_name),
        )
    )
    return errors
