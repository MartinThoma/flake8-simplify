import pytest

from tests import _results, _rule_hits

RULE = "SIM220"

TRUE_POSITIVES = [
    pytest.param(
        "a and not a",
        {
            "1:0 SIM220 Use 'False' instead of 'a and not a'",
        },
        id="and-not",
    ),
]

FALSE_POSITIVES = [
    pytest.param("a and not b", id="different-names"),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
