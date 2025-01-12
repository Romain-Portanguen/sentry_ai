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
	@if [ ! -d "dist/SentryAI.app" ]; then \
		echo "Error: Application build failed. dist/SentryAI.app not found"; \
		exit 1; \
	fi
	@echo "Removing problematic library: liblzma.5.dylib"
	@rm -f "dist/SentryAI.app/Contents/Frameworks/liblzma.5.dylib"
	@echo "Signing application..."
	@find "dist/SentryAI.app" \( -name "Python" -o -name "*.dylib" -o -name "*.so" \) \
		-exec codesign --force --sign - --entitlements entitlements.plist --preserve-metadata=identifier,flags,runtime --timestamp=none {} +
	@find "dist/SentryAI.app/Contents/Frameworks" -type d -name "*.framework" \
		-exec codesign --force --deep --sign - --entitlements entitlements.plist --preserve-metadata=identifier,flags,runtime --timestamp=none {} +
	@codesign --force --sign - --entitlements entitlements.plist --preserve-metadata=identifier,flags,runtime --timestamp=none --no-strict "dist/SentryAI.app"
	@echo "Standalone application created in dist/SentryAI.app"

create-dmg: build-mac-release
	@echo "Creating DMG..."
	@rm -f "dist/SentryAI.dmg"
	@create-dmg \
		--volname "SentryAI" \
		--volicon "app/public/assets/AppIcon.png" \
		--window-pos 200 120 \
		--window-size 800 400 \
		--icon-size 100 \
		--icon "SentryAI.app" 200 190 \
		--hide-extension "SentryAI.app" \
		--app-drop-link 600 185 \
		"dist/SentryAI.dmg" \
		"dist/SentryAI.app"
	@echo "Signing DMG..."
	@codesign --force --sign - --preserve-metadata=identifier,entitlements,flags,runtime --timestamp=none --no-strict "dist/SentryAI.dmg"
	@echo "DMG created at dist/SentryAI.dmg"

run-app:
	./dist/SentryAI.app/Contents/MacOS/SentryAI