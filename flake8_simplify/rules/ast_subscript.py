import ast
from collections.abc import Iterator

from flake8_simplify.constants import BOOL_CONST_TYPES
from flake8_simplify.registry import Violation, rule
from flake8_simplify.utils import to_source


@rule("SIM907", ast.Subscript)
def get_sim907(node: ast.Subscript) -> Iterator[Violation]:
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

    if not (isinstance(node.value, ast.Name) and node.value.id == "Union"):
        return

    if isinstance(node.slice, ast.Tuple):
        # Python 3.9+, before it was node.slice.value
        tuple_var = node.slice
    else:
        return

    has_none = False
    others = []
    for elt in tuple_var.elts:  # type: ignore
        if isinstance(elt, BOOL_CONST_TYPES) and elt.value is None:
            has_none = True
        else:
            others.append(elt)

    RULE = "Use 'Optional[{type_}]' instead of '{original}'"
    if len(others) == 1 and has_none:
        type_ = to_source(others[0])
        yield Violation(
            node, RULE.format(type_=type_, original=to_source(node))
        )
