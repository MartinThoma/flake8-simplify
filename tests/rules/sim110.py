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
    "same-return-after-loop": snippet("""
        for x in iterable:
            if check(x):
                return True
        return True
    """),
    "if-with-else": snippet("""
        for x in iterable:
            if check(x):
                return True
            else:
                foo()
        return False
    """),
    "for-else": snippet("""
        for x in iterable:
            if check(x):
                return True
        else:
            foo()
        return False
    """),
    "return-in-other-branch": snippet("""
        if a:
            for x in iterable:
                if check(x):
                    return True
        else:
            return False
    """),
}
