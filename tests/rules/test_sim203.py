import pytest

from tests import _results, _rule_hits, snippet

RULE = "SIM203"

TRUE_POSITIVES = [
    pytest.param(
        "not a in b",
        {
            "1:0 SIM203 Use 'a not in b' instead of 'not a in b'",
        },
        id="not-in",
    ),
    pytest.param(
        snippet("""
            if not key in a_dict:
                value = 'default'
        """),
        {
            "1:3 SIM203 Use 'key not in a_dict' instead of 'not key in a_dict'",
        },
        id="in-if-condition",
    ),
]

FALSE_POSITIVES = [
    pytest.param("a not in b", id="not-in-operator"),
    pytest.param("a in b", id="plain-in"),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
