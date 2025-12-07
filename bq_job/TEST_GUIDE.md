# BigQuery Job Labels POC - Test Guide

This guide walks you through testing the BigQuery Job Labels POC to demonstrate slot usage tracking and analysis.

## Prerequisites

1. **GCP Project Setup**
   - Access to a GCP project with BigQuery enabled
   - BigQuery API enabled
   - **Required IAM permissions**:
     - `roles/bigquery.jobUser` (minimum for creating jobs and viewing own jobs)
     - `roles/bigquery.admin` (for querying INFORMATION_SCHEMA.JOBS_BY_PROJECT)
     - Or custom role with `bigquery.jobs.list` and `bigquery.jobs.get` permissions
   - **Note**: If you get "Access Denied" errors, see `TROUBLESHOOTING.md`

2. **Python Environment**
   ```bash
   pip install -r requirements.txt
   ```

3. **Authentication**
   ```bash
   gcloud auth application-default login
   # Or set GOOGLE_APPLICATION_CREDENTIALS environment variable
   ```

4. **BigQuery Dataset**
   - Create a test dataset or use an existing one
   - Ensure you have a table to query (or use public datasets)

## Test Scenarios

### Test 1: Run a Single Query with Labels

**Objective**: Verify that labels can be applied to a query and are visible in INFORMATION_SCHEMA.

**Steps**:

1. Run a simple query with labels:
   ```bash
   python scripts/run_labeled_query.py \
       --project YOUR_PROJECT_ID \
       --query "SELECT 1 as test_value" \
       --labels "project_id:test-project,team:data-engineering,environment:dev"
   ```

2. Verify the output shows:
   - Job ID
   - Total slot milliseconds
   - Labels applied

