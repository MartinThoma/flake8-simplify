"""Test cases for SIM108. See tests/rules/__init__.py."""

from tests import snippet

TRUE_POSITIVES = {
    "if-else-assignment": (
        snippet("""
            if a:
                b = c
            else:
                b = d
        """),
        {
            "1:0 SIM108 Use ternary operator 'b = c if a else d' instead of if-else-block",
        },
    ),
    "nested-in-if-body": (
        snippet("""
            if a:
                x = 1
                if b:
                    x = 2
                else:
                    x = 3
        """),
        {
            "3:4 SIM108 Use ternary operator 'x = 2 if b else 3' instead of if-else-block",
        },
    ),
}

FALSE_POSITIVES = {
    "elif-chain": snippet("""
        if E == 0:
            M = 3
        elif E == 1:
            M = 2
        else:
            M = 0.5
    """),
    "different-targets": snippet("""
        if a:
            b = c
        else:
            d = e
    """),
}
