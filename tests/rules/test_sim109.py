import pytest

from tests import _results, _rule_hits

RULE = "SIM109"

TRUE_POSITIVES = [
    pytest.param(
        "a == b or a == c",
        {
            "1:0 SIM109 Use 'a in ((b, c))' instead of 'a == b or a == c'",
        },
        id="two-comparisons",
    ),
]

FALSE_POSITIVES = [
    pytest.param("a == b() or a == c", id="call-left"),
    pytest.param("a == b or a == c()", id="call-right"),
    pytest.param("a == b() or a == c()", id="calls-both"),
    pytest.param("a == b or c == d", id="different-variables"),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
