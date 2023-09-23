# Core Library
import ast
import json
import logging
from typing import List, Tuple

# First party
from flake8_simplify.constants import BOOL_CONST_TYPES
from flake8_simplify.utils import Call, to_source

logger = logging.getLogger(__name__)


def get_sim115(node: Call) -> List[Tuple[int, int, str]]:
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
    RULE = "SIM115 Use context handler for opening files"
    errors: List[Tuple[int, int, str]] = []
    if not (
        isinstance(node.func, ast.Name)
        and node.func.id == "open"
        and not isinstance(node.parent, ast.withitem)
    ):
        return errors
    errors.append((node.lineno, node.col_offset, RULE))
    return errors


# Experimental rules


def get_sim901(node: ast.Call) -> List[Tuple[int, int, str]]:
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
    RULE = "SIM901 Use '{expected}' instead of '{actual}'"
    errors: List[Tuple[int, int, str]] = []
    if not (
        isinstance(node.func, ast.Name)
        and node.func.id == "bool"
        and len(node.args) == 1
        and isinstance(node.args[0], ast.Compare)
    ):
        return errors

    actual = to_source(node)
    expected = to_source(node.args[0])

    errors.append(
        (
            node.lineno,
            node.col_offset,
            RULE.format(actual=actual, expected=expected),
        )
    )
    return errors


def get_sim905(node: ast.Call) -> List[Tuple[int, int, str]]:
    RULE = "SIM905 Use '{expected}' instead of '{actual}'"
    errors: List[Tuple[int, int, str]] = []
    if not (
        isinstance(node.func, ast.Attribute)
        and node.func.attr == "split"
        and isinstance(node.func.value, (ast.Str, ast.Constant))
    ):
        return errors

    if isinstance(node.func.value, ast.Constant):
        value = node.func.value.value
    else:
        value = node.func.value.s

    expected = json.dumps(value.split())
    actual = to_source(node.func.value) + ".split()"
    errors.append(
        (
            node.lineno,
            node.col_offset,
            RULE.format(expected=expected, actual=actual),
        )
    )
    return errors


def get_sim906(node: ast.Call) -> List[Tuple[int, int, str]]:
    RULE = "SIM906 Use '{expected}' instead of '{actual}'"
    errors: List[Tuple[int, int, str]] = []
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
        return errors

    def get_os_path_join_args(node: ast.Call) -> List[str]:
        names: List[str] = []
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
            elif isinstance(arg, ast.Name):
                names.append(arg.id)
            elif isinstance(arg, ast.Str):
                names.append(f"'{arg.s}'")
            else:
                logger.debug(
                    f"Unexpected os.path.join arg: {arg} -- {to_source(arg)}"
                )
        return names

    names = get_os_path_join_args(node)

    actual = to_source(node)
    expected = f"os.path.join({', '.join(names)})"
    errors.append(
        (
            node.lineno,
            node.col_offset,
            RULE.format(actual=actual, expected=expected),
        )
    )
    return errors


def get_sim910(node: Call) -> List[Tuple[int, int, str]]:
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
    RULE = "SIM910 Use '{expected}' instead of '{actual}'"
    errors: List[Tuple[int, int, str]] = []
    if not (
        isinstance(node.func, ast.Attribute)
        and node.func.attr == "get"
        and isinstance(node.func.ctx, ast.Load)
    ):
        return errors

    # check the argument value
    if not (
        len(node.args) == 2
        and isinstance(node.args[1], BOOL_CONST_TYPES)
        and node.args[1].value is None
    ):
        return errors

    actual = to_source(node)
    func = to_source(node.func)
    key = to_source(node.args[0])
    expected = f"{func}({key})"
    errors.append(
        (
            node.lineno,
            node.col_offset,
            RULE.format(actual=actual, expected=expected),
        )
    )
    return errors


def get_sim911(node: ast.AST) -> List[Tuple[int, int, str]]:
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
        "SIM911 Use '{name}.items()' instead of "
        "'zip({name}.keys(), {name}.values())'"
    )
    errors: List[Tuple[int, int, str]] = []

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
            errors.append(
                (
                    node.lineno,
                    node.col_offset,
                    RULE.format(name=first_arg.func.value.id),
                )
            )
    return errors
