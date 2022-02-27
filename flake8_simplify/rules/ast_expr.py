# Core Library
import ast
from typing import List, Tuple

# First party
from flake8_simplify.constants import STR_TYPES
from flake8_simplify.utils import to_source


def get_sim112(node: ast.Expr) -> List[Tuple[int, int, str]]:
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
                slice=Index(
                    value=Constant(value='foo', kind=None),
                ),
                ctx=Load(),
            ),
        ),
    """
    RULE = "SIM112 Use '{expected}' instead of '{original}'"
    errors: List[Tuple[int, int, str]] = []

    is_index_call = (
        isinstance(node.value, ast.Subscript)
        and isinstance(node.value.value, ast.Attribute)
        and isinstance(node.value.value.value, ast.Name)
        and node.value.value.value.id == "os"
        and node.value.value.attr == "environ"
        and (
            (
                isinstance(node.value.slice, ast.Index)
                and isinstance(node.value.slice.value, STR_TYPES)  # type: ignore  # noqa
            )
            or isinstance(node.value.slice, ast.Constant)
        )
    )
    if is_index_call:
        subscript = node.value
        assert isinstance(subscript, ast.Subscript), "hint for mypy"  # noqa
        slice_ = subscript.slice
        if isinstance(slice_, ast.Index):
            # Python < 3.9
            string_part = slice_.value  # type: ignore
            assert isinstance(string_part, STR_TYPES), "hint for mypy"  # noqa
            env_name = to_source(string_part)
        elif isinstance(slice_, ast.Constant):
            # Python 3.9
            env_name = to_source(slice_)

        # Check if this has a change
        has_change = env_name != env_name.upper()

    is_get_call = (
        isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Attribute)
        and isinstance(node.value.func.value, ast.Attribute)
        and isinstance(node.value.func.value.value, ast.Name)
        and node.value.func.value.value.id == "os"
        and node.value.func.value.attr == "environ"
        and node.value.func.attr == "get"
        and len(node.value.args) in [1, 2]
        and isinstance(node.value.args[0], STR_TYPES)
    )
    if is_get_call:
        call = node.value
        assert isinstance(call, ast.Call), "hint for mypy"  # noqa
        string_part = call.args[0]
        assert isinstance(string_part, STR_TYPES), "hint for mypy"  # noqa
        env_name = to_source(string_part)
        # Check if this has a change
        has_change = env_name != env_name.upper()
    if not (is_index_call or is_get_call) or not has_change:
        return errors
    if is_index_call:
        original = to_source(node)
        expected = f"os.environ[{env_name.upper()}]"
    elif is_get_call:
        original = to_source(node)
        if len(node.value.args) == 1:  # type: ignore
            expected = f"os.environ.get({env_name.upper()})"
        else:
            assert isinstance(node.value, ast.Call), "hint for mypy"  # noqa
            default_value = to_source(node.value.args[1])
            expected = f"os.environ.get({env_name.upper()}, {default_value})"
    else:
        return errors
    errors.append(
        (
            node.lineno,
            node.col_offset,
            RULE.format(original=original, expected=expected),
        )
    )
    return errors
