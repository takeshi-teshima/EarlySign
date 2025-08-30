.PHONY: install lint type test check format

install:
	poetry install --with dev,ci

lint:
	poetry run black --check .

type:
	poetry run mypy -p earlysign

test:
	poetry run pytest

format:
	poetry run black .

docs-build:
	# Build Sphinx docs into docs/_build/html
	poetry run sphinx-build -b html docs/source docs/_build/html || \
	poetry run sphinx-build -b html docs docs/_build/html

docs-serve:
	# Serve docs locally with live-reload (requires sphinx-autobuild)
	poetry run sphinx-autobuild docs/source docs/_build/html --open-browser || \
	poetry run sphinx-autobuild docs docs/_build/html --open-browser

# Run steps sequentially and fail fast so the make invocation returns the
# failing command's non-zero exit code and the output is preserved.
# Run steps sequentially and fail fast so the make invocation returns the
# failing command's non-zero exit code and the output is preserved.
check: lint type test docs-build
