import pytest

from tests import _results, _rule_hits, snippet

RULE = "SIM908"

TRUE_POSITIVES = [
    pytest.param(
        snippet("""
            name = "some_default"
            if "some_key" in some_dict:
                name = some_dict["some_key"]
        """),
        {
            '2:0 SIM908 Use \'some_dict.get("some_key")\' instead of \'if "some_key" in some_dict: some_dict["some_key"]\'',
        },
        id="default-then-override",
    ),
]

FALSE_POSITIVES = [
    pytest.param(
        snippet("""
            if "." in resistance:
                # Swap '.' with suffix
                resistance = resistance.replace(".", resistance[-1])[:-1]
        """),
        id="issue-125",
    ),
    pytest.param(
        snippet("""
            if "." in iterable:
                iterable = iterable[:-1]
        """),
        id="issue-125-simplified",
    ),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
