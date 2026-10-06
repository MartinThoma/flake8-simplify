import pytest

from tests import _results, _rule_hits

RULE = "SIM300"

TRUE_POSITIVES = [
    pytest.param(
        "'Yoda' == i_am",
        {
            "1:0 SIM300 Use 'i_am == \"Yoda\"' instead of '\"Yoda\" == i_am' (Yoda-conditions)",
        },
        id="string",
    ),
    pytest.param(
        "42 == age",
        {
            "1:0 SIM300 Use 'age == 42' instead of '42 == age' (Yoda-conditions)",
        },
        id="int",
    ),
]

FALSE_POSITIVES = [
    pytest.param("age == 42", id="variable-first"),
    pytest.param("a == b", id="both-variables"),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
