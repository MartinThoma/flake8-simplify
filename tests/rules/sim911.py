"""Test cases for SIM911. See tests/rules/__init__.py."""

TRUE_POSITIVES = {
    "keys-values": (
        "zip(d.keys(), d.values())",
        {
            "1:0 SIM911 Use 'd.items()' instead of 'zip(d.keys(), d.values())'",
        },
    ),
}

FALSE_POSITIVES = {
    "keys-keys": "zip(d.keys(), d.keys())",
    "different-dicts": "zip(d1.keys(), d2.values())",
    "keys-and-name": "zip(d1.keys(), values)",
    "names": "zip(keys, values)",
}
