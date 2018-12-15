update-app-deps:
	pip-compile requirements.in --output-file requirements.txt

update-dev-deps:
	pip-compile requirements.in requirements.dev.in --output-file requirements.dev.txt

update-deps: update-app-deps update-dev-deps

.PHONY: update-deps
