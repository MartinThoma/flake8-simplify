import pytest

from tests import _results, _rule_hits, snippet

RULE = "SIM904"

TRUE_POSITIVES = [
    pytest.param(
        snippet("""
            a = { }
            a['b'] = 'c'
        """),
        {
            "1:0 SIM904 Initialize dictionary 'a' directly",
        },
        id="minimal",
    ),
]

FALSE_POSITIVES = [
    pytest.param(
        snippet("""
            my_dict = {
                'foo': [1, 2, 3, 4],
                'bar': [5, 6, 7, 8]
            }
            my_dict['both'] = [item for _list in my_dict.values() for item in _list]
        """),
        id="issue-99",
    ),
    pytest.param(
        snippet("""
            perf = {"total_time": end_time - start_time}
            perf["frame_time"] = perf["total_time"] / total_frames
            perf["fps"] = 1.0 / perf["frame_time"]
            perf["time_per_step"] = time_per_step
            perf["avg_sim_step_time"] = total_sim_step_time / total_frames
        """),
        id="issue-100-1",
    ),
    pytest.param(
        snippet("""
            perf = {"a": 1}
            perf["b"] = perf["a"] / 10
        """),
        id="issue-100-2",
    ),
    pytest.param(
        snippet("""
            def f(a=None):
                if a is None:
                    a = {"b": "c"}
                else:
                    a["b"] = "c"

        """),
        id="issue-157-1",
    ),
    pytest.param(
        snippet("""
            def f(a=None):
                if a is None:
                    a = {"b": "x"}
                else:
                    a["b"] = "c"

        """),
        id="issue-157-2",
    ),
    pytest.param(
        snippet("""
            for x in y:
                a = {}
            else:
                a["b"] = "c"

        """),
        id="for-else",
    ),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
