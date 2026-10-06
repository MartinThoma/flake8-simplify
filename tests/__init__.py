import ast
import textwrap

from flake8_simplify import Plugin


def _results(code: str) -> set[str]:
    """Apply the plugin to the given code."""
    tree = ast.parse(code)
    plugin = Plugin(tree)
    return {f"{line}:{col} {msg}" for line, col, msg, _ in plugin.run()}


def _rule_hits(code: str, rule: str) -> set[str]:
    """Apply the plugin and keep only the results of the given rule."""
    return {r for r in _results(code) if f" {rule} " in r}


def snippet(snippet: str) -> str:
    """Let test snippets be indented like the surrounding test code."""
    return textwrap.dedent(snippet).strip("\n")
