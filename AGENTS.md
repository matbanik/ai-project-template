# AGENTS.md

AI guidance for maximizing **work efficiency**. Detailed workflows via `/workflow-name`.

---

## User Rules

### Communication Style
- Always summarize the user's request before acting
- Ask clarifying questions if requirements are ambiguous
- Confirm before making destructive changes (file deletions, major refactors)
- Follow the re-prompting protocol so user has a chance to adjust their request

---

## Critical Rules

1. **Never delete** without user request + pomera backup
2. **Never push** without user confirmation
3. **Backup before** large modifications (>50% of file)
4. **Prefer native tools** over shell when available
5. **Log sessions** to pomera after significant work

---

## Getting Started (New Users)

1. **First prompt**: Just ask your question - AI will guide you
2. **Workflows**: Type `/mcp-workflows` to see MCP tools available
3. **Search**: AI uses web search when helpful (defaults to Tavily)
4. **Backups**: AI will remind you before risky operations
5. **Memory**: Sessions logged to Pomera for continuity

---

## MCP Servers

| Server | Purpose | When to Enable |
|--------|---------|----------------|
| `backup` | File/folder backup with versioning | Risky operations, refactoring |
| `pomera` | Text tools, notes, session memory | Always (default) |
| `text-editor` | Hash-based conflict-detected edits | Complex multi-file edits |
| `sequential-thinking` | Step-by-step problem analysis | Complex planning, debugging |
| `markdownify` | Convert web/docs to markdown | Research, content conversion |

**Toggle servers**: `npx mcpick`

---

## Available Workflows

| Command | Purpose |
|---------|---------|
| `/content-conversion-workflow` | Markdownify, web content extraction |
| `/creative-writing` | Creative writing assistance |
| `/data-analysis` | Data analysis and visualization |
| `/file-organization-workflow` | Git, backups, project structure |
| `/git-workflow` | Git conventions, branching |
| `/keyword-guide` | SEO keyword research |
| `/mcp-workflows` | MCP servers, mcpick, backup tools |
| `/meta-review` | Workflow document review |
| `/pomera-notes-workflow` | Pomera notes for backup/memory |
| `/readme-writing` | GitHub README best practices |
| `/research-project` | Research project workflows |
| `/rule-mapping` | AI rules sync across IDEs |
| `/session-log` | Log prompts/responses to Pomera |
| `/text-workflows` | Text processing, pomera tools |
| `/web-search-workflow` | Engine selection, result logging |
| `/writing-hooks` | Writing hooks and CTAs |

---

## Re-Prompting Protocol

**Before each task, AI processes through this checklist:**

### 1. Summarize & Confirm
Restate request in 1-2 sentences to verify understanding.

### 2. Clarifying Questions
Ask if: scope ambiguous, multiple paths, trade-offs needed, details missing.

### 3. Web Search Consideration
Offer search if: current info needed, best practices, error resolution.

### 4. MCP Tooling Check

| Task Type | Enable | Run |
|-----------|--------|-----|
| Simple Q&A | pomera only | `npx mcpick` |
| Coding | + text-editor, sequential-thinking | |
| Research | + markdownify | |
| Risky ops | + backup server | |

### 5. Backup Reminder
Trigger if: deleting files, refactoring >50%, bulk replace, restructuring.

### 6. Complexity Estimate
- Simple: 1-3 tools
- Medium: 5-15 tools
- Complex: 20+ tools → recommend enabling `sequential-thinking`

### 7. Automatic Prompt Recording
**After significant work, log to Pomera:**
```bash
pomera_notes save --title "Session/{date}/{task-slug}" \
  --input_content "PROMPT: {user request}" \
  --output_content "RESULT: {what was done, outcome}"
```

---

## Quick Commands

```bash
# Web search (saves to file)
python tools/web_search.py "query" -o searches/ -t task-name

# MCP server toggle (pre-session)
npx mcpick

# Validation
python tools/validate.py
```

---

## Project Structure

```
tools/              # Python scripts
.agent/workflows/   # Slash command workflows (16 total)
content-docs/       # User data (raw/, processed/, exports/)
searches/           # Web search results (by date)
```

---

## Automatic Session Logging

**After completing significant work:**
```bash
pomera_notes save \
  --title "Session/{YYYY-MM-DD}/{HH-MM}-{task}" \
  --input_content "USER: {original request}" \
  --output_content "AI: {what done, files changed, outcome}"
```

**After web searches:**
```bash
pomera_notes save \
  --title "Search/{YYYY-MM-DD}/{query-slug}" \
  --input_content "QUERY: {search terms}" \
  --output_content "RESULTS: {key findings}"
```

---

## Workflow Quick Reference

```
┌────────────────────────────────────────────┐
│ 1. SUMMARIZE  2. CLARIFY  3. SEARCH        │
│ 4. MCP-CHECK  5. BACKUP   6. ESTIMATE      │
│ 7. RECORD                                  │
└────────────────────────────────────────────┘
```

*For details: `/mcp-workflows`, `/file-organization-workflow`, etc.*
