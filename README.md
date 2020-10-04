[![PyPI version](https://badge.fury.io/py/flake8-simplify.svg)](https://badge.fury.io/py/flake8-simplify)
[![Code on Github](https://img.shields.io/badge/Code-GitHub-brightgreen)](https://github.com/MartinThoma/flake8-simplify)
[![Actions Status](https://github.com/MartinThoma/flake8-simplify/workflows/Unit%20Tests/badge.svg)](https://github.com/MartinThoma/flake8-simplify/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# flake8-simplify

A [flake8](https://flake8.pycqa.org/en/latest/index.html) plugin that helps you simplify your code.

## Installation

Install with `pip`:

```bash
pip install flake8-simplify
```

Python 3.6 to 3.8 are supported.


## Usage

Just call `flake8 .` in your package or `flake your.py`:

```
$ flake8 .
./foo/__init__.py:690:12: SIM101 Multiple isinstance-calls which can be merged into a single call for variable 'other'
```


## Rules

* `SIM101`: Multiple isinstance-calls which can be merged into a single call by
  using a tuple as a second argument.
* `SIM102`: Use a single if-statement instead of nested if-statements
* `SIM103`: Return the boolean condition directly
* `SIM104`: Use 'yield from iterable' (introduced in Python 3.3, see [PEP 380](https://docs.python.org/3/whatsnew/3.3.html#pep-380))
* `SIM105`: Use ['contextlib.suppress(...)'](https://docs.python.org/3/library/contextlib.html#contextlib.suppress) instead of try-except-pass
* `SIM106`: Handle error-cases first
* `SIM107`: Don't use `return` in try/except and finally.
* `SIM201`: Use 'a != b' instead of 'not a == b'
* `SIM202`: Use 'a == b' instead of 'not a != b'
* `SIM203`: Use 'a not in b' instead of 'not (a in b)'
* `SIM204`: Use 'a >= b' instead of 'not (a < b)'
* `SIM205`: Use 'a > b' instead of 'not (a <= b)'
* `SIM206`: Use 'a <= b' instead of 'not (a > b)'
* `SIM207`: Use 'a < b' instead of 'not (a <= b)'
* `SIM208`: Use 'a' instead of 'not (not a)'
* `SIM210`: Use 'bool(a)' instead of 'True if a else False'
* `SIM211`: Use 'not a' instead of 'False if a else True'
* `SIM212`: Use 'a if a else b' instead of 'b if not a else a'
* `SIM220`: Use 'False' instead of 'a and not a'
* `SIM221`: Use 'True' instead of 'a or not a'
* `SIM222`: Use 'True' instead of '... or True'
* `SIM223`: Use 'False' instead of '... and False'

The `SIM201` - `SIM208` rules have one good reason to be ignored: When you are
checking an error condition:

```python
if not correct_condition:
    handle_error()  # e.g. raise Exception
```


## Examples

### SIM101

```python
# Bad
isinstance(a, int) or isinstance(a, float)

# Good
isinstance(a, (int, float))
```

### SIM102

```python
# Bad
if a:
    if b:
        c

# Good
if a and b:
    c
```

### SIM107

```python
# Bad: This example returns 3!
def foo():
    try:
        1 / 0
        return "1"
    except:
        return "2"
    finally:
        return "3"


# Good
def foo():
    return_value = None
    try:
        1 / 0
        return_value = "1"
    except:
        return_value = "2"
    finally:
        return_value = "3"  # you might also want to check if "except" happened
    return return_value
```

### SIM201

```python
# Bad
not a == b

# Good
a != b
```

### SIM202

```python
# Bad
not a != b

# Good
a == b
```

### SIM203

```python
# Bad
not a in b

# Good
a not in b
```

### SIM204

```python
# Bad
not a < b

# Good
a >= b
```

### SIM205

```python
# Bad
not a <= b

# Good
a > b
```

### SIM206

```python
# Bad
not a > b

# Good
a <= b
```

### SIM207

```python
# Bad
not a >= b

# Good
a < b
```

### SIM208

```python
# Bad
not (not a)

# Good
a
```

### SIM210

```python
# Bad
True if a else False

# Good
bool(a)
```

### SIM211

```python
# Bad
False if a else True

# Good
not a
```

### SIM212

```python
# Bad
b if not a else a

# Good
a if a else b
```

### SIM220

```python
# Bad
a and not a

# Good
False
```

### SIM221

```python
# Bad
a or not a

# Good
True
```

### SIM222

```python
# Bad
... or True

# Good
True
```

### SIM223

```python
# Bad
... and False

# Good
False
```
