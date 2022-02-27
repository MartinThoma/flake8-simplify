# First party
from tests import _results


def test_sim401_if_else():
    ret = _results(
        """if key in a_dict:
    value = a_dict[key]
else:
    value = 'default'"""
    )
    assert ret == {
        """1:0 SIM401 Use 'value = a_dict.get(key, "default")' """
        """instead of an if-block"""
    }


def test_sim401_negated_if_else():
    ret = _results(
        """if key not in a_dict:
    value = 'default'
else:
    value = a_dict[key] """
    )
    assert (
        """1:0 SIM401 Use 'value = a_dict.get(key, "default")' """
        """instead of an if-block""" in ret
    )


def test_sim401_prefix_negated_if_else():
    ret = _results(
        """if not key in a_dict:
    value = 'default'
else:
    value = a_dict[key] """
    )
    assert (
        """1:3 SIM401 Use 'value = a_dict.get(key, "default")' """
        """instead of an if-block""" in ret
    ) or (
        "1:3 SIM203 Use 'key not in a_dict' instead of 'not key in a_dict'"
        in ret
    )


def test_sim401_false_positive():
    ret = _results(
        """if "foo" in some_dict["a"]:
    some_dict["b"] = some_dict["a"]["foo"]
else:
    some_dict["a"]["foo"] = some_dict["b"]"""
    )
    for el in ret:
        assert "SIM401" not in el


def test_sim401_positive_msg_issue84_example1():
    """
    This is a regression test for the SIM401 message.

    The original issue #84 was reported by jonyscathe. Thank you 🤗
    """
    ret = _results(
        """if "last_name" in test_dict:
    name = test_dict["last_name"]
else:
    name = test_dict["first_name"]"""
    )
    has_sim401 = False
    expected_proposal = (
        'Use \'name = test_dict.get("last_name", '
        "test_dict['first_name'])' instead of an if-block"
    )
    for el in ret:
        if "SIM401" in el:
            msg = el.split("SIM401")[1].strip()
            has_sim401 = True
            assert msg == expected_proposal
    assert has_sim401


def test_sim401_positive_msg_issue84_example2():
    """
    This is a regression test for the SIM401 message.

    The original issue #84 was reported by jonyscathe. Thank you 🤗
    """
    ret = _results(
        """if "phone_number" in test_dict:
    number = test_dict["phone_number"]
else:
    number = "" """
    )
    has_sim401 = False
    expected_proposal = (
        'Use \'number = test_dict.get("phone_number", "")\' '
        "instead of an if-block"
    )
    for el in ret:
        if "SIM401" in el:
            msg = el.split("SIM401")[1].strip()
            has_sim401 = True
            assert msg == expected_proposal
    assert has_sim401


def test_sim401_positive_msg_check_issue89():
    """
    This is a regression test for the SIM401 message.

    The original issue #89 was reported by Aarni Koskela. Thank you 🤗
    """
    ret = _results(
        """if a:
    token = a[1]
elif 'token' in dct:
    token = dct['token']
else:
    token = None"""
    )
    has_sim401 = False
    expected_proposal = (
        "Use 'token = dct.get(\"token\", None)' instead of an if-block"
    )
    for el in ret:
        if "SIM401" in el:
            msg = el.split("SIM401")[1].strip()
            has_sim401 = True
            assert msg == expected_proposal
    assert has_sim401
