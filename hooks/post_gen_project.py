#!/usr/bin/env python
"""Post-generation hook for SAAGA MCP Server Cookie Cutter."""

import os
import sys
import platform
import subprocess
import json
from pathlib import Path


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def get_project_path():
    """Get the absolute path of the generated project."""
    return os.path.abspath(os.getcwd())


def get_python_executable_path():
    """Get the path to the Python executable for the virtual environment."""
    project_path = Path(get_project_path())

    # Determine the platform-specific Python executable path
    if platform.system() == "Windows":
        venv_python = project_path / ".venv" / "Scripts" / "python.exe"
    else:
        venv_python = project_path / ".venv" / "bin" / "python"

    return str(venv_python)


def escape_path_for_json(path):
    """Escape backslashes in Windows paths for JSON."""
    # On Windows, paths use backslashes which need to be escaped in JSON
    if platform.system() == "Windows":
        return path.replace("\\", "\\\\")
    return path


def get_cookiecutter_context():
    """Get common cookiecutter context variables."""
    return {
        "project_name": "{{ cookiecutter.project_name }}",
        "project_slug": "{{ cookiecutter.project_slug }}",
        "include_admin_ui": "{{ cookiecutter.include_admin_ui }}",
        "mcp_config_file_path": "{{ cookiecutter.mcp_config_file_path }}",
        "configure_bazel_build_files": "{{ cookiecutter.configure_bazel_build_files }}",
        "update_aws_parameter_store": "{{ cookiecutter.update_aws_parameter_store }}",
    }


# =============================================================================
# README PATH UPDATING
# =============================================================================


def update_readme_with_paths():
    """Replace path placeholders in README.md with actual paths."""
    readme_path = Path("README.md")

    if not readme_path.exists():
        print("WARNING: README.md not found, skipping path injection")
        return

    # Read the current README content
    content = readme_path.read_text()

    # Get the actual paths
    project_path = get_project_path()
    python_exe_path = get_python_executable_path()

    # Escape paths for JSON
    project_path_json = escape_path_for_json(project_path)
    python_exe_path_json = escape_path_for_json(python_exe_path)

    # Get the project slug for the template replacements
    context = get_cookiecutter_context()
    project_slug = context["project_slug"]

    # Replace placeholders with actual paths
    # Handle both old ASEP-47 patterns and new ASEP-41 patterns
    replacements = {
        # Original ASEP-47 patterns (if any remain)
        '"/path/to/your/project"': f'"{project_path_json}"',
        '"/path/to/your/venv/bin/python"': f'"{python_exe_path_json}"',
        '"cwd": "/path/to/your/project"': f'"cwd": "{project_path_json}"',
        '"PYTHONPATH": "/path/to/your/project"': f'"PYTHONPATH": "{project_path_json}"',
        # New ASEP-41 patterns with cookiecutter variable
        f'"/path/to/{project_slug}"': f'"{project_path_json}"',
        f'"cwd": "/path/to/{project_slug}"': f'"cwd": "{project_path_json}"',
        f'"/path/to/{project_slug}/.venv/bin/python"': f'"{python_exe_path_json}"',
        f'"--directory=/path/to/{project_slug}"': f'"--directory={project_path_json}"',
        '"UV_PROJECT_ENVIRONMENT": "/path/to/specific/venv"': f'"UV_PROJECT_ENVIRONMENT": "{escape_path_for_json(str(Path(python_exe_path).parent.parent))}"',
    }

    for placeholder, actual_path in replacements.items():
        content = content.replace(placeholder, actual_path)

    # Write the updated content back
    readme_path.write_text(content)

    print(f"✅ Updated README.md with actual paths:")
    print(f"   Project path: {project_path}")
    print(f"   Python executable: {python_exe_path}")


# =============================================================================
# UV DEPENDENCY INSTALLATION
# =============================================================================


