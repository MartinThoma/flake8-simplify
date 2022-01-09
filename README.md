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

Python-specific rules:

* `SIM101`: Multiple isinstance-calls which can be merged into a single call by
  using a tuple as a second argument ([example](#SIM101))
* [`SIM104`](https://github.com/MartinThoma/flake8-simplify/issues/4) ![](https://shields.io/badge/-legacyfix-inactive): Use 'yield from iterable' (introduced in Python 3.3, see [PEP 380](https://docs.python.org/3/whatsnew/3.3.html#pep-380)) ([example](#SIM104))
* [`SIM105`](https://github.com/MartinThoma/flake8-simplify/issues/5): Use ['contextlib.suppress(...)'](https://docs.python.org/3/library/contextlib.html#contextlib.suppress) instead of try-except-pass ([example](#SIM105))
* [`SIM107`](https://github.com/MartinThoma/flake8-simplify/issues/9): Don't use `return` in try/except and finally  ([example](#SIM107))
* [`SIM108`](https://github.com/MartinThoma/flake8-simplify/issues/12): Use the ternary operator if it's reasonable  ([example](#SIM108))
* [`SIM109`](https://github.com/MartinThoma/flake8-simplify/issues/11): Use a tuple to compare a value against multiple values ([example](#SIM109))
* [`SIM110`](https://github.com/MartinThoma/flake8-simplify/issues/15): Use [any(...)](https://docs.python.org/3/library/functions.html#any)  ([example](#SIM110))
* [`SIM111`](https://github.com/MartinThoma/flake8-simplify/issues/15): Use [all(...)](https://docs.python.org/3/library/functions.html#all) ([example](#SIM111))
* [`SIM113`](https://github.com/MartinThoma/flake8-simplify/issues/18): Use enumerate instead of manually incrementing a counter ([example](#SIM113))
* [`SIM114`](https://github.com/MartinThoma/flake8-simplify/issues/10): Combine conditions via a logical or to prevent duplicating code ([example](#SIM114))
* [`SIM115`](https://github.com/MartinThoma/flake8-simplify/issues/17): Use context handler for opening files ([example](#SIM115))
* [`SIM116`](https://github.com/MartinThoma/flake8-simplify/issues/31): Use a dictionary instead of many if/else equality checks ([example](#SIM116))
* [`SIM117`](https://github.com/MartinThoma/flake8-simplify/issues/35): Merge with-statements that use the same scope ([example](#SIM117))
* [`SIM119`](https://github.com/MartinThoma/flake8-simplify/issues/37) ![](https://shields.io/badge/-legacyfix-inactive): Use dataclasses for data containers ([example](#SIM119))
* `SIM120` ![](https://shields.io/badge/-legacyfix-inactive): Use 'class FooBar:' instead of 'class FooBar(object):' ([example](#SIM120))

Simplifying Comparations:

* `SIM201`: Use 'a != b' instead of 'not a == b' ([example](#SIM201))
* `SIM202`: Use 'a == b' instead of 'not a != b' ([example](#SIM202))
* `SIM203`: Use 'a not in b' instead of 'not (a in b)' ([example](#SIM203))
* `SIM204`: Use 'a >= b' instead of 'not (a < b)' ([example](#SIM204))
* `SIM205`: Use 'a > b' instead of 'not (a <= b)' ([example](#SIM205))
* `SIM206`: Use 'a <= b' instead of 'not (a > b)' ([example](#SIM206))
* `SIM207`: Use 'a < b' instead of 'not (a <= b)' ([example](#SIM207))
* `SIM208`: Use 'a' instead of 'not (not a)' ([example](#SIM208))
* `SIM210`: Use 'bool(a)' instead of 'True if a else False' ([example](#SIM210))
* `SIM211`: Use 'not a' instead of 'False if a else True' ([example](#SIM211))
* [`SIM212`](https://github.com/MartinThoma/flake8-simplify/issues/6): Use 'a if a else b' instead of 'b if not a else a' ([example](#SIM212))
* [`SIM220`](https://github.com/MartinThoma/flake8-simplify/issues/6): Use 'False' instead of 'a and not a' ([example](#SIM220))
* [`SIM221`](https://github.com/MartinThoma/flake8-simplify/issues/6): Use 'True' instead of 'a or not a' ([example](#SIM221))
* [`SIM222`](https://github.com/MartinThoma/flake8-simplify/issues/6): Use 'True' instead of '... or True' ([example](#SIM222))
* [`SIM223`](https://github.com/MartinThoma/flake8-simplify/issues/6): Use 'False' instead of '... and False' ([example](#SIM223))
* [`SIM300`](https://github.com/MartinThoma/flake8-simplify/issues/16): Use 'age == 42' instead of '42 == age' ([example](#SIM300))

Simplifying usage of dictionaries:

* [`SIM401`](https://github.com/MartinThoma/flake8-simplify/issues/72): Use 'a_dict.get(key, "default_value")' instead of an if-block ([example](#SIM401))
* [`SIM118`](https://github.com/MartinThoma/flake8-simplify/issues/40): Use 'key in dict' instead of 'key in dict.keys()' ([example](#SIM118))

General Code Style:

* `SIM102`: Use a single if-statement instead of nested if-statements ([example](#SIM102))
* [`SIM103`](https://github.com/MartinThoma/flake8-simplify/issues/3): Return the boolean condition directly ([example](#SIM103))
* [`SIM106`](https://github.com/MartinThoma/flake8-simplify/issues/8): Handle error-cases first ([example](#SIM106))
* [`SIM112`](https://github.com/MartinThoma/flake8-simplify/issues/19): Use CAPITAL environment variables ([example](#SIM112))

You might have good reasons to ignore some rules. To do that, use the standard Flake8 configuration. For example, within the `setup.cfg` file:

```python
[flake8]
ignore = SIM106, SIM113, SIM119
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

### SIM108

```python
# Bad
if a:
    b = c
else:
    b = d

# Good
b = c if a else d
```

### SIM109

```python
# Bad
if a == b or a == c:
    d

# Good
if a in (b, c):
    d
```

### SIM110

```python
# Bad
for x in iterable:
    if check(x):
        return True
return False

# Good
return any(check(x) for x in iterable)
```

### SIM111

```python
# Bad
for x in iterable:
    if check(x):
        return False
return True

# Good
return all(not check(x) for x in iterable)
```

### SIM112

```python
# Bad
os.environ["foo"]
os.environ.get("bar")

# Good
os.environ["FOO"]
os.environ.get("BAR")
```

### SIM113

Using [`enumerate`](https://docs.python.org/3/library/functions.html#enumerate) in simple cases like the loops below is a tiny bit easier to read as the reader does not have to figure out where / when the loop variable is incremented (or if it is incremented in multiple places).

```python
# Bad
idx = 0
for el in iterable:
    ...
    idx += 1

# Good
for idx, el in enumerate(iterable):
    ...
```

### SIM114

```python
# Bad
if a:
    b
elif c:
    b

# Good
if a or c:
    b
```

### SIM115

```python
# Bad
f = open(...)
...  # (do something with f)
f.close()

# Good
with open(...) as f:
    ...  # (do something with f)
```

### SIM116

```python
# Bad
if a == "foo":
    return "bar"
elif a == "bar":
    return "baz"
elif a == "boo":
    return "ooh"
else:
    return 42

# Good
mapping = {"foo": "bar", "bar": "baz", "boo": "ooh"}
return mapping.get(a, 42)
```

### SIM117

```python
# Bad
with A() as a:
    with B() as b:
        print("hello")

# Good
with A() as a, B() as b:
    print("hello")
```

Thank you for pointing this one out, [Aaron Gokaslan](https://github.com/Skylion007)!

### SIM118

```python
# Bad
key in a_dict.keys()

# Good
key in a_dict
```

Thank you for pointing this one out, [Aaron Gokaslan](https://github.com/Skylion007)!

### SIM119

Dataclasses were introduced with [PEP 557](https://www.python.org/dev/peps/pep-0557/)
in Python 3.7. The main reason not to use dataclasses is to support legacy Python versions.

Dataclasses create a lot of the boilerplate code for you:

* `__init__`
* `__eq__`
* `__hash__`
* `__str__`
* `__repr__`

A lot of projects use them:

* [black](https://github.com/psf/black/blob/master/src/black/__init__.py#L1472)

### SIM120

```
# Bad
class FooBar(object):
    ...

# Good
class FooBar:
    ...
```

Both notations are equivalent in Python 3, but the second one is shorter.

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

### SIM300

```python
# Bad; This is called a "Yoda-Condition"
42 == age

# Good
age == 42
```

### SIM401

```python
# Bad
if key in a_dict:
    value = a_dict[key]
else:
    value = "default_value"

# Good
thing = a_dict.get(key, "default_value")
```
