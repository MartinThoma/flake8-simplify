"""Test cases for SIM101. See tests/rules/__init__.py."""

from tests import snippet

TRUE_POSITIVES = {
    "two-lines": (
        snippet("""
            isinstance(a, int) or isinstance(a, float)
            isinstance(b, bool) or isinstance(b, str)
        """),
        {
            "1:0 SIM101 Multiple isinstance-calls which can be merged into a single call for variable 'a'",
            "2:0 SIM101 Multiple isinstance-calls which can be merged into a single call for variable 'b'",
        },
    ),
    "after-other-code": (
        snippet("""
            foo(a, b, c) or bar(a, b)
            isinstance(b, bool) or isinstance(b, str)
        """),
        {
            "2:0 SIM101 Multiple isinstance-calls which can be merged into a single call for variable 'b'",
        },
    ),
}

FALSE_POSITIVES = {
    "single-call": "isinstance(a, int) or foo",
    "and-instead-of-or": "isinstance(b, bool) and isinstance(b, str)",
    "other-function": "isfoo(a, int) or isfoo(a, float)",
    "different-variables": "isinstance(a, int) or isinstance(b, float)",
}
