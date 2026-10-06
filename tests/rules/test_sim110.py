import pytest

from tests import _results, _rule_hits, snippet

RULE = "SIM110"

TRUE_POSITIVES = [
    pytest.param(
        snippet("""
            for x in iterable:
                if check(x):
                    return True
            return False
        """),
        {
            "1:0 SIM110 Use 'return any(check(x) for x in iterable)'",
        },
        id="any",
    ),
]

FALSE_POSITIVES = [
    pytest.param(
        snippet("""
            for el in [1,2,3]:
                if is_true(el):
                    return True
            raise Exception
        """),
        id="raise-after-loop",
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
