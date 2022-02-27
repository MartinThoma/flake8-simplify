# Core Library
import ast
from typing import List, Tuple


def get_sim119(node: ast.ClassDef) -> List[Tuple[int, int, str]]:
    """
    Get a list of all classes that should be dataclasses"

        ClassDef(
            name='Person',
            bases=[],
            keywords=[],
            body=[
                AnnAssign(
                    target=Name(id='first_name', ctx=Store()),
                    annotation=Name(id='str', ctx=Load()),
                    value=None,
                    simple=1,
                ),
                AnnAssign(
                    target=Name(id='last_name', ctx=Store()),
                    annotation=Name(id='str', ctx=Load()),
                    value=None,
                    simple=1,
                ),
                AnnAssign(
                    target=Name(id='birthdate', ctx=Store()),
                    annotation=Name(id='date', ctx=Load()),
                    value=None,
                    simple=1,
                ),
            ],
            decorator_list=[Name(id='dataclass', ctx=Load())],
        )
    """
    RULE = "SIM119 Use a dataclass for 'class {classname}'"
    errors: List[Tuple[int, int, str]] = []

    if not (len(node.decorator_list) == 0 and len(node.bases) == 0):
        return errors

    dataclass_functions = [
        "__init__",
        "__eq__",
        "__hash__",
        "__repr__",
        "__str__",
    ]
    has_only_dataclass_functions = True
    has_any_functions = False
    has_complex_statements = False
    for body_el in node.body:
        if isinstance(body_el, (ast.FunctionDef, ast.AsyncFunctionDef)):
            has_any_functions = True
            if body_el.name == "__init__":
                # Ensure constructor only has pure assignments
                # without any calculation.
                for el in body_el.body:
                    if not isinstance(el, ast.Assign):
                        has_complex_statements = True
                        break
                    # It is an assignment, but we only allow
                    # `self.attribute = name`.
                    if any(
                        [
                            not isinstance(target, ast.Attribute)
                            for target in el.targets
                        ]
                    ) or not isinstance(el.value, ast.Name):
                        has_complex_statements = True
                        break
            if body_el.name not in dataclass_functions:
                has_only_dataclass_functions = False

    if (
        has_any_functions
        and has_only_dataclass_functions
        and not has_complex_statements
    ):
        errors.append(
            (node.lineno, node.col_offset, RULE.format(classname=node.name))
        )

    return errors


def get_sim120(node: ast.ClassDef) -> List[Tuple[int, int, str]]:
    """
    Get a list of all classes that inherit from object.
    """
    RULE = (
        "SIM120 Use 'class {classname}:' "
        "instead of 'class {classname}(object):'"
    )
    errors: List[Tuple[int, int, str]] = []
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
