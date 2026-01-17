# AGENTS.md

AI-specific guidance for working with this codebase. This file contains conventions, commands, and patterns that help AI coding assistants work effectively.

## Quick Commands

```bash
# Web search
python tools/web_search.py "query"                    # Default: Brave
python tools/web_search.py "query" --engine google    # Google
python tools/web_search.py "query" --engine context7  # Code docs
```

## Project Structure

```
tools/              # Python scripts and utilities
.agent/             # AI documentation and workflows (see below)
content-docs/       # User data for AI processing (see below)
```

### content-docs/ (User Data)

**Primary folder for all user-provided data** that AI will process:

| Subfolder | Purpose |
|-----------|---------|
| `raw/` | Unprocessed imports (CSVs, exports, dumps) |
| `processed/` | Cleaned/transformed data ready for analysis |
| `research/` | Research materials, articles, references |
| `exports/` | AI-generated outputs, reports, summaries |

**Usage:**
- Place any data files here before asking AI to process them
- AI should read from this folder, not modify source files
- Processed outputs go to `exports/` or dedicated subfolders
- Large files: Consider importing to SQLite instead of direct processing

**Example structure:**
```
content-docs/
├── raw/
│   ├── sales-2024.csv
│   └── customer-feedback.json
├── processed/
│   └── sales-cleaned.csv
├── research/
│   ├── competitor-analysis/
│   └── market-trends/
└── exports/
    └── quarterly-report.md
```

## .agent/ Folder (AI Resources)

### Documentation (`.agent/docs/`)

| File | Purpose |
|------|---------|
| `project-architecture.md` | System design and data flow |

### Workflows (`.agent/workflows/`)

Invoke with slash commands in AI assistants:

| Workflow | Use Case |
|----------|----------|
| `/git-workflow` | Git conventions and branching |
| `/data-analysis` | Data processing with SQLite and pandas |
| `/creative-writing` | Writing projects: blogs, stories, articles |
| `/research-project` | Research and knowledge synthesis |

### Context (`.agent/context/`)

| File | Purpose |
|------|---------|
| `current-focus.md` | Active work items and priorities |
| `known-issues.md` | Tracked bugs and limitations |
| `recent-changes.md` | Recent modifications log |

## Context File Management

The `.agent/context/` files provide lightweight, version-controlled session state. Use these files in addition to `pomera_notes` for information that should be visible in the repository.

### When to Update Each File

#### `current-focus.md` - Session State

**Update at session START:**
- Read file to understand current state
- Update "Session Goals" with what you'll work on
- Review any blockers from previous sessions

**Update DURING session:**
- Check off completed tasks
- Add new tasks discovered during work
- Document blockers immediately when encountered

