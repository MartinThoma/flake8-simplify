"""Test cases for SIM102. See tests/rules/__init__.py."""

from tests import snippet

TRUE_POSITIVES = {
    "nested": (
        snippet("""
            if a:
                if b:
                    c
        """),
        {
            "1:0 SIM102 Use a single if-statement instead of nested if-statements",
        },
    ),
    "nested-in-elif": (
        snippet("""
            if a:
                pass
            elif b:
                if c:
                    d
        """),
        {
            "3:0 SIM102 Use a single if-statement instead of nested if-statements",
        },
    ),
    "not-main-check": (
        snippet("""
            if __name__ != "__main__":
                if x:
                    pass
        """),
        {
            "1:0 SIM102 Use a single if-statement instead of nested if-statements",
        },
    ),
}

FALSE_POSITIVES = {
    "inner-else": snippet("""
        if a:
            if b:
                c
            else:
                d
    """),
    "main-guard": snippet("""
        if __name__ == "__main__":
            if foo(): ...
    """),
    "intermediate-statement": snippet("""
        if a:
            d
            if b:
                c
    """),
}
