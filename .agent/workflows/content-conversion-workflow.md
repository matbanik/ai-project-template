---
description: Content conversion using markdownify MCP and Python tools
---

# Content Conversion Workflow

## Markdownify MCP Tools

Enable with: "use markdownify" in prompt

| Tool | Input | Output |
|------|-------|--------|
| `pdf-to-markdown` | PDF file | Markdown text |
| `image-to-markdown` | Image file | Markdown with metadata |
| `audio-to-markdown` | Audio file | Transcription as markdown |
| `docx-to-markdown` | Word document | Markdown |
| `xlsx-to-markdown` | Excel file | Markdown tables |
| `pptx-to-markdown` | PowerPoint | Markdown slides |
| `webpage-to-markdown` | URL | Clean markdown content |
| `youtube-to-markdown` | YouTube URL | Video transcript |
| `bing-search-to-markdown` | Search query | Results as markdown |

## Python Web Tools

### read_url_content (Native)

```bash
# Built-in tool for fetching web content
read_url_content --Url "https://example.com"
```

Best for: Static pages, documentation, APIs

### web_search.py

```bash
# Search with file output
python tools/web_search.py "query" -o searches/ -t task-name
```

Saves to: `searches/YYYY-MM-DD/HH-MM-SS-{engine}-{query}.json`

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
FORMAT: {pdf/docx/audio/video/web}
TOOL: {markdownify tool used}" \
  --output_content "{converted markdown content}

SUMMARY:
- {key takeaway 1}
- {key takeaway 2}"
```

## When to Use Each

| Task | Tool |
|------|------|
| Quick web fetch | `read_url_content` |
| PDF/Office docs | `markdownify` MCP |
| YouTube transcript | `markdownify` MCP |
| Web search + save | `web_search.py -o` |
| Extract patterns | `pomera_extract` |

## Output Organization

```
content-docs/
├── exports/           # Processed outputs
│   ├── transcripts/   # Audio/video transcripts
│   ├── documents/     # Converted docs
│   └── research/      # Research summaries
└── research/          # Source materials
```
