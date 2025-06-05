.PHONY: setup install run clean help

VENV_DIR = venv
PYTHON = python3
ACTIVATE = . $(VENV_DIR)/bin/activate

help:
	@echo "Available commands:"
	@echo "  setup    - Create virtual environment"
	@echo "  install  - Install dependencies"
	@echo "  run      - Set up environment and run the server"
	@echo "  clean    - Remove virtual environment"
	@echo "  help     - Show this help message"

setup:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created in $(VENV_DIR)/"

install: setup
	@echo "Installing dependencies..."
	$(ACTIVATE) && pip install --upgrade pip
	$(ACTIVATE) && pip install -r requirements.txt

run: install
	@echo "Starting the mock server..."
	$(ACTIVATE) && python index.py

clean:
	@echo "Removing virtual environment..."
	rm -rf $(VENV_DIR)
	@echo "Virtual environment removed." 