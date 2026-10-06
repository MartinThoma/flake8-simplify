import pytest

from tests import _results, _rule_hits, snippet

RULE = "SIM116"

TRUE_POSITIVES = [
    pytest.param(
        snippet("""
            if a == "foo":
                return "bar"
            elif a == "bar":
                return "baz"
            elif a == "boo":
                return "ooh"
            else:
                return 42
        """),
        {
            "1:0 SIM116 Use a dictionary lookup instead of 3+ if/elif-statements: return {'foo': 'bar', 'bar': 'baz', 'boo': 'ooh'}.get(a, 42)",
        },
        id="three-branches",
    ),
]

FALSE_POSITIVES = [
    pytest.param(
        snippet("""
            if a == "foo":
                return "bar"
            elif a == "bar":
                return baz()
            elif a == "boo":
                return "ooh"
            else:
                return 42
        """),
        id="non-constant-return",
    ),
    pytest.param(
        snippet("""
            if a == "foo":
                return "bar"
            elif a == "bar":
                return "baz"
            else:
                return 42
        """),
        id="two-branches",
    ),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
