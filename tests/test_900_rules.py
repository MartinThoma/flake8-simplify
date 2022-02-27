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
