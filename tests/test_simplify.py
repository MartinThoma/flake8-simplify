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


def test_s104_async_generator_false_positive():
    ret = _results(
        """async def items():
    for c in 'abc':
        yield c"""
    )
    for el in ret:
        assert "SIM104" not in el


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


@pytest.mark.parametrize(
    "s",
    (
        """if image_extension in ['.jpg', '.jpeg']:
    return 'JPEG'
elif image_extension in ['.png']:
    return 'PNG'
else:
    raise ValueError("Unknwon image extension {image extension}")""",
        """if image_extension in ['.jpg', '.jpeg']:
    return 'JPEG'
elif image_extension in ['.png']:
    return 'PNG'
else:
    logger.error("Unknwon image extension {image extension}")
    raise ValueError("Unknwon image extension {image extension}")""",
        """if cond:
    raise Exception
else:
    raise Exception""",
    ),
    ids=["ValueError", "ValueError-with-logging", "TwoExceptions"],
)
def test_sim106_false_positive(s):
    ret = _results(s)
    for el in ret:
        assert "SIM106" not in el


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
        "1:0 SIM109 Use 'a in (b, c)' instead of 'a == b or a == c'"
    }


@pytest.mark.parametrize(
    "s",
    (
        "a == b() or a == c",
        "a == b or a == c()",
        "a == b() or a == c()",
    ),
)
def test_sim109_nop(s):
    ret = _results(s)
    assert not ret


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


def test_sim110_raise_exception():
    ret = _results(
        """
for el in [1,2,3]:
    if is_true(el):
        return True
raise Exception"""
    )
    for el in ret:
        assert "SIM110" not in el


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


