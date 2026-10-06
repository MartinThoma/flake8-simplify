"""Test cases for SIM103. See tests/rules/__init__.py."""

from tests import snippet

TRUE_POSITIVES = {
    "true-false": (
        snippet("""
            if a:
                return True
            else:
                return False
        """),
        {
            "1:0 SIM103 Return the condition a directly",
        },
    ),
}

FALSE_POSITIVES = {
    "non-bool-returns": snippet("""
        if a:
            return 1
        else:
            return 2
    """),
    "no-else": snippet("""
        if a:
            return True
        return 2
    """),
}
