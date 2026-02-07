.PHONY: install sync format lint typecheck check test precommit run

# Install dependencies (alias for sync)
install: sync

# Sync dependencies
sync:
	@uv sync --all-extras

# Format code with ruff
format:
	uv run ruff format .
	uv run ruff check --fix . || true

# Lint code with ruff
lint:
	uv run ruff check .

# Type check with mypy
typecheck:
	uv run mypy src

# Run lint and typecheck
check: lint typecheck

# Run tests with pytest
test: sync
	uv run pytest || test $$? -eq 5

# Run all precommit checks
precommit: sync format test check
	@echo "✓ All precommit checks passed"

# Legacy targets for backwards compatibility
run:
	uv run python -m iphone_backup backup

# pyenv setup (manual step)
pyenv:
	pyenv virtualenv 3.11.4 iphone-image-backup
	pyenv local iphone-image-backup
