import pytest

from tests import _results, _rule_hits

RULE = "SIM905"

TRUE_POSITIVES = [
    pytest.param(
        'domains = "de com net org".split()',
        {
            '1:10 SIM905 Use \'["de", "com", "net", "org"]\' instead of \'"de com net org".split()\'',
        },
        id="split",
    ),
]

FALSE_POSITIVES = [
    pytest.param("domains = names.split()", id="variable"),
    pytest.param('domains = "de,com".split(",")', id="with-separator"),
    pytest.param('domains = "de com net".split(None, 1)', id="with-maxsplit"),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
