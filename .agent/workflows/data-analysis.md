# Data Analysis Workflow

AI-guided workflow for data analysis projects using SQLite, Python, and MCP tools.

---

## Phase 0: Context Creation (5W1H Framework)

> **AI-GUIDANCE**: Before touching data, establish complete context. This prevents wasted cycles analyzing the wrong things.

### The 5W1H Questions for Data Analysis

| Question | Data Analysis Focus | Example |
|----------|---------------------|---------|
| **WHO** | Who needs this analysis? Who provided the data? | "Marketing team, data from CRM export" |
| **WHAT** | What questions must be answered? What data exists? | "Customer churn predictors, 2 years of transactions" |
| **WHEN** | What time period? When is delivery needed? | "Q3-Q4 2024 data, results by Friday" |
| **WHERE** | Data source location, output destination | "PostgreSQL dump → SQLite → Markdown report" |
| **WHY** | Business decision this supports, success metric | "Reduce churn 10%, identify top 3 risk factors" |
| **HOW** | Analysis methods, tools, validation approach | "SQLite queries → Python viz → statistical tests" |

### Context Template

```yaml
analysis_context:
  who:
    requester: "[stakeholder name/role]"
    data_owner: "[source system/team]"
  what:
    questions: ["[question 1]", "[question 2]"]
    data_description: "[rows, columns, format]"
  when:
    data_period: "[start] to [end]"
    deadline: "[date]"
  where:
    source: "[file/database/API]"
    output: "[format and destination]"
  why:
    decision: "[what this informs]"
    success: "[measurable outcome]"
  how:
    tools: ["SQLite", "Python", "pandas"]
    validation: "[how to verify correctness]"
```

### Example: Filled Context

```yaml
analysis_context:
  who:
    requester: "VP of Sales"
    data_owner: "Salesforce export from RevOps"
  what:
    questions:
      - "Which accounts are at highest churn risk?"
      - "What behaviors predict churn in 30 days?"
    data_description: "50K accounts, 24 months, 45 columns"
  when:
    data_period: "2023-01 to 2024-12"
    deadline: "2025-01-17"
  why:
    decision: "Allocate CSM resources to at-risk accounts"
    success: "Identify 80% of churning accounts 30 days early"
  how:
    tools: ["SQLite", "pandas", "scikit-learn"]
    validation: "Backtest on Q3 2024 known churns"
```

---

## Prioritized Analysis Questions

> **Principle**: Answer foundational questions before diving into complex analysis.

### Question Priority for Data Analysis

| Priority | Question Type | Examples |
|----------|--------------|----------|
| **P1 - Data Quality** | Can I trust this data? | Nulls, duplicates, ranges, freshness |
| **P2 - Descriptive** | What does the data show? | Distributions, counts, trends |
| **P3 - Diagnostic** | Why did this happen? | Correlations, segments, anomalies |
| **P4 - Predictive** | What will happen next? | Models, forecasts (only if P1-P3 done) |

### The Analysis Sequence

```
P1: DATA QUALITY (ALWAYS FIRST)
├── Row count matches expectation?
├── Date range correct?
├── Null patterns acceptable?
├── Duplicates handled?
└── Value ranges valid?

P2: DESCRIPTIVE (SHAPE THE DATA)
├── Key distributions
├── Time-series patterns
├── Category breakdowns
└── Summary statistics

P3: DIAGNOSTIC (EXPLAIN PATTERNS)
├── Correlation analysis
├── Segment comparisons
├── Anomaly investigation
└── Root cause hypotheses

P4: PREDICTIVE (ONLY IF WARRANTED)
├── Feature engineering
├── Model training
├── Validation
└── Business interpretation
```

### Pre-Flight Checklist

Before ANY analysis query, confirm:

- [ ] **WHO** asked for this is documented
- [ ] **WHAT** question this answers is clear
- [ ] **P1 quality checks** have passed
- [ ] **Expected output format** is defined
- [ ] **Validation method** exists

---

## Focused Execution Protocol

> **Principle**: Complete one analysis phase fully before moving to next.

### Single-Task Execution Rules

1. **Finish P1 completely** before any P2 queries
2. **One question per query block** - Don't combine unrelated analysis
3. **Save immediately** - Document each finding as discovered
4. **Validate before proceeding** - Sanity check each result

### Execution Loop

```
┌─────────────────────────────────────┐
│  START: Load 5W1H context           │
├─────────────────────────────────────┤
│  P1: Data Quality Loop              │
│    1. Run quality check query       │
│    2. Document findings             │
│    3. Fix issues or note caveats    │
│    4. Proceed only when confident   │
├─────────────────────────────────────┤
│  P2-P4: Analysis Loop (one at time) │
│    1. State the question            │
│    2. Write and run query           │
│    3. Interpret results             │
│    4. Save to notes                 │
│    5. Check: Answer the WHY yet?    │
├─────────────────────────────────────┤
│  END: Synthesize findings           │
└─────────────────────────────────────┘
```

---

## Principles

1. **Context first** - Complete 5W1H before touching data
2. **Quality before analysis** - P1 checks are mandatory
3. **One question at a time** - Complete each before next
4. **Query first, reason later** - Use SQL to filter/aggregate before AI analysis
5. **Preserve raw data** - Never modify source files; create derived tables
6. **Document transformations** - Save data lineage in pomera notes
7. **Iterate incrementally** - Build understanding step by step

