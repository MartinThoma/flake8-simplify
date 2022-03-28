# First party
from tests import _results


def test_sim201():
    ret = _results("not a == b")
    assert ret == {"1:0 SIM201 Use 'a != b' instead of 'not a == b'"}


def test_sim201_not_in_exception_check():
    ret = _results(
        """if not a == b:
    raise ValueError()"""
    )
    assert ret == set()


def test_sim202_base():
    ret = _results("not a != b")
    assert ret == {("1:0 SIM202 Use 'a == b' instead of 'not a != b'")}


def test_sim203_base():
    ret = _results("not a in b")
    assert ret == {("1:0 SIM203 Use 'a not in b' instead of 'not a in b'")}


def test_sim208_base():
    ret = _results("not (not a)")
    assert ret == {("1:0 SIM208 Use 'a' instead of 'not (not a)'")}


def test_sim210_base():
    ret = _results("True if True else False")
    assert ret == {
        ("1:0 SIM210 Use 'bool(True)' instead of 'True if True else False'")
    }


def test_sim211_base():
    ret = _results("False if True else True")
    assert ret == {
        ("1:0 SIM211 Use 'not True' instead of 'False if True else True'")
    }


def test_sim212_base():
    ret = _results("b if not a else a")
    assert ret == {
        ("1:0 SIM212 Use 'a if a else b' instead of 'b if not a else a'")
    }


def test_sim220_base():
    ret = _results("a and not a")
    assert ret == {("1:0 SIM220 Use 'False' instead of 'a and not a'")}


def test_sim221_base():
    ret = _results("a or not a")
    assert ret == {("1:0 SIM221 Use 'True' instead of 'a or not a'")}


def test_sim222_base():
    ret = _results("a or True")
    assert ret == {("1:0 SIM222 Use 'True' instead of '... or True'")}


def test_sim223_base():
    ret = _results("a and False")
    assert ret == {("1:0 SIM223 Use 'False' instead of '... and False'")}
