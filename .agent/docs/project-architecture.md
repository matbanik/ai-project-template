# Project Architecture

> **AI-GUIDANCE**: This document describes the system design, data flow, and key patterns. Read this before making architectural changes. Update when adding major components.

## Overview

<!-- High-level description of what this project does -->

This is an AI agent project template with tools for web search, data processing, and persistent memory.

## System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     User / AI Agent                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
    ┌──────────┐    ┌──────────┐    ┌──────────────┐
    │   MCP    │    │  Tools   │    │   Context    │
    │ Servers  │    │ (Python) │    │   (.agent/)  │
    └────┬─────┘    └────┬─────┘    └──────────────┘
         │               │
         │               ▼
         │         ┌──────────┐
         │         │  SQLite  │
         │         │   Data   │
         │         └──────────┘
         │
    ┌────┴─────────────────────────────┐
    │         MCP Capabilities         │
    ├──────────────┬───────────────────┤
    │   Pomera     │  Sequential       │
    │   (Notes,    │  Thinking         │
    │   Text       │  (Analysis)       │
    │   Processing)│                   │
    └──────────────┴───────────────────┘
```

## Directory Structure

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `tools/` | Python utilities | `web_search.py`, `email/` |
| `.agent/context/` | Session state | `current-focus.md`, `known-issues.md` |
| `.agent/docs/` | Architecture docs | This file |
| `.agent/workflows/` | Reusable workflows | Data analysis, writing, research |

## Data Flow Patterns

### Web Search Flow
```
Query → web_search.py → API (Brave/Google/Context7) → Results → AI Analysis
```

### Persistent Memory Flow
```
Session Work → pomera_notes save → SQLite DB → pomera_notes search → Resume
```

### Data Processing Flow
```
Raw Data → SQLite Import → SQL Queries → Focused Subset → AI Reasoning
```

## Key Design Decisions

<!-- Document important architectural choices -->

| Decision | Rationale |
|----------|-----------|
| SQLite for data | Portable, no server needed, handles large datasets |
| pomera_notes for memory | Persistent across sessions, full-text search |
| Multi-engine search | Different engines excel at different query types |
| File-based context | Easy to read/update, version controlled |

## Extension Points

<!-- Where to add new functionality -->

1. **New tools**: Add Python scripts to `tools/`
2. **New workflows**: Add markdown to `.agent/workflows/`
3. **New MCP servers**: Configure in `mcp_settings.json`
4. **New platforms** (email): Add patterns to `tools/email/platforms.py`

---

## Update Protocol

**When to update this file:**
1. Adding major new components
2. Changing data flow patterns
3. Making architectural decisions
4. Deprecating components

**Keep this file:**
- High-level (not implementation details)
- Current (remove deprecated info)
- Useful for orientation (new session context)
