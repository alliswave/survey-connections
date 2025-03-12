.PHONY: lint lint-check lint-fix help test

help:
	@echo "Available commands:"
	@echo "  make lint       - Run ruff to check and fix errors and formatting"
	@echo "  make lint-check - Run ruff to check for errors without fixing"
	@echo "  make lint-fix   - Run ruff to fix errors and formatting issues"
	@echo "  make test       - Run all tests"
	@echo "  make test MODULE=path/to/test.py - Run specific test module"
	@echo "  make test REUSE=1 - Run tests reusing the test database"

lint: lint-check lint-fix

lint-check:
	@echo "Running ruff check..."
	ruff check backend/

lint-fix:
	@echo "Running ruff format..."
	ruff format backend/
	@echo "Running ruff check with --fix..."
	ruff check --fix backend/

test:
	cd backend && python -m pytest $(if $(REUSE),--reuse-db,) $(MODULE)