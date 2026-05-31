.PHONY: install test lint typecheck format demo build clean

install:
	pip install -e ".[dev]"

test:
	pytest -v --cov=agentaudit tests/

lint:
	ruff check .
	ruff format --check .

format:
	ruff format .
	ruff check --fix .

typecheck:
	mypy agentaudit tests/

demo:
	python -m agentaudit.cli run examples/basic/agentaudit.yml

build:
	python -m build

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache .coverage htmlcov reports/
	find . -type d -name "__pycache__" -exec rm -rf {} +
