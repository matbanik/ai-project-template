---
description: Log prompts and responses to Pomera for cross-session learning
---

# Session Logging Workflow

## Purpose

Record interactions to:
1. Build searchable history across sessions
2. Identify effective prompting patterns
3. Learn from successful approaches
4. Maintain continuity between sessions

---

## Automatic Logging (AI Should Do This)

### After Significant Work

```bash
pomera_notes save \
  --title "Session/{YYYY-MM-DD}/{HH-MM}-{task-slug}" \
  --input_content "USER PROMPT:
{original user request}

CONTEXT:
- Files: {list of files involved}
- Goal: {what user wanted to achieve}" \
  --output_content "AI RESPONSE:
- Approach: {what was done}
- Tools: {tools used}
- Files changed: {list}
- Outcome: {success/partial/failed}
- Lessons: {what worked, what didn't}"
```

### After Web Searches

```bash
pomera_notes save \
  --title "Search/{YYYY-MM-DD}/{query-slug}" \
  --input_content "QUERY: {search terms}
ENGINE: {tavily/google/brave}
TASK: {why searching}" \
  --output_content "RESULTS:
1. {title} - {key insight}
2. {title} - {key insight}
3. {title} - {key insight}

APPLIED: {how results were used}"
```

---

## When to Log

**Always log:**
- Complex multi-step tasks completed
- Novel problem-solving approaches
- Workflow discoveries
- Significant debugging sessions
- Research with multiple sources

**Skip logging:**
- Simple Q&A interactions
- Routine file edits (<5 lines)
- Repetitive tasks same session

---

## Search & Review

```bash
# Find recent sessions
pomera_notes list --limit 20

# Search by topic
pomera_notes search --search_term "Session/*refactor*" --limit 10

# Find successful approaches
pomera_notes search --search_term "*success*" --limit 10

# Review specific date
pomera_notes search --search_term "Session/2026-01-19/*" --limit 20
```

---

## Learning From History

**Start of new session:**
```bash
# Check what was done last time
pomera_notes search --search_term "Session/*" --limit 5

# Find related past work
pomera_notes search --search_term "*{topic}*" --limit 10
```

**When stuck:**
```bash
# Find how similar problems were solved
pomera_notes search --search_term "*{error or problem}*"
```

---

## Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Sessions | `Session/{date}/{HH-MM}-{task}` | `Session/2026-01-19/14-30-refactor-users` |
| Searches | `Search/{date}/{query}` | `Search/2026-01-19/python-async-patterns` |
| Backups | `Backup/{filepath}-{date}` | `Backup/src-api-py-2026-01-19` |
| Decisions | `Decision/{topic}` | `Decision/auth-jwt-vs-session` |
| Memory | `Memory/{type}/{topic}` | `Memory/Context/project-architecture` |

---

## Monthly Cleanup

Review and archive old sessions:
```bash
# List sessions from last 30 days
pomera_notes search --search_term "Session/*" --limit 100

# Archive valuable patterns to Memory/
pomera_notes save --title "Memory/Patterns/{topic}" \
  --input_content "{consolidated lessons from multiple sessions}"
```
