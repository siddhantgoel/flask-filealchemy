BLACK_CMD=black
BLACK_OPTS=--line-length 79 --skip-string-normalization

update-app-deps:
	pip-compile requirements.in --output-file requirements.txt

update-dev-deps:
	pip-compile requirements.in requirements.dev.in --output-file requirements.dev.txt

update-deps: update-app-deps update-dev-deps

black:
	$(BLACK_CMD) $(BLACK_OPTS) flask_filealchemy/
	$(BLACK_CMD) $(BLACK_OPTS) tests/

.PHONY: update-deps black
