# Core Library
import ast
from typing import Any, Dict, List, Optional, Tuple

# First party
from flake8_simplify.constants import AST_CONST_TYPES, BOOL_CONST_TYPES
from flake8_simplify.utils import (
    If,
    get_if_body_pairs,
    is_body_same,
    to_source,
)


def get_sim102(node: ast.If) -> List[Tuple[int, int, str]]:
    """Get a list of all nested if-statements without else-blocks."""
    RULE = "SIM102 Use a single if-statement instead of nested if-statements"
    errors: List[Tuple[int, int, str]] = []

    # ## Pattern 1
    # if a: <---
    #     if b: <---
    #         c
    is_pattern_1 = (
        node.orelse == []
        and len(node.body) == 1
        and isinstance(node.body[0], ast.If)
        and node.body[0].orelse == []
    )
    # ## Pattern 2
    # if a: < irrelevant for here
    #     pass
    # elif b:  <--- this is treated like a nested block
    #     if c: <---
    #         d

    if not is_pattern_1:
        return errors
    is_main_check = (
        isinstance(node.test, ast.Compare)
        and isinstance(node.test.left, ast.Name)
        and node.test.left.id == "__name__"
        and len(node.test.comparators) == 1
        and isinstance(node.test.comparators[0], ast.Str)
        and node.test.comparators[0].s == "__main__"
    )
    if is_main_check:
        return errors
    errors.append((node.lineno, node.col_offset, RULE))
    return errors


def get_sim103(node: ast.If) -> List[Tuple[int, int, str]]:
    """
    Get a list of all calls that wrap a condition to return a bool.

    if cond:
        return True
    else:
        return False

    which is

        If(
            test=Name(id='cond', ctx=Load()),
            body=[
                Return(
                    value=Constant(value=True, kind=None),
                ),
            ],
            orelse=[
                Return(
                    value=Constant(value=False, kind=None),
                ),
            ],
        ),

    """
    SIM103 = "SIM103 Return the condition {cond} directly"
    errors: List[Tuple[int, int, str]] = []
    if (
        len(node.body) != 1
        or not isinstance(node.body[0], ast.Return)
        or not isinstance(node.body[0].value, BOOL_CONST_TYPES)
        or not (
            node.body[0].value.value is True
            or node.body[0].value.value is False
        )
        or len(node.orelse) != 1
        or not isinstance(node.orelse[0], ast.Return)
        or not isinstance(node.orelse[0].value, BOOL_CONST_TYPES)
        or not (
            node.orelse[0].value.value is True
            or node.orelse[0].value.value is False
        )
    ):
        return errors
    cond = to_source(node.test)
    errors.append((node.lineno, node.col_offset, SIM103.format(cond=cond)))
    return errors


def get_sim108(node: If) -> List[Tuple[int, int, str]]:
    """
    Get a list of all if-elses which could be a ternary operator assignment.

        If(
            test=Name(id='a', ctx=Load()),
            body=[
                Assign(
                    targets=[Name(id='b', ctx=Store())],
                    value=Name(id='c', ctx=Load()),
                    type_comment=None,
                ),
            ],
            orelse=[
                Assign(
                    targets=[Name(id='b', ctx=Store())],
                    value=Name(id='d', ctx=Load()),
                    type_comment=None,
                ),
            ],
        ),
    """
    RULE = (
        "SIM108 Use ternary operator "
        "'{assign} = {body} if {cond} else {orelse}' "
        "instead of if-else-block"
    )
    errors: List[Tuple[int, int, str]] = []
    if not (
        len(node.body) == 1
        and isinstance(node.body[0], ast.Assign)
        and len(node.orelse) == 1
        and isinstance(node.orelse[0], ast.Assign)
        and len(node.body[0].targets) == 1
        and len(node.orelse[0].targets) == 1
        and isinstance(node.body[0].targets[0], ast.Name)
        and isinstance(node.orelse[0].targets[0], ast.Name)
        and node.body[0].targets[0].id == node.orelse[0].targets[0].id
    ):
        return errors

    target_var = node.body[0].targets[0]
    assign = to_source(target_var)

    # It's part of a bigger if-elseif block:
    # https://github.com/MartinThoma/flake8-simplify/issues/115
    if isinstance(node.parent, ast.If):
        for n in node.parent.body:
            if (
                isinstance(n, ast.Assign)
                and isinstance(n.targets[0], ast.Name)
                and n.targets[0].id == target_var.id
            ):
                return errors

    body = to_source(node.body[0].value)
    cond = to_source(node.test)
    orelse = to_source(node.orelse[0].value)
    new_code = RULE.format(assign=assign, body=body, cond=cond, orelse=orelse)
    if len(new_code) > 79:
        return errors
    errors.append((node.lineno, node.col_offset, new_code))
    return errors


