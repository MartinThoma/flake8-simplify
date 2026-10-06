import ast

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


def test_fine_code():
    ret = _results("- ( a+ b)")
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
