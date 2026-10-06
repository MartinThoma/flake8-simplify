import ast
import itertools
from collections import defaultdict


def add_meta(root: ast.AST) -> None:
    """
    Link every node to its parent and its siblings.

    Siblings are linked across all fields of the parent, so the last
    statement of ``body`` has the first statement of ``orelse`` as next
    sibling. Use ``get_parent`` / ``get_previous_sibling`` /
    ``get_next_sibling`` to read the links.
    """
    for parent in ast.walk(root):
        previous: ast.AST | None = None
        for child in ast.iter_child_nodes(parent):
            setattr(child, "parent", parent)  # noqa: B010
            setattr(child, "previous_sibling", previous)  # noqa: B010
            setattr(child, "next_sibling", None)  # noqa: B010
            if previous is not None:
                setattr(previous, "next_sibling", child)  # noqa: B010
            previous = child


def get_parent(node: ast.AST) -> ast.AST | None:
    return getattr(node, "parent", None)  # type: ignore[no-any-return]


def get_previous_sibling(node: ast.AST) -> ast.AST | None:
    return getattr(node, "previous_sibling", None)  # type: ignore[no-any-return]


def get_next_sibling(node: ast.AST) -> ast.AST | None:
    return getattr(node, "next_sibling", None)  # type: ignore[no-any-return]


def in_same_block(first: ast.AST, second: ast.AST) -> bool:
    """
    Check that both statements are part of the same statement list.

    Siblings are linked across the fields of a node, so the last statement of
    ``body`` has the first statement of ``orelse`` as next sibling.
    """
    parent = get_parent(first)
    if parent is None:
        return True
    for _, value in ast.iter_fields(parent):
        if isinstance(value, list) and first in value:
            return second in value
    return True


def get_returned_bool(body: list[ast.stmt]) -> bool | None:
    """Get the value if the body is just ``return True`` / ``return False``."""
    if (
        len(body) == 1
        and isinstance(body[0], ast.Return)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, bool)
    ):
        return body[0].value.value
    return None


def negate_source(expr: ast.expr) -> str:
    """Get the source code of ``not expr``, with parentheses if needed."""
    if isinstance(expr, ast.UnaryOp) and isinstance(expr.op, ast.Not):
        return to_source(expr.operand)
    # These bind weaker than "not"
    if isinstance(expr, (ast.BoolOp, ast.IfExp, ast.Lambda, ast.NamedExpr)):
        return f"not ({to_source(expr)})"
    return f"not {to_source(expr)}"


def to_source(
    node: None | ast.expr | ast.Expr | ast.withitem | ast.slice | ast.Assign,
) -> str:
    if node is None:
        return "None"
    source: str = ast.unparse(node).strip()
    # Only string literals: an expression like 'a' <= x <= 'z' also starts
    # and ends with a quote, but must not be changed
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        source = strip_triple_quotes(source)
        source = use_double_quotes(source)
    return source


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
        return f'"""{string[len(quotes) : -len(quotes)]}"""'
    if len(string) >= 2 and string[0] == "'" and string[-1] == "'":
        return f'"{string[1:-1]}"'
    return string


def is_body_same(body1: list[ast.stmt], body2: list[ast.stmt]) -> bool:
    """Check if two lists of expressions are equivalent."""
    if len(body1) != len(body2):
        return False
    for a, b in zip(body1, body2, strict=True):
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
        return all(itertools.starmap(is_stmt_equal, zip(a, b, strict=True)))
    else:
        return a == b


def get_if_body_pairs(node: ast.If) -> list[tuple[ast.expr, list[ast.stmt]]]:
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
    return (
        isinstance(expr.op, ast.Add)
        and isinstance(expr.value, ast.Constant)
        and isinstance(expr.value.value, (int, float, complex))
        and expr.value.value == 1
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


def _get_duplicated_isinstance_call_by_node(node: ast.BoolOp) -> list[str]:
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
    counter: defaultdict[str, int] = defaultdict(int)

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


def body_contains_continue(stmts: list[ast.stmt]) -> bool:
    return any(
        isinstance(stmt, ast.Continue)
        or (isinstance(stmt, ast.If) and body_contains_continue(stmt.body))
        for stmt in stmts
    )
