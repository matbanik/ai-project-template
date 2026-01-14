# How To Set Up This Template

> Everything you need to get your AI-powered development environment running smoothly.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Environment Setup](#environment-setup)
- [MCP Servers & Tools](#mcp-servers--tools)
- [Web Search Integration](#web-search-integration)
- [SQLite for AI Context](#sqlite-for-ai-context)
- [Workflow Templates](#workflow-templates)
- [Project Structure](#project-structure)
- [Security Notes](#security-notes)

---

## Quick Start

> ⚠️ **First Two Steps Are Critical!** If you skip syncing rules and setting up MCP servers, your AI assistant won't know about any of the cool stuff in this template. It's like hiring an expert consultant but forgetting to give them the project brief.

```bash
# 1. Clone and enter template
git clone <your-repo-url>
cd ai-project-template

# 2. Set up Python environment
conda create -n ai-project python=3.11
conda activate ai-project
pip install -r requirements.txt

# 3. ⭐ SYNC AI RULES TO YOUR IDE ⭐
python tools/sync_rules.py --ide cline     # For VS Code + Cline
python tools/sync_rules.py --ide cursor    # For Cursor
python tools/sync_rules.py --all           # For all supported IDEs

# 4. ⭐ SET UP MCP SERVERS ⭐
python tools/setup_mcp.py                  # Auto-detect IDE and get instructions
python tools/setup_mcp.py --check          # Verify MCP tools are installed

# 5. Configure API keys
cp api-keys.json api-keys.local.json  # Edit with your keys
# Add api-keys.local.json to .gitignore

# 6. Test web search
python tools/web_search.py "test query"
```

---

## ⭐ Step 1: Sync AI Rules (Don't Skip This!)

Your AI assistant needs to read project-specific rules to work effectively. The `AGENTS.md` file contains all the conventions, but your IDE needs it in its native format.

### Why Sync Rules?

Without syncing:
- ❌ AI doesn't know your project structure
- ❌ AI forgets your preferences every session
- ❌ AI doesn't know about MCP tools available to it

After syncing:
- ✅ AI reads rules automatically when you open the project
- ✅ AI knows about `pomera_notes`, `web_search.py`, and workflows
- ✅ AI follows your coding conventions

### How to Sync

```bash
# List all supported IDEs
python tools/sync_rules.py --list

# Sync to your IDE
python tools/sync_rules.py --ide cline       # VS Code + Cline
python tools/sync_rules.py --ide cursor      # Cursor
python tools/sync_rules.py --ide windsurf    # Windsurf
python tools/sync_rules.py --ide claude_code # Claude Code (CLAUDE.md)
python tools/sync_rules.py --all             # All IDEs at once
```

### When to Re-Sync

Run `python tools/sync_rules.py` whenever you:
- Update `AGENTS.md` with new conventions
- Add new tools or workflows
- Change project structure

---

## ⭐ Step 2: Set Up MCP Servers (Also Critical!)

MCP (Model Context Protocol) servers give your AI superpowers: persistent memory, advanced text processing, and structured reasoning.

### Check What You Need

```bash
# See what's installed and what's missing
python tools/setup_mcp.py --check
```

Output will show:
```
🔍 Checking MCP tool installation:

  ✓ pomera     — Installed
  ✗ uvx        — NOT FOUND - Run: pip install uv
  ✓ npx        — Installed
```

### Get Setup Instructions for Your IDE

```bash
# Auto-detect your IDE
python tools/setup_mcp.py

# Or specify IDE
python tools/setup_mcp.py --ide vscode-cline
python tools/setup_mcp.py --ide cursor
python tools/setup_mcp.py --ide claude-desktop
```

This generates copy-paste ready configuration for your IDE's MCP settings.

### Quick Install All MCP Dependencies

```bash
# Install all MCP server dependencies
npm install -g pomera-ai-commander
npm install -g @modelcontextprotocol/server-sequential-thinking
pip install uv
```

---

## Environment Setup

### Python with Conda

**Why Conda?** Conda manages both Python versions and system dependencies, making it ideal for AI projects that need specific library versions.

#### Installation

1. **Install Miniconda** (lightweight) or Anaconda:
   - Miniconda: https://docs.conda.io/en/latest/miniconda.html
   - Windows: Download `.exe` installer, run with default options
   - macOS/Linux: `wget` the `.sh` script, run with `bash Miniconda3-*.sh`

2. **Verify installation:**
   ```bash
   conda --version
   conda info
   ```

#### Creating Project Environments

```bash
# Create new environment with specific Python version
conda create -n ai-project python=3.11

# Activate environment
conda activate ai-project

# Install packages
pip install -r requirements.txt
# OR use conda for packages with compiled dependencies
conda install numpy pandas scipy

# Deactivate when done
conda deactivate

# List all environments
conda env list
```

#### Environment Best Practices

```bash
# Export environment for reproducibility
conda env export > environment.yml

# Recreate environment from file
conda env create -f environment.yml

# Remove environment
conda env remove -n old-environment
```

#### VS Code Integration

The template includes `.vscode/settings.json` pre-configured for Conda:

```json
{
  "python.condaPath": "conda",
  "python.defaultInterpreterPath": "~/.conda/envs/ai-project/python"
}
```

---

## MCP Servers & Tools

### What is MCP?

Model Context Protocol (MCP) extends Claude's capabilities with specialized tools. This template configures three MCP servers:

### Available Servers

#### 1. Pomera Server (22 Text Tools)

Comprehensive text processing and persistent memory:

| Tool | Purpose | Example Use |
|------|---------|-------------|
| `pomera_notes` | Persistent memory across sessions | Save research, code snapshots, decisions |
| `pomera_extract` | Pattern extraction | Find URLs, emails, regex matches |
| `pomera_json_xml` | Data format handling | Validate/format JSON, XML |
| `pomera_markdown` | Markdown processing | Extract links, headers, tables |
| `pomera_text_stats` | Text analysis | Word count, reading time |
| `pomera_word_frequency` | Vocabulary analysis | Keyword density, overused words |
| `pomera_sort` | List operations | Sort, deduplicate, filter |
| `pomera_generators` | Content generation | UUIDs, slugs, timestamps |

**Setup:**
```bash
npm install -g pomera-ai-commander
```

#### 2. Text-Editor Server

Advanced file editing with conflict detection:

- Hash-based validation prevents overwriting concurrent changes
- Multi-range editing in single operations
- Line-range precision for large files

**Setup:**
```bash
# Requires Python's uv package manager
pip install uv
# Then uvx runs mcp-text-editor automatically when needed
```

#### 3. Sequential Thinking Server

Structured problem-solving with revision capability:

- Step-by-step analysis with adjustable depth
- Revise previous thoughts as understanding improves
- Branch into alternative reasoning paths

**Setup:**
```bash
# Global install (recommended)
npm install -g @modelcontextprotocol/server-sequential-thinking

# Or use npx for one-time runs (no install needed)
npx -y @modelcontextprotocol/server-sequential-thinking
```

### Quick Install All MCP Tools

```bash
# Node.js-based tools
npm install -g pomera-ai-commander
npm install -g @modelcontextprotocol/server-sequential-thinking

# Python-based tool
pip install uv
```

### MCP Configuration

Edit `mcp_settings.json` with your paths:

```json
{
  "mcpServers": {
    "pomera": {
      "command": "D:/Pomera/pomera.exe",
      "args": ["--mcp-server"],
      "timeout": 60
    },
    "text-editor": {
      "command": "uvx",
      "args": ["mcp-text-editor"],
      "timeout": 60
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
      "timeout": 60
    }
  }
}
```

---

## Web Search Integration

### Supported Search Engines

| Engine | Free Tier | Best For |
|--------|-----------|----------|
| **Brave Search** | 2000/month | General queries, default choice |
| **Google Custom Search** | 100/day | Complex queries, commercial intent |
| **Context7** | Varies | Code/library documentation |

### Usage

```bash
# Basic search (defaults to Brave)
python tools/web_search.py "your query"

# Specify engine
python tools/web_search.py "query" --engine brave
python tools/web_search.py "query" --engine google
python tools/web_search.py "pandas dataframe tutorial" --engine context7

# More results
python tools/web_search.py "query" --count 10

# JSON output for processing
python tools/web_search.py "query" --json
```

### API Key Setup

1. **Brave Search:** https://brave.com/search/api/
2. **Google Custom Search:**
   - API Key: https://console.cloud.google.com/apis/credentials
   - Search Engine ID: https://programmablesearchengine.google.com/
3. **Context7:** https://context7.io/

Edit `api-keys.json` with your credentials.

---

## SQLite for AI Context

### Why SQLite with AI?

Instead of having AI manually process large datasets with reasoning (expensive, slow, error-prone), use SQLite for:

- **Smart context building:** Query only relevant data before asking AI
- **Efficient data processing:** SQL handles aggregation, filtering, joins
- **Persistent storage:** Data survives between sessions
- **Scalable:** Handles millions of rows efficiently

### Pattern: Query First, Then Reason

**Bad approach:**
```
AI: "Here's all 10,000 emails. Let me analyze each one..."
(Consumes entire context window, slow, expensive)
```

**Good approach:**
```sql
-- AI asks for summary query first
SELECT platform, COUNT(*) as count, MAX(timestamp) as latest
FROM emails
GROUP BY platform
ORDER BY count DESC;

-- AI gets focused context
AI: "I see 500 TradingView notifications, 300 from LinkedIn..."
```

### Database Design Tips

```python
import sqlite3

# Enable WAL mode for better concurrency
conn = sqlite3.connect('data.db')
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA synchronous=NORMAL")
conn.row_factory = sqlite3.Row  # Dict-like access

# Index frequently queried columns
conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON data(timestamp)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON data(category)")
```

### Example: Email Processing System

See `tools/email/` for a complete example of:
- OAuth2 authentication
- Batch fetching with rate limiting
- Platform detection and enrichment
- Efficient SQLite storage with upsert pattern

---

## Workflow Templates

### Coding Projects

```markdown
## Session Startup
1. Check pomera notes for previous session state
2. Review current-focus.md for active tasks
3. Run validation: `python tools/validate_site.py`

## Before Major Changes
1. Save original code to pomera_notes
2. Create todo list with implementation steps
3. Make changes incrementally, validating each step

## Before Commits
1. Run all validations
2. Review changes with git diff
3. Use conventional commit format
```

### Data Analysis Projects

```markdown
## Data Ingestion
1. Create SQLite schema matching your data structure
2. Batch insert with executemany() for efficiency
3. Add indexes on columns you'll filter/sort by

## Analysis Workflow
1. Start with SQL queries to understand data shape
2. Export relevant subsets for AI analysis
3. Use pandas for complex transformations
4. Save insights to pomera_notes

## Reporting
1. Generate visualizations with matplotlib/plotly
2. Export summaries in markdown
3. Archive analysis in dated notes
```

### Creative Writing Projects

```markdown
## Research Phase
1. Use web_search.py to gather source material
2. Save research snippets to pomera_notes
3. Extract key themes with pomera_word_frequency

## Writing Phase
1. Create outline in pomera_notes
2. Draft sections, saving versions as you go
3. Use pomera_text_stats for word count targets

## Revision Phase
1. Compare draft versions with pomera_list_compare
2. Check for overused words with word_frequency
3. Save final version with clear title
```

### Research Projects

```markdown
## Source Collection
1. Search with multiple engines (Brave, Google, Context7)
2. Extract URLs and save to pomera_notes
3. Fetch and summarize key pages

## Analysis
1. Use sequential_thinking for complex topics
2. Compare sources with list_compare
3. Build structured notes with markdown tools

## Synthesis
1. Aggregate findings in dated notes
2. Generate summary with key citations
3. Archive research trail for reproducibility
```

---

## Project Structure

```
ai-project-template/
├── .agent/                    # AI-specific documentation
│   ├── context/              # Session state tracking
│   │   ├── current-focus.md  # Active work items
│   │   ├── known-issues.md   # Tracked bugs
│   │   └── recent-changes.md # Modification log
│   ├── docs/                 # Architecture documentation
│   └── workflows/            # Reusable workflow guides
├── .vscode/                   # Editor configuration
├── tools/                     # Python scripts and utilities
│   ├── web_search.py         # Multi-engine web search
│   └── email/                # Email processing example
├── AGENTS.md                  # AI guidance document
├── api-keys.json             # API credentials (template)
├── mcp_settings.json         # MCP server configuration
└── README.md                 # Project overview
```

### Key Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Comprehensive AI assistant guidance |
| `api-keys.json` | API credentials (use `.local.json` for real keys) |
| `mcp_settings.json` | MCP server paths and settings |
| `.agent/context/*.md` | Session state for continuity |

---

## Security Notes

### Credential Management

1. **Never commit real API keys** - Use `api-keys.local.json` pattern
2. **Add to .gitignore:**
   ```
   api-keys.local.json
   *.pickle
   **/token.pickle
   **/credentials.json
   **/*_secrets.json
   *.db
   ```
3. **Rotate exposed keys immediately** if accidentally committed

### Environment Variables Alternative

```python
import os

# Instead of api-keys.json
BRAVE_API_KEY = os.environ.get('BRAVE_API_KEY')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
```

### OAuth Token Security

- OAuth tokens (`.pickle` files) grant account access
- Never commit to version control
- Store in user-specific directories outside project

---

## Prompt Improvement System

### Why Invest in Better Prompts?

Every vague or poorly-structured prompt costs you:
- **Tokens** — More back-and-forth = more money spent
- **Time** — Waiting for clarification loops
- **Quality** — Inconsistent results require manual fixes

This template includes a comprehensive **Prompt Progression Guide** that teaches systematic prompt improvement.

### Token Savings at a Glance

| Technique | How It Saves | Potential Savings |
|-----------|--------------|-------------------|
| **Explicit formatting** | Avoids "can you reformat that?" follow-ups | 20-30% |
| **Few-shot examples** | AI understands faster, fewer iterations | 30-50% |
| **Constraints** | "Max 5 items" = shorter responses | 20-40% |
| **Prompt caching** | Static context first, reused across calls | Up to 90% |
| **RAG patterns** | Only inject relevant docs, not everything | Up to 70% |
| **RSIP (self-improvement)** | AI catches own errors before you do | 40-60% |

### The POWER Framework (Intermediate Level)

Use this structure for consistent results:

| Letter | Element | Example |
|--------|---------|---------|
| **P** | Purpose | "Review this code for security issues" |
| **O** | Output Format | "Return as numbered list with severity" |
| **W** | What (Core Task) | "Focus on SQL injection and XSS" |
| **E** | Examples | Show 2-3 sample outputs |
| **R** | Rules/Constraints | "Maximum 5 issues, skip style" |

### Quick Start: Pick Your Level

| If You're... | Start With | Time Investment |
|--------------|------------|-----------------|
| **New to prompting** | Beginner section: Clear commands | 10 min read |
| **Getting inconsistent results** | Intermediate: POWER framework | 20 min read |
| **Want to optimize costs** | Advanced: Meta-cognition patterns | 30 min read |
| **Building AI workflows** | Expert: Context engineering | Full guide |

### Practical Implementation

1. **Read the guide:** [`.agent/docs/prompt-progression-guide.md`](./.agent/docs/prompt-progression-guide.md)

2. **Create your prompt library:**
   ```
   .agent/
   └── prompts/
       ├── README.md          # Index of your prompts
       ├── templates/         # Reusable structures
       └── weekly-reflections/ # Learning journal
   ```

3. **Schedule weekly reflection** (10 minutes every Friday):
   - What prompt worked best this week?
   - What prompt failed? How would you rewrite it?
   - One technique to practice next week

4. **Use AI as your coach** — Copy reflection prompts from the guide and run them on your recent work

### Example: Before & After

**Before (vague):**
```
Summarize this article
```

**After (structured):**
```
TASK: Summarize this article for a fintech newsletter
FORMAT: 3 bullet points, each under 20 words
CONSTRAINTS: No jargon, no promotional language
AUDIENCE: Busy professionals
```

**Result:** First version might need 2-3 follow-ups. Second version works on first try = 60% token savings.

### The Progression Path

| Level | What You'll Learn | Key Outcome |
|-------|------------------|-------------|
| **1. Beginner** | Clear commands, explicit formats | Coherent responses |
| **2. Intermediate** | POWER framework, few-shot examples | Consistent quality |
| **3. Advanced** | RSIP, confidence calibration | Self-correcting prompts |
| **4. Expert** | Context budgeting, meta-prompting | Autonomous workflows |

**👉 Action item:** Read the guide, pick ONE technique, practice it for one week, then level up.

---

## Related Resources

### GitHub Templates & Inspiration

- [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) - Curated commands and workflows
- [claude-flow](https://github.com/ruvnet/claude-flow) - Multi-agent orchestration
- [awesome-ai-agents](https://github.com/e2b-dev/awesome-ai-agents) - Comprehensive agent list
- [GenAI_Agents](https://github.com/NirDiamant/GenAI_Agents) - Tutorial implementations
- [500-AI-Agents-Projects](https://github.com/ashishpatel26/500-AI-Agents-Projects) - Use case collection

### Best Practices

- [How to write a great agents.md](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/) - GitHub's analysis
