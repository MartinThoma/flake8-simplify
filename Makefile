maint:
	pre-commit autoupdate && pre-commit run --all-files
	pip-compile -U requirements/lint.in
	pip-compile -U requirements/dev.in

lint:
	mypy flake8_simplify --strict
	flake8 .

upload:
	make clean
	flit publish

clean:
	pyclean .
	rm -rf *.pyc build dist tests/reports docs/build .pytest_cache .tox .coverage html/

mutmut-run:
	mutmut run --paths-to-mutate flake8_simplify.py

mutmut-results:
	mutmut html

bandit:
	# Python3 only: B322 is save
	bandit -r mpu -s B322
