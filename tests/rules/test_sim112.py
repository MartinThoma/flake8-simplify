import pytest

from tests import _results, _rule_hits

RULE = "SIM112"

TRUE_POSITIVES = [
    pytest.param(
        "os.environ['foo']",
        {
            "1:0 SIM112 Use 'os.environ[\"FOO\"]' instead of 'os.environ['foo']'",
        },
        id="index",
    ),
    pytest.param(
        "os.environ.get('foo')",
        {
            "1:0 SIM112 Use 'os.environ.get(\"FOO\")' instead of 'os.environ.get('foo')'",
        },
        id="get",
    ),
    pytest.param(
        "os.environ.get('foo', 'bar')",
        {
            "1:0 SIM112 Use 'os.environ.get(\"FOO\", \"bar\")' instead of 'os.environ.get('foo', 'bar')'",
        },
        id="get-with-default",
    ),
]

FALSE_POSITIVES = [
    pytest.param("os.environ['FOO']", id="already-capital"),
    pytest.param("config['foo']", id="other-mapping"),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
