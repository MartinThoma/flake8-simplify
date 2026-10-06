import pytest

from tests import _results, _rule_hits, snippet

RULE = "SIM115"

TRUE_POSITIVES = [
    pytest.param(
        snippet("""
            f = open('foo.txt')
            data = f.read()
            f.close()
        """),
        {
            "1:4 SIM115 Use context handler for opening files",
        },
        id="open-without-with",
    ),
]

FALSE_POSITIVES = [
    pytest.param(
        snippet("""
            with open('foo.txt') as f:
                data = f.read()
        """),
        id="with-statement",
    ),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
