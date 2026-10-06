"""Test cases for SIM300. See tests/rules/__init__.py."""

TRUE_POSITIVES = {
    "string": (
        "'Yoda' == i_am",
        {
            "1:0 SIM300 Use 'i_am == \"Yoda\"' instead of '\"Yoda\" == i_am' (Yoda-conditions)",
        },
    ),
    "int": (
        "42 == age",
        {
            "1:0 SIM300 Use 'age == 42' instead of '42 == age' (Yoda-conditions)",
        },
    ),
}

FALSE_POSITIVES = {
    "variable-first": "age == 42",
    "both-variables": "a == b",
}