def get_sim114(node: ast.If) -> List[Tuple[int, int, str]]:
    """
    Find same bodys.

    Examples
    --------
        If(
            test=Name(id='a', ctx=Load()),
            body=[
                Expr(
                    value=Name(id='b', ctx=Load()),
                ),
            ],
            orelse=[
                If(
                    test=Name(id='c', ctx=Load()),
                    body=[
                        Expr(
                            value=Name(id='b', ctx=Load()),
                        ),
                    ],
                    orelse=[],
                ),
            ],
        ),
    """
    SIM114 = "SIM114 Use logical or (({cond1}) or ({cond2})) and a single body"
    errors: List[Tuple[int, int, str]] = []
    if_body_pairs = get_if_body_pairs(node)
    error_pairs = []
    for i in range(len(if_body_pairs) - 1):
        # It's not all combinations because of this:
        # https://github.com/MartinThoma/flake8-simplify/issues/70
        # #issuecomment-924074984
        ifbody1 = if_body_pairs[i]
        ifbody2 = if_body_pairs[i + 1]
        if is_body_same(ifbody1[1], ifbody2[1]):
            error_pairs.append((ifbody1, ifbody2))
    for ifbody1, ifbody2 in error_pairs:
        errors.append(
            (
                ifbody1[0].lineno,
                ifbody1[0].col_offset,
                SIM114.format(
                    cond1=to_source(ifbody1[0]), cond2=to_source(ifbody2[0])
                ),
            )
        )
    return errors


