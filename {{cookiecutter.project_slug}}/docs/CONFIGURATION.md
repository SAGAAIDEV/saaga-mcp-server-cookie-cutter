# Configuration Guide for {{ cookiecutter.project_name }}

This document provides comprehensive guidance on configuring your {{ cookiecutter.project_name }} MCP server.

## Configuration File Location

The configuration file `config.yaml` is automatically created in platform-specific locations:

- **Windows**: `%APPDATA%\{{ cookiecutter.project_slug }}\config.yaml`
- **macOS**: `~/Library/Application Support/{{ cookiecutter.project_slug }}/config.yaml`
- **Linux**: `~/.config/{{ cookiecutter.project_slug }}/config.yaml`

## Configuration Structure

The configuration file uses YAML format with the following main sections:

### Server Configuration

```yaml
server:
  name: "{{ cookiecutter.project_name }}"
  description: "{{ cookiecutter.description }}"
  port: {{ cookiecutter.server_port }}
  host: "127.0.0.1"
  transport: "stdio"
  log_level: "{{ cookiecutter.log_level }}"
  log_retention_days: {{ cookiecutter.log_retention_days }}
```

**Settings:**
- `name`: Display name for the MCP server
- `description`: Brief description of the server's purpose
- `port`: Port number for SSE transport (if used)
- `host`: Host address for server binding
- `transport`: Transport protocol ("stdio" or "sse")
- `log_level`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `log_retention_days`: How long to keep log entries

{% if cookiecutter.include_parallel_example == 'yes' -%}
### Parallel Processing Configuration

```yaml
server:
  parallel:
    max_workers: 4
    timeout_seconds: 300
    enable_multiprocessing: true
```

**Settings:**
- `max_workers`: Maximum number of parallel worker processes
- `timeout_seconds`: Timeout for parallel operations
- `enable_multiprocessing`: Enable/disable multiprocessing support
{% endif -%}

### Logging Configuration

```yaml
logging:
  level: "{{ cookiecutter.log_level }}"
  retention_days: {{ cookiecutter.log_retention_days }}
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  database_logging: true
  file_logging: true
```

**Settings:**
- `level`: Log level (DEBUG, INFO, WARNING, ERROR)
- `retention_days`: Days to retain log entries
- `format`: Python logging format string
- `database_logging`: Enable SQLite logging database
- `file_logging`: Enable file-based logging

### Tools Configuration

```yaml
tools:
  enabled_tools: []  # Empty means all tools enabled
  tool_timeout_seconds: 300
  
  {% if cookiecutter.include_example_tools == 'yes' -%}
  example_tools:
    - name: "get_time"
      enabled: true
      timeout_seconds: 5
    - name: "calculate_fibonacci"
      enabled: true
      timeout_seconds: 30
  {% endif -%}
```

**Settings:**
- `enabled_tools`: List of enabled tool names (empty = all enabled)
- `tool_timeout_seconds`: Global timeout for tool execution
- `example_tools`: Individual tool configurations

### Feature Flags

```yaml
features:
  admin_ui: {{ cookiecutter.include_admin_ui == 'yes' }}
  example_tools: {{ cookiecutter.include_example_tools == 'yes' }}
  parallel_examples: {{ cookiecutter.include_parallel_example == 'yes' }}
  database_logging: true
  file_logging: true
  auto_reload: false
```

{% if cookiecutter.include_admin_ui == 'yes' -%}
### UI Configuration

```yaml
ui:
  title: "{{ cookiecutter.project_name }} Admin"
  port: {{ cookiecutter.server_port | int + 1 }}
  host: "127.0.0.1"
  theme: "light"
  show_logs: true
  show_config: true
  show_tools: true
  refresh_interval_seconds: 30
```

**Settings:**
- `title`: Admin UI page title
- `port`: Port for Streamlit UI
- `theme`: UI theme ("light" or "dark")
- `show_*`: Enable/disable UI sections
- `refresh_interval_seconds`: Auto-refresh interval
{% endif -%}

## Example Configurations

### Development Configuration

Optimized for development with debug logging and auto-reload:

```yaml
version: 1
server:
  name: "{{ cookiecutter.project_name }} Dev"
  port: {{ cookiecutter.server_port }}
  log_level: "DEBUG"
development:
  debug_mode: true
  auto_reload: true
  profiling_enabled: true
features:
  admin_ui: true
  example_tools: true
```

### Production Configuration

Optimized for production with security and performance features:

```yaml
version: 1
server:
  name: "{{ cookiecutter.project_name }} Prod"
  port: {{ cookiecutter.server_port }}
  log_level: "INFO"
security:
  enable_cors: true
  api_key_required: true
  rate_limiting:
    enabled: true
    requests_per_minute: 60
performance:
  cache_enabled: true
  connection_pool_size: 20
```

### Testing Configuration

Optimized for automated testing:

```yaml
version: 1
server:
  name: "{{ cookiecutter.project_name }} Test"
  port: {{ cookiecutter.server_port }}
  log_level: "WARNING"
development:
  mock_external_services: true
features:
  admin_ui: false
  example_tools: true
```

## Configuration Management

### Validation

Validate your configuration file:

```bash
python -m {{ cookiecutter.project_slug }}.config --validate
```

### Health Check

Perform a comprehensive health check:

```bash
python -m {{ cookiecutter.project_slug }}.config --health-check
```

### Migration

Configuration files are automatically migrated when the server starts. Manual migration is also supported through the configuration module.

### Backup

Configuration backups are automatically created before updates. Backups are stored with timestamps and only the last 5 backups are retained.

## Advanced Configuration

### Security Settings

```yaml
security:
  enable_cors: false
  allowed_origins: []
  api_key_required: false
  rate_limiting:
    enabled: false
    requests_per_minute: 60
```

### Performance Settings

```yaml
performance:
  cache_enabled: true
  cache_ttl_seconds: 3600
  connection_pool_size: 10
  request_timeout_seconds: 30
```

### Development Settings

```yaml
development:
  debug_mode: false
  auto_reload: false
  profiling_enabled: false
  mock_external_services: false
```

## Configuration Version History

### Version 1 (Current)
- Added comprehensive configuration structure
- Introduced security and performance sections
- Added tool-specific configurations
- Implemented feature flags

### Version 0 (Legacy)
- Basic server configuration
- Simple logging setup
- Limited customization options

## Troubleshooting

### Common Issues

1. **Configuration file not found**
   - The server will create a default configuration automatically
   - Check the platform-specific location mentioned above

2. **Invalid YAML syntax**
   - Use the validation command to identify syntax errors
   - Ensure proper indentation (spaces, not tabs)

3. **Port conflicts**
   - Change the port number in the server section
   - Ensure the port is not in use by another application

4. **Permission errors**
   - Ensure the configuration directory is writable
   - Check file permissions on the configuration file

### Getting Help

- Use `--health-check` for comprehensive diagnostics
- Check the logs for detailed error messages
- Verify configuration with `--validate` before restarting

## Best Practices

1. **Version Control**: Include `config.yaml.example` in version control, not the actual config
2. **Environment-Specific**: Use different configurations for dev/staging/production
3. **Security**: Never commit sensitive information like API keys
4. **Backup**: Regularly backup your configuration before major changes
5. **Validation**: Always validate configuration changes before deployment