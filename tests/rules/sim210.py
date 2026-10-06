"""Test cases for SIM210. See tests/rules/__init__.py."""

TRUE_POSITIVES = {
    "true-false": (
        "True if True else False",
        {
            "1:0 SIM210 Use 'bool(True)' instead of 'True if True else False'",
        },
    ),
}

FALSE_POSITIVES = {
    "different-values": "1 if a else 0",
}
