maint:
	uv run pre-commit autoupdate && uv run pre-commit run --all-files
	uv lock --upgrade

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy flake8_simplify
	uv run flake8 .

test:
	uv run pytest

clean:
	rm -rf *.pyc build dist tests/reports docs/build .pytest_cache .coverage html/

mutmut-run:
	# mutmut has no time limit option; it resumes from mutants/ on the next run
	timeout 30m uv run --group mutation mutmut run

mutmut-results:
	uv run --group mutation mutmut browse
