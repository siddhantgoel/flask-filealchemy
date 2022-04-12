fmt-black:
	poetry run black flask_filealchemy/ tests/ example/

lint-black:
	poetry run black --check flask_filealchemy/ tests/ example/

lint-flake8:
	poetry run flake8 flask_filealchemy/ tests/ example/

lint-mypy:
	poetry run mypy flask_filealchemy/

lint: lint-black lint-flake8 lint-mypy

test-pytest:
	poetry run pytest tests/

test: test-pytest

.PHONY: fmt-black lint-black lint-flake8 lint test-pytest test
