# JIRA Issues - Phases 5-6: MCP Server Cookie Cutter

## Phase 5: Documentation and Examples

### ACT-155: README and Documentation Templates

**Labels:** mcp, cookie-cutter, documentation

**Background & Goal:**
The cookie cutter template needs comprehensive documentation that helps developers understand both how to use the template and how to work with the generated MCP server. This includes the main README for the cookie cutter itself, README template for generated projects, and additional documentation templates that cover common scenarios.

**Goal:** Create a complete documentation suite that enables developers to quickly understand and effectively use both the cookie cutter template and the generated MCP servers.

**Acceptance Criteria:**
1. Create main cookie cutter README.md with:
   - Clear project overview and benefits
   - Prerequisites and installation instructions
   - Cookie cutter variables explanation
   - Quick start guide with examples
   - Links to additional resources

2. Create README template for generated projects ({{cookiecutter.project_slug}}/README.md.jinja2) with:
   - Dynamic content based on cookie cutter choices
   - Installation and setup instructions
   - MCP client configuration examples (Claude Desktop, Cursor)
   - Tool documentation placeholders
   - Troubleshooting section

3. Create CONTRIBUTING.md template with:
   - Development setup instructions
   - Code style guidelines
   - Testing requirements
   - Pull request process

4. Create API_DOCUMENTATION.md template with:
   - Tool documentation structure
   - Parameter descriptions
   - Example requests and responses
   - Error handling documentation

5. Create ARCHITECTURE.md template explaining:
   - Decorator pattern implementation
   - Logging system design
   - Configuration management
   - Optional Streamlit UI integration

**Technical Guidance:**
- Use Jinja2 templating for dynamic content based on cookie cutter variables
- Include code snippets and examples throughout
- Ensure documentation works for both stdio and SSE transport modes
- Reference the SAAGA decorator patterns clearly
- Include platform-specific instructions where needed (Windows, macOS, Linux)

---

### ACT-156: Example Tools and Usage Patterns

**Labels:** mcp, cookie-cutter, documentation

**Background & Goal:**
Developers need concrete examples to understand how to build tools with the SAAGA decorator patterns. The template should include optional example tools that demonstrate best practices for exception handling, logging, and parallelization.

**Goal:** Provide well-documented example tools that serve as templates for developers to build their own MCP tools using SAAGA patterns.

**Acceptance Criteria:**
1. Create basic example tools when include_example_tools is "yes":
   - Simple calculation tool (demonstrates basic decorator usage)
   - File operation tool (demonstrates exception handling)
   - API fetch tool (demonstrates async patterns)
   - Data processing tool (demonstrates logging)

2. Create parallel example tool when include_parallel_example is "yes":
   - Batch processing tool using parallelize decorator
   - Clear documentation on when to use parallelization
   - Performance comparison examples

3. Create example_patterns.py with common patterns:
   - Input validation patterns
   - Error handling strategies
   - Logging best practices
   - Configuration usage examples

4. Create tests/test_examples.py demonstrating:
   - How to test decorated tools
   - Mocking strategies for decorators
   - Integration testing patterns

5. Include inline documentation in all examples:
   - Clear docstrings following Google style
   - Comments explaining decorator behavior
   - Type hints throughout

**Technical Guidance:**
- Examples should be functional but simple enough to understand
- Show both successful and error scenarios
- Demonstrate proper use of all three decorators (exception_handler, tool_logger, parallelize)
- Include examples of configuration customization
- Show how to access logs programmatically

---

### ACT-157: Developer Guide and Troubleshooting

**Labels:** mcp, cookie-cutter, documentation

**Background & Goal:**
Developers need guidance on common development tasks, debugging strategies, and solutions to frequently encountered issues. This comprehensive guide will help them work effectively with the generated MCP servers.

**Goal:** Create a developer guide that addresses common scenarios, provides debugging strategies, and offers solutions to typical problems.

**Acceptance Criteria:**
1. Create DEVELOPER_GUIDE.md with sections on:
   - Setting up development environment
   - Understanding the decorator chain
   - Adding new tools
   - Customizing decorators
   - Working with the configuration system

2. Create debugging section covering:
   - Enabling debug logging
   - Inspecting decorator behavior
   - Using the SQLite log viewer
   - Common error messages and solutions
   - Performance profiling tips

3. Create troubleshooting guide with:
   - MCP client connection issues
   - Decorator ordering problems
   - Configuration loading errors
   - Streamlit UI issues
   - Platform-specific problems

4. Create FAQ section addressing:
   - When to use each decorator
   - How to handle async tools
   - Configuration best practices
   - Log rotation and maintenance
   - Security considerations

5. Include code snippets for common tasks:
   - Adding custom decorators
   - Extending the logging system
   - Creating custom UI pages
   - Integrating with external services

