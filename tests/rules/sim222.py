"""Test cases for SIM222. See tests/rules/__init__.py."""

TRUE_POSITIVES = {
    "or-true": (
        "a or True",
        {
            "1:0 SIM222 Use 'True' instead of '... or True'",
        },
    ),
}

FALSE_POSITIVES = {
    "or-name": "a or b",
    "and-true": "a and True",
}
