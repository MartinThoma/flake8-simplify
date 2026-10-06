"""Test cases for SIM109. See tests/rules/__init__.py."""

TRUE_POSITIVES = {
    "two-comparisons": (
        "a == b or a == c",
        {
            "1:0 SIM109 Use 'a in ((b, c))' instead of 'a == b or a == c'",
        },
    ),
}

FALSE_POSITIVES = {
    "call-left": "a == b() or a == c",
    "call-right": "a == b or a == c()",
    "calls-both": "a == b() or a == c()",
    "different-variables": "a == b or c == d",
}
