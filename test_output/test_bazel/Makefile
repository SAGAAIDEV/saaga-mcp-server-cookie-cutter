# Makefile for Test Bazel

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
	@bazel run //test_bazel:test_bazel

## refresh-requirements: Regenerate requirements.txt files for Bazel
refresh-requirements:
	@echo "📋 Refreshing requirements files..."
	@./refresh_requirements_txt.sh