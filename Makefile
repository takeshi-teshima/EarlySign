.PHONY: install lint type test check format

install:
	poetry install --with dev,ci

lint:
	poetry run black --check .

type:
	poetry run mypy -p earlysign

test:
	poetry run pytest -q

format:
	poetry run black .

check: lint type test
