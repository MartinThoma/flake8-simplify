"""Test cases for SIM201. See tests/rules/__init__.py."""

from tests import snippet

TRUE_POSITIVES = {
    "not-eq": (
        "not a == b",
        {
            "1:0 SIM201 Use 'a != b' instead of 'not a == b'",
        },
    ),
}

FALSE_POSITIVES = {
    "in-exception-check": snippet("""
        if not a == b:
            raise ValueError()
    """),
}
