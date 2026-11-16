"""Test cases for SIM906. See tests/rules/__init__.py."""

TRUE_POSITIVES = {
    "preserve-nested-tail": (
        "os.path.join(os.path.join(a, b), os.path.join(c, d))",
        {
            "1:0 SIM906 Use 'os.path.join(a, b, os.path.join(c, d))' instead of 'os.path.join(os.path.join(a, b), os.path.join(c, d))'",
        },
    ),
    "recursive-first-argument": (
        "os.path.join(os.path.join(os.path.join(a, b), c), d)",
        {
            "1:0 SIM906 Use 'os.path.join(a, b, c, d)' instead of 'os.path.join(os.path.join(os.path.join(a, b), c), d)'",
            "1:13 SIM906 Use 'os.path.join(a, b, c)' instead of 'os.path.join(os.path.join(a, b), c)'",
        },
    ),
    "base": (
        "os.path.join(os.path.join(a,b),c)",
        {
            "1:0 SIM906 Use 'os.path.join(a, b, c)' instead of 'os.path.join(os.path.join(a, b), c)'",
        },
    ),
    "str-arg": (
        "os.path.join(os.path.join(a,'b'),c)",
        {
            "1:0 SIM906 Use 'os.path.join(a, 'b', c)' instead of 'os.path.join(os.path.join(a, 'b'), c)'",
        },
    ),
    "attribute-arg": (
        "os.path.join(os.path.join(a, b), c.d)",
        {
            "1:0 SIM906 Use 'os.path.join(a, b, c.d)' instead of 'os.path.join(os.path.join(a, b), c.d)'",
        },
    ),
    "call-and-starred-args": (
        "os.path.join(os.path.join(f(), *parts), tail)",
        {
            "1:0 SIM906 Use 'os.path.join(f(), *parts, tail)' instead of 'os.path.join(os.path.join(f(), *parts), tail)'",
        },
    ),
}

FALSE_POSITIVES = {
    "nested-tail": "os.path.join(a, os.path.join(b, c))",
    "windows-drive-relative": "os.path.join('C:', os.path.join('a', 'C:'))",
    "empty-starred-tail": "os.path.join(a, os.path.join(*parts))",
    "flat": "os.path.join(a, b, c)",
    "other-function": "foo.join(a, foo.join(b, c))",
}
