import pytest

from tests import _results, _rule_hits

RULE = "SIM911"

TRUE_POSITIVES = [
    pytest.param(
        "zip(d.keys(), d.values())",
        {
            "1:0 SIM911 Use 'd.items()' instead of 'zip(d.keys(), d.values())'",
        },
        id="keys-values",
    ),
]

FALSE_POSITIVES = [
    pytest.param("zip(d.keys(), d.keys())", id="keys-keys"),
    pytest.param("zip(d1.keys(), d2.values())", id="different-dicts"),
    pytest.param("zip(d1.keys(), values)", id="keys-and-name"),
    pytest.param("zip(keys, values)", id="names"),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
