import ast
from collections.abc import Iterator

from flake8_simplify.registry import Violation, rule
from flake8_simplify.utils import to_source


def _is_os_environ(node: ast.expr) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "os"
        and node.attr == "environ"
    )


@rule("SIM112", ast.Expr)
def get_sim112(node: ast.Expr) -> Iterator[Violation]:
    """
    Find non-capitalized calls to environment variables.

    os.environ["foo"]
        Expr(
            value=Subscript(
                value=Attribute(
                    value=Name(id='os', ctx=Load()),
                    attr='environ',
                    ctx=Load(),
                ),
                slice=Constant(value='foo', kind=None),
                ctx=Load(),
            ),
        ),
    """
    RULE = "Use '{expected}' instead of '{original}'"
    value = node.value

    if (
        isinstance(value, ast.Subscript)
        and _is_os_environ(value.value)
        and isinstance(value.slice, ast.Constant)
    ):
        env_name = to_source(value.slice)
        expected = f"os.environ[{env_name.upper()}]"
    elif (
        isinstance(value, ast.Call)
        and isinstance(value.func, ast.Attribute)
        and value.func.attr == "get"
        and _is_os_environ(value.func.value)
        and len(value.args) in [1, 2]
        and isinstance(value.args[0], ast.Constant)
    ):
        env_name = to_source(value.args[0])
        arguments = [env_name.upper()]
        arguments += [to_source(arg) for arg in value.args[1:]]
        expected = f"os.environ.get({', '.join(arguments)})"
    else:
        return

    if env_name == env_name.upper():
        return
    yield Violation(
        node, RULE.format(original=to_source(node), expected=expected)
    )
