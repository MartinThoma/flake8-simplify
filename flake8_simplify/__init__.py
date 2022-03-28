# Core Library
import ast
import logging
import sys
from typing import Any, Generator, List, Tuple, Type

# First party
from flake8_simplify.rules.ast_assign import get_sim904, get_sim909
from flake8_simplify.rules.ast_bool_op import (
    get_sim101,
    get_sim109,
    get_sim220,
    get_sim221,
    get_sim222,
    get_sim223,
)
from flake8_simplify.rules.ast_call import (
    get_sim115,
    get_sim901,
    get_sim902,
    get_sim903,
    get_sim905,
    get_sim906,
)
from flake8_simplify.rules.ast_classdef import get_sim120
from flake8_simplify.rules.ast_compare import get_sim118, get_sim300
from flake8_simplify.rules.ast_expr import get_sim112
from flake8_simplify.rules.ast_for import (
    get_sim104,
    get_sim110_sim111,
    get_sim113,
)
from flake8_simplify.rules.ast_if import (
    get_sim102,
    get_sim103,
    get_sim108,
    get_sim114,
    get_sim116,
    get_sim401,
    get_sim908,
)
from flake8_simplify.rules.ast_ifexp import get_sim210, get_sim211, get_sim212
from flake8_simplify.rules.ast_subscript import get_sim907
from flake8_simplify.rules.ast_try import get_sim105, get_sim107
from flake8_simplify.rules.ast_unary_op import (
    get_sim201,
    get_sim202,
    get_sim203,
    get_sim208,
)
from flake8_simplify.rules.ast_with import get_sim117
from flake8_simplify.utils import Call, For, If, UnaryOp

logger = logging.getLogger(__name__)


if sys.version_info < (3, 8):  # pragma: no cover (<PY38)
    # Third party
    import importlib_metadata
else:  # pragma: no cover (PY38+)
    # Core Library
    import importlib.metadata as importlib_metadata


class Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: List[Tuple[int, int, str]] = []

    def visit_Assign(self, node: ast.Assign) -> Any:
        self.errors += get_sim904(node)
        self.errors += get_sim909(node)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> Any:
        self.errors += get_sim115(Call(node))
        self.errors += get_sim901(node)
        self.errors += get_sim902(Call(node))
        self.errors += get_sim903(Call(node))
        self.errors += get_sim905(node)
        self.errors += get_sim906(node)
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> Any:
        self.errors += get_sim117(node)
        self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr) -> None:
        self.errors += get_sim112(node)
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self.errors += get_sim101(node)
        self.errors += get_sim109(node)
        self.errors += get_sim220(node)
        self.errors += get_sim221(node)
        self.errors += get_sim222(node)
        self.errors += get_sim223(node)
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        self.errors += get_sim102(node)
        self.errors += get_sim103(node)
        self.errors += get_sim108(If(node))
        self.errors += get_sim114(node)
        self.errors += get_sim116(node)
        self.errors += get_sim908(node)
        self.errors += get_sim401(node)
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self.errors += get_sim104(node)
        self.errors += get_sim110_sim111(node)
        self.errors += get_sim113(For(node))
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        self.errors += get_sim907(node)
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        self.errors += get_sim105(node)
        self.errors += get_sim107(node)
        self.generic_visit(node)

    def visit_UnaryOp(self, node_v: ast.UnaryOp) -> None:
        node = UnaryOp(node_v)
        self.errors += get_sim201(node)
        self.errors += get_sim202(node)
        self.errors += get_sim203(node)
        self.errors += get_sim208(node)
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:
        self.errors += get_sim210(node)
        self.errors += get_sim211(node)
        self.errors += get_sim212(node)
        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> None:
        self.errors += get_sim118(node)
        self.errors += get_sim300(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.errors += get_sim120(node)
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
            node.parent = root  # type: ignore
        node.previous_sibling = previous_sibling  # type: ignore
        node.next_sibling = None  # type: ignore
        if previous_sibling:
            node.previous_sibling.next_sibling = node  # type: ignore
        previous_sibling = node
        for child in ast.iter_child_nodes(node):
            child.parent = node  # type: ignore
        add_meta(node, level=level + 1)
