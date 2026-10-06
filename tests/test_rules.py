"""Run the test cases in tests/rules/simNNN.py."""

import importlib
import pathlib
import re
from typing import Any

import pytest

from tests import _results, _rule_hits

RULES_DIR = pathlib.Path(__file__).parent / "rules"
RULE_MODULES = sorted(p.stem for p in RULES_DIR.glob("sim*.py"))


def _cases(attribute: str) -> list[Any]:
    params = []
    for module_name in RULE_MODULES:
        module = importlib.import_module(f"tests.rules.{module_name}")
        for case_id, case in getattr(module, attribute).items():
            args = case if isinstance(case, tuple) else (case,)
            params.append(
                pytest.param(
                    module_name.upper(),
                    *args,
                    id=f"{module_name}-{case_id}",
                )
            )
    return params


@pytest.mark.parametrize(
    ("rule", "code", "expected"), _cases("TRUE_POSITIVES")
)
def test_true_positive(rule, code, expected):
    """The code is flagged with exactly the expected messages."""
    assert _results(code) == expected
    assert all(f" {rule} " in message for message in expected)


@pytest.mark.parametrize(("rule", "code"), _cases("FALSE_POSITIVES"))
def test_false_positive(rule, code):
    """The code is fine; this rule must not flag it (others may)."""
    assert _rule_hits(code, rule) == set()


def _implemented_rules() -> set[str]:
    source_dir = pathlib.Path(__file__).parent.parent / "flake8_simplify"
    found: set[str] = set()
    for path in (source_dir / "rules").glob("*.py"):
        found |= set(re.findall(r'"(SIM\d{3}) ', path.read_text()))
    return found


@pytest.mark.parametrize("rule", sorted(_implemented_rules()))
def test_rule_has_true_and_false_positive_cases(rule):
    """Every rule needs tests/rules/simNNN.py with both kinds of case."""
    module = importlib.import_module(f"tests.rules.{rule.lower()}")
    assert module.TRUE_POSITIVES, f"{rule} has no true-positive test"
    assert module.FALSE_POSITIVES, f"{rule} has no false-positive test"
