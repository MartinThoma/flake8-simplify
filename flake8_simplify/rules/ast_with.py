# Core Library
import ast
from typing import List, Tuple

# First party
from flake8_simplify.utils import to_source


def get_sim117(node: ast.With) -> List[Tuple[int, int, str]]:
    """
    Find multiple with-statements with same scope.

        With(
            items=[
                withitem(
                    context_expr=Call(
                        func=Name(id='A', ctx=Load()),
                        args=[],
                        keywords=[],
                    ),
                    optional_vars=Name(id='a', ctx=Store()),
                ),
            ],
            body=[
                With(
                    items=[
                        withitem(
                            context_expr=Call(
                                func=Name(id='B', ctx=Load()),
                                args=[],
                                keywords=[],
                            ),
                            optional_vars=Name(id='b', ctx=Store()),
                        ),
                    ],
                    body=[
                        Expr(
                            value=Call(
                                func=Name(id='print', ctx=Load()),
                                args=[Constant(value='hello', kind=None)],
                                keywords=[],
                            ),
                        ),
                    ],
                    type_comment=None,
                ),
            ],
            type_comment=None,
        ),
    """
    SIM117 = "SIM117 Use '{merged_with}' instead of multiple with statements"
    errors: List[Tuple[int, int, str]] = []
    if not (len(node.body) == 1 and isinstance(node.body[0], ast.With)):
        return errors
    with_items = []
    for withitem in node.items + node.body[0].items:
        with_items.append(f"{to_source(withitem)}")
    merged_with = f"with {', '.join(with_items)}:"
    errors.append(
        (node.lineno, node.col_offset, SIM117.format(merged_with=merged_with))
    )
    return errors
