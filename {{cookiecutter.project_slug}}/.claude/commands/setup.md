# Claude Setup Command

This command runs Claude with the MCP server integration instructions for setting up the generated server in the SAAGA infrastructure.

## Command Template

```bash
claude -p "# MCP Server Integration Instructions for {{ cookiecutter.project_slug }}

## Overview
These are the exact files that need to be modified to integrate the **{{ cookiecutter.project_slug }}** MCP server into the SAAGA infrastructure.

## IMPORTANT: Parallel Execution
**Execute ALL file modifications IN PARALLEL using concurrent tool calls for maximum efficiency!**

## Server Configuration
- **Server name**: {{ cookiecutter.project_slug }}
- **Assigned port**: {{ cookiecutter.server_port }}
- **Environment variable**: {{ cookiecutter.project_slug.upper() }}_URL

## Assigned Port
**Your assigned port: {{ cookiecutter.server_port }}**

## AWS Environment Variable
**IMPORTANT**: The AWS SSM parameter \`solve-env-prod\` has been automatically updated with:
\`\`\`
{{ cookiecutter.project_slug.upper() }}_URL=http://usrpod:{{ cookiecutter.server_port }}/sse
\`\`\`
This environment variable name **MUST** be used exactly in the TypeScript configuration.
Use port **{{ cookiecutter.server_port }}** in all configuration files below.

## Files to Modify (Execute ALL in parallel)

### STEP 1: Bazel Build Configuration
**File**: \`mcp/usrpod/BUILD.bazel\`

Add the server to both \`usrpod\` and \`usrpod_container\` targets in the \`data\` section:
\`\`\`python
# Add this line to both targets' data arrays:
\"//mcp/<category>/{{ cookiecutter.project_slug }}:{{ cookiecutter.project_slug }}_bin\",
\`\`\`

Note: Replace \`<category>\` with the appropriate category (social, research, db, ops, etc.)

### STEP 2: Shell Scripts for Server Launch

#### 2a. Local Development Runner
**File**: \`mcp/usrpod/run.sh\`

Add this command block (adjust for Python or Node.js):
\`\`\`bash
# Run {{ cookiecutter.project_slug }} in background
packages/vendor/supergateway/supergateway_/supergateway \\
    --stdio \"mcp/<category>/{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}_bin\" \\
    --outputTransport sse \\
    --port {{ cookiecutter.server_port }} &
\`\`\`

#### 2b. Container Runner  
**File**: \`mcp/usrpod/run-container.sh\`

For Python servers, add:
\`\`\`bash
# Run {{ cookiecutter.project_slug }} in background using python3
cd \"\${RUNFILES_ROOT}/packages/vendor/supergateway\" && node main.js \\
    --stdio \"python3 \${RUNFILES_ROOT}/mcp/<category>/{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}_bin\" \\
    --outputTransport sse \\
    --logLevel info \\
    --port {{ cookiecutter.server_port }} &
\`\`\`

For Node.js servers, add:
\`\`\`bash
# Run {{ cookiecutter.project_slug }} in background using node
cd \"\${RUNFILES_ROOT}/packages/vendor/supergateway\" && node main.js \\
    --stdio \"\${RUNFILES_ROOT}/mcp/<category>/{{ cookiecutter.project_slug }}/{{ cookiecutter.project_slug }}_bin_/{{ cookiecutter.project_slug }}_bin\" \\
    --outputTransport sse \\
    --logLevel info \\
    --port {{ cookiecutter.server_port }} &
\`\`\`

### STEP 3: Frontend Integration

#### 3a. Register the Server
**File**: \`solve/src/lib/mcp-server-registry.ts\`

Add to the \`MCP_SERVER_REGISTRY\` array:
\`\`\`typescript
{
  key: '{{ cookiecutter.project_slug }}',
  urlEnvKey: '{{ cookiecutter.project_slug.upper() }}_URL',  // Must match AWS SSM parameter
  name: '<Display Name>',
  description: '<Description of your MCP server functionality>',
}
\`\`\`

#### 3b. Configure Default Port
**File**: \`solve/src/config/mcp-servers.ts\`

Add to the \`defaultPorts\` object:
\`\`\`typescript
const defaultPorts: Record<string, number> = {
  // ... existing ports ...
  {{ cookiecutter.project_slug }}: {{ cookiecutter.server_port }},
}
\`\`\`

#### 3c. Define URL Endpoints
**File**: \`solve/src/lib/mcp-urls.ts\`

Add to BOTH the development and production URL sections:
\`\`\`typescript
// In development section (around line 15-25):
{{ cookiecutter.project_slug.upper() }}_URL: \`\${baseUrl}:{{ cookiecutter.server_port }}/sse\`,

// In production section (around line 30-40):
{{ cookiecutter.project_slug.upper() }}_URL: \`\${baseUrl}:{{ cookiecutter.server_port }}/sse\`,
\`\`\`

### STEP 4: Kubernetes Configuration

#### 4a. K8s Service Manager
**File**: \`solve/src/lib/k8s-manager.ts\`

Add port mapping in TWO locations:

1. In the service spec ports array (around line 100-115):
\`\`\`typescript
{ name: '{{ cookiecutter.project_slug.replace('_', '-') }}', port: {{ cookiecutter.server_port }}, targetPort: {{ cookiecutter.server_port }} },
\`\`\`

2. In the ingress service ports array (around line 365-375):
\`\`\`typescript
{ name: '{{ cookiecutter.project_slug.replace('_', '-') }}', port: {{ cookiecutter.server_port }}, targetPort: {{ cookiecutter.server_port }} },
\`\`\`

## Port Assignment Reference
Check the current port assignments, if we have a collision. Move to the next 80XX port.

## Pre-Setup Verification

### 1. Verify BUILD.bazel Configuration
Before integrating the server, ensure the BUILD.bazel in your MCP server directory is correctly configured:

#### Python MCP Servers
\`\`\`python
load(\"@rules_python//python:defs.bzl\", \"py_binary\", \"py_library\")

py_binary(
    name = \"{{ cookiecutter.project_slug }}\",  # This is the target name you'll reference
    srcs = [\"{{ cookiecutter.project_slug }}/__main__.py\"],
    imports = [\"{{ cookiecutter.project_slug }}\"],  # Should match your package directory name
    main = \"{{ cookiecutter.project_slug }}/__main__.py\",
    visibility = [\"//visibility:public\"],
    deps = [\":{{ cookiecutter.project_slug }}_lib\"],
)

py_library(
    name = \"{{ cookiecutter.project_slug }}_lib\",
    srcs = glob([\"{{ cookiecutter.project_slug }}/**/*.py\"]),
    imports = [\".\"],
    visibility = [\"//visibility:public\"],
    deps = [
        # List all your dependencies explicitly
        \"@mcp_{{ cookiecutter.project_slug }}//mcp\",
        \"@mcp_{{ cookiecutter.project_slug }}//anyio\",
        # ... other deps
    ],
)
\`\`\`

**Common issues to check:**
- [ ] Target name matches what you'll reference (not the directory name)
- [ ] Imports path is correct (package name for py_binary, \".\" for py_library)
- [ ] Dependencies use the correct hub name (e.g., \`@mcp_{{ cookiecutter.project_slug }}//\`)
- [ ] All required dependencies are listed explicitly

#### Node.js MCP Servers
\`\`\`javascript
# BUILD.bazel for Node.js servers will differ
# Add appropriate configuration here
\`\`\`

## Execution Instructions

### PARALLEL EXECUTION STRATEGY
1. **Read all files first** (in parallel) to understand current state
2. **Execute ALL file edits in parallel** - All modifications can be done simultaneously
3. **Use TodoWrite tool** to track progress across parallel operations

### File Modification Summary
You need to modify exactly these files:
1. \`mcp/usrpod/BUILD.bazel\` - Add server to data dependencies
2. \`mcp/usrpod/run.sh\` - Add launch command
3. \`mcp/usrpod/run-container.sh\` - Add container launch command
4. \`solve/src/lib/mcp-server-registry.ts\` - Register server
5. \`solve/src/config/mcp-servers.ts\` - Configure port
6. \`solve/src/lib/mcp-urls.ts\` - Define URL endpoints
7. \`solve/src/lib/k8s-manager.ts\` - Add K8s port mappings (2 locations)

## Port Selection Helper
\`\`\`bash
# Find the highest port number in use
grep -h \"port [0-9]\" mcp/usrpod/run.sh | grep -o \"[0-9]\\+\" | sort -n | tail -1
# Next available port = highest + 1
\`\`\`

## Testing Verification

### Local Testing
\`\`\`bash
# Test Bazel build first
cd mcp/research/{{ cookiecutter.project_slug }}
bazel build :{{ cookiecutter.project_slug }}

# Verify all files were updated correctly
git diff --name-only | sort
# Should show exactly these 6 files:
# MODULE.bazel
# mcp/usrpod/BUILD.bazel
# mcp/usrpod/run-container.sh
# mcp/usrpod/run.sh
# solve/src/config/mcp-servers.ts
\`\`\`

### Debug Checklist
If build fails:
- [ ] Check target name matches across all files
- [ ] Verify binary name in run scripts matches BUILD.bazel output
- [ ] Ensure all Python dependencies are in requirements.txt
- [ ] Confirm MODULE.bazel hub name matches BUILD.bazel deps references
- [ ] Check imports paths are correct in BUILD.bazel

## Common Pitfalls

1. **Target name mismatch**: The BUILD.bazel target name must match references in usrpod/BUILD.bazel
2. **Binary path confusion**: The binary path in run.sh/run-container.sh must match the actual output from Bazel
3. **Missing MODULE.bazel entry**: Python servers need pip.parse configuration
4. **Wrong imports path**: py_binary should use package name, py_library should use \".\"
5. **Dependency hub mismatch**: Ensure @hub_name// matches between MODULE.bazel and BUILD.bazel

## Quick Reference

| File | What to Add | Key Detail |
|------|------------|------------|
| MODULE.bazel | pip.parse block | Hub name: mcp_{{ cookiecutter.project_slug }} |
| mcp/usrpod/BUILD.bazel | Target reference | //path:{{ cookiecutter.project_slug }} |
| run.sh | Launch command | Binary path from BUILD |
| run-container.sh | Container launch | Add python3 for Python |
| mcp-servers.ts | Frontend config | Port and env var name |
| service.tf | K8s port | Use kebab-case name |

## Example: Complete Parallel Setup

When setting up a new MCP server, execute ALL of these operations in parallel:

\`\`\`bash
# 1. First, detect the server and gather info (parallel reads)
- Read mcp/research/{{ cookiecutter.project_slug }}/BUILD.bazel (get target name)
- Read MODULE.bazel (find insertion point)
- Read mcp/usrpod/run.sh (find highest port)
- Read all other files to understand structure

# 2. Then execute ALL edits simultaneously
- Edit MODULE.bazel (add pip.parse)
- Edit mcp/usrpod/BUILD.bazel (add to both targets)
- Edit mcp/usrpod/run.sh (add launch command)
- Edit mcp/usrpod/run-container.sh (add container launch)
- Edit solve/src/config/mcp-servers.ts (add config)
\`\`\`

This parallel approach reduces setup time from ~5 minutes to ~30 seconds!" --dangerously-skip-permissions
```

## Usage

After running cookiecutter to generate your MCP server:

1. Navigate to the generated project directory
2. Run the command above, which will:
   - Use the port specified in `cookiecutter.json` (default: 3001)
   - Set up all necessary integrations with the SAAGA infrastructure
   - Configure the server with the project slug name

The command uses cookiecutter template variables that will be replaced with actual values when the project is generated.

## Variables Used

- `{{ cookiecutter.project_slug }}`: The server name (e.g., `my_mcp_server`)
- `{{ cookiecutter.server_port }}`: The assigned port number (e.g., `3001`)
- `{{ cookiecutter.project_slug.upper() }}`: The uppercase environment variable prefix (e.g., `MY_MCP_SERVER`)
- `{{ cookiecutter.project_slug.replace('_', '-') }}`: The kebab-case name for K8s (e.g., `my-mcp-server`)