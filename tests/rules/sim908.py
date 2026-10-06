"""Test cases for SIM908. See tests/rules/__init__.py."""

from tests import snippet

TRUE_POSITIVES = {
    "default-then-override": (
        snippet("""
            name = "some_default"
            if "some_key" in some_dict:
                name = some_dict["some_key"]
        """),
        {
            '2:0 SIM908 Use \'some_dict.get("some_key")\' instead of \'if "some_key" in some_dict: some_dict["some_key"]\'',
        },
    ),
}

FALSE_POSITIVES = {
    "issue-125": snippet("""
        if "." in resistance:
            # Swap '.' with suffix
            resistance = resistance.replace(".", resistance[-1])[:-1]
    """),
    "issue-125-simplified": snippet("""
        if "." in iterable:
            iterable = iterable[:-1]
    """),
}
