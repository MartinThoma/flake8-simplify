Release History
===============

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
