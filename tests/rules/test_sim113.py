import pytest

from tests import _results, _rule_hits, snippet

RULE = "SIM113"

TRUE_POSITIVES = [
    pytest.param(
        snippet("""
            idx = 0
            for el in iterable:
                idx += 1
        """),
        {
            "1:0 SIM113 Use enumerate for 'idx'",
        },
        id="counter",
    ),
]

FALSE_POSITIVES = [
    pytest.param(
        snippet("""
            nb_points = 0
            for line in lines:
                for point in line:
                    nb_points += 1
        """),
        id="nested-loop-counter",
    ),
    pytest.param(
        snippet("""
            for x in xs:
                cm[x] += 1
        """),
        id="augment-dict",
    ),
    pytest.param(
        snippet("""
            for line in read_list(redis_conn, storage_key):
                line += '\\n'
        """),
        id="add-string",
    ),
    pytest.param(
        snippet("""
            even_numbers = 0
            for el in range(100):
                if el % 2 == 1:
                    continue
                even_numbers += 1
        """),
        id="continue",
    ),
    pytest.param(
        snippet("""
            count = 0
            for foo in foos:
                for bar in bars:
                    count +=1
        """),
        id="double-loop",
    ),
    pytest.param(
        snippet("""
            epoch, i = np.load(resume_file)
            while epochs < TOTAL_EPOCHS:
                for b in batches:
                    i+=1
        """),
        id="while-loop",
    ),
]


@pytest.mark.parametrize(("code", "expected"), TRUE_POSITIVES)
def test_true_positives(code, expected):
    assert _results(code) == expected


@pytest.mark.parametrize("code", FALSE_POSITIVES)
def test_false_positives(code):
    assert _rule_hits(code, RULE) == set()
