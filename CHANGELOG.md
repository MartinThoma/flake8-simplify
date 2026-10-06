Release History
===============

### 0.31.1
Release on 06.10.2026

False-positives fixed:

* SIM103: if/else that returns the same constant in both branches
* SIM105: try-except-pass with a `finally` block
* SIM110 / SIM111: The return after the loop was not checked, and an
  `else` / `elif` inside the loop or a for-else was ignored
* SIM116: A function call in the first branch (#113). A chain of 4+
  branches is now reported only once.
* SIM401: The dict that is read was not compared with the dict in the
  condition. For `not in`, the assigned variables were not compared.
* SIM905: `str.split()` with a separator or maxsplit
* SIM908: The dict that is read was not compared with the dict in the
  condition

False-negatives fixed (these rules can report more than before):

* SIM102: `if __name__ != "__main__":` was treated like a main guard
* SIM104: Sync generators nested in an async function
* SIM107: Returns in `except` blocks, nested returns, and returns in the
  `else` block of a try
* SIM108: if/else nested in an if-block that assigns the same variable

Wrong suggestions fixed:

* SIM103: `if a: return False else: return True` suggests `not a`
* SIM111: Negated conditions like `not (a or b)` no longer get a double
  negation
* SIM116: Values are shown as code instead of strings, e.g.
  `{'a': 1, 'b': B}` instead of `{'a': '1', 'b': 'B'}`. For a repeated
  key, the first branch wins.
* SIM906: Arguments other than names and strings were dropped
* Expressions like `'a' <= x <= 'z'` were shown with broken quotes

Other changes:

* Rules register themselves with the `@rule` decorator
  (`flake8_simplify/registry.py`); the rule index is built once instead
  of for every file
* Tests: one data file per rule in `tests/rules/` with true- and
  false-positive cases

### 0.31.0
Release on 06.10.2026

BREAKING CHANGE:

* Dropped support for Python 3.9

Other changes:

* SIM904: A false-positive was fixed

### 0.30.0
Release on 01.01.2025

BREAKING CHANGE:

* Deprecated support for Python 3.6, 3.7 and 3.8. Minimum supported
  Python version is now 3.9.

Other changes:

* Added support for Python 3.13
* Removed dependency on `astor`


### 0.21.0
Release on 23.09.2023

New rules:

* SIM911: zip(dict.keys(), dict.values()) → dict.items()

### 0.20.0
Release on 30.03.2023

New rules:

* SIM910: dict.get(key, None) → dict.get(key)

### 0.19.3
Released on 28.07.2022

* SIM104: Remove false-positives in case the loop is not a direct child of
          an async function (#147) by @wyuenho

### 0.19.2
Released on 29.03.2022

Removed rules due to false-positives:

* SIM903: Positional-only parameters cannot be identified in the AST
* SIM909: Class attribute assignments are not reflexive assignments

### 0.19.1
Released on 29.03.2022

Removed rules due to false-positives:

* SIM902: Positional-only parameters cannot be identified in the AST
* SIM908: Ensure that the assigned name is equal to the name in the if.test

### 0.19.0
Released on 28.03.2022

New rules:

* SIM902: Use keyword-argument instead of magic boolean
* SIM903: Use keyword-argument instead of magic number
* SIM907: Use Optional[Type] instead of Union[Type, None]
* SIM908: Use ".get" instead of "if X in dict: dict[X]"
* SIM909: Avoid reflexive assignments

Removed rules due to false-positives:

* SIM119: Hinting to dataclasses in a proper way is hard

Fixed false-positives:

* SIM108: Encourage the use of a terniary operator only when it is
          actually possible
* SIM111: Recommending to use all/any only if there is no side-effect after
          the for-loop
* SIM116: When a function is called, we cannot simply convert the
          if-else block to a dictionary

### 0.18.2
Released on 26.03.2022

Removed rules due to false-positives:

* SIM204: Use 'a >= b' instead of 'not (a < b)'
* SIM205: Use 'a > b' instead of 'not (a <= b)'
* SIM206: Use 'a <= b' instead of 'not (a > b)'
* SIM207: Use 'a < b' instead of 'not (a <= b)'

Fixed false-positives:

* SIM113: Use enumerate instead of manually incrementing a counter

Maintenance:

* Split a way-too-big module into smaller modules

### 0.18.1
Released on 24.02.2022

Only distribute the `flake8_simplify` package. `0.18.0` did also distribute
the `tests` package which caused issues in some systems.

### 0.18.0
Released on 20.02.2022

New rules since 0.17.0:

* SIM906: Merge nested os.path.join calls

Maintenance:

* Restructure repository to simplify future development. It's time for more
  than one file.

### 0.17.1
Released on 16.02.2022

* SIM904: Removed false-positives that happened when a dictionary value was
          derived from another value of the same dictionary.

### 0.17.0
Released on 13.02.2022

* SIM905: Added
