# Third party
import pytest

# First party
from tests import _results


def test_sim901():
    results = _results("bool(a == b)")
    assert results == {"1:0 SIM901 Use 'a == b' instead of 'bool(a == b)'"}


@pytest.mark.parametrize(
    "s",
    (
        "foo(a, b, True)",
        "set_foo(a, b, True)",
    ),
    ids=[
        "basic",
        "set_multiple",
    ],
)
def test_sim902(s):
    error_messages = _results(s)
    assert any("SIM902" in error_message for error_message in error_messages)


@pytest.mark.parametrize(
    "s",
    (
        "foo(a, b, foo=True)",
        "dict.get('foo', True)",
        "set_visible(True)",
        "line.set_visible(True)",
        "partial(foo, True)",
        "partial(foo, bar=True)",
    ),
    ids=[
        "kw_arg_is_used",
        "dict_get",
        "boolean_setter_function",
        "boolean_setter_method",
        "partial_arg",
        "partial_kwarg",
    ],
)
def test_sim902_false_positive_check(s):
    error_messages = _results(s)
    for error_message in error_messages:
        assert "SIM902" not in error_message


@pytest.mark.parametrize(
    "s",
    ("foo(a, b, 123123)", "foo(a, b, 123.123)"),
    ids=["int", "float"],
)
def test_sim903_true_positive_check(s):
    error_messages = _results(s)
    assert any("SIM903" in error_message for error_message in error_messages)


@pytest.mark.parametrize(
    "s",
    (
        "dict.get('foo', 123)",
        "set_foo(1.23)",
        "line.set_foo(1.23)",
        "partial(foo, 1, 2, 3)",
        "min(0.5, g_norm)",
        "QColor(53, 53, 53, 128)",
    ),
    ids=[
        "get_exception",
        "set_function",
        "set_method",
        "partial",
        "min",
        "color",
    ],
)
def test_sim903_false_positive_check(s):
    error_messages = _results(s)
    for error_message in error_messages:
        assert "SIM903" not in error_message


def test_sim903_insert_exception():
    ret = _results("sys.path.insert(0, 'foo')")
    assert ret == set()


def test_sim903_range_exception():
    ret = _results("range(42)")
    assert ret == set()


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


def test_sim907():
    results = _results(
        """def foo(a: Union[int, None]) -> bool:
  return a"""
    )
    assert results == {
        "1:11 SIM907 Use 'Optional[int]' instead of 'Union[int, None]'"
    }


def test_sim908():
    results = _results(
        """name = "some_default"
if "some_key" in some_dict:
    name = some_dict["some_key"]"""
    )
    assert results == {
        "2:0 SIM908 Use 'some_dict.get(\"some_key\")' instead of "
        '\'if "some_key" in some_dict: some_dict["some_key"]\''
    }


@pytest.mark.parametrize(
    ("s", "msg"),
    (
        # Credits to Ryan Delaney for the following two example
        # https://github.com/MartinThoma/flake8-simplify/issues/114
        (
            "foo = foo",
            "1:0 SIM909 Remove reflexive assignment 'foo = foo'",
        ),
        (
            "foo = foo = 42",
            "1:0 SIM909 Remove reflexive assignment 'foo = foo = 42'",
        ),
        (
            "foo = bar = foo = 42",
            "1:0 SIM909 Remove reflexive assignment 'foo = bar = foo = 42'",
        ),
        (
            "n, m = n, m",
            "1:0 SIM909 Remove reflexive assignment 'n, m = n, m'",
        ),
        (
            "a['foo'] = a['foo']",
            "1:0 SIM909 Remove reflexive assignment 'a['foo'] = a['foo']'",
        ),
    ),
    ids=["simple", "double", "multiple", "tuple", "dict"],
)
def test_sim909(s, msg):
    results = _results(s)
    assert results == {msg}


@pytest.mark.parametrize(
    ("s"),
    ("n, m = m, n", "foo = 'foo'"),
    ids=["tuple-switch", "variable"],
)
def test_sim909_false_positives(s):
    results = _results(s)
    for result in results:
        assert "SIM909" not in result
