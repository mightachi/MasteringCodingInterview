#!/usr/bin/env python3
"""
Example script to run multiple BigQuery queries with labels in batch.

This demonstrates how to apply consistent labels across multiple queries,
useful for ETL pipelines or scheduled jobs.

Usage:
    python batch_labeled_queries.py \
        --project your-project-id \
        --queries-file queries.txt \
        --labels project_id:analytics,team:data-engineering,environment:prod
"""

import argparse
import sys
import time
from typing import Dict, List, Optional
from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError


def parse_labels(label_string: str) -> Dict[str, str]:
    """Parse label string into dictionary."""
    labels = {}
    if not label_string:
        return labels
    
    for pair in label_string.split(','):
        pair = pair.strip()
        if ':' not in pair:
            raise ValueError(f"Invalid label format: {pair}. Expected 'key:value'")
        
        key, value = pair.split(':', 1)
        labels[key.strip()] = value.strip()
    
    return labels


def read_queries_from_file(filepath: str) -> List[Dict[str, str]]:
    """
    Read queries from file.
    
    Expected format:
    - Each query separated by comments (lines starting with #) or empty lines
    - Lines starting with # Query N are treated as query names
    - Empty lines separate queries
    - Queries can span multiple lines
    
    Returns:
        List of dictionaries with 'name' and 'query' keys
    """
    queries = []
    with open(filepath, 'r') as f:
        current_query = []
        current_name = None
        in_query = False
        
        for line in f:
            original_line = line
            line = line.strip()
            
            # Check if this is a query name comment (e.g., "# Query 1", "# Query 2")
            if line.startswith('# Query') or (line.startswith('#') and 'query' in line.lower()):
                # Finish previous query if exists
                if current_query:
                    query_text = '\n'.join(current_query).strip()
                    if query_text:  # Only add if query is not empty
                        queries.append({
                            'name': current_name or f'query_{len(queries) + 1}',
                            'query': query_text
                        })
                
                # Start new query
                current_query = []
                # Extract name from comment (e.g., "# Query 1" -> "Query 1")
                current_name = line.lstrip('#').strip()
                in_query = False
                continue
            
            # Skip other comments and empty lines (but empty lines can separate queries)
            if line.startswith('#'):
                continue
            
            # Empty line - if we're in a query, it might be the end, but continue collecting
            # We'll use comment markers to definitively separate queries
            if not line:
                # If we have content, this might be a separator
                if current_query:
                    in_query = True
                continue
            
            # This is a query line
            current_query.append(original_line.rstrip('\n'))
            in_query = True
        
        # Add last query
        if current_query:
            query_text = '\n'.join(current_query).strip()
            if query_text:  # Only add if query is not empty
                queries.append({
                    'name': current_name or f'query_{len(queries) + 1}',
                    'query': query_text
                })
    
    return queries


