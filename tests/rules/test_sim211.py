import pytest

from tests import _results, _rule_hits

RULE = "SIM211"

TRUE_POSITIVES = [
    pytest.param(
        "False if True else True",
        {
            "1:0 SIM211 Use 'not True' instead of 'False if True else True'",
        },
        id="false-true",
    ),
]

FALSE_POSITIVES = [
    pytest.param("1 if a else 0", id="different-values"),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
