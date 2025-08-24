# Cookie Cutter Template Maintenance Reference

## ⚠️ FOR TEMPLATE MAINTAINERS ONLY ⚠️

This `.reference/` directory contains documentation for maintaining and evolving the SAAGA MCP Server Cookie Cutter template itself. This is NOT for MCP server developers using the template - they have their own `.reference/` in generated projects.

## Purpose

When working on JIRA issues to improve the cookie cutter template, AI assistants read these references to understand:
- How to safely modify the template without breaking existing functionality
- Cookiecutter-specific patterns and best practices
- What parts of the template are critical and why
- How to test template changes

## Document Structure

### Template-Specific Documentation (This Directory)
- **`cookiecutter-maintenance.md`** - How to maintain and modify the cookiecutter template
- **`template-evolution.md`** - Guidelines for evolving the template over time
- **`critical-files.md`** - Files that must not be broken and why

### MCP/SAAGA Pattern Documentation (Reference from Template)
For MCP and SAAGA patterns, we follow DRY principles and reference the canonical documentation in:
- `{{cookiecutter.project_slug}}/.reference/` - The source of truth for MCP/SAAGA patterns

## How Commands Use These References

Top-level commands (in `.claude/commands/`) reference both:
1. This directory for template maintenance patterns
2. The template's `.reference/` for MCP/SAAGA patterns

Example command grounding:
```markdown
## Grounding References
- Template maintenance: See `.reference/cookiecutter-maintenance.md`
- MCP patterns: See `{{cookiecutter.project_slug}}/.reference/patterns/tool_patterns.py`
- SAAGA integration: See `{{cookiecutter.project_slug}}/.reference/saaga-mcp-integration.md`
```

## Key Principles

1. **DRY (Don't Repeat Yourself)**: We don't duplicate MCP/SAAGA documentation
2. **Single Source of Truth**: Each concept is documented in exactly one place
3. **Clear Separation**: Template maintenance vs. MCP development are distinct concerns
4. **Maintainability**: Changes to patterns happen in one canonical location

## What Goes Where?

| Topic | Documentation Location |
|-------|----------------------|
| How to add a cookiecutter variable | `.reference/cookiecutter-maintenance.md` |
| MCP tool patterns | `{{cookiecutter.project_slug}}/.reference/patterns/tool_patterns.py` |
| Post-generation hooks | `.reference/cookiecutter-maintenance.md` |
| SAAGA decorator chain | `{{cookiecutter.project_slug}}/.reference/saaga-mcp-integration.md` |
| Template versioning | `.reference/template-evolution.md` |
| Integration test patterns | `{{cookiecutter.project_slug}}/.reference/patterns/integration_test_patterns.py` |

## For Template Maintainers

When working on template improvements:
1. Check this `.reference/` for template-specific guidelines
2. Reference the template's `.reference/` for MCP/SAAGA patterns
3. Ensure changes don't break critical dependencies (see `critical-files.md`)
4. Test template generation after changes
5. Update documentation if you change fundamental patterns