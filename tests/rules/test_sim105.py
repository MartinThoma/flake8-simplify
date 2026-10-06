import pytest

from tests import _results, _rule_hits, snippet

RULE = "SIM105"

TRUE_POSITIVES = [
    pytest.param(
        snippet("""
            try:
                foo()
            except ValueError:
                pass
        """),
        {
            "1:0 SIM105 Use 'contextlib.suppress(ValueError)'",
        },
        id="specific-exception",
    ),
    pytest.param(
        snippet("""
            try:
                foo()
            except:
                pass
        """),
        {
            "1:0 SIM105 Use 'contextlib.suppress(Exception)'",
        },
        id="bare-except",
    ),
]

FALSE_POSITIVES = [
    pytest.param(
        snippet("""
            try:
                foo()
            except ValueError:
                bar()
        """),
        id="handler-does-something",
    ),
    pytest.param(
        snippet("""
            try:
                foo()
            except ValueError:
                pass
            else:
                bar()
        """),
        id="has-else",
    ),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
