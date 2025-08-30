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

# Run steps sequentially and fail fast so the make invocation returns the
# failing command's non-zero exit code and the output is preserved.
check: lint type test
