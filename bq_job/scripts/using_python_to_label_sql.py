from google.cloud import bigquery

client = bigquery.Client()

job_config = bigquery.QueryJobConfig(
    labels={
        "project": "orion",
        "team": "mle",
        "application": "pricing-insights",
        "environment": "dev",
        "priority": "high"
    }
)

query = """
    select corpus, sum(word_count) from `bigquery-public-data.samples.shakespeare` group by corpus
"""

query_job = client.query(query, job_config=job_config)
results = query_job.result()