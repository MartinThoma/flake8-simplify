import ast


def get_sim120(node: ast.ClassDef) -> list[tuple[int, int, str]]:
    """
    Get a list of all classes that inherit from object.
    """
    RULE = (
        "SIM120 Use 'class {classname}:' "
        "instead of 'class {classname}(object):'"
    )
    errors: list[tuple[int, int, str]] = []
    if not (
        len(node.bases) == 1
        and isinstance(node.bases[0], ast.Name)
        and node.bases[0].id == "object"
    ):
        return errors
    errors.append(
        (node.lineno, node.col_offset, RULE.format(classname=node.name))
    )
    return errors
