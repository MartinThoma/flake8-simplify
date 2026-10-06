"""
One module per rule: ``test_simNNN.py``.

Each module defines two lists, which is where new test cases go:

* ``TRUE_POSITIVES``: ``pytest.param(code, expected_messages, id=...)``. The
  code must produce exactly these messages and nothing else.
* ``FALSE_POSITIVES``: ``pytest.param(code, id=...)``. The code is fine and
  the rule must not flag it (other rules may).
"""
