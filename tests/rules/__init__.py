"""
One data-only module per rule: ``simNNN.py``. Add test cases there; the
shared tests in ``tests/test_rules.py`` pick them up automatically.

``TRUE_POSITIVES``: ``{"case-id": (code, {expected messages})}``. The code
must produce exactly these messages and nothing else.

``FALSE_POSITIVES``: ``{"case-id": code}``. The code is fine, so the rule
must not flag it (other rules may).

Multi-line code is written as ``snippet(\"\"\"...\"\"\")`` (from ``tests``) so it
can be indented like the surrounding code.
"""
