---
description: Extract and validate SEO keywords from existing content
---

# Keyword Research from Content Guide

This guide explains how to extract keywords from your existing content (PDFs, markdown files) and validate them using web search APIs to prioritize which keywords to target in blog posts.

## Overview

The workflow has three phases:
1. **Content Scanning** - AI analyzes your files and extracts keyword candidates
2. **Keyword Validation** - APIs check search traction and competition
3. **Prioritized Output** - Receive a ranked list with recommendations

---

## Phase 1: Content Scanning (AI-Assisted)

### What the AI Does

When you point to your PDFs and MD files, the AI will:

1. **Read all your content** - PDFs, markdown files in folders like `content-docs/cycling/`
2. **Extract key concepts** - Topics, phrases, product names, techniques mentioned
3. **Identify candidate keywords** - Using word frequency analysis and phrase extraction
4. **Create a keyword candidate list** - Organized by topic/theme

### MCP Tools Used

- `read_file` - For markdown files
- `pomera_extract` - Extract patterns and URLs
- `pomera_text_stats` - Analyze word frequency
- `pomera_word_frequency` - Find commonly used terms
- `pomera_markdown` - Extract headers and links

---

## Phase 2: Keyword Validation (API-Driven)

### For Each Candidate Keyword

The AI will:

1. **Check search traction** using `web_search.py` (Brave/Google)
   - Search volume indicators
   - Current top results analysis

2. **Find related searches** using SERP Keyword Extractor (ValueSERP)
   - People Also Ask questions
   - Related keyword variations

3. **Assess competition** by analyzing top results
   - Domain authority of ranking sites
   - Content depth and quality

4. **Compile a prioritized list** with recommendations

### APIs Used

| API | Purpose | Cost |
|-----|---------|------|
| **Brave Search** | Initial keyword validation | 2000 free/month |
| **Google Search** | Secondary validation | 100 free/day |
| **ValueSERP** | Related searches + PAA (optional external tool) | Varies |
| **Context7** | Technical/code topics (optional MCP) | Varies |

---

## Phase 3: Prioritized Output

### Example Output Format

```markdown
# Keyword Analysis: [Topic Name]

## High Priority Keywords (Target First)
| Keyword | Search Indicators | Competition | Your Advantage |
|---------|-------------------|-------------|----------------|
| "road bike fitting guide" | High SERP activity | Medium | Your fit data PDF |
| "bike fit measurements" | Multiple PAA questions | Medium-Low | Detailed measurements |

## Medium Priority Keywords
| Keyword | Search Indicators | Competition | Notes |
|---------|-------------------|-------------|-------|
| "cycling ergonomics" | Moderate interest | Medium | Related to health angle |
| "bike saddle height calculator" | Good long-tail | Low | Opportunity for tool |

## Long-tail Opportunities (Low Competition)
- "how to measure saddle height for road bike"
- "bike fit for tall riders over 6 feet"
- "professional bike fitting vs DIY fitting"
- "road bike reach measurement guide"

## Content Gap Analysis
**What competitors cover that you don't yet:**
- Interactive fitting calculators
- Video demonstrations
- Before/after case studies

## Recommended Blog Post Structure

### Blog Post #1: "Complete Road Bike Fitting Guide"
**Primary Keyword:** road bike fitting guide
**Target Difficulty:** Medium

1. **H1:** Complete Road Bike Fitting Guide for Beginners
2. **H2:** Why Proper Bike Fit Matters (answer PAA: "why is bike fit important")
3. **H2:** Essential Bike Fit Measurements (use your PDF data)
4. **H2:** Step-by-Step DIY Fitting Process
5. **H2:** When to Get Professional Bike Fitting
6. **H2:** FAQ Section (from PAA questions)

### Blog Post #2: "Bike Fit Measurements Explained"
**Primary Keyword:** bike fit measurements
**Target Difficulty:** Medium-Low

1. **H1:** Understanding Bike Fit Measurements: A Complete Guide
2. **H2:** Key Measurements Every Cyclist Should Know
3. **H2:** How to Take Accurate Bike Fit Measurements (your advantage)
4. **H2:** Common Bike Fit Mistakes to Avoid
5. **H2:** Tools Needed for DIY Bike Fitting
```

---

## How to Start This Process

### Option A: Single Topic Focus
```
"Analyze my cycling content in content-docs/cycling/ and find the best keywords for blog posts"
```

**What happens:**
- AI reads all files in that folder
- Extracts cycling-specific keywords
- Validates with search APIs
- Returns prioritized list

### Option B: Specific Files
```
"Read content-docs/cycling/BLOG - Bike Review Research and Summary.md and
content-docs/cycling/BLOG - Mat_Banik_fit_data.pdf and extract keyword opportunities"
```

**What happens:**
- AI focuses on just those files
- More targeted keyword extraction
- Faster results for specific content

