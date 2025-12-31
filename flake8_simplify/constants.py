# Core Library
import ast
import sys

if sys.version_info < (3, 8):
  BOOL_CONST_TYPES = (ast.Constant, ast.NameConstant)
  AST_CONST_TYPES = (ast.Constant, ast.NameConstant, ast.Str, ast.Num)
  STR_TYPES = (ast.Constant, ast.Str)
else:
  BOOL_CONST_TYPES = (ast.Constant,)
  AST_CONST_TYPES = (ast.Constant,)
  STR_TYPES = (ast.Constant,)
