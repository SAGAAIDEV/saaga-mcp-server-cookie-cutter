# Ripple Effects Analysis Plan - Cookiecutter Parameter Removal

## Overview
This document outlines a comprehensive plan to analyze and address all ripple effects from removing 6 parameters from `cookiecutter.json`:
- `include_admin_ui` 
- `include_example_tools`
- `include_parallel_example`
- `log_retention_days`
- `default_transport`
- `log_level`

## Changes Already Completed
1. **cookiecutter.json** - Removed all 6 parameters
2. **config.py** - Hardcoded: `log_level="INFO"`, `log_retention_days=30`, `default_transport="stdio"`
3. **server/app.py** - Changed default transport to hardcoded `"stdio"`
4. **hooks/post_gen_project.py** - Removed admin UI cleanup logic
5. **tests/test_transport_integration.py** - Updated test config

## Phase 1: Documentation & README Files

### Files to Check
- `/README.md` - Main template README
- `/{{cookiecutter.project_slug}}/README.md` - Generated project README  
- `/SETUP_ASSISTANT_PROMPT.md` - Setup instructions
- `/docs/*.md` - All documentation files
- `/{{cookiecutter.project_slug}}/docs/*.md` - Generated docs

### What to Look For
- References to removed parameters in setup instructions
- Example configurations showing old parameters
- CLI examples with `--log-level` or `--transport` flags that don't exist
- Installation steps mentioning admin UI as optional
- Any "if you selected X during generation" language
- Configuration examples showing removed parameters
- Environment variable documentation for removed settings

## Phase 2: UI Files - Remove ALL Conditionals

### Files to Check
- `/{{cookiecutter.project_slug}}/ui/__init__.py`
- `/{{cookiecutter.project_slug}}/ui/app.py`
- `/{{cookiecutter.project_slug}}/ui/lib/__init__.py`
- `/{{cookiecutter.project_slug}}/ui/lib/components.py`
- `/{{cookiecutter.project_slug}}/ui/lib/styles.py`
- `/{{cookiecutter.project_slug}}/ui/lib/utils.py`
- `/{{cookiecutter.project_slug}}/ui/pages/1_Home.py`
- `/{{cookiecutter.project_slug}}/ui/pages/2_Configuration.py`
- `/{{cookiecutter.project_slug}}/ui/pages/3_Logs.py`

### What to Look For
- ALL `{% if cookiecutter.include_admin_ui == "yes" %}` conditionals - REMOVE
- ALL `{% else %}` blocks for admin UI - REMOVE
- ALL `{% endif %}` tags for admin UI - REMOVE
- ALL `{% if cookiecutter.include_example_tools == "yes" %}` conditionals - REMOVE
- ALL `{% if cookiecutter.include_parallel_example == "yes" %}` conditionals - REMOVE
- Hardcoded references to `{{cookiecutter.log_level}}` - Replace with "INFO"
- Hardcoded references to `{{cookiecutter.log_retention_days}}` - Replace with 30
- Hardcoded references to `{{cookiecutter.default_transport}}` - Replace with "stdio"

## Phase 3: Tool Files - Remove Example Tool Conditionals

### Files to Check
- `/{{cookiecutter.project_slug}}/tools/example_tools.py`
- `/{{cookiecutter.project_slug}}/tools/parallel_example_tools.py`
- `/{{cookiecutter.project_slug}}/server/app.py` - Tool registration section
- `/{{cookiecutter.project_slug}}/__init__.py` - Package exports

### What to Look For
- `{% if cookiecutter.include_example_tools == "yes" %}` around tool imports
- `{% if cookiecutter.include_parallel_example == "yes" %}` around parallel tools
- Conditional tool registration in app.py
- Conditional imports in __init__ files
- Any tool documentation mentioning they're optional

## Phase 4: Test Files

### Files to Check
- `/tests/test_*.py` - All test files in root tests directory
- `/{{cookiecutter.project_slug}}/tests/unit/*.py`
- `/{{cookiecutter.project_slug}}/tests/integration/*.py`
- `/{{cookiecutter.project_slug}}/tests/conftest.py`
- `/{{cookiecutter.project_slug}}/tests/helpers/*.py`

### What to Look For
- Test fixtures using removed parameters
- Tests that check for optional features (skip if not present)
- Mock configurations with old parameters
- Integration tests assuming conditional features
- Test data/configs with removed parameters
- Parameterized tests varying removed parameters

## Phase 5: Scripts & Utilities

### Files to Check
- `/scripts/*.sh` or `*.py` (if directory exists)
- `/{{cookiecutter.project_slug}}/scripts/*.sh` or `*.py`
- `/{{cookiecutter.project_slug}}/refresh_requirements_txt.sh`
- Any Makefile
- Any task runner configs (taskfile.yml, etc.)

