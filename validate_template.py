#!/usr/bin/env python3
"""
Validate cookiecutter template structure and key files
"""

import os
import json
from pathlib import Path

def validate_template_structure():
    """Validate the cookiecutter template structure"""
    print("🔍 Validating cookiecutter template structure...")
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")
    
    # Check for cookiecutter.json
    cookiecutter_json = current_dir / "cookiecutter.json"
    if not cookiecutter_json.exists():
        print("❌ cookiecutter.json not found!")
        return False
    
    print("✅ cookiecutter.json found")
    
    # Read and validate cookiecutter.json
    try:
        with open(cookiecutter_json, 'r') as f:
            config = json.load(f)
        
        print("✅ cookiecutter.json is valid JSON")
        
        # Check required fields
        required_fields = [
            'project_name', 'project_slug', 'description', 'author_name', 
            'author_email', 'python_version', 'include_admin_ui'
        ]
        
        for field in required_fields:
            if field not in config:
                print(f"❌ Missing required field: {field}")
                return False
        
        print("✅ All required fields present in cookiecutter.json")
        
        # Print configuration
        print("\n📋 Configuration:")
        for key, value in config.items():
            print(f"  {key}: {value}")
        
    except json.JSONDecodeError as e:
        print(f"❌ cookiecutter.json is not valid JSON: {e}")
        return False
    
    # Check for template directory
    template_dir = current_dir / "{{cookiecutter.project_slug}}"
    if not template_dir.exists():
        print("❌ Template directory {{cookiecutter.project_slug}} not found!")
        return False
    
    print("✅ Template directory found")
    
    # Check key template files
    key_files = [
        "{{cookiecutter.project_slug}}/pyproject.toml",
        "{{cookiecutter.project_slug}}/README.md",
        "{{cookiecutter.project_slug}}/{{cookiecutter.project_slug}}/__init__.py",
        "{{cookiecutter.project_slug}}/{{cookiecutter.project_slug}}/server/app.py",
        "{{cookiecutter.project_slug}}/{{cookiecutter.project_slug}}/config.py",
        "{{cookiecutter.project_slug}}/{{cookiecutter.project_slug}}/decorators/__init__.py",
        "{{cookiecutter.project_slug}}/{{cookiecutter.project_slug}}/ui/app.py",
        "{{cookiecutter.project_slug}}/{{cookiecutter.project_slug}}/ui/lib/components.py",
    ]
    
    print("\n🔍 Checking key template files:")
    for file_path in key_files:
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            return False
    
    # Check conditional UI files
    ui_files = [
        "{{cookiecutter.project_slug}}/{{cookiecutter.project_slug}}/ui/lib/components.py",
        "{{cookiecutter.project_slug}}/{{cookiecutter.project_slug}}/ui/lib/styles.py",
        "{{cookiecutter.project_slug}}/{{cookiecutter.project_slug}}/ui/lib/utils.py",
        "{{cookiecutter.project_slug}}/{{cookiecutter.project_slug}}/ui/pages/1_🏠_Home.py",
        "{{cookiecutter.project_slug}}/{{cookiecutter.project_slug}}/ui/pages/2_⚙️_Configuration.py",
        "{{cookiecutter.project_slug}}/{{cookiecutter.project_slug}}/ui/pages/3_📊_Logs.py",
    ]
    
    print("\n🎨 Checking UI template files:")
    for file_path in ui_files:
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            return False
    
    # Check if UI files have conditional content
    print("\n🔧 Checking conditional UI content:")
    ui_main_file = current_dir / "{{cookiecutter.project_slug}}/{{cookiecutter.project_slug}}/ui/app.py"
    try:
        with open(ui_main_file, 'r') as f:
            content = f.read()
            if '{% if cookiecutter.include_admin_ui == "yes" %}' in content:
                print("  ✅ UI files have conditional content")
            else:
                print("  ❌ UI files missing conditional content")
                return False
    except Exception as e:
        print(f"  ❌ Error reading UI file: {e}")
        return False
    
    # Check pyproject.toml for conditional dependencies
    print("\n📦 Checking conditional dependencies:")
    pyproject_file = current_dir / "{{cookiecutter.project_slug}}/pyproject.toml"
    try:
        with open(pyproject_file, 'r') as f:
            content = f.read()
            if '{% if cookiecutter.include_admin_ui == "yes" %}' in content:
                print("  ✅ pyproject.toml has conditional dependencies")
            else:
                print("  ❌ pyproject.toml missing conditional dependencies")
                return False
    except Exception as e:
        print(f"  ❌ Error reading pyproject.toml: {e}")
        return False
    
    return True

def main():
    """Main validation function"""
    print("🚀 Starting cookiecutter template validation...")
    print("=" * 50)
    
    if validate_template_structure():
        print("\n" + "=" * 50)
        print("✅ ALL CHECKS PASSED!")
        print("🎉 The cookiecutter template is properly structured and ready for use.")
        print("\nTo test generation, run:")
        print("cookiecutter . --no-input project_name=\"Test UI Server\" project_slug=\"test_ui_server\" include_admin_ui=\"yes\"")
        return True
    else:
        print("\n" + "=" * 50)
        print("❌ VALIDATION FAILED!")
        print("🔧 Please fix the issues above before using the template.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)