---
description: How to sync AI rules across different IDEs and plugins
---

# Rule Mapping Workflow

> **AI-GUIDANCE**: Use this workflow to synchronize `.agent/` content and `AGENTS.md` to native rule formats for different IDEs.

---

## Overview

Different AI-powered IDEs and plugins use different file conventions for project-specific instructions. This workflow documents each format and provides a sync strategy.

---

## IDE Rule File Reference

### Quick Reference Table

| IDE/Plugin | Rule File Location | Format | Scope |
|------------|-------------------|--------|-------|
| **Cursor** | `.cursor/rules/*.mdc` | Markdown | Project |
| **Cursor (legacy)** | `.cursorrules` | Markdown | Project |
| **Windsurf** | `.windsurf/rules/*.md` | Markdown | Project |
| **Cline (VS Code)** | `.clinerules/` or `.clinerules` | Markdown | Project |
| **Claude Code** | `CLAUDE.md` or `.claude/CLAUDE.md` | Markdown | Project |
| **GitHub Copilot** | `.github/copilot-instructions.md` | Markdown | Project |
| **IntelliJ IDEA** | `.aiassistant/rules/*.md` | Markdown | Project |
| **Zed** | `.rules` | Markdown | Project |
| **Warp** | `WARP.md` | Markdown | Project |
| **Kiro (AWS)** | `.kiro/steering/*.md` | Markdown | Project |
| **Trae (ByteDance)** | `project_rules.md` | Markdown | Project |
| **Void** | `.voidrules` | Markdown | Project |
| **Gemini Code Assist** | `GEMINI.md` | Markdown | Project |
| **Antigravity** | Uses Claude Code conventions | Markdown | Project |

---

## Detailed IDE Documentation

### Cursor

**Modern Approach (v0.40+):**
```
.cursor/
└── rules/
    ├── coding-standards.mdc
    ├── testing-patterns.mdc
    └── project-context.mdc
```

**Legacy Approach:**
```
.cursorrules          # Single file in project root
```

**Notes:**
- `.mdc` files can include YAML frontmatter for metadata
- Rules directory is version-controlled
- Global rules configured in Cursor Settings > Rules

---

### Windsurf (Codeium)

```
.windsurf/
├── rules/
│   ├── coding-style.md
│   └── architecture.md
└── workflows/
    └── custom-workflow.md
```

**Notes:**
- Previously used `.windsurfrules` (deprecated)
- Global rules in `global_rules.md`
- Supports conditional rule inclusion

---

### Cline (VS Code Extension)

**Directory Approach:**
```
.clinerules/
├── general.md
├── testing.md
└── security.md
```

**Single File Approach:**
```
.clinerules           # Single file in project root
```

**Global Rules Location:**
- Windows: `Documents\Cline\Rules`
- macOS: `~/Documents/Cline/Rules`
- Linux: `~/Documents/Cline/Rules`

---

### Claude Code

```
CLAUDE.md             # Project root (recommended)
# OR
.claude/
├── CLAUDE.md         # Project instructions
├── settings.json     # Permissions and config
└── agents/           # Subagent definitions
    └── specialist.md
```

**Notes:**
- `CLAUDE.md` is automatically read by Claude Code
- Keep concise; use progressive disclosure linking to other docs
- `.claude/settings.json` manages permissions

---

### GitHub Copilot

```
.github/
└── copilot-instructions.md
```

**Notes:**
- Requires VS Code setting: `github.copilot.chat.codeGeneration.useInstructionFiles`
- Primarily affects Copilot Chat, not inline autocomplete
- Can also use `.instructions.md` for path-specific rules

---

### IntelliJ IDEA AI Assistant

```
.aiassistant/
└── rules/
    ├── guidelines.md
    └── testing.md
```

**Notes:**
- Configure via Settings > Tools > AI Assistant > Rules
- Rules can be: Always, Manual, By Model Decision, or By File Patterns
- Also supports Prompt Library for action-specific prompts

---

### Zed

```
.rules                # Project root (primary)
.cursorrules          # Also supported for compatibility
AGENT.md              # Also supported
```

**Configuration:**
- User settings: `~/.config/zed/settings.json` (Linux) or equivalent
- Project settings: `.zed/settings.json`
- Rules Library accessible via IDE

---

### Warp Terminal

```
WARP.md               # Project root
```

