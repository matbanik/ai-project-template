# Secret Scanning & Pre-commit Hooks Setup Guide

> **Purpose:** This document describes the implementation of automated secret scanning and code quality checks using Gitleaks and pre-commit hooks. Use this as a template for setting up similar protection on other projects.

## Overview

This project implements a multi-layer approach to prevent accidental credential commits:

1. **`.gitignore`** - First line of defense: prevents sensitive files from being tracked
2. **Pre-commit hooks** - Second line of defense: scans staged changes before commit
3. **Gitleaks** - Secret detection engine with 100+ built-in patterns
4. **Custom rules** - Project-specific patterns in `.gitleaks.toml`

## Quick Start (Automated Setup)

Run the appropriate script from the project root:

```bash
# Linux / macOS
chmod +x tools/setup-hooks.sh
./tools/setup-hooks.sh
```

```powershell
# Windows (PowerShell)
.\tools\setup-hooks.ps1
```

These scripts will:
1. Detect your OS and package manager
2. Install Gitleaks (if not present)
3. Install pre-commit (if not present)
4. Run `pre-commit install` to activate hooks
5. Run an initial scan of all files

---

## What's Installed

### Files Created

| File | Purpose |
|------|---------|
| `.pre-commit-config.yaml` | Pre-commit hook configuration |
| `.gitleaks.toml` | Custom Gitleaks rules and allowlist |

### System Dependencies

| Tool | Install Command | Purpose |
|------|-----------------|---------|
| `gitleaks` | `brew install gitleaks` | Secret detection engine |
| `pre-commit` | `brew install pre-commit` | Git hook framework |

## How It Works

### On Every Commit

When you run `git commit`, the pre-commit hook automatically:

1. **🔐 Scans for secrets** - Gitleaks checks staged files for API keys, passwords, tokens
2. **🐘 Checks file sizes** - Blocks files >5MB (prevents large binaries)
3. **✅ Validates JSON/YAML** - Catches syntax errors before commit
4. **📄 Fixes end of file** - Ensures files end with newline
5. **✂️ Trims whitespace** - Removes trailing whitespace
6. **🔑 Detects private keys** - Catches SSH/PGP keys

### If Secrets Are Found

The commit is **blocked** and you'll see output like:

```
🔐 Detect secrets with Gitleaks..........................................Failed

Finding:     "api_key": "sk-abc123..."
Secret:      sk-abc123...
RuleID:      generic-api-key
File:        config.json
Line:        15
```

**To fix:**
1. Remove the secret from the file
2. Use environment variables or a gitignored config file instead
3. Re-stage and commit

## Setup Instructions (Template)

### Step 1: Install Dependencies

#### macOS (Homebrew)
```bash
brew install gitleaks pre-commit
```

#### Ubuntu/Debian (Linux)
```bash
# Pre-commit
pip install pre-commit

# Gitleaks - download binary from GitHub releases
wget https://github.com/gitleaks/gitleaks/releases/download/v8.21.2/gitleaks_8.21.2_linux_x64.tar.gz
tar -xzf gitleaks_8.21.2_linux_x64.tar.gz
sudo mv gitleaks /usr/local/bin/
```

#### Windows

**Option 1: Winget (Recommended)**
```powershell
winget install Gitleaks.Gitleaks
pip install pre-commit
```

**Option 2: Chocolatey**
```powershell
choco install gitleaks
pip install pre-commit
```

**Option 3: Scoop**
```powershell
scoop install gitleaks
pip install pre-commit
```

