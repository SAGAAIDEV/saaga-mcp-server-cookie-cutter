#!/usr/bin/env python
"""Post-generation hook to resolve and inject absolute paths into the generated project."""

import os
import sys
import platform
import subprocess
from pathlib import Path


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
    
    # Replace placeholders with actual paths
    replacements = {
        '"/path/to/your/project"': f'"{project_path_json}"',
        '"/path/to/your/venv/bin/python"': f'"{python_exe_path_json}"',
        '"cwd": "/path/to/your/project"': f'"cwd": "{project_path_json}"',
        '"PYTHONPATH": "/path/to/your/project"': f'"PYTHONPATH": "{project_path_json}"'
    }
    
    for placeholder, actual_path in replacements.items():
        content = content.replace(placeholder, actual_path)
    
    # Write the updated content back
    readme_path.write_text(content)
    
    print(f"✅ Updated README.md with actual paths:")
    print(f"   Project path: {project_path}")
    print(f"   Python executable: {python_exe_path}")


def run_uv_commands():
    """Run uv sync and uv pip install -e . commands."""
    # Access cookiecutter context
    from cookiecutter.main import cookiecutter
    
    # The context is available as a global variable in post-gen hooks
    project_name = "{{ cookiecutter.project_name }}"
    project_slug = "{{ cookiecutter.project_slug }}"
    include_admin_ui = "{{ cookiecutter.include_admin_ui }}"
    
    print(f"\n📦 Installing dependencies for '{project_name}' with uv...")
    
    try:
        # Run uv sync
        print("   Running: uv sync")
        result = subprocess.run(
            ["uv", "sync"],
            capture_output=False,  # Allow output to be printed directly
            text=True,
            check=True
        )
        print("   ✅ uv sync completed successfully")
        
        # Run uv pip install -e .
        print("   Running: uv pip install -e .")
        result = subprocess.run(
            ["uv", "pip", "install", "-e", "."],
            capture_output=False,  # Allow output to be printed directly
            text=True,
            check=True
        )
        print("   ✅ uv pip install -e . completed successfully")
        
        # Show additional info based on cookiecutter variables
        if include_admin_ui == "yes":
            print("\n   📊 Admin UI is included! You can run it with:")
            print(f"      streamlit run {project_slug}/ui/app.py")
        
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️  Warning: Failed to run uv commands: {e}")
        print("   You may need to run 'uv sync' and 'uv pip install -e .' manually.")
    except FileNotFoundError:
        print("   ⚠️  Warning: 'uv' command not found.")
        print("   Please install uv first: https://github.com/astral-sh/uv")
        print("   Then run 'uv sync' and 'uv pip install -e .' manually.")


def main():
    """Main entry point for the post-generation hook."""
    print("\n🔧 Running post-generation hook...")
    
    try:
        update_readme_with_paths()
        print("✅ Path resolution completed successfully!")
    except Exception as e:
        print(f"⚠️  Warning: Failed to update paths in README.md: {e}")
        print("   You may need to manually update the paths in the configuration examples.")
    
    # Run uv commands
    run_uv_commands()
    
    print("\n✅ Post-generation hook completed!")
    # Don't fail the entire cookiecutter generation for any errors
    sys.exit(0)


if __name__ == "__main__":
    main()