**Also Reads (for compatibility):**
- `CLAUDE.md`
- `AGENTS.md`
- `AGENT.md`
- `.cursorrules`
- `.windsurfrules`
- `.clinerules`
- `.github/copilot-instructions.md`
- `GEMINI.md`

**Notes:**
- Generate with `/init` command in Auto or Agent mode
- Access rules via Settings > AI > Knowledge > Manage Rules

---

### Kiro (AWS)

```
.kiro/
└── steering/
    ├── product.md      # App features
    ├── structure.md    # Codebase organization
    ├── tech.md         # Technology stack
    └── custom.md       # Your additions
```

**Notes:**
- Steering files are auto-generated on project setup
- Can be Always, Conditional, or Manual inclusion
- Also supports hooks for automated workflows

---

### Trae (ByteDance)

```
project_rules.md      # Project root
```

**User-Level Rules:**
```
user_rules.md         # Applies to all projects
```

**Notes:**
- Access via Settings icon in AI dialog
- Supports natural language or Markdown format
- Available in IDE and SOLO modes

---

### Void

```
.voidrules            # Project root
```

**Notes:**
- VS Code fork with open-source AI integration
- Directory-based rules planned for future versions
- Supports connecting to custom LLM providers

---

### Gemini Code Assist

```
GEMINI.md             # Project root
# OR
~/.gemini/GEMINI.md   # Global config
```

**For GitHub Integration:**
```
.gemini/
└── styleguide.md
```

**Notes:**
- Project files override global files
- Supports `<PROTOCOL>` blocks for gated execution
- Can link to `.gemini-guidelines/` for stack-specific guides

---

## Sync Strategy

### Source of Truth

This template uses:
1. **`AGENTS.md`** — Primary AI guidance document
2. **`.agent/workflows/`** — Reusable workflow patterns
3. **`.agent/docs/`** — Architecture documentation

### Manual Sync

For quick one-off syncs:

```bash
# Copy AGENTS.md content to specific IDE format
cp AGENTS.md CLAUDE.md
cp AGENTS.md .cursorrules
cp AGENTS.md WARP.md
```

### Automated Sync Script

See `tools/sync_rules.py` for automated synchronization:

```bash
# Detect IDEs and sync to all
python tools/sync_rules.py

# Preview changes without applying
python tools/sync_rules.py --dry-run

# Target specific IDE
python tools/sync_rules.py --ide cursor

# List detected IDEs
python tools/sync_rules.py --list
```

---

## Best Practices

### Content Guidelines

1. **Keep rules concise** — Most IDEs work best with focused instructions
2. **Use progressive disclosure** — Link to detailed docs instead of inlining everything
3. **Test after syncing** — Verify AI behavior in each IDE
4. **Version control rules** — Commit rule files alongside code

### What to Include

| Include | Skip |
|---------|------|
| Coding conventions | Implementation details |
| Technology stack | API keys or secrets |
| Testing patterns | User-specific preferences |
| Project structure | Temporary workarounds |
| Common commands | Deprecated patterns |

### Cross-IDE Compatibility

Some IDEs read multiple file formats. To maximize compatibility:

```bash
# Create symlinks (Unix/macOS)
ln -s AGENTS.md CLAUDE.md
ln -s AGENTS.md .cursorrules
ln -s AGENTS.md WARP.md

# Or use sync script to maintain copies
python tools/sync_rules.py --keep-synced
```

---

## Troubleshooting

### Rules Not Loading

1. Check file location matches IDE expectations
2. Verify file permissions (readable)
3. Restart IDE or reload workspace
4. Check IDE-specific settings for rule enablement

### Conflicting Rules

If same rule file exists in multiple locations:
- Most IDEs prefer project-level over global
- Closer to working directory wins
- Check IDE documentation for precedence

### Large Rule Files

If rules exceed context limits:
- Split into multiple focused files
- Use conditional inclusion where supported
- Link to external documentation

---

## Quick Commands

```bash
# Check which IDEs are configured in current project
ls -la .cursor* .windsurf* .clinerules* CLAUDE.md WARP.md .kiro* .voidrules GEMINI.md 2>/dev/null

# Count lines in all rule files
wc -l .cursorrules CLAUDE.md AGENTS.md 2>/dev/null

# Find all markdown rule files
find . -name "*.md" -path "*rules*" -o -name "*rules*" -type f 2>/dev/null
```