def test_sim113_false_positive_continue():
    ret = _results(
        """even_numbers = 0
for el in range(100):
    if el % 2 == 1:
        continue
    even_numbers += 1"""
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


def test_sim114_false_positive70():
    ret = _results(
        """def complicated_calc(*arg, **kwargs):
    return 42

def foo(p):
    if p == 2:
        return complicated_calc(microsecond=0)
    elif p == 3:
        return complicated_calc(microsecond=0, second=0)
    return None"""
    )
    for el in ret:
        assert "SIM114" not in el


def test_sim114_false_positive_elif_in_between():
    ret = _results(
        """a = False
b = True
c = True

if a:
    z = 1
elif b:
    z = 2
elif c:
    z = 1 """
    )
    for el in ret:
        assert "SIM114" not in el


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
"""
    )
    assert results == {"2:0 SIM119 Use a dataclass for 'class FooBar'"}


def test_sim119_ignored_dunder_methods():
    """
    Dunder methods do not make a class not be a dataclass candidate.
    Examples for dunder (double underscore) methods are:
      * __str__
      * __eq__
      * __hash__
    """
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


@pytest.mark.xfail(
    reason="https://github.com/MartinThoma/flake8-simplify/issues/63"
)
def test_sim119_false_positive():
    results = _results(
        '''class OfType:
    """
    >>> 3 == OfType(int, str, bool)
    True
    >>> 'txt' == OfType(int)
    False
    """

    def __init__(self, *types):
        self.types = types

    def __eq__(self, other):
        return isinstance(other, self.types)'''
    )
    for el in results:
        assert "SIM119" not in el


def test_sim119_async():
    results = _results(
        """
class FooBar:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    async def foo(self):
        return "FooBar"
"""
    )
    assert results == set()


def test_sim119_constructor_processing():
    results = _results(
        """
class FooBar:
    def __init__(self, a):
        self.a = a + 5
"""
    )
    assert results == set()


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


def test_sim401_if_else():
    ret = _results(
        """if key in a_dict:
    value = a_dict[key]
else:
    value = 'default'"""
    )
    assert ret == {
        """1:0 SIM401 Use 'value = a_dict.get(key, "default")' """
        """instead of an if-block"""
    }


def test_sim401_negated_if_else():
    ret = _results(
        """if key not in a_dict:
    value = 'default'
else:
    value = a_dict[key] """
    )
    assert (
        """1:0 SIM401 Use 'value = a_dict.get(key, "default")' """
        """instead of an if-block""" in ret
    )


def test_sim401_prefix_negated_if_else():
    ret = _results(
        """if not key in a_dict:
    value = 'default'
else:
    value = a_dict[key] """
    )
    assert (
        """1:3 SIM401 Use 'value = a_dict.get(key, "default")' """
        """instead of an if-block""" in ret
    ) or (
        "1:3 SIM203 Use 'key not in a_dict' instead of 'not key in a_dict'"
        in ret
    )


def test_sim401_false_positive():
    ret = _results(
        """if "foo" in some_dict["a"]:
    some_dict["b"] = some_dict["a"]["foo"]
else:
    some_dict["a"]["foo"] = some_dict["b"]"""
    )
    for el in ret:
        assert "SIM401" not in el


def test_sim401_positive_msg_issue84_example1():
    """
    This is a regression test for the SIM401 message.

    The original issue #84 was reported by jonyscathe. Thank you 🤗
    """
    ret = _results(
        """if "last_name" in test_dict:
    name = test_dict["last_name"]
else:
    name = test_dict["first_name"]"""
    )
    has_sim401 = False
    expected_proposal = (
        'Use \'name = test_dict.get("last_name", '
        "test_dict['first_name'])' instead of an if-block"
    )
    for el in ret:
        if "SIM401" in el:
            msg = el.split("SIM401")[1].strip()
            has_sim401 = True
            assert msg == expected_proposal
    assert has_sim401


def test_sim401_positive_msg_issue84_example2():
    """
    This is a regression test for the SIM401 message.

    The original issue #84 was reported by jonyscathe. Thank you 🤗
    """
    ret = _results(
        """if "phone_number" in test_dict:
    number = test_dict["phone_number"]
else:
    number = "" """
    )
    has_sim401 = False
    expected_proposal = (
        'Use \'number = test_dict.get("phone_number", "")\' '
        "instead of an if-block"
    )
    for el in ret:
        if "SIM401" in el:
            msg = el.split("SIM401")[1].strip()
            has_sim401 = True
            assert msg == expected_proposal
    assert has_sim401


def test_sim401_positive_msg_check_issue89():
    """
    This is a regression test for the SIM401 message.

    The original issue #89 was reported by Aarni Koskela. Thank you 🤗
    """
    ret = _results(
        """if a:
    token = a[1]
elif 'token' in dct:
    token = dct['token']
else:
    token = None"""
    )
    has_sim401 = False
    expected_proposal = (
        "Use 'token = dct.get(\"token\", None)' instead of an if-block"
    )
    for el in ret:
        if "SIM401" in el:
            msg = el.split("SIM401")[1].strip()
            has_sim401 = True
            assert msg == expected_proposal
    assert has_sim401


def test_sim901():
    results = _results("bool(a == b)")
    assert results == {"1:0 SIM901 Use 'a == b' instead of 'bool(a == b)'"}


@pytest.mark.parametrize(
    "s",
    (
        """a = { }
a['b'] = 'c'""",
        pytest.param(
            """a = { }
a['b'] = ba""",
            marks=pytest.mark.xfail,
        ),
    ),
    ids=["minimal", "contains-name"],
)
def test_sim904(s):
    results = _results(s)
    assert results == {"1:0 SIM904 Initialize dictionary 'a' directly"}


@pytest.mark.parametrize(
    "s",
    (
        # Credits to MetRonnie for the following example
        # https://github.com/MartinThoma/flake8-simplify/issues/99
        """my_dict = {
    'foo': [1, 2, 3, 4],
    'bar': [5, 6, 7, 8]
}
my_dict['both'] = [item for _list in my_dict.values() for item in _list]""",
        # Credits to Skylion007 for the following two examples
        # https://github.com/MartinThoma/flake8-simplify/issues/100
        """perf = {"total_time": end_time - start_time}
perf["frame_time"] = perf["total_time"] / total_frames
perf["fps"] = 1.0 / perf["frame_time"]
perf["time_per_step"] = time_per_step
perf["avg_sim_step_time"] = total_sim_step_time / total_frames""",
        """perf = {"a": 1}
perf["b"] = perf["a"] / 10""",
    ),
    ids=["issue-99", "issue-100-1", "issue-100-2"],
)
def test_sim904_false_positives(s):
    results = _results(s)
    for result in results:
        assert "SIM904" not in result


def test_sim905():
    results = _results("""domains = "de com net org".split()""")
    assert results == {
        '1:10 SIM905 Use \'["de", "com", "net", "org"]\' '
        "instead of '\"de com net org\".split()'"
    }


@pytest.mark.parametrize(
    ("s", "msg"),
    (
        # Credits to Skylion007 for the following example
        # https://github.com/MartinThoma/flake8-simplify/issues/101
        (
            "os.path.join(a,os.path.join(b,c))",
            "1:0 SIM906 Use 'os.path.join(a, b, c)' "
            "instead of 'os.path.join(a, os.path.join(b, c))'",
        ),
        (
            "os.path.join(a,os.path.join('b',c))",
            "1:0 SIM906 Use 'os.path.join(a, 'b', c)' "
            "instead of 'os.path.join(a, os.path.join('b', c))'",
        ),
    ),
    ids=["base", "str-arg"],
)
def test_sim906(s, msg):
    results = _results(s)
    assert results == {msg}
