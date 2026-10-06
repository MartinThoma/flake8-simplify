import ast
import json
from collections.abc import Iterator

from flake8_simplify.registry import Violation, rule
from flake8_simplify.utils import get_parent, to_source


@rule("SIM115", ast.Call)
def get_sim115(node: ast.Call) -> Iterator[Violation]:
    """
    Find places where open() is called without a context handler.

    Example AST
    -----------
        Assign(
            targets=[Name(id='f', ctx=Store())],
            value=Call(
                func=Name(id='open', ctx=Load()),
                args=[Constant(value=Ellipsis, kind=None)],
                keywords=[],
            ),
            type_comment=None,
        )
        ...
        Expr(
            value=Call(
                func=Attribute(
                    value=Name(id='f', ctx=Load()),
                    attr='close',
                    ctx=Load(),
                ),
                args=[],
                keywords=[],
            ),
        ),
    """
    RULE = "Use context handler for opening files"
    if not (
        isinstance(node.func, ast.Name)
        and node.func.id == "open"
        and not isinstance(get_parent(node), ast.withitem)
    ):
        return
    yield Violation(node, RULE)


# Experimental rules


@rule("SIM901", ast.Call)
def get_sim901(node: ast.Call) -> Iterator[Violation]:
    """
    Get a list of all calls of the type "bool(comparison)".

    Call(
        func=Name(id='bool', ctx=Load()),
        args=[
            Compare(
                left=Name(id='a', ctx=Load()),
                ops=[Eq()],
                comparators=[Name(id='b', ctx=Load())],
            ),
        ],
        keywords=[],
    )
    """
    RULE = "Use '{expected}' instead of '{actual}'"
    if not (
        isinstance(node.func, ast.Name)
        and node.func.id == "bool"
        and len(node.args) == 1
        and isinstance(node.args[0], ast.Compare)
    ):
        return

    actual = to_source(node)
    expected = to_source(node.args[0])

    yield Violation(node, RULE.format(actual=actual, expected=expected))


@rule("SIM905", ast.Call)
def get_sim905(node: ast.Call) -> Iterator[Violation]:
    RULE = "Use '{expected}' instead of '{actual}'"
    if not (
        isinstance(node.func, ast.Attribute)
        and node.func.attr == "split"
        and isinstance(node.func.value, ast.Constant)
        and isinstance(node.func.value.value, str)
        and not node.args
        and not node.keywords
    ):
        return

    value = node.func.value.value

    expected = json.dumps(value.split())
    actual = to_source(node.func.value) + ".split()"
    yield Violation(node, RULE.format(expected=expected, actual=actual))


@rule("SIM906", ast.Call)
def get_sim906(node: ast.Call) -> Iterator[Violation]:
    RULE = "Use '{expected}' instead of '{actual}'"
    if not (
        isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Attribute)
        and isinstance(node.func.value.value, ast.Name)
        and node.func.value.value.id == "os"
        and node.func.value.attr == "path"
        and node.func.attr == "join"
        and len(node.args) == 2
        and any(
            (
                isinstance(arg, ast.Call)
                and isinstance(arg.func, ast.Attribute)
                and isinstance(arg.func.value, ast.Attribute)
                and isinstance(arg.func.value.value, ast.Name)
                and arg.func.value.value.id == "os"
                and arg.func.value.attr == "path"
                and arg.func.attr == "join"
            )
            for arg in node.args
        )
    ):
        return

    def get_os_path_join_args(node: ast.Call) -> list[str]:
        names: list[str] = []
        for arg in node.args:
            if (
                isinstance(arg, ast.Call)
                and isinstance(arg.func, ast.Attribute)
                and isinstance(arg.func.value, ast.Attribute)
                and isinstance(arg.func.value.value, ast.Name)
                and arg.func.value.value.id == "os"
                and arg.func.value.attr == "path"
                and arg.func.attr == "join"
            ):
                names = names + get_os_path_join_args(arg)
            elif isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                names.append(repr(arg.value))
            else:
                names.append(to_source(arg))
        return names

    names = get_os_path_join_args(node)

    actual = to_source(node)
    expected = f"os.path.join({', '.join(names)})"
    yield Violation(node, RULE.format(actual=actual, expected=expected))


@rule("SIM910", ast.Call)
def get_sim910(node: ast.Call) -> Iterator[Violation]:
    """
    Get a list of all usages of "dict.get(key, None)"

    Example AST
    -----------
        Expr(
            value=Call(
                func=Attribute(
                    value=Name(id='a_dict', ctx=Load()),
                    attr='get',
                    ctx=Load()
                ),
                args=[
                    Name(id='key', ctx=Load()),
                    Constant(value=None)
                ],
                keywords=[]
            ),
        ),
    """
    RULE = "Use '{expected}' instead of '{actual}'"
    if not (
        isinstance(node.func, ast.Attribute)
        and node.func.attr == "get"
        and isinstance(node.func.ctx, ast.Load)
    ):
        return

    # check the argument value
    if not (
        len(node.args) == 2
        and isinstance(node.args[1], ast.Constant)
        and node.args[1].value is None
    ):
        return

    actual = to_source(node)
    func = to_source(node.func)
    key = to_source(node.args[0])
    expected = f"{func}({key})"
    yield Violation(node, RULE.format(actual=actual, expected=expected))


@rule("SIM911", ast.Call)
def get_sim911(node: ast.AST) -> Iterator[Violation]:
    """
    Find nodes representing the expression "zip(_.keys(), _.values())".

    Returns a list of tuples containing the line number and column offset
    of each identified node.

    Expr(
        value=Call(
            func=Name(id='zip', ctx=Load()),
            args=[
                Call(
                    func=Attribute(
                        value=Name(id='_', ctx=Load()),
                        attr='keys',
                        ctx=Load()),
                    args=[],
                    keywords=[]),
                Call(
                    func=Attribute(
                        value=Name(id='_', ctx=Load()),
                        attr='values',
                        ctx=Load()),
                    args=[],
                    keywords=[])],
            keywords=[
                keyword(
                    arg='strict',
                    value=Constant(value=False))
                ]
            )
        )
    """
    RULE = (
        "Use '{name}.items()' instead of 'zip({name}.keys(), {name}.values())'"
    )

    if isinstance(node, ast.Call) and (
        isinstance(node.func, ast.Name)
        and node.func.id == "zip"
        and len(node.args) == 2
    ):
        first_arg, second_arg = node.args
        if (
            isinstance(first_arg, ast.Call)
            and isinstance(first_arg.func, ast.Attribute)
            and isinstance(first_arg.func.value, ast.Name)
            and first_arg.func.attr == "keys"
            and isinstance(second_arg, ast.Call)
            and isinstance(second_arg.func, ast.Attribute)
            and isinstance(second_arg.func.value, ast.Name)
            and second_arg.func.attr == "values"
            and first_arg.func.value.id == second_arg.func.value.id
        ):
            yield Violation(node, RULE.format(name=first_arg.func.value.id))