**Update at session END:**
- Mark completed work
- Set context for next session (what's next, what to remember)

#### `known-issues.md` - Bug & Limitation Tracking

**Add an issue when:**
- Bug discovered during development
- Unexpected behavior that needs investigation
- Design limitation identified that affects work
- External dependency causing problems
- Workaround implemented (document the workaround)

**Resolve an issue when:**
- Bug is confirmed fixed
- Move to "Resolved" section with solution notes
- Include date and brief description of fix

#### `recent-changes.md` - Change Log

**Log a change after:**
- Completing a feature or significant fix
- Major refactoring (even if not complete)
- Configuration changes that affect behavior
- Dependency updates
- Architectural decisions implemented

**Do NOT log:**
- Minor typo fixes
- Formatting-only changes
- Work-in-progress that will be revised

### Context Files vs pomera_notes

| Use Context Files For | Use pomera_notes For |
|-----------------------|----------------------|
| Current state (what's happening now) | Historical state (what happened before) |
| Visible in repo (team awareness) | Private memory (personal context) |
| Brief, actionable items | Detailed content, code snapshots |
| Rolling window (recent only) | Long-term archive |

### Session Protocol

**Starting a session:**
```bash
# 1. Read context files
cat .agent/context/current-focus.md
cat .agent/context/known-issues.md

# 2. Check pomera for detailed context
pomera_notes search --search_term "Memory/Session/*" --limit 5

# 3. Update current-focus.md with session goals
```

**Ending a session:**
```bash
# 1. Update current-focus.md with progress
# 2. Log significant changes to recent-changes.md
# 3. Add any new issues to known-issues.md
# 4. Save detailed context to pomera_notes
pomera_notes save --title "Memory/Session/{task}-{date}" \
  --input_content "<detailed progress and context>"
```

## MCP Servers & Tools

### Active MCP Servers

Three MCP servers provide specialized capabilities:

#### 1. Pomera Server (22 Text Tools)
Comprehensive text processing, data manipulation, and note-taking.

Install: `npm install -g pomera-ai-commander`

#### 2. Text-Editor Server (2 Advanced Editing Tools)
Hash-based conflict detection and precise line-range editing.

Install: `pip install uv`

#### 3. Sequential Thinking Server (1 Advanced Analysis Tool)
Structured, step-by-step problem-solving with revision capabilities.

Install: `npm install -g @modelcontextprotocol/server-sequential-thinking`

### MCP Tools Usage Guide

#### For Code Modifications

| Tool | Use Case | Example |
|------|----------|---------|
| **pomera_notes** | Save original code before major refactoring | Store function/component before changes for rollback |
| **pomera_extract** | Extract patterns from codebase | Find all API endpoints, function names, imports |
| **pomera_json_xml** | Validate/prettify config files | Format package.json, tsconfig.json |
| **pomera_string_escape** | Generate escaped strings | Create JSON/SQL strings, escape HTML entities |
| **pomera_line_tools** | Clean up code formatting | Remove duplicate imports, empty lines |
| **pomera_whitespace** | Normalize code indentation | Convert tabs to spaces, trim whitespace |
| **pomera_column_tools** | Process CSV/TSV data | Extract columns from data files |
| **text-editor tools** | Complex multi-range edits | Edit multiple sections with conflict detection |

**Code Modification Workflow:**
```bash
# 1. Save original version to notes before major changes
pomera_notes save --title "Code/{Component}-Original-{date}" --input_content "<original code>"

# 2. Extract patterns to understand codebase
pomera_extract --text "<file>" --type regex --pattern "function \w+\("

# 3. Use text-editor for precise edits with hash verification
get_text_file_contents → edit_text_file_contents (with hashes)

# 4. Validate JSON/config changes
pomera_json_xml --operation json_validate --text "<config>"

# 5. Retrieve original if needed
pomera_notes get --note_id <id>
```

#### For Research & Writing

| Tool | Use Case | Example |
|------|----------|---------|
| **pomera_notes** | Save research snippets, draft versions | Store quotes, sources, draft paragraphs |
| **pomera_text_stats** | Analyze content length, reading time | Get word count, reading time estimate |
| **pomera_markdown** | Process markdown content | Extract links, headers, convert tables |
| **pomera_extract** | Extract URLs, emails from sources | Gather research links, contact info |
| **pomera_url_parse** | Analyze reference URLs | Parse and validate source links |
| **pomera_word_frequency** | Analyze writing patterns | Check keyword density, overused words |
| **pomera_list_compare** | Compare research lists | Find unique sources, common themes |
| **pomera_html** | Extract content from web pages | Get text from HTML research sources |
| **pomera_text_wrap** | Format text for readability | Wrap paragraphs to specific width |
| **pomera_sort** | Organize research notes | Sort alphabetically, remove duplicates |
| **pomera_generators** | Generate content elements | Create slugs, UUIDs for posts |

**Research & Writing Workflow:**
```bash
# 1. Save research snippets as notes
pomera_notes save --title "Research/{Topic}/Sources-{date}" --input_content "<links>"

# 2. Extract URLs from research materials
pomera_extract --text "<content>" --type urls

# 3. Get text statistics
pomera_text_stats --text "<draft>" --words_per_minute 200

# 4. Compare versions
pomera_notes search --search_term "Draft*"
pomera_list_compare --list_a "<v1>" --list_b "<v2>"

# 5. Analyze word frequency (avoid repetition)
pomera_word_frequency --text "<text>"
```

#### Notes as Free-Form Version Control

**Strategy:** Use `pomera_notes` as a lightweight versioning system for tracking text changes, drafts, and experimental code.

**When to Save Notes:**
- Before major code refactoring
- When testing different approaches
- Saving valuable research snippets
- Storing intermediate draft versions
- Preserving code that might be needed later

**Note Organization:**
```bash
# Save with descriptive titles using naming conventions
pomera_notes save --title "Code/{Component}/Original-{date}" --input_content "<code>"
pomera_notes save --title "Writing/{Project}/Draft-v1-{date}" --input_content "<draft>"
pomera_notes save --title "Research/{Topic}/Sources-{date}" --input_content "<urls>"

# Search with FTS5 wildcards
pomera_notes search --search_term "Code/*" --limit 10
pomera_notes search --search_term "*Draft*" --limit 20

# List recent notes
pomera_notes list --limit 20
```

**Naming Conventions:**
- `Code/{Component}/{Description}-{Date}` - Code snapshots
- `Writing/{Project}/{Type}-{Date}` - Writing drafts
- `Research/{Topic}/{Description}-{Date}` - Research notes
- `Memory/{Type}/{Topic}-{Date}` - Session memory

#### Persistent Memory Management

**Strategy:** Use `pomera_notes` as a persistent memory layer to maintain context across sessions.

**Common Problems Addressed:**
- Context window degradation during long sessions
- Cross-session amnesia requiring complete re-explanation
- Lost architectural decisions and rationale
- Wasted time re-establishing project context

**Memory Types to Maintain:**

| Type | What to Store | Example Title |
|------|---------------|---------------|
| **Session State** | Current task progress, blockers, next steps | `Memory/Session/{Task}-{date}` |
| **Decisions Log** | Architecture choices, rejected approaches | `Memory/Decisions/{topic}` |
| **Code Snapshots** | Original versions before refactoring | `Memory/Code/{component}-original` |
| **Research Findings** | Useful links, API discoveries | `Memory/Research/{topic}` |
| **Project Context** | Conventions, patterns, common pitfalls | `Memory/Context/project-conventions` |

**Session Startup Protocol:**
```bash
# 1. Check for recent session state
pomera_notes search --search_term "Memory/Session/*" --limit 5

# 2. Load project conventions
pomera_notes search --search_term "Memory/Context/*"

# 3. Review recent decisions
pomera_notes search --search_term "Memory/Decisions/*" --limit 10
```

**Session Shutdown Protocol:**
```bash
# 1. Save current progress
pomera_notes save --title "Memory/Session/{Task}-{date}" \
  --input_content "<what was accomplished>" \
  --output_content "<next steps and blockers>"

# 2. Document any decisions made
pomera_notes save --title "Memory/Decisions/{Decision}-{date}" \
  --input_content "<options considered>" \
  --output_content "<chosen approach and rationale>"
```

#### For Complex Analysis & Problem-Solving

| Tool | Use Case | Example |
|------|----------|---------|
| **sequentialthinking** | Multi-step problem analysis | Architectural planning, debugging complex issues |

**When to Use Sequential Thinking:**
- Planning complex features or refactoring
- Analyzing architectural decisions
- Breaking down multi-step implementation tasks
- Problems where scope isn't clear initially
- Analysis that might need course correction

**Example Analysis Workflow:**
```bash
# 1. Start with initial problem assessment
sequentialthinking --thought "Analyzing problem..."
  --thoughtNumber 1 --totalThoughts 5 --nextThoughtNeeded true

# 2. Revise if understanding changes
  --isRevision true --revisesThought 2

# 3. Adjust total thoughts if needed
  --totalThoughts 6 --needsMoreThoughts true

# 4. Continue until solution is reached
  --nextThoughtNeeded false  # Final thought
```

### Web Search

Search the web using Brave Search, Google Custom Search, or Context7:

```bash
# Basic search (defaults to Brave)
python tools/web_search.py "your search query"

# Specify engine
python tools/web_search.py "your query" --engine brave
python tools/web_search.py "your query" --engine google
python tools/web_search.py "pandas dataframe tutorial" --engine context7

# Request more results
python tools/web_search.py "your query" --count 10

# Get JSON output
python tools/web_search.py "your query" --json
```

**Engine Selection Strategy:**

| Use Brave When | Use Google When | Use Context7 When |
|----------------|-----------------|-------------------|
| Basic, short queries | Brave fails (no results) | Searching for code examples |
| Non-critical research | Complex/specific queries | Library/framework documentation |
| General information | Commercial intent queries | API usage patterns |
| Initial exploration | Long-tail queries | Programming how-to |

**Cost Considerations:**
- **Brave:** 2000 free queries/month — use as default
- **Google:** 100 free queries/day — reserve for complex queries
- **Context7:** Specialized for code/library documentation

## Critical Rules

### File Deletion Policy

**NEVER delete files unless explicitly stated by the user.** When file deletion is explicitly requested:

1. **Before deleting**: Save the entire file content to pomera notes:
   ```bash
   pomera-mcp --call pomera_notes --args '{"action": "save", "title": "Deleted/{filepath}-{date}", "input_content": "<entire file content>"}'
   ```

2. **Include in the note**:
   - Full file path
   - Complete file content (not truncated)
   - Reason for deletion
   - Date of deletion

3. **Example workflow**:
   ```bash
   # 1. Read the file first
   cat path/to/file.md

   # 2. Save to pomera notes before deletion
   pomera-mcp --call pomera_notes --args '{
     "action": "save",
     "title": "Deleted/path/to/file.md-2026-01-16",
     "input_content": "<complete file content>",
     "output_content": "Deleted per user request: [reason]"
   }'

   # 3. Only then delete the file
   rm path/to/file.md
   ```

### Large-Scale Modifications Policy

**Before making large-scale modifications**, back up the original content:

**What counts as large-scale:**
- Refactoring >50% of a file
- Replacing entire functions/classes
- Converting between languages (shell → Python)
- Restructuring project directories
- Bulk find/replace operations

**Backup workflow:**
```bash
# Save original before major refactoring
pomera-mcp --call pomera_notes --args '{
  "action": "save",
  "title": "Backup/{component}-original-{date}",
  "input_content": "<original code>",
  "output_content": "Backup before: [description of changes]"
}'
```

**Recovery:**
```bash
# List recent backups
pomera-mcp --call pomera_notes --args '{"action": "list", "limit": 20}'

# Get specific backup
pomera-mcp --call pomera_notes --args '{"action": "get", "note_id": <id>}'
```

### Git Conventions

- Default branch: `main`
- Use conventional commits: `type(scope): description`
- Wait for explicit user instruction before commits/pushes
- Never push without user confirmation

## Validation

Always run validation before committing:
```bash
# Run project-specific validation if available
python tools/validate.py
```
