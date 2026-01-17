---
description:
---

# Writing Hooks for Hobby Pages

> **AI-GUIDANCE**: Use this guide when creating or updating hook text for hobby landing pages.

---

## Overview

A **hook** is the opening sentence(s) that grab attention and compel visitors to keep reading. For hobby pages, hooks should connect emotionally with the reader while introducing the hobby's core value.

---

## Legendary Copywriters: Top Techniques

### David Ogilvy — "Father of Advertising"
> "On average, five times as many people read the headline as read the body copy."

**Key Rules:**
1. **Headlines = 80% of the work** — If your headline fails, everything fails
2. **Promise a benefit** — Tell readers what's in it for them
3. **Be instantly comprehensible** — No cleverness that confuses
4. **Write 20 headlines** — Then test to find the winner
5. **First paragraph must "grab"** — Make it impossible to stop reading

**Power Words That Work:**
- "How to..." | "Introducing..." | "Amazing..." | "Finally..."

---

### Gary Halbert — "Prince of Print"
> "Curiosity is the single most persuasive sales technique."

**Key Rules:**
1. **Create an "itch"** — Leave something incomplete so readers MUST continue
2. **Address readers by name** — Make copy feel personal, not like advertising
3. **AIDA always works** — Attention → Interest → Desire → Action
4. **Eye relief matters** — Short sentences, short paragraphs, easy flow
5. **"A-pile vs B-pile"** — Make your content feel personal, not promotional

**Famous Hook:**
> "The Amazing Money-Making Secret Of A Desperate Nerd From Ohio!"

---

### Eugene Schwartz — "Breakthrough Advertising"
> "Copy cannot create desire. It can only channel existing desire."

**Key Rules:**
1. **80% research, 20% writing** — Know your audience deeply
2. **Match market awareness** — Different hooks for different awareness levels
3. **Write to the "chimpanzee brain"** — Simple, clear, direct
4. **Show results, not stuff** — Focus on transformation, not features
5. **Listen like crazy** — Understand hidden emotions and desires

**Headline Formula:**
> Proof + Pain + Benefit = Compelling Hook

Example: "Burn Disease Out of Your Body Using Nothing More Than the Palm of Your Hand!"

---

### Joe Sugarman — "The Slippery Slide"
> "The sole purpose of the first sentence is to get you to read the second sentence."

**Key Rules:**
1. **Slippery slide effect** — Each sentence pulls you to the next
2. **Get early agreement** — Start with truths readers will nod to
3. **Sell a concept, not a product** — Position around a bigger idea
4. **Emotion + Logic** — Hook with feeling, justify with reason
5. **Anticipate objections** — Answer concerns before they arise

**Immediate Engagement Technique:**
> Get readers saying "yes" early. The more yeses, the more likely they'll say yes to your offer.

---

### Quick Reference: The Masters' Core Principles

| Master | Core Principle | Apply To Hooks |
|--------|---------------|----------------|
| **Ogilvy** | Research first, promise benefits | Lead with what reader gains |
| **Halbert** | Curiosity creates compulsion | Leave something unfinished |
| **Schwartz** | Channel existing desire | Mirror reader's current feelings |
| **Sugarman** | Make reading effortless | Each word earns the next |

---

## Copywriting Frameworks

### 1. PAS (Problem → Agitate → Solution)

**Best for:** Hobbies that solve a pain point

```
Problem:  "Feeling disconnected from nature?"
Agitate:  "Screen time and city life drain your energy."
Solution: "Hiking reconnects you to wild spaces and yourself."
```

**Hook Examples:**
- **Hiking**: "Stuck behind screens all day? The trail is calling."
- **Nutrition**: "Tired of diet confusion? One meal philosophy, endless energy."
- **Systems**: "Drowning in manual tasks? Automate the boring stuff."

---

### 2. AIDA (Attention → Interest → Desire → Action)

**Best for:** Inspiring hobbies with aspirational appeal

```
Attention: Shocking stat or bold claim
Interest:  How it works/what it offers
Desire:    The transformation promised
Action:    What to do next
```

**Hook Examples:**
- **Cycling**: "100 million Americans ride. Here's why I'm one of them."
- **Archery**: "One arrow. One breath. Total focus."
- **Markets**: "The stock market moves $200B daily. Want in?"

---

## Hook Techniques

### Technique Cheat Sheet

| Technique | Example | Best For |
|-----------|---------|----------|
| **Question** | "Ever wonder why...?" | Building curiosity |
| **Bold Statement** | "This changed everything." | Making a claim |
| **Statistic** | "2.2B people hike yearly" | Adding credibility |
| **Pain Point** | "Tired of X?" | Addressing problems |
| **Curiosity Gap** | "Here's what nobody tells you..." | Creating intrigue |
| **Story** | "It started with..." | Building connection |

---

## Hook Formulas

### Formula 1: Question + Value Prop
```
"{Provocative question}? {Hobby} offers {core benefit}."
```
- Hiking: "Need to escape? Trails offer solitude and adventure."

### Formula 2: Problem + Twist
```
"Everyone says {common advice}. Here's what actually works."
```
- Nutrition: "Everyone says 'eat less.' Here's what actually works."

### Formula 3: Stat + Personal Angle
```
"{Impressive number} {activity}. Here's why I'm one of them."
```
- Audiobooks: "500M audiobook listeners worldwide. Here's why I listen daily."

### Formula 4: Benefit-First
```
"{Benefit} + {Benefit} + {Benefit}. That's {hobby}."
```
- Cycling: "Fitness. Freedom. Flow. That's cycling."

### Formula 5: Before/After Contrast
```
"I used to {old state}. Now I {new state}."
```
- Archery: "I used to rush everything. Now I wait for the perfect release."

---

## Writing Checklist

- [ ] **Under 20 words** — Keep it punchy
- [ ] **Uses "you" or implies reader** — Makes it personal
- [ ] **Creates curiosity** — Why keep reading?
- [ ] **Connects to benefit** — What's in it for them?
- [ ] **Matches hobby tone** — Active hobbies = active voice

---

## Anti-Patterns (Avoid These)

❌ **Too generic**: "Welcome to my hiking page"
❌ **Too salesy**: "Buy now for amazing results!"
❌ **Too long**: Hooks over 2 sentences lose impact
❌ **Jargon-heavy**: "Optimize your nutritional macros"
❌ **No emotion**: Flat, factual statements without energy



# README files and larger content that comes after the HOOK

## Consolidated Research

### 2-3 Strategic Searches Only

**Instead of** 5-10 separate searches, execute **maximum 3**:

| Search | Query Pattern | What to Extract |
|--------|---------------|-----------------|
| **Search 1** | `[topic] complete guide` OR `[topic] ultimate guide` | Top 3 ranking URLs, H2 structures, word counts |
| **Search 2** | `[topic] tips` OR `how to [topic]` | Question keywords, People Also Ask, related searches |
| **Search 3** (if needed) | `[topic] statistics [year]` | Pre-collect stats for later use |

### Extraction Protocol

After each search, extract and store in context:
- Primary keyword candidate (appears in top titles)
- 10 secondary keywords (from titles, headings, related searches)
- 5 question-based keywords
- Top 3 competitor URLs
- Any statistics with source URLs

### Commands

```bash
# General topic research
python tools/web_search.py "[topic] complete guide" --engine brave --count 10

# Question-based keywords
python tools/web_search.py "how to [topic]" --engine brave --count 10

# Code/library documentation (Context7)
python tools/web_search.py "[technical topic]" --engine context7

# Google for complex queries (100/day limit)
python tools/web_search.py "[complex query]" --engine google
```


## Tone Suggestions

### Voice Profile

| Element | Style | Example |
|---------|-------|---------|
| **Tone** | Direct, curious, practical | "Here's what actually works." |
| **Sentences** | Short, punchy | Max 20 words per sentence |
| **Humor** | Self-deprecating | "I learned this the hard way..." |
| **Opening** | Personal anecdote or bold claim | "I almost quit cycling last year." |
| **Closing** | Actionable takeaway + question | "What's your experience with...?" |
| **Register** | Informal (tú/du not usted/Sie) | Direct "you" address |

### Hook Formulas

| Type | Formula | Example |
|------|---------|---------|
| **Curiosity Gap** | "Most people think X, but..." | "Most people think bike fit is about comfort. It's not." |
| **Bold Claim** | "[Controversial statement]. Here's why." | "You don't need expensive equipment. Here's why." |
| **Personal Story** | "I [action] and [result]..." | "I rode 5,000 miles last year and learned one thing..." |
| **Direct Question** | "Have you ever wondered...?" | "Have you ever wondered why your back hurts after riding?" |

## Decision Shortcuts

When uncertain, use these defaults:

| Decision | Default |
|----------|---------|
| Word count unclear | 1,500-2,000 words |
| Audience unclear | Informed beginner |
| Tone unclear | Direct, conversational |
| Number of H2 sections | 5-7 |
| Statistics needed | 3-5 data points |
| Internal links | 2-3 |
| External links | 2-3 |

## Hard Limits (Enforce These)

| Activity | Maximum |
|----------|---------|
| Brief clarification | 1 exchange |
| Keyword research searches | 3 searches |
| Competitor articles analyzed | 3 articles |
| Time per competitor | 3 minutes |
| Outline revisions | 1 revision |
| Meta element revisions | 1 minor tweak at end |



### Outline Generation - Intent-Based Templates

Match search intent to template:

| Search Intent | Template Structure |
|---------------|-------------------|
| **Informational** | Intro → Definition → Context → Key Points (3-5 H2s) → Examples → Conclusion |
| **How-To** | Intro → Prerequisites → Steps (numbered H2s) → Tips → FAQ → Conclusion |
| **Comparison** | Intro → Criteria → Option A/B/C → Table → Verdict → Conclusion |
| **Listicle** | Intro → Items 1-N (H2 each) → Honorable Mentions → Conclusion |
| **Problem-Solution** | Intro → Problem → Why It Matters → Solutions (H2s) → Implementation → Conclusion |

### Keyword Mapping (One-Time)

| Keyword Type | Placement Rule |
|--------------|----------------|
| Primary keyword | Title, Intro (first 100 words), one H2, Conclusion |
| Top 3 secondary | One per major body section H2 |
| Question keywords | Use as H2 or H3 subheadings directly |
| LSI terms | Sprinkle naturally; no forced placement |

### Meta Elements (Draft Once)

```yaml
meta:
  title: "[Primary Keyword]: [Value Proposition]"  # 50-60 chars
  description: "[Benefit/Hook]. Learn [what they'll get]."  # 150-160 chars
  slug: "primary-keyword-simplified"
```

**Do not revisit** these until final validation.

---
## Competitor Analysis

### Rapid Skim of Top 3 Only

**Time limit:** 3 minutes per competitor article

For each competitor URL, extract ONLY:

```yaml
competitor:
  url: ""
  h2_headings: []
  word_count: 0
  format: "listicle | guide | tutorial | comparison"
  unique_insight: ""
  weakness_or_gap: ""
```

### Aggregation Rules

| Coverage | Action |
|----------|--------|
| Subtopic in 2+ competitors | **MUST INCLUDE** |
| Subtopic in 1 competitor | Consider including |
| Gap in all 3 | **OPPORTUNITY** (prioritize) |

---
