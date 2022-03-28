# First party
from tests import _results


def test_sim300_string():
    ret = _results("'Yoda' == i_am")
    assert ret == {
        (
            "1:0 SIM300 Use 'i_am == \"Yoda\"' "
            "instead of '\"Yoda\" == i_am' (Yoda-conditions)"
        )
    }


def test_sim300_int():
    ret = _results("42 == age")
    assert ret == {
        "1:0 SIM300 Use 'age == 42' instead of '42 == age' (Yoda-conditions)"
    }
