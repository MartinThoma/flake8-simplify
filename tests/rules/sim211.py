"""Test cases for SIM211. See tests/rules/__init__.py."""

TRUE_POSITIVES = {
    "false-true": (
        "False if True else True",
        {
            "1:0 SIM211 Use 'not True' instead of 'False if True else True'",
        },
    ),
}

FALSE_POSITIVES = {
    "different-values": "1 if a else 0",
}
