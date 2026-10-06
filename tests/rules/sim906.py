"""Test cases for SIM906. See tests/rules/__init__.py."""

TRUE_POSITIVES = {
    "base": (
        "os.path.join(a,os.path.join(b,c))",
        {
            "1:0 SIM906 Use 'os.path.join(a, b, c)' instead of 'os.path.join(a, os.path.join(b, c))'",
        },
    ),
    "str-arg": (
        "os.path.join(a,os.path.join('b',c))",
        {
            "1:0 SIM906 Use 'os.path.join(a, 'b', c)' instead of 'os.path.join(a, os.path.join('b', c))'",
        },
    ),
    "attribute-arg": (
        "os.path.join(a, os.path.join(b, c.d))",
        {
            "1:0 SIM906 Use 'os.path.join(a, b, c.d)' instead of 'os.path.join(a, os.path.join(b, c.d))'",
        },
    ),
    "call-and-starred-args": (
        "os.path.join(f(), os.path.join(*parts))",
        {
            "1:0 SIM906 Use 'os.path.join(f(), *parts)' instead of 'os.path.join(f(), os.path.join(*parts))'",
        },
    ),
}

FALSE_POSITIVES = {
    "flat": "os.path.join(a, b, c)",
    "other-function": "foo.join(a, foo.join(b, c))",
}
