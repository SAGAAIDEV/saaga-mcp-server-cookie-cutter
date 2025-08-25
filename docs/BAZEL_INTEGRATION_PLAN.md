# Bazel Integration Plan for SAAGA MCP Server Cookie-Cutter

## Overview

This document outlines the plan to add Bazel BUILD file support to the SAAGA MCP server cookie-cutter template, enabling generated MCP servers to integrate seamlessly with the SAAGA build system.

**Status**: ✅ BUILD.bazel template implemented (January 2025)

## Analysis of Existing Patterns

### SQLite MCP Server BUILD.bazel Pattern

The SQLite MCP server provides the cleanest example for Python-based MCP servers:

```bazel
load("@rules_python//python:defs.bzl", "py_binary", "py_library")

py_binary(
    name = "sqlite",
    srcs = ["main.py"],
    imports = ["src"],
    main = "main.py",
    visibility = ["//visibility:public"],
    deps = [":sqlite_lib"],
)

py_library(
    name = "sqlite_lib",
    srcs = glob(["src/mcp_server_sqlite/*.py"]),
    imports = ["src"],
    visibility = ["//visibility:public"],
    deps = [
        "@mcp_pypi//mcp",
        "@mcp_pypi//pydantic",
    ],
)
```

### Key Patterns Identified

1. **Two-target structure**: `py_binary` for the executable, `py_library` for the source code
2. **Import path management**: Uses `imports = ["src"]` or similar to set Python import paths
3. **Dependency declaration**: External deps use `@mcp_pypi//` prefix
4. **Public visibility**: Both targets are publicly visible for integration
5. **Glob patterns**: Uses `glob()` to automatically include all Python files

## Implementation Status

### ✅ BUILD.bazel Template Created

The BUILD.bazel template has been successfully implemented at:
`/Users/andrew/saga/saaga-mcp-server-cookie-cutter/{{cookiecutter.project_slug}}/BUILD.bazel`

The template:
- Follows the SQLite MCP server pattern
- Adapts paths for the cookie-cutter project structure
- Includes conditional dependencies based on `include_admin_ui`
- Uses proper Python imports and visibility settings

## Original Implementation Plan

### 1. Create BUILD.bazel Template

Location: `/Users/andrew/saga/saaga-mcp-server-cookie-cutter/{{cookiecutter.project_slug}}/BUILD.bazel`

Template content:
```bazel
load("@rules_python//python:defs.bzl", "py_binary", "py_library")

py_binary(
    name = "{{ cookiecutter.project_slug }}",
    srcs = ["{{ cookiecutter.project_slug }}/__main__.py"],
    imports = ["."],
    main = "{{ cookiecutter.project_slug }}/__main__.py",
    visibility = ["//visibility:public"],
    deps = [":{{ cookiecutter.project_slug }}_lib"],
)

py_library(
    name = "{{ cookiecutter.project_slug }}_lib",
    srcs = glob(["{{ cookiecutter.project_slug }}/**/*.py"]),
    imports = ["."],
    visibility = ["//visibility:public"],
    deps = [
        "@mcp_pypi//mcp",
        "@mcp_pypi//pydantic",
        "@mcp_pypi//streamlit",
        "@mcp_pypi//platformdirs",
        # Add additional dependencies based on your requirements
    ],
)
```

### 2. Update Cookie-Cutter Variables

No new variables needed since this is Python-only. The existing variables are sufficient:
- `project_slug` - Used for target names

### 3. Integration Process for Generated Servers

When a new MCP server is generated from the cookie-cutter:

1. **Generate the server**:
   ```bash
   cookiecutter /Users/andrew/saga/saaga-mcp-server-cookie-cutter
   ```

2. **Move to appropriate location** under `/Users/andrew/saaga/mcp/`:
   - `mcp/db/` - For database-related servers
   - `mcp/ops/` - For operations/communication servers
   - `mcp/finance/` - For finance-related servers
   - `mcp/analytics/` - For analytics servers
   - etc.

3. **Update consuming targets** (e.g., usrpod) to include the new server:
   ```bazel
   sh_binary(
       name = "usrpod",
       srcs = ["run.sh"],
       data = [
           ":node_modules",
           "//mcp/db/fileio",
           "//mcp/db/sqlite",
           "//mcp/category/your_new_server",  # Add this line
           "//packages/vendor/supergateway",
       ],
   )
   ```

### 4. Bazel Workspace Requirements

The SAAGA workspace must have:
- `@rules_python` configured for Python rules
- `@mcp_pypi` repository defined for Python dependencies
- Proper Python toolchain configuration

### 5. Testing the Integration

After adding BUILD.bazel to the cookie-cutter:

1. Generate a test server
2. Place it in the SAAGA mcp directory
3. Run `bazel build //mcp/test/test_server`
4. Verify the build succeeds
5. Test integration with usrpod or other consuming targets

## Benefits

1. **Consistent build configuration** across all MCP servers
2. **Automatic dependency management** through Bazel
3. **Easy integration** with the larger SAAGA system
4. **Reproducible builds** across different environments
5. **Clear visibility** of dependencies and build targets

## Future Enhancements

1. Support for containerization (OCI images) if needed
2. Support for additional languages (TypeScript/JavaScript) if requirements change
3. Automated testing targets
4. Documentation generation targets

## Notes

- The BUILD.bazel file acts as the integration point between individual MCP servers and the SAAGA build system
- Each generated server becomes a Bazel package that can be referenced by other parts of the system
- The pattern follows the existing SQLite server example for consistency