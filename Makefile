.PHONY: help
.PHONY: run
.PHONY: execute
.PHONY: dev
.PHONY: docs
.PHONY: tests
.PHONY: test
.PHONY: tox
.PHONY: hook
.PHONY: lint
.PHONY: mypy
.PHONY: build
.PHONY: Makefile

# Trick to allow passing commands to make
# Use quotes (" ") if command contains flags (-h / --help)
args = `arg="$(filter-out $@,$(MAKECMDGOALS))" && echo $${arg:-${1}}`

# If command doesn't match, do not throw error
%:
	@:

define helptext

  Commands:

  run                  Run dndfog as a script.
  execute              Run compiled executable.
  dev                  Serve manual testing server
  docs                 Serve mkdocs for development.
  tests                Run all tests with coverage.
  test <name>          Run all tests maching the given <name>
  tox                  Run all tests with tox.
  hook                 Install pre-commit hook.
  lint                 Run pre-commit hooks on all files.
  mypy                 Run mypy on all files.
  build                Build executable with pyinstaller.

  Use quotes (" ") if command contains flags (-h / --help)
endef

export helptext

help:
	@echo "$$helptext"

run:
	@poetry run dndfog --file tests/map/Cragmaw-Hideout.png --gridsize 165

execute:
	@dist/dndfog.exe --file tests/map/Cragmaw-Hideout.png --gridsize 165

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

lint:
	@poetry run pre-commit run --all-files

mypy:
	@poetry run mypy dndfog/

build:
	@poetry run pyinstaller \
		--onefile \
		--noconsole \
		--name dndfog \
		--paths $(shell poetry env info --path)\Lib\site-packages \
		dndfog/main.py
