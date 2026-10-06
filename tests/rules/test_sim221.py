import pytest

from tests import _results, _rule_hits

RULE = "SIM221"

TRUE_POSITIVES = [
    pytest.param(
        "a or not a",
        {
            "1:0 SIM221 Use 'True' instead of 'a or not a'",
        },
        id="or-not",
    ),
]

FALSE_POSITIVES = [
    pytest.param("a or not b", id="different-names"),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
