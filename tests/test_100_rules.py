# Core Library
from typing import Iterable

# Third party
import pytest

# First party
from tests import _results


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


@pytest.mark.parametrize(
    "s",
    (
        """if __name__ == "__main__":
    if foo(): ...""",
        """if a:
    d
    if b:
        c""",
    ),
    ids=("__main__", "intermediate-statement"),
)
def test_sim102_should_not_trigger(s):
    ret = _results(s)
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


def test_s104_async_generator_false_positive_2():
    ret = _results(
        """async def items():
    with open('/etc/passwd') as f:
        for line in f:
            yield line"""
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


def test_sim108_false_positive():
    ret = _results(
        """if E == 0:
    M = 3
elif E == 1:
    M = 2
else:
    M = 0.5"""
    )
    for el in ret:
        assert "SIM108" not in el


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
        """
idx = 0
for el in iterable:
    idx += 1"""
    )
    assert ret == {"2:0 SIM113 Use enumerate for 'idx'"}


def test_sim113_false_positive2():
    ret = _results(
        """nb_points = 0
for line in lines:
    for point in line:
        nb_points += 1"""
    )
    assert ret == set()


@pytest.mark.parametrize(
    "s",
    (
        """for x in xs:
    cm[x] += 1""",
        r"""for line in read_list(redis_conn, storage_key):
    line += '\n'""",
        """even_numbers = 0
for el in range(100):
    if el % 2 == 1:
        continue
    even_numbers += 1""",
        # The following two examples (double-loop and while-loop) were
        # contributed by Skylion007 via
        # https://github.com/MartinThoma/flake8-simplify/issues/25
        """count = 0
for foo in foos:
    for bar in bars:
        count +=1""",
        """epoch, i = np.load(resume_file)
while epochs < TOTAL_EPOCHS:
    for b in batches:
        i+=1""",
    ),
    ids=(
        "augment-dict",
        "add-string",
        "continue",
        "double-loop",
        "while-loop",
    ),
)
def test_sim113_false_positive(s):
    ret = _results(s)
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


def test_sim116_false_positive():
    ret = _results(
        """if a == "foo":
    return "bar"
elif a == "bar":
    return baz()
elif a == "boo":
    return "ooh"
else:
    return 42"""
    )
    for el in ret:
        assert "SIM116" not in el


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


def test_sim120():
    results = _results("class FooBar(object): pass")
    assert results == {
        "1:0 SIM120 Use 'class FooBar:' instead of 'class FooBar(object):'"
    }


def test_sim111_false_positive():
    results = _results(
        """for a in my_list:
  if a == 2:
    return False
call_method()
return True"""
    )
    for el in results:
        assert "SIM111" not in el
