import pytest

from tests import _results, _rule_hits

RULE = "SIM901"

TRUE_POSITIVES = [
    pytest.param(
        "bool(a == b)",
        {
            "1:0 SIM901 Use 'a == b' instead of 'bool(a == b)'",
        },
        id="bool-compare",
    ),
]

FALSE_POSITIVES = [
    pytest.param("bool(a)", id="bool-name"),
    pytest.param("a == b", id="plain-compare"),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
