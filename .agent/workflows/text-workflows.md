---
description: Text processing using mcp_text-editor, pomera, and native IDE tools
---

# Text Workflows

## Tool Selection Matrix

| Task | Best Tool | Why |
|------|-----------|-----|
| Read file | `view_file` (native) | Line numbers, structured |
| Create file | `write_to_file` (native) | Creates dirs, handles encoding |
| Single edit | `replace_file_content` (native) | Simple, fast |
| Multi-edit (same file) | `multi_replace_file_content` | Non-contiguous changes |
| Complex edit with conflicts | `mcp_text-editor` | Hash verification |
| Pattern extraction | `pomera_extract` | Regex, URLs, emails |
| Text statistics | `pomera_text_stats` | Word count, reading time |
| Compare versions | `pomera_list_compare` | Diff two lists |

## mcp_text-editor Workflow

Use for complex multi-range edits with conflict detection:

```bash
# 1. Get file contents with hash
get_text_file_contents --file_path "/path/to/file" --ranges [{"start":1}]

# 2. Edit with hash verification
edit_text_file_contents --files [{
  "path": "/path/to/file",
  "file_hash": "<hash from step 1>",
  "patches": [{"line_start": 10, "line_end": 15, "contents": "<new content>"}]
}]
```

## Pomera Text Tools

### Notes (Version Control)

```bash
# Save before major changes
pomera_notes save --title "Code/{file}-{date}" --input_content "<content>"

# Search history
pomera_notes search --search_term "Code/*" --limit 10

# Retrieve backup
pomera_notes get --note_id <id>
```

### Pattern Extraction

```bash
# Extract URLs
pomera_extract --text "<content>" --type urls

# Extract with regex
pomera_extract --text "<content>" --type regex --pattern "function \w+\("
```

### Text Analysis

```bash
# Get statistics
pomera_text_stats --text "<content>" --words_per_minute 200

# Check word frequency
pomera_word_frequency --text "<content>"
```

### Formatting

```bash
# Clean whitespace
pomera_whitespace --text "<content>" --operation trim

# Process lines
pomera_line_tools --text "<content>" --operation remove_duplicates

# Validate JSON
pomera_json_xml --operation json_validate --text "<json>"
```

## Native IDE Tools

### File Operations

| Tool | Use |
|------|-----|
| `view_file` | Read with line numbers |
| `view_file_outline` | Get structure (functions, classes) |
| `write_to_file` | Create/overwrite file |
| `replace_file_content` | Single contiguous edit |
| `multi_replace_file_content` | Multiple non-contiguous edits |

### Search Operations

| Tool | Use |
|------|-----|
| `grep_search` | Find text patterns |
| `find_by_name` | Find files by name/pattern |
| `view_code_item` | View specific function/class |

## Naming Conventions for Notes

| Category | Pattern |
|----------|---------|
| Code backups | `Code/{Component}/{Description}-{Date}` |
| Writing drafts | `Writing/{Project}/{Type}-{Date}` |
| Research | `Research/{Topic}/{Description}-{Date}` |
| Session memory | `Memory/Session/{Task}-{Date}` |
| Decisions | `Memory/Decisions/{Topic}-{Date}` |
