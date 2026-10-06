"""Test cases for SIM105. See tests/rules/__init__.py."""

from tests import snippet

TRUE_POSITIVES = {
    "specific-exception": (
        snippet("""
            try:
                foo()
            except ValueError:
                pass
        """),
        {
            "1:0 SIM105 Use 'contextlib.suppress(ValueError)'",
        },
    ),
    "bare-except": (
        snippet("""
            try:
                foo()
            except:
                pass
        """),
        {
            "1:0 SIM105 Use 'contextlib.suppress(Exception)'",
        },
    ),
}

FALSE_POSITIVES = {
    "handler-does-something": snippet("""
        try:
            foo()
        except ValueError:
            bar()
    """),
    "has-else": snippet("""
        try:
            foo()
        except ValueError:
            pass
        else:
            bar()
    """),
    "has-finally": snippet("""
        try:
            foo()
        except ValueError:
            pass
        finally:
            bar()
    """),
}
