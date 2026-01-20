---
description: Web search engine selection and result logging
---

# Web Search Workflow

## Quick Reference

```bash
# Basic (defaults to Tavily)
python tools/web_search.py "query"

# Specify engine
python tools/web_search.py "query" --engine tavily
python tools/web_search.py "query" --engine google
python tools/web_search.py "query" --engine brave
python tools/web_search.py "query" --engine duckduckgo

# Save results to file (RECOMMENDED for AI workflows)
python tools/web_search.py "query" --output searches/ --task task-name
```

---

## Engine Priority

**Default order (use unless user specifies):**

| Priority | Engine | Limit | Best For |
|----------|--------|-------|----------|
| 1 | **tavily** | 1000/month | AI-optimized snippets (DEFAULT) |
| 2 | google | 100/day | Complex, specific queries |
| 3 | brave | 2000/month | General search |
| 4 | duckduckgo | Unlimited | Backup, privacy, rate limited |

**Conserve these (one-time credits):**

| Engine | Total Limit | Use Only If |
|--------|-------------|-------------|
| serpapi | 100 total | Explicitly instructed |
| serper | 2500 total | Explicitly instructed |

---

## Pomera Search Logging

**After each significant search, log to Pomera:**

```bash
pomera_notes save \
  --title "Search/{YYYY-MM-DD}/{query-slug}" \
  --input_content "QUERY: {search query}
ENGINE: {engine used}
TASK: {what you're researching}" \
  --output_content "RESULTS:
1. {title} - {snippet} - {url}
2. {title} - {snippet} - {url}
3. {title} - {snippet} - {url}

KEY FINDINGS:
- {main insight 1}
- {main insight 2}"
```

**Why log searches:**
- Cross-session reference (avoid repeating searches)
- Track research progress
- Learn which engines work best
- Build personal knowledge base

---

## Search + URL Content Workflow

For in-depth research:

```bash
# 1. Search
python tools/web_search.py "query" -o searches/ -t research-topic

# 2. Read promising URLs (tool depends on your environment)
# - If you have a URL->markdown tool (e.g., markdownify), use it
# - Otherwise open in a browser and copy key excerpts

# 3. Log combined findings
pomera_notes save \
  --title "Research/{topic}/{date}" \
  --input_content "QUERY: {query}\nSOURCES: {urls}" \
  --output_content "{key excerpts + notes}"
```

---

## When to Search

**DO search:**
- Technical questions needing current info
- Library/framework documentation
- Best practices and patterns
- Error messages and solutions
- Competitive research

**SKIP search:**
- Questions answerable from context
- Project-specific logic
- Code already visible in files
- Repeated searches same session
- Simple syntax questions (prefer local docs/Context7 if available)

---

## Context7 (MCP Only)

For code documentation in AI editors:
- Optional: configure a Context7 MCP server in your IDE (not included in this template by default)
- Include "use context7" in prompts
- Not available as CLI search
- Best for: Library docs, API patterns, code examples

---

## Output File Structure

When using `--output searches/`:

```
searches/
└── 2026-01-19/
    ├── 10-30-45-tavily-task-seo-research-cycling-keywords.json
    ├── 11-15-22-google-python-async-patterns.json
    └── 14-00-00-brave-competitor-analysis.json
```

Each JSON contains:
- `meta`: query, engine, timestamp, task
- `results`: title, snippet, url, source for each result
