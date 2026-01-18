.PHONY: install format lint typecheck check test precommit run

# Development targets
install:
	uv sync --all-extras

format:
	uv run ruff format .
	uv run ruff check --fix . || true

lint:
	uv run ruff check .

typecheck:
	uv run mypy src

check: lint typecheck

test:
	uv run pytest || test $$? -eq 5

precommit: format test check
	@echo "All precommit checks passed"

# Legacy targets for backwards compatibility
run:
	uv run python -m iphone_backup backup

# pyenv setup (manual step)
pyenv:
	pyenv virtualenv 3.11.4 iphone-image-backup
	pyenv local iphone-image-backup
