# Core Library
import ast
import itertools
import json
import logging
import sys
from collections import defaultdict
from typing import (
    Any,
    DefaultDict,
    Dict,
    Generator,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)

# Third party
import astor

logger = logging.getLogger(__name__)


class UnaryOp(ast.UnaryOp):
    def __init__(self, orig: ast.UnaryOp) -> None:
        self.op = orig.op
        self.operand = orig.operand
        # For all ast.*:
        self.lineno = orig.lineno
        self.col_offset = orig.col_offset
        self.parent: ast.Expr = orig.parent  # type: ignore


class Call(ast.Call):
    def __init__(self, orig: ast.Call) -> None:
        self.func = orig.func
        self.args = orig.args
        self.keywords = orig.keywords
        # For all ast.*:
        self.lineno = orig.lineno
        self.col_offset = orig.col_offset
        self.parent: ast.Expr = orig.parent  # type: ignore


if sys.version_info < (3, 8):  # pragma: no cover (<PY38)
    # Third party
    import importlib_metadata
else:  # pragma: no cover (PY38+)
    # Core Library
    import importlib.metadata as importlib_metadata

# Python-Specific
SIM101 = (
    "SIM101 Multiple isinstance-calls which can be merged into a single "
    "call for variable '{var}'"
)
SIM102 = "SIM102 Use a single if-statement instead of nested if-statements"
SIM103 = "SIM103 Return the condition {cond} directly"
SIM104 = "SIM104 Use 'yield from {iterable}'"
SIM105 = "SIM105 Use 'contextlib.suppress({exception})'"
SIM106 = "SIM106 Handle error-cases first"
SIM107 = "SIM107 Don't use return in try/except and finally"
SIM108 = (
    "SIM108 Use ternary operator "
    "'{assign} = {body} if {cond} else {orelse}' "
    "instead of if-else-block"
)
SIM109 = "SIM109 Use '{value} in {values}' instead of '{or_op}'"
SIM110 = "SIM110 Use 'return any({check} for {target} in {iterable})'"
SIM111 = "SIM111 Use 'return all({check} for {target} in {iterable})'"
SIM112 = "SIM112 Use '{expected}' instead of '{original}'"
SIM113 = "SIM113 Use enumerate instead of '{variable}'"
SIM114 = "SIM114 Use logical or (({cond1}) or ({cond2})) and a single body"
SIM115 = "SIM115 Use context handler for opening files"
SIM116 = (
    "SIM116 Use a dictionary lookup instead of 3+ if/elif-statements: "
    "return {ret}"
)
SIM117 = "SIM117 Use '{merged_with}' instead of multiple with statements"
SIM118 = "SIM118 Use '{el} in {dict}' instead of '{el} in {dict}.keys()'"
SIM119 = "SIM119 Use a dataclass for 'class {classname}'"
SIM120 = (
    "SIM120 Use 'class {classname}:' instead of 'class {classname}(object):'"
)

# Comparations
SIM201 = "SIM201 Use '{left} != {right}' instead of 'not {left} == {right}'"
SIM202 = "SIM202 Use '{left} == {right}' instead of 'not {left} != {right}'"
SIM203 = "SIM203 Use '{a} not in {b}' instead of 'not {a} in {b}'"
SIM204 = "SIM204 Use '{a} >= {b}' instead of 'not ({a} < {b})'"
SIM205 = "SIM205 Use '{a} > {b}' instead of 'not ({a} <= {b})'"
SIM206 = "SIM206 Use '{a} <= {b}' instead of 'not ({a} > {b})'"
SIM207 = "SIM207 Use '{a} < {b}' instead of 'not ({a} >= {b})'"
SIM208 = "SIM208 Use '{a}' instead of 'not (not {a})'"
SIM210 = "SIM210 Use 'bool({cond})' instead of 'True if {cond} else False'"
SIM211 = "SIM211 Use 'not {cond}' instead of 'False if {cond} else True'"
SIM212 = (
    "SIM212 Use '{a} if {a} else {b}' instead of '{b} if not {a} else {a}'"
)
SIM220 = "SIM220 Use 'False' instead of '{a} and not {a}'"
SIM221 = "SIM221 Use 'True' instead of '{a} or not {a}'"
SIM222 = "SIM222 Use 'True' instead of '... or True'"
SIM223 = "SIM223 Use 'False' instead of '... and False'"
SIM300 = (
    "SIM300 Use '{right} == {left}' instead of "
    "'{left} == {right}' (Yoda-conditions)"
)
SIM401 = (
    "SIM401 Use '{value} = {dict}.get({key}, {default_value})' "
    "instead of an if-block"
)
SIM901 = "SIM901 Use '{expected}' instead of '{actual}'"
SIM904 = "SIM904 Initialize dictionary '{dict_name}' directly"
SIM905 = "SIM905 Use '{expected}' instead of '{actual}'"
SIM906 = "SIM906 Use '{expected}' instead of '{actual}'"

# ast.Constant in Python 3.8, ast.NameConstant in Python 3.6 and 3.7
BOOL_CONST_TYPES = (ast.Constant, ast.NameConstant)
AST_CONST_TYPES = (ast.Constant, ast.NameConstant, ast.Str, ast.Num)
STR_TYPES = (ast.Constant, ast.Str)


