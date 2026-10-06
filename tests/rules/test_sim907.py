import pytest

from tests import _results, _rule_hits, snippet

RULE = "SIM907"

TRUE_POSITIVES = [
    pytest.param(
        snippet("""
            def foo(a: Union[int, None]) -> bool:
              return a
        """),
        {
            "1:11 SIM907 Use 'Optional[int]' instead of 'Union[int, None]'",
        },
        id="union-none",
    ),
]

FALSE_POSITIVES = [
    pytest.param(
        snippet("""
            def foo(a: Optional[int]) -> bool:
              return a
        """),
        id="optional",
    ),
    pytest.param(
        snippet("""
            def foo(a: Union[int, str]) -> bool:
              return a
        """),
        id="union-two-types",
    ),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
