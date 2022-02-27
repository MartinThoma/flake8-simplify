# Core Library
import ast

# First party
from flake8_simplify import Plugin
from flake8_simplify.utils import get_if_body_pairs
from tests import _results


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


def test_get_if_body_pairs():
    ret = ast.parse(
        """if a == b:
    foo(a)
    foo(b)"""
    ).body[0]
    assert isinstance(ret, ast.If)
    result = get_if_body_pairs(ret)
    assert len(result) == 1
    comp = result[0][0]
    assert isinstance(comp, ast.Compare)
    assert isinstance(result[0][1], list)
    assert isinstance(comp.left, ast.Name)
    assert len(comp.ops) == 1
    assert isinstance(comp.ops[0], ast.Eq)
    assert len(comp.comparators) == 1
    assert isinstance(comp.comparators[0], ast.Name)
    assert comp.left.id == "a"
    assert comp.comparators[0].id == "b"


def test_get_if_body_pairs_2():
    ret = ast.parse(
        """if a == b:
    foo(a)
    foo(b)
elif a == b:
    foo(c)"""
    ).body[0]
    assert isinstance(ret, ast.If)
    result = get_if_body_pairs(ret)
    assert len(result) == 2
    comp = result[0][0]
    assert isinstance(comp, ast.Compare)
    assert isinstance(result[0][1], list)
    assert isinstance(comp.left, ast.Name)
    assert len(comp.ops) == 1
    assert isinstance(comp.ops[0], ast.Eq)
    assert len(comp.comparators) == 1
    assert isinstance(comp.comparators[0], ast.Name)
    assert comp.left.id == "a"
    assert comp.comparators[0].id == "b"
