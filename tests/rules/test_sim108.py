import pytest

from tests import _results, _rule_hits, snippet

RULE = "SIM108"

TRUE_POSITIVES = [
    pytest.param(
        snippet("""
            if a:
                b = c
            else:
                b = d
        """),
        {
            "1:0 SIM108 Use ternary operator 'b = c if a else d' instead of if-else-block",
        },
        id="if-else-assignment",
    ),
]

FALSE_POSITIVES = [
    pytest.param(
        snippet("""
            if E == 0:
                M = 3
            elif E == 1:
                M = 2
            else:
                M = 0.5
        """),
        id="elif-chain",
    ),
    pytest.param(
        snippet("""
            if a:
                b = c
            else:
                d = e
        """),
        id="different-targets",
    ),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
