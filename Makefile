lint-flake8:
	poetry run flake8 flask_filealchemy/ tests/

lint-black:
	poetry run black --check flask_filealchemy/ tests/

lint: lint-black lint-flake8

test-pytest:
	poetry run py.test tests/

test: test-pytest

.PHONY: lint-black lint-flake8 lint test-pytest test
