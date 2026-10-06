import ast
from collections.abc import Iterable, Iterator

from flake8_simplify.registry import Violation, rule
from flake8_simplify.utils import to_source


@rule("SIM105", ast.Try)
def get_sim105(node: ast.Try) -> Iterator[Violation]:
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
    SIM105 = "Use 'contextlib.suppress({exception})'"
    if (
        len(node.body) != 1
        or len(node.handlers) != 1
        or not isinstance(node.handlers[0], ast.ExceptHandler)
        or len(node.handlers[0].body) != 1
        or not isinstance(node.handlers[0].body[0], ast.Pass)
        or node.orelse != []
        or node.finalbody != []
    ):
        return
    if node.handlers[0].type is None:
        exception = "Exception"
    else:
        exception = to_source(node.handlers[0].type)
    yield Violation(node, SIM105.format(exception=exception))


def _find_return(nodes: Iterable[ast.AST]) -> ast.Return | None:
    """
    Find the first return statement in source order.

    Nested functions and classes are skipped, as their returns belong to them.
    """
    for node in nodes:
        if isinstance(node, ast.Return):
            return node
        if isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        ):
            continue
        found = _find_return(ast.iter_child_nodes(node))
        if found is not None:
            return found
    return None


@rule("SIM107", ast.Try)
def get_sim107(node: ast.Try) -> Iterator[Violation]:
    """
    Get a list of all calls where try/except and finally have 'return'.

    The return in finally silently replaces the other return values and
    swallows exceptions.
    """
    SIM107 = "Don't use return in try/except and finally"
    finally_return = _find_return(node.finalbody)
    if finally_return is None:
        return
    if _find_return([*node.body, *node.handlers, *node.orelse]) is None:
        return
    yield Violation(finally_return, SIM107)
