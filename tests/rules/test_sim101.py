import pytest

from tests import _results, _rule_hits, snippet

RULE = "SIM101"

TRUE_POSITIVES = [
    pytest.param(
        snippet("""
            isinstance(a, int) or isinstance(a, float)
            isinstance(b, bool) or isinstance(b, str)
        """),
        {
            "1:0 SIM101 Multiple isinstance-calls which can be merged into a single call for variable 'a'",
            "2:0 SIM101 Multiple isinstance-calls which can be merged into a single call for variable 'b'",
        },
        id="two-lines",
    ),
    pytest.param(
        snippet("""
            foo(a, b, c) or bar(a, b)
            isinstance(b, bool) or isinstance(b, str)
        """),
        {
            "2:0 SIM101 Multiple isinstance-calls which can be merged into a single call for variable 'b'",
        },
        id="after-other-code",
    ),
]

FALSE_POSITIVES = [
    pytest.param("isinstance(a, int) or foo", id="single-call"),
    pytest.param(
        "isinstance(b, bool) and isinstance(b, str)", id="and-instead-of-or"
    ),
    pytest.param("isfoo(a, int) or isfoo(a, float)", id="other-function"),
    pytest.param(
        "isinstance(a, int) or isinstance(b, float)", id="different-variables"
    ),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
