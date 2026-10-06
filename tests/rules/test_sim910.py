import pytest

from tests import _results, _rule_hits

RULE = "SIM910"

TRUE_POSITIVES = [
    pytest.param(
        "d.get(key, None)",
        {
            "1:0 SIM910 Use 'd.get(key)' instead of 'd.get(key, None)'",
        },
        id="name-key",
    ),
    pytest.param(
        "d.get('key', None)",
        {
            "1:0 SIM910 Use 'd.get(\"key\")' instead of 'd.get('key', None)'",
        },
        id="str-key",
    ),
]

FALSE_POSITIVES = [
    pytest.param("d.get(key)", id="no-default"),
    pytest.param("d.get(key, 1)", id="other-default"),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
