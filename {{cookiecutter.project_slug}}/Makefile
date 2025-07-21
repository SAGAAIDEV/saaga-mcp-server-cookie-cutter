# Makefile for {{ cookiecutter.project_name }}

.PHONY: build clean test help run refresh-requirements

# Default target
all: build

## help: Show this help message
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^##' Makefile | sed 's/## /  /'

## build: Build with Bazel
build:
	@echo "🏗️  Building with Bazel..."
	@bazel build //...

## test: Run tests with Bazel
test:
	@echo "🧪 Running tests..."
	@bazel test //...

## clean: Clean Bazel build artifacts
clean:
	@bazel clean

## run: Run the MCP server
run:
	@bazel run //{{ cookiecutter.project_slug }}:{{ cookiecutter.project_slug }}

## refresh-requirements: Regenerate requirements.txt files for Bazel
refresh-requirements:
	@echo "📋 Refreshing requirements files..."
	@./refresh_requirements_txt.sh