def strip_parenthesis(string: str) -> str:
    if len(string) >= 2 and string[0] == "(" and string[-1] == ")":
        return string[1:-1]
    return string


def strip_triple_quotes(string: str) -> str:
    quotes = '"""'
    is_tripple_quoted = string.startswith(quotes) and string.endswith(quotes)
    if not (
        is_tripple_quoted and '"' not in string[len(quotes) : -len(quotes)]
    ):
        return string
    string = string[len(quotes) : -len(quotes)]
    string = f'"{string}"'
    if len(string) == 0:
        string = '""'
    return string


def use_double_quotes(string: str) -> str:
    quotes = "'''"
    if string.startswith(quotes) and string.endswith(quotes):
        return f'"""{string[len(quotes):-len(quotes)]}"""'
    if len(string) >= 2 and string[0] == "'" and string[-1] == "'":
        return f'"{string[1:-1]}"'
    return string


def to_source(
    node: Union[None, ast.expr, ast.Expr, ast.withitem, ast.slice]
) -> str:
    if node is None:
        return "None"
    source: str = astor.to_source(node).strip()
    source = strip_parenthesis(source)
    source = strip_triple_quotes(source)
    source = use_double_quotes(source)
    return source


def _get_duplicated_isinstance_call_by_node(node: ast.BoolOp) -> List[str]:
    """
    Get a list of isinstance arguments which could be shortened.

    This checks SIM101.

    Examples
    --------
    >> g = _get_duplicated_isinstance_call_by_node
    >> g("isinstance(a, int) or isinstance(a, float) or isinstance(b, int)
    ['a']
    >> g("isinstance(a, int) or isinstance(b, float) or isinstance(b, int)
    ['b']
    """
    counter: DefaultDict[str, int] = defaultdict(int)

    for call in node.values:
        # Make sure that this function call is actually a call of the built-in
        # "isinstance"
        if not isinstance(call, ast.Call) or len(call.args) != 2:
            continue
        function_name = to_source(call.func)
        if function_name != "isinstance":
            continue

        # Collect the name of the argument
        isinstance_arg0_name = to_source(call.args[0])
        counter[isinstance_arg0_name] += 1
    return [arg0_name for arg0_name, count in counter.items() if count > 1]


def _get_sim101(
    node: ast.BoolOp,
) -> List[Tuple[int, int, str]]:
    """Get a positions where the duplicate isinstance problem appears."""
    errors: List[Tuple[int, int, str]] = []
    if not isinstance(node.op, ast.Or):
        return errors

    for var in _get_duplicated_isinstance_call_by_node(node):
        errors.append((node.lineno, node.col_offset, SIM101.format(var=var)))
    return errors


def _get_sim102(node: ast.If) -> List[Tuple[int, int, str]]:
    """Get a list of all nested if-statements without else-blocks."""
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
    # if a: < irrelvant for here
    #     pass
    # elif b:  <--- this is treated like a nested block
    #     if c: <---
    #         d

    if not is_pattern_1:
        return errors
    errors.append((node.lineno, node.col_offset, SIM102))
    return errors


def _get_sim103(node: ast.If) -> List[Tuple[int, int, str]]:
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


def _get_sim104(node: ast.For) -> List[Tuple[int, int, str]]:
    """
    Get a list of all "iterate and yield" patterns.

    for item in iterable:
        yield item

    which is

        For(
            target=Name(id='item', ctx=Store()),
            iter=Name(id='iterable', ctx=Load()),
            body=[
                Expr(
                    value=Yield(
                        value=Name(id='item', ctx=Load()),
                    ),
                ),
            ],
            orelse=[],
            type_comment=None,
        ),

    """
    errors: List[Tuple[int, int, str]] = []
    if (
        len(node.body) != 1
        or not isinstance(node.body[0], ast.Expr)
        or not isinstance(node.body[0].value, ast.Yield)
        or not isinstance(node.target, ast.Name)
        or not isinstance(node.body[0].value.value, ast.Name)
        or node.target.id != node.body[0].value.value.id
        or node.orelse != []
    ):
        return errors
    if isinstance(node.parent, ast.AsyncFunctionDef):  # type: ignore
        return errors
    iterable = to_source(node.iter)
    errors.append(
        (node.lineno, node.col_offset, SIM104.format(iterable=iterable))
    )
    return errors


def _get_sim105(node: ast.Try) -> List[Tuple[int, int, str]]:
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


def _get_sim106(node: ast.If) -> List[Tuple[int, int, str]]:
    """
    Get a list of all calls where an exception is raised in else.

    if cond:
        return True
    else:
        raise Exception

    which is

        If(
            test=Name(id='cond', ctx=Load()),
            body=[
                Expr(
                    value=Name(id='a', ctx=Load()),
                ),
                Expr(
                    value=Name(id='b', ctx=Load()),
                ),
                Expr(
                    value=Name(id='c', ctx=Load()),
                ),
            ],
            orelse=[
                Raise(
                    exc=Name(id='Exception', ctx=Load()),
                    cause=None,
                ),
            ],
        )
    """
    errors: List[Tuple[int, int, str]] = []
    just_one = (
        len(node.orelse) == 1
        and len(node.orelse) >= 1
        and isinstance(node.orelse[-1], ast.Raise)
        and not isinstance(node.body[-1], ast.Raise)
    )
    many = (
        len(node.body) > 2 * len(node.orelse)
        and len(node.orelse) >= 1
        and isinstance(node.orelse[-1], ast.Raise)
        and not isinstance(node.body[-1], ast.Raise)
    )
    if not (just_one or many):
        return errors
    ast_raise = node.orelse[-1]
    if not isinstance(ast_raise, ast.Raise):
        return errors
    ast_raised = ast_raise.exc
    if (
        isinstance(ast_raised, ast.Call)
        and ast_raised.func
        and isinstance(ast_raised.func, ast.Name)
        and ast_raised.func.id in ["ValueError", "NotImplementedError"]
    ):
        return errors

    errors.append((node.lineno, node.col_offset, SIM106))
    return errors


def _get_sim107(node: ast.Try) -> List[Tuple[int, int, str]]:
    """
    Get a list of all calls where try/except and finally have 'return'.
    """
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


def _get_sim108(node: ast.If) -> List[Tuple[int, int, str]]:
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
    errors: List[Tuple[int, int, str]] = []
    if not (
        len(node.body) == 1
        and len(node.orelse) == 1
        and isinstance(node.body[0], ast.Assign)
        and isinstance(node.orelse[0], ast.Assign)
        and len(node.body[0].targets) == 1
        and len(node.orelse[0].targets) == 1
        and isinstance(node.body[0].targets[0], ast.Name)
        and isinstance(node.orelse[0].targets[0], ast.Name)
        and node.body[0].targets[0].id == node.orelse[0].targets[0].id
    ):
        return errors
    assign = to_source(node.body[0].targets[0])
    body = to_source(node.body[0].value)
    cond = to_source(node.test)
    orelse = to_source(node.orelse[0].value)
    new_code = SIM108.format(
        assign=assign, body=body, cond=cond, orelse=orelse
    )
    if len(new_code) > 79:
        return errors
    errors.append((node.lineno, node.col_offset, new_code))
    return errors


def _get_sim109(node: ast.BoolOp) -> List[Tuple[int, int, str]]:
    """
    Check if multiple equalities with the same value are combined via "or".

        BoolOp(
                op=Or(),
                values=[
                    Compare(
                        left=Name(id='a', ctx=Load()),
                        ops=[Eq()],
                        comparators=[Name(id='b', ctx=Load())],
                    ),
                    Compare(
                        left=Name(id='a', ctx=Load()),
                        ops=[Eq()],
                        comparators=[Name(id='c', ctx=Load())],
                    ),
                ],
        )
    """
    errors: List[Tuple[int, int, str]] = []
    if not isinstance(node.op, ast.Or):
        return errors
    equalities = [
        value
        for value in node.values
        if isinstance(value, ast.Compare)
        and len(value.ops) == 1
        and isinstance(value.ops[0], ast.Eq)
    ]
    id2vals: Dict[str, List[ast.Name]] = defaultdict(list)
    for eq in equalities:
        if (
            isinstance(eq.left, ast.Name)
            and len(eq.comparators) == 1
            and isinstance(eq.comparators[0], ast.Name)
        ):
            id2vals[eq.left.id].append(eq.comparators[0])
    for value, values in id2vals.items():
        if len(values) == 1:
            continue
        errors.append(
            (
                node.lineno,
                node.col_offset,
                SIM109.format(
                    or_op=to_source(node),
                    value=value,
                    values=f"({to_source(ast.Tuple(elts=values))})",
                ),
            )
        )
    return errors


def _get_sim110_sim111(node: ast.For) -> List[Tuple[int, int, str]]:
    """
    Check if any / all could be used.

    For(
        target=Name(id='x', ctx=Store()),
        iter=Name(id='iterable', ctx=Load()),
        body=[
            If(
                test=Call(
                    func=Name(id='check', ctx=Load()),
                    args=[Name(id='x', ctx=Load())],
                    keywords=[],
                ),
                body=[
                    Return(
                        value=Constant(value=True, kind=None),
                    ),
                ],
                orelse=[],
            ),
        ],
        orelse=[],
        type_comment=None,
    ),
    Return(value=Constant(value=False, kind=None))
    """
    errors: List[Tuple[int, int, str]] = []
    if not (
        len(node.body) == 1
        and isinstance(node.body[0], ast.If)
        and len(node.body[0].body) == 1
        and isinstance(node.body[0].body[0], ast.Return)
        and isinstance(node.body[0].body[0].value, BOOL_CONST_TYPES)
    ):
        return errors
    if not hasattr(node.body[0].body[0].value, "value"):
        return errors
    if isinstance(node.next_sibling, ast.Raise):  # type: ignore
        return errors
    check = to_source(node.body[0].test)
    target = to_source(node.target)
    iterable = to_source(node.iter)
    if node.body[0].body[0].value.value is True:
        errors.append(
            (
                node.lineno,
                node.col_offset,
                SIM110.format(check=check, target=target, iterable=iterable),
            )
        )
    elif node.body[0].body[0].value.value is False:
        is_compound_expression = " and " in check or " or " in check

        if is_compound_expression:
            check = f"not ({check})"
        else:
            if check.startswith("not "):
                check = check[len("not ") :]
            else:
                check = f"not {check}"
        errors.append(
            (
                node.lineno,
                node.col_offset,
                SIM111.format(check=check, target=target, iterable=iterable),
            )
        )
    return errors


def _get_sim112(node: ast.Expr) -> List[Tuple[int, int, str]]:
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
            SIM112.format(original=original, expected=expected),
        )
    )
    return errors


def _get_sim113(node: ast.For) -> List[Tuple[int, int, str]]:
    """
    Find loops in which "enumerate" should be used.

        For(
            target=Name(id='el', ctx=Store()),
            iter=Name(id='iterable', ctx=Load()),
            body=[
                Expr(
                    value=Constant(value=Ellipsis, kind=None),
                ),
                AugAssign(
                    target=Name(id='idx', ctx=Store()),
                    op=Add(),
                    value=Constant(value=1, kind=None),
                ),
            ],
            orelse=[],
            type_comment=None,
        ),
    """
    errors: List[Tuple[int, int, str]] = []
    variable_candidates = []
    if body_contains_continue(node.body):
        return errors
    for expression in node.body:
        if (
            isinstance(expression, ast.AugAssign)
            and is_constant_increase(expression)
            and isinstance(expression.target, ast.Name)
        ):
            variable_candidates.append(expression.target)

    for candidate in variable_candidates:
        errors.append(
            (
                candidate.lineno,
                candidate.col_offset,
                SIM113.format(variable=to_source(candidate)),
            )
        )
    return errors


def body_contains_continue(stmts: List[ast.stmt]) -> bool:
    return any(
        isinstance(stmt, ast.Continue)
        or (isinstance(stmt, ast.If) and body_contains_continue(stmt.body))
        for stmt in stmts
    )


def _get_sim114(node: ast.If) -> List[Tuple[int, int, str]]:
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


def _get_sim115(node: Call) -> List[Tuple[int, int, str]]:
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
    errors: List[Tuple[int, int, str]] = []
    if not (
        isinstance(node.func, ast.Name)
        and node.func.id == "open"
        and not isinstance(node.parent, ast.withitem)
    ):
        return errors
    errors.append((node.lineno, node.col_offset, SIM115))
    return errors


def _get_sim116(node: ast.If) -> List[Tuple[int, int, str]]:
    """
    Find places where 3 or more consecutive if-statements with direct returns.

    * Each if-statement must be a check for equality with the
      same variable
    * Each if-statement must just have a "return"
    * Else must also just have a return
    """
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


def _get_sim117(node: ast.With) -> List[Tuple[int, int, str]]:
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


def _get_sim118(node: ast.Compare) -> List[Tuple[int, int, str]]:
    """
    Get a list of all usages of "key in dict.keys()"

    Compare(left=Name(id='key', ctx=Load()),
            ops=[In()],
            comparators=[
                Call(
                    func=Attribute(
                        value=Name(id='dict', ctx=Load()),
                        attr='keys',
                        ctx=Load(),
                    ),
                    args=[],
                    keywords=[],
                ),
            ],
        )
    """
    errors: List[Tuple[int, int, str]] = []
    if not (
        len(node.ops) == 1
        and isinstance(node.ops[0], ast.In)
        and len(node.comparators) == 1
    ):
        return errors
    call_node = node.comparators[0]
    if not isinstance(call_node, ast.Call):
        return errors

    attr_node = call_node.func
    if not (
        isinstance(call_node.func, ast.Attribute)
        and call_node.func.attr == "keys"
        and isinstance(call_node.func.ctx, ast.Load)
    ):
        return errors
    assert isinstance(attr_node, ast.Attribute), "hint for mypy"  # noqa

    key_str = to_source(node.left)
    dict_str = to_source(attr_node.value)
    errors.append(
        (
            node.lineno,
            node.col_offset,
            SIM118.format(el=key_str, dict=dict_str),
        )
    )
    return errors


def _get_sim119(node: ast.ClassDef) -> List[Tuple[int, int, str]]:
    """
    Get a list of all classes that should be dataclasses"

        ClassDef(
            name='Person',
            bases=[],
            keywords=[],
            body=[
                AnnAssign(
                    target=Name(id='first_name', ctx=Store()),
                    annotation=Name(id='str', ctx=Load()),
                    value=None,
                    simple=1,
                ),
                AnnAssign(
                    target=Name(id='last_name', ctx=Store()),
                    annotation=Name(id='str', ctx=Load()),
                    value=None,
                    simple=1,
                ),
                AnnAssign(
                    target=Name(id='birthdate', ctx=Store()),
                    annotation=Name(id='date', ctx=Load()),
                    value=None,
                    simple=1,
                ),
            ],
            decorator_list=[Name(id='dataclass', ctx=Load())],
        )
    """
    errors: List[Tuple[int, int, str]] = []

    if not (len(node.decorator_list) == 0 and len(node.bases) == 0):
        return errors

    dataclass_functions = [
        "__init__",
        "__eq__",
        "__hash__",
        "__repr__",
        "__str__",
    ]
    has_only_dataclass_functions = True
    has_any_functions = False
    has_complex_statements = False
    for body_el in node.body:
        if isinstance(body_el, (ast.FunctionDef, ast.AsyncFunctionDef)):
            has_any_functions = True
            if body_el.name == "__init__":
                # Ensure constructor only has pure assignments
                # without any calculation.
                for el in body_el.body:
                    if not isinstance(el, ast.Assign):
                        has_complex_statements = True
                        break
                    # It is an assignment, but we only allow
                    # `self.attribute = name`.
                    if any(
                        [
                            not isinstance(target, ast.Attribute)
                            for target in el.targets
                        ]
                    ) or not isinstance(el.value, ast.Name):
                        has_complex_statements = True
                        break
            if body_el.name not in dataclass_functions:
                has_only_dataclass_functions = False

    if (
        has_any_functions
        and has_only_dataclass_functions
        and not has_complex_statements
    ):
        errors.append(
            (node.lineno, node.col_offset, SIM119.format(classname=node.name))
        )

    return errors