---

## Phase 1: Data Ingestion

### Initial Assessment
```bash
# Understand file structure
ls -la data/
head -n 20 data/sample.csv
wc -l data/*.csv

# Check encoding and format issues
file data/*.csv
```

### Create SQLite Database
```python
import sqlite3
import pandas as pd

# Connect with performance optimizations
conn = sqlite3.connect('analysis.db')
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA synchronous=NORMAL")

# Load data
df = pd.read_csv('data/source.csv')
df.to_sql('raw_data', conn, index=False, if_exists='replace')

# Add indexes for common queries
conn.execute("CREATE INDEX idx_date ON raw_data(date)")
conn.execute("CREATE INDEX idx_category ON raw_data(category)")
```

### Save Schema to Notes
```bash
# Document the schema for future reference
pomera_notes save --title "Data/Schema/{project}-{date}" \
  --input_content "$(sqlite3 analysis.db '.schema')"
```

---

## Phase 2: Exploration

### Quick Overview Queries
```sql
-- Row counts and date range
SELECT COUNT(*), MIN(date), MAX(date) FROM raw_data;

-- Category distribution
SELECT category, COUNT(*) as count
FROM raw_data
GROUP BY category
ORDER BY count DESC
LIMIT 20;

-- Missing value check
SELECT
  SUM(CASE WHEN column1 IS NULL THEN 1 ELSE 0 END) as null_col1,
  SUM(CASE WHEN column2 IS NULL THEN 1 ELSE 0 END) as null_col2
FROM raw_data;
```

### Use Sequential Thinking for Complex Analysis
```
When encountering complex patterns or unclear data:
1. Use sequentialthinking to break down the problem
2. Revise hypotheses as you discover more
3. Document findings in pomera_notes
```

---

## Phase 3: Transformation

### Create Derived Views/Tables
```sql
-- Create clean, analysis-ready view
CREATE VIEW clean_data AS
SELECT
  id,
  COALESCE(value, 0) as value,
  LOWER(TRIM(category)) as category,
  DATE(timestamp) as date
FROM raw_data
WHERE value IS NOT NULL;

-- Aggregation table for dashboards
CREATE TABLE daily_summary AS
SELECT
  date,
  category,
  COUNT(*) as count,
  AVG(value) as avg_value,
  SUM(value) as total_value
FROM clean_data
GROUP BY date, category;
```

### Validate Transformations
```bash
# Compare raw vs clean counts
sqlite3 analysis.db "SELECT COUNT(*) FROM raw_data"
sqlite3 analysis.db "SELECT COUNT(*) FROM clean_data"

# Spot check records
sqlite3 analysis.db "SELECT * FROM clean_data LIMIT 5"
```

---

## Phase 4: Analysis

### Pattern: Focused Context for AI
```sql
-- Instead of dumping all data to AI, create targeted extracts
-- Example: Top anomalies for AI to explain
SELECT *
FROM daily_summary
WHERE avg_value > (SELECT AVG(avg_value) + 2*STDEV(avg_value) FROM daily_summary)
ORDER BY avg_value DESC
LIMIT 20;
```

### Using pomera Tools
```bash
# Extract statistics
pomera_text_stats --text "$(sqlite3 analysis.db 'SELECT * FROM summary')"

# Compare time periods
pomera_list_compare \
  --list_a "$(sqlite3 analysis.db 'SELECT category FROM data WHERE date < \"2024-06\"')" \
  --list_b "$(sqlite3 analysis.db 'SELECT category FROM data WHERE date >= \"2024-06\"')"
```

---

## Phase 5: Reporting

### Export Results
```python
import pandas as pd

conn = sqlite3.connect('analysis.db')

# Export to CSV for sharing
summary = pd.read_sql("SELECT * FROM daily_summary", conn)
summary.to_csv('output/summary.csv', index=False)

# Export to markdown for reports
print(summary.head(20).to_markdown())
```

### Archive Findings
```bash
# Save key insights
pomera_notes save --title "Analysis/{project}/Findings-{date}" \
  --input_content "<key statistics and queries>" \
  --output_content "<conclusions and recommendations>"
```

---

## Best Practices

### DO:
- Start with simple queries, add complexity gradually
- Create indexes before running heavy queries
- Save intermediate results to tables (not just views)
- Use EXPLAIN QUERY PLAN for slow queries
- Back up database before major transformations

### DON'T:
- Load entire tables into AI context
- Modify raw data tables
- Skip data validation steps
- Forget to document transformations
- Run aggregations without indexes

---

## Common Query Patterns

### Time Series
```sql
-- Daily rollup with gaps filled
WITH RECURSIVE dates(date) AS (
  SELECT MIN(date) FROM data
  UNION ALL
  SELECT DATE(date, '+1 day') FROM dates
  WHERE date < (SELECT MAX(date) FROM data)
)
SELECT d.date, COALESCE(t.total, 0) as total
FROM dates d
LEFT JOIN daily_summary t ON d.date = t.date;
```

### Moving Average
```sql
SELECT
  date,
  value,
  AVG(value) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as ma_7
FROM daily_data;
```

### Percentile Ranks
```sql
SELECT
  *,
  PERCENT_RANK() OVER (ORDER BY value) as percentile
FROM data;
```
