"""Test cases for SIM212. See tests/rules/__init__.py."""

TRUE_POSITIVES = {
    "negated-condition": (
        "b if not a else a",
        {
            "1:0 SIM212 Use 'a if a else b' instead of 'b if not a else a'",
        },
    ),
}

FALSE_POSITIVES = {
    "plain-ifexp": "b if a else c",
    "different-names": "b if not a else c",
}
