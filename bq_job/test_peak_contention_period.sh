#!/bin/bash
# Run multiple queries to create some activity
for i in {1..5}; do
  python scripts/run_labeled_query.py \
      --project n8n-demo-479207 \
      --query "SELECT COUNT(*) FROM \`bigquery-public-data.samples.shakespeare\`" \
      --labels "project_id:project-a,team:team-1,environment:prod"
  sleep 2
done