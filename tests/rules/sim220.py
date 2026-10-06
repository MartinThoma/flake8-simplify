"""Test cases for SIM220. See tests/rules/__init__.py."""

TRUE_POSITIVES = {
    "and-not": (
        "a and not a",
        {
            "1:0 SIM220 Use 'False' instead of 'a and not a'",
        },
    ),
}

FALSE_POSITIVES = {
    "different-names": "a and not b",
}
