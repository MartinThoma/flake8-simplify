import pytest

from tests import _results, _rule_hits, snippet

RULE = "SIM909"

TRUE_POSITIVES = [
    pytest.param(
        "foo = foo",
        {
            "1:0 SIM909 Remove reflexive assignment 'foo = foo'",
        },
        id="simple",
    ),
    pytest.param(
        "foo = foo = 42",
        {
            "1:0 SIM909 Remove reflexive assignment 'foo = foo = 42'",
        },
        id="double",
    ),
    pytest.param(
        "foo = bar = foo = 42",
        {
            "1:0 SIM909 Remove reflexive assignment 'foo = bar = foo = 42'",
        },
        id="multiple",
    ),
    pytest.param(
        "a['foo'] = a['foo']",
        {
            "1:0 SIM909 Remove reflexive assignment 'a['foo'] = a['foo']'",
        },
        id="dict",
    ),
]

FALSE_POSITIVES = [
    pytest.param("n, m = m, n", id="tuple-switch"),
    pytest.param("foo = 'foo'", id="variable"),
    pytest.param(
        snippet("""
            database = Database(url=url)
            metadata = sqlalchemy.MetaData()

            class BaseMeta:
                metadata = metadata
                database = database
        """),
        id="class-attributes",
    ),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