def _get_sim120(node: ast.ClassDef) -> List[Tuple[int, int, str]]:
    """
    Get a list of all classes that inherit from object.
    """
    errors: List[Tuple[int, int, str]] = []
    if not (
        len(node.bases) == 1
        and isinstance(node.bases[0], ast.Name)
        and node.bases[0].id == "object"
    ):
        return errors
    errors.append(
        (node.lineno, node.col_offset, SIM120.format(classname=node.name))
    )
    return errors


def get_if_body_pairs(node: ast.If) -> List[Tuple[ast.expr, List[ast.stmt]]]:
    pairs = [(node.test, node.body)]
    orelse = node.orelse
    while (
        isinstance(orelse, list)
        and len(orelse) == 1
        and isinstance(orelse[0], ast.If)
    ):
        pairs.append((orelse[0].test, orelse[0].body))
        orelse = orelse[0].orelse
    return pairs


def is_body_same(body1: List[ast.stmt], body2: List[ast.stmt]) -> bool:
    """Check if two lists of expressions are equivalent."""
    if len(body1) != len(body2):
        return False
    for a, b in zip(body1, body2):
        try:
            stmt_equal = is_stmt_equal(a, b)
        except RecursionError:  # maximum recursion depth
            stmt_equal = False
        if not stmt_equal:
            return False
    return True


def is_stmt_equal(a: ast.stmt, b: ast.stmt) -> bool:
    if type(a) is not type(b):
        return False
    if isinstance(a, ast.AST):
        specials = (
            "lineno",
            "col_offset",
            "ctx",
            "end_lineno",
            "parent",
            "previous_sibling",
            "next_sibling",
        )
        for k, v in vars(a).items():
            if k.startswith("_") or k in specials:
                continue
            if not is_stmt_equal(v, getattr(b, k)):
                return False
        return True
    elif isinstance(a, list):
        if len(a) != len(b):
            return False
        return all(itertools.starmap(is_stmt_equal, zip(a, b)))
    else:
        return a == b


def is_constant_increase(expr: ast.AugAssign) -> bool:
    return isinstance(expr.op, ast.Add) and (
        (isinstance(expr.value, ast.Constant) and expr.value.value == 1)
        or (isinstance(expr.value, ast.Num) and expr.value.n == 1)
    )


def _get_sim201(node: UnaryOp) -> List[Tuple[int, int, str]]:
    """
    Get a list of all calls where an unary 'not' is used for an equality.
    """
    errors: List[Tuple[int, int, str]] = []
    if (
        (
            not isinstance(node.op, ast.Not)
            or not isinstance(node.operand, ast.Compare)
            or len(node.operand.ops) != 1
            or not isinstance(node.operand.ops[0], ast.Eq)
        )
        or isinstance(node.parent, ast.If)
        and is_exception_check(node.parent)
    ):
        return errors
    comparison = node.operand
    left = to_source(comparison.left)
    right = to_source(comparison.comparators[0])
    errors.append(
        (node.lineno, node.col_offset, SIM201.format(left=left, right=right))
    )

    return errors


def is_exception_check(node: ast.If) -> bool:
    if len(node.body) == 1 and isinstance(node.body[0], ast.Raise):
        return True
    return False


def _get_sim202(node: UnaryOp) -> List[Tuple[int, int, str]]:
    """
    Get a list of all calls where an unary 'not' is used for an quality.
    """
    errors: List[Tuple[int, int, str]] = []
    if (
        (
            not isinstance(node.op, ast.Not)
            or not isinstance(node.operand, ast.Compare)
            or len(node.operand.ops) != 1
            or not isinstance(node.operand.ops[0], ast.NotEq)
        )
        or isinstance(node.parent, ast.If)
        and is_exception_check(node.parent)
    ):
        return errors
    comparison = node.operand
    left = to_source(comparison.left)
    right = to_source(comparison.comparators[0])
    errors.append(
        (node.lineno, node.col_offset, SIM202.format(left=left, right=right))
    )

    return errors


def _get_sim203(node: UnaryOp) -> List[Tuple[int, int, str]]:
    """
    Get a list of all calls where an unary 'not' is used for an in-check.
    """
    errors: List[Tuple[int, int, str]] = []
    if (
        (
            not isinstance(node.op, ast.Not)
            or not isinstance(node.operand, ast.Compare)
            or len(node.operand.ops) != 1
            or not isinstance(node.operand.ops[0], ast.In)
        )
        or isinstance(node.parent, ast.If)
        and is_exception_check(node.parent)
    ):
        return errors
    comparison = node.operand
    left = to_source(comparison.left)
    right = to_source(comparison.comparators[0])
    errors.append(
        (node.lineno, node.col_offset, SIM203.format(a=left, b=right))
    )

    return errors


