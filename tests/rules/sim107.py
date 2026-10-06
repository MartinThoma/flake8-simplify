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
    "return-in-except": (
        snippet("""
            def foo():
                try:
                    bar()
                except ValueError:
                    return 1
                finally:
                    return 2
        """),
        {
            "7:8 SIM107 Don't use return in try/except and finally",
        },
    ),
    "nested-return-in-try": (
        snippet("""
            def foo():
                try:
                    if a:
                        return 1
                finally:
                    return 2
        """),
        {
            "6:8 SIM107 Don't use return in try/except and finally",
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
    "return-only-in-finally": snippet("""
        def foo():
            try:
                bar()
            finally:
                return 2
    """),
    "return-in-nested-function": snippet("""
        def foo():
            try:
                def inner():
                    return 1
            finally:
                return 2
    """),
}
