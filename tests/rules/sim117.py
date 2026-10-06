"""Test cases for SIM117. See tests/rules/__init__.py."""

from tests import snippet

TRUE_POSITIVES = {
    "nested-with": (
        snippet("""
            with A() as a:
                with B() as b:
                    print('hello')
        """),
        {
            "1:0 SIM117 Use 'with A() as a, B() as b:' instead of multiple with statements",
        },
    ),
}

FALSE_POSITIVES = {
    "statement-before-inner-with": snippet("""
        with A() as a:
            a()
            with B() as b:
                print('hello')
    """),
    "statement-after-inner-with": snippet("""
        with A() as a:
            with B() as b:
                print('hello')
            a()
    """),
}
