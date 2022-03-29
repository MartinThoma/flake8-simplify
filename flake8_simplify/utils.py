# Core Library
import ast
import itertools
from collections import defaultdict
from typing import DefaultDict, List, Tuple, Union

# Third party
import astor


# The following types were created to help mypy understand that there is a
# "parent" attribute on the ast.AST nodes.
class UnaryOp(ast.UnaryOp):
    def __init__(self, orig: ast.UnaryOp) -> None:
        self.op = orig.op
        self.operand = orig.operand
        # For all ast.*:
        self.lineno = orig.lineno
        self.col_offset = orig.col_offset
        self.parent: ast.Expr = orig.parent  # type: ignore


class Call(ast.Call):
    """For mypy so that it knows that added attributes exist."""

    def __init__(self, orig: ast.Call) -> None:
        self.func = orig.func
        self.args = orig.args
        self.keywords = orig.keywords
        # For all ast.*:
        self.lineno = orig.lineno
        self.col_offset = orig.col_offset

        # Added attributes
        self.parent: ast.Expr = orig.parent  # type: ignore


class If(ast.If):
    """For mypy so that it knows that added attributes exist."""

    def __init__(self, orig: ast.If) -> None:
        self.test = orig.test
        self.body = orig.body
        self.orelse = orig.orelse

        # For all ast.*:
        self.lineno = orig.lineno
        self.col_offset = orig.col_offset

        # Added attributes
        self.parent: ast.Expr = orig.parent  # type: ignore


class For(ast.For):
    """For mypy so that it knows that added attributes exist."""

    def __init__(self, orig: ast.For) -> None:
        self.target = orig.target
        self.iter = orig.iter
        self.body = orig.body
        self.orelse = orig.orelse
        # For all ast.*:
        self.lineno = orig.lineno
        self.col_offset = orig.col_offset

        # Added attributes
        self.parent: ast.AST = orig.parent  # type: ignore
        self.previous_sibling = orig.previous_sibling  # type: ignore


class Assign(ast.Assign):
    """For mypy so that it knows that added attributes exist."""

    def __init__(self, orig: ast.Assign) -> None:
        self.targets = orig.targets
        self.value = orig.value
        # For all ast.*:
        self.orig = orig
        self.lineno = orig.lineno
        self.col_offset = orig.col_offset

        # Added attributes
        self.parent: ast.AST = orig.parent  # type: ignore
        self.previous_sibling = orig.previous_sibling  # type: ignore


def to_source(
    node: Union[None, ast.expr, ast.Expr, ast.withitem, ast.slice, ast.Assign]
) -> str:
    if node is None:
        return "None"
    source: str = astor.to_source(node).strip()
    source = strip_parenthesis(source)
    source = strip_triple_quotes(source)
    source = use_double_quotes(source)
    return source


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


def is_constant_increase(expr: ast.AugAssign) -> bool:
    return isinstance(expr.op, ast.Add) and (
        (isinstance(expr.value, ast.Constant) and expr.value.value == 1)
        or (isinstance(expr.value, ast.Num) and expr.value.n == 1)
    )


def is_exception_check(node: ast.If) -> bool:
    if len(node.body) == 1 and isinstance(node.body[0], ast.Raise):
        return True
    return False


def is_same_expression(a: ast.expr, b: ast.expr) -> bool:
    """Check if two expressions are equal to each other."""
    if isinstance(a, ast.Name) and isinstance(b, ast.Name):
        return a.id == b.id
    else:
        return False


def expression_uses_variable(expr: ast.expr, var: str) -> bool:
    if var in to_source(expr):
        # This is WAY too broad, but it's better to have false-negatives
        # than false-positives
        return True
    return False


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


def body_contains_continue(stmts: List[ast.stmt]) -> bool:
    return any(
        isinstance(stmt, ast.Continue)
        or (isinstance(stmt, ast.If) and body_contains_continue(stmt.body))
        for stmt in stmts
    )
