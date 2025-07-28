#!/bin/bash
# Quick UV Migration Test Script
# Tests the most critical functionality

set -e  # Exit on error

echo "=== Quick UV Migration Test ==="
echo "UV Version: $(uv --version)"
echo "Current Branch: $(git branch --show-current)"
echo

# Create test directory
TEST_DIR="test_uv_quick_$(date +%s)"
echo "Creating test directory: $TEST_DIR"
mkdir -p "$TEST_DIR"

# Test 1: Cookie cutter generation
echo
echo "TEST 1: Testing cookie cutter generation..."
uv run cookiecutter . --no-input \
  project_name="UV Test Project" \
  project_slug="uv_test" \
  include_admin_ui="yes" \
  include_example_tools="yes" \
  -o "$TEST_DIR"

if [ -d "$TEST_DIR/uv_test" ]; then
  echo "✅ Cookie cutter generation: PASSED"
else
  echo "❌ Cookie cutter generation: FAILED"
  exit 1
fi

# Test 2: Generated project structure
echo
echo "TEST 2: Checking generated project structure..."
EXPECTED_FILES=(
  "pyproject.toml"
  "README.md"
  ".gitignore"
  "uv_test/__init__.py"
  "uv_test/server/app.py"
  "uv_test/tools/example_tools.py"
  "uv_test/decorators/__init__.py"
  "uv_test/ui/app.py"
)

cd "$TEST_DIR/uv_test"
MISSING_FILES=0
for file in "${EXPECTED_FILES[@]}"; do
  if [ ! -e "$file" ]; then
    echo "❌ Missing: $file"
    MISSING_FILES=$((MISSING_FILES + 1))
  fi
done

if [ $MISSING_FILES -eq 0 ]; then
  echo "✅ Project structure: PASSED"
else
  echo "❌ Project structure: FAILED ($MISSING_FILES files missing)"
fi

# Test 3: UV installation
echo
echo "TEST 3: Testing UV installation..."
uv venv
source .venv/bin/activate || . .venv/Scripts/activate 2>/dev/null
uv sync

if uv pip list | grep -q "mcp"; then
  echo "✅ UV installation: PASSED"
else
  echo "❌ UV installation: FAILED"
  exit 1
fi

# Test 4: Import test
echo
echo "TEST 4: Testing Python imports..."
if python -c "import uv_test.server.app; print('Server module imported successfully')"; then
  echo "✅ Python imports: PASSED"
else
  echo "❌ Python imports: FAILED"
  exit 1
fi

# Test 5: MCP server help
echo
echo "TEST 5: Testing MCP server CLI..."
if uv run python -m uv_test.server.app --help > /dev/null 2>&1; then
  echo "✅ MCP server CLI: PASSED"
else
  echo "❌ MCP server CLI: FAILED"
  exit 1
fi

# Test 6: Check for pip references in generated files
echo
echo "TEST 6: Checking for remaining pip references..."
PIP_REFS=$(grep -r "pip install" . --include="*.md" --include="*.txt" 2>/dev/null | wc -l)
if [ "$PIP_REFS" -eq 0 ]; then
  echo "✅ No pip references: PASSED"
else
  echo "⚠️  Found $PIP_REFS pip references in generated files"
  grep -r "pip install" . --include="*.md" --include="*.txt" 2>/dev/null || true
fi

# Cleanup
cd ../..
deactivate 2>/dev/null || true

# Summary
echo
echo "=== TEST SUMMARY ==="
echo "Test directory: $TEST_DIR"
echo "All critical tests completed!"
echo
echo "To run the generated server:"
echo "  cd $TEST_DIR/uv_test"
echo "  source .venv/bin/activate"
echo "  uv run mcp dev uv_test/server/app.py"
echo
echo "To clean up test files:"
echo "  rm -rf $TEST_DIR"