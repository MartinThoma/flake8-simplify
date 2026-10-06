"""Test cases for SIM907. See tests/rules/__init__.py."""

from tests import snippet

TRUE_POSITIVES = {
    "union-none": (
        snippet("""
            def foo(a: Union[int, None]) -> bool:
              return a
        """),
        {
            "1:11 SIM907 Use 'Optional[int]' instead of 'Union[int, None]'",
        },
    ),
}

FALSE_POSITIVES = {
    "optional": snippet("""
        def foo(a: Optional[int]) -> bool:
          return a
    """),
    "union-two-types": snippet("""
        def foo(a: Union[int, str]) -> bool:
          return a
    """),
}