def _get_sim204(node: UnaryOp) -> List[Tuple[int, int, str]]:
    """Get a list of all calls of the type "not (a < b)"."""
    errors: List[Tuple[int, int, str]] = []
    if (
        (
            not isinstance(node.op, ast.Not)
            or not isinstance(node.operand, ast.Compare)
            or len(node.operand.ops) != 1
            or not isinstance(node.operand.ops[0], ast.Lt)
        )
        or isinstance(node.parent, ast.If)
        and is_exception_check(node.parent)
    ):
        return errors
    comparison = node.operand
    left = to_source(comparison.left)
    right = to_source(comparison.comparators[0])
    errors.append(
        (node.lineno, node.col_offset, SIM204.format(a=left, b=right))
    )
    return errors


def _get_sim205(node: UnaryOp) -> List[Tuple[int, int, str]]:
    """Get a list of all calls of the type "not (a <= b)"."""
    errors: List[Tuple[int, int, str]] = []
    if (
        (
            not isinstance(node.op, ast.Not)
            or not isinstance(node.operand, ast.Compare)
            or len(node.operand.ops) != 1
            or not isinstance(node.operand.ops[0], ast.LtE)
        )
        or isinstance(node.parent, ast.If)
        and is_exception_check(node.parent)
    ):
        return errors
    comparison = node.operand
    left = to_source(comparison.left)
    right = to_source(comparison.comparators[0])
    errors.append(
        (node.lineno, node.col_offset, SIM205.format(a=left, b=right))
    )
    return errors


def _get_sim206(node: UnaryOp) -> List[Tuple[int, int, str]]:
    """Get a list of all calls of the type "not (a > b)"."""
    errors: List[Tuple[int, int, str]] = []
    if (
        (
            not isinstance(node.op, ast.Not)
            or not isinstance(node.operand, ast.Compare)
            or len(node.operand.ops) != 1
            or not isinstance(node.operand.ops[0], ast.Gt)
        )
        or isinstance(node.parent, ast.If)
        and is_exception_check(node.parent)
    ):
        return errors
    comparison = node.operand
    left = to_source(comparison.left)
    right = to_source(comparison.comparators[0])
    errors.append(
        (node.lineno, node.col_offset, SIM206.format(a=left, b=right))
    )
    return errors


def _get_sim207(node: UnaryOp) -> List[Tuple[int, int, str]]:
    """Get a list of all calls of the type "not (a >= b)"."""
    errors: List[Tuple[int, int, str]] = []
    if (
        (
            not isinstance(node.op, ast.Not)
            or not isinstance(node.operand, ast.Compare)
            or len(node.operand.ops) != 1
            or not isinstance(node.operand.ops[0], ast.GtE)
        )
        or isinstance(node.parent, ast.If)
        and is_exception_check(node.parent)
    ):
        return errors
    comparison = node.operand
    left = to_source(comparison.left)
    right = to_source(comparison.comparators[0])
    errors.append(
        (node.lineno, node.col_offset, SIM207.format(a=left, b=right))
    )
    return errors


def _get_sim208(node: ast.UnaryOp) -> List[Tuple[int, int, str]]:
    """Get a list of all calls of the type "not (not a)"."""
    errors: List[Tuple[int, int, str]] = []
    if (
        not isinstance(node.op, ast.Not)
        or not isinstance(node.operand, ast.UnaryOp)
        or not isinstance(node.operand.op, ast.Not)
    ):
        return errors
    a = to_source(node.operand.operand)
    errors.append((node.lineno, node.col_offset, SIM208.format(a=a)))
    return errors


def _get_sim210(node: ast.IfExp) -> List[Tuple[int, int, str]]:
    """Get a list of all calls of the type "True if a else False"."""
    errors: List[Tuple[int, int, str]] = []
    if (
        not isinstance(node.body, BOOL_CONST_TYPES)
        or node.body.value is not True
        or not isinstance(node.orelse, BOOL_CONST_TYPES)
        or node.orelse.value is not False
    ):
        return errors
    cond = to_source(node.test)
    errors.append((node.lineno, node.col_offset, SIM210.format(cond=cond)))
    return errors


def _get_sim211(node: ast.IfExp) -> List[Tuple[int, int, str]]:
    """Get a list of all calls of the type "False if a else True"."""
    errors: List[Tuple[int, int, str]] = []
    if (
        not isinstance(node.body, BOOL_CONST_TYPES)
        or node.body.value is not False
        or not isinstance(node.orelse, BOOL_CONST_TYPES)
        or node.orelse.value is not True
    ):
        return errors
    cond = to_source(node.test)
    errors.append((node.lineno, node.col_offset, SIM211.format(cond=cond)))
    return errors


def is_same_expression(a: ast.expr, b: ast.expr) -> bool:
    """Check if two expressions are equal to each other."""
    if isinstance(a, ast.Name) and isinstance(b, ast.Name):
        return a.id == b.id
    else:
        return False