### What to Look For
- Scripts that pass `--log-level` as CLI argument
- Scripts that pass `--transport` as CLI argument  
- Build scripts checking for admin UI presence
- Dev scripts with hardcoded transport options
- Setup scripts mentioning optional components
- Docker/container scripts with removed ENV vars

## Phase 6: Configuration Files

### Files to Check
- `/{{cookiecutter.project_slug}}/pyproject.toml`
- `/{{cookiecutter.project_slug}}/.env.example`
- `/{{cookiecutter.project_slug}}/config.yaml` (if exists)
- `/{{cookiecutter.project_slug}}/config.json` (if exists)
- Docker configs (Dockerfile, docker-compose.yml)
- Kubernetes configs (if any)

### What to Look For
- Environment variable examples for removed settings
- Default config examples with old parameters
- Container ENV declarations for removed settings
- Optional dependencies based on removed features
- Build configurations with conditionals

## Phase 7: CI/CD & GitHub Files

### Files to Check
- `/.github/workflows/*.yml`
- `/{{cookiecutter.project_slug}}/.github/workflows/*.yml`
- `.gitignore` files
- `.github/ISSUE_TEMPLATE/*.md`
- `.github/PULL_REQUEST_TEMPLATE.md`

### What to Look For
- CI workflows using removed parameters in matrix builds
- Test matrices with different parameter combinations
- Documentation deployment conditions based on admin UI
- Release workflows with conditional steps
- Git ignores for optional directories

## Phase 8: Example/Test Directories Generated During Development

### Directories to Check
- `/test_oauth_ui/*` - Test generated project
- `/tim_oauth/*` - Another test project  
- `/test_oauth_backend/*` - OAuth test project
- Any other directories that look like generated projects

### What to Look For
- These might have old generated code that could confuse analysis
- Check if they're using old parameter values
- Ensure they don't affect the template
- Consider if they should be deleted or gitignored

## Phase 9: Edge Cases & Special Files

### Files to Check
- `_copy_without_render` entries in cookiecutter.json
- Binary/image files that might have embedded docs
- `.claude/` directory files
- `.reference/` directory files
- `*.md.template` files (if any)
- Hidden files (.env, .editorconfig, etc.)

### What to Look For
- Documentation that might reference old workflow
- Example configs with removed parameters
- Template files that generate configs
- Hidden configuration with old parameters

## Phase 10: Cross-References & Imports

### Analysis Needed
- Check all imports of `config.py` to ensure they handle hardcoded values
- Check all references to `ServerConfig` class
- Check environment variable lookups (LOG_LEVEL, DEFAULT_TRANSPORT, etc.)
- Verify no code expects these to be template variables
- Check for dynamic config loading that might fail
- Verify all config.get() calls have proper defaults

## Execution Order Priority

1. **CRITICAL**: UI files (Phase 2) - Must remove ALL conditionals
2. **CRITICAL**: Tool registration (Phase 3) - Must always include examples  
3. **HIGH**: Documentation (Phase 1) - User-facing, must be accurate
4. **HIGH**: Tests (Phase 4) - Must pass with new structure
5. **MEDIUM**: Config files (Phase 6) - May have examples to update
6. **MEDIUM**: Scripts (Phase 5) - May have hardcoded flags
7. **LOW**: CI/CD (Phase 7) - May need parameter updates
8. **LOW**: Test directories (Phase 8) - Cleanup if needed
9. **LOW**: Edge cases (Phase 9) - Final sweep
10. **VERIFY**: Cross-references (Phase 10) - Final validation

## Success Criteria

### Must Have
- [ ] All UI files have zero conditionals for removed parameters
- [ ] All tools are always included (no conditionals)
- [ ] Documentation reflects new simplified setup
- [ ] All tests pass with hardcoded values
- [ ] Generated project runs without errors

### Should Have
- [ ] No references to removed parameters in docs
- [ ] Clean, consistent configuration examples
- [ ] Updated CI/CD workflows
- [ ] No orphaned or empty files after generation

### Nice to Have
- [ ] Cleaned up test directories
- [ ] Updated all scripts to use new defaults
- [ ] Comprehensive environment variable docs

## Testing Strategy

After making all changes:

1. **Generate Fresh Project**: 
   ```bash
   cookiecutter . --no-input
   ```

2. **Run All Tests**:
   ```bash
   cd generated_project
   uv run pytest
   ```

3. **Test All Transports**:
   - STDIO: `uv run python -m project.server.app`
   - SSE: `uv run python -m project.server.app --transport sse`
   - HTTP: `uv run python -m project.server.app --transport streamable-http`

4. **Test Admin UI**:
   ```bash
   uv run streamlit run project/ui/app.py
   ```

5. **Verify Tools Load**:
   - Check example tools are registered
   - Check parallel tools work
   - Verify tool count in server startup

## Notes

- This is a breaking change for the template
- Existing generated projects are unaffected
- Simplifies from 14+ questions to ~8 questions
- Makes template more opinionated but easier to use
- All features can still be removed post-generation if needed