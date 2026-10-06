"""Test cases for SIM104. See tests/rules/__init__.py."""

from tests import snippet

TRUE_POSITIVES = {
    "sync-generator": (
        snippet("""
            for item in iterable:
                yield item
        """),
        {
            "1:0 SIM104 Use 'yield from iterable'",
        },
    ),
    "sync-generator-in-async-function": (
        snippet("""
            async def items():
                def inner():
                    for item in iterable:
                        yield item
        """),
        {
            "3:8 SIM104 Use 'yield from iterable'",
        },
    ),
}

FALSE_POSITIVES = {
    "async-generator": snippet("""
        async def items():
            for c in 'abc':
                yield c
    """),
    "async-generator-with": snippet("""
        async def items():
            with open('/etc/passwd') as f:
                for line in f:
                    yield line
    """),
    "yield-other-value": snippet("""
        for item in iterable:
            yield item + 1
    """),
}
