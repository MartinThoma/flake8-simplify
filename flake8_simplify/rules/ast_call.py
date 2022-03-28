# Core Library
import ast
import json
import logging
from typing import List, Tuple

# First party
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


def get_sim902(node: Call) -> List[Tuple[int, int, str]]:
    """Find bare boolean function arguments."""
    SIM902 = (
        "SIM902 Use keyword-argument instead of magic boolean for '{func}'"
    )
    errors: List[Tuple[int, int, str]] = []

    if isinstance(node.func, ast.Attribute):
        call_name = node.func.attr
    elif isinstance(node.func, ast.Name):
        call_name = node.func.id
    else:
        logger.debug(f"Unknown call type: {type(node.func)}")
        return errors

    nb_args = len(node.args)

    if call_name in ["partial", "min", "max"] or call_name.startswith("_"):
        return errors

    has_bare_bool = any(
        isinstance(call_arg, (ast.Constant, ast.NameConstant))
        and (call_arg.value is True or call_arg.value is False)
        for call_arg in node.args
    )

    is_setter = call_name.lower().startswith("set") and nb_args <= 2
    is_exception = isinstance(node.func, ast.Attribute) and node.func.attr in [
        "get"
    ]
    if has_bare_bool and not (is_exception or is_setter):
        source = to_source(node)
        errors.append(
            (node.lineno, node.col_offset, SIM902.format(func=source))
        )
    return errors


def get_sim903(node: Call) -> List[Tuple[int, int, str]]:
    """Find bare numeric function arguments."""
    SIM903 = "SIM903 Use keyword-argument instead of magic number for '{func}'"
    acceptable_magic_numbers = (0, 1, 2)
    errors: List[Tuple[int, int, str]] = []

    if isinstance(node.func, ast.Attribute):
        call_name = node.func.attr
    elif isinstance(node.func, ast.Name):
        call_name = node.func.id
    else:
        logger.debug(f"Unknown call type: {type(node.func)}")
        return errors

    nb_args = len(node.args)
    if nb_args <= 1 or call_name.startswith("_"):
        return errors

    functions_any_arg = ["partial", "min", "max", "minimum", "maximum"]
    functions_1_arg = ["sqrt", "sleep", "hideColumn"]
    functions_2_args = [
        "arange",
        "uniform",
        "zeros",
        "percentile",
        "setColumnWidth",
        "float_power",
        "power",
        "pow",
        "float_power",
        "binomial",
    ]
    if any(
        (
            call_name in functions_any_arg,
            call_name in functions_1_arg and nb_args == 1,
            call_name in functions_2_args and nb_args == 2,
            call_name in ["linspace"] and nb_args == 3,
            "color" in call_name.lower() and nb_args in [3, 4],
            "point" in call_name.lower() and nb_args in [2, 3],
        )
    ):
        return errors

    has_bare_int = any(
        isinstance(call_arg, ast.Num)
        and call_arg.n not in acceptable_magic_numbers
        for call_arg in node.args
    )

    is_setter = call_name.lower().startswith("set") and nb_args <= 2
    is_exception = isinstance(node.func, ast.Name) and node.func.id == "range"
    is_exception = is_exception or (
        isinstance(node.func, ast.Attribute)
        and node.func.attr
        in [
            "get",
            "insert",
        ]
    )
    if has_bare_int and not (is_exception or is_setter):
        source = to_source(node)
        errors.append(
            (node.lineno, node.col_offset, SIM903.format(func=source))
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
                    f"Unexpexted os.path.join arg: {arg} -- {to_source(arg)}"
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
