import pytest

from tests import _results, _rule_hits, snippet

RULE = "SIM107"

TRUE_POSITIVES = [
    pytest.param(
        snippet("""
            def foo():
                try:
                    1 / 0
                    return "1"
                except:
                    return "2"
                finally:
                    return "3"
        """),
        {
            "8:8 SIM107 Don't use return in try/except and finally",
        },
        id="return-in-try-and-finally",
    ),
]

FALSE_POSITIVES = [
    pytest.param(
        snippet("""
            def foo():
                try:
                    return 1
                except ValueError:
                    bar()
        """),
        id="return-only-in-try",
    ),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
