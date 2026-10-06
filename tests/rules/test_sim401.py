import pytest

from tests import _results, _rule_hits, snippet

RULE = "SIM401"

TRUE_POSITIVES = [
    pytest.param(
        snippet("""
            if key in a_dict:
                value = a_dict[key]
            else:
                value = 'default'
        """),
        {
            "1:0 SIM401 Use 'value = a_dict.get(key, \"default\")' instead of an if-block",
        },
        id="if-else",
    ),
    pytest.param(
        snippet("""
            if key not in a_dict:
                value = 'default'
            else:
                value = a_dict[key]
        """),
        {
            "1:0 SIM401 Use 'value = a_dict.get(key, \"default\")' instead of an if-block",
        },
        id="negated",
    ),
    pytest.param(
        snippet("""
            if "last_name" in test_dict:
                name = test_dict["last_name"]
            else:
                name = test_dict["first_name"]
        """),
        {
            "1:0 SIM401 Use 'name = test_dict.get(\"last_name\", test_dict['first_name'])' instead of an if-block",
        },
        id="issue-84-dict-default",
    ),
    pytest.param(
        snippet("""
            if "phone_number" in test_dict:
                number = test_dict["phone_number"]
            else:
                number = ""
        """),
        {
            '1:0 SIM401 Use \'number = test_dict.get("phone_number", "")\' instead of an if-block',
        },
        id="issue-84-empty-string",
    ),
    pytest.param(
        snippet("""
            if a:
                token = a[1]
            elif 'token' in dct:
                token = dct['token']
            else:
                token = None
        """),
        {
            "3:0 SIM401 Use 'token = dct.get(\"token\", None)' instead of an if-block",
        },
        id="issue-89-elif",
    ),
]

FALSE_POSITIVES = [
    pytest.param(
        snippet("""
            if "foo" in some_dict["a"]:
                some_dict["b"] = some_dict["a"]["foo"]
            else:
                some_dict["a"]["foo"] = some_dict["b"]
        """),
        id="different-subscripts",
    ),
    pytest.param(
        snippet("""
            if key in a_dict:
                value = a_dict[key]
        """),
        id="no-else",
    ),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
