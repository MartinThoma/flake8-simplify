# Core Library
import ast
from collections import defaultdict
from typing import Dict, List, Tuple

# First party
from flake8_simplify.constants import BOOL_CONST_TYPES
from flake8_simplify.utils import (
    _get_duplicated_isinstance_call_by_node,
    is_same_expression,
    to_source,
)


def get_sim101(
    node: ast.BoolOp,
) -> List[Tuple[int, int, str]]:
    """Get a positions where the duplicate isinstance problem appears."""
    errors: List[Tuple[int, int, str]] = []
    if not isinstance(node.op, ast.Or):
        return errors

    RULE = (
        "SIM101 Multiple isinstance-calls which can be merged into a single "
        "call for variable '{var}'"
    )
    for var in _get_duplicated_isinstance_call_by_node(node):
        errors.append((node.lineno, node.col_offset, RULE.format(var=var)))
    return errors


def get_sim109(node: ast.BoolOp) -> List[Tuple[int, int, str]]:
    """
    Check if multiple equalities with the same value are combined via "or".

        BoolOp(
                op=Or(),
                values=[
                    Compare(
                        left=Name(id='a', ctx=Load()),
                        ops=[Eq()],
                        comparators=[Name(id='b', ctx=Load())],
                    ),
                    Compare(
                        left=Name(id='a', ctx=Load()),
                        ops=[Eq()],
                        comparators=[Name(id='c', ctx=Load())],
                    ),
                ],
        )
    """
    errors: List[Tuple[int, int, str]] = []
    if not isinstance(node.op, ast.Or):
        return errors
    equalities = [
        value
        for value in node.values
        if isinstance(value, ast.Compare)
        and len(value.ops) == 1
        and isinstance(value.ops[0], ast.Eq)
    ]
    id2vals: Dict[str, List[ast.Name]] = defaultdict(list)
    for eq in equalities:
        if (
            isinstance(eq.left, ast.Name)
            and len(eq.comparators) == 1
            and isinstance(eq.comparators[0], ast.Name)
        ):
            id2vals[eq.left.id].append(eq.comparators[0])
    RULE = "SIM109 Use '{value} in {values}' instead of '{or_op}'"
    for value, values in id2vals.items():
        if len(values) == 1:
            continue
        errors.append(
            (
                node.lineno,
                node.col_offset,
                RULE.format(
                    or_op=to_source(node),
                    value=value,
                    values=f"({to_source(ast.Tuple(elts=values))})",
                ),
            )
        )
    return errors


def get_sim220(node: ast.BoolOp) -> List[Tuple[int, int, str]]:
    """
    Get a list of all calls of the type "a and not a".

    BoolOp(
        op=And(),
        values=[
            Name(id='a', ctx=Load()),
            UnaryOp(
                op=Not(),
                operand=Name(id='a', ctx=Load()),
            ),
        ],
    )
    """
    errors: List[Tuple[int, int, str]] = []
    if not (isinstance(node.op, ast.And) and len(node.values) >= 2):
        return errors
    # We have a boolean And. Let's make sure there is two times the same
    # expression, but once with a "not"
    negated_expressions = []
    non_negated_expressions = []
    for exp in node.values:
        if isinstance(exp, ast.UnaryOp) and isinstance(exp.op, ast.Not):
            negated_expressions.append(exp.operand)
        else:
            non_negated_expressions.append(exp)
    if len(negated_expressions) == 0:
        return errors

    RULE = "SIM220 Use 'False' instead of '{a} and not {a}'"
    for negated_expression in negated_expressions:
        for non_negated_expression in non_negated_expressions:
            if is_same_expression(negated_expression, non_negated_expression):
                a = to_source(negated_expression)
                errors.append((node.lineno, node.col_offset, RULE.format(a=a)))
                return errors
    return errors


def get_sim221(node: ast.BoolOp) -> List[Tuple[int, int, str]]:
    """
    Get a list of all calls of the type "a or not a".

    BoolOp(
        op=Or(),
        values=[
            Name(id='a', ctx=Load()),
            UnaryOp(
                op=Not(),
                operand=Name(id='a', ctx=Load()),
            ),
        ],
    )
    """
    errors: List[Tuple[int, int, str]] = []
    if not (isinstance(node.op, ast.Or) and len(node.values) >= 2):
        return errors
    # We have a boolean OR. Let's make sure there is two times the same
    # expression, but once with a "not"
    negated_expressions = []
    non_negated_expressions = []
    for exp in node.values:
        if isinstance(exp, ast.UnaryOp) and isinstance(exp.op, ast.Not):
            negated_expressions.append(exp.operand)
        else:
            non_negated_expressions.append(exp)
    if len(negated_expressions) == 0:
        return errors

    RULE = "SIM221 Use 'True' instead of '{a} or not {a}'"
    for negated_expression in negated_expressions:
        for non_negated_expression in non_negated_expressions:
            if is_same_expression(negated_expression, non_negated_expression):
                a = to_source(negated_expression)
                errors.append((node.lineno, node.col_offset, RULE.format(a=a)))
                return errors
    return errors


def get_sim222(node: ast.BoolOp) -> List[Tuple[int, int, str]]:
    """
    Get a list of all calls of the type "... or True".

    BoolOp(
        op=Or(),
        values=[
            Name(id='a', ctx=Load()),
            UnaryOp(
                op=Not(),
                operand=Name(id='a', ctx=Load()),
            ),
        ],
    )
    """
    errors: List[Tuple[int, int, str]] = []
    if not (isinstance(node.op, ast.Or)):
        return errors

    RULE = "SIM222 Use 'True' instead of '... or True'"
    for exp in node.values:
        if isinstance(exp, BOOL_CONST_TYPES) and exp.value is True:
            errors.append((node.lineno, node.col_offset, RULE))
            return errors
    return errors


def get_sim223(node: ast.BoolOp) -> List[Tuple[int, int, str]]:
    """
    Get a list of all calls of the type "... and False".

    BoolOp(
        op=And(),
        values=[
            Name(id='a', ctx=Load()),
            UnaryOp(
                op=Not(),
                operand=Name(id='a', ctx=Load()),
            ),
        ],
    )
    """
    errors: List[Tuple[int, int, str]] = []
    if not (isinstance(node.op, ast.And)):
        return errors

    RULE = "SIM223 Use 'False' instead of '... and False'"
    for exp in node.values:
        if isinstance(exp, BOOL_CONST_TYPES) and exp.value is False:
            errors.append((node.lineno, node.col_offset, RULE))
            return errors
    return errors