def run_uv_commands():
    """Run uv sync to install dependencies."""
    # Get cookiecutter context
    context = get_cookiecutter_context()
    project_name = context["project_name"]
    project_slug = context["project_slug"]
    include_admin_ui = context["include_admin_ui"]

    print(f"\n📦 Installing dependencies for '{project_name}' with uv...")

    try:
        # Run uv sync (this installs all dependencies including the project itself in editable mode)
        print("   Running: uv sync")
        subprocess.run(
            ["uv", "sync"],
            capture_output=False,  # Allow output to be printed directly
            text=True,
            check=True,
        )
        print("   ✅ uv sync completed successfully")

        # Show additional info based on cookiecutter variables
        if include_admin_ui == "yes":
            print("\n   📊 Admin UI is included! You can run it with:")
            print(f"      uv run streamlit run {project_slug}/ui/app.py")

    except subprocess.CalledProcessError as e:
        print(f"   ⚠️  Warning: Failed to run uv commands: {e}")
        print("   You may need to run 'uv sync' manually.")
    except FileNotFoundError:
        print("   ⚠️  Warning: 'uv' command not found.")
        print("   Please install uv first: https://github.com/astral-sh/uv")
        print("   Then run 'uv sync' manually.")


# =============================================================================
# MCP SERVER CONFIGURATION INSTALLATION
# =============================================================================


def create_integration_test_config():
    """Create mcp.integration_test.json with single server configuration."""
    # Get cookiecutter context
    context = get_cookiecutter_context()
    project_slug = context["project_slug"]

    print(f"\n🧪 Creating mcp.integration_test.json for Claude testing...")

    try:
        # Get absolute project path
        project_path = get_project_path()

        # Create the configuration
        integration_config = {
            "mcpServers": {
                project_slug: {
                    "command": "uv",
                    "args": ["run", "--directory", project_path, f"{project_slug}-server"],
                }
            }
        }

        # Write the integration test configuration
        integration_config_path = Path(project_path) / "mcp.integration_test.json"
        with open(integration_config_path, "w", encoding="utf-8") as f:
            json.dump(integration_config, f, indent=2, ensure_ascii=False)

        print(f"   ✅ Created mcp.integration_test.json")
        print(f"   📋 Test with: claude --config {integration_config_path}")

    except Exception as e:
        print(f"   ⚠️  Warning: Failed to create integration test config: {e}")


def install_mcp_server_config():
    """Install the MCP server configuration into a specified JSON config file."""
    # Get cookiecutter context
    context = get_cookiecutter_context()
    project_name = context["project_name"]
    project_slug = context["project_slug"]
    mcp_config_file_path = context["mcp_config_file_path"]

    # Skip if no path provided
    if not mcp_config_file_path or mcp_config_file_path.strip() == "":
        return

    print(f"\n🔧 Installing MCP server configuration...")

    try:
        # Expand user path and resolve absolute path
        config_path = Path(mcp_config_file_path).expanduser().resolve()

        # Check if file exists
        if not config_path.exists():
            print(f"   ⚠️  Warning: Config file not found: {config_path}")
            print("   Skipping MCP server configuration installation.")
            return

        # Read and parse JSON file
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"   ⚠️  Warning: Invalid JSON in config file: {e}")
            print("   Skipping MCP server configuration installation.")
            return

        # Check if mcpServers key exists
        if "mcpServers" not in config_data:
            print(f"   ⚠️  Warning: Config file does not contain 'mcpServers' key")
            print("   Skipping MCP server configuration installation.")
            return

        # Get absolute project path
        project_path = get_project_path()

        # Create the server configuration entry
        server_config = {
            "command": "uv",
            "args": ["run", "--directory", project_path, f"{project_slug}-server"],
        }

        # Check if project_slug already exists and replace/add
        action = "Updated" if project_slug in config_data["mcpServers"] else "Added"
        config_data["mcpServers"][project_slug] = server_config

        # Write back the updated configuration
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            print(f"   ✅ {action} '{project_slug}' server configuration in: {config_path}")
            print(f"   📋 Configuration:")
            print(f"      Command: uv run --directory {project_path} {project_slug}-server")

        except PermissionError:
            print(f"   ⚠️  Warning: Permission denied writing to: {config_path}")
            print("   You may need to manually add the server configuration.")
        except Exception as e:
            print(f"   ⚠️  Warning: Failed to write config file: {e}")
            print("   You may need to manually add the server configuration.")

    except Exception as e:
        print(f"   ⚠️  Warning: Failed to process MCP config file: {e}")
        print("   You may need to manually add the server configuration.")


def run_refresh_requirements():
    """Run the refresh_requirements_txt.sh script to generate requirements.txt files for Bazel."""
    print("\n📋 Generating requirements.txt files for Bazel...")

    try:
        # Get the refresh script path
        refresh_script = Path(get_project_path()) / "refresh_requirements_txt.sh"

        if not refresh_script.exists():
            print("   ⚠️  Warning: refresh_requirements_txt.sh not found")
            return

        # Make the script executable
        if platform.system() != "Windows":
            os.chmod(refresh_script, 0o755)

        # Run the script
        print("   Running: ./refresh_requirements_txt.sh")
        result = subprocess.run(
            (
                ["bash", str(refresh_script)]
                if platform.system() == "Windows"
                else [str(refresh_script)]
            ),
            capture_output=True,
            text=True,
            cwd=get_project_path(),
        )

        if result.returncode == 0:
            print("   ✅ Requirements files generated successfully")
            if Path(get_project_path(), "requirements.txt").exists():
                print("      - requirements.txt")
            if Path(get_project_path(), "requirements_linux_arm64.txt").exists():
                print("      - requirements_linux_arm64.txt")
        else:
            print(f"   ⚠️  Warning: Failed to generate requirements files")
            if result.stderr:
                print(f"      Error: {result.stderr}")

    except Exception as e:
        print(f"   ⚠️  Warning: Failed to run refresh_requirements_txt.sh: {e}")
        print("   You may need to run './refresh_requirements_txt.sh' manually.")