### Option C: Full Content Audit
```
"Scan all my content-docs and identify the top 20 keywords I should prioritize
across all topics (cycling, nutrition, markets, etc.)"
```

**What happens:**
- Comprehensive analysis across all topics
- Cross-topic keyword opportunities
- Broader strategic view

---

## Workflow Commands

### Step 1: Extract Keywords from Content
```
Please analyze content-docs/cycling/ and extract potential keywords
```

### Step 2: Validate Keywords
```
For these keywords [list], check search volume and competition using Brave Search
```

### Step 3: Get Related Searches
```
For the top 5 keywords, find related searches and PAA questions using ValueSERP
```

### Step 4: Create Blog Structure
```
Based on the keyword analysis, suggest 3 blog post outlines with H1/H2 structure
```

---

## Expected Timeline

| Phase | Duration | Depends On |
|-------|----------|------------|
| Content Scanning | 5-10 minutes | Number of files |
| Keyword Validation | 10-15 minutes | API rate limits |
| Related Search Extraction | 5 minutes | ValueSERP queries |
| Report Generation | 5 minutes | Analysis complexity |
| **Total** | **25-35 minutes** | For typical topic |

---

## Tips for Best Results

### 1. Organize Your Content First
- Group related docs in topic folders
- Name files descriptively
- Include research notes and drafts

### 2. Be Specific About Your Goals
Instead of: "Find keywords"
Better: "Find keywords for beginner cyclists interested in bike fitting"

### 3. Leverage Your Unique Data
- Fitness measurements
- Product reviews
- Personal experiences
- Research compilations

### 4. Consider Your Existing Rankings
If you have Google Search Console set up, mention:
- "Also check what I currently rank for positions 4-20"
- Optimization opportunities for existing content

---

## Advanced: Competitive Analysis

### Ask for Competitor Comparison
```
"Compare my cycling fitting content against the top 3 ranking sites for
'road bike fitting guide' and identify content gaps"
```

**What you get:**
- What competitors include that you don't
- Unique angles you can take
- Length/depth requirements
- Media opportunities (images, videos, tools)

---

## Saving Results

### Recommended Organization
```
content-docs/seo/
├── [topic-name]/
│   ├── keyword-analysis-[date].md
│   ├── related-searches-[date].csv
│   ├── competitor-analysis-[date].md
│   └── blog-outlines-[date].md
```

### Version Control
- Save each analysis with date stamp
- Track keyword performance over time
- Update quarterly for trending topics

---

## Integration with Blog Writing Workflow

### Before Writing (Planning Phase)
1. Run keyword analysis on your research docs
2. Get prioritized keyword list
3. Choose primary + secondary keywords
4. Get blog post structure recommendation

### During Writing
1. Use primary keyword in H1
2. Include related keywords in H2s
3. Answer PAA questions in FAQ section
4. Naturally incorporate long-tail variations

### After Publishing
1. Save keyword research to `content-docs/seo/[post-slug]/`
2. Track rankings monthly using GSC tools
3. Update content based on new keyword opportunities

---

## Troubleshooting

### "No good keywords found"
**Reasons:**
- Content too niche (very specialized topics)
- Content needs more depth
- Keywords exist but competition is too high

**Solutions:**
- Try longer, more specific phrases
- Look for question-based keywords
- Target "how to" queries

### "Keywords have high competition"
**Solutions:**
- Target long-tail variations
- Focus on your unique angle
- Build up with easier keywords first
- Look for "people also ask" opportunities

### "API rate limits reached"
**Solutions:**
- Spread keyword validation over multiple days
- Prioritize most important keywords first
- Use free tier strategically (Brave: 2000/month, Google: 100/day)

---

## Quick Reference

### Available Commands
```bash
# Keyword extraction from content
"Extract keywords from content-docs/[topic]/"

# Validate keywords with search
"Check search volume for: [keyword1, keyword2, keyword3]"

# Get related searches
"Find related searches for: [keyword]"

# Full workflow
"Analyze content-docs/[topic]/, validate keywords, and create blog outlines"
```

### MCP Tools Reference
- `pomera_extract` - Pattern extraction
- `pomera_text_stats` - Content statistics
- `pomera_word_frequency` - Term frequency
- `pomera_markdown` - Structure extraction
- `pomera_notes` - Save research findings

### API Tools Reference
- `web_search.py` - Brave/Google/Context7 search
- SERP Keyword Extractor (Streamlit) - ValueSERP integration
- Question Extraction (GSC) - Find questions from your data

---

## Next Steps

1. Choose a topic to start with (e.g., cycling, nutrition, markets)
2. Point to the folder or files to analyze
3. Review the keyword analysis output
4. Select keywords to target in blog posts
5. Use the recommended blog structure
6. Track performance and iterate

Ready to start? Just tell me which content to analyze!
