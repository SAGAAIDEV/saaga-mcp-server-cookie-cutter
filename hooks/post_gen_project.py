#!/usr/bin/env python
"""Post-generation hook to resolve and inject absolute paths into the generated project."""

import os
import sys
import platform
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


def main():
    """Main entry point for the post-generation hook."""
    print("\n🔧 Running post-generation hook for path resolution...")
    
    try:
        update_readme_with_paths()
        print("✅ Path resolution completed successfully!")
    except Exception as e:
        print(f"⚠️  Warning: Failed to update paths in README.md: {e}")
        print("   You may need to manually update the paths in the configuration examples.")
        # Don't fail the entire cookiecutter generation for this
        sys.exit(0)


if __name__ == "__main__":
    main()