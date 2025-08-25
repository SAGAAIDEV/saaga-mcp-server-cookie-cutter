# Contributing to SAAGA MCP Server Cookie Cutter

Thank you for your interest in contributing to the SAAGA MCP Server Cookie Cutter! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Project Structure](#project-structure)
- [Style Guidelines](#style-guidelines)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please treat all contributors and users with respect.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- [UV](https://github.com/astral-sh/uv) - An extremely fast Python package manager

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/saaga-mcp-server-cookie-cutter.git
   cd saaga-mcp-server-cookie-cutter
   ```

## Development Setup

1. Create a virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   # Or simply use: uv shell
   
   uv sync --extra dev
   ```

2. Install pre-commit hooks:
   ```bash
   uv run pre-commit install
   ```

## Making Changes

### Branch Naming Convention

Create branches using the following format:
- `feature/description-of-feature`
- `bugfix/description-of-fix`
- `docs/description-of-documentation-change`

### Development Process

1. Create a new branch for your changes:
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. Make your changes following the style guidelines
3. Test your changes locally
4. Commit your changes with clear, descriptive messages
5. Push to your fork and create a pull request

## Testing

### Running Tests

Run the full test suite:
```bash
uv run pytest tests/
```

### Testing Template Generation

Test that the cookiecutter template works correctly:

1. Test minimal generation:
   ```bash
   uv run cookiecutter . --no-input
   ```

2. Test with all features enabled:
   ```bash
   uv run cookiecutter . --no-input
   ```

3. Test generated project:
   ```bash
   cd my_mcp_server  # or whatever name was generated
   uv sync
   uv run pytest tests/
   ```

### Adding New Tests

When adding new features:
1. Add unit tests in the `tests/` directory
2. Test template generation with your changes
3. Ensure all existing tests still pass

## Submitting Changes

### Pull Request Process

1. Update documentation if needed
2. Ensure all tests pass
3. Update the CHANGELOG.md if applicable
4. Create a pull request with:
   - Clear title and description
   - Reference to any related issues
   - Screenshots (if applicable)
   - Test results

### Pull Request Guidelines

- Keep PRs focused and atomic
- Write clear commit messages
- Update documentation as needed
- Ensure backwards compatibility when possible
- Follow the established code style

## Project Structure

### Repository Structure

```
saaga-mcp-server-cookie-cutter/
├── cookiecutter.json              # Template configuration
├── pyproject.toml                 # Project configuration and dependencies
├── uv.lock                        # Locked dependency versions
├── .pre-commit-config.yaml       # Code quality hooks
├── .github/workflows/test.yml     # CI/CD pipeline
├── tests/                         # Test suite
├── docs/                          # Documentation
├── {{cookiecutter.project_slug}}/ # Template directory
│   ├── {{cookiecutter.project_slug}}/
│   │   ├── server/               # FastMCP server code
│   │   ├── tools/                # MCP tools
│   │   ├── decorators/           # SAAGA decorators
│   │   └── ui/                   # Streamlit UI
│   ├── tests/                    # Generated project tests
│   ├── docs/                     # Generated project docs
│   └── pyproject.toml            # Generated project config
└── README.md                     # This file
```

### Template Variables

When adding new template variables:
1. Add them to `cookiecutter.json`
2. Document them in the README
3. Add tests for different variable combinations
4. Update the GitHub Actions workflow if needed

## Style Guidelines

### Python Code Style

- Use [Black](https://github.com/psf/black) for code formatting
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use type hints where appropriate
- Write docstrings for all public functions and classes

### Template Code Style

- Use consistent indentation (4 spaces)
- Add comments for complex template logic
- Use meaningful variable names
- Keep template files focused and modular

### Documentation Style

- Use clear, concise language
- Include code examples where helpful
- Keep README files up to date
- Use proper Markdown formatting

### Commit Message Style

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
type(scope): description

- feat: new feature
- fix: bug fix
- docs: documentation changes
- style: formatting changes
- refactor: code refactoring
- test: adding tests
- chore: maintenance tasks
```

Examples:
```
feat(template): add support for Python 3.12
fix(cookiecutter): resolve variable interpolation issue
docs(readme): update installation instructions
```

## Common Tasks

### Adding a New Template Variable

1. Add the variable to `cookiecutter.json`
2. Use it in template files with `{{cookiecutter.variable_name}}`
3. Add tests for the new variable
4. Update documentation

### Modifying Generated Project Structure

1. Update the template directory structure
2. Modify template files as needed
3. Update the GitHub Actions workflow
4. Test template generation thoroughly

### Adding New Dependencies

1. Add to the appropriate section in `pyproject.toml`:
   ```bash
   # For main dependencies
   uv add package-name
   
   # For development dependencies
   uv add --dev package-name
   ```
2. Update the generated project's `pyproject.toml` template if needed
3. Test compatibility with supported Python versions

## Getting Help

If you need help or have questions:
1. Check existing issues on GitHub
2. Review the documentation
3. Ask questions in pull requests or issues
4. Reach out to maintainers

## Recognition

Contributors will be recognized in:
- Git commit history
- Pull request acknowledgments
- Project documentation (when appropriate)

Thank you for contributing to the SAAGA MCP Server Cookie Cutter!