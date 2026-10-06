"""Test cases for SIM116. See tests/rules/__init__.py."""

from tests import snippet

TRUE_POSITIVES = {
    "three-branches": (
        snippet("""
            if a == "foo":
                return "bar"
            elif a == "bar":
                return "baz"
            elif a == "boo":
                return "ooh"
            else:
                return 42
        """),
        {
            "1:0 SIM116 Use a dictionary lookup instead of 3+ if/elif-statements: return {'foo': 'bar', 'bar': 'baz', 'boo': 'ooh'}.get(a, 42)",
        },
    ),
    "repeated-key-first-wins": (
        snippet("""
            if x == "a":
                return "1"
            elif x == "b":
                return "2"
            elif x == "c":
                return "3"
            elif x == "c":
                return "4"
        """),
        {
            "1:0 SIM116 Use a dictionary lookup instead of 3+ if/elif-statements: return {'a': '1', 'b': '2', 'c': '3'}.get(x)",
        },
    ),
}

FALSE_POSITIVES = {
    "non-constant-return": snippet("""
        if a == "foo":
            return "bar"
        elif a == "bar":
            return baz()
        elif a == "boo":
            return "ooh"
        else:
            return 42
    """),
    "two-branches": snippet("""
        if a == "foo":
            return "bar"
        elif a == "bar":
            return "baz"
        else:
            return 42
    """),
}
