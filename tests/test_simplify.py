# Core Library
import ast
from typing import Iterable, Set

# Third party
import pytest

# First party
from flake8_simplify import Plugin, get_if_body_pairs


def _results(code: str) -> Set[str]:
    """Apply the plugin to the given code."""
    tree = ast.parse(code)
    plugin = Plugin(tree)
    return {f"{line}:{col} {msg}" for line, col, msg, _ in plugin.run()}


def test_trivial_case():
    """Check the plugins output for no code."""
    assert _results("") == set()


def test_plugin_version():
    assert isinstance(Plugin.version, str)
    assert "." in Plugin.version


def test_plugin_name():
    assert isinstance(Plugin.name, str)


def test_single_isinstance():
    ret = _results("isinstance(a, int) or foo")
    assert ret == set()


def test_fine_code():
    ret = _results("- ( a+ b)")
    assert ret == set()


def test_multiple_isinstance_multiple_lines():
    ret = _results(
        "isinstance(a, int) or isinstance(a, float)\n"
        "isinstance(b, bool) or isinstance(b, str)"
    )
    assert ret == {
        (
            "1:0 SIM101 Multiple isinstance-calls which can be merged "
            "into a single call for variable 'a'"
        ),
        (
            "2:0 SIM101 Multiple isinstance-calls which can be merged "
            "into a single call for variable 'b'"
        ),
    }


def test_first_wrong_then_multiple_isinstance():
    ret = _results(
        "foo(a, b, c) or bar(a, b)\nisinstance(b, bool) or isinstance(b, str)"
    )
    assert ret == {
        (
            "2:0 SIM101 Multiple isinstance-calls which can be merged "
            "into a single call for variable 'b'"
        ),
    }


def test_multiple_isinstance_and():
    ret = _results("isinstance(b, bool) and isinstance(b, str)")
    assert ret == set()


def test_multiple_other_function():
    ret = _results("isfoo(a, int) or isfoo(a, float)")
    assert ret == set()


def test_sim102_pattern1():
    ret = _results(
        """if a:
    if b:
        c"""
    )
    assert ret == {
        (
            "1:0 SIM102 Use a single if-statement instead of "
            "nested if-statements"
        )
    }


def test_sim102_pattern2():
    ret = _results(
        """if a:
    pass
elif b:
    if c:
        d"""
    )
    assert ret in [
        {  # Python 3.7+
            "3:0 SIM102 Use a single if-statement instead of "
            "nested if-statements"
        },
        {
            # Python 3.6
            "3:5 SIM102 Use a single if-statement instead of "
            "nested if-statements"
        },
    ]


def test_sim102_not_active1():
    ret = _results(
        """if a:
    if b:
        c
    else:
        d"""
    )
    assert ret == set()


def test_sim102_not_active2():
    ret = _results(
        """if a:
    d
    if b:
        c"""
    )
    assert ret == set()


def test_sim103_true_false():
    ret = _results(
        """if a:
    return True
else:
    return False"""
    )
    assert ret == {"1:0 SIM103 Return the condition a directly"}


def test_sim104():
    ret = _results(
        """for item in iterable:
    yield item"""
    )
    assert ret == {"1:0 SIM104 Use 'yield from iterable'"}


def test_sim105():
    ret = _results(
        """try:
    foo()
except ValueError:
    pass"""
    )
    assert ret == {"1:0 SIM105 Use 'contextlib.suppress(ValueError)'"}


def test_sim105_pokemon():
    ret = _results(
        """try:
    foo()
except:
    pass"""
    )
    assert ret == {"1:0 SIM105 Use 'contextlib.suppress(Exception)'"}


def test_sim106():
    ret = _results(
        """if cond:
    a
    b
    c
else:
    raise Exception"""
    )
    assert ret == {"1:0 SIM106 Handle error-cases first"}


def test_sim106_no():
    ret = _results(
        """if cond:
    raise Exception
else:
    raise Exception"""
    )
    assert ret == set()


def test_sim107():
    ret = _results(
        """def foo():
    try:
        1 / 0
        return "1"
    except:
        return "2"
    finally:
        return "3" """
    )
    assert ret == {"8:8 SIM107 Don't use return in try/except and finally"}


def test_sim108():
    ret = _results(
        """if a:
    b = c
else:
    b = d"""
    )
    exp = (
        "1:0 SIM108 Use ternary operator "
        "'b = c if a else d' instead of if-else-block"
    )
    assert ret == {exp}


def test_sim109():
    ret = _results("a == b or a == c")
    assert ret == {
        "1:0 SIM109 Use 'a in [b, c]' instead of 'a == b or a == c'"
    }


def test_sim110_any():
    def opt1(iterable):
        for x in iterable:  # noqa
            if x:
                return True
        return False

    def opt2(iterable):
        return any(x for x in iterable)

    ret = _results(
        """for x in iterable:
    if check(x):
        return True
return False"""
    )
    assert ret == {"1:0 SIM110 Use 'return any(check(x) for x in iterable)'"}


