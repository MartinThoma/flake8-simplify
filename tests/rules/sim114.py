"""Test cases for SIM114. See tests/rules/__init__.py."""

from tests import snippet

TRUE_POSITIVES = {
    "same-body": (
        snippet("""
            if a:
                b
            elif c:
                b
        """),
        {
            "1:3 SIM114 Use logical or ((a) or (c)) and a single body",
        },
    ),
}

FALSE_POSITIVES = {
    "different-calls": snippet("""
        def complicated_calc(*arg, **kwargs):
            return 42

        def foo(p):
            if p == 2:
                return complicated_calc(microsecond=0)
            elif p == 3:
                return complicated_calc(microsecond=0, second=0)
            return None
    """),
    "elif-in-between": snippet("""
        a = False
        b = True
        c = True

        if a:
            z = 1
        elif b:
            z = 2
        elif c:
            z = 1
    """),
}
