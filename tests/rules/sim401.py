"""Test cases for SIM401. See tests/rules/__init__.py."""

from tests import snippet

TRUE_POSITIVES = {
    "if-else": (
        snippet("""
            if key in a_dict:
                value = a_dict[key]
            else:
                value = 'default'
        """),
        {
            "1:0 SIM401 Use 'value = a_dict.get(key, \"default\")' instead of an if-block",
        },
    ),
    "negated": (
        snippet("""
            if key not in a_dict:
                value = 'default'
            else:
                value = a_dict[key]
        """),
        {
            "1:0 SIM401 Use 'value = a_dict.get(key, \"default\")' instead of an if-block",
        },
    ),
    "issue-84-dict-default": (
        snippet("""
            if "last_name" in test_dict:
                name = test_dict["last_name"]
            else:
                name = test_dict["first_name"]
        """),
        {
            "1:0 SIM401 Use 'name = test_dict.get(\"last_name\", test_dict['first_name'])' instead of an if-block",
        },
    ),
    "issue-84-empty-string": (
        snippet("""
            if "phone_number" in test_dict:
                number = test_dict["phone_number"]
            else:
                number = ""
        """),
        {
            '1:0 SIM401 Use \'number = test_dict.get("phone_number", "")\' instead of an if-block',
        },
    ),
    "issue-89-elif": (
        snippet("""
            if a:
                token = a[1]
            elif 'token' in dct:
                token = dct['token']
            else:
                token = None
        """),
        {
            "3:0 SIM401 Use 'token = dct.get(\"token\", None)' instead of an if-block",
        },
    ),
}

FALSE_POSITIVES = {
    "different-subscripts": snippet("""
        if "foo" in some_dict["a"]:
            some_dict["b"] = some_dict["a"]["foo"]
        else:
            some_dict["a"]["foo"] = some_dict["b"]
    """),
    "no-else": snippet("""
        if key in a_dict:
            value = a_dict[key]
    """),
}