def run_claude_setup(assigned_port=None):
    """Run Claude with setup instructions if configure_bazel_build_files is set to yes."""
    context = get_cookiecutter_context()
    configure_bazel_build_files = context["configure_bazel_build_files"]

    if configure_bazel_build_files != "yes":
        return

    print("\n🤖 Running Claude setup assistant...")

    # Placeholder for Claude setup instructions

    # Get the specific values we need from context
    project_slug = context["project_slug"]
    env_var_name = f"{project_slug.upper()}_URL"

    # Build port information section
    if assigned_port:
        port_info = f"""## Assigned Port
**Your assigned port: {assigned_port}**

## AWS Environment Variable
**IMPORTANT**: The AWS SSM parameter `solve-env-prod` has been automatically updated with:
```
{env_var_name}=http://usrpod:{assigned_port}/sse
```
This environment variable name **MUST** be used exactly in the TypeScript configuration.
Use port **{assigned_port}** in all configuration files below.

"""
    else:
        port_info = f"""## Port Assignment
**Note**: AWS parameter store update was disabled or failed. You'll need to manually assign a port.
Check existing ports in solve-env-prod and use the next available 8XXX port.

## Environment Variable
The expected environment variable format:
```
{env_var_name}=http://usrpod:[YOUR_PORT]/sse
```

"""

    # Build the instructions with proper string formatting
    intro_section = f"""# MCP Server Setup Checklist

## Overview
This checklist ensures proper configuration when adding a new MCP server to the SAAGA supergateway infrastructure. Use this alongside MCP_SERVER_SETUP_INSTRUCTIONS.md.

## IMPORTANT: Parallel Execution
**All configuration updates can and should be performed IN PARALLEL using concurrent tool calls for maximum efficiency!**

## Auto-Detection
The MCP server being configured: **{project_slug}**

{port_info}"""

    rest_of_instructions = """## Pre-Setup Verification

### 1. Verify BUILD.bazel Configuration
Before integrating the server, ensure the BUILD.bazel in your MCP server directory is correctly configured:

#### Python MCP Servers
```python
load("@rules_python//python:defs.bzl", "py_binary", "py_library")

py_binary(
    name = "my_server",  # This is the target name you'll reference
    srcs = ["my_server/__main__.py"],
    imports = ["my_server"],  # Should match your package directory name
    main = "my_server/__main__.py",
    visibility = ["//visibility:public"],
    deps = [":my_server_lib"],
)

py_library(
    name = "my_server_lib",
    srcs = glob(["my_server/**/*.py"]),
    imports = ["."],
    visibility = ["//visibility:public"],
    deps = [
        # List all your dependencies explicitly
        "@mcp_my_server//mcp",
        "@mcp_my_server//anyio",
        # ... other deps
    ],
)
```

**Common issues to check:**
- [ ] Target name matches what you'll reference (not the directory name)
- [ ] Imports path is correct (package name for py_binary, "." for py_library)
- [ ] Dependencies use the correct hub name (e.g., `@mcp_my_server//`)
- [ ] All required dependencies are listed explicitly

#### Node.js MCP Servers
```javascript
# BUILD.bazel for Node.js servers will differ
# Add appropriate configuration here
```

## Setup Checklist

### PARALLEL EXECUTION STRATEGY
When implementing these changes:
1. **Read all files first** (in parallel) to understand current state
2. **Execute all edits in parallel** - All 6 file modifications can be done simultaneously
3. **Use TodoWrite tool** to track progress across parallel operations

### 1. Choose Configuration
- [ ] Server name: `________________`
- [ ] Port number: `________________` (check existing ports first: 8001-8007 taken, 8008-8030 available)
- [ ] Runtime type: [ ] Python [ ] Node.js

### 2. Update MODULE.bazel (Python servers only)
- [ ] Add pip.parse configuration:
```python
pip.parse(
    download_only = True,
    extra_pip_args = ["--only-binary=:all:"],
    hub_name = "mcp_<server_name>",
    python_version = "3.12",
    requirements_by_platform = {
        "//mcp/research/<server_name>:requirements_linux_arm64.txt": "linux_arm64",
        "//mcp/research/<server_name>:requirements.txt": "linux_x86_64,osx_aarch64,osx_x86_64,windows_x86_64",
    },
)
```
- [ ] Add hub name to use_repo: `use_repo(pip, ..., "mcp_<server_name>")`

### 3. Update BUILD.bazel Dependencies
**File**: `mcp/usrpod/BUILD.bazel`

- [ ] Add to `usrpod` sh_binary data:
```python
"//mcp/research/<server_name>:<target_name>",
```
- [ ] Add to `usrpod_container` sh_binary data (same line)

### 4. Add Supergateway Launch Command
**File**: `mcp/usrpod/run.sh`

- [ ] Add launch command:
```bash
# Run <server_name> in background
packages/vendor/supergateway/supergateway_/supergateway \
    --stdio "mcp/research/<server_name>/<binary_name>" \
    --outputTransport sse \
    --port <port_number> &
```

### 5. Add Container Launch Command
**File**: `mcp/usrpod/run-container.sh`

For Python servers:
- [ ] Add:
```bash
# Run <server_name> in background using python3
cd "${RUNFILES_ROOT}/packages/vendor/supergateway" && \
node main.js --stdio "python3 ${RUNFILES_ROOT}/mcp/research/<server_name>/<binary_name>" \
    --outputTransport sse \
    --port <port_number> &
```

For Node.js servers:
- [ ] Add:
```bash
# Run <server_name> in background using node
cd "${RUNFILES_ROOT}/packages/vendor/supergateway" && \
node main.js --stdio "${RUNFILES_ROOT}/mcp/research/<server_name>/<binary_name>_/<binary_name>" \
    --outputTransport sse \
    --port <port_number> &
```

### 6. Configure Frontend Connection
**File**: `solve/src/config/mcp-servers.ts`

- [ ] Add configuration:
```typescript
<server_name>: {
  type: 'sse',
  url: process.env.<SERVER_NAME>_URL || 'http://localhost:<port_number>/sse',
  description: '<Description of your MCP server>',
  enabled: true,
},
```

**CRITICAL**: The environment variable name `<SERVER_NAME>_URL` must exactly match the AWS SSM parameter variable name that was automatically added to solve-env-prod. This ensures proper environment variable resolution in production.

### 7. Add Kubernetes Service Port
**File**: `stacks/60.solve/service.tf`

- [ ] Add port configuration:
```hcl
port {
  name        = "<server-name>-mcp"  # Use kebab-case
  port        = <port_number>
  target_port = <port_number>
  protocol    = "TCP"
}
```

## Port Selection Helper
```bash
# Find the highest port number in use
grep -h "port [0-9]" mcp/usrpod/run.sh | grep -o "[0-9]\+" | sort -n | tail -1
# Next available port = highest + 1
```

## Testing Verification

### Local Testing
```bash
# Test Bazel build first
cd mcp/research/<server_name>
bazel build :<target_name>

# Verify all files were updated correctly
git diff --name-only | sort
# Should show exactly these 6 files:
# MODULE.bazel
# mcp/usrpod/BUILD.bazel
# mcp/usrpod/run-container.sh
# mcp/usrpod/run.sh
# solve/src/config/mcp-servers.ts
# stacks/60.solve/service.tf
```


### Debug Checklist
If build fails:
- [ ] Check target name matches across all files
- [ ] Verify binary name in run scripts matches BUILD.bazel output
- [ ] Ensure all Python dependencies are in requirements.txt
- [ ] Confirm MODULE.bazel hub name matches BUILD.bazel deps references
- [ ] Check imports paths are correct in BUILD.bazel

## Common Pitfalls

1. **Target name mismatch**: The BUILD.bazel target name must match references in usrpod/BUILD.bazel
2. **Binary path confusion**: The binary path in run.sh/run-container.sh must match the actual output from Bazel
3. **Missing MODULE.bazel entry**: Python servers need pip.parse configuration
4. **Wrong imports path**: py_binary should use package name, py_library should use "."
5. **Dependency hub mismatch**: Ensure @hub_name// matches between MODULE.bazel and BUILD.bazel

## Quick Reference

| File | What to Add | Key Detail |
|------|------------|------------|
| MODULE.bazel | pip.parse block | Hub name: mcp_<server_name> |
| mcp/usrpod/BUILD.bazel | Target reference | //path:<target_name> |
| run.sh | Launch command | Binary path from BUILD |
| run-container.sh | Container launch | Add python3 for Python |
| mcp-servers.ts | Frontend config | Port and env var name |
| service.tf | K8s port | Use kebab-case name |

## Example: Complete Parallel Setup

When setting up a new MCP server, execute ALL of these operations in parallel:

```bash
# 1. First, detect the server and gather info (parallel reads)
- Read mcp/research/<server_name>/BUILD.bazel (get target name)
- Read MODULE.bazel (find insertion point)
- Read mcp/usrpod/run.sh (find highest port)
- Read all other files to understand structure

# 2. Then execute ALL edits simultaneously
- Edit MODULE.bazel (add pip.parse)
- Edit mcp/usrpod/BUILD.bazel (add to both targets)
- Edit mcp/usrpod/run.sh (add launch command)
- Edit mcp/usrpod/run-container.sh (add container launch)
- Edit solve/src/config/mcp-servers.ts (add config)
- Edit stacks/60.solve/service.tf (add port)

# 3. Test and commit
- Run bazel build test
- Commit all 6 files together
```

This parallel approach reduces setup time from ~5 minutes to ~30 seconds!
"""

    # Combine the instruction sections and replace placeholders
    combined_instructions = intro_section + rest_of_instructions

    # Replace generic placeholders with specific values if port is assigned
    if assigned_port:
        claude_setup_instructions = combined_instructions.replace(
            "<port_number>", str(assigned_port)
        )
        claude_setup_instructions = claude_setup_instructions.replace("<server_name>", project_slug)
        claude_setup_instructions = claude_setup_instructions.replace(
            "<SERVER_NAME>", project_slug.upper()
        )
    else:
        claude_setup_instructions = combined_instructions

    try:
        # Run Claude with the setup instructions
        print('   Running: claude -p "<setup instructions>" --dangerously-skip-permissions')
        result = subprocess.run(
            ["claude", "-p", claude_setup_instructions, "--dangerously-skip-permissions"],
            capture_output=True,
            text=True,
            cwd=get_project_path(),
        )

        if result.returncode == 0:
            print("   ✅ Claude setup completed successfully")
            if result.stdout:
                print(f"   Output: {result.stdout}")
        else:
            print(f"   ⚠️  Warning: Claude setup failed")
            if result.stderr:
                print(f"      Error: {result.stderr}")

    except FileNotFoundError:
        print("   ⚠️  Warning: 'claude' command not found.")
        print("   Please ensure Claude CLI is installed and in your PATH.")
    except Exception as e:
        print(f"   ⚠️  Warning: Failed to run Claude setup: {e}")


