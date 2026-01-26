---
description: MCP server management - when to enable/disable for token optimization
---

# MCP Workflows

## Server Tiers

| Tier | Servers | When to Enable |
|------|---------|----------------|
| **CORE** | pomera | Always (notes, session logs, text tools) |
| **CODING** | text-editor, sequential-thinking | Complex code edits, debugging |
| **RESEARCH** | markdownify | Content conversion |
| **SAFETY** | backup | Before risky operations |

---

## Pre-Session Setup with mcpick

```bash
# Effect: Select only needed servers
# Reduces overhead significantly
```
---

## In-Session Toggle (IDE-dependent)

```bash
# Many IDEs provide a UI/command to toggle MCP servers mid-session.
# If not available, use `npx mcpick` pre-session.
```

---

## Workflow Presets

| Preset | Servers | ~Tokens | Use For |
|--------|---------|---------|---------|
| **Minimal** | pomera | 600 | Simple Q&A, quick edits |
| **Coding** | pomera, text-editor, sequential-thinking | 1300 | Refactoring, debugging |
| **Research** | pomera, markdownify | 1400 | Content conversion |
| **Safety** | pomera, backup | 1000 | Before risky operations |
| **Full** | All servers | 2000+ | Major projects |

---

## backup (MCP-Backup-Server)

Agent-triggered file snapshots before risky operations.

```bash
# Install
git clone https://github.com/hexitex/MCP-Backup-Server
cd MCP-Backup-Server && npm install && npm run build
```

### ⚠️ CRITICAL: Windows Path Configuration

**The MCP backup server MUST use absolute paths.** Relative paths (like `./.code_backups`) cause the server to crash because the MCP server's working directory is unknown and likely not your project folder.

**Symptom of misconfiguration:**
```
Error: invalid character 'C' looking for beginning of value
```
This JSON parsing error occurs when the restore operation encounters Windows paths (starting with `C:\`) while the server expects relative paths.

**Fix: Use absolute paths in MCP config**

Edit your IDE's MCP settings (e.g., `mcp_settings.json` or equivalent):

```json
"backup": {
  "command": "node",
  "args": ["C:/path/to/MCP-Backup-Server/build/index.js"],
  "env": {
    "BACKUP_DIR": "C:/Users/YourUsername/.code_backups",
    "EMERGENCY_BACKUP_DIR": "C:/Users/YourUsername/.code_emergency_backups",
    "MAX_VERSIONS": "50"
  }
}
```

**Key points:**
- Use forward slashes (`/`) in paths, not backslashes
- Create the backup directories before first use
- Replace `YourUsername` with your actual Windows username

### When to trigger backup

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
