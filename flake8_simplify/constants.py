# Core Library
import ast

# ast.Constant in Python 3.8, ast.NameConstant in Python 3.6 and 3.7
BOOL_CONST_TYPES = (ast.Constant, ast.NameConstant)
AST_CONST_TYPES = (ast.Constant, ast.NameConstant, ast.Str, ast.Num)
STR_TYPES = (ast.Constant, ast.Str)
