"""Test cases for SIM203. See tests/rules/__init__.py."""

from tests import snippet

TRUE_POSITIVES = {
    "not-in": (
        "not a in b",
        {
            "1:0 SIM203 Use 'a not in b' instead of 'not a in b'",
        },
    ),
    "in-if-condition": (
        snippet("""
            if not key in a_dict:
                value = 'default'
        """),
        {
            "1:3 SIM203 Use 'key not in a_dict' instead of 'not key in a_dict'",
        },
    ),
}

FALSE_POSITIVES = {
    "not-in-operator": "a not in b",
    "plain-in": "a in b",
}
