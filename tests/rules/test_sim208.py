import pytest

from tests import _results, _rule_hits

RULE = "SIM208"

TRUE_POSITIVES = [
    pytest.param(
        "not (not a)",
        {
            "1:0 SIM208 Use 'a' instead of 'not (not a)'",
        },
        id="double-not",
    ),
]

FALSE_POSITIVES = [
    pytest.param("not a", id="single-not"),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
