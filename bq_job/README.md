# BigQuery Job Labels POC - Slot Contention Analysis

## Overview

This POC demonstrates how to use BigQuery Job Labels to track and analyze slot usage/contention across different projects. Job Labels allow you to tag queries with metadata (e.g., project_id, team, environment) and then filter and analyze slot consumption using INFORMATION_SCHEMA.

## Problem Statement

We are currently facing challenges in analyzing BigQuery slot contention because we cannot easily distinguish query usage across different projects. This lack of visibility makes it hard to identify which specific jobs are consuming the most resources during peak times.

## Solution

Use BigQuery Job Labels to tag queries with metadata, enabling:
- Per-project slot usage tracking
- Team-level resource attribution
- Environment-based filtering (dev, staging, prod)
- Bottleneck identification during peak times

## Directory Structure

```
bq_job/
├── README.md                          # This file
├── DOCUMENTATION.md                   # Comprehensive documentation on Job Labels
├── LABELING_STRATEGY.md               # Proposed standard labeling strategy
├── TEST_GUIDE.md                      # Step-by-step testing guide
├── requirements.txt                   # Python dependencies
├── queries/
│   ├── analyze_slot_usage_by_labels.sql
│   ├── analyze_slot_usage_by_labels_user.sql  # User-specific (lower permissions)
│   ├── find_peak_contention.sql
│   ├── project_level_analysis.sql
│   ├── team_resource_attribution.sql
│   ├── label_coverage_report.sql
│   └── label_value_distribution.sql
├── scripts/
│   ├── run_labeled_query.py          # Example: Run query with labels
│   ├── batch_labeled_queries.py     # Example: Run multiple labeled queries
│   └── monitor_slot_usage.py         # Monitor slot usage by labels
└── examples/
    └── sample_queries_with_labels.sql
```

## Quick Start

### 1. Review Documentation
Start with `DOCUMENTATION.md` to understand how Job Labels work and how to query them.

### 2. Review Labeling Strategy
Check `LABELING_STRATEGY.md` for the proposed standard labeling approach.

### 3. Run Test Queries
```bash
# Set your project
export GCP_PROJECT=your-project-id

# Run a labeled query
python scripts/run_labeled_query.py \
  --project $GCP_PROJECT \
  --query "SELECT 1" \
  --labels project_id:analytics,team:data-engineering,environment:prod
```

### 4. Analyze Slot Usage
```bash
# Run analysis queries
bq query --use_legacy_sql=false < queries/analyze_slot_usage_by_labels.sql
```

## Key Features

- ✅ Comprehensive documentation on Job Labels
- ✅ SQL queries for slot usage analysis via INFORMATION_SCHEMA
- ✅ Python scripts demonstrating label application
- ✅ Proposed standard labeling strategy
- ✅ Test examples and use cases

## Acceptance Criteria Status

- [x] Documentation/report created explaining Job Labels usage
- [x] Test queries with labels applied
- [x] Slot usage analysis via INFORMATION_SCHEMA
- [x] Standard labeling strategy proposed

## Testing

See `TEST_GUIDE.md` for comprehensive testing instructions and validation steps.

## Troubleshooting

If you encounter "Access Denied" errors when querying INFORMATION_SCHEMA, see:
- **`TROUBLESHOOTING.md`** - Detailed troubleshooting guide
- **`PERMISSION_ALTERNATIVES.md`** - Alternative approaches when INFORMATION_SCHEMA is unavailable
- **`QUICK_FIX.md`** - Quick reference for permission issues

Common fixes:
- Use `JOBS_BY_USER` instead of `JOBS_BY_PROJECT` (lower permission requirements)
- Request `roles/bigquery.jobUser` or `roles/bigquery.admin` from your administrator
- Use the user-specific query: `queries/analyze_slot_usage_by_labels_user.sql`
- Use BigQuery Console to view jobs (may work even if SQL doesn't)
- Use the API approach: `scripts/get_jobs_via_api.py` (different permission model)

## Next Steps

1. Review and customize the labeling strategy for your organization
2. Test with your actual BigQuery datasets (see `TEST_GUIDE.md`)
3. Integrate label application into your data pipeline code
4. Set up monitoring dashboards using the provided SQL queries
5. Set up scheduled queries for regular slot usage analysis

## Additional Resources

- **Documentation**: `DOCUMENTATION.md` - Complete guide on Job Labels
- **Labeling Strategy**: `LABELING_STRATEGY.md` - Standard labeling approach
- **Test Guide**: `TEST_GUIDE.md` - Step-by-step testing instructions
- **Troubleshooting**: `TROUBLESHOOTING.md` - Common issues and solutions
- **Example Queries**: `examples/sample_queries_with_labels.sql` - Sample SQL queries

