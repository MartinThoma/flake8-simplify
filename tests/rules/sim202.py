"""Test cases for SIM202. See tests/rules/__init__.py."""

TRUE_POSITIVES = {
    "not-ne": (
        "not a != b",
        {
            "1:0 SIM202 Use 'a == b' instead of 'not a != b'",
        },
    ),
}

FALSE_POSITIVES = {
    "plain-eq": "a == b",
    "not-eq": "not a",
}
