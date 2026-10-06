"""Test cases for SIM115. See tests/rules/__init__.py."""

from tests import snippet

TRUE_POSITIVES = {
    "open-without-with": (
        snippet("""
            f = open('foo.txt')
            data = f.read()
            f.close()
        """),
        {
            "1:4 SIM115 Use context handler for opening files",
        },
    ),
}

FALSE_POSITIVES = {
    "with-statement": snippet("""
        with open('foo.txt') as f:
            data = f.read()
    """),
}
