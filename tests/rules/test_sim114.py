import pytest

from tests import _results, _rule_hits, snippet

RULE = "SIM114"

TRUE_POSITIVES = [
    pytest.param(
        snippet("""
            if a:
                b
            elif c:
                b
        """),
        {
            "1:3 SIM114 Use logical or ((a) or (c)) and a single body",
        },
        id="same-body",
    ),
]

FALSE_POSITIVES = [
    pytest.param(
        snippet("""
            def complicated_calc(*arg, **kwargs):
                return 42

            def foo(p):
                if p == 2:
                    return complicated_calc(microsecond=0)
                elif p == 3:
                    return complicated_calc(microsecond=0, second=0)
                return None
        """),
        id="different-calls",
    ),
    pytest.param(
        snippet("""
            a = False
            b = True
            c = True

            if a:
                z = 1
            elif b:
                z = 2
            elif c:
                z = 1
        """),
        id="elif-in-between",
    ),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
