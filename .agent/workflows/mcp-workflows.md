---
description: MCP server management - when to enable/disable for token optimization
---

# MCP Workflows

## Server Tiers

| Tier | Servers | When to Enable |
|------|---------|----------------|
| **CORE** | pomera | Always (notes, backup, memory) |
| **CODING** | text-editor, sequential-thinking | Complex code edits, debugging |
| **RESEARCH** | markdownify | Content conversion |
| **SAFETY** | MCP-Backup-Server | Before risky operations |

---

## Pre-Session Setup with mcpick

```bash
# Install mcpick (one-time)
npm install -g mcpick

# Run before each session to toggle servers
npx mcpick

# Effect: Select only needed servers
# Reduces overhead significantly
```

**mcpick workflow:**
1. Run `npx mcpick` before starting work
2. Select servers based on task type (see presets below)
3. Start your AI session with optimized context

---

## In-Session Toggle

```bash
# Antigravity / Claude Code
/mcp  # Opens server management menu

# Or use @ menu → MCP Servers → Toggle
# Note: Changes reset on restart
```

---

## Workflow Presets

| Preset | Servers | ~Tokens | Use For |
|--------|---------|---------|---------|
| **Minimal** | pomera | 600 | Simple Q&A, quick edits |
| **Coding** | pomera, text-editor, thinking | 1300 | Refactoring, debugging |
| **Research** | pomera, markdownify | 1400 | Content conversion |
| **Safety** | pomera, backup | 1000 | Before risky operations |
| **Full** | All servers | 2000+ | Major projects |

---

## MCP-Backup-Server

Agent-triggered file snapshots before risky operations.

```bash
# Install
git clone https://github.com/hexitex/MCP-Backup-Server
cd MCP-Backup-Server && npm install && npm run build

# Configuration (in mcp_settings.json)
# BACKUP_DIR: ./.code_backups
# MAX_VERSIONS: 50
```

**When to trigger backup:**
- Before refactoring >50% of a file
- Before bulk find/replace
- Before directory restructuring
- Before any destructive operation

**In prompt:** "Back up src/ folder before refactoring"

---

## Core Tools

### pomera (v1.2.2)

Notes, text processing, persistent memory.

| Tool | Use Case |
|------|----------|
| `pomera_notes` | Save/retrieve notes, backups, session logs |
| `pomera_extract` | Extract patterns (URLs, regex) |
| `pomera_text_stats` | Word count, reading time |
| `pomera_json_xml` | Validate/format JSON/XML |
| `pomera_markdown` | Process markdown |
| `pomera_word_frequency` | Analyze word usage |
| `pomera_list_compare` | Compare lists |

### text-editor

Hash-based conflict detection for safe multi-edit.

| Tool | Use Case |
|------|----------|
| `get_text_file_contents` | Read file with hash |
| `edit_text_file_contents` | Edit with hash verification |

### sequential-thinking

Structured analysis with revision capability.

Use for:
- Multi-step problem analysis
- Architectural planning
- Complex debugging
- Scope discovery

---

## Optional Tools

### markdownify
Convert documents to markdown.
- PDF, DOCX, XLSX, PPTX, images, audio, web pages
- Prompt: "use markdownify" to activate

---

## Per-Prompt Activation

Include in your prompts:
- "use markdownify" → Content conversion
- "use sequential thinking" → Structured analysis
- "back up before changes" → Trigger backup

---

## Token Optimization Tips

1. **Start minimal** - Enable only pomera for simple tasks
2. **Add as needed** - Enable specialized servers mid-session
3. **Use mcpick** - Pre-select servers before sessions
4. **Disable after use** - Turn off research servers when done
