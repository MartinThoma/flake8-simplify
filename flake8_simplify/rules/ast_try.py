# Core Library
import ast
from typing import List, Tuple

# First party
from flake8_simplify.utils import to_source


def get_sim105(node: ast.Try) -> List[Tuple[int, int, str]]:
    """
    Get a list of all "try-except-pass" patterns.

    try:
        foo()
    except ValueError:
        pass

    which is

        Try(
            body=[
                Expr(
                    value=Call(
                        func=Name(id='foo', ctx=Load()),
                        args=[],
                        keywords=[],
                    ),
                ),
            ],
            handlers=[
                ExceptHandler(
                    type=Name(id='ValueError', ctx=Load()),
                    name=None,
                    body=[Pass()],
                ),
            ],
            orelse=[],
            finalbody=[],
        ),


    """
    SIM105 = "SIM105 Use 'contextlib.suppress({exception})'"
    errors: List[Tuple[int, int, str]] = []
    if (
        len(node.body) != 1
        or len(node.handlers) != 1
        or not isinstance(node.handlers[0], ast.ExceptHandler)
        or len(node.handlers[0].body) != 1
        or not isinstance(node.handlers[0].body[0], ast.Pass)
        or node.orelse != []
    ):
        return errors
    if node.handlers[0].type is None:
        exception = "Exception"
    else:
        exception = to_source(node.handlers[0].type)
    errors.append(
        (node.lineno, node.col_offset, SIM105.format(exception=exception))
    )
    return errors


def get_sim107(node: ast.Try) -> List[Tuple[int, int, str]]:
    """
    Get a list of all calls where try/except and finally have 'return'.
    """
    SIM107 = "SIM107 Don't use return in try/except and finally"
    errors: List[Tuple[int, int, str]] = []

    try_has_return = False
    for stmt in node.body:
        if isinstance(stmt, ast.Return):
            try_has_return = True
            break

    except_has_return = False
    for stmt2 in node.handlers:
        if isinstance(stmt2, ast.Return):
            except_has_return = True
            break

    finally_has_return = False
    finally_return = None
    for stmt in node.finalbody:
        if isinstance(stmt, ast.Return):
            finally_has_return = True
            finally_return = stmt
            break

    if (try_has_return or except_has_return) and finally_has_return:
        assert finally_return is not None, "hint for mypy"
        errors.append(
            (finally_return.lineno, finally_return.col_offset, SIM107)
        )
    return errors
