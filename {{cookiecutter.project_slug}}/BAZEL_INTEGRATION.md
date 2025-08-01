# Bazel Integration

This project includes Bazel build support for building and running the MCP server.

## Prerequisites

1. **Bazel**: Install Bazel following the [official installation guide](https://bazel.build/install)
2. **Python**: Ensure Python {{ cookiecutter.python_version }} is available
3. **Requirements**: Run `./refresh_requirements_txt.sh` to generate the requirements files needed by Bazel

## Building with Bazel

```bash
# Build all targets
bazel build //...

# Build the MCP server specifically
bazel build //{{ cookiecutter.project_slug }}:{{ cookiecutter.project_slug }}
```

## Running with Bazel

```bash
# Run the MCP server
bazel run //{{ cookiecutter.project_slug }}:{{ cookiecutter.project_slug }}

# Run with arguments
bazel run //{{ cookiecutter.project_slug }}:{{ cookiecutter.project_slug }} -- --help
```

## Project Structure

The Bazel build is configured in `BUILD.bazel`:

- **py_binary**: `{{ cookiecutter.project_slug }}` - The executable MCP server
- **py_library**: `{{ cookiecutter.project_slug }}_lib` - The library containing all source files

## Dependencies

Dependencies are explicitly listed in the `BUILD.bazel` file. The project includes:

- Core MCP dependencies (mcp, anyio, starlette, uvicorn, click)
- Utility dependencies (platformdirs, loguru, pydantic, pyyaml, python-multipart)
{% if cookiecutter.include_admin_ui == "yes" -%}
- Admin UI dependencies (streamlit, plotly, pandas)
{%- endif %}

### Adding New Dependencies

When adding new dependencies:

1. Add the dependency to `pyproject.toml`
2. Run `./refresh_requirements_txt.sh` to update the requirements files
3. Add the dependency to the `deps` list in `BUILD.bazel`:
   ```python
   deps = [
       # ... existing deps ...
       "@mcp_{{ cookiecutter.project_slug }}//new_package",
   ]
   ```

### Package Name Mappings

Some Python packages have different names in Bazel:

| Python Package | Bazel Target |
|----------------|--------------|
| python-multipart | @mcp_pypi//multipart |
| PyYAML | @mcp_pypi//pyyaml |

## Testing with Bazel

```bash
# Run all tests
bazel test //...

# Run specific test targets
bazel test //tests:all
```

## Troubleshooting

### Import Errors

If you encounter import errors:
- Verify all dependencies are listed in both `pyproject.toml` and `BUILD.bazel`
- Check that the `imports` attribute is correctly set
- Ensure `refresh_requirements_txt.sh` has been run recently

### Missing Dependencies

If Bazel reports missing dependencies:
- Ensure the dependency is in your WORKSPACE pip_parse rule
- Check for package name mappings (e.g., `python-multipart` → `multipart`)
- Verify the dependency exists in the generated requirements files

### Build Cache

To clean the Bazel build cache:
```bash
bazel clean
```

For a full clean including the external dependencies:
```bash
bazel clean --expunge
```