.PHONY: lint lint-check lint-fix help

help:
	@echo "Available commands:"
	@echo "  make lint       - Run ruff to check and fix errors and formatting"
	@echo "  make lint-check - Run ruff to check for errors without fixing"
	@echo "  make lint-fix   - Run ruff to fix errors and formatting issues"

lint: lint-check lint-fix

lint-check:
	@echo "Running ruff check..."
	ruff check backend/

lint-fix:
	@echo "Running ruff format..."
	ruff format backend/
	@echo "Running ruff check with --fix..."
	ruff check --fix backend/ 