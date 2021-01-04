#!/bin/bash -e
mypy flake8_simplify.py
pytest -x
