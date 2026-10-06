import pytest

from tests import _results, _rule_hits

RULE = "SIM202"

TRUE_POSITIVES = [
    pytest.param(
        "not a != b",
        {
            "1:0 SIM202 Use 'a == b' instead of 'not a != b'",
        },
        id="not-ne",
    ),
]

FALSE_POSITIVES = [
    pytest.param("a == b", id="plain-eq"),
    pytest.param("not a", id="not-eq"),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
