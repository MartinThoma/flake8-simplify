"""Test cases for SIM904. See tests/rules/__init__.py."""

from tests import snippet

TRUE_POSITIVES = {
    "minimal": (
        snippet("""
            a = { }
            a['b'] = 'c'
        """),
        {
            "1:0 SIM904 Initialize dictionary 'a' directly",
        },
    ),
}

FALSE_POSITIVES = {
    "issue-99": snippet("""
        my_dict = {
            'foo': [1, 2, 3, 4],
            'bar': [5, 6, 7, 8]
        }
        my_dict['both'] = [item for _list in my_dict.values() for item in _list]
    """),
    "issue-100-1": snippet("""
        perf = {"total_time": end_time - start_time}
        perf["frame_time"] = perf["total_time"] / total_frames
        perf["fps"] = 1.0 / perf["frame_time"]
        perf["time_per_step"] = time_per_step
        perf["avg_sim_step_time"] = total_sim_step_time / total_frames
    """),
    "issue-100-2": snippet("""
        perf = {"a": 1}
        perf["b"] = perf["a"] / 10
    """),
    "issue-157-1": snippet("""
        def f(a=None):
            if a is None:
                a = {"b": "c"}
            else:
                a["b"] = "c"
    """),
    "issue-157-2": snippet("""
        def f(a=None):
            if a is None:
                a = {"b": "x"}
            else:
                a["b"] = "c"
    """),
    "for-else": snippet("""
        for x in y:
            a = {}
        else:
            a["b"] = "c"
    """),
}
