#!/usr/bin/env python3
"""
Example script to run a BigQuery query with labels applied.

This demonstrates how to apply job labels to BigQuery queries for tracking
and monitoring purposes.

Usage:
    python run_labeled_query.py \
        --project your-project-id \
        --query "SELECT 1" \
        --labels project_id:analytics,team:data-engineering,environment:prod
"""

import argparse
import sys
from typing import Dict, Optional
from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError


def parse_labels(label_string: str) -> Dict[str, str]:
    """
    Parse label string into dictionary.
    
    Args:
        label_string: Comma-separated key:value pairs
        
    Returns:
        Dictionary of labels
        
    Example:
        "project_id:analytics,team:data-engineering" -> 
        {"project_id": "analytics", "team": "data-engineering"}
    """
    labels = {}
    if not label_string:
        return labels
    
    for pair in label_string.split(','):
        pair = pair.strip()
        if ':' not in pair:
            raise ValueError(f"Invalid label format: {pair}. Expected 'key:value'")
        
        key, value = pair.split(':', 1)
        key = key.strip()
        value = value.strip()
        
        if not key or not value:
            raise ValueError(f"Empty key or value in label: {pair}")
        
        labels[key] = value
    
    return labels


def validate_labels(labels: Dict[str, str]) -> None:
    """
    Validate that labels meet BigQuery requirements.
    
    Args:
        labels: Dictionary of labels to validate
        
    Raises:
        ValueError: If labels don't meet requirements
    """
    required_labels = ['project_id', 'team']
    
    for key in required_labels:
        if key not in labels:
            raise ValueError(f"Required label '{key}' is missing")
    
    for key, value in labels.items():
        # Key must be lowercase, alphanumeric, hyphens, underscores
        if not key.replace('_', '').replace('-', '').islower() and not key.replace('_', '').replace('-', '').isalnum():
            raise ValueError(f"Label key '{key}' must be lowercase alphanumeric with hyphens/underscores only")
        
        if len(key) > 63:
            raise ValueError(f"Label key '{key}' exceeds 63 characters")
        
        if len(value) > 63:
            raise ValueError(f"Label value '{value}' exceeds 63 characters")
        
        # Check for invalid characters in key
        if not all(c.islower() or c.isdigit() or c in ['-', '_'] for c in key):
            raise ValueError(f"Label key '{key}' contains invalid characters")


def run_query_with_labels(
    project: str,
    query: str,
    labels: Dict[str, str],
    dry_run: bool = False
) -> Optional[bigquery.QueryJob]:
    """
    Run a BigQuery query with labels applied.
    
    Args:
        project: GCP project ID
        query: SQL query to execute
        labels: Dictionary of labels to apply
        dry_run: If True, validate query without running
        
    Returns:
        QueryJob object if successful, None if dry_run
    """
    client = bigquery.Client(project=project)
    
    # Configure job with labels
    job_config = bigquery.QueryJobConfig()
    job_config.labels = labels
    job_config.dry_run = dry_run
    job_config.use_query_cache = True
    
    print(f"Running query with labels: {labels}")
    print(f"Query: {query[:100]}..." if len(query) > 100 else f"Query: {query}")
    print(f"Dry run: {dry_run}")
    print()
    
    try:
        query_job = client.query(query, job_config=job_config)
        
        if dry_run:
            print(f"✓ Query is valid")
            print(f"  Estimated bytes processed: {query_job.total_bytes_processed:,}")
            return None
        else:
            # Wait for job to complete
            print("Waiting for query to complete...")
            results = query_job.result()
            
            print(f"✓ Query completed successfully")
            print(f"  Job ID: {query_job.job_id}")
            
            # Get slot milliseconds - may be in statistics or directly on job
            try:
                # Try accessing via statistics first (newer API)
                if hasattr(query_job, 'statistics') and hasattr(query_job.statistics, 'total_slot_ms'):
                    total_slot_ms = query_job.statistics.total_slot_ms
                # Try direct attribute (older API or different version)
                elif hasattr(query_job, 'total_slot_ms'):
                    total_slot_ms = query_job.total_slot_ms
                # Try getting from job resource
                else:
                    # Reload job to get full statistics
                    query_job.reload()
                    total_slot_ms = getattr(query_job, 'total_slot_ms', None)
                    if total_slot_ms is None and hasattr(query_job, 'statistics'):
                        total_slot_ms = getattr(query_job.statistics, 'total_slot_ms', None)
            except Exception:
                total_slot_ms = None
            
            if total_slot_ms is not None:
                print(f"  Total slot milliseconds: {total_slot_ms:,}")
            else:
                print(f"  Total slot milliseconds: N/A (not available)")
            
            print(f"  Total bytes processed: {query_job.total_bytes_processed:,}")
            print(f"  Creation time: {query_job.created}")
            print(f"  End time: {query_job.ended}")
            
            # Show results if any
            rows = list(results)
            if rows:
                print(f"\n  Results ({len(rows)} rows):")
                for i, row in enumerate(rows[:5], 1):  # Show first 5 rows
                    print(f"    Row {i}: {dict(row)}")
                if len(rows) > 5:
                    print(f"    ... and {len(rows) - 5} more rows")
            
            return query_job
            
    except GoogleCloudError as e:
        print(f"✗ Error running query: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Run a BigQuery query with labels applied',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a simple query with labels
  python run_labeled_query.py \\
      --project my-project \\
      --query "SELECT 1 as test" \\
      --labels "project_id:analytics,team:data-engineering,environment:prod"
  
  # Dry run to validate query
  python run_labeled_query.py \\
      --project my-project \\
      --query "SELECT * FROM dataset.table" \\
      --labels "project_id:analytics,team:data-engineering" \\
      --dry-run
        """
    )
    
    parser.add_argument(
        '--project',
        required=True,
        help='GCP project ID'
    )
    
    parser.add_argument(
        '--query',
        required=True,
        help='SQL query to execute'
    )
    
    parser.add_argument(
        '--labels',
        required=True,
        help='Comma-separated key:value pairs (e.g., "project_id:analytics,team:data-engineering")'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate query without running it'
    )
    
    args = parser.parse_args()
    
    # Parse and validate labels
    try:
        labels = parse_labels(args.labels)
        validate_labels(labels)
    except ValueError as e:
        print(f"✗ Label validation error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Run query
    run_query_with_labels(
        project=args.project,
        query=args.query,
        labels=labels,
        dry_run=args.dry_run
    )


if __name__ == '__main__':
    main()

