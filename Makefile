.PHONY: install test clean run

install:
	python3.10 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install -r requirements.txt

install-dev:
	python3.10 -m venv .venv
	. .venv/bin/activate && pip install -e ".[dev]"

test:
	. .venv/bin/activate && pytest tests/ -v

coverage:
	. .venv/bin/activate && pytest tests/ --cov=sentry --cov-report=term-missing

clean:
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "*.egg-info" -exec rm -r {} +

run:
	PYTHONPATH=. python3 -m app.main

format:
	black .

lint:
	flake8 . 