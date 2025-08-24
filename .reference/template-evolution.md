# Template Evolution Guidelines

Guidelines for evolving the SAAGA MCP Server Cookie Cutter template while maintaining backward compatibility and user trust.

## Version Management

### Semantic Versioning
Follow semantic versioning for the template:
- **MAJOR**: Breaking changes (requires migration)
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes and documentation updates

### Version Tracking
Track version in multiple places:
```python
# cookiecutter.json
{
  "_template_version": "2.1.0",
  ...
}

# {{cookiecutter.project_slug}}/CHANGELOG.md
Update with each release
```

## Critical Dependencies

### Files That Must Stay in Sync

#### 1. Decorator Chain
These files are tightly coupled and must be updated together:
```
{{cookiecutter.project_slug}}/
├── decorators/
│   ├── type_converter.py
│   ├── tool_logger.py
│   ├── exception_handler.py
│   └── parallelize.py
└── server/app.py  # Applies decorators in specific order
```

**Rule**: If you change decorator signatures, update ALL decorators and app.py

#### 2. Logging System
```
{{cookiecutter.project_slug}}/
├── log_system/         # Package name is critical (NOT "logging")
│   ├── unified_logger.py
│   ├── correlation.py
│   └── destinations/
└── decorators/tool_logger.py  # Depends on log_system
```

**Rule**: Never rename log_system package - it conflicts with Python stdlib

#### 3. MCP Integration
```
{{cookiecutter.project_slug}}/
├── server/app.py       # FastMCP initialization
├── tools/*.py          # All tools must have ctx: Context = None
└── .reference/         # Documents requirements
```

**Rule**: All tools MUST maintain async signature with Context parameter

### What Breaks If Changed

| Component | If You Change... | What Breaks |
|-----------|-----------------|-------------|
| Decorator order in app.py | Order of application | Type conversion, logging, error handling |
| Tool signature pattern | Remove ctx: Context = None | Correlation IDs, OAuth passthrough |
| log_system package name | Rename to "logging" | Import conflicts with Python stdlib |
| .reference/ directory | Remove or rename | AI assistant commands fail |
| FastMCP version | Major version bump | Potentially all MCP tools |

## Breaking Changes

### What Constitutes a Breaking Change

1. **Removing cookiecutter variables**
2. **Changing default behavior** (e.g., decorators applied by default → optional)
3. **Renaming generated files or directories**
4. **Changing required Python version**
5. **Modifying decorator signatures**

### How to Handle Breaking Changes

#### 1. Document in CHANGELOG
```markdown
## [2.0.0] - 2024-01-15
### ⚠️ BREAKING CHANGES
- Renamed `logging/` to `log_system/` to avoid Python stdlib conflicts
  - **Migration**: Update all imports from `logging.*` to `log_system.*`
- Changed decorator application from automatic to explicit
  - **Migration**: See migration guide below
```

#### 2. Provide Migration Guide
Create `MIGRATION.md` for major versions:
```markdown
# Migration Guide: v1.x to v2.0

## Step 1: Update imports
Replace all occurrences of:
```python
from logging.unified_logger import UnifiedLogger
```
With:
```python
from log_system.unified_logger import UnifiedLogger
```
```

#### 3. Support Period
- Maintain previous major version for 3 months
- Backport critical security fixes
- Clearly mark deprecated features

## Adding New Features

### Feature Flags
Add optional features via cookiecutter variables:
```json
{
  "include_new_feature": "no"  // Default to "no" for backward compatibility
}
```

### Progressive Enhancement
1. **Phase 1**: Add as optional (default: no)
2. **Phase 2**: Change default to yes (minor version)
3. **Phase 3**: Make mandatory (major version)

### Testing Matrix
Test combinations of features:
```python
test_configs = [
    {"include_oauth_passthrough": "yes", "include_streamlit_ui": "yes"},
    {"include_oauth_passthrough": "yes", "include_streamlit_ui": "no"},
    {"include_oauth_passthrough": "no", "include_streamlit_ui": "yes"},
    {"include_oauth_passthrough": "no", "include_streamlit_ui": "no"},
]
```

## Deprecation Process

### 1. Mark as Deprecated
```python
# In template code
import warnings

def deprecated_function():
    warnings.warn(
        "This function is deprecated and will be removed in v3.0",
        DeprecationWarning,
        stacklevel=2
    )
```

### 2. Document Timeline
```markdown
## Deprecation Schedule
- v2.1.0: Feature marked as deprecated
- v2.2.0: Warning becomes more prominent
- v3.0.0: Feature removed
```

### 3. Provide Alternative
Always show users the new way:
```python
# Deprecated: Direct decorator application
@tool_logger
async def my_tool():
    pass

# New way: Explicit registration
async def my_tool():
    pass

register_tool(my_tool, decorators=[tool_logger])
```

## Quality Checklist

Before releasing a new version:

- [ ] All generated tests pass
- [ ] MCP Inspector can connect to generated server
- [ ] OAuth passthrough works (if included)
- [ ] Streamlit UI launches (if included)
- [ ] Correlation IDs are tracked properly
- [ ] Documentation is updated
- [ ] CHANGELOG reflects all changes
- [ ] Migration guide provided (if breaking)
- [ ] Version bumped in cookiecutter.json

## Rollback Plan

If a release causes issues:

1. **Immediate**: Pin previous version in documentation
2. **Within 24h**: Hotfix or revert problematic changes
3. **Communication**: Update GitHub issues, announcement
4. **Post-mortem**: Document what went wrong, improve tests

## Long-term Stability

### Core Principles
1. **MCP Protocol Compliance**: Always maintain compatibility
2. **SAAGA Pattern Integrity**: Preserve decorator chain
3. **Developer Experience**: Changes should simplify, not complicate
4. **Documentation First**: Update docs before changing code

### Future-Proofing
- Abstract MCP client creation for easier updates
- Use dependency injection for flexibility
- Keep business logic separate from framework code
- Maintain comprehensive test coverage