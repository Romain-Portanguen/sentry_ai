.PHONY: clean install install-dev test lint format run build-mac build-mac-release clean-all create-dmg

clean:
	rm -rf build dist *.egg-info app/*.egg-info
	find . -name "*.dist-info" -exec rm -rf {} +
	find . -name "*.so" -exec rm -f {} +
	rm -rf app/__pycache__
	rm -f app/*.pyc app/*.pyo app/*.so

clean-all: clean
	rm -rf .venv

install:
	python3.10 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install -e .

install-dev:
	python3.10 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install -e ".[dev]"

test:
	. .venv/bin/activate && pytest

lint:
	. .venv/bin/activate && flake8 app tests

format:
	. .venv/bin/activate && black app tests

run:
	. .venv/bin/activate && python -m app.main

build-mac:
	rm -rf build dist *.egg-info app/*.egg-info
	find . -name "*.dist-info" -exec rm -rf {} +
	find . -name "*.so" -exec rm -f {} +
	rm -rf app/__pycache__
	rm -f app/*.pyc app/*.pyo app/*.so
	. .venv/bin/activate && python setup.py py2app -A
	@echo "Application created in dist/Sentry AI.app"

build-mac-release:
	$(MAKE) clean-all
	$(MAKE) install-dev
	. .venv/bin/activate && python setup.py py2app
	@if [ ! -d "dist/Sentry AI.app" ]; then \
		echo "Error: Application build failed. dist/Sentry AI.app not found"; \
		exit 1; \
	fi
	@echo "Standalone application created in dist/Sentry AI.app"

create-dmg: build-mac-release
	@echo "Creating DMG..."
	@rm -f "dist/Sentry AI.dmg"
	@create-dmg \
		--volname "Sentry AI" \
		--volicon "app/public/assets/AppIcon.png" \
		--background "app/public/assets/dmg-background.png" \
		--window-pos 200 120 \
		--window-size 800 400 \
		--icon-size 100 \
		--icon "Sentry AI.app" 200 190 \
		--hide-extension "Sentry AI.app" \
		--app-drop-link 600 185 \
		"dist/Sentry AI.dmg" \
		"dist/Sentry AI.app"
	@echo "DMG created at dist/Sentry AI.dmg"

run-app:
	./dist/Sentry\ AI.app/Contents/MacOS/Sentry\ AI