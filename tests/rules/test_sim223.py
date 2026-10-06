import pytest

from tests import _results, _rule_hits

RULE = "SIM223"

TRUE_POSITIVES = [
    pytest.param(
        "a and False",
        {
            "1:0 SIM223 Use 'False' instead of '... and False'",
        },
        id="and-false",
    ),
]

FALSE_POSITIVES = [
    pytest.param("a and b", id="and-name"),
    pytest.param("a or False", id="or-false"),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
