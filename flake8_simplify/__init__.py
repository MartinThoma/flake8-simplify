import ast
import importlib.metadata as importlib_metadata
import logging
from collections.abc import Generator
from typing import Any

from flake8_simplify.registry import get_rules

logger = logging.getLogger(__name__)


class Visitor(ast.NodeVisitor):
    """Run every rule registered for a node type on each node of that type."""

    def __init__(self) -> None:
        self.errors: list[tuple[int, int, str]] = []
        self._rules = get_rules()

    def visit(self, node: ast.AST) -> Any:
        for rule in self._rules.get(type(node), ()):
            checked_node = rule.wrapper(node) if rule.wrapper else node
            for violation in rule.check(checked_node):
                self.errors.append(
                    (
                        violation.node.lineno,
                        violation.node.col_offset,
                        f"{rule.code} {violation.message}",
                    )
                )
        self.generic_visit(node)


class Plugin:
    name = __name__
    version = importlib_metadata.version(__name__)  # type: ignore

    def __init__(self, tree: ast.AST):
        self._tree = tree

    def run(self) -> Generator[tuple[int, int, str, type[Any]], None, None]:
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
