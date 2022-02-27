# Core Library
import ast
from typing import List, Tuple

# First party
from flake8_simplify.constants import AST_CONST_TYPES
from flake8_simplify.utils import to_source


def get_sim118(node: ast.Compare) -> List[Tuple[int, int, str]]:
    """
    Get a list of all usages of "key in dict.keys()"

    Compare(left=Name(id='key', ctx=Load()),
            ops=[In()],
            comparators=[
                Call(
                    func=Attribute(
                        value=Name(id='dict', ctx=Load()),
                        attr='keys',
                        ctx=Load(),
                    ),
                    args=[],
                    keywords=[],
                ),
            ],
        )
    """
    RULE = "SIM118 Use '{el} in {dict}' instead of '{el} in {dict}.keys()'"
    errors: List[Tuple[int, int, str]] = []
    if not (
        len(node.ops) == 1
        and isinstance(node.ops[0], ast.In)
        and len(node.comparators) == 1
    ):
        return errors
    call_node = node.comparators[0]
    if not isinstance(call_node, ast.Call):
        return errors

    attr_node = call_node.func
    if not (
        isinstance(call_node.func, ast.Attribute)
        and call_node.func.attr == "keys"
        and isinstance(call_node.func.ctx, ast.Load)
    ):
        return errors
    assert isinstance(attr_node, ast.Attribute), "hint for mypy"  # noqa

    key_str = to_source(node.left)
    dict_str = to_source(attr_node.value)
    errors.append(
        (
            node.lineno,
            node.col_offset,
            RULE.format(el=key_str, dict=dict_str),
        )
    )
    return errors


def get_sim300(node: ast.Compare) -> List[Tuple[int, int, str]]:
    """
    Get a list of all Yoda conditions.

    Compare(
                left=Constant(value='Yoda', kind=None),
                ops=[Eq()],
                comparators=[Name(id='i_am', ctx=Load())],
            )
    """

    RULE = (
        "SIM300 Use '{right} == {left}' instead of "
        "'{left} == {right}' (Yoda-conditions)"
    )
    errors: List[Tuple[int, int, str]] = []
    if not (
        isinstance(node.left, AST_CONST_TYPES)
        and len(node.ops) == 1
        and isinstance(node.ops[0], ast.Eq)
    ):
        return errors

    left = to_source(node.left)
    right = to_source(node.comparators[0])
    errors.append(
        (node.lineno, node.col_offset, RULE.format(left=left, right=right))
    )
    return errors
