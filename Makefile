ifeq ($(wildcard .venv/Scripts/python.exe),.venv/Scripts/python.exe)
PYTHON := .venv/Scripts/python.exe
else ifeq ($(wildcard .venv/bin/python),.venv/bin/python)
PYTHON := .venv/bin/python
else
$(error Local virtualenv Python not found. Create .venv and install dependencies first)
endif

.PHONY: help setup-db test test-all benchmark keygen run-streamlit run-streamlist run-backend run-frontend run-platform build-frontend

help:
	@echo "Targets:"
	@echo "  make run-streamlit   # Legacy Streamlit app"
	@echo "  make run-streamlist  # Alias for run-streamlit (common typo)"
	@echo "  make run-backend     # Platform FastAPI backend"
	@echo "  make run-frontend    # Platform React frontend"
	@echo "  make run-platform    # Backend + frontend together"
	@echo "  make test            # Quick test run"
	@echo "  make test-all        # Unit + integration + security"
	@echo "  make build-frontend  # Production frontend build"
	@echo "  make setup-db        # Initialize SQLite DB"
	@echo "  make benchmark       # Crypto benchmark script"
	@echo "  make keygen          # Generate sample keypairs"

setup-db:
	$(PYTHON) scripts/setup_db.py

test:
	$(PYTHON) -m pytest -q

test-all:
	$(PYTHON) -m pytest -q tests/unit tests/integration tests/security -v

benchmark:
	$(PYTHON) scripts/benchmark.py

keygen:
	$(PYTHON) scripts/keygen.py

run-streamlit:
	$(PYTHON) scripts/run_project.py streamlit

run-streamlist:
	$(MAKE) run-streamlit

run-backend:
	$(PYTHON) scripts/run_project.py backend

run-frontend:
	$(PYTHON) scripts/run_project.py frontend

run-platform:
	$(PYTHON) scripts/run_project.py platform

build-frontend:
	cd platform/frontend && npm run build
