# BigQuery CLI Command Explanation

## Command Breakdown

```bash
bq query --use_legacy_sql=false < queries/label_coverage_report.sql
```

### Components

#### 1. `bq`
- **What it is**: BigQuery command-line tool (part of Google Cloud SDK)
- **Purpose**: Allows you to interact with BigQuery from the terminal
- **Prerequisites**: Must have `gcloud` CLI installed and authenticated

#### 2. `query`
- **What it is**: A subcommand of `bq`
- **Purpose**: Executes a SQL query against BigQuery
- **Alternative**: You can also use `bq query` with inline SQL using quotes

#### 3. `--use_legacy_sql=false`
- **What it is**: A flag that specifies which SQL dialect to use
- **Purpose**: 
  - `false` = Use **Standard SQL** (modern, recommended)
  - `true` or omitted = Use **Legacy SQL** (deprecated)
- **Why it matters**: 
  - Standard SQL is more powerful and compatible with SQL standards
  - INFORMATION_SCHEMA views require Standard SQL
  - Most modern BigQuery features use Standard SQL

#### 4. `<` (Input Redirection)
- **What it is**: Shell input redirection operator
- **Purpose**: Reads the SQL query from a file instead of typing it inline
- **How it works**: 
  - `<` takes the contents of the file and feeds it as input to the command
  - Equivalent to: `cat queries/label_coverage_report.sql | bq query --use_legacy_sql=false`

#### 5. `queries/label_coverage_report.sql`
- **What it is**: Path to the SQL file containing the query
- **Purpose**: Contains the SQL query to execute
- **Content**: The label coverage report query that checks how many jobs have required labels

## Alternative Ways to Run the Same Command

### Option 1: Inline SQL (without file)
```bash
bq query --use_legacy_sql=false "
SELECT COUNT(*) AS total_jobs
FROM \`region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT\`
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
"
```

### Option 2: Using cat (explicit)
```bash
cat queries/label_coverage_report.sql | bq query --use_legacy_sql=false
```

### Option 3: Using here-string
```bash
bq query --use_legacy_sql=false <<< "$(cat queries/label_coverage_report.sql)"
```

### Option 4: Specify project explicitly
```bash
bq query --use_legacy_sql=false --project_id=your-project-id < queries/label_coverage_report.sql
```

## What the Query Does

The `label_coverage_report.sql` file contains a query that:
- Counts total jobs in the last 7 days
- Checks how many jobs have the required labels (`project_id`, `team`)
- Calculates percentage of jobs with labels
- Helps monitor adoption of the labeling strategy

## Common Flags for `bq query`

| Flag | Description | Example |
|------|-------------|---------|
| `--use_legacy_sql` | Use Legacy SQL (default: true) | `--use_legacy_sql=false` |
| `--project_id` | Specify project | `--project_id=my-project` |
| `--format` | Output format | `--format=prettyjson`, `--format=csv` |
| `--max_rows` | Limit result rows | `--max_rows=100` |
| `--dry_run` | Validate without running | `--dry_run` |
| `--label` | Add job label | `--label=key:value` |
| `--location` | Specify region | `--location=us` |

## Example with Additional Flags

```bash
# Run query with labels, format as JSON, limit to 10 rows
bq query \
  --use_legacy_sql=false \
  --project_id=my-project \
  --format=prettyjson \
  --max_rows=10 \
  --label=analysis:coverage-report \
  < queries/label_coverage_report.sql
```

## Troubleshooting

### Error: "Command not found: bq"
**Solution**: Install Google Cloud SDK
```bash
# macOS
brew install google-cloud-sdk

# Or download from: https://cloud.google.com/sdk/docs/install
```

### Error: "Access Denied"
**Solution**: Authenticate and set project
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Error: "Table not found"
**Solution**: Check region and project
```bash
# Verify region in query matches your BigQuery region
# Check project: gcloud config get-value project
```

## Related Commands

```bash
# List datasets
bq ls

# Show dataset
bq show dataset_name

# Show table
bq show dataset_name.table_name

# List jobs
bq ls -j

# Show job details
bq show -j JOB_ID
```



