"""Test cases for SIM909. See tests/rules/__init__.py."""

from tests import snippet

TRUE_POSITIVES = {
    "simple": (
        "foo = foo",
        {
            "1:0 SIM909 Remove reflexive assignment 'foo = foo'",
        },
    ),
    "double": (
        "foo = foo = 42",
        {
            "1:0 SIM909 Remove reflexive assignment 'foo = foo = 42'",
        },
    ),
    "multiple": (
        "foo = bar = foo = 42",
        {
            "1:0 SIM909 Remove reflexive assignment 'foo = bar = foo = 42'",
        },
    ),
    "dict": (
        "a['foo'] = a['foo']",
        {
            "1:0 SIM909 Remove reflexive assignment 'a['foo'] = a['foo']'",
        },
    ),
}

FALSE_POSITIVES = {
    "tuple-switch": "n, m = m, n",
    "variable": "foo = 'foo'",
    "class-attributes": snippet("""
        database = Database(url=url)
        metadata = sqlalchemy.MetaData()

        class BaseMeta:
            metadata = metadata
            database = database
    """),
}
