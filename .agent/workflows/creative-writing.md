# Creative Writing Workflow

AI-guided workflow for creative writing projects: storytelling, blog posts, articles, and content creation.

## Principles

1. **Research before writing** - Build context and inspiration first
2. **Version everything** - Save drafts at each major stage
3. **Iterate with feedback** - Use text analysis tools to refine
4. **Maintain voice consistency** - Document style decisions

---

## Phase 1: Research & Inspiration

### Gather Source Material
```bash
# Search for topic background
python tools/web_search.py "topic research query" --engine brave

# For code/technical topics
python tools/web_search.py "topic documentation" --engine context7
```

### Save Research Notes
```bash
# Create research note with sources
pomera_notes save --title "Writing/{Project}/Research-{date}" \
  --input_content "URLs, quotes, key facts" \
  --output_content "Themes to explore, angles to consider"

# Extract URLs from research
pomera_extract --text "<research content>" --type urls
```

### Build Character/Topic Profiles
```bash
# For fiction: character sheets
pomera_notes save --title "Writing/{Project}/Characters/{name}" \
  --input_content "Background, motivations, relationships"

# For non-fiction: topic outline
pomera_notes save --title "Writing/{Project}/Outline" \
  --input_content "Main points, structure, key arguments"
```

---

## Phase 2: Planning & Outlining

### Create Structure
```bash
# Use sequential thinking for complex narratives
sequentialthinking --thought "Planning story structure..."
  --thoughtNumber 1 --totalThoughts 5 --nextThoughtNeeded true

# Save outline to notes
pomera_notes save --title "Writing/{Project}/Outline-v1" \
  --input_content "Chapter/section breakdown"
```

### Set Word Count Targets
```bash
# Example targets by type:
# - Blog post: 800-1500 words
# - Article: 1500-3000 words
# - Short story: 3000-7500 words
# - Novella: 17,500-40,000 words

# Track during writing
pomera_text_stats --text "<draft>" --words_per_minute 200
```

---

## Phase 3: Drafting

### First Draft Approach
- Write freely without self-editing
- Save frequently to pomera_notes
- Mark sections needing research with [TODO: research X]

### Version Management
```bash
# Save each draft version
pomera_notes save --title "Writing/{Project}/Draft-v1-{date}" \
  --input_content "<complete draft>"

# Later versions
pomera_notes save --title "Writing/{Project}/Draft-v2-{date}" \
  --input_content "<revised draft>"
```

### Handle Writer's Block
```bash
# Use sequential thinking to unstick
sequentialthinking --thought "Character is stuck at [point]. Options: ..."
  --thoughtNumber 1 --totalThoughts 3

# Search for inspiration
python tools/web_search.py "similar story situations"
```

---

## Phase 4: Revision

### Self-Analysis Tools
```bash
# Check word frequency (find overused words)
pomera_word_frequency --text "<draft>"

# Check reading statistics
pomera_text_stats --text "<draft>" --words_per_minute 200

# Extract all headers/structure
pomera_markdown --operation extract_headers --text "<draft>"
```

### Compare Versions
```bash
# List drafts
pomera_notes search --search_term "Writing/{Project}/Draft*"

# Compare two versions
pomera_list_compare \
  --list_a "<sentences from v1>" \
  --list_b "<sentences from v2>"
```

### Style Checks

| Check | Tool | What to Look For |
|-------|------|------------------|
| Overused words | `pomera_word_frequency` | Words appearing >3% |
| Sentence variety | `pomera_text_stats` | Average sentence length |
| Structure | `pomera_markdown` | Heading balance |
| Readability | Manual review | Varied paragraph lengths |

---

## Phase 5: Polish

### Final Formatting
```bash
# Wrap paragraphs for readability
pomera_text_wrap --text "<paragraph>" --width 80

# Generate URL slug (for blog posts)
pomera_generators --generator slug --text "Article Title Here"

# Generate unique ID (for tracking)
pomera_generators --generator uuid
```

### Pre-Publication Checklist

- [ ] Spelling and grammar check (external tool)
- [ ] All [TODO] markers resolved
- [ ] Word count meets target
- [ ] Headers properly structured
- [ ] Links validated
- [ ] Images have alt text (if applicable)
- [ ] Meta description written (for web)

### Archive Final Version
```bash
pomera_notes save --title "Writing/{Project}/Final-{date}" \
  --input_content "<final version>" \
  --output_content "Publication notes, platform, URL"
```

---

## Genre-Specific Tips

### Blog Posts
- Strong hook in first paragraph
- Subheadings every 300-400 words
- Bullet points for scanability
- Call to action at end

### Technical Articles
- Code examples with context
- Step-by-step instructions
- Prerequisite section
- "What you'll learn" upfront

### Fiction
- Show, don't tell
- Dialogue advances plot
- Sensory details
- Consistent POV

### Research/Reports
- Executive summary first
- Citations throughout
- Data visualization
- Recommendations section

---

## Template: Blog Post Planning

```markdown
# Blog Post: [Title]

## Meta
- Target audience: [who]
- Word count target: [number]
- Primary keyword: [keyword]
- Publish date: [date]

## Research Notes
[Links and key facts]

## Outline
1. Hook/Introduction
2. Main Point 1
3. Main Point 2
4. Main Point 3
5. Conclusion/CTA

## Draft History
- v1: [date] - First draft
- v2: [date] - Structure revision
- v3: [date] - Final polish
```

---

## Template: Story Planning

```markdown
# Story: [Title]

## Concept
One-line summary: [logline]

## Characters
- Protagonist: [name, motivation, arc]
- Antagonist: [name, motivation]
- Supporting: [names, roles]

## Structure
- Opening: [hook/inciting incident]
- Rising action: [key events]
- Climax: [turning point]
- Resolution: [conclusion]

## Research Needed
- [Topic 1]
- [Topic 2]

## Draft History
[tracked in pomera_notes]
```
