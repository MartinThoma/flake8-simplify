import pytest

from tests import _results, _rule_hits

RULE = "SIM906"

TRUE_POSITIVES = [
    pytest.param(
        "os.path.join(a,os.path.join(b,c))",
        {
            "1:0 SIM906 Use 'os.path.join(a, b, c)' instead of 'os.path.join(a, os.path.join(b, c))'",
        },
        id="base",
    ),
    pytest.param(
        "os.path.join(a,os.path.join('b',c))",
        {
            "1:0 SIM906 Use 'os.path.join(a, 'b', c)' instead of 'os.path.join(a, os.path.join('b', c))'",
        },
        id="str-arg",
    ),
]

FALSE_POSITIVES = [
    pytest.param("os.path.join(a, b, c)", id="flat"),
    pytest.param("foo.join(a, foo.join(b, c))", id="other-function"),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
