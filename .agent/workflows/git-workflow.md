---
description: Git workflow and branch conventions for this project
---

# Git Workflow

## Default Branch

**IMPORTANT: Always use the `main` branch for all commits and pushes.**

## Standard Git Commands

**IMPORTANT: Do NOT commit or push changes to GitHub without explicit user instructions.**

Wait for the user to explicitly say "commit", "push to GitHub", or similar before proceeding with git operations.

When committing and pushing changes:

```bash
# Ensure you're on main branch
git checkout main

# Stage changes
git add <files>

# Commit with conventional commit message
git commit -m "type(scope): description"

# Push to main
git push origin main
```

## Commit Message Convention

Use conventional commits:
- `feat(scope):` - New feature
- `fix(scope):` - Bug fix
- `docs(scope):` - Documentation
- `style(scope):` - Formatting
- `refactor(scope):` - Code restructure
- `chore(scope):` - Maintenance

## Before Major Changes

**Always backup to Pomera before:**
- Deleting files
- Large-scale refactoring (>50% of file)
- Converting between languages
- Restructuring directories

```bash
# Backup before major changes
pomera-mcp --call pomera_notes --args '{
  "action": "save",
  "title": "Backup/{filename}-{date}",
  "input_content": "<file content>",
  "output_content": "Backup before: [reason]"
}'
```

## DO NOT USE

- Do NOT push to `master` branch
- The `master` branch is deprecated and only creates preview deployments
