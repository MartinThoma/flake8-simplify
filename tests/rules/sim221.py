"""Test cases for SIM221. See tests/rules/__init__.py."""

TRUE_POSITIVES = {
    "or-not": (
        "a or not a",
        {
            "1:0 SIM221 Use 'True' instead of 'a or not a'",
        },
    ),
}

FALSE_POSITIVES = {
    "different-names": "a or not b",
}
