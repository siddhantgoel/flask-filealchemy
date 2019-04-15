BLACK_CMD=black
BLACK_OPTS=--line-length 79 --skip-string-normalization

update-deps:
	pip-compile requirements.dev.in --output-file requirements.dev.txt

black:
	$(BLACK_CMD) $(BLACK_OPTS) flask_filealchemy/
	$(BLACK_CMD) $(BLACK_OPTS) tests/

.PHONY: update-deps black
