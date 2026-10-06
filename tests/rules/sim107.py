"""Test cases for SIM107. See tests/rules/__init__.py."""

from tests import snippet

TRUE_POSITIVES = {
    "return-in-try-and-finally": (
        snippet("""
            def foo():
                try:
                    1 / 0
                    return "1"
                except:
                    return "2"
                finally:
                    return "3"
        """),
        {
            "8:8 SIM107 Don't use return in try/except and finally",
        },
    ),
}

FALSE_POSITIVES = {
    "return-only-in-try": snippet("""
        def foo():
            try:
                return 1
            except ValueError:
                bar()
    """),
}
