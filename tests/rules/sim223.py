"""Test cases for SIM223. See tests/rules/__init__.py."""

TRUE_POSITIVES = {
    "and-false": (
        "a and False",
        {
            "1:0 SIM223 Use 'False' instead of '... and False'",
        },
    ),
}

FALSE_POSITIVES = {
    "and-name": "a and b",
    "or-false": "a or False",
}
