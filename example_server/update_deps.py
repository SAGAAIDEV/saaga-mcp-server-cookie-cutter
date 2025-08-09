#!/usr/bin/env python3
"""
Script to extract package names from requirements.txt and update BUILD.bazel deps
"""
import re
from pathlib import Path

def extract_package_names(requirements_file):
    """Extract package names from requirements.txt file"""
    package_names = []
    
    with open(requirements_file, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if line.startswith('#') or not line:
                continue
            
            # Look for lines with package==version format
            if '==' in line:
                # Extract package name (everything before ==)
                package_name = line.split('==')[0].strip()
                # Convert hyphens to underscores for Python imports
                package_name = package_name.replace('-', '_')
                package_names.append(package_name)
    
    # Remove duplicates and sort
    return sorted(list(set(package_names)))

def update_build_bazel(build_file, package_names):
    """Update BUILD.bazel file with the extracted dependencies"""
    
    # Read the current BUILD.bazel file
    with open(build_file, 'r') as f:
        content = f.read()
    
    # Generate the new dependencies list
    deps_lines = []
    for pkg in package_names:
        deps_lines.append(f'        "@mcp_semrush_mcp//{pkg}",')
    
    deps_content = '\n'.join(deps_lines)
    
    # Find and replace the deps section in py_library
    pattern = r'(py_library\(\s*\n\s*name = "semrush_mcp_lib",.*?\n\s*deps = \[)(.*?)(\n\s*\],\s*\n\))'
    
    def replace_deps(match):
        prefix = match.group(1)
        suffix = match.group(3)
        return f"{prefix}\n{deps_content}{suffix}"
    
    new_content = re.sub(pattern, replace_deps, content, flags=re.DOTALL)
    
    # Write the updated content back
    with open(build_file, 'w') as f:
        f.write(new_content)

def main():
    script_dir = Path(__file__).parent
    requirements_file = script_dir / 'requirements.txt'
    build_file = script_dir / 'BUILD.bazel'
    
    if not requirements_file.exists():
        print(f"Error: {requirements_file} not found")
        return
    
    if not build_file.exists():
        print(f"Error: {build_file} not found")
        return
    
    print("Extracting package names from requirements.txt...")
    package_names = extract_package_names(requirements_file)
    
    print(f"Found {len(package_names)} packages:")
    for pkg in package_names:
        print(f"  - {pkg}")
    
    print("\nUpdating BUILD.bazel...")
    update_build_bazel(build_file, package_names)
    
    print("BUILD.bazel updated successfully!")

if __name__ == '__main__':
    main() 