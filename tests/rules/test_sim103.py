import pytest

from tests import _results, _rule_hits, snippet

RULE = "SIM103"

TRUE_POSITIVES = [
    pytest.param(
        snippet("""
            if a:
                return True
            else:
                return False
        """),
        {
            "1:0 SIM103 Return the condition a directly",
        },
        id="true-false",
    ),
]

FALSE_POSITIVES = [
    pytest.param(
        snippet("""
            if a:
                return 1
            else:
                return 2
        """),
        id="non-bool-returns",
    ),
    pytest.param(
        snippet("""
            if a:
                return True
            return 2
        """),
        id="no-else",
    ),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
