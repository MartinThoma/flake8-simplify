"""Test cases for SIM118. See tests/rules/__init__.py."""

from tests import snippet

TRUE_POSITIVES = {
    "in-keys": (
        "key in dict.keys()",
        {
            "1:0 SIM118 Use 'key in dict' instead of 'key in dict.keys()'",
        },
    ),
}

FALSE_POSITIVES = {
    "delete-while-iterating": snippet("""
        for key in list(dict.keys()):
            if some_property(key):
                del dict[key]
    """),
    "in-dict": "key in dict",
}
