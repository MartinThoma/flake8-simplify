import ast

from flake8_simplify import Plugin


def _results(code: str) -> set[str]:
    """Apply the plugin to the given code."""
    tree = ast.parse(code)
    plugin = Plugin(tree)
    return {f"{line}:{col} {msg}" for line, col, msg, _ in plugin.run()}
