# Development
- This repository uses `make` to organize workspace tasks. For the details, see the Makefile.
- We use `poetry`. So the commands usually need to be run as `poetry run python ...` etc.
- At the end of the edits, make sure to run `make format` to ensure the code is compliant to the formatting standards of this repository.
- Also run `make check` occasionally to make sure the code passes the tests and lint checks.
- When installing a package, make sure to use `poetry add` instead of writing directly to pyproject.toml.

# Preferences
- We prefer keeping all the test and formatting configurations in `pyproject.toml`.
