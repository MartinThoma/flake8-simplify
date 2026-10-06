import pytest

from tests import _results, _rule_hits, snippet

RULE = "SIM117"

TRUE_POSITIVES = [
    pytest.param(
        snippet("""
            with A() as a:
                with B() as b:
                    print('hello')
        """),
        {
            "1:0 SIM117 Use 'with A() as a, B() as b:' instead of multiple with statements",
        },
        id="nested-with",
    ),
]

FALSE_POSITIVES = [
    pytest.param(
        snippet("""
            with A() as a:
                a()
                with B() as b:
                    print('hello')
        """),
        id="statement-before-inner-with",
    ),
    pytest.param(
        snippet("""
            with A() as a:
                with B() as b:
                    print('hello')
                a()
        """),
        id="statement-after-inner-with",
    ),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
