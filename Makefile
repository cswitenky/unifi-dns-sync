.PHONY: help install run build publish clean

# Default target
help:
	@echo "Available targets:"
	@echo "  install      Install the package in development mode"
	@echo "  run          Run the application directly"
	@echo "  build        Build the package for distribution"
	@echo "  publish      Publish to PyPI (requires credentials)"
	@echo "  clean        Clean build artifacts"

# Install the package
install:
	python -m pip install -e .

# Run the application directly
run:
	python -m unifi_dns_sync

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info/ src/*.egg-info/

# Build the package
build: clean
	python -m build

# Publish to PyPI
publish: build
	twine upload dist/*

