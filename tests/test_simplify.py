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


def test_fine_code():
    ret = _results("- ( a+ b)")
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


def test_sim_102_base():
    ret = _results(
        """if a:
    if b:
        c"""
    )
    assert ret == {
        (
            "1:0 SIM102: Use a single if-statement instead of "
            "nested if-statements"
        )
    }


def test_sim_102_not_active1():
    ret = _results(
        """if a:
    if b:
        c
    else:
        d"""
    )
    assert ret == set()


def test_sim_102_not_active2():
    ret = _results(
        """if a:
    d
    if b:
        c"""
    )
    assert ret == set()


def test_unary_not_equality():
    ret = _results("not a == b")
    assert ret == {("1:0 SIM201 Use 'a != b' instead of 'not a == b'")}


def test_sim_202_base():
    ret = _results("not a != b")
    assert ret == {("1:0 SIM202 Use 'a == b' instead of 'not a != b'")}


def test_sim_203_base():
    ret = _results("not a in b")
    assert ret == {("1:0 SIM203 Use 'a not in b' instead of 'not a in b'")}


def test_sim_204_base():
    ret = _results("not a < b")
    assert ret == {("1:0 SIM204 Use 'a >= b' instead of 'not (a < b)'")}


def test_sim_205_base():
    ret = _results("not a <= b")
    assert ret == {("1:0 SIM205 Use 'a > b' instead of 'not (a <= b)'")}


def test_sim_206_base():
    ret = _results("not a > b")
    assert ret == {("1:0 SIM206 Use 'a <= b' instead of 'not (a > b)'")}


def test_sim_207_base():
    ret = _results("not a >= b")
    assert ret == {("1:0 SIM207 Use 'a < b' instead of 'not (a >= b)'")}


def test_sim_208_base():
    ret = _results("not (not a)")
    assert ret == {("1:0 SIM208 Use 'a' instead of 'not (not a)'")}
