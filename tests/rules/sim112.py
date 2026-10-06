"""Test cases for SIM112. See tests/rules/__init__.py."""

TRUE_POSITIVES = {
    "index": (
        "os.environ['foo']",
        {
            "1:0 SIM112 Use 'os.environ[\"FOO\"]' instead of 'os.environ['foo']'",
        },
    ),
    "get": (
        "os.environ.get('foo')",
        {
            "1:0 SIM112 Use 'os.environ.get(\"FOO\")' instead of 'os.environ.get('foo')'",
        },
    ),
    "get-with-default": (
        "os.environ.get('foo', 'bar')",
        {
            "1:0 SIM112 Use 'os.environ.get(\"FOO\", \"bar\")' instead of 'os.environ.get('foo', 'bar')'",
        },
    ),
}

FALSE_POSITIVES = {
    "already-capital": "os.environ['FOO']",
    "other-mapping": "config['foo']",
}
