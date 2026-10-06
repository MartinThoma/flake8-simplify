import pytest

from tests import _results, _rule_hits, snippet

RULE = "SIM102"

TRUE_POSITIVES = [
    pytest.param(
        snippet("""
            if a:
                if b:
                    c
        """),
        {
            "1:0 SIM102 Use a single if-statement instead of nested if-statements",
        },
        id="nested",
    ),
    pytest.param(
        snippet("""
            if a:
                pass
            elif b:
                if c:
                    d
        """),
        {
            "3:0 SIM102 Use a single if-statement instead of nested if-statements",
        },
        id="nested-in-elif",
    ),
]

FALSE_POSITIVES = [
    pytest.param(
        snippet("""
            if a:
                if b:
                    c
                else:
                    d
        """),
        id="inner-else",
    ),
    pytest.param(
        snippet("""
            if __name__ == "__main__":
                if foo(): ...
        """),
        id="main-guard",
    ),
    pytest.param(
        snippet("""
            if a:
                d
                if b:
                    c
        """),
        id="intermediate-statement",
    ),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
