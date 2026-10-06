import pytest

from tests import _results, _rule_hits

RULE = "SIM210"

TRUE_POSITIVES = [
    pytest.param(
        "True if True else False",
        {
            "1:0 SIM210 Use 'bool(True)' instead of 'True if True else False'",
        },
        id="true-false",
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