@pytest.mark.xfail(reason="See issue #34: False-positive for SIM110")
def test_sim110_raise_exception():
    ret = _results(
        """
for el in [1,2,3]:
    if is_true(el):
        return True
raise Exception"""
    )
    assert ret == set()


def test_sim111_all():
    def opt1(iterable: Iterable[bool]) -> bool:
        for x in iterable:  # noqa
            if x:
                return False
        return True

    def opt2(iterable: Iterable[bool]) -> bool:
        return all(not x for x in iterable)

    iterables = ((True,), (False,))
    for iterable in iterables:
        assert opt1(iterable) == opt2(iterable)

    ret = _results(
        """for x in iterable:
    if check(x):
        return False
return True"""
    )
    assert ret == {
        "1:0 SIM111 Use 'return all(not check(x) for x in iterable)'"
    }


def test_sim111_all2():
    def opt1(iterable: Iterable[bool]) -> bool:
        for x in iterable:  # noqa
            if not x:
                return False
        return True

    def opt2(iterable: Iterable[bool]) -> bool:
        return all(x for x in iterable)

    iterables = ((True,), (False,))
    for iterable in iterables:
        assert opt1(iterable) == opt2(iterable)

    ret = _results(
        """for x in iterable:
    if not x.is_empty():
        return False
return True"""
    )
    assert ret == {
        "1:0 SIM111 Use 'return all(x.is_empty() for x in iterable)'"
    }


def test_sim110_sim111_false_positive_check():
    ret = _results(
        """for x in iterable:
    if check(x):
        return "foo"
return "bar" """
    )
    assert ret == set()


def test_sim112_index():
    ret = _results("os.environ['foo']")
    assert ret == {
        "1:0 SIM112 Use 'os.environ[\"FOO\"]' instead of 'os.environ['foo']'"
    }


def test_sim112_get():
    ret = _results("os.environ.get('foo')")
    assert ret == {
        "1:0 SIM112 Use 'os.environ.get(\"FOO\")' instead of "
        "'os.environ.get('foo')'"
    }


def test_sim112_get_with_default():
    ret = _results("os.environ.get('foo', 'bar')")
    assert ret == {
        '1:0 SIM112 Use \'os.environ.get("FOO", "bar")\' instead of '
        "'os.environ.get('foo', 'bar')'"
    }


def test_sim113():
    ret = _results(
        """for el in iterable:
    idx += 1"""
    )
    assert ret == {"2:4 SIM113 Use enumerate instead of 'idx'"}


def test_sim113_false_positive():
    ret = _results(
        """for x in xs:
    cm[x] += 1"""
    )
    assert ret == set()


def test_sim113_false_positive_add_string():
    ret = _results(
        r"""for line in read_list(redis_conn, storage_key):
    line += '\n'"""
    )
    assert ret == set()


def test_sim114():
    ret = _results(
        """if a:
    b
elif c:
    b"""
    )
    assert ret == {"1:3 SIM114 Use logical or ((a) or (c)) and a single body"}


def test_sim115():
    ret = _results(
        """f = open('foo.txt')
data = f.read()
f.close()"""
    )
    assert ret == {"1:4 SIM115 Use context handler for opening files"}


def test_sim115_not_triggered():
    ret = _results(
        """with open('foo.txt') as f:
    data = f.read()"""
    )
    assert ret == set()


def test_sim116():
    ret = _results(
        """if a == "foo":
    return "bar"
elif a == "bar":
    return "baz"
elif a == "boo":
    return "ooh"
else:
    return 42"""
    )
    assert ret == {
        "1:0 SIM116 Use a dictionary lookup "
        "instead of 3+ if/elif-statements: "
        "return {'foo': 'bar', 'bar': "
        "'baz', 'boo': 'ooh'}.get(a, 42)"
    }


def test_sim117():
    ret = _results(
        """with A() as a:
    with B() as b:
        print('hello')"""
    )
    assert ret == {
        "1:0 SIM117 Use 'with A() as a, B() as b:' "
        "instead of multiple with statements"
    }


def test_sim117_no_trigger_begin():
    ret = _results(
        """with A() as a:
    a()
    with B() as b:
        print('hello')"""
    )
    assert ret == set()


def test_sim117_no_trigger_end():
    ret = _results(
        """with A() as a:
    with B() as b:
        print('hello')
    a()"""
    )
    assert ret == set()


def test_sim118():
    results = _results("key in dict.keys()")
    assert results == {
        "1:0 SIM118 Use 'key in dict' instead of 'key in dict.keys()'"
    }


def test_sim118_del_key():
    results = _results(
        """for key in list(dict.keys()):
    if some_property(key):
        del dict[key]"""
    )
    assert results == set()


def test_sim119():
    results = _results(
        """
class FooBar:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __str__(self):
        return "FooBar"
"""
    )
    assert results == {"2:0 SIM119 Use a dataclass for 'class FooBar'"}


