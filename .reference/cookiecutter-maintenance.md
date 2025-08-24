# Cookiecutter Template Maintenance Guide

This guide explains how to maintain and modify the SAAGA MCP Server Cookie Cutter template.

## Adding New Variables

### 1. Update cookiecutter.json
Add your variable with a sensible default:
```json
{
  "project_name": "My MCP Server",
  "project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '_').replace('-', '_') }}",
  "your_new_variable": "default_value"
}
```

### 2. Use in Templates
Reference in any template file:
```python
# In {{cookiecutter.project_slug}}/config.py
YOUR_SETTING = "{{cookiecutter.your_new_variable}}"
```

### 3. Conditional Logic
Use Jinja2 conditions for optional features:
```python
{% if cookiecutter.include_oauth_passthrough == 'yes' %}
from .decorators.oauth_passthrough import oauth_passthrough
{% endif %}
```

## Managing Conditional Files

### Entire File Inclusion
Control file generation in `hooks/post_gen_project.py`:
```python
if '{{ cookiecutter.include_oauth_passthrough }}' != 'yes':
    remove_file('{{cookiecutter.project_slug}}/tools/github_passthrough_tools.py')
```

### Partial Content
Use Jinja2 blocks within files:
```python
async def main():
    tools = [tool1, tool2]
    {% if cookiecutter.include_oauth_passthrough == 'yes' %}
    tools.extend(oauth_tools)
    {% endif %}
```

## Post-Generation Hooks

### Structure
```
hooks/
├── pre_gen_project.py   # Runs before template rendering
└── post_gen_project.py  # Runs after template rendering
```

### Common Patterns

#### Remove Optional Files
```python
def remove_file(filepath):
    os.unlink(filepath)

if '{{ cookiecutter.include_streamlit_ui }}' != 'yes':
    shutil.rmtree('{{cookiecutter.project_slug}}/ui')
```

#### Configure Based on Options
```python
if '{{ cookiecutter.python_version }}' == '3.11':
    # Update pyproject.toml for Python 3.11
    update_pyproject_toml()
```

#### Set Executable Permissions
```python
for script in ['test_mcp_integration.sh', 'test_mcp_with_claude.sh']:
    st = os.stat(script)
    os.chmod(script, st.st_mode | stat.S_IEXEC)
```

## Testing Template Generation

### Manual Testing
```bash
# Generate with defaults
cookiecutter . --no-input

# Generate with custom values
cookiecutter . --no-input \
  project_name="Test Server" \
  include_oauth_passthrough=yes

# Interactive generation
cookiecutter .
```

### Automated Testing
Create a test script:
```python
# test_template_generation.py
from cookiecutter.main import cookiecutter

def test_default_generation():
    result = cookiecutter(
        '.',
        no_input=True,
        output_dir='test_output'
    )
    assert os.path.exists(f'{result}/pyproject.toml')
    
def test_oauth_included():
    result = cookiecutter(
        '.',
        no_input=True,
        extra_context={'include_oauth_passthrough': 'yes'}
    )
    assert os.path.exists(f'{result}/tools/github_passthrough_tools.py')
```

## File Organization

### Template Structure
```
{{cookiecutter.project_slug}}/
├── Static files (copied as-is)
│   ├── .reference/           # Never templated
│   └── docs/images/          # Binary files
├── Templated files
│   ├── *.py                  # All Python files
│   ├── *.md                  # Documentation
│   └── pyproject.toml        # Configuration
└── Conditional files
    └── ui/                   # Only if include_streamlit_ui=yes
```

### Variable Naming Conventions
- Use `snake_case` for variable names
- Prefix boolean options with `include_` or `use_`
- Provide sensible defaults that work out-of-box
- Document each variable's purpose in README

## Common Pitfalls

### 1. Raw Brackets in Python
Use `{% raw %}` for literal brackets:
```python
{% raw %}
decorators = {
    "tool_logger": tool_logger,
    "exception_handler": exception_handler
}
{% endraw %}
```

### 2. Conditional Imports
Always handle missing optional imports:
```python
{% if cookiecutter.include_oauth_passthrough == 'yes' %}
from .oauth_passthrough import oauth_passthrough
{% else %}
oauth_passthrough = None
{% endif %}
```

### 3. Path Handling
Use `pathlib` for cross-platform compatibility:
```python
from pathlib import Path
project_dir = Path.cwd()
file_to_remove = project_dir / "optional_file.py"
```

## Validation

### Pre-Generation Validation
In `hooks/pre_gen_project.py`:
```python
import re
import sys

MODULE_REGEX = r'^[_a-zA-Z][_a-zA-Z0-9]+$'

module_name = '{{ cookiecutter.project_slug }}'
if not re.match(MODULE_REGEX, module_name):
    print(f'ERROR: {module_name} is not a valid Python module name!')
    sys.exit(1)
```

### Post-Generation Checks
Verify critical files exist:
```python
required_files = [
    'pyproject.toml',
    '{{cookiecutter.project_slug}}/server/app.py',
    '.reference/saaga-mcp-integration.md'
]

for file in required_files:
    if not os.path.exists(file):
        print(f'WARNING: Required file {file} was not generated!')
```

## Testing Your Changes

1. **Generate a test project**: Use the template with various options
2. **Run the generated tests**: Ensure all tests pass in generated project
3. **Test MCP integration**: Use MCP Inspector or test scripts
4. **Check documentation**: Ensure README is accurate for options chosen
5. **Verify .reference/**: Confirm reference docs are complete and correct