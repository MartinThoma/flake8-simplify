# Core Library
import ast
from typing import Set

# First party
from flake8_simplify import Plugin


def _results(code: str) -> Set[str]:
    """Apply the plugin to the given code."""
    tree = ast.parse(code)
    plugin = Plugin(tree)
    return {f"{line}:{col} {msg}" for line, col, msg, _ in plugin.run()}


def test_trivial_case():
    """Check the plugins output for no code."""
    assert _results("") == set()


def test_plugin_version():
    assert isinstance(Plugin.version, str)
    assert "." in Plugin.version


def test_plugin_name():
    assert isinstance(Plugin.name, str)


def test_single_isinstance():
    ret = _results("isinstance(a, int) or foo")
    assert ret == set()


def test_multiple_isinstance_multiple_lines():
    ret = _results(
        "isinstance(a, int) or isinstance(a, float)\n"
        "isinstance(b, bool) or isinstance(b, str)"
    )
    assert ret == {
        (
            "1:0 SIM101 Multiple isinstance-calls which can be merged "
            "into a single call for variable 'a'"
        ),
        (
            "2:0 SIM101 Multiple isinstance-calls which can be merged "
            "into a single call for variable 'b'"
        ),
    }


def test_first_wrong_then_multiple_isinstance():
    ret = _results(
        "foo(a, b, c) or bar(a, b)\nisinstance(b, bool) or isinstance(b, str)"
    )
    assert ret == {
        (
            "2:0 SIM101 Multiple isinstance-calls which can be merged "
            "into a single call for variable 'b'"
        ),
    }


def test_multiple_isinstance_and():
    ret = _results("isinstance(b, bool) and isinstance(b, str)")
    assert ret == set()


def test_multiple_other_function():
    ret = _results("isfoo(a, int) or isfoo(a, float)")
    assert ret == set()


def test_unary_not_equality():
    ret = _results("not a == b")
    assert ret == {("1:0 SIM201 Used 'not a == b' instead of 'a != b'")}


def test_sim_202_base():
    ret = _results("not a != b")
    assert ret == {("1:0 SIM202 Used 'not a != b' instead of 'a == b'")}
