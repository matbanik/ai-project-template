# Data Analysis Workflow

AI-guided workflow for data analysis projects using SQLite, Python, and MCP tools.

## Principles

1. **Query first, reason later** - Use SQL to filter/aggregate before AI analysis
2. **Preserve raw data** - Never modify source files; create derived tables
3. **Document transformations** - Save data lineage in pomera notes
4. **Iterate incrementally** - Build understanding step by step

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