**Option 4: Manual Download**
1. Download `gitleaks_X.X.X_windows_x64.zip` from [Gitleaks Releases](https://github.com/gitleaks/gitleaks/releases)
2. Extract and add to PATH
3. Install pre-commit: `pip install pre-commit`

**Verify Installation (All Platforms)**
```bash
gitleaks version
pre-commit --version
```

### Step 2: Create Pre-commit Config

Create `.pre-commit-config.yaml` in project root:

```yaml
# Pre-commit hooks for secret scanning and code quality
# Install: pip install pre-commit && pre-commit install
# Run manually: pre-commit run --all-files

repos:
  # Gitleaks - Secret Detection
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.2  # Check for latest version
    hooks:
      - id: gitleaks
        name: 🔐 Detect secrets with Gitleaks
        description: Prevents committing secrets and credentials

  # Additional useful hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0  # Check for latest version
    hooks:
      - id: check-added-large-files
        args: ['--maxkb=5000']
        name: 🐘 Check for large files
      - id: check-json
        name: ✅ Validate JSON
      - id: check-yaml
        name: ✅ Validate YAML
      - id: end-of-file-fixer
        name: 📄 Fix end of file
      - id: trailing-whitespace
        name: ✂️ Trim trailing whitespace
      - id: detect-private-key
        name: 🔑 Detect private keys
```

### Step 3: Create Gitleaks Config (Optional)

Create `.gitleaks.toml` for custom rules:

```toml
# Gitleaks Configuration
title = "Project Gitleaks Configuration"

# Use default rules
[extend]
useDefault = true

# Files to allow (reduce false positives)
[allowlist]
description = "Allowlisted files and patterns"
paths = [
    '''\.gitleaks\.toml$''',
    '''\.pre-commit-config\.yaml$''',
    '''\.gitignore$''',
    '''package-lock\.json$''',
    '''\.md$''',
]

# Add custom rules for project-specific patterns
[[rules]]
id = "custom-api-key"
description = "Custom API key pattern"
regex = '''(?i)(my_app_key)\s*[:=]\s*['"]?([a-zA-Z0-9_-]{16,})['"]?'''
tags = ["custom"]
```

### Step 4: Install Hooks

```bash
cd your-project
pre-commit install
```

### Step 5: Initial Scan

```bash
# Scan all files (may auto-fix some issues)
pre-commit run --all-files

# Or scan just staged files
pre-commit run
```

### Step 6: Update .gitignore

Ensure sensitive files are ignored:

```gitignore
# API Keys & Credentials
api-keys.json
*.local.json
.env
.env.*
!.env.example

# OAuth & Authentication
*.pickle
**/token.pickle
**/credentials.json
**/*_secrets.json
**/client_secret*.json
```

## Manual Scanning Commands

```bash
# Scan current directory (all files, ignoring git)
gitleaks detect --source . --no-git -v

# Scan git history
gitleaks detect --source . -v

# Scan specific file
gitleaks detect --source ./config.json

# Generate report
gitleaks detect --source . --report-format json --report-path gitleaks-report.json
```

## What Gets Detected

Gitleaks detects 100+ secret types including:

| Category | Examples |
|----------|----------|
| **Cloud** | AWS keys, GCP keys, Azure secrets |
| **APIs** | Stripe, Twilio, SendGrid, Slack tokens |
| **Auth** | JWT secrets, OAuth tokens, API keys |
| **Databases** | Connection strings, passwords |
| **Private Keys** | SSH, PGP, RSA keys |
| **Generic** | High-entropy strings, password assignments |

## Troubleshooting

### False Positives

If Gitleaks flags something that isn't a secret:

1. **Add to allowlist** in `.gitleaks.toml`:
   ```toml
   [allowlist]
   paths = ['''path/to/file\.txt$''']
   ```

2. **Inline comment** (if supported):
   ```python
   API_KEY = "not-a-real-key"  # gitleaks:allow
   ```

### Bypass for Emergency

**⚠️ Use sparingly - only when you're certain no secrets are staged:**

```bash
git commit --no-verify -m "your message"
```

### Re-run After Failure

After fixing the issue:

```bash
git add .
pre-commit run --all-files
git commit -m "your message"
```

## Best Practices

1. **Never commit secrets** - Use environment variables or secret managers
2. **Use `.env.example`** - Template file with dummy values for documentation
3. **Rotate exposed keys** - If a key was ever committed, consider it compromised
4. **Regular scans** - Run `gitleaks detect` periodically on full history
5. **Keep tools updated** - Check for new Gitleaks/pre-commit versions

## Recovery: Removing Secrets from Git History

If secrets were accidentally committed:

```bash
# 0. FIRST: Backup the sensitive file to Pomera
pomera-mcp --call pomera_notes --args '{
  "action": "save",
  "title": "Backup/secret-file-before-removal-{date}",
  "input_content": "<file content>",
  "output_content": "Backup before removing from git history"
}'

# 1. Stash current changes
git stash --include-untracked

# 2. Remove file from all history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/secret-file.json' \
  --prune-empty --tag-name-filter cat -- --all

# 3. Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. Force push (rewrites remote history)
git push origin main --force

# 5. Restore stash
git stash pop

# 6. Verify file is in .gitignore
echo "path/to/secret-file.json" >> .gitignore
```

**Important:** After force-pushing, all collaborators must re-clone the repository.

---

## Implementation Details (This Project)

**Date Implemented:** 2026-01-16

**What Was Done:**
1. Removed `api-keys.json` from git history using `git filter-branch`
2. Force-pushed to GitHub to remove credentials from remote
3. Installed Gitleaks v8.21.2 and pre-commit v5.0.0
4. Created `.pre-commit-config.yaml` with 7 hooks
5. Created `.gitleaks.toml` with custom Olaplex patterns
6. Verified `api-keys.json` is in `.gitignore`
7. Ran initial scan - all hooks passed
8. Updated Pomera to v1.2.1 (supports `--call` CLI mode)
