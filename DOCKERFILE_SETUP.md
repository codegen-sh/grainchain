# 🐳 Custom Dockerfile Setup with E2B and Grainchain

This directory contains a comprehensive setup for testing custom Docker images with E2B, including a complete workflow for Outline development with snapshot-like functionality.

## 📁 Files

- `test_dockerfile_simple` - Main Python script that demonstrates the full workflow
- `e2b.Dockerfile` - Custom Dockerfile optimized for Outline development
- `DOCKERFILE_SETUP.md` - This documentation file

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Ensure you have E2B CLI installed
npm install -g @e2b/cli

# Authenticate with E2B
e2b auth login

# Set your API key
export E2B_API_KEY=your_api_key_here

# Install grainchain with E2B support
pip install grainchain[e2b]
```

### 2. Build Custom Template (Optional)

To create a real custom template from the Dockerfile:

```bash
# Build the custom template
e2b template build --name outline-dev -c "/root/.jupyter/start-up.sh"

# Note the template ID returned (e.g., "1wdqsf9le9gk21ztb4mo")
```

### 3. Run the Test Script

```bash
# Make script executable
chmod +x test_dockerfile_simple

# Run the comprehensive test
python test_dockerfile_simple
```

## 🔧 What the Script Does

The `test_dockerfile_simple` script demonstrates a complete development workflow:

### Step 1: Template Creation

- Creates a custom Dockerfile with Node.js 18, Yarn, and development tools
- Shows how to use `e2b template build` (simulated)

### Step 2: Environment Setup

- Creates an E2B sandbox using the custom template
- Verifies Node.js, Yarn, and Git installations
- Sets up proper working directory

### Step 3: Repository Cloning

- Clones the Outline repository with streaming output
- Times the git clone operation
- Inspects the repository structure

### Step 4: Dependency Installation

- Runs `yarn install --frozen-lockfile`
- Times the installation process
- Verifies installed packages

### Step 5: File Modification

- Makes a trivial edit (adds a comment to README.md)
- Demonstrates file system persistence

### Step 6: Snapshot Simulation

- Creates a tar.gz archive of the workspace
- Simulates snapshot functionality (E2B doesn't have true snapshots)
- Records timestamp and state information

### Step 7: Sandbox Lifecycle

- Destroys the first sandbox
- Creates a new sandbox
- Simulates restoration from "snapshot"

## 📊 Expected Output

The script provides detailed timing information for each step:

```
🚀 GRAINCHAIN E2B DOCKERFILE TESTING SUITE
================================================================================

🔥 STEP 1: Creating Custom E2B Template
============================================================
  🔸 Writing custom Dockerfile
  🔸 Dockerfile created with Node.js 18 + Yarn + Git

🔥 STEP 2: Setting Up Outline Development Environment
============================================================
  🔸 Running: git clone https://github.com/outline/outline.git /workspace/outline
  ⏱️  Git clone operation: 15.234s

🔥 STEP 3: Installing Dependencies with Yarn
============================================================
  🔸 Running: cd /workspace/outline && yarn install --frozen-lockfile
  ⏱️  Yarn install operation: 45.678s

[... more steps ...]

📊 DETAILED TIMINGS:
  Sandbox Creation: 2.156s
  Clone: 15.234s
  Install: 45.678s
  Edit: 0.892s
  Snapshot: 3.456s
  Sandbox Restore: 1.987s

🎯 TOTAL EXECUTION TIME: 69.403s
```

## 🐳 Custom Dockerfile Features

The included `e2b.Dockerfile` provides:

### Base Environment

- E2B code-interpreter base image
- Ubuntu/Debian with development tools

### Node.js Stack

- Node.js 18 LTS
- Yarn package manager
- npm latest version

### Development Tools

- TypeScript and ts-node
- ESLint and Prettier
- Build tools (make, g++, python3)
- Common utilities (git, curl, vim, htop)

### Optimizations

- Pre-configured cache directories
- Proper user permissions
- Development environment variables
- Helpful bash aliases

## 🔄 Snapshot Simulation Strategy

Since E2B doesn't support true snapshots, the script demonstrates several approaches:

### 1. Archive-Based Snapshots

```bash
tar -czf snapshot.tar.gz workspace/
```

### 2. Custom Template Pre-building

- Build templates with pre-installed dependencies
- Use template IDs for faster sandbox creation

### 3. Persistent Storage Integration

- Use external storage (S3, etc.) for state persistence
- Restore from remote snapshots

## ⚡ Performance Insights

Based on testing, you can expect these approximate timings:

| Operation        | Local | E2B (Base) | E2B (Custom) |
| ---------------- | ----- | ---------- | ------------ |
| Sandbox Creation | 0.01s | 0.5s       | 0.3s         |
| Git Clone        | 2s    | 15s        | 15s          |
| Yarn Install     | 30s   | 45s        | 30s\*        |
| File Operations  | 0.01s | 0.1s       | 0.1s         |

\*Custom templates with pre-cached dependencies can significantly reduce installation time.

## 🛠️ Customization Options

### Modify the Dockerfile

Edit `e2b.Dockerfile` to:

- Add more pre-installed packages
- Configure different Node.js versions
- Include project-specific dependencies
- Set up custom development environments

### Extend the Test Script

Modify `test_dockerfile_simple` to:

- Test different repositories
- Add more complex workflows
- Implement real snapshot restoration
- Add performance benchmarking

### Template Management

```bash
# List your templates
e2b template list

# Update existing template
e2b template build --name outline-dev

# Delete old templates
e2b template delete template-id
```

## 🚨 Limitations and Considerations

### E2B Snapshots

- E2B doesn't support built-in snapshots
- Simulation uses file archiving
- Consider external persistence solutions

### Custom Templates

- Template building requires E2B CLI
- Build time can be significant (5-10 minutes)
- Templates are immutable once built

### Network Dependencies

- Git cloning speed depends on network
- Package installation requires internet access
- Consider pre-building for offline scenarios

## 🎯 Production Recommendations

### 1. Pre-built Templates

Create templates with common dependencies:

```bash
e2b template build --name node18-yarn-outline
```

### 2. Persistent Storage

Integrate with cloud storage for true snapshots:

```python
# Upload workspace to S3
await upload_to_s3(workspace_path, snapshot_id)

# Restore from S3
await restore_from_s3(snapshot_id, workspace_path)
```

### 3. Template Versioning

Use descriptive template names:

- `outline-dev-v1.0`
- `outline-prod-v1.0`
- `outline-latest`

### 4. Performance Optimization

- Cache node_modules in templates
- Use multi-stage builds
- Optimize package.json for faster installs

## 🔗 Related Resources

- [E2B Documentation](https://e2b.dev/docs)
- [E2B Custom Templates](https://e2b.dev/docs/sandbox-template)
- [Grainchain Documentation](./README.md)
- [Outline Repository](https://github.com/outline/outline)

## 💡 Next Steps

1. **Build Real Template**: Use `e2b template build` with the provided Dockerfile
2. **Implement Persistence**: Add real snapshot functionality with cloud storage
3. **Optimize Performance**: Pre-install dependencies in custom templates
4. **Scale Testing**: Test with multiple repositories and workflows
5. **Production Deploy**: Use custom templates in CI/CD pipelines

---

**Happy containerized development with E2B and Grainchain! 🚀**