def get_sim116(node: ast.If) -> List[Tuple[int, int, str]]:
    """
    Find places where 3 or more consecutive if-statements with direct returns.

    * Each if-statement must be a check for equality with the
      same variable
    * Each if-statement must just have a "return"
    * Else must also just have a return
    """
    SIM116 = (
        "SIM116 Use a dictionary lookup instead of 3+ if/elif-statements: "
        "return {ret}"
    )
    errors: List[Tuple[int, int, str]] = []
    if not (
        isinstance(node.test, ast.Compare)
        and isinstance(node.test.left, ast.Name)
        and len(node.test.ops) == 1
        and isinstance(node.test.ops[0], ast.Eq)
        and len(node.test.comparators) == 1
        and isinstance(node.test.comparators[0], AST_CONST_TYPES)
        and len(node.body) == 1
        and isinstance(node.body[0], ast.Return)
        and len(node.orelse) == 1
        and isinstance(node.orelse[0], ast.If)
    ):
        return errors
    variable = node.test.left
    child: Optional[ast.If] = node.orelse[0]
    assert isinstance(child, ast.If), "hint for mypy"
    else_value: Optional[str] = None
    key_value_pairs: Dict[Any, Any]
    if isinstance(node.test.comparators[0], ast.Str):
        value = to_source(node.body[0].value)
        if value[0] == '"' and value[-1] == '"':
            value = value[1:-1]
        key_value_pairs = {node.test.comparators[0].s: value}
    elif isinstance(node.test.comparators[0], ast.Num):
        key_value_pairs = {
            node.test.comparators[0].n: to_source(node.body[0].value)
        }
    else:
        key_value_pairs = {
            node.test.comparators[0].value: to_source(node.body[0].value)
        }
    while child:
        if not (
            isinstance(child.test, ast.Compare)
            and isinstance(child.test.left, ast.Name)
            and child.test.left.id == variable.id
            and len(child.test.ops) == 1
            and isinstance(child.test.ops[0], ast.Eq)
            and len(child.test.comparators) == 1
            and isinstance(child.test.comparators[0], AST_CONST_TYPES)
            and len(child.body) == 1
            and isinstance(child.body[0], ast.Return)
            and len(child.orelse) <= 1
        ):
            return errors
        return_call = child.body[0]
        assert isinstance(return_call, ast.Return), "hint for mypy"
        if isinstance(return_call.value, ast.Call):
            # See https://github.com/MartinThoma/flake8-simplify/issues/113
            return errors
        key: Any
        if isinstance(child.test.comparators[0], ast.Str):
            key = child.test.comparators[0].s
        elif isinstance(child.test.comparators[0], ast.Num):
            key = child.test.comparators[0].n
        else:
            key = child.test.comparators[0].value

        value = to_source(child.body[0].value)
        if value[0] == '"' and value[-1] == '"':
            value = value[1:-1]
        key_value_pairs[key] = value

        if len(child.orelse) == 1:
            if isinstance(child.orelse[0], ast.If):
                child = child.orelse[0]
            elif isinstance(child.orelse[0], ast.Return):
                else_value = to_source(child.orelse[0].value)
                child = None
            else:
                return errors
        else:
            child = None
    if len(key_value_pairs) < 3:
        return errors
    if else_value:
        ret = f"{key_value_pairs}.get({variable.id}, {else_value})"
    else:
        ret = f"{key_value_pairs}.get({variable.id})"
    errors.append((node.lineno, node.col_offset, SIM116.format(ret=ret)))
    return errors


def get_sim908(node: ast.If) -> List[Tuple[int, int, str]]:
    """
    Get all if-blocks which only check if a key is in a dictionary.
    """
    RULE = (
        "SIM908 Use '{dictname}.get({key})' instead of "
        "'if {key} in {dictname}: {dictname}[{key}]'"
    )
    errors: List[Tuple[int, int, str]] = []
    if not (
        isinstance(node.test, ast.Compare)
        and len(node.test.ops) == 1
        and isinstance(node.test.ops[0], ast.In)
        and len(node.body) == 1
        and len(node.orelse) == 0
    ):
        return errors

    # We might still be left with a check if a value is in a list or in
    # the body the developer might remove the element from the list
    # We need to have a look at the body
    if not (
        isinstance(node.body[0], ast.Assign)
        and isinstance(node.body[0].value, ast.Subscript)
        and len(node.body[0].targets) == 1
        and isinstance(node.body[0].targets[0], ast.Name)
    ):
        return errors

    test_var = node.test.left
    slice_var = node.body[0].value.slice
    if to_source(slice_var) != to_source(test_var):
        return errors

    key = to_source(node.test.left)
    dictname = to_source(node.test.comparators[0])
    errors.append(
        (
            node.lineno,
            node.col_offset,
            RULE.format(key=key, dictname=dictname),
        )
    )
    return errors


