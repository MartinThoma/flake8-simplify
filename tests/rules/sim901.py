"""Test cases for SIM901. See tests/rules/__init__.py."""

TRUE_POSITIVES = {
    "bool-compare": (
        "bool(a == b)",
        {
            "1:0 SIM901 Use 'a == b' instead of 'bool(a == b)'",
        },
    ),
}

FALSE_POSITIVES = {
    "bool-name": "bool(a)",
    "plain-compare": "a == b",
}
