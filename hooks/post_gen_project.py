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

        # Show Admin UI info
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


def cleanup_conditional_files():
    """Remove files that shouldn't exist based on cookiecutter choices.
    
    This prevents empty or stub files from being generated when features
    are not selected, keeping the generated project clean.
    """
    files_removed = []
    
    # OAuth Passthrough files
    if "{{ cookiecutter.include_oauth_passthrough }}" != "yes":
        oauth_passthrough_files = [
            "tests/unit/test_oauth_passthrough.py",
            "tests/integration/test_oauth_passthrough_integration.py",
            "{{ cookiecutter.project_slug }}/tools/github_passthrough_tools.py",
            "{{ cookiecutter.project_slug }}/decorators/oauth_passthrough.py",
        ]
        for file_path in oauth_passthrough_files:
            if os.path.exists(file_path):
                os.remove(file_path)
                files_removed.append(file_path)
    
    # OAuth Backend files
    if "{{ cookiecutter.include_oauth_backend }}" != "yes":
        oauth_backend_files = [
            "tests/unit/test_oauth_backend.py",
            "tests/integration/test_oauth_backend_integration.py",
            "tests/helpers/mock_oauth_backend.py",
            "{{ cookiecutter.project_slug }}/tools/reddit_backend_tools.py",
            "{{ cookiecutter.project_slug }}/decorators/oauth_backend.py",
            "{{ cookiecutter.project_slug }}/clients/oauth_api_client.py",
            "test_oauth_backend.py",
            "test_oauth_backend_simple.py",
            "test_oauth_backend_with_real_http.py",
            "docs/OAUTH_BACKEND.md",
            "docs/OAUTH_COMPARISON.md",
        ]
        for file_path in oauth_backend_files:
            if os.path.exists(file_path):
                os.remove(file_path)
                files_removed.append(file_path)
    
    
    if files_removed:
        print(f"\n🧹 Cleaned up {len(files_removed)} conditional files not needed for this configuration")
        for file_path in files_removed[:5]:  # Show first 5
            print(f"   - {file_path}")
        if len(files_removed) > 5:
            print(f"   ... and {len(files_removed) - 5} more")


def main():
    """Main entry point for the post-generation hook."""
    print("\n🔧 Running post-generation hook...")
    
    # Get cookiecutter context for use throughout
    context = get_cookiecutter_context()
    
    # Clean up conditional files first
    cleanup_conditional_files()

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

    # Create MCP config files for various transports
    create_integration_test_config()

    # Claude setup has been moved to a separate command file
    # See claude-setup-command.md in the root directory for the command to run

    print("\n✅ Post-generation hook completed!")
    
    # Print reminder about Claude Code setup in SAAGA
    print("\n" + "="*70)
    print("📌 IMPORTANT: Claude Code Setup in SAAGA")
    print("="*70)
    print("\nTo use this MCP server with Claude Code in SAAGA:")
    print(f"1. Launch Claude Code in SAAGA")
    print(f"2. Run the command: /setup-mcp {context['project_slug']} {{ cookiecutter.server_port }}")
    print(f"   (This configures the MCP server on port {{ cookiecutter.server_port }})")
    print("\nThe server will be available at:")
    print(f"   http://localhost:{{ cookiecutter.server_port }}/mcp")
    print("="*70)
    
    # Don't fail the entire cookiecutter generation for any errors
    sys.exit(0)


if __name__ == "__main__":
    main()
