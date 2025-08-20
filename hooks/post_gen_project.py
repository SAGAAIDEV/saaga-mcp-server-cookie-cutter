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
        "server_port": "{{ cookiecutter.server_port }}",
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
    """Create MCP configuration files for both STDIO and Streamable HTTP transports."""
    # Get cookiecutter context
    context = get_cookiecutter_context()
    project_slug = context["project_slug"]

    print(f"\n🧪 Creating MCP configuration files for testing...")

    try:
        # Get absolute project path
        project_path = get_project_path()

        # Create STDIO configuration (traditional)
        stdio_config = {
            "mcpServers": {
                project_slug: {
                    "command": "uv",
                    "args": ["run", "--directory", project_path, f"{project_slug}-server-stdio"],
                }
            }
        }

        # Create Streamable HTTP configuration (for web clients)
        http_config = {
            "mcpServers": {
                project_slug: {
                    "url": "http://localhost:{{ cookiecutter.server_port }}/mcp",
                    "transport": "streamable-http",
                }
            }
        }

        # Create combined configuration showing both options
        combined_config = {
            "mcpServers": {
                f"{project_slug}_stdio": {
                    "command": "uv",
                    "args": ["run", "--directory", project_path, f"{project_slug}-server-stdio"],
                },
                f"{project_slug}_http": {
                    "url": "http://localhost:{{ cookiecutter.server_port }}/mcp",
                    "transport": "streamable-http",
                },
            }
        }

        # Write STDIO configuration
        stdio_config_path = Path(project_path) / "mcp.stdio.json"
        with open(stdio_config_path, "w", encoding="utf-8") as f:
            json.dump(stdio_config, f, indent=2, ensure_ascii=False)

        # Write HTTP configuration
        http_config_path = Path(project_path) / "mcp.http.json"
        with open(http_config_path, "w", encoding="utf-8") as f:
            json.dump(http_config, f, indent=2, ensure_ascii=False)

        # Write combined configuration
        combined_config_path = Path(project_path) / "mcp.combined.json"
        with open(combined_config_path, "w", encoding="utf-8") as f:
            json.dump(combined_config, f, indent=2, ensure_ascii=False)

        print(f"   ✅ Created MCP configuration files:")
        print(f"      - mcp.stdio.json (traditional STDIO transport)")
        print(f"      - mcp.http.json (Streamable HTTP transport for web clients)")
        print(f"      - mcp.combined.json (both transports in one config)")
        print(f"\n   📋 Usage examples:")
        print(f"      STDIO: claude --config {stdio_config_path}")
        print(f"      HTTP:  Start server with 'uv run {project_slug}-server-http'")
        print(
            f"             Then connect client to http://localhost:{{ cookiecutter.server_port }}/mcp"
        )

    except Exception as e:
        print(f"   ⚠️  Warning: Failed to create MCP configs: {e}")


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

    # Create MCP config files for various transports
    create_integration_test_config()

    # Claude setup has been moved to a separate command file
    # See claude-setup-command.md in the root directory for the command to run

    print("\n✅ Post-generation hook completed!")
    # Don't fail the entire cookiecutter generation for any errors
    sys.exit(0)


if __name__ == "__main__":
    main()