def test_sim119_pydantic():
    results = _results(
        """
from pydantic import BaseModel

class FooBar(BaseModel):
    foo : str

    class Config:
        extra = "allow"
"""
    )
    assert results == set()


def test_sim120():
    results = _results("class FooBar(object): pass")
    assert results == {
        "1:0 SIM120 Use 'class FooBar:' instead of 'class FooBar(object):'"
    }


def test_get_if_body_pairs():
    ret = ast.parse(
        """if a == b:
    foo(a)
    foo(b)"""
    ).body[0]
    assert isinstance(ret, ast.If)
    result = get_if_body_pairs(ret)
    assert len(result) == 1
    comp = result[0][0]
    assert isinstance(comp, ast.Compare)
    assert isinstance(result[0][1], list)
    assert isinstance(comp.left, ast.Name)
    assert len(comp.ops) == 1
    assert isinstance(comp.ops[0], ast.Eq)
    assert len(comp.comparators) == 1
    assert isinstance(comp.comparators[0], ast.Name)
    assert comp.left.id == "a"
    assert comp.comparators[0].id == "b"


def test_get_if_body_pairs_2():
    ret = ast.parse(
        """if a == b:
    foo(a)
    foo(b)
elif a == b:
    foo(c)"""
    ).body[0]
    assert isinstance(ret, ast.If)
    result = get_if_body_pairs(ret)
    assert len(result) == 2
    comp = result[0][0]
    assert isinstance(comp, ast.Compare)
    assert isinstance(result[0][1], list)
    assert isinstance(comp.left, ast.Name)
    assert len(comp.ops) == 1
    assert isinstance(comp.ops[0], ast.Eq)
    assert len(comp.comparators) == 1
    assert isinstance(comp.comparators[0], ast.Name)
    assert comp.left.id == "a"
    assert comp.comparators[0].id == "b"


def test_sim201():
    ret = _results("not a == b")
    assert ret == {"1:0 SIM201 Use 'a != b' instead of 'not a == b'"}


def test_sim201_not_in_exception_check():
    ret = _results(
        """if not a == b:
    raise ValueError()"""
    )
    assert ret == set()


def test_sim202_base():
    ret = _results("not a != b")
    assert ret == {("1:0 SIM202 Use 'a == b' instead of 'not a != b'")}


def test_sim203_base():
    ret = _results("not a in b")
    assert ret == {("1:0 SIM203 Use 'a not in b' instead of 'not a in b'")}


def test_sim204_base():
    ret = _results("not a < b")
    assert ret == {("1:0 SIM204 Use 'a >= b' instead of 'not (a < b)'")}


def test_sim205_base():
    ret = _results("not a <= b")
    assert ret == {("1:0 SIM205 Use 'a > b' instead of 'not (a <= b)'")}


def test_sim206_base():
    ret = _results("not a > b")
    assert ret == {("1:0 SIM206 Use 'a <= b' instead of 'not (a > b)'")}


def test_sim207_base():
    ret = _results("not a >= b")
    assert ret == {("1:0 SIM207 Use 'a < b' instead of 'not (a >= b)'")}


def test_sim208_base():
    ret = _results("not (not a)")
    assert ret == {("1:0 SIM208 Use 'a' instead of 'not (not a)'")}


def test_sim210_base():
    ret = _results("True if True else False")
    assert ret == {
        ("1:0 SIM210 Use 'bool(True)' instead of 'True if True else False'")
    }


def test_sim211_base():
    ret = _results("False if True else True")
    assert ret == {
        ("1:0 SIM211 Use 'not True' instead of 'False if True else True'")
    }


def test_sim212_base():
    ret = _results("b if not a else a")
    assert ret == {
        ("1:0 SIM212 Use 'a if a else b' instead of 'b if not a else a'")
    }


def test_sim220_base():
    ret = _results("a and not a")
    assert ret == {("1:0 SIM220 Use 'False' instead of 'a and not a'")}


def test_sim221_base():
    ret = _results("a or not a")
    assert ret == {("1:0 SIM221 Use 'True' instead of 'a or not a'")}


def test_sim222_base():
    ret = _results("a or True")
    assert ret == {("1:0 SIM222 Use 'True' instead of '... or True'")}


def test_sim223_base():
    ret = _results("a and False")
    assert ret == {("1:0 SIM223 Use 'False' instead of '... and False'")}


def test_sim300_string():
    ret = _results("'Yoda' == i_am")
    assert ret == {
        (
            "1:0 SIM300 Use 'i_am == \"Yoda\"' "
            "instead of '\"Yoda\" == i_am' (Yoda-conditions)"
        )
    }


def test_sim300_int():
    ret = _results("42 == age")
    assert ret == {
        "1:0 SIM300 Use 'age == 42' instead of '42 == age' (Yoda-conditions)"
    }
