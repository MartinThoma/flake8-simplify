import ast
from collections.abc import Iterator

from flake8_simplify.registry import Violation, rule


@rule("SIM120", ast.ClassDef)
def get_sim120(node: ast.ClassDef) -> Iterator[Violation]:
    """
    Get a list of all classes that inherit from object.
    """
    RULE = "Use 'class {classname}:' instead of 'class {classname}(object):'"
    if not (
        len(node.bases) == 1
        and isinstance(node.bases[0], ast.Name)
        and node.bases[0].id == "object"
    ):
        return
    yield Violation(node, RULE.format(classname=node.name))