def run_query_with_labels(
    client: bigquery.Client,
    query: str,
    labels: Dict[str, str],
    query_name: str = "query"
) -> Optional[bigquery.QueryJob]:
    """
    Run a BigQuery query with labels applied.
    
    Returns:
        QueryJob object if successful
    """
    job_config = bigquery.QueryJobConfig()
    job_config.labels = labels
    job_config.use_query_cache = True
    
    try:
        print(f"  Running: {query_name}...")
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        
        print(f"    ✓ Completed (Job ID: {query_job.job_id})")
        
        # Get slot milliseconds safely
        try:
            if hasattr(query_job, 'statistics') and hasattr(query_job.statistics, 'total_slot_ms'):
                total_slot_ms = query_job.statistics.total_slot_ms
            elif hasattr(query_job, 'total_slot_ms'):
                total_slot_ms = query_job.total_slot_ms
            else:
                query_job.reload()
                total_slot_ms = getattr(query_job, 'total_slot_ms', None) or \
                               (getattr(query_job.statistics, 'total_slot_ms', None) if hasattr(query_job, 'statistics') else None)
        except Exception:
            total_slot_ms = None
        
        slot_info = f"Slot-ms: {total_slot_ms:,}" if total_slot_ms is not None else "Slot-ms: N/A"
        print(f"      {slot_info}, Bytes: {query_job.total_bytes_processed:,}")
        
        return query_job
        
    except GoogleCloudError as e:
        print(f"    ✗ Error: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"    ✗ Unexpected error: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Run multiple BigQuery queries with labels in batch',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run queries from file
  python batch_labeled_queries.py \\
      --project my-project \\
      --queries-file queries.sql \\
      --labels "project_id:analytics,team:data-engineering,environment:prod"
  
  # Run with custom workflow label
  python batch_labeled_queries.py \\
      --project my-project \\
      --queries-file etl_queries.sql \\
      --labels "project_id:analytics,team:data-engineering,workflow:daily-etl"
        """
    )
    
    parser.add_argument(
        '--project',
        required=True,
        help='GCP project ID'
    )
    
    parser.add_argument(
        '--queries-file',
        required=True,
        help='File containing SQL queries (one per line or separated)'
    )
    
    parser.add_argument(
        '--labels',
        required=True,
        help='Comma-separated key:value pairs'
    )
    
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Run queries in parallel (default: sequential)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between queries in seconds (default: 1.0)'
    )
    
    args = parser.parse_args()
    
    # Parse labels
    try:
        labels = parse_labels(args.labels)
    except ValueError as e:
        print(f"✗ Label parsing error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Read queries
    try:
        queries = read_queries_from_file(args.queries_file)
        if not queries:
            print(f"✗ No queries found in {args.queries_file}", file=sys.stderr)
            sys.exit(1)
    except FileNotFoundError:
        print(f"✗ File not found: {args.queries_file}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error reading queries file: {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found {len(queries)} queries")
    print(f"Labels: {labels}")
    print()
    
    # Initialize client
    client = bigquery.Client(project=args.project)
    
    # Run queries
    results = []
    start_time = time.time()
    
    if args.parallel:
        # Run queries in parallel
        print("Running queries in parallel...")
        jobs = []
        for query_info in queries:
            job_config = bigquery.QueryJobConfig()
            job_config.labels = labels
            job_config.use_query_cache = True
            
            try:
                query_job = client.query(query_info['query'], job_config=job_config)
                jobs.append((query_info['name'], query_job))
            except Exception as e:
                print(f"  ✗ Failed to start {query_info['name']}: {e}", file=sys.stderr)
        
        # Wait for all jobs to complete
        for name, job in jobs:
            try:
                job.result()
                print(f"  ✓ {name} completed (Job ID: {job.job_id})")
                results.append(job)
            except Exception as e:
                print(f"  ✗ {name} failed: {e}", file=sys.stderr)
    else:
        # Run queries sequentially
        print("Running queries sequentially...")
        for i, query_info in enumerate(queries, 1):
            print(f"[{i}/{len(queries)}] {query_info['name']}")
            job = run_query_with_labels(
                client=client,
                query=query_info['query'],
                labels=labels,
                query_name=query_info['name']
            )
            if job:
                results.append(job)
            
            # Delay between queries (except for last one)
            if i < len(queries) and args.delay > 0:
                time.sleep(args.delay)
    
    elapsed_time = time.time() - start_time
    
    # Summary
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total queries: {len(queries)}")
    print(f"Successful: {len(results)}")
    print(f"Failed: {len(queries) - len(results)}")
    print(f"Total time: {elapsed_time:.2f} seconds")
    
    if results:
        # Calculate totals safely
        total_slot_ms = 0
        total_bytes = 0
        for job in results:
            try:
                if hasattr(job, 'statistics') and hasattr(job.statistics, 'total_slot_ms'):
                    total_slot_ms += job.statistics.total_slot_ms
                elif hasattr(job, 'total_slot_ms'):
                    total_slot_ms += job.total_slot_ms
                else:
                    job.reload()
                    slot_ms = getattr(job, 'total_slot_ms', None) or \
                             (getattr(job.statistics, 'total_slot_ms', None) if hasattr(job, 'statistics') else None)
                    if slot_ms:
                        total_slot_ms += slot_ms
            except Exception:
                pass
            total_bytes += job.total_bytes_processed
        
        if total_slot_ms > 0:
            print(f"Total slot-ms: {total_slot_ms:,}")
            print(f"Average slot-ms per query: {total_slot_ms / len(results):,.0f}")
        else:
            print(f"Total slot-ms: N/A (not available)")
        print(f"Total bytes processed: {total_bytes:,}")


if __name__ == '__main__':
    main()

