
.PHONY: help dev docs tests test tox hook pre-commit mypy build Makefile

# Trick to allow passing commands to make
# Use quotes (" ") if command contains flags (-h / --help)
args = `arg="$(filter-out $@,$(MAKECMDGOALS))" && echo $${arg:-${1}}`

# If command doesn't match, do not throw error
%:
	@:

help:
	@echo ""
	@echo "Commands:"
	@echo "  run                  Run dndfog as a script."
	@echo "  docs                 Serve mkdocs for development."
	@echo "  tests                Run all tests with coverage."
	@echo "  test <name>          Run all tests maching the given <name>"
	@echo "  tox                  Run all tests with tox."
	@echo "  hook                 Install pre-commit hook."
	@echo "  pre-commit           Run pre-commit hooks on all files."
	@echo "  pre-commit-update    Update all pre-commit hooks to latest versions."
	@echo "  mypy                 Run mypy on all files."
	@echo "  build                Build executable with pyinstaller."

run:
	@poetry run dndfog

docs:
	@poetry run mkdocs serve -a localhost:8080

tests:
	@poetry run coverage run -m pytest

test:
	@poetry run pytest -k $(call args, "")

tox:
	@poetry run tox

hook:
	@poetry run pre-commit install

pre-commit:
	@poetry run pre-commit run --all-files

pre-commit-update:
	@poetry run pre-commit autoupdate

mypy:
	@poetry run mypy dndfog

build:
	@pyinstaller -n dndfog --onefile --noconsole --paths .venv/Lib/site-packages dndfog/main.py