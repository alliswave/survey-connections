.PHONY: lint lint-check lint-fix help test install start-dev

INSTALL_MARKER=.venv/.install-complete

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies using uv and requirements.txt"
	@echo "  make start-dev  - Start development server (installs dependencies if needed)"
	@echo "  make lint       - Run ruff to check and fix errors and formatting"
	@echo "  make lint-check - Run ruff to check for errors without fixing"
	@echo "  make lint-fix   - Run ruff to fix errors and formatting issues"
	@echo "  make test       - Run all tests"
	@echo "  make test MODULE=path/to/test.py - Run specific test module"
	@echo "  make test REUSE=1 - Run tests reusing the test database"

$(INSTALL_MARKER): requirements.txt
	@echo "Installing dependencies using uv..."
	@if ! command -v uv &> /dev/null; then \
		echo "uv not found. Please install uv first."; \
		exit 1; \
	fi
	@if [ ! -d ".venv" ]; then \
		echo "Creating virtual environment..."; \
		python -m venv .venv; \
	fi
	@source .venv/bin/activate && uv pip install -r requirements.txt
	@mkdir -p $(dir $(INSTALL_MARKER))
	@touch $(INSTALL_MARKER)
	@echo "Installation complete!"

install: $(INSTALL_MARKER)

start-dev: $(INSTALL_MARKER)
	@echo "Starting development server..."
	@source .venv/bin/activate && cd backend && python manage.py runserver

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