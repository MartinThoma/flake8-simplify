import pytest

from tests import _results, _rule_hits, snippet

RULE = "SIM201"

TRUE_POSITIVES = [
    pytest.param(
        "not a == b",
        {
            "1:0 SIM201 Use 'a != b' instead of 'not a == b'",
        },
        id="not-eq",
    ),
]

FALSE_POSITIVES = [
    pytest.param(
        snippet("""
            if not a == b:
                raise ValueError()
        """),
        id="in-exception-check",
    ),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
