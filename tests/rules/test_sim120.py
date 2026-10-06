import pytest

from tests import _results, _rule_hits

RULE = "SIM120"

TRUE_POSITIVES = [
    pytest.param(
        "class FooBar(object): pass",
        {
            "1:0 SIM120 Use 'class FooBar:' instead of 'class FooBar(object):'",
        },
        id="object-base",
    ),
]

FALSE_POSITIVES = [
    pytest.param("class FooBar: pass", id="no-base"),
    pytest.param("class FooBar(Base): pass", id="other-base"),
    pytest.param(
        "class FooBar(Base, object): pass", id="object-and-other-base"
    ),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
