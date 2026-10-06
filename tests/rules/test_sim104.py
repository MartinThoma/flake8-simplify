import pytest

from tests import _results, _rule_hits, snippet

RULE = "SIM104"

TRUE_POSITIVES = [
    pytest.param(
        snippet("""
            for item in iterable:
                yield item
        """),
        {
            "1:0 SIM104 Use 'yield from iterable'",
        },
        id="sync-generator",
    ),
]

FALSE_POSITIVES = [
    pytest.param(
        snippet("""
            async def items():
                for c in 'abc':
                    yield c
        """),
        id="async-generator",
    ),
    pytest.param(
        snippet("""
            async def items():
                with open('/etc/passwd') as f:
                    for line in f:
                        yield line
        """),
        id="async-generator-with",
    ),
    pytest.param(
        snippet("""
            for item in iterable:
                yield item + 1
        """),
        id="yield-other-value",
    ),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
