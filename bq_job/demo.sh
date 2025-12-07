#!/bin/bash
# 1. Set variables
export PROJECT_ID=n8n-demo-479207
export REGION=us

# 2. Run test queries with labels
python scripts/run_labeled_query.py \
    --project $PROJECT_ID \
    --query "SELECT COUNT(*) as count FROM \`n8n-demo-479207.demo_dataset.demo_table\`" \
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

# 5. Check label coverage (FIXED: use input redirection instead of command substitution)
bq query --use_legacy_sql=false \
    --format=prettyjson \
    --project_id=$PROJECT_ID \
    < queries/label_coverage_report.sql