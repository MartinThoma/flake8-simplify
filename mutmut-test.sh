#!/bin/bash -e
mypy --strict flake8_simplify.py
pytest -x
