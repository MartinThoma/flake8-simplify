# Core Library
import ast
import sys
from collections import defaultdict
from typing import Any, DefaultDict, Dict, Generator, List, Tuple, Type, Union

# Third party
import astor

if sys.version_info < (3, 8):  # pragma: no cover (<PY38)
    # Third party
    import importlib_metadata
else:  # pragma: no cover (PY38+)
    # Core Library
    import importlib.metadata as importlib_metadata

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

# ast.Constant in Python 3.8, ast.NameConstant in Python 3.6 and 3.7
BOOL_CONST_TYPES = (ast.Constant, ast.NameConstant)
AST_CONST_TYPES = (ast.Constant, ast.NameConstant, ast.Str, ast.Num)
STR_TYPES = (ast.Constant, ast.Str)


def strip_parenthesis(string: str) -> str:
    if string[0] == "(" and string[-1] == ")":
        return string[1:-1]
    return string


def strip_triple_quotes(string: str) -> str:
    if not (
        string.startswith('"""')
        and string.endswith('"""')
        and '"' not in string[3:-3]
    ):
        return string
    string = string[3:-3]
    if len(string) == 0:
        string = '""'
    return string


def to_source(node: Union[ast.expr, ast.Expr]) -> str:
    source = astor.to_source(node).strip()
    source = strip_parenthesis(source)
    source = strip_triple_quotes(source)
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
    ids = []  # (name, compared_to)
    for eq in equalities:
        if isinstance(eq.left, ast.Name):
            ids.append((eq.left, eq.comparators[0]))
        if len(eq.comparators) == 1 and isinstance(
            eq.comparators[0], ast.Name
        ):
            ids.append((eq.comparators[0], eq.left))

    id2count: Dict[str, List[ast.expr]] = {}
    for identifier, compared_to in ids:
        if identifier.id not in id2count:
            id2count[identifier.id] = []
        id2count[identifier.id].append(compared_to)
    for value, values in id2count.items():
        if len(values) == 1:
            continue
        errors.append(
            (
                node.lineno,
                node.col_offset,
                SIM109.format(
                    or_op=to_source(node),
                    value=value,
                    values=to_source(ast.List(elts=values)),
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
        and isinstance(node.value.slice, ast.Index)
        and isinstance(node.value.slice.value, STR_TYPES)
    )
    if is_index_call:
        subscript = node.value
        assert isinstance(subscript, ast.Subscript)
        slice_ = subscript.slice
        assert isinstance(slice_, ast.Index)
        string_part = slice_.value
        assert isinstance(string_part, STR_TYPES)
        if isinstance(string_part, ast.Str):
            env_name = string_part.s  # Python 3.6 / 3.7 fallback
        else:
            env_name = string_part.value
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
        assert isinstance(call, ast.Call)
        string_part = call.args[0]
        assert isinstance(string_part, STR_TYPES)
        if isinstance(string_part, ast.Str):
            env_name = string_part.s  # Python 3.6 / 3.7 fallback
        else:
            env_name = string_part.value
        # Check if this has a change
        has_change = env_name != env_name.upper()
    if not (is_index_call or is_get_call) or not has_change:
        return errors
    if is_index_call:
        original = to_source(node)
        expected = f'os.environ["{env_name.upper()}"]'
    elif is_get_call:
        original = to_source(node)
        if len(node.value.args) == 1:  # type: ignore
            expected = f'os.environ.get("{env_name.upper()}")'
        else:
            assert isinstance(node.value, ast.Call)
            default_value = to_source(node.value.args[1])
            expected = (
                f'os.environ.get("{env_name.upper()}", "{default_value}")'
            )
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


def _get_sim201(node: ast.UnaryOp) -> List[Tuple[int, int, str]]:
    """
    Get a list of all calls where an unary 'not' is used for an equality.
    """
    errors: List[Tuple[int, int, str]] = []
    if (
        not isinstance(node.op, ast.Not)
        or not isinstance(node.operand, ast.Compare)
        or len(node.operand.ops) != 1
        or not isinstance(node.operand.ops[0], ast.Eq)
    ):
        return errors
    comparison = node.operand
    left = to_source(comparison.left)
    right = to_source(comparison.comparators[0])
    errors.append(
        (node.lineno, node.col_offset, SIM201.format(left=left, right=right))
    )

    return errors


def _get_sim202(node: ast.UnaryOp) -> List[Tuple[int, int, str]]:
    """
    Get a list of all calls where an unary 'not' is used for an quality.
    """
    errors: List[Tuple[int, int, str]] = []
    if (
        not isinstance(node.op, ast.Not)
        or not isinstance(node.operand, ast.Compare)
        or len(node.operand.ops) != 1
        or not isinstance(node.operand.ops[0], ast.NotEq)
    ):
        return errors
    comparison = node.operand
    left = to_source(comparison.left)
    right = to_source(comparison.comparators[0])
    errors.append(
        (node.lineno, node.col_offset, SIM202.format(left=left, right=right))
    )

    return errors


def _get_sim203(node: ast.UnaryOp) -> List[Tuple[int, int, str]]:
    """
    Get a list of all calls where an unary 'not' is used for an in-check.
    """
    errors: List[Tuple[int, int, str]] = []
    if (
        not isinstance(node.op, ast.Not)
        or not isinstance(node.operand, ast.Compare)
        or len(node.operand.ops) != 1
        or not isinstance(node.operand.ops[0], ast.In)
    ):
        return errors
    comparison = node.operand
    left = to_source(comparison.left)
    right = to_source(comparison.comparators[0])
    errors.append(
        (node.lineno, node.col_offset, SIM203.format(a=left, b=right))
    )

    return errors


def _get_sim204(node: ast.UnaryOp) -> List[Tuple[int, int, str]]:
    """Get a list of all calls of the type "not (a < b)"."""
    errors: List[Tuple[int, int, str]] = []
    if (
        not isinstance(node.op, ast.Not)
        or not isinstance(node.operand, ast.Compare)
        or len(node.operand.ops) != 1
        or not isinstance(node.operand.ops[0], ast.Lt)
    ):
        return errors
    comparison = node.operand
    left = to_source(comparison.left)
    right = to_source(comparison.comparators[0])
    errors.append(
        (node.lineno, node.col_offset, SIM204.format(a=left, b=right))
    )
    return errors


def _get_sim205(node: ast.UnaryOp) -> List[Tuple[int, int, str]]:
    """Get a list of all calls of the type "not (a <= b)"."""
    errors: List[Tuple[int, int, str]] = []
    if (
        not isinstance(node.op, ast.Not)
        or not isinstance(node.operand, ast.Compare)
        or len(node.operand.ops) != 1
        or not isinstance(node.operand.ops[0], ast.LtE)
    ):
        return errors
    comparison = node.operand
    left = to_source(comparison.left)
    right = to_source(comparison.comparators[0])
    errors.append(
        (node.lineno, node.col_offset, SIM205.format(a=left, b=right))
    )
    return errors


def _get_sim206(node: ast.UnaryOp) -> List[Tuple[int, int, str]]:
    """Get a list of all calls of the type "not (a > b)"."""
    errors: List[Tuple[int, int, str]] = []
    if (
        not isinstance(node.op, ast.Not)
        or not isinstance(node.operand, ast.Compare)
        or len(node.operand.ops) != 1
        or not isinstance(node.operand.ops[0], ast.Gt)
    ):
        return errors
    comparison = node.operand
    left = to_source(comparison.left)
    right = to_source(comparison.comparators[0])
    errors.append(
        (node.lineno, node.col_offset, SIM206.format(a=left, b=right))
    )
    return errors


def _get_sim207(node: ast.UnaryOp) -> List[Tuple[int, int, str]]:
    """Get a list of all calls of the type "not (a >= b)"."""
    errors: List[Tuple[int, int, str]] = []
    if (
        not isinstance(node.op, ast.Not)
        or not isinstance(node.operand, ast.Compare)
        or len(node.operand.ops) != 1
        or not isinstance(node.operand.ops[0], ast.GtE)
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
    is_py37_str = isinstance(node.left, ast.Str)
    is_py38_str = isinstance(node.left, ast.Constant) and isinstance(
        node.left.value, str
    )
    if is_py38_str or is_py37_str:
        left = f'"{left}"'
    right = to_source(node.comparators[0])
    errors.append(
        (node.lineno, node.col_offset, SIM300.format(left=left, right=right))
    )
    return errors


class Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: List[Tuple[int, int, str]] = []

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
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self.errors += _get_sim104(node)
        self.errors += _get_sim110_sim111(node)
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        self.errors += _get_sim105(node)
        self.errors += _get_sim107(node)
        self.generic_visit(node)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
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
        self.errors += _get_sim300(node)
        self.generic_visit(node)


class Plugin:
    name = __name__
    version = importlib_metadata.version(__name__)

    def __init__(self, tree: ast.AST):
        self._tree = tree

    def run(self) -> Generator[Tuple[int, int, str, Type[Any]], None, None]:
        visitor = Visitor()
        visitor.visit(self._tree)

        for line, col, msg in visitor.errors:
            yield line, col, msg, type(self)
