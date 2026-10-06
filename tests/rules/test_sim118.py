import pytest

from tests import _results, _rule_hits, snippet

RULE = "SIM118"

TRUE_POSITIVES = [
    pytest.param(
        "key in dict.keys()",
        {
            "1:0 SIM118 Use 'key in dict' instead of 'key in dict.keys()'",
        },
        id="in-keys",
    ),
]

FALSE_POSITIVES = [
    pytest.param(
        snippet("""
            for key in list(dict.keys()):
                if some_property(key):
                    del dict[key]
        """),
        id="delete-while-iterating",
    ),
    pytest.param("key in dict", id="in-dict"),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
