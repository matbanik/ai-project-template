# Research Project Workflow

AI-guided workflow for research projects: literature review, competitive analysis, topic exploration, and knowledge synthesis.

---

## Phase 0: Context Creation (5W1H Framework)

> **AI-GUIDANCE**: Before any research begins, establish complete context using 5W1H. This creates optimal conditions for focused, efficient AI assistance.

### The 5W1H Questions

Answer ALL six questions before proceeding:

| Question | Purpose | Example |
|----------|---------|---------|
| **WHO** | Target audience, stakeholders, personas | "Beginner developers learning Python" |
| **WHAT** | Core topic, specific deliverables | "Tutorial series on async programming" |
| **WHEN** | Timeline, recency requirements | "Published 2023+, deadline in 2 weeks" |
| **WHERE** | Geography, platform, context | "Stack Overflow, GitHub, English sources" |
| **WHY** | Motivation, success criteria | "Fill content gap, drive 5K monthly views" |
| **HOW** | Methods, tools, output format | "Web search → synthesis → markdown report" |

### Context Template

```yaml
research_context:
  who: "[audience + stakeholders]"
  what: "[topic + deliverables]"
  when: "[timeframe + recency needs]"
  where: "[sources + geography + platform]"
  why: "[motivation + success metrics]"
  how: "[methodology + tools + output format]"
```

### Example: Filled Context

```yaml
research_context:
  who: "Product managers evaluating no-code tools"
  what: "Comparison of top 5 platforms, feature matrix"
  when: "Q1 2024 data, 1-week deadline"
  where: "Official sites, G2 reviews, tech blogs"
  why: "Support vendor selection, save $50K decision"
  how: "Web search → feature extraction → comparison table"
```

---

## Prioritized Questions Framework

> **Principle**: Not all questions are equal. Prioritize by impact and dependency.

### Question Priority Matrix

| Priority | Criteria | Action |
|----------|----------|--------|
| **P1 - Blocking** | Answers unlock other research | Research FIRST |
| **P2 - Core** | Directly answers main objective | Research NEXT |
| **P3 - Supporting** | Adds depth, nice-to-have | Research IF TIME |
| **P4 - Tangential** | Interesting but non-essential | SKIP or NOTE for later |

### Prioritization Checklist

Before researching each question, ask:

1. **Does this block other work?** → P1
2. **Does this directly answer the WHY?** → P2
3. **Does this add valuable context?** → P3
4. **Is this just curiosity?** → P4 (skip)

### Example: Prioritized Research Plan

```markdown
## Research: No-Code Platform Comparison

### P1 - Blocking Questions
- [ ] What are the current top 5 platforms by market share?
- [ ] What pricing tiers exist? (determines comparison structure)

### P2 - Core Questions  
- [ ] What are each platform's unique features?
- [ ] What are documented limitations of each?
- [ ] What do power users say about each?

### P3 - Supporting Questions
- [ ] What is each company's funding/stability?
- [ ] What integrations does each support?

### P4 - Tangential (Skip)
- [ ] History of each company
- [ ] Founder backgrounds
```

---

## Focused Execution Protocol

> **Principle**: One task at a time. Complete before moving to next.

### Execution Rules

1. **Single-thread research** - Complete one question fully before starting next
2. **Time-box each question** - Max 15 min per P2/P3 question
3. **Document as you go** - Save findings immediately, not at end
4. **Check dependencies** - P1 answers may change P2 questions

### Session Structure

```
┌─────────────────────────────────────┐
│  START: Load 5W1H context           │
├─────────────────────────────────────┤
│  LOOP (for each P1, then P2):       │
│    1. State the question clearly    │
│    2. Execute search (max 3 queries)│
│    3. Extract key findings          │
│    4. Save to notes immediately     │
│    5. Check: Does this change plan? │
├─────────────────────────────────────┤
│  END: Synthesize, identify gaps     │
└─────────────────────────────────────┘
```

---

## Principles

1. **Context first** - Complete 5W1H before any searches
2. **Prioritize ruthlessly** - P1 and P2 only, skip P4
3. **Single-thread execution** - One question at a time
4. **Multiple sources** - Never rely on single source; triangulate
5. **Document everything** - Save sources, quotes, and reasoning
6. **Structured synthesis** - Build knowledge incrementally
7. **Citation trail** - Track where information came from

---

## Phase 1: Define Scope

### Research Questions
```bash
# Document your research questions
pomera_notes save --title "Research/{Project}/Questions-{date}" \
  --input_content "Primary question: [what you want to know]
Secondary questions:
- [sub-question 1]
- [sub-question 2]
- [sub-question 3]"
```

### Scope Boundaries
Define what's in and out of scope:
- Time period: [specific range]
- Geographic focus: [regions]
- Industry/domain: [specific areas]
- Depth level: [overview vs deep dive]

---

## Phase 2: Source Collection

### Web Search Strategy
```bash
# General search (free tier: 2000/month)
python tools/web_search.py "research topic" --engine brave

# Complex/commercial queries (free tier: 100/day)
python tools/web_search.py "detailed query" --engine google

# Technical/code documentation
python tools/web_search.py "library documentation" --engine context7
```