3. Query INFORMATION_SCHEMA to verify labels:
   ```sql
   SELECT
     job_id,
     creation_time,
     (
       SELECT value 
       FROM UNNEST(labels) 
       WHERE key = 'project_id'
     ) AS project_id,
     (
       SELECT value 
       FROM UNNEST(labels) 
       WHERE key = 'team'
     ) AS team,
     total_slot_ms
   FROM
     `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
   WHERE
     job_id = 'YOUR_JOB_ID'
   ```

**Expected Result**: Labels should appear in the query results.

### Test 2: Run Multiple Queries with Labels

**Objective**: Demonstrate batch labeling and verify slot usage aggregation.

**Steps**:

1. Create a queries file (`test_queries.txt`):
   ```
   # Query 1
   SELECT COUNT(*) as count FROM `bigquery-public-data.samples.shakespeare`
   
   # Query 2
   SELECT word, SUM(word_count) as total
   FROM `bigquery-public-data.samples.shakespeare`
   GROUP BY word
   ORDER BY total DESC
   LIMIT 10
   ```

2. Run batch queries:
   ```bash
   python scripts/batch_labeled_queries.py \
       --project YOUR_PROJECT_ID \
       --queries-file test_queries.txt \
       --labels "project_id:test-project,team:data-engineering,environment:dev,workflow:test-batch"
   ```

3. Verify all queries completed with labels applied.

**Expected Result**: All queries should complete successfully with consistent labels.

### Test 3: Analyze Slot Usage by Labels

**Objective**: Use INFORMATION_SCHEMA to analyze slot usage grouped by labels.

**Steps**:

1. Run several queries with different label combinations:
   ```bash
   # Project A queries
   python scripts/run_labeled_query.py \
       --project YOUR_PROJECT_ID \
       --query "SELECT COUNT(*) FROM \`bigquery-public-data.samples.shakespeare\`" \
       --labels "project_id:project-a,team:team-1,environment:prod"
   
   python scripts/run_labeled_query.py \
       --project YOUR_PROJECT_ID \
       --query "SELECT word FROM \`bigquery-public-data.samples.shakespeare\` LIMIT 100" \
       --labels "project_id:project-a,team:team-1,environment:prod"
   
   # Project B queries
   python scripts/run_labeled_query.py \
       --project YOUR_PROJECT_ID \
       --query "SELECT COUNT(*) FROM \`bigquery-public-data.samples.shakespeare\`" \
       --labels "project_id:project-b,team:team-2,environment:prod"
   ```

2. Wait a few minutes for jobs to appear in INFORMATION_SCHEMA.

3. Run the analysis query:
   ```bash
   bq query --use_legacy_sql=false < queries/analyze_slot_usage_by_labels.sql
   ```

   Or use the monitoring script:
   ```bash
   python scripts/monitor_slot_usage.py \
       --project YOUR_PROJECT_ID \
       --region us \
       --days 1 \
       --group-by project_id,team
   ```

**Expected Result**: 
- Slot usage should be grouped by project_id and team
- You should see different slot consumption for different projects/teams

### Test 4: Find Peak Contention Periods

**Objective**: Identify time periods with highest slot usage.

**Steps**:

1. Run queries at different times (or simulate with different timestamps):
   ```bash
   # Run multiple queries to create some activity
   for i in {1..5}; do
     python scripts/run_labeled_query.py \
         --project YOUR_PROJECT_ID \
         --query "SELECT COUNT(*) FROM \`bigquery-public-data.samples.shakespeare\`" \
         --labels "project_id:project-a,team:team-1,environment:prod"
     sleep 2
   done
   ```

2. Run the peak contention query:
   ```bash
   bq query --use_legacy_sql=false < queries/find_peak_contention.sql
   ```

**Expected Result**: 
- Results should show hourly aggregation
- Top projects by slot usage per hour should be identified

### Test 5: Label Coverage Report

**Objective**: Verify label adoption and compliance.

**Steps**:

1. Run queries with and without labels:
   ```bash
   # With labels
   python scripts/run_labeled_query.py \
       --project YOUR_PROJECT_ID \
       --query "SELECT 1" \
       --labels "project_id:test,team:test"
   
   # Without labels (using bq CLI directly)
   bq query --use_legacy_sql=false "SELECT 1"
   ```

2. Run the coverage report:
   ```bash
   bq query --use_legacy_sql=false < queries/label_coverage_report.sql
   ```

**Expected Result**: 
- Should show percentage of jobs with required labels
- Helps track adoption of labeling strategy

### Test 6: Project-Level Analysis

**Objective**: Get comprehensive statistics per project.

**Steps**:

1. Run queries for different projects:
   ```bash
   python scripts/run_labeled_query.py \
       --project YOUR_PROJECT_ID \
       --query "SELECT COUNT(*) FROM \`bigquery-public-data.samples.shakespeare\`" \
       --labels "project_id:analytics,team:data-engineering,environment:prod"
   
   python scripts/run_labeled_query.py \
       --project YOUR_PROJECT_ID \
       --query "SELECT word FROM \`bigquery-public-data.samples.shakespeare\` LIMIT 1000" \
       --labels "project_id:analytics,team:data-engineering,environment:prod"
   ```

2. Run project-level analysis:
   ```bash
   bq query --use_legacy_sql=false < queries/project_level_analysis.sql
   ```

**Expected Result**: 
- Comprehensive statistics per project
- Percentiles, averages, top jobs

## Validation Checklist

After running the tests, verify:

- [ ] Labels are applied correctly to jobs
- [ ] Labels appear in INFORMATION_SCHEMA queries
- [ ] Slot usage can be aggregated by labels
- [ ] Different projects/teams show different slot usage
- [ ] Peak contention periods can be identified
- [ ] Label coverage can be monitored
- [ ] Project-level statistics are accurate

## Troubleshooting

### Issue: Labels not appearing in INFORMATION_SCHEMA

**Possible Causes**:
- Jobs are too recent (wait a few minutes)
- Wrong region specified in query
- Labels not applied correctly

**Solution**:
- Wait 2-5 minutes after job completion
- Verify region matches your BigQuery region
- Check job details in BigQuery console

### Issue: Permission errors

**Possible Causes**:
- Missing IAM permissions
- Wrong project ID

**Solution**:
- Ensure you have `bigquery.jobs.create` permission
- Verify project ID is correct
- Check authentication: `gcloud auth list`

### Issue: Query errors in INFORMATION_SCHEMA

**Possible Causes**:
- Wrong region specified
- Table doesn't exist
- Syntax errors
- **Missing IAM permissions** (most common)

**Solution**:
- Use correct region (e.g., `region-us`, `region-europe-west1`)
- Verify INFORMATION_SCHEMA access
- Check SQL syntax
- **For permission errors**: See `TROUBLESHOOTING.md` for detailed solutions
  - Try `JOBS_BY_USER` instead of `JOBS_BY_PROJECT` (lower permission requirements)
  - Request `roles/bigquery.jobUser` or `roles/bigquery.admin` from your administrator
  - Use a different project where you have permissions

## Next Steps

1. **Integrate into Production**
   - Update your data pipeline code to apply labels
   - Set up scheduled queries for monitoring
   - Create dashboards using the analysis queries

2. **Customize for Your Organization**
   - Adjust label keys/values in LABELING_STRATEGY.md
   - Modify SQL queries for your specific needs
   - Add additional analysis queries

3. **Set Up Monitoring**
   - Schedule daily/weekly reports
   - Create alerts for unusual slot usage
   - Track label adoption over time

## Demo Script

For a complete demo, run this sequence:

```bash
# 1. Set variables
export PROJECT_ID=your-project-id
export REGION=us

# 2. Run test queries with labels
python scripts/run_labeled_query.py \
    --project $PROJECT_ID \
    --query "SELECT COUNT(*) as count FROM \`bigquery-public-data.samples.shakespeare\`" \
    --labels "project_id:demo-project,team:demo-team,environment:dev"

# 3. Wait a few minutes
echo "Waiting for jobs to appear in INFORMATION_SCHEMA..."
sleep 120

# 4. Analyze slot usage
python scripts/monitor_slot_usage.py \
    --project $PROJECT_ID \
    --region $REGION \
    --days 1 \
    --group-by project_id,team

# 5. Check label coverage
bq query --use_legacy_sql=false \
    --replace \
    --format=prettyjson \
    "$(cat queries/label_coverage_report.sql)"
```

This demonstrates the complete workflow from applying labels to analyzing slot usage.

