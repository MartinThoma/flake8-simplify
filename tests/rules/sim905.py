"""Test cases for SIM905. See tests/rules/__init__.py."""

TRUE_POSITIVES = {
    "split": (
        'domains = "de com net org".split()',
        {
            '1:10 SIM905 Use \'["de", "com", "net", "org"]\' instead of \'"de com net org".split()\'',
        },
    ),
}

FALSE_POSITIVES = {
    "variable": "domains = names.split()",
    "with-separator": 'domains = "de,com".split(",")',
    "with-maxsplit": 'domains = "de com net".split(None, 1)',
}
