# Core Library
import ast
from typing import Set

# First party
from flake8_simplify import Plugin


def _results(s: str) -> Set[str]:
    tree = ast.parse(s)
    plugin = Plugin(tree)
    return {f"{line}:{col} {msg}" for line, col, msg, _ in plugin.run()}


def test_trivial_case():
    assert _results("") == set()


def test_multiple_isinstance():
    ret = _results("isinstance(a, int) or isinstance(a, float)")
    assert ret == {
        (
            "1:0 SIM101 Multiple isinstance-calls which can be merged "
            "into a single call for variable 'a'"
        )
    }


def test_multiple_other_function():
    ret = _results("isfoo(a, int) or isfoo(a, float)")
    assert ret == set()
