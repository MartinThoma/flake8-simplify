[![PyPI version](https://badge.fury.io/py/flake8-simplify.svg)](https://badge.fury.io/py/flake8-simplify)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Code on Github](https://img.shields.io/badge/Code-GitHub-brightgreen)](https://github.com/MartinThoma/flake8-simplify)

# flake8-simplify

A [flake8](https://flake8.pycqa.org/en/latest/index.html) plugin that helps you simplify your code.

## Installation

Install with `pip`:

```
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
* `SIM201`: Used 'not a == b' instead of 'a != b'


## Examples

### SIM101

```python
# Bad
isinstance(a, int) or isinstance(a, float)

# Good
isinstance(a, (int, float))
```

### SIM201

```python
# Bad
not a == b

# Good
a != b
```
