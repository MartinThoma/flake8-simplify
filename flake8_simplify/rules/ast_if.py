import ast
from collections.abc import Iterator
from typing import Any

from flake8_simplify.registry import Violation, rule
from flake8_simplify.utils import (
    get_if_body_pairs,
    get_parent,
    is_body_same,
    to_source,
)


def _is_main_check(test: ast.expr) -> bool:
    """Check for ``__name__ <op> "__main__"``."""
    return (
        isinstance(test, ast.Compare)
        and isinstance(test.left, ast.Name)
        and test.left.id == "__name__"
        and len(test.comparators) == 1
        and isinstance(test.comparators[0], ast.Constant)
        and test.comparators[0].value == "__main__"
    )


def _returns_bool(body: list[ast.stmt]) -> bool:
    """Check if the body is just ``return True`` or ``return False``."""
    return (
        len(body) == 1
        and isinstance(body[0], ast.Return)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, bool)
    )


def _get_single_name_assign(
    body: list[ast.stmt],
) -> tuple[ast.Name, ast.expr] | None:
    """Get target and value if the body is just ``name = value``."""
    if not (
        len(body) == 1
        and isinstance(body[0], ast.Assign)
        and len(body[0].targets) == 1
        and isinstance(body[0].targets[0], ast.Name)
    ):
        return None
    return body[0].targets[0], body[0].value


def _get_eq_constant_check(
    test: ast.expr,
) -> tuple[ast.Name, ast.Constant] | None:
    """Get the name and the constant of ``name == constant``."""
    if (
        isinstance(test, ast.Compare)
        and isinstance(test.left, ast.Name)
        and len(test.ops) == 1
        and isinstance(test.ops[0], ast.Eq)
        and len(test.comparators) == 1
        and isinstance(test.comparators[0], ast.Constant)
    ):
        return test.left, test.comparators[0]
    return None


def _strip_double_quotes(source: str) -> str:
    if source.startswith('"') and source.endswith('"'):
        return source[1:-1]
    return source


@rule("SIM102", ast.If)
def get_sim102(node: ast.If) -> Iterator[Violation]:
    """Get a list of all nested if-statements without else-blocks."""
    RULE = "Use a single if-statement instead of nested if-statements"

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
        return
    if _is_main_check(node.test):
        return
    yield Violation(node, RULE)


@rule("SIM103", ast.If)
def get_sim103(node: ast.If) -> Iterator[Violation]:
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
    SIM103 = "Return the condition {cond} directly"
    if not (_returns_bool(node.body) and _returns_bool(node.orelse)):
        return
    cond = to_source(node.test)
    yield Violation(node, SIM103.format(cond=cond))


@rule("SIM108", ast.If)
def get_sim108(node: ast.If) -> Iterator[Violation]:
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
        "Use ternary operator "
        "'{assign} = {body} if {cond} else {orelse}' "
        "instead of if-else-block"
    )
    body_assign = _get_single_name_assign(node.body)
    orelse_assign = _get_single_name_assign(node.orelse)
    if not (
        body_assign
        and orelse_assign
        and body_assign[0].id == orelse_assign[0].id
    ):
        return

    target_var, body_value = body_assign
    assign = to_source(target_var)

    # It's part of a bigger if-elseif block:
    # https://github.com/MartinThoma/flake8-simplify/issues/115
    parent = get_parent(node)
    if isinstance(parent, ast.If):
        for n in parent.body:
            if (
                isinstance(n, ast.Assign)
                and isinstance(n.targets[0], ast.Name)
                and n.targets[0].id == target_var.id
            ):
                return

    body = to_source(body_value)
    cond = to_source(node.test)
    orelse = to_source(orelse_assign[1])
    new_code = RULE.format(assign=assign, body=body, cond=cond, orelse=orelse)
    # Only suggest the ternary if the full message fits into 79 characters
    if len(f"SIM108 {new_code}") > 79:
        return
    yield Violation(node, new_code)


@rule("SIM114", ast.If)
def get_sim114(node: ast.If) -> Iterator[Violation]:
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
    SIM114 = "Use logical or (({cond1}) or ({cond2})) and a single body"
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
        yield Violation(
            ifbody1[0],
            SIM114.format(
                cond1=to_source(ifbody1[0]), cond2=to_source(ifbody2[0])
            ),
        )


