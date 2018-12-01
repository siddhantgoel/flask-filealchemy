update-deps:
	pip-compile requirements.in > requirements.txt
	pip-compile requirements.dev.in > requirements.dev.txt

.PHONY: update-deps
