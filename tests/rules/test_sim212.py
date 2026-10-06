import pytest

from tests import _results, _rule_hits

RULE = "SIM212"

TRUE_POSITIVES = [
    pytest.param(
        "b if not a else a",
        {
            "1:0 SIM212 Use 'a if a else b' instead of 'b if not a else a'",
        },
        id="negated-condition",
    ),
]

FALSE_POSITIVES = [
    pytest.param("b if a else c", id="plain-ifexp"),
    pytest.param("b if not a else c", id="different-names"),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