@rule("SIM116", ast.If)
def get_sim116(node: ast.If) -> Iterator[Violation]:
    """
    Find places where 3 or more consecutive if-statements with direct returns.

    * Each if-statement must be a check for equality with the
      same variable
    * Each if-statement must just have a "return"
    * Else must also just have a return
    """
    SIM116 = (
        "Use a dictionary lookup instead of 3+ if/elif-statements: "
        "return {ret}"
    )
    check = _get_eq_constant_check(node.test)
    if not (
        check
        and len(node.body) == 1
        and isinstance(node.body[0], ast.Return)
        and len(node.orelse) == 1
        and isinstance(node.orelse[0], ast.If)
    ):
        return
    variable, first_key = check
    first_value = to_source(node.body[0].value)
    if isinstance(first_key.value, str):
        first_value = _strip_double_quotes(first_value)
    key_value_pairs: dict[Any, str] = {first_key.value: first_value}

    else_value: str | None = None
    child: ast.If | None = node.orelse[0]
    while child:
        check = _get_eq_constant_check(child.test)
        if not (
            check
            and check[0].id == variable.id
            and len(child.body) == 1
            and isinstance(child.body[0], ast.Return)
            and len(child.orelse) <= 1
        ):
            return
        return_value = child.body[0].value
        if isinstance(return_value, ast.Call):
            # See https://github.com/MartinThoma/flake8-simplify/issues/113
            return
        key_value_pairs[check[1].value] = _strip_double_quotes(
            to_source(return_value)
        )

        if len(child.orelse) == 1:
            if isinstance(child.orelse[0], ast.If):
                child = child.orelse[0]
            elif isinstance(child.orelse[0], ast.Return):
                else_value = to_source(child.orelse[0].value)
                child = None
            else:
                return
        else:
            child = None
    if len(key_value_pairs) < 3:
        return
    if else_value:
        ret = f"{key_value_pairs}.get({variable.id}, {else_value})"
    else:
        ret = f"{key_value_pairs}.get({variable.id})"
    yield Violation(node, SIM116.format(ret=ret))


@rule("SIM908", ast.If)
def get_sim908(node: ast.If) -> Iterator[Violation]:
    """
    Get all if-blocks which only check if a key is in a dictionary.
    """
    RULE = (
        "Use '{dictname}.get({key})' instead of "
        "'if {key} in {dictname}: {dictname}[{key}]'"
    )
    if not (
        isinstance(node.test, ast.Compare)
        and len(node.test.ops) == 1
        and isinstance(node.test.ops[0], ast.In)
        and len(node.body) == 1
        and len(node.orelse) == 0
    ):
        return

    # We might still be left with a check if a value is in a list or in
    # the body the developer might remove the element from the list
    # We need to have a look at the body
    if not (
        isinstance(node.body[0], ast.Assign)
        and isinstance(node.body[0].value, ast.Subscript)
        and len(node.body[0].targets) == 1
        and isinstance(node.body[0].targets[0], ast.Name)
    ):
        return

    test_var = node.test.left
    slice_var = node.body[0].value.slice
    if to_source(slice_var) != to_source(test_var):
        return

    key = to_source(node.test.left)
    dictname = to_source(node.test.comparators[0])
    yield Violation(node, RULE.format(key=key, dictname=dictname))


def _get_dict_get_parts(
    node: ast.If,
) -> tuple[ast.expr, ast.expr, ast.expr, ast.expr] | None:
    """
    Match the if-blocks that dict.get(key, default) could replace.

    Returns the key, the dictionary, the default value and the assigned
    variable.
    """
    test = node.test
    if not (
        isinstance(test, ast.Compare)
        and len(test.ops) == 1
        and len(node.body) == 1
        and isinstance(node.body[0], ast.Assign)
        and len(node.orelse) == 1
        and isinstance(node.orelse[0], ast.Assign)
    ):
        return None
    body, orelse = node.body[0], node.orelse[0]

    if isinstance(test.ops[0], ast.In):
        # The if-branch reads the dict, the else-branch uses the default
        if len(body.targets) != 1 or len(orelse.targets) != 1:
            return None
        if to_source(body.targets[0]) != to_source(orelse.targets[0]):
            return None
        lookup, default = body, orelse
    elif isinstance(test.ops[0], ast.NotIn):
        # Same, but reversed. The targets are not compared here.
        lookup, default = orelse, body
    else:
        return None

    if not isinstance(lookup.value, ast.Subscript):
        return None
    if to_source(test.left) != to_source(lookup.value.slice):
        return None
    return test.left, test.comparators[0], default.value, body.targets[0]


@rule("SIM401", ast.If)
def get_sim401(node: ast.If) -> Iterator[Violation]:
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
        "Use '{value} = {dict}.get({key}, {default_value})' "
        "instead of an if-block"
    )
    parts = _get_dict_get_parts(node)
    if parts is None:
        return
    key, dict_name, default_value, value_node = parts
    yield Violation(
        node,
        SIM401.format(
            key=to_source(key),
            dict=to_source(dict_name),
            default_value=to_source(default_value),
            value=to_source(value_node),
        ),
    )
