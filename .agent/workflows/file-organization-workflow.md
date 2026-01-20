---
description: File organization, git conventions, and project structure management
---

# File Organization Workflow

## Project Structure

```
tools/              # Python scripts and utilities
.agent/             # AI documentation and workflows
  ├── docs/         # Architecture documentation
  ├── workflows/    # Slash command workflows
  └── context/      # Session state files
content-docs/       # User data for AI processing
  ├── raw/          # Unprocessed imports
  ├── processed/    # Cleaned data
  ├── research/     # Research materials
  └── exports/      # AI-generated outputs
searches/           # Web search result logs (by date)
```

---

## Git Conventions

- Default branch: `main`
- Commit format: `type(scope): description`
- Types: feat, fix, docs, style, refactor, test, chore
- **Never push without user confirmation**
- **Never commit without explicit instruction**

---

## Backup Strategy

### Decision Tree: When to Backup

```
Is the operation risky?
├── Deleting files? → YES, backup
├── Refactoring >50% of file? → YES, backup
├── Bulk find/replace? → YES, backup
├── Changing project structure? → YES, backup
├── Converting between languages? → YES, backup
└── Simple edit <20 lines? → NO, skip backup
```

### Option 1: Pomera Notes (Lightweight)

```bash
pomera_notes save \
  --title "Backup/{filepath}-{date}" \
  --input_content "<entire file content>" \
  --output_content "Reason: {description of upcoming changes}"
```

### Option 2: MCP-Backup-Server (Full)

When enabled, trigger with prompt:
- "Back up src/ folder before refactoring"
- "Create snapshot before bulk replace"

Backups stored in: `./.code_backups/`

### Option 3: Git Snapshot

```bash
git add -A && git commit -m "WIP: pre-refactor snapshot"
# Or create experiment branch
git checkout -b experiment/feature-name
```

### Recovery

```bash
# From Pomera
pomera_notes search --search_term "Backup/*" --limit 20
pomera_notes get --note_id <id>

# From MCP-Backup-Server
# Check ./.code_backups/ folder

# From Git
git log --oneline -10
git checkout <commit-hash> -- path/to/file
```

---

## Context Files (.agent/context/)

| File | Purpose | Update When |
|------|---------|-------------|
| `current-focus.md` | Active work | Start/during/end of session |
| `known-issues.md` | Bugs, limitations | Bug discovered or fixed |
| `recent-changes.md` | Change log | Feature complete, major refactor |

### Session Protocol

**Start of session:**
```bash
cat .agent/context/current-focus.md
pomera_notes search --search_term "Memory/Session/*" --limit 5
```

**End of session:**
```bash
# Update current-focus.md with progress
# Log changes to recent-changes.md
pomera_notes save --title "Memory/Session/{task}-{date}" \
  --input_content "<progress>" --output_content "<next steps>"
```

---

## File Deletion Policy

**NEVER delete without explicit user request.**

When deletion is requested:
1. Read file content first
2. Save to pomera notes with full path and content
3. Only then delete

```bash
# Example
pomera_notes save --title "Deleted/{filepath}-{date}" \
  --input_content "<entire file>" \
  --output_content "Deleted per user request: {reason}"
```

---

## Native vs Shell Tools

| Task | Prefer | Why |
|------|--------|-----|
| Read file | `view_file` (native) | Line numbers, structured |
| Create/edit file | `write_to_file` (native) | Creates dirs, encoding |
| Find files | `find_by_name` (native) | Fast, fd-based |
| Search content | `grep_search` (native) | Ripgrep-based |
| Git operations | `run_command` (shell) | Only option |
| Install deps | `run_command` (shell) | Only option |
| Complex multi-edit | `mcp_text-editor` | Hash verification |
