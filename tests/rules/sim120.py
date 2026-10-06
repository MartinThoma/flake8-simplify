"""Test cases for SIM120. See tests/rules/__init__.py."""

TRUE_POSITIVES = {
    "object-base": (
        "class FooBar(object): pass",
        {
            "1:0 SIM120 Use 'class FooBar:' instead of 'class FooBar(object):'",
        },
    ),
}

FALSE_POSITIVES = {
    "no-base": "class FooBar: pass",
    "other-base": "class FooBar(Base): pass",
    "object-and-other-base": "class FooBar(Base, object): pass",
}
