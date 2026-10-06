"""
Registry of all rules.

A rule is a generator function which receives a node of the given type and
yields a ``Violation`` for every problem it finds. It registers itself with
the ``rule`` decorator; modules in ``flake8_simplify/rules/`` are discovered
automatically, so adding a rule never requires touching any other file.

    @rule("SIM120", ast.ClassDef)
    def get_sim120(node: ast.ClassDef) -> Iterator[Violation]:
        if ...:
            yield Violation(node, "Use 'class Foo:' ...")
"""

import ast
import importlib
import pkgutil
from collections import defaultdict
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any, NamedTuple


class Violation(NamedTuple):
    """A problem found by a rule, reported at the position of ``node``."""

    node: ast.expr | ast.stmt
    message: str


@dataclass(frozen=True)
class Rule:
    code: str
    node_type: type[ast.AST]
    check: Callable[[Any], Iterator[Violation]]


_RULES: list[Rule] = []


def rule(
    code: str,
    node_type: type[ast.AST],
) -> Callable[
    [Callable[[Any], Iterator[Violation]]],
    Callable[[Any], Iterator[Violation]],
]:
    """Register a function as the check for ``code`` on ``node_type`` nodes."""

    def register(
        check: Callable[[Any], Iterator[Violation]],
    ) -> Callable[[Any], Iterator[Violation]]:
        _RULES.append(Rule(code, node_type, check))
        return check

    return register


def get_rules() -> dict[type[ast.AST], list[Rule]]:
    """Get all rules, grouped by the type of node they check."""
    from flake8_simplify import rules

    for module in pkgutil.iter_modules(rules.__path__):
        importlib.import_module(f"{rules.__name__}.{module.name}")

    by_node_type: dict[type[ast.AST], list[Rule]] = defaultdict(list)
    for registered in _RULES:
        by_node_type[registered.node_type].append(registered)
    return by_node_type
