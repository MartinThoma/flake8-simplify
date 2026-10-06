"""Test cases for SIM111. See tests/rules/__init__.py."""

from tests import snippet

TRUE_POSITIVES = {
    "all-negated-call": (
        snippet("""
            for x in iterable:
                if check(x):
                    return False
            return True
        """),
        {
            "1:0 SIM111 Use 'return all(not check(x) for x in iterable)'",
        },
    ),
    "all-negated-condition": (
        snippet("""
            for x in iterable:
                if not x.is_empty():
                    return False
            return True
        """),
        {
            "1:0 SIM111 Use 'return all(x.is_empty() for x in iterable)'",
        },
    ),
    "compound-condition": (
        snippet("""
            for x in iterable:
                if a(x) and b(x):
                    return False
            return True
        """),
        {
            "1:0 SIM111 Use 'return all(not (a(x) and b(x)) for x in iterable)'",
        },
    ),
    "negated-compound-condition": (
        snippet("""
            for x in iterable:
                if not (a(x) or b(x)):
                    return False
            return True
        """),
        {
            "1:0 SIM111 Use 'return all(a(x) or b(x) for x in iterable)'",
        },
    ),
    "negated-chained-comparison-with-strings": (
        snippet("""
            for letter in content:
                if not 'a' <= letter <= 'z':
                    return False
            return True
        """),
        {
            "1:0 SIM111 Use 'return all('a' <= letter <= 'z' for letter in content)'",
        },
    ),
}

FALSE_POSITIVES = {
    "statement-between-loop-and-return": snippet("""
        for a in my_list:
          if a == 2:
            return False
        call_method()
        return True
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
                return False
        return False
    """),
    "for-else": snippet("""
        for x in iterable:
            if check(x):
                return False
        else:
            foo()
        return True
    """),
}
