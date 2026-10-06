"""Test cases for SIM910. See tests/rules/__init__.py."""

TRUE_POSITIVES = {
    "name-key": (
        "d.get(key, None)",
        {
            "1:0 SIM910 Use 'd.get(key)' instead of 'd.get(key, None)'",
        },
    ),
    "str-key": (
        "d.get('key', None)",
        {
            "1:0 SIM910 Use 'd.get(\"key\")' instead of 'd.get('key', None)'",
        },
    ),
}

FALSE_POSITIVES = {
    "no-default": "d.get(key)",
    "other-default": "d.get(key, 1)",
}