def _get_sim212(node: ast.IfExp) -> List[Tuple[int, int, str]]:
    """
    Get a list of all calls of the type "b if not a else a".

    IfExp(
        test=UnaryOp(
            op=Not(),
            operand=Name(id='a', ctx=Load()),
        ),
        body=Name(id='b', ctx=Load()),
        orelse=Name(id='a', ctx=Load()),
    )
    """
    errors: List[Tuple[int, int, str]] = []
    if not (
        isinstance(node.test, ast.UnaryOp)
        and isinstance(node.test.op, ast.Not)
        and is_same_expression(node.test.operand, node.orelse)
    ):
        return errors
    a = to_source(node.test.operand)
    b = to_source(node.body)
    errors.append((node.lineno, node.col_offset, SIM212.format(a=a, b=b)))
    return errors


def _get_sim220(node: ast.BoolOp) -> List[Tuple[int, int, str]]:
    """
    Get a list of all calls of the type "a and not a".

    BoolOp(
        op=And(),
        values=[
            Name(id='a', ctx=Load()),
            UnaryOp(
                op=Not(),
                operand=Name(id='a', ctx=Load()),
            ),
        ],
    )
    """
    errors: List[Tuple[int, int, str]] = []
    if not (isinstance(node.op, ast.And) and len(node.values) >= 2):
        return errors
    # We have a boolean And. Let's make sure there is two times the same
    # expression, but once with a "not"
    negated_expressions = []
    non_negated_expressions = []
    for exp in node.values:
        if isinstance(exp, ast.UnaryOp) and isinstance(exp.op, ast.Not):
            negated_expressions.append(exp.operand)
        else:
            non_negated_expressions.append(exp)
    if len(negated_expressions) == 0:
        return errors

    for negated_expression in negated_expressions:
        for non_negated_expression in non_negated_expressions:
            if is_same_expression(negated_expression, non_negated_expression):
                a = to_source(negated_expression)
                errors.append(
                    (node.lineno, node.col_offset, SIM220.format(a=a))
                )
                return errors
    return errors


def _get_sim221(node: ast.BoolOp) -> List[Tuple[int, int, str]]:
    """
    Get a list of all calls of the type "a or not a".

    BoolOp(
        op=Or(),
        values=[
            Name(id='a', ctx=Load()),
            UnaryOp(
                op=Not(),
                operand=Name(id='a', ctx=Load()),
            ),
        ],
    )
    """
    errors: List[Tuple[int, int, str]] = []
    if not (isinstance(node.op, ast.Or) and len(node.values) >= 2):
        return errors
    # We have a boolean OR. Let's make sure there is two times the same
    # expression, but once with a "not"
    negated_expressions = []
    non_negated_expressions = []
    for exp in node.values:
        if isinstance(exp, ast.UnaryOp) and isinstance(exp.op, ast.Not):
            negated_expressions.append(exp.operand)
        else:
            non_negated_expressions.append(exp)
    if len(negated_expressions) == 0:
        return errors

    for negated_expression in negated_expressions:
        for non_negated_expression in non_negated_expressions:
            if is_same_expression(negated_expression, non_negated_expression):
                a = to_source(negated_expression)
                errors.append(
                    (node.lineno, node.col_offset, SIM221.format(a=a))
                )
                return errors
    return errors


def _get_sim222(node: ast.BoolOp) -> List[Tuple[int, int, str]]:
    """
    Get a list of all calls of the type "... or True".

    BoolOp(
        op=Or(),
        values=[
            Name(id='a', ctx=Load()),
            UnaryOp(
                op=Not(),
                operand=Name(id='a', ctx=Load()),
            ),
        ],
    )
    """
    errors: List[Tuple[int, int, str]] = []
    if not (isinstance(node.op, ast.Or)):
        return errors

    for exp in node.values:
        if isinstance(exp, BOOL_CONST_TYPES) and exp.value is True:
            errors.append((node.lineno, node.col_offset, SIM222))
            return errors
    return errors


def _get_sim223(node: ast.BoolOp) -> List[Tuple[int, int, str]]:
    """
    Get a list of all calls of the type "... and False".

    BoolOp(
        op=And(),
        values=[
            Name(id='a', ctx=Load()),
            UnaryOp(
                op=Not(),
                operand=Name(id='a', ctx=Load()),
            ),
        ],
    )
    """
    errors: List[Tuple[int, int, str]] = []
    if not (isinstance(node.op, ast.And)):
        return errors

    for exp in node.values:
        if isinstance(exp, BOOL_CONST_TYPES) and exp.value is False:
            errors.append((node.lineno, node.col_offset, SIM223))
            return errors
    return errors


def _get_sim300(node: ast.Compare) -> List[Tuple[int, int, str]]:
    """
    Get a list of all Yoda conditions.

    Compare(
                left=Constant(value='Yoda', kind=None),
                ops=[Eq()],
                comparators=[Name(id='i_am', ctx=Load())],
            )
    """
    errors: List[Tuple[int, int, str]] = []
    if not (
        isinstance(node.left, AST_CONST_TYPES)
        and len(node.ops) == 1
        and isinstance(node.ops[0], ast.Eq)
    ):
        return errors

    left = to_source(node.left)
    right = to_source(node.comparators[0])
    errors.append(
        (node.lineno, node.col_offset, SIM300.format(left=left, right=right))
    )
    return errors


def _get_sim401(node: ast.If) -> List[Tuple[int, int, str]]:
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