**Technical Guidance:**
- Use real error messages from testing
- Include command-line examples
- Provide diagnostic scripts where helpful
- Reference specific log entries
- Include platform-specific sections clearly marked

---

## Phase 6: Testing and Validation

### ACT-158: Cookie Cutter Template Testing Framework

**Labels:** mcp, cookie-cutter, testing

**Background & Goal:**
The cookie cutter template needs comprehensive testing to ensure it generates valid projects under all configuration combinations. This includes testing the template rendering, generated code functionality, and integration between components.

**Goal:** Implement a robust testing framework that validates the cookie cutter template and all generated project variations.

**Acceptance Criteria:**
1. Create test suite for cookie cutter template:
   - Test all variable combinations
   - Validate generated file structure
   - Ensure Jinja2 templates render correctly
   - Check for syntax errors in generated Python code

2. Implement automated project generation tests:
   - Generate projects with different configurations
   - Run generated project tests
   - Validate that decorators apply correctly
   - Test both stdio and SSE transport modes

3. Create integration tests for:
   - MCP server startup and shutdown
   - Tool registration with decorators
   - Configuration loading
   - Logging system functionality
   - Optional Streamlit UI launch

4. Implement pre-commit hooks for:
   - Template syntax validation
   - Python code formatting (black)
   - Import sorting (isort)
   - Type checking (mypy)

5. Create GitHub Actions workflow for:
   - Running all tests on PR
   - Testing on Python 3.10, 3.11, 3.12
   - Validating documentation builds
   - Checking for broken links

**Technical Guidance:**
- Use pytest for test framework
- Implement fixtures for common test scenarios
- Use temporary directories for generated projects
- Mock external dependencies appropriately
- Ensure tests run in isolated environments

---

### ACT-159: Cross-Platform Compatibility Testing

**Labels:** mcp, cookie-cutter, testing

**Background & Goal:**
MCP servers need to work reliably across Windows, macOS, and Linux. The cookie cutter template must generate projects that handle platform-specific differences in paths, processes, and system behaviors.

**Goal:** Ensure generated MCP servers work correctly on all major platforms with proper handling of platform-specific concerns.

**Acceptance Criteria:**
1. Test configuration paths on all platforms:
   - Verify platformdirs usage is correct
   - Test path normalization
   - Validate file permissions handling
   - Check Unicode path support

2. Validate process management across platforms:
   - Test stdio communication on each OS
   - Verify signal handling differences
   - Check process cleanup behavior
   - Test with different shells/terminals

3. Test Streamlit UI on all platforms:
   - Verify UI launches correctly
   - Test file upload/download features
   - Check log file access permissions
   - Validate configuration editing

4. Create platform-specific test matrix:
   - Windows 10/11 with PowerShell and CMD
   - macOS 12+ with zsh and bash
   - Ubuntu 20.04/22.04
   - Common Docker environments

5. Document platform-specific requirements:
   - Required system libraries
   - Python version constraints
   - Shell/terminal requirements
   - Known limitations per platform

**Technical Guidance:**
- Use GitHub Actions matrix builds
- Test with os.path and pathlib variations
- Include tests for different file encodings
- Test with spaces and special characters in paths
- Verify SQLite works correctly on all platforms

---

### ACT-160: End-to-End Validation and Release Preparation

**Labels:** mcp, cookie-cutter, testing

**Background & Goal:**
Before releasing the cookie cutter template, we need comprehensive end-to-end validation that simulates real developer workflows. This includes testing the complete journey from template installation to deploying a working MCP server.

**Goal:** Validate the complete developer experience and prepare the template for public release with all necessary documentation and tooling.

**Acceptance Criteria:**
1. Create end-to-end test scenarios:
   - Fresh developer installing template
   - Creating first MCP server
   - Adding custom tools
   - Configuring with MCP clients
   - Using the Streamlit UI

2. Implement release checklist validation:
   - All documentation is complete and accurate
   - Examples run without errors
   - Tests pass on all platforms
   - Security scan shows no vulnerabilities
   - License files are in place

3. Create performance benchmarks:
   - Measure decorator overhead
   - Test logging system performance
   - Validate parallel tool efficiency
   - Check memory usage patterns
   - Document performance characteristics

4. Prepare release automation:
   - Version bumping scripts
   - Changelog generation
   - PyPI package building
   - GitHub release creation
   - Documentation deployment

5. Create post-release validation:
   - Test pip installation
   - Verify cookiecutter command works
   - Check all links in documentation
   - Monitor initial user issues
   - Establish feedback channels

**Technical Guidance:**
- Use semantic versioning
- Create comprehensive CHANGELOG.md
- Include migration guides for future versions
- Set up issue templates for bug reports
- Establish clear contribution guidelines