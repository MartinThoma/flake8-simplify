"""Test cases for SIM110. See tests/rules/__init__.py."""

from tests import snippet

TRUE_POSITIVES = {
    "any": (
        snippet("""
            for x in iterable:
                if check(x):
                    return True
            return False
        """),
        {
            "1:0 SIM110 Use 'return any(check(x) for x in iterable)'",
        },
    ),
}

FALSE_POSITIVES = {
    "raise-after-loop": snippet("""
        for el in [1,2,3]:
            if is_true(el):
                return True
        raise Exception
    """),
    "non-bool-returns": snippet("""
        for x in iterable:
            if check(x):
                return "foo"
        return "bar"
    """),
}
