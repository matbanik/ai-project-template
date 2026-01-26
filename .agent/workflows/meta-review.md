---
description: Review workflow documents for token efficiency and clarity, analyze session prompts for metacognition
---

# Meta-Review Workflow

## Purpose

Periodically review AGENTS.md and workflow documents to:
1. Remove redundant instructions
2. Consolidate similar patterns
3. Keep content beginner-friendly
4. Optimize for work efficiency
5. **Analyze prompting patterns for improvement** (new)

---

## Session Prompt Analysis (Metacognition)

Use `extract_user_prompts.py` to analyze your prompting patterns from exported sessions.

### Quick Commands

```bash
# Export session from Antigravity: Menu → Export
# Then analyze:

# Statistics only - quick overview
python tools/extract_user_prompts.py session-export.md --stats

# Training format - grouped by category with tips
python tools/extract_user_prompts.py session-export.md --training -o review.md

# Full analysis with categories
python tools/extract_user_prompts.py session-export.md --analyze --json

# Batch process all exports
python tools/extract_user_prompts.py exports/ --batch --stats
```

### What to Look For

| Pattern | Issue | Improvement |
|---------|-------|-------------|
| Short prompts (<10 words) | Missing context | Add file refs, expected outcome |
| Many "continue" prompts | AI needs clarification | Be more specific upfront |
| Multiple corrections | Misunderstood intent | State constraints early |
| Few file references | Context switching overhead | Use @[file] syntax |

### AI Agent Summary Request

After running the analysis, ask the AI to summarize patterns:

```
Review the extracted prompts and provide feedback on:
1. Which prompts were most effective and why
2. Patterns that led to back-and-forth clarification
3. Suggestions for more efficient prompting
4. Token-saving opportunities I missed
```

---

## When to Run

- After adding new workflows
- Monthly maintenance
- When AGENTS.md exceeds 150 lines
- When workflows feel verbose
- **After completing complex sessions** (for prompt analysis)

---

## Review Checklist

### AGENTS.md (<150 lines target)

- [ ] No duplicate sections
- [ ] Tables used instead of verbose lists
- [ ] Examples are minimal but complete
- [ ] Commands use template syntax `{var}`
- [ ] Links to workflows, not inline details

### Workflow Documents

- [ ] Clear, numbered steps
- [ ] No over-explanation
- [ ] Turbo annotations where appropriate
- [ ] Examples are actionable

### Session Prompt Quality

- [ ] Avg words/prompt ≥ 15
- [ ] Command prompts > 50%
- [ ] File references where applicable
- [ ] Minimal correction/clarification cycles

---

## Optimization Patterns

| Before | After | Savings |
|--------|-------|---------|
| Long paragraphs | Bullet points | ~30% |
| Repeated instructions | Link to section | ~50% |
| Full command examples | Template `{var}` | ~40% |
| Vague prompts | Specific + @[file] refs | ~60% |

---

## Quick Audit Commands

```bash
# Count AGENTS.md lines
wc -l AGENTS.md

# List all workflows
ls -la .agent/workflows/

# Analyze recent session
python tools/extract_user_prompts.py session-export.md --stats
```

---

## After Review

1. Update AGENTS.md with improvements
2. If requested, commit: `git commit -m "docs: meta-review optimization"`
3. Log review to pomera:
```bash
pomera_notes save --title "Meta/Review/{date}" \
  --input_content "Reviewed: AGENTS.md, {workflows}" \
  --output_content "Changes: {summary}"
```
