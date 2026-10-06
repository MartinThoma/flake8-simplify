import pytest

from tests import _results, _rule_hits

RULE = "SIM222"

TRUE_POSITIVES = [
    pytest.param(
        "a or True",
        {
            "1:0 SIM222 Use 'True' instead of '... or True'",
        },
        id="or-true",
    ),
]

FALSE_POSITIVES = [
    pytest.param("a or b", id="or-name"),
    pytest.param("a and True", id="and-true"),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
