---
description: Content conversion using web tools and pomera text processing
---

# Content Conversion Workflow

## Native Web Tools

### read_url_content (Built-in)

```bash
# Fetch and convert web content to markdown
read_url_content --Url "https://example.com"
```

Best for: Static pages, documentation, APIs, blog posts

### web_search.py

```bash
# Search with file output
python tools/web_search.py "query" -o searches/ -t task-name
```

Saves to: `searches/YYYY-MM-DD/HH-MM-SS-{engine}-{query}.json`

## Pomera Text Processing Tools

| Tool | Purpose |
|------|---------|
| `pomera_extract` | Extract URLs, emails, patterns from text |
| `pomera_markdown` | Process markdown (strip, extract links/headers) |
| `pomera_html` | Extract visible text from HTML |
| `pomera_text_stats` | Word count, reading time |
| `pomera_json_xml` | Validate/prettify JSON/XML |

## Conversion Workflow

1. **Fetch content** using appropriate tool
2. **Log to Pomera** for cross-session reference
3. **Extract key info** using pomera tools
4. **Save processed output** to content-docs/exports/

```bash
# Example: Web page to notes
# 1. Fetch
read_url_content --Url "https://example.com/docs"

# 2. Log to Pomera
pomera_notes save --title "Research/{topic}/{date}" \
  --input_content "SOURCE: https://example.com/docs
TYPE: web page
TASK: {why fetching this}" \
  --output_content "{extracted key content}

KEY POINTS:
- {insight 1}
- {insight 2}"

# 3. Extract URLs if needed
pomera_extract --text "<content>" --type urls
```

## Pomera Logging After Conversions

**Always log after converting content:**

```bash
pomera_notes save \
  --title "Conversion/{type}/{date}-{source-name}" \
  --input_content "SOURCE: {file path or URL}
FORMAT: {web/text/json}
TOOL: {tool used}" \
  --output_content "{converted content}

SUMMARY:
- {key takeaway 1}
- {key takeaway 2}"
```

## When to Use Each

| Task | Tool |
|------|------|
| Quick web fetch | `read_url_content` |
| Web search + save | `web_search.py -o` |
| Extract patterns | `pomera_extract` |
| Process HTML | `pomera_html` |
| Markdown processing | `pomera_markdown` |

## Output Organization

```
content-docs/
├── exports/           # Processed outputs
│   ├── transcripts/   # Audio/video transcripts
│   ├── documents/     # Converted docs
│   └── research/      # Research summaries
└── research/          # Source materials
```