# =============================================================================
# AWS SSM PARAMETER MANAGEMENT
# =============================================================================


def update_aws_ssm_parameter():
    """Update AWS SSM parameter with incremented port for the new MCP server."""
    # Get cookiecutter context
    context = get_cookiecutter_context()
    project_slug = context["project_slug"]
    update_aws_parameter_store = context["update_aws_parameter_store"]

    # Skip AWS parameter store update if not requested
    if update_aws_parameter_store != "yes":
        print(f"\n⏭️  Skipping AWS parameter store update (disabled in cookiecutter config)")
        return None

    print(f"\n☁️ Updating AWS SSM parameter for '{project_slug}'...")

    # Proactively ensure AWS SSO login
    print("   🔐 Ensuring AWS SSO login...")
    try:
        # Check if AWS CLI is available
        subprocess.run(
            ["aws", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Attempt AWS SSO login
        result = subprocess.run(
            ["aws", "sso", "login"],
            capture_output=False,  # Allow interactive prompts
            text=True,
        )

        if result.returncode != 0:
            print("   ❌ AWS SSO login failed or was declined")
            print("   📋 Manual setup required:")
            print(f"      1. Run 'aws sso login' manually")
            print(f"      2. Add this line to the solve-env-prod AWS SSM parameter:")
            print(f"         {project_slug.upper()}_URL=http://usrpod:[NEXT_PORT]/sse")
            print(f"      3. Find the next available port by checking existing 8XXX ports")
            print(f"      4. Contact saaga@saaga.dev or evan@saaga.dev for assistance")
            return None

        print("   ✅ AWS SSO login completed")

    except FileNotFoundError:
        print("   ❌ AWS CLI not found")
        print("   📋 Manual setup required:")
        print(f"      1. Install AWS CLI: https://aws.amazon.com/cli/")
        print(f"      2. Run 'aws sso login'")
        print(f"      3. Add this line to the solve-env-prod AWS SSM parameter:")
        print(f"         {project_slug.upper()}_URL=http://usrpod:[NEXT_PORT]/sse")
        print(f"      4. Find the next available port by checking existing 8XXX ports")
        print(f"      5. Contact saaga@saaga.dev or evan@saaga.dev for assistance")
        return None
    except Exception as e:
        print(f"   ❌ Unexpected error during AWS setup: {e}")
        print("   📋 Manual setup required:")
        print(f"      1. Run 'aws sso login' manually")
        print(f"      2. Add this line to the solve-env-prod AWS SSM parameter:")
        print(f"         {project_slug.upper()}_URL=http://usrpod:[NEXT_PORT]/sse")
        print(f"      3. Find the next available port by checking existing 8XXX ports")
        print(f"      4. Contact saaga@saaga.dev or evan@saaga.dev for assistance")
        return None

    try:
        # Get current parameter value
        print("   Getting current solve-env-prod parameter...")
        result = subprocess.run(
            [
                "aws",
                "ssm",
                "get-parameter",
                "--name",
                "solve-env-prod",
                "--with-decryption",
                "--query",
                "Parameter.Value",
                "--output",
                "text",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        current_value = result.stdout.strip()

        # Find the highest port starting with 8XXX
        import re

        port_pattern = r"http://usrpod:8(\d{3})/sse"
        ports = []

        for line in current_value.split("\n"):
            matches = re.findall(port_pattern, line)
            for match in matches:
                port_num = int(f"8{match}")
                ports.append(port_num)

                # Determine next port
        if not ports:
            print(f"   ❌ Error: No existing ports starting with 8XXX found in AWS parameter")
            print(f"   This suggests the solve-env-prod parameter may not be properly configured")
            print(f"   Expected to find at least one URL like: http://usrpod:8XXX/sse")
            print(f"   Stopping process to prevent misconfiguration.")
            sys.exit(1)

        next_port = max(ports) + 1

        print(f"   Found existing ports: {sorted(ports)}")
        print(f"   Using next available port: {next_port}")

        # Create new parameter value
        new_line = f"{project_slug.upper()}_URL=http://usrpod:{next_port}/sse"
        new_value = f"{current_value}\n{new_line}"

        # Update parameter
        print("   Updating solve-env-prod parameter...")
        subprocess.run(
            [
                "aws",
                "ssm",
                "put-parameter",
                "--name",
                "solve-env-prod",
                "--value",
                new_value,
                "--type",
                "SecureString",
                "--overwrite",
                "--no-cli-pager",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        print(f"   ✅ Successfully updated AWS SSM parameter")
        print(f"      Added: {new_line}")
        print(f"      Port: {next_port}")

        return next_port

    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed to update AWS SSM parameter: {e}")
        if e.stderr:
            print(f"      Error: {e.stderr}")
        print("   📋 Manual setup required:")
        print(f"      1. Run 'aws sso login' manually if needed")
        print(f"      2. Add this line to the solve-env-prod AWS SSM parameter:")
        print(f"         {project_slug.upper()}_URL=http://usrpod:[NEXT_PORT]/sse")
        print(f"      3. Find the next available port by checking existing 8XXX ports")
        print(f"      4. Contact saaga@saaga.dev or evan@saaga.dev for assistance")
        return None
    except Exception as e:
        print(f"   ❌ Failed to update AWS SSM parameter: {e}")
        print("   📋 Manual setup required:")
        print(f"      1. Run 'aws sso login' manually if needed")
        print(f"      2. Add this line to the solve-env-prod AWS SSM parameter:")
        print(f"         {project_slug.upper()}_URL=http://usrpod:[NEXT_PORT]/sse")
        print(f"      3. Find the next available port by checking existing 8XXX ports")
        print(f"      4. Contact saaga@saaga.dev or evan@saaga.dev for assistance")
        return None


def main():
    """Main entry point for the post-generation hook."""
    print("\n🔧 Running post-generation hook...")

    # Update README.md with actual paths
    try:
        update_readme_with_paths()
        print("✅ Path resolution completed successfully!")
    except Exception as e:
        print(f"⚠️  Warning: Failed to update paths in README.md: {e}")
        print("   You may need to manually update the paths in the configuration examples.")

    # Install dependencies with UV
    run_uv_commands()

    # Generate requirements.txt files for Bazel
    run_refresh_requirements()

    # Install MCP server configuration if requested
    install_mcp_server_config()

    # Create integration test config for Claude
    create_integration_test_config()

    # Update AWS SSM parameter first to get the port
    assigned_port = update_aws_ssm_parameter()

    # Run Claude setup if requested (after AWS parameter is updated)
    run_claude_setup(assigned_port)

    print("\n✅ Post-generation hook completed!")
    # Don't fail the entire cookiecutter generation for any errors
    sys.exit(0)


if __name__ == "__main__":
    main()
