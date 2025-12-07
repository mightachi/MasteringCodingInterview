#!/usr/bin/env python3
"""
Monitor BigQuery slot usage by labels using INFORMATION_SCHEMA.

This script queries INFORMATION_SCHEMA to analyze slot usage patterns
for jobs with specific labels.

Usage:
    python monitor_slot_usage.py \
        --project your-project-id \
        --region us \
        --days 7 \
        --group-by project_id,team
"""

import argparse
import sys
from typing import List, Optional
from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError


def build_analysis_query(
    region: str,
    days: int,
    group_by: List[str],
    filter_labels: Optional[dict] = None
) -> str:
    """
    Build SQL query to analyze slot usage by labels.
    
    Args:
        region: BigQuery region (e.g., 'us', 'europe-west1')
        days: Number of days to look back
        group_by: List of label keys to group by
        filter_labels: Optional dict of label key:value to filter by
        
    Returns:
        SQL query string
    """
    # Build label extraction for group by columns
    label_extractions = []
    for key in group_by:
        label_extractions.append(
            f"(\n    SELECT value \n    FROM UNNEST(labels) \n    WHERE key = '{key}'\n  ) AS {key}"
        )
    
    # Build WHERE clause for label filters
    where_clauses = [
        f"creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)",
        "job_type = 'QUERY'",
        "state = 'DONE'"
    ]
    
    # Add label existence checks for group_by columns
    for key in group_by:
        where_clauses.append(
            f"EXISTS (\n    SELECT 1 \n    FROM UNNEST(labels) AS label\n    WHERE label.key = '{key}'\n  )"
        )
    
    # Add label value filters if provided
    if filter_labels:
        for key, value in filter_labels.items():
            where_clauses.append(
                f"EXISTS (\n    SELECT 1 \n    FROM UNNEST(labels) AS label\n    WHERE label.key = '{key}' AND label.value = '{value}'\n  )"
            )
    
    # Build GROUP BY clause
    group_by_clause = ",\n  ".join(group_by)
    
    # Build WHERE clause (cannot use backslash in f-string expression)
    where_clause = " AND\n  ".join(where_clauses)
    
    # Build SELECT clause
    select_clause = ",\n  ".join(label_extractions)
    
    query = f"""
SELECT
  {select_clause},
  COUNT(*) AS job_count,
  SUM(total_slot_ms) AS total_slot_ms,
  SUM(total_slot_ms) / 1000.0 / 60.0 / 60.0 AS total_slot_hours,
  AVG(total_slot_ms) AS avg_slot_ms,
  MAX(total_slot_ms) AS max_slot_ms,
  APPROX_QUANTILES(total_slot_ms, 100)[OFFSET(50)] AS median_slot_ms,
  APPROX_QUANTILES(total_slot_ms, 100)[OFFSET(95)] AS p95_slot_ms,
  SUM(total_bytes_processed) AS total_bytes_processed,
  SUM(total_bytes_processed) / POW(10, 12) AS total_tb_processed,
  MIN(creation_time) AS first_job_time,
  MAX(creation_time) AS last_job_time
FROM
  `region-{region}.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE
  {where_clause}
GROUP BY
  {group_by_clause}
ORDER BY
  total_slot_ms DESC
"""
    return query


def format_number(num: float) -> str:
    """Format number with commas."""
    if num is None:
        return "N/A"
    if num >= 1e12:
        return f"{num / 1e12:.2f}T"
    elif num >= 1e9:
        return f"{num / 1e9:.2f}B"
    elif num >= 1e6:
        return f"{num / 1e6:.2f}M"
    elif num >= 1e3:
        return f"{num / 1e3:.2f}K"
    else:
        return f"{num:,.0f}"


def format_column_name(name: str) -> str:
    """Format column name for display."""
    # Convert snake_case to Title Case
    return name.replace('_', ' ').title()


def print_results(results):
    """Print query results in a beautifully formatted table."""
    if not results:
        print("❌ No results found.")
        return
    
    # Get column names
    columns = list(results[0].keys())
    
    # Calculate column widths (with padding)
    widths = {}
    for col in columns:
        # Use formatted column name for header width
        header_width = len(format_column_name(col))
        widths[col] = header_width
    
    # Calculate widths based on data
    for row in results:
        for col in columns:
            value = row.get(col)
            if value is None:
                value = "N/A"
            elif isinstance(value, float):
                value = format_number(value)
            else:
                value = str(value)
            widths[col] = max(widths[col], len(value))
    
    # Add padding
    for col in columns:
        widths[col] += 2  # Add padding on both sides
    
    # Build border parts
    border_parts = ["─" * widths[col] for col in columns]
    
    # Print top border
    print("┌" + "┬".join(border_parts) + "┐")
    
    # Print header
    header_parts = []
    for col in columns:
        header_text = format_column_name(col)
        header_parts.append(header_text.center(widths[col]))
    print("│" + "│".join(header_parts) + "│")
    
    # Print header separator
    print("├" + "┼".join(border_parts) + "┤")
    
    # Print rows
    for i, row in enumerate(results):
        values = []
        for col in columns:
            value = row.get(col)
            if value is None:
                value = "N/A"
            elif isinstance(value, float):
                value = format_number(value)
            else:
                value = str(value)
            
            # Right-align numbers, left-align text
            if isinstance(row.get(col), (int, float)) and row.get(col) is not None:
                values.append(value.rjust(widths[col]))
            else:
                values.append(value.ljust(widths[col]))
        
        print("│" + "│".join(values) + "│")
        
        # Add separator between rows (optional, for readability)
        if i < len(results) - 1:
            print("├" + "┼".join(border_parts) + "┤")
    
    # Print bottom border
    print("└" + "┴".join(border_parts) + "┘")


