"""Test cases for SIM113. See tests/rules/__init__.py."""

from tests import snippet

TRUE_POSITIVES = {
    "counter": (
        snippet("""
            idx = 0
            for el in iterable:
                idx += 1
        """),
        {
            "1:0 SIM113 Use enumerate for 'idx'",
        },
    ),
}

FALSE_POSITIVES = {
    "nested-loop-counter": snippet("""
        nb_points = 0
        for line in lines:
            for point in line:
                nb_points += 1
    """),
    "augment-dict": snippet("""
        for x in xs:
            cm[x] += 1
    """),
    "add-string": snippet("""
        for line in read_list(redis_conn, storage_key):
            line += '\\n'
    """),
    "continue": snippet("""
        even_numbers = 0
        for el in range(100):
            if el % 2 == 1:
                continue
            even_numbers += 1
    """),
    "double-loop": snippet("""
        count = 0
        for foo in foos:
            for bar in bars:
                count +=1
    """),
    "while-loop": snippet("""
        epoch, i = np.load(resume_file)
        while epochs < TOTAL_EPOCHS:
            for b in batches:
                i+=1
    """),
}
