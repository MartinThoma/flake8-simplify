"""Test cases for SIM208. See tests/rules/__init__.py."""

TRUE_POSITIVES = {
    "double-not": (
        "not (not a)",
        {
            "1:0 SIM208 Use 'a' instead of 'not (not a)'",
        },
    ),
}

FALSE_POSITIVES = {
    "single-not": "not a",
}