def main():
    parser = argparse.ArgumentParser(
        description='Monitor BigQuery slot usage by labels',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze by project and team
  python monitor_slot_usage.py \\
      --project my-project \\
      --region us \\
      --days 7 \\
      --group-by project_id,team
  
  # Filter by specific project
  python monitor_slot_usage.py \\
      --project my-project \\
      --region us \\
      --days 7 \\
      --group-by project_id,team \\
      --filter project_id:analytics
  
  # Analyze by environment
  python monitor_slot_usage.py \\
      --project my-project \\
      --region us \\
      --days 7 \\
      --group-by environment,project_id
        """
    )
    
    parser.add_argument(
        '--project',
        required=True,
        help='GCP project ID'
    )
    
    parser.add_argument(
        '--region',
        default='us',
        help='BigQuery region (default: us)'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days to look back (default: 7)'
    )
    
    parser.add_argument(
        '--group-by',
        required=True,
        help='Comma-separated list of label keys to group by (e.g., project_id,team)'
    )
    
    parser.add_argument(
        '--filter',
        help='Comma-separated key:value pairs to filter by (e.g., project_id:analytics,environment:prod)'
    )
    
    args = parser.parse_args()
    
    # Parse group-by columns
    group_by = [key.strip() for key in args.group_by.split(',')]
    
    # Parse filter labels
    filter_labels = None
    if args.filter:
        filter_labels = {}
        for pair in args.filter.split(','):
            if ':' not in pair:
                print(f"✗ Invalid filter format: {pair}. Expected 'key:value'", file=sys.stderr)
                sys.exit(1)
            key, value = pair.split(':', 1)
            filter_labels[key.strip()] = value.strip()
    
    # Build query
    query = build_analysis_query(
        region=args.region,
        days=args.days,
        group_by=group_by,
        filter_labels=filter_labels
    )
    
    # Print header
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "BigQuery Slot Usage Analysis" + " " * 30 + "║")
    print("╠" + "═" * 78 + "╣")
    print("║" + f" Project: {args.project:<65} " + "║")
    print("║" + f" Region:  {args.region:<65} " + "║")
    print("║" + f" Period:  Last {args.days} days{'':<60} " + "║")
    print("║" + f" Group By: {', '.join(group_by):<64} " + "║")
    if filter_labels:
        filter_str = ", ".join(f"{k}={v}" for k, v in filter_labels.items())
        print("║" + f" Filters:  {filter_str:<64} " + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    # Run query
    print("🔍 Running analysis query...")
    client = bigquery.Client(project=args.project)
    
    try:
        query_job = client.query(query)
        results = list(query_job.result())
        
        print(f"✅ Found {len(results)} group(s)")
        print()
        
        if results:
            print_results(results)
            
            # Summary statistics
            total_slot_ms = sum(row['total_slot_ms'] for row in results if row['total_slot_ms'])
            total_jobs = sum(row['job_count'] for row in results if row['job_count'])
            avg_slot_ms = total_slot_ms / total_jobs if total_jobs > 0 else 0
            
            print()
            print("╔" + "═" * 78 + "╗")
            print("║" + " " * 25 + "Summary Statistics" + " " * 36 + "║")
            print("╠" + "═" * 78 + "╣")
            print("║" + f" Total Jobs:        {total_jobs:>15,} {'':<45} " + "║")
            print("║" + f" Total Slot-ms:     {format_number(total_slot_ms):>15} {'':<45} " + "║")
            print("║" + f" Total Slot-hours:  {total_slot_ms / 1000.0 / 60.0 / 60.0:>15.2f} {'':<45} " + "║")
            print("║" + f" Avg Slot-ms/Job:   {format_number(avg_slot_ms):>15} {'':<45} " + "║")
            print("╚" + "═" * 78 + "╝")
        else:
            print("⚠️  No results found matching the criteria.")
        
    except GoogleCloudError as e:
        print(f"✗ Error running query: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

