#!/usr/bin/env python3
"""
Test script to run cookiecutter template generation
"""

import os
import sys

def test_cookiecutter():
    """Test cookiecutter template generation"""
    try:
        # Try to import cookiecutter
        try:
            from cookiecutter.main import cookiecutter
        except ImportError:
            print("cookiecutter module not found. Trying to install...")
            os.system("pip3 install cookiecutter")
            from cookiecutter.main import cookiecutter
        
        # Change to the directory containing the template
        template_dir = '/Users/timkitchens/projects/client-repos/saaga-mcp-server-cookie-cutter'
        os.chdir(template_dir)
        
        # Define the context for cookiecutter
        context = {
            'project_name': 'Test UI Server',
            'project_slug': 'test_ui_server',
            'include_admin_ui': 'yes',
            'include_example_tools': 'yes',
            'include_parallel_example': 'yes',
            'description': 'MCP server with SAAGA decorators',
            'author_name': 'Test Author',
            'author_email': 'test@example.com',
            'python_version': '3.11',
            'server_port': '3001',
            'log_level': 'INFO',
            'log_retention_days': '30'
        }
        
        print(f"Running cookiecutter with context: {context}")
        
        # Run cookiecutter
        result = cookiecutter(
            template_dir,
            no_input=True,
            extra_context=context,
            output_dir=template_dir
        )
        
        print(f"Cookiecutter completed. Generated project at: {result}")
        
        # Check if the generated directory exists
        if os.path.exists(result):
            print("SUCCESS: Project generated successfully!")
            
            # List the contents of the generated directory
            print("\nGenerated directory structure:")
            for root, dirs, files in os.walk(result):
                level = root.replace(result, '').count(os.sep)
                indent = ' ' * 2 * level
                print(f"{indent}{os.path.basename(root)}/")
                subindent = ' ' * 2 * (level + 1)
                for file in files:
                    print(f"{subindent}{file}")
                    
            return True
        else:
            print("ERROR: Generated project directory not found")
            return False
            
    except Exception as e:
        print(f"Error running cookiecutter: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cookiecutter()
    sys.exit(0 if success else 1)