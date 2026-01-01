import ast

from flake8_simplify.constants import BOOL_CONST_TYPES
from flake8_simplify.utils import to_source


def get_sim907(node: ast.Subscript) -> list[tuple[int, int, str]]:
    """

    Subscript(
        value=Name(id='Union', ctx=Load()),
        slice=Tuple(
            elts=[
                Name(id='int', ctx=Load()),
                Name(id='str', ctx=Load()),
                Constant(value=None, kind=None),
            ],
            ...
        )
    )
    """
    errors: list[tuple[int, int, str]] = []

    if not (isinstance(node.value, ast.Name) and node.value.id == "Union"):
        return errors

    if isinstance(node.slice, ast.Tuple):
        # Python 3.9+, before it was node.slice.value
        tuple_var = node.slice
    else:
        return errors

    has_none = False
    others = []
    for elt in tuple_var.elts:  # type: ignore
        if isinstance(elt, BOOL_CONST_TYPES) and elt.value is None:
            has_none = True
        else:
            others.append(elt)

    RULE = "SIM907 Use 'Optional[{type_}]' instead of '{original}'"
    if len(others) == 1 and has_none:
        type_ = to_source(others[0])
        errors.append(
            (
                node.lineno,
                node.col_offset,
                RULE.format(type_=type_, original=to_source(node)),
            )
        )
    return errors