def get_sim401(node: ast.If) -> List[Tuple[int, int, str]]:
    """
    Get all calls that should use default values for dictionary access.

    Pattern 1
    ---------
    if key in a_dict:
        value = a_dict[key]
    else:
        value = "default"

    which is

        If(
            test=Compare(
                left=Name(id='key', ctx=Load()),
                ops=[In()],
                comparators=[Name(id='a_dict', ctx=Load())],
            ),
            body=[
                Assign(
                    targets=[Name(id='value', ctx=Store())],
                    value=Subscript(
                        value=Name(id='a_dict', ctx=Load()),
                        slice=Name(id='key', ctx=Load()),
                        ctx=Load(),
                    ),
                    type_comment=None,
                ),
            ],
            orelse=[
                Assign(
                    targets=[Name(id='value', ctx=Store())],
                    value=Constant(value='default', kind=None),
                    type_comment=None,
                ),
            ],
        ),

    Pattern 2
    ---------

        if key not in a_dict:
            value = 'default'
        else:
            value = a_dict[key]

    which is

        If(
            test=Compare(
                left=Name(id='key', ctx=Load()),
                ops=[NotIn()],
                comparators=[Name(id='a_dict', ctx=Load())],
            ),
            body=[
                Assign(
                    targets=[Name(id='value', ctx=Store())],
                    value=Constant(value='default', kind=None),
                    type_comment=None,
                ),
            ],
            orelse=[
                Assign(
                    targets=[Name(id='value', ctx=Store())],
                    value=Subscript(
                        value=Name(id='a_dict', ctx=Load()),
                        slice=Name(id='key', ctx=Load()),
                        ctx=Load(),
                    ),
                    type_comment=None,
                ),
            ],
        )

    """
    SIM401 = (
        "SIM401 Use '{value} = {dict}.get({key}, {default_value})' "
        "instead of an if-block"
    )
    errors: List[Tuple[int, int, str]] = []
    is_pattern_1 = (
        len(node.body) == 1
        and isinstance(node.body[0], ast.Assign)
        and len(node.body[0].targets) == 1
        and isinstance(node.body[0].value, ast.Subscript)
        and len(node.orelse) == 1
        and isinstance(node.orelse[0], ast.Assign)
        and len(node.orelse[0].targets) == 1
        and isinstance(node.test, ast.Compare)
        and len(node.test.ops) == 1
        and isinstance(node.test.ops[0], ast.In)
    )

    # just like pattern_1, but using NotIn and reversing if/else
    is_pattern_2 = (
        len(node.body) == 1
        and isinstance(node.body[0], ast.Assign)
        and len(node.orelse) == 1
        and isinstance(node.orelse[0], ast.Assign)
        and isinstance(node.orelse[0].value, ast.Subscript)
        and isinstance(node.test, ast.Compare)
        and len(node.test.ops) == 1
        and isinstance(node.test.ops[0], ast.NotIn)
    )
    if is_pattern_1:
        assert isinstance(node.test, ast.Compare)
        assert isinstance(node.body[0], ast.Assign)
        assert isinstance(node.body[0].value, ast.Subscript)
        assert isinstance(node.orelse[0], ast.Assign)
        key = node.test.left
        if to_source(key) != to_source(node.body[0].value.slice):
            return errors  # second part of pattern 1
        assign_to_if_body = node.body[0].targets[0]
        assign_to_else = node.orelse[0].targets[0]
        if to_source(assign_to_if_body) != to_source(assign_to_else):
            return errors
        dict_name = node.test.comparators[0]
        default_value = node.orelse[0].value
        value_node = node.body[0].targets[0]
        key_str = to_source(key)
        dict_str = to_source(dict_name)
        default_str = to_source(default_value)
        value_str = to_source(value_node)
    elif is_pattern_2:
        assert isinstance(node.test, ast.Compare)
        assert isinstance(node.body[0], ast.Assign)
        assert isinstance(node.orelse[0], ast.Assign)
        assert isinstance(node.orelse[0].value, ast.Subscript)
        key = node.test.left
        if to_source(key) != to_source(node.orelse[0].value.slice):
            return errors  # second part of pattern 1
        dict_name = node.test.comparators[0]
        default_value = node.body[0].value
        value_node = node.body[0].targets[0]
        key_str = to_source(key)
        dict_str = to_source(dict_name)
        default_str = to_source(default_value)
        value_str = to_source(value_node)
    else:
        return errors
    errors.append(
        (
            node.lineno,
            node.col_offset,
            SIM401.format(
                key=key_str,
                dict=dict_str,
                default_value=default_str,
                value=value_str,
            ),
        )
    )
    return errors
