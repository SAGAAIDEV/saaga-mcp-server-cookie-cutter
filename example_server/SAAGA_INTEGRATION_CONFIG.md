# SAAGA Supergateway Integration Configuration for example_server

This document contains all the configuration snippets needed to integrate the `example_server` MCP server into the SAAGA supergateway infrastructure.

## Server Details
- **Server Name**: example_server
- **Target Name**: example_server_bin (from BUILD.bazel)
- **Suggested Port**: 8008 (assuming 8001-8007 are taken based on checklist)
- **Runtime Type**: Python
- **Hub Name**: mcp_example_server

## Configuration Updates Required

### 1. MODULE.bazel Configuration
Add the following pip.parse configuration to your MODULE.bazel file:

```python
pip.parse(
    download_only = True,
    extra_pip_args = ["--only-binary=:all:"],
    hub_name = "mcp_example_server",
    python_version = "3.12",
    requirements_by_platform = {
        "//mcp/research/example_server:requirements_linux_arm64.txt": "linux_arm64",
        "//mcp/research/example_server:requirements.txt": "linux_x86_64,osx_aarch64,osx_x86_64,windows_x86_64",
    },
)
```

Also add to the use_repo call:
```python
use_repo(pip, ..., "mcp_example_server")
```

### 2. mcp/usrpod/BUILD.bazel Updates
Add to both `usrpod` and `usrpod_container` sh_binary data sections:

```python
"//mcp/research/example_server:example_server_bin",
```

### 3. mcp/usrpod/run.sh Launch Command
Add the following launch command:

```bash
# Run example_server in background
packages/vendor/supergateway/supergateway_/supergateway \
    --stdio "mcp/research/example_server/example_server_bin" \
    --outputTransport sse \
    --port 8008 &
```

### 4. mcp/usrpod/run-container.sh Launch Command
Add the following for Python server:

```bash
# Run example_server in background using python3
cd "${RUNFILES_ROOT}/packages/vendor/supergateway" && node main.js \
    --stdio "python3 ${RUNFILES_ROOT}/mcp/research/example_server/example_server_bin" \
    --outputTransport sse \
    --port 8008 &
```

### 5. solve/src/config/mcp-servers.ts Configuration
Add the following configuration:

```typescript
example_server: {
  type: 'sse',
  url: process.env.EXAMPLE_SERVER_URL || 'http://localhost:8008/sse',
  description: 'A fully-featured example MCP server demonstrating all SAAGA patterns and features',
  enabled: true,
},
```

### 6. stacks/60.solve/service.tf Port Configuration
Add the following port configuration:

```hcl
port {
  name        = "example-server-mcp"  # Using kebab-case
  port        = 8008
  target_port = 8008
  protocol    = "TCP"
}
```

## Environment Variable
The expected environment variable that should be set in AWS Parameter Store:
```
EXAMPLE_SERVER_URL=http://usrpod:8008/sse
```

## Parallel Execution Script
To apply all changes simultaneously, you can use these commands in parallel:

```bash
# Step 1: Read all files first (parallel)
cat MODULE.bazel
cat mcp/usrpod/BUILD.bazel
cat mcp/usrpod/run.sh
cat mcp/usrpod/run-container.sh
cat solve/src/config/mcp-servers.ts
cat stacks/60.solve/service.tf

# Step 2: Apply all edits simultaneously
# Use your preferred editor or automated tools to apply all 6 changes

# Step 3: Verify the build
bazel build //mcp/research/example_server:example_server_bin

# Step 4: Commit all changes together
git add MODULE.bazel \
    mcp/usrpod/BUILD.bazel \
    mcp/usrpod/run.sh \
    mcp/usrpod/run-container.sh \
    solve/src/config/mcp-servers.ts \
    stacks/60.solve/service.tf
git commit -m "feat: Integrate example_server MCP server into supergateway infrastructure"
```

## Testing Commands

### Local Testing
```bash
# Test Bazel build
cd mcp/research/example_server
bazel build :example_server_bin

# Verify all files were updated
git diff --name-only | sort
# Should show exactly 6 files modified
```

### Port Verification
```bash
# Check if port 8008 is already in use
grep -h "port 800" mcp/usrpod/run.sh | grep -o "800[0-9]" | sort -n
```

## Common Issues and Solutions

1. **Build Failures**: Ensure all dependencies in requirements.txt are included in BUILD.bazel deps
2. **Binary Path Issues**: The binary name must match between BUILD.bazel and run scripts
3. **Port Conflicts**: Verify port 8008 is not already assigned to another service
4. **Hub Name Mismatch**: Ensure @mcp_example_server// matches between MODULE.bazel and BUILD.bazel

## Notes
- The BUILD.bazel already has the correct hub name (@mcp_example_server) in the deps
- The target name is `example_server_bin` which should be used in all references
- This is a Python server, so use python3 prefix in container launch command
- Port 8008 is suggested but verify it's available in your infrastructure