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
    "four-branches-reported-once": (
        snippet("""
            if x == 1:
                return "a"
            elif x == 2:
                return "b"
            elif x == 3:
                return "c"
            elif x == 4:
                return "d"
        """),
        {
            "1:0 SIM116 Use a dictionary lookup instead of 3+ if/elif-statements: return {1: 'a', 2: 'b', 3: 'c', 4: 'd'}.get(x)",
        },
    ),
    "chain-after-other-condition": (
        snippet("""
            if y:
                return 0
            elif x == 1:
                return "a"
            elif x == 2:
                return "b"
            elif x == 3:
                return "c"
        """),
        {
            "3:0 SIM116 Use a dictionary lookup instead of 3+ if/elif-statements: return {1: 'a', 2: 'b', 3: 'c'}.get(x)",
        },
    ),
    "non-string-values": (
        snippet("""
            if x == "a":
                return 1
            elif x == "b":
                return B
            elif x == "c":
                return "c"
        """),
        {
            "1:0 SIM116 Use a dictionary lookup instead of 3+ if/elif-statements: return {'a': 1, 'b': B, 'c': 'c'}.get(x)",
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
    "call-in-first-branch": snippet("""
        if x == 1:
            return g()
        elif x == 2:
            return "b"
        elif x == 3:
            return "c"
    """),
}
