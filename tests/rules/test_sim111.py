import pytest

from tests import _results, _rule_hits, snippet

RULE = "SIM111"

TRUE_POSITIVES = [
    pytest.param(
        snippet("""
            for x in iterable:
                if check(x):
                    return False
            return True
        """),
        {
            "1:0 SIM111 Use 'return all(not check(x) for x in iterable)'",
        },
        id="all-negated-call",
    ),
    pytest.param(
        snippet("""
            for x in iterable:
                if not x.is_empty():
                    return False
            return True
        """),
        {
            "1:0 SIM111 Use 'return all(x.is_empty() for x in iterable)'",
        },
        id="all-negated-condition",
    ),
]

FALSE_POSITIVES = [
    pytest.param(
        snippet("""
            for a in my_list:
              if a == 2:
                return False
            call_method()
            return True
        """),
        id="statement-between-loop-and-return",
    ),
    pytest.param(
        snippet("""
            for x in iterable:
                if check(x):
                    return "foo"
            return "bar"
        """),
        id="non-bool-returns",
    ),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