### Multi-Engine Approach
| Query Type | Primary | Fallback |
|------------|---------|----------|
| General facts | Brave | Google |
| Academic | Google Scholar | Brave |
| Technical docs | Context7 | Google |
| Recent news | Brave | Google |

### Save Sources Systematically
```bash
# Create source entry for each valuable find
pomera_notes save --title "Research/{Project}/Source-{number}" \
  --input_content "URL: [url]
Author: [author]
Date: [date]
Key quotes:
- [quote 1]
- [quote 2]"
```

### Extract URLs for Later
```bash
# Extract all URLs from research notes
pomera_extract --text "<research notes>" --type urls
```

---

## Phase 3: Analysis

### Use Sequential Thinking for Complex Topics
```bash
# Break down complex analysis
sequentialthinking --thought "Analyzing conflicting claims about [topic]..."
  --thoughtNumber 1 --totalThoughts 5 --nextThoughtNeeded true

# Revise as understanding deepens
  --isRevision true --revisesThought 2
```

### Compare Sources
```bash
# Find agreements/disagreements
pomera_list_compare \
  --list_a "<claims from source 1>" \
  --list_b "<claims from source 2>"
```

### Identify Patterns
```bash
# Word frequency across sources
pomera_word_frequency --text "<combined source text>"

# Extract key themes
pomera_extract --text "<sources>" --type regex --pattern "(?:conclude|find|show|suggest)s? that .+?[.]"
```

---

## Phase 4: Synthesis

### Build Knowledge Structure
```bash
# Create synthesis note
pomera_notes save --title "Research/{Project}/Synthesis-{date}" \
  --input_content "Key findings:
1. [finding with citation]
2. [finding with citation]

Contradictions:
- Source A says X, Source B says Y

Gaps:
- [areas needing more research]"
```

### Cross-Reference Pattern
```
For each key claim:
1. Identify original source
2. Find supporting sources
3. Note any contradictions
4. Assess overall confidence
```

### Confidence Levels
| Level | Criteria |
|-------|----------|
| High | 3+ independent sources agree |
| Medium | 2 sources agree, no contradictions |
| Low | Single source or contradictions exist |
| Unverified | No authoritative source found |

---

## Phase 5: Documentation

### Research Report Structure
```markdown
# Research Report: [Topic]

## Executive Summary
[Key findings in 2-3 paragraphs]

## Methodology
- Search engines used
- Date range of sources
- Inclusion/exclusion criteria

## Findings

### Finding 1: [Title]
[Description]
Sources: [1], [2], [3]
Confidence: High/Medium/Low

### Finding 2: [Title]
...

## Gaps & Limitations
[What couldn't be determined]

## Recommendations
[Next steps or actions]

## Sources
1. [Author]. [Title]. [URL]. Accessed [date].
2. ...
```

### Archive Research Trail
```bash
# Save complete research package
pomera_notes save --title "Research/{Project}/Complete-{date}" \
  --input_content "<all source notes>" \
  --output_content "<synthesis and conclusions>"
```

---

## Specialized Research Types

### Competitive Analysis
```bash
# Research competitors
python tools/web_search.py "competitor name features"
python tools/web_search.py "competitor name pricing"
python tools/web_search.py "competitor name reviews"

# Track in structured notes
pomera_notes save --title "Research/Competitive/{competitor}" \
  --input_content "Features:
Pricing:
Strengths:
Weaknesses:
Sources:"
```

### Literature Review
```bash
# Academic search pattern
python tools/web_search.py "topic site:arxiv.org OR site:scholar.google.com"

# Track papers
pomera_notes save --title "Research/Literature/{paper-id}" \
  --input_content "Title:
Authors:
Year:
Abstract:
Key findings:
Methodology:
Limitations:"
```

### Market Research
```bash
# Industry data
python tools/web_search.py "industry market size 2024"
python tools/web_search.py "industry trends forecast"

# Structure findings
pomera_notes save --title "Research/Market/{segment}" \
  --input_content "Market size:
Growth rate:
Key players:
Trends:
Sources with dates:"
```

---

## Research Session Protocol

### Starting a Session
```bash
# 1. Load previous context
pomera_notes search --search_term "Research/{Project}/*" --limit 10

# 2. Review research questions
pomera_notes get --note_id [questions-note-id]

# 3. Check gaps from last session
pomera_notes search --search_term "*Gaps*"
```

### Ending a Session
```bash
# 1. Save session progress
pomera_notes save --title "Research/{Project}/Session-{date}" \
  --input_content "Sources reviewed:
Key findings:
New questions:
Next steps:"

# 2. Update gaps list
pomera_notes save --title "Research/{Project}/Gaps-{date}" \
  --input_content "Still need to research:
- [gap 1]
- [gap 2]"
```

---

## Quality Checklist

Before concluding research:
- [ ] Multiple independent sources for key claims
- [ ] Recent sources (check dates)
- [ ] Authoritative sources (check credibility)
- [ ] Contradictions acknowledged
- [ ] Gaps documented
- [ ] All sources archived with URLs
- [ ] Synthesis connects to research questions