def _get_sim901(node: ast.Call) -> List[Tuple[int, int, str]]:
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
            SIM901.format(actual=actual, expected=expected),
        )
    )
    return errors


def _get_sim904(node: ast.Assign) -> List[Tuple[int, int, str]]:
    """
    Assign values to dictionary directly at initialization.

    Example
    -------
    Code:
        # Bad
        a = { }
        a['b] = 'c'

        # Good
        a = {'b': 'c'}
    Bad AST:
        [
            Assign(
                targets=[Name(id='a', ctx=Store())],
                value=Dict(keys=[], values=[]),
                type_comment=None,
            ),
            Assign(
                targets=[
                    Subscript(
                        value=Name(id='a', ctx=Load()),
                        slice=Constant(value='b', kind=None),
                        ctx=Store(),
                    ),
                ],
                value=Constant(value='c', kind=None),
                type_comment=None,
            ),
        ]
    """
    errors: List[Tuple[int, int, str]] = []
    n2 = node.next_sibling  # type: ignore
    if not (
        isinstance(node.value, ast.Dict)
        and isinstance(n2, ast.Assign)
        and len(n2.targets) == 1
        and len(node.targets) == 1
        and isinstance(n2.targets[0], ast.Subscript)
        and isinstance(n2.targets[0].value, ast.Name)
        and isinstance(node.targets[0], ast.Name)
        and n2.targets[0].value.id == node.targets[0].id
    ):
        return errors

    dict_name = to_source(node.targets[0])
    # Capture cases where the assigned value uses another dictionary value
    if expression_uses_variable(n2.value, dict_name):
        return errors

    errors.append(
        (
            node.lineno,
            node.col_offset,
            SIM904.format(dict_name=dict_name),
        )
    )
    return errors


def expression_uses_variable(expr: ast.expr, var: str) -> bool:
    if var in to_source(expr):
        # This is WAY too broad, but it's better to have false-negatives
        # than false-positives
        return True
    return False


def _get_sim905(node: ast.Call) -> List[Tuple[int, int, str]]:
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
            SIM905.format(expected=expected, actual=actual),
        )
    )
    return errors


def _get_sim906(node: ast.Call) -> List[Tuple[int, int, str]]:
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
            SIM906.format(actual=actual, expected=expected),
        )
    )
    return errors


class Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: List[Tuple[int, int, str]] = []

    def visit_Assign(self, node: ast.Assign) -> Any:
        self.errors += _get_sim904(node)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> Any:
        self.errors += _get_sim115(Call(node))
        self.errors += _get_sim901(node)
        self.errors += _get_sim905(node)
        self.errors += _get_sim906(node)
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> Any:
        self.errors += _get_sim117(node)
        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> None:
        self.errors += _get_sim112(node)
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self.errors += _get_sim101(node)
        self.errors += _get_sim109(node)
        self.errors += _get_sim220(node)
        self.errors += _get_sim221(node)
        self.errors += _get_sim222(node)
        self.errors += _get_sim223(node)
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        self.errors += _get_sim102(node)
        self.errors += _get_sim103(node)
        self.errors += _get_sim106(node)
        self.errors += _get_sim108(node)
        self.errors += _get_sim114(node)
        self.errors += _get_sim116(node)
        self.errors += _get_sim401(node)
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self.errors += _get_sim104(node)
        self.errors += _get_sim110_sim111(node)
        self.errors += _get_sim113(node)
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        self.errors += _get_sim105(node)
        self.errors += _get_sim107(node)
        self.generic_visit(node)

    def visit_UnaryOp(self, node_v: ast.UnaryOp) -> None:
        node = UnaryOp(node_v)
        self.errors += _get_sim201(node)
        self.errors += _get_sim202(node)
        self.errors += _get_sim203(node)
        self.errors += _get_sim204(node)
        self.errors += _get_sim205(node)
        self.errors += _get_sim206(node)
        self.errors += _get_sim207(node)
        self.errors += _get_sim208(node)
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:
        self.errors += _get_sim210(node)
        self.errors += _get_sim211(node)
        self.errors += _get_sim212(node)
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> None:
        self.errors += _get_sim118(node)
        self.errors += _get_sim300(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.errors += _get_sim119(node)
        self.errors += _get_sim120(node)
        self.generic_visit(node)


class Plugin:
    name = __name__
    version = importlib_metadata.version(__name__)  # type: ignore

    def __init__(self, tree: ast.AST):
        self._tree = tree

    def run(self) -> Generator[Tuple[int, int, str, Type[Any]], None, None]:
        visitor = Visitor()

        # Add parent
        add_meta(self._tree)
        visitor.visit(self._tree)

        for line, col, msg in visitor.errors:
            yield line, col, msg, type(self)


def add_meta(root: ast.AST, level: int = 0) -> None:
    previous_sibling = None
    for node in ast.iter_child_nodes(root):
        if level == 0:
            node.parent = None  # type: ignore
        node.previous_sibling = previous_sibling  # type: ignore
        node.next_sibling = None  # type: ignore
        if previous_sibling:
            node.previous_sibling.next_sibling = node  # type: ignore
        previous_sibling = node
        for child in ast.iter_child_nodes(node):
            child.parent = node  # type: ignore
        add_meta(node, level=level + 1)
