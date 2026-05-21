# 🏗️ Agoda Round 2: System Design for Data Engineering — Complete Preparation Notebook

> **Purpose:** Master every concept needed for Agoda's Data Engineering System Design round.  
> **Scale Context:** Agoda processes **3+ trillion events/day**, serves **1M+ QPS** during peak, manages **petabytes** of data across multiple data centers.  
> **Last Updated:** April 2026

---

## 📋 Master Table of Contents

| # | Section | What You'll Learn |
|---|---------|-------------------|
| 1 | [Interview Intelligence](#1-interview-intelligence) | Agoda questions from last 2 years, what interviewers evaluate |
| 2 | [The Framework](#2-the-framework) | How to structure ANY system design answer |
| 3 | [Data Pipelines at Scale](#3-data-pipelines) | Batch, streaming, CDC, Lambda/Kappa, Medallion architecture |
| 4 | [Data Modeling & Storage](#4-data-modeling) | SQL vs NoSQL, partitioning, indexing, schema design |
| 5 | [Distributed Processing (Spark)](#5-spark-deep-dive) | Internals, optimization, skew, shuffles, at TB scale |
| 6 | [Streaming & Event-Driven Systems](#6-streaming) | Kafka at 3T events/day, exactly-once, backpressure |
| 7 | [Performance & Scalability](#7-performance) | 1M+ QPS patterns, caching, sharding, async workflows |
| 8 | [Operational Excellence](#8-ops-excellence) | Monitoring, alerting, disaster recovery, SRE practices |
| 9 | [ML Feature Store Design](#9-feature-store) | Online/offline serving, training-serving skew, Agoda's approach |
| 10 | [OTA System Design Problems](#10-ota-designs) | 6 complete Agoda-specific system designs with code |
| 11 | [Common Mistakes & Edge Cases](#11-mistakes) | What trips people up at 1M+ QPS / TB scale |
| 12 | [Mock Interview Q&A](#12-mock-qa) | 30+ questions with model answers |

---

# 1. Interview Intelligence — Agoda Data Engineering Round 2 <a name="1-interview-intelligence"></a>

## 1.1 What This Round Assesses

```
┌────────────────────────────────────────────────────────────────────┐
│                  AGODA ROUND 2: SCORING RUBRIC                      │
│                                                                      │
│  ┌──────────────────────┬───────┬──────────────────────────────┐    │
│  │ Dimension            │Weight │ What They Look For            │    │
│  ├──────────────────────┼───────┼──────────────────────────────┤    │
│  │ System Architecture  │  25%  │ End-to-end design, component  │    │
│  │                      │       │ selection, data flow           │    │
│  ├──────────────────────┼───────┼──────────────────────────────┤    │
│  │ Data Management      │  25%  │ Modeling, storage choices,     │    │
│  │                      │       │ consistency, partitioning      │    │
│  ├──────────────────────┼───────┼──────────────────────────────┤    │
│  │ Scalability          │  20%  │ Handle 10x load, bottleneck    │    │
│  │                      │       │ identification, optimization   │    │
│  ├──────────────────────┼───────┼──────────────────────────────┤    │
│  │ Operational          │  15%  │ Monitoring, recovery, graceful │    │
│  │ Excellence           │       │ degradation, observability     │    │
│  ├──────────────────────┼───────┼──────────────────────────────┤    │
│  │ Communication        │  15%  │ Clarity, trade-off reasoning,  │    │
│  │                      │       │ collaboration, adaptability    │    │
│  └──────────────────────┴───────┴──────────────────────────────┘    │
└────────────────────────────────────────────────────────────────────┘
```

## 1.2 Actual Agoda Interview Questions (2024-2026, sourced from Glassdoor, LeetCode, InterviewQuery)

### Category A: End-to-End Data Pipeline Design

```python
agoda_questions_pipeline = {
    "Q1": {
        "question": "Design a real-time clickstream analytics pipeline for Agoda's website "
                    "that captures user behavior (searches, clicks, page views) and makes "
                    "this data available for both real-time dashboards and batch ML training.",
        "what_they_test": [
            "Ingestion at scale (billions of events/day)",
            "Lambda vs Kappa architecture choice",
            "Storage tiering (hot/warm/cold)",
            "Data quality and late-arriving events",
        ],
        "frequency": "Very Common — asked in ~40% of DE interviews",
    },
    "Q2": {
        "question": "Design a Change Data Capture (CDC) pipeline that syncs transactional "
                    "data from MySQL (bookings, inventory) to the data warehouse with "
                    "minimal latency and zero data loss.",
        "what_they_test": [
            "CDC tools (Debezium, Maxwell)",
            "Exactly-once delivery semantics",
            "Schema evolution handling",
            "Backfill strategies for historical data",
        ],
        "frequency": "Common — asked in ~30% of DE interviews",
    },
    "Q3": {
        "question": "Design a data pipeline that processes hotel availability updates from "
                    "10,000+ supplier APIs, normalizes them, and makes them searchable "
                    "in under 5 seconds.",
        "what_they_test": [
            "High-throughput ingestion from heterogeneous sources",
            "Data normalization and deduplication",
            "Freshness vs consistency trade-offs",
            "Rate limiting and backpressure handling",
        ],
        "frequency": "Common — Agoda-specific OTA problem",
    },
}
```

### Category B: Storage & Data Modeling

```python
agoda_questions_storage = {
    "Q4": {
        "question": "Design the data model for Agoda's hotel inventory system that supports "
                    "real-time availability checks across 2.5M+ properties with varying "
                    "room types, rate plans, and date-specific availability.",
        "what_they_test": [
            "Dimensional modeling vs normalized",
            "Partitioning strategy for time-series availability",
            "Hot vs cold storage separation",
            "Query patterns driving schema design",
        ],
    },
    "Q5": {
        "question": "You have a table with 500B rows of booking events. Design an efficient "
                    "storage and querying strategy that supports both analytical queries "
                    "(aggregations by date/city) and point lookups (by booking_id).",
        "what_they_test": [
            "Columnar vs row storage trade-offs",
            "Partitioning and clustering",
            "Materialized views / pre-aggregation",
            "Cost vs performance optimization",
        ],
    },
    "Q6": {
        "question": "How would you design a slowly changing dimension (SCD) for hotel "
                    "metadata (name, star rating, amenities) that changes infrequently "
                    "but needs full history for ML training?",
        "what_they_test": [
            "SCD Type 1 vs Type 2 vs Type 3",
            "Delta Lake / Iceberg for time-travel",
            "Storage efficiency for versioned data",
        ],
    },
}
```

### Category C: Distributed Processing & Spark

```python
agoda_questions_spark = {
    "Q7": {
        "question": "Your Spark job processes 10TB of clickstream data daily but has been "
                    "taking 8 hours. The SLA is 2 hours. How do you optimize it?",
        "what_they_test": [
            "Systematic performance debugging approach",
            "Spark UI interpretation (stages, tasks, shuffles)",
            "Data skew identification and resolution",
            "Resource tuning (executors, memory, partitions)",
        ],
    },
    "Q8": {
        "question": "Explain how you would handle data skew in a Spark join where 80% of "
                    "bookings belong to the top 1% of hotels.",
        "what_they_test": [
            "Salting technique",
            "Broadcast join for small tables",
            "AQE skew join optimization",
            "Partial aggregation before join",
        ],
    },
    "Q9": {
        "question": "Design a Spark-based feature engineering pipeline that computes "
                    "100+ features for 2.5M hotels daily, supporting both batch training "
                    "and online serving.",
        "what_they_test": [
            "Feature computation architecture",
            "Training-serving skew prevention",
            "Incremental vs full computation strategies",
            "Feature store integration",
        ],
    },
}
```

### Category D: Real-Time & Streaming

```python
agoda_questions_streaming = {
    "Q10": {
        "question": "Design a real-time hotel pricing update system where price changes "
                    "from suppliers must be reflected on the search page within 5 seconds.",
        "what_they_test": [
            "Event-driven architecture",
            "Kafka consumer group design",
            "Cache invalidation strategies",
            "Consistency guarantees",
        ],
    },
    "Q11": {
        "question": "How would you design a real-time fraud detection pipeline that "
                    "evaluates every booking within 100ms?",
        "what_they_test": [
            "Stream processing (Flink/Kafka Streams)",
            "Feature serving at low latency",
            "Rules engine + ML model hybrid",
            "False positive handling",
        ],
    },
    "Q12": {
        "question": "Design a system to track and aggregate real-time metrics (bookings, "
                    "revenue, searches) and display them on a dashboard with max 30-second delay.",
        "what_they_test": [
            "Streaming aggregation with windowing",
            "Exactly-once counting semantics",
            "Time-series storage (InfluxDB/TimescaleDB)",
            "Dashboard refresh strategies",
        ],
    },
}
```

### Category E: Operational & Scenario-Based

```python
agoda_questions_ops = {
    "Q13": {
        "question": "Your daily Spark pipeline failed at 3 AM and the data team needs "
                    "fresh data by 9 AM. Walk me through your troubleshooting and recovery process.",
        "what_they_test": [
            "Systematic debugging approach",
            "Idempotency and safe re-runs",
            "Monitoring and alerting setup",
            "Communication with stakeholders",
        ],
    },
    "Q14": {
        "question": "How do you handle schema evolution in a production data pipeline "
                    "when the upstream service adds new fields or changes types?",
        "what_they_test": [
            "Schema registry (Avro/Protobuf)",
            "Forward/backward compatibility",
            "Schema evolution in Parquet/Delta",
            "Pipeline resilience to changes",
        ],
    },
    "Q15": {
        "question": "Design the monitoring and alerting system for a data platform that "
                    "processes 3 trillion events daily. What metrics would you track?",
        "what_they_test": [
            "Data quality metrics (completeness, freshness, accuracy)",
            "Pipeline health metrics (latency, throughput, error rate)",
            "Business impact metrics",
            "Alert fatigue prevention",
        ],
    },
}
```

---

# 2. The Framework — How to Answer ANY System Design Question <a name="2-the-framework"></a>

## 2.1 The DRIVE Framework (5 Steps, 45-60 min)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    THE DRIVE FRAMEWORK                                │
│                                                                       │
│  D — DEFINE Requirements           (5-8 min)                        │
│      • Functional: What does the system DO?                          │
│      • Non-Functional: Latency, throughput, availability, cost       │
│      • Constraints: Data volume, QPS, team size, existing infra      │
│      • Success Metrics: How do we know it's working?                 │
│                                                                       │
│  R — REASON About Data             (8-10 min)                        │
│      • Data sources, volume, velocity, variety                       │
│      • Data model / schema design                                    │
│      • Access patterns (read-heavy? write-heavy? mixed?)             │
│      • Consistency and freshness requirements per data type          │
│                                                                       │
│  I — INTEGRATE Components          (15-20 min)                       │
│      • High-level architecture diagram                               │
│      • Component selection with JUSTIFICATION                        │
│      • Data flow from ingestion to processing to storage to serving │
│      • API contracts between components                              │
│                                                                       │
│  V — VALIDATE at Scale             (8-10 min)                        │
│      • Bottleneck identification                                     │
│      • Scaling strategies (horizontal, vertical, caching)            │
│      • Failure modes and recovery                                    │
│      • Performance estimates (back-of-envelope calculations)         │
│                                                                       │
│  E — ENSURE Operational Excellence  (5-8 min)                        │
│      • Monitoring and alerting                                       │
│      • Deployment and rollback                                       │
│      • Data quality checks                                           │
│      • Disaster recovery                                             │
└─────────────────────────────────────────────────────────────────────┘
```

## 2.2 Back-of-Envelope Calculations (MUST KNOW)

```python
class BackOfEnvelopeCalculator:
    """
    Common calculations for system design interviews.
    
    KEY NUMBERS TO MEMORIZE:
    ========================
    - 1 day = 86,400 seconds ~ 100K seconds
    - 1 million requests/day ~ 12 QPS
    - 1 billion requests/day ~ 12,000 QPS
    
    LATENCY NUMBERS TO KNOW:
    ========================
    - L1 cache:           0.5 ns
    - RAM access:         100 ns
    - SSD read:           150 us
    - HDD seek:           10 ms
    - Network (same DC):  0.5 ms
    - Network (cross DC): 50-150 ms
    - Redis GET:          0.5 ms
    - MySQL query:        5-50 ms
    - S3 GET:             50-200 ms
    """
    
    @staticmethod
    def agoda_scale_example():
        """Example: Estimate Agoda clickstream pipeline capacity."""
        
        events_per_day = 3_000_000_000_000  # 3T
        events_per_second = events_per_day / 86400  # ~ 34.7M events/sec
        
        avg_event_size_bytes = 500
        daily_bytes = events_per_day * avg_event_size_bytes  # 1.5 PB/day raw
        
        # Kafka sizing: 1 partition ~ 10 MB/s write throughput
        write_throughput_mbs = (events_per_second * avg_event_size_bytes) / (1024**2)
        kafka_partitions_needed = write_throughput_mbs / 10  # ~ 1,660 partitions
        
        return {
            "events_per_second": f"{events_per_second:,.0f} eps",
            "daily_data_volume": f"~1.5 PB/day (raw)",
            "kafka_partitions": f"~{kafka_partitions_needed:.0f} partitions",
        }
    
    @staticmethod
    def hotel_search_estimation():
        """Estimate hotel search system capacity."""
        
        search_qps = 50_000  # peak
        
        # Per-search data movement:
        # ES query result: 500 hotels x 200 bytes = 100 KB
        # Redis lookups: 500 x 3 dates x 8 bytes = 12 KB  
        # Feature fetch: 300 hotels x 50 features x 4 bytes = 60 KB
        # Total: ~172 KB per search
        
        latency_budget = {
            "api_gateway": "5ms",
            "elasticsearch_query": "30ms",
            "redis_availability": "10ms (MGET batch)",
            "feature_store_fetch": "15ms",
            "ml_inference": "20ms (ONNX batch 300 items)",
            "business_rules": "5ms",
            "serialization": "5ms",
            "network_overhead": "10ms",
            "total": "100ms (50% buffer for p99)",
        }
        
        return latency_budget
```

---

# 3. Data Pipelines at Scale — Deep Dive <a name="3-data-pipelines"></a>

## 3.1 Medallion Architecture (Bronze to Silver to Gold)

```
┌──────────────────────────────────────────────────────────────────────┐
│                   MEDALLION ARCHITECTURE                              │
│                                                                        │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐        │
│  │   BRONZE      │─────>│   SILVER      │─────>│    GOLD       │       │
│  │   (Raw)       │      │  (Validated)  │      │  (Business)   │       │
│  │               │      │               │      │               │       │
│  │ - Append-only │      │ - Deduped     │      │ - Aggregated  │       │
│  │ - Schema-on-  │      │ - Type-cast   │      │ - Joined      │       │
│  │   read        │      │ - Validated   │      │ - ML-ready    │       │
│  │ - Raw JSON/   │      │ - Null-       │      │ - Dashboard-  │       │
│  │   Avro/Proto  │      │   handled     │      │   ready       │       │
│  │ - Partitioned │      │ - Partitioned │      │ - Partitioned │       │
│  │   by ingest   │      │   by event    │      │   by entity   │       │
│  │   date        │      │   date        │      │   + date      │       │
│  └──────────────┘      └──────────────┘      └──────────────┘        │
│        |                      |                      |                 │
│  Format: Parquet         Format: Delta           Format: Delta         │
│  Retention: 90 days      Retention: 1 year      Retention: 3 years    │
└──────────────────────────────────────────────────────────────────────┘
```

### Complete Medallion Pipeline Implementation

```python
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import *
from pyspark.sql.window import Window
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AgodaBookingPipeline:
    """
    Production-grade Medallion pipeline for Agoda booking data.
    
    Data Flow:
    Booking Service (MySQL) -> Debezium CDC -> Kafka -> Bronze -> Silver -> Gold
    
    Scale: ~5M bookings/day, ~200M searches/day
    """
    
    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.quality_metrics = {}
    
    # ================================================================
    # BRONZE LAYER — Raw Ingestion (No transformations!)
    # ================================================================
    
    def ingest_bronze(self, source_path: str, batch_id: str) -> DataFrame:
        """
        Ingest raw data into Bronze layer.
        
        Rules:
        1. NEVER modify source data
        2. Add audit metadata (ingestion timestamp, source, batch_id)
        3. Handle schema evolution (accept any new fields)
        4. Partition by ingestion date for lifecycle management
        
        Common Mistake: Filtering or transforming data in Bronze.
        Bronze should be a FAITHFUL COPY of the source.
        """
        raw_df = self.spark.read \
            .option("mode", "PERMISSIVE") \
            .option("columnNameOfCorruptRecord", "_corrupt_record") \
            .json(source_path)
        
        bronze_df = raw_df \
            .withColumn("_ingestion_timestamp", F.current_timestamp()) \
            .withColumn("_source_file", F.input_file_name()) \
            .withColumn("_batch_id", F.lit(batch_id)) \
            .withColumn("_ingestion_date", F.current_date())
        
        corrupt_count = bronze_df.filter(
            F.col("_corrupt_record").isNotNull()
        ).count()
        
        if corrupt_count > 0:
            logger.warning(f"Found {corrupt_count} corrupt records in batch {batch_id}")
        
        bronze_df.write \
            .mode("append") \
            .partitionBy("_ingestion_date") \
            .format("delta") \
            .save("s3://agoda-datalake/bronze/bookings/")
        
        return bronze_df
    
    # ================================================================
    # SILVER LAYER — Cleansing, Validation, Deduplication
    # ================================================================
    
    def process_silver(self, bronze_df: DataFrame) -> DataFrame:
        """
        Transform Bronze to Silver with data quality enforcement.
        
        Rules:
        1. Deduplicate (by booking_id, keep latest)
        2. Enforce schema (type casting, null handling)
        3. Validate business rules (price > 0, valid dates)
        4. Partition by business-relevant key (booking_date)
        
        Common Mistake: Not handling late-arriving data.
        Solution: Use MERGE (upsert) with Delta Lake, not overwrite.
        """
        
        # Deduplicate (keep most recent version of each booking)
        window_spec = Window.partitionBy("booking_id").orderBy(
            F.col("_ingestion_timestamp").desc()
        )
        
        deduped_df = bronze_df \
            .withColumn("_row_num", F.row_number().over(window_spec)) \
            .filter(F.col("_row_num") == 1) \
            .drop("_row_num")
        
        # Schema enforcement
        typed_df = deduped_df.select(
            F.col("booking_id").cast("string"),
            F.col("hotel_id").cast("string"),
            F.col("user_id").cast("string"),
            F.col("check_in_date").cast("date"),
            F.col("check_out_date").cast("date"),
            F.col("num_guests").cast("integer"),
            F.col("total_price").cast("double"),
            F.col("currency").cast("string"),
            F.col("booking_status").cast("string"),
            F.col("booking_timestamp").cast("timestamp"),
            F.col("device_type").cast("string"),
            F.col("_ingestion_timestamp"),
            F.col("_batch_id"),
        )
        
        # Business rule validation
        validated_df = typed_df \
            .filter(F.col("booking_id").isNotNull()) \
            .filter(F.col("hotel_id").isNotNull()) \
            .filter(F.col("total_price") > 0) \
            .filter(F.col("total_price") < 1_000_000) \
            .filter(F.col("check_out_date") > F.col("check_in_date")) \
            .withColumn(
                "stay_duration",
                F.datediff(F.col("check_out_date"), F.col("check_in_date"))
            ) \
            .filter(F.col("stay_duration").between(1, 365))
        
        # Data Quality gate
        bronze_count = bronze_df.count()
        silver_count = validated_df.count()
        drop_rate = 1 - (silver_count / max(bronze_count, 1))
        
        if drop_rate > 0.05:  # > 5% dropped
            raise Exception(
                f"Silver drop rate {drop_rate:.2%} exceeds 5% threshold!"
            )
        
        validated_df.write \
            .mode("overwrite") \
            .partitionBy("check_in_date") \
            .format("delta") \
            .save("s3://agoda-datalake/silver/bookings/")
        
        return validated_df
    
    # ================================================================
    # GOLD LAYER — Business Aggregations & ML Features
    # ================================================================
    
    def build_gold_hotel_features(self, silver_bookings, silver_clicks, silver_reviews):
        """
        Build Gold-layer hotel feature table for ML models.
        Output: One row per hotel_id with 50+ features
        """
        
        now = F.current_timestamp()
        
        # Booking Features
        booking_features = silver_bookings \
            .groupBy("hotel_id") \
            .agg(
                F.count("*").alias("total_bookings_all_time"),
                F.countDistinct("user_id").alias("unique_guests"),
                F.sum(F.when(
                    F.datediff(now, "booking_timestamp") <= 7, 1
                ).otherwise(0)).alias("bookings_7d"),
                F.sum(F.when(
                    F.datediff(now, "booking_timestamp") <= 30, 1
                ).otherwise(0)).alias("bookings_30d"),
                F.avg("total_price").alias("avg_booking_price"),
                F.avg(F.when(
                    F.col("booking_status") == "cancelled", 1
                ).otherwise(0)).alias("cancellation_rate"),
                F.avg("stay_duration").alias("avg_stay_duration"),
            )
        
        # Click Features (CTR)
        click_features = silver_clicks \
            .groupBy("hotel_id") \
            .agg(
                F.count("*").alias("total_impressions"),
                F.sum(F.when(F.col("action") == "click", 1).otherwise(0)).alias("total_clicks"),
            ) \
            .withColumn(
                "ctr", F.col("total_clicks") / F.greatest(F.col("total_impressions"), F.lit(1))
            )
        
        # Review Features
        review_features = silver_reviews \
            .groupBy("hotel_id") \
            .agg(
                F.count("*").alias("total_reviews"),
                F.avg("rating").alias("avg_rating"),
                F.stddev("rating").alias("rating_variance"),
            )
        
        # Join All Features
        gold_features = booking_features \
            .join(click_features, "hotel_id", "left") \
            .join(review_features, "hotel_id", "left") \
            .fillna(0)
        
        # Derived Features
        gold_features = gold_features \
            .withColumn(
                "conversion_rate",
                F.col("total_bookings_all_time") / F.greatest(F.col("total_impressions"), F.lit(1))
            ) \
            .withColumn(
                "quality_score",
                (F.col("avg_rating") * 0.4 + 
                 F.col("ctr") * 100 * 0.3 + 
                 (1 - F.col("cancellation_rate")) * 5 * 0.3)
            )
        
        gold_features.write \
            .mode("overwrite") \
            .format("delta") \
            .save("s3://agoda-datalake/gold/hotel_features/")
        
        return gold_features
```

## 3.2 Change Data Capture (CDC) — Critical for Agoda

```python
"""
WHY CDC at Agoda?
=================
Agoda's booking system runs on MySQL (transactional DB).
Can't query production MySQL for analytics (kills performance).
CDC streams changes from MySQL binlog to data lake.

Architecture:
MySQL (bookings DB)
    |
    v
Debezium (CDC connector) <-- Reads MySQL binlog (WAL)
    |
    v
Kafka (change events topic)
    |
    |-->  Spark Streaming -> Delta Lake (Silver) -> Gold tables
    |-->  Flink -> Redis (real-time inventory cache)
    |-->  Flink -> Elasticsearch (search index updates)
"""

class CDCPipeline:
    """
    Production CDC pipeline: MySQL -> Kafka -> Delta Lake
    
    Key Design Decisions:
    1. Debezium (not custom binlog reader) - battle-tested
    2. Avro serialization with Schema Registry - schema evolution
    3. Delta Lake MERGE for upserts - handles updates/deletes correctly
    4. Exactly-once with Kafka transactions + Spark checkpoints
    """
    
    def process_cdc_stream(self, spark):
        """Spark Structured Streaming: Kafka -> Delta Lake (Silver)"""
        
        cdc_stream = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "kafka-broker:9092") \
            .option("subscribe", "dbserver1.bookings_db.bookings") \
            .option("startingOffsets", "latest") \
            .option("maxOffsetsPerTrigger", 100000) \
            .load()
        
        def upsert_to_delta(batch_df, batch_id):
            """
            MERGE logic for CDC events.
            
            CRITICAL: Sort by CDC timestamp within each booking_id.
            Keep only the LATEST event per booking_id.
            """
            from delta.tables import DeltaTable
            
            if batch_df.isEmpty():
                return
            
            # Deduplicate within micro-batch
            window = Window.partitionBy("booking_id").orderBy(
                F.col("_cdc_timestamp").desc()
            )
            latest_events = batch_df \
                .withColumn("_rn", F.row_number().over(window)) \
                .filter(F.col("_rn") == 1) \
                .drop("_rn")
            
            # MERGE into Delta table
            target_table = DeltaTable.forPath(
                spark, "s3://agoda-datalake/silver/bookings/"
            )
            
            target_table.alias("target").merge(
                latest_events.alias("source"),
                "target.booking_id = source.booking_id"
            ).whenMatchedUpdateAll(
            ).whenNotMatchedInsertAll(
            ).execute()
        
        query = cdc_stream.writeStream \
            .foreachBatch(upsert_to_delta) \
            .option("checkpointLocation", "s3://checkpoints/cdc-bookings/") \
            .trigger(processingTime="30 seconds") \
            .start()
        
        return query
    
    def backfill_historical_data(self, spark, start_date, end_date):
        """
        BACKFILL: Load historical data from MySQL snapshot.
        
        WARNING: Do NOT run backfill while CDC is running!
        Pause CDC -> Backfill -> Resume CDC.
        """
        snapshot_df = spark.read \
            .format("jdbc") \
            .option("url", "jdbc:mysql://read-replica:3306/bookings_db") \
            .option("dbtable", f"""
                (SELECT * FROM bookings 
                 WHERE booking_date BETWEEN '{start_date}' AND '{end_date}')
                AS tmp
            """) \
            .option("numPartitions", 100) \
            .option("partitionColumn", "booking_id") \
            .option("lowerBound", 1) \
            .option("upperBound", 100000000) \
            .load()
        
        snapshot_df.write \
            .mode("overwrite") \
            .partitionBy("booking_date") \
            .format("delta") \
            .save("s3://agoda-datalake/silver/bookings/")
```

## 3.3 Lambda vs Kappa Architecture

```python
architecture_comparison = {
    "Lambda Architecture": {
        "structure": "Batch Layer (Spark) + Speed Layer (Flink) -> Serving Layer",
        "pros": ["Accurate batch + low-latency speed", "Batch can fix speed layer errors"],
        "cons": ["TWO codebases to maintain", "Logic duplication risk", "Complex merge logic"],
        "use_when": "Need both historical accuracy AND real-time results",
    },
    
    "Kappa Architecture": {
        "structure": "Everything through Streaming Layer (Kafka + Flink)",
        "pros": ["Single codebase", "Simpler to maintain"],
        "cons": ["Reprocessing history requires replaying ALL events", "Complex state mgmt"],
        "use_when": "Real-time is primary requirement, batch is secondary",
    },
    
    "Agoda's Actual Approach": {
        "what": "HYBRID - Lambda-inspired with modern tooling",
        "batch_path": "Spark -> Delta Lake -> Feature Store (offline)",
        "streaming_path": "Kafka -> Flink -> Feature Store (online) + Redis",
        "serving": "Feature Store provides unified serving layer",
        "why": "Some features MUST be batch (90-day rolling avg), others MUST be real-time (live inventory)",
    },
}

# INTERVIEW TIP: Don't just say "Lambda" or "Kappa". Say:
# "I'd use a HYBRID approach because [specific features] need batch computation
#  while [other features] need real-time updates. The Feature Store provides the 
#  unified serving layer that abstracts away this complexity."
```

---

# 4. Data Modeling & Storage — Deep Dive <a name="4-data-modeling"></a>

## 4.1 Storage Selection Matrix

```python
storage_selection = {
    "Bookings, Payments, Inventory": {
        "storage": "PostgreSQL / MySQL",
        "why": "ACID transactions prevent double bookings",
        "scale": "Vertical + read replicas (10K-50K QPS reads)",
    },
    "Hotel Search (text, geo, filters)": {
        "storage": "Elasticsearch / OpenSearch",
        "why": "Inverted index for text, geo-point for location",
        "scale": "Horizontal sharding, 50K+ QPS",
    },
    "Feature Store, Session cache, Inventory counts": {
        "storage": "Redis / ScyllaDB",
        "why": "Sub-millisecond reads for serving",
        "scale": "Redis Cluster 1M+ QPS, ScyllaDB 10M+ QPS",
    },
    "Reporting, BI Dashboards, Ad-hoc queries": {
        "storage": "BigQuery / ClickHouse",
        "why": "Columnar, MPP query engine, PB-scale",
    },
    "Raw events, ML training data, archive": {
        "storage": "S3 + Delta Lake / Iceberg",
        "why": "Cheapest $/GB, schema evolution, time travel, ACID",
    },
}
```

## 4.2 OTA Data Model (Agoda-Specific)

```sql
-- FACT TABLE: Bookings (append-only, immutable events)
CREATE TABLE fact_bookings (
    booking_id          BIGINT PRIMARY KEY,
    user_id             BIGINT NOT NULL,
    hotel_id            BIGINT NOT NULL,
    room_type_id        INT NOT NULL,
    check_in_date       DATE NOT NULL,
    check_out_date      DATE NOT NULL,
    num_nights          INT NOT NULL,
    total_price_usd     DECIMAL(12,2) NOT NULL,
    commission_pct      DECIMAL(5,2),
    booking_status      VARCHAR(20),  -- confirmed, cancelled, completed, no_show
    booking_timestamp   TIMESTAMP NOT NULL,
    source_channel      VARCHAR(20),  -- web, mobile_app, api
    device_type         VARCHAR(10),
    booking_date        DATE NOT NULL  -- PARTITION KEY
)
PARTITION BY RANGE (booking_date);

-- WHY this design?
-- 1. Partitioned by booking_date (most queries filter by date)
-- 2. Separate fact from dimensions (star schema for analytics)
-- 3. Pre-computed num_nights (avoid date arithmetic in queries)
-- 4. USD normalization (consistent revenue comparison)

-- DIMENSION TABLE: Hotels (SCD Type 2 for history)
CREATE TABLE dim_hotels (
    hotel_sk            BIGINT PRIMARY KEY,  -- Surrogate key
    hotel_id            BIGINT NOT NULL,     -- Natural key
    hotel_name          VARCHAR(500),
    city                VARCHAR(100),
    country             CHAR(2),
    star_rating         DECIMAL(2,1),
    property_type       VARCHAR(50),
    total_rooms         INT,
    effective_from      DATE NOT NULL,
    effective_to        DATE DEFAULT '9999-12-31',
    is_current          BOOLEAN DEFAULT TRUE
);

-- WHY SCD Type 2?
-- Hotels change star ratings, names, ownership.
-- ML models need HISTORICAL state (what was the rating WHEN booking happened?)
-- Point-in-time correctness prevents data leakage in training!

-- REAL-TIME AVAILABILITY (Redis, not SQL!)
-- Key:   avail:{hotel_id}:{room_type}:{date}
-- Value: {available_count}
-- TTL:   48 hours
-- Why Redis? Sub-ms reads, atomic DECR on booking, TTL auto-cleans
```

## 4.3 Partitioning Strategies

```python
partitioning_guide = {
    "Rule 1": "Partition by the MOST COMMON filter in your queries",
    "Rule 2": "Aim for partition sizes between 128MB - 1GB (Spark optimal)",
    "Rule 3": "Too many partitions = small file problem (S3 listing slow)",
    "Rule 4": "Too few partitions = data skew (hot partitions)",
    
    "Good Examples": {
        "Booking events": "partition_by=booking_date (queries filter by date)",
        "Clickstream": "partition_by=(event_date, event_hour) (high volume needs finer grain)",
        "Hotel features": "partition_by=computation_date (daily recompute, easy rollback)",
    },
    
    "Anti-Patterns": {
        "BAD: partition_by=user_id": "50M users = 50M tiny partitions!",
        "BAD: partition_by=hotel_id": "Skewed: top hotels have millions of events",
        "BAD: partition_by=timestamp(second)": "86,400 partitions/day = small files",
    },
    
    "Fix for skew": "Partition by date, then Z-ORDER BY hotel_id within partitions",
}
```

---

# 5. Distributed Processing — Spark Deep Dive <a name="5-spark-deep-dive"></a>

## 5.1 Spark Internals You Must Know

```python
"""
SPARK EXECUTION MODEL:

1. USER CODE -> Driver Program
   Creates SparkSession, defines lazy transformations, triggers action

2. LOGICAL PLAN -> Catalyst Optimizer
   Parse -> Analyze -> Optimize -> Physical Plan

3. PHYSICAL PLAN -> DAGScheduler
   Splits into STAGES (separated by shuffles)
   Each stage = set of parallel TASKS

4. EXECUTION -> TaskScheduler -> Executors
   Each task processes ONE partition

KEY INSIGHT: SHUFFLES happen at STAGE BOUNDARIES.
Shuffles are the #1 performance killer in Spark.
Minimize shuffles = Optimize Spark

NARROW (no shuffle): map, filter, select, union
WIDE (shuffle!): groupBy, join, distinct, repartition, sort
"""
```

## 5.2 The 8 Commandments of Spark Optimization

```python
# 1. CHOOSE THE RIGHT FORMAT
# Delta Lake ~ Parquet > ORC >> JSON >> CSV
# Why Parquet? Columnar (reads only needed cols), Compression (75%+ I/O reduction),
# Statistics (skip irrelevant files)

# 2. FILTER EARLY, SELECT FEWER COLUMNS
# BAD:
bad = spark.read.parquet("s3://bookings/") \
    .join(hotels_df, "hotel_id") \
    .filter(F.col("booking_date") >= "2026-01-01") \
    .select("hotel_id", "total_price")

# GOOD:
from pyspark.sql.functions import broadcast
good = spark.read.parquet("s3://bookings/") \
    .select("hotel_id", "total_price", "booking_date") \
    .filter(F.col("booking_date") >= "2026-01-01") \
    .join(broadcast(hotels_df.select("hotel_id", "city")), "hotel_id")

# 3. HANDLE DATA SKEW
def handle_data_skew_salting(bookings_df, hotels_df, NUM_SALTS=10):
    """
    SALTING: Distribute hot keys across multiple partitions.
    Before: hotel_id "HILTON_BKK" -> single partition with 10M rows
    After:  Spread across 10 partitions with 1M rows each
    """
    # Salt the large table
    salted_bookings = bookings_df.withColumn(
        "hotel_id_salted",
        F.concat(F.col("hotel_id"), F.lit("_"), 
                 (F.rand() * NUM_SALTS).cast("int").cast("string"))
    )
    
    # Explode the small table to match all salt values
    salt_df = spark.range(NUM_SALTS).withColumnRenamed("id", "salt")
    exploded_hotels = hotels_df.crossJoin(salt_df).withColumn(
        "hotel_id_salted",
        F.concat(F.col("hotel_id"), F.lit("_"), F.col("salt").cast("string"))
    ).drop("salt")
    
    # Join on salted key - evenly distributed!
    return salted_bookings.join(exploded_hotels, "hotel_id_salted") \
        .drop("hotel_id_salted")


def handle_skew_two_phase_agg(bookings_df, NUM_SALTS=20):
    """TWO-PHASE AGGREGATION: Pre-aggregate before final groupBy."""
    # Phase 1: Partial aggregation with salt
    partial = bookings_df \
        .withColumn("salt", (F.rand() * NUM_SALTS).cast("int")) \
        .groupBy("hotel_id", "salt") \
        .agg(
            F.count("*").alias("partial_count"),
            F.sum("total_price").alias("partial_revenue"),
        )
    
    # Phase 2: Final aggregation without salt
    return partial.groupBy("hotel_id").agg(
        F.sum("partial_count").alias("total_bookings"),
        F.sum("partial_revenue").alias("total_revenue"),
    )


# 4. BROADCAST JOINS - Eliminate Shuffles
# Small table < 10MB -> broadcast to all executors -> NO shuffle of large table
# Tables to ALWAYS broadcast at Agoda:
#   dim_room_types (50K rows ~ 2MB), dim_countries (200 rows ~ 10KB)

# 5. ENABLE AQE (Adaptive Query Execution)
spark = SparkSession.builder \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.sql.adaptive.skewJoin.enabled", "true") \
    .getOrCreate()

# 6. EXECUTOR SIZING
"""
Given: 100 nodes, 16 cores, 64GB RAM each

Cores per executor: 5 (sweet spot, avoid GC pressure)
Executors per node: 3 (15 cores / 5)
Memory per executor: ~19 GB (63GB / 3, minus overhead)
Total executors: 299 (100 x 3 - 1 for AppMaster)

--num-executors 299
--executor-cores 5
--executor-memory 19g
--conf spark.sql.shuffle.partitions=600
"""

# 7. AVOID PYTHON UDFs - Use Built-in or Pandas UDFs
# Built-in: 10-100x faster than Python UDFs (Catalyst-optimized)
# If you MUST use UDF, use Pandas UDF (vectorized):
from pyspark.sql.functions import pandas_udf
import pandas as pd

@pandas_udf("float")
def calc_score_vectorized(price: pd.Series, rating: pd.Series) -> pd.Series:
    return price * 0.3 + rating * 0.7

# 8. READ THE SPARK UI
"""
Jobs Tab: Which job is slow?
Stages Tab: Which stage? Big shuffles? Task skew (max >> median)?
SQL Tab: BroadcastHashJoin vs SortMergeJoin? Predicate pushdown working?
Executors Tab: GC time > 10%? Memory balanced?
"""
```

---

# 6. Streaming & Event-Driven Systems <a name="6-streaming"></a>

## 6.1 Kafka Deep Dive (Agoda: 3T events/day)

```python
"""
AGODA'S KAFKA ARCHITECTURE:

1. MULTIPLE SMALL CLUSTERS (not one giant cluster)
   Why? Fault isolation. One cluster issue doesn't affect others.

2. 2-STEP LOGGING PATTERN
   App -> Local Disk -> Forwarder Daemon -> Kafka
   Why? App doesn't block if Kafka is slow.

3. MULTI-DC REPLICATION (Custom MirrorMaker 2)
   DC-1 <-> DC-2 with bidirectional offset sync
   Why? DR failover without data loss.
"""

kafka_deep_dive = {
    "Partitioning": {
        "key_rule": "Messages with same key -> same partition -> ordered",
        "sizing": "Start with 6-12 per topic, scale as needed",
        "gotcha": "NEVER change partition count on a topic with keyed messages!",
    },
    
    "Delivery Guarantees": {
        "at_most_once": "Commit offset before processing. Risk: data loss. Use for: logs",
        "at_least_once": "Process then commit. Risk: duplicates. Use for: most cases",
        "exactly_once": "Kafka Transactions. Cost: 20-30% throughput hit. Use for: financial data",
    },
    
    "Backpressure": {
        "symptoms": ["Consumer lag growing", "Memory pressure", "Latency increasing"],
        "solutions": [
            "Add more consumers (up to num_partitions)",
            "Increase batch size (fetch.max.bytes)",
            "Optimize consumer processing logic",
            "Rate limit producers",
        ],
        "monitoring": "Consumer lag = latest offset - consumer offset. Alert if > 5 min lag",
    },
    
    "Idempotent Consumer Pattern": {
        "problem": "At-least-once delivery can produce duplicates",
        "solutions": [
            "Use message key as dedup key in target system",
            "UPSERT / ON CONFLICT in database",
            "Track processed offsets in target system",
        ],
    },
}
```

## 6.2 Real-Time Price Update Pipeline

```python
class RealTimePriceUpdatePipeline:
    """
    Processes hotel price updates from Kafka in real-time.
    
    SLA: Price reflected in search within 5 seconds
    Scale: ~100K price updates/second during peak
    """
    
    def start_streaming(self, spark):
        price_stream = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "kafka:9092") \
            .option("subscribe", "hotel-price-updates") \
            .option("startingOffsets", "latest") \
            .option("maxOffsetsPerTrigger", 50000) \
            .load()
        
        def process_batch(batch_df, batch_id):
            if batch_df.isEmpty():
                return
            
            # 1. Update Redis (for real-time availability)
            self._update_redis_cache(batch_df)
            
            # 2. Update Elasticsearch (for search results)
            self._update_elasticsearch(batch_df)
            
            # 3. Append to Delta Lake (for analytics)
            batch_df.write.mode("append").format("delta") \
                .save("s3://agoda-datalake/silver/price_updates/")
        
        query = price_stream.writeStream \
            .foreachBatch(process_batch) \
            .option("checkpointLocation", "s3://checkpoints/price-updates/") \
            .trigger(processingTime="5 seconds") \
            .start()
        
        return query
    
    def _update_redis_cache(self, batch_df):
        """
        Use Redis PIPELINE for batch updates.
        Individual SETs: 100K x 0.5ms = 50 seconds
        Pipelined SETs: 100K batched = 0.5 seconds
        """
        import redis
        r = redis.Redis(host='redis-cluster', port=6379)
        pipe = r.pipeline()
        
        updates = batch_df.select("hotel_id", "room_type_id", "date", "price_usd").collect()
        
        for row in updates:
            key = f"price:{row.hotel_id}:{row.room_type_id}:{row.date}"
            pipe.set(key, str(row.price_usd))
            pipe.expire(key, 172800)  # 48h TTL
        
        pipe.execute()  # Single round-trip!
```

---

# 7. Performance & Scalability at 1M+ QPS <a name="7-performance"></a>

## 7.1 Scaling Progression

```python
scaling_progression = {
    "10K QPS": {
        "db": "Single PostgreSQL + read replica",
        "cache": "Single Redis",
        "pipeline": "Cron-based batch jobs",
    },
    "100K QPS": {
        "db": "Read replicas, connection pooling (PgBouncer)",
        "cache": "Redis Cluster, cache warming",
        "pipeline": "Spark + Airflow, CQRS pattern",
    },
    "500K QPS": {
        "db": "Sharding by region/hotel_id",
        "cache": "Multi-tier (L1: local, L2: Redis)",
        "pipeline": "Real-time streaming for critical paths",
    },
    "1M+ QPS (Agoda)": {
        "db": "Polyglot persistence (specialized DB per use case)",
        "cache": "THREE-TIER: CDN -> App local cache -> Redis -> DB",
        "pipeline": "Unified streaming platform (Kafka backbone)",
        "architecture": "Multi-DC active-active, circuit breakers everywhere",
    },
}
```

## 7.2 Caching Strategies

```python
caching_patterns = {
    "Cache-Aside": {
        "flow": "App checks cache -> miss -> query DB -> write to cache",
        "when": "Most use cases (default choice)",
        "gotcha": "Thundering herd when TTL expires. Fix: add jitter to TTL",
    },
    "Write-Through": {
        "flow": "Write to cache AND DB simultaneously",
        "when": "Data that MUST be consistent (inventory)",
    },
    "Write-Behind": {
        "flow": "Write to cache first, async write to DB",
        "when": "Analytics events, non-critical data",
    },
}

cache_stampede_prevention = """
PROBLEM: Popular key expires -> 10K requests hit DB simultaneously

SOLUTION: Mutex Lock Pattern
def get_hotel_with_lock(hotel_id):
    cached = redis.get(f"hotel:{hotel_id}")
    if cached:
        return json.loads(cached)
    
    # Try to acquire lock
    acquired = redis.set(f"lock:hotel:{hotel_id}", "1", nx=True, ex=5)
    
    if acquired:
        hotel = db.query("SELECT * FROM hotels WHERE id = %s", hotel_id)
        redis.setex(f"hotel:{hotel_id}", 3600, json.dumps(hotel))
        redis.delete(f"lock:hotel:{hotel_id}")
        return hotel
    else:
        time.sleep(0.05)  # Wait for other request to populate cache
        return get_hotel_with_lock(hotel_id)
"""
```

## 7.3 Real-World Challenges at 1M+ QPS

```python
extreme_scale_challenges = {
    "Thundering Herd": {
        "scenario": "Flash sale -> 10M users search simultaneously",
        "solutions": [
            "Rate limiting at API gateway",
            "Request coalescing (batch identical requests)",
            "Cache pre-warming for anticipated popular queries",
            "Queue-based load leveling via Kafka",
            "Graceful degradation (serve stale cached results)",
        ],
    },
    
    "Tail Latency (p99 vs p50)": {
        "scenario": "p50=20ms but p99=2000ms",
        "causes": ["GC pauses", "Network congestion", "DB lock contention", "Cold cache"],
        "solutions": {
            "Hedged Requests": "Send to 2 replicas, take first response",
            "Timeouts": "Hard 100ms timeout + fallback to cached result",
            "Pre-warm": "Background threads refresh hot data before expiry",
        },
    },
    
    "Data Consistency at Scale": {
        "scenario": "User books room, but cache shows available -> double booking!",
        "solution": {
            "Search": "Uses cache (eventual consistency OK for search results)",
            "Booking": "Uses DB with optimistic locking (strong consistency)",
            "Pattern": "UPDATE inventory SET count=count-1 WHERE hotel_id=X AND version=V",
        },
    },
    
    "Large-Scale Data Backfill": {
        "scenario": "Bug produced wrong features for 90 days. Need to recompute.",
        "optimized_approach": [
            "1. Identify affected date range",
            "2. Scale up temporary Spark cluster",
            "3. Process ALL dates in parallel (not sequential)",
            "4. Write to separate output path",
            "5. Validate: compare old vs new features",
            "6. Atomic swap in feature store",
            "7. Scale down temporary cluster",
        ],
    },
}
```

---

# 8. Operational Excellence <a name="8-ops-excellence"></a>

## 8.1 Data Quality Framework

```python
class DataQualityFramework:
    """
    VACCF Framework:
    V - Volume: Expected record count
    A - Accuracy: Values are correct
    C - Completeness: No missing required fields
    C - Consistency: Follows business rules
    F - Freshness: Data is up-to-date
    """
    
    def check_volume(self, df, table_name, min_records, max_records):
        count = df.count()
        if count < min_records or count > max_records:
            alert(f"VOLUME ISSUE: {table_name} has {count} records")
    
    def check_completeness(self, df, required_columns, max_null_pct=0.01):
        for col_name in required_columns:
            null_pct = df.filter(F.col(col_name).isNull()).count() / df.count()
            if null_pct > max_null_pct:
                alert(f"NULL ISSUE: {col_name} has {null_pct:.2%} NULLs")
    
    def check_freshness(self, df, timestamp_col, max_lag_minutes=60):
        latest = df.agg(F.max(timestamp_col)).collect()[0][0]
        lag = (datetime.now() - latest).total_seconds() / 60
        if lag > max_lag_minutes:
            alert(f"FRESHNESS: Latest record is {lag:.0f} min old")
    
    def check_anomaly(self, current_value, historical_mean, historical_stddev):
        z_score = abs(current_value - historical_mean) / max(historical_stddev, 1e-6)
        if z_score > 3:
            alert(f"ANOMALY: z-score={z_score:.2f}")
```

## 8.2 Monitoring Design

```python
monitoring_design = {
    "Pipeline Health": {
        "latency": "End-to-end: source -> serving (target: < 30 min for batch)",
        "throughput": "Records/sec at each stage, baseline deviation",
        "error_rate": "% records failing quality checks (target: < 0.1%)",
        "consumer_lag": "Kafka consumer lag (target: < 10K messages)",
    },
    
    "Alert Severity": {
        "P0 Critical": "Pipeline stopped, data loss -> PagerDuty, 15 min response",
        "P1 High": "Pipeline delayed > 2x SLA -> Slack, 1 hour response",
        "P2 Medium": "Slower than usual but within SLA -> Email, next business day",
    },
    
    "Best Practices": [
        "Every alert MUST have a runbook link",
        "Group related alerts to avoid notification storms",
        "Track MTTR (Mean Time To Recovery) per alert type",
        "Review alert effectiveness monthly",
    ],
}
```

## 8.3 Disaster Recovery

```python
disaster_recovery = {
    "Kafka": {
        "strategy": "Multi-DC replication with MirrorMaker 2",
        "rpo": "< 1 second", "rto": "< 5 minutes",
    },
    "Delta Lake": {
        "strategy": "S3 cross-region replication + time travel",
        "rpo": "< 15 minutes", "rto": "< 1 hour",
    },
    "Feature Store (Redis)": {
        "strategy": "Redis Cluster with AOF + cross-DC replica",
        "rpo": "< 1 second", "rto": "< 5 minutes",
        "gotcha": "If both fail -> rebuild from Delta Lake (1-2 hours)",
    },
    "Key Principle": "Pipelines must be IDEMPOTENT for safe recovery",
}
```

---

# 9. ML Feature Store Design <a name="9-feature-store"></a>

```python
"""
WHY A FEATURE STORE?

Problem 1: Training-Serving Skew
  Data scientist computes features in pandas -> works offline
  ML engineer reproduces in production -> different values!

Problem 2: Feature Duplication
  Team A computes "avg_price_7d" for ranking
  Team B computes "avg_price_7d" for pricing  
  Different implementations, different results!

Problem 3: Point-in-Time Correctness (Data Leakage)
  Training data must use feature values AT TIME OF EVENT (not latest!)
  Without feature store -> accidentally use future data -> leakage

AGODA'S ARCHITECTURE:
- Offline Store: Delta Lake (S3) - full history, point-in-time joins
- Online Store: ScyllaDB + Redis - latest values, <10ms p99 reads
- Serving migrated from JVM to Scala, experimented with Rust for latency
- P99 latency SLA: 10ms at millions of QPS
"""

class FeatureStoreGuide:
    """Guide for discussing feature store in interviews."""
    
    training_serving_skew_prevention = """
    SOLUTION: Single feature definition used by BOTH pipelines.
    
    Training: Point-in-time correct join
      For each (hotel_id, event_timestamp), fetch features 
      AS THEY WERE at event_timestamp - NOT latest values!
      This prevents DATA LEAKAGE.
    
    Serving: Online lookup
      For each hotel_id, fetch LATEST feature values.
      Latency target: < 10ms for batch of 500 hotels.
    
    Fallback: If feature store is down:
      1. Local cache (5-min TTL)
      2. Default feature values
      3. Rule-based ranking (no ML)
    """
```

---

# 10. OTA System Design Problems <a name="10-ota-designs"></a>

## 10.1 Hotel Search Pipeline Architecture

```
User Query ("Bangkok, July 15-18, 2 adults")
     |
     v
API GATEWAY (rate limiting, auth, A/B routing)
     |
     v
SEARCH ORCHESTRATOR (manages multi-step flow, timeouts, fallbacks)
     |
     |--> Step 1: Elasticsearch (Candidate Retrieval, top 500)
     |
     |--> Step 2: Redis (Availability Filter, ~300 remain)
     |
     |--> Step 3: Feature Store + ML Model (Ranking, final score)
     |
     |--> Step 4: Business Rules (sponsored, diversity, re-rank)
     |
     v
Final Ranked Results (Top 20 per page)

DATA PIPELINES FEEDING THIS:
1. Hotel Index Pipeline (batch daily): Silver hotels -> ES bulk index
2. Inventory Pipeline (streaming): MySQL CDC -> Kafka -> Redis
3. Feature Pipeline (batch+stream): Logs -> Spark/Flink -> Feature Store
4. ML Training Pipeline (batch daily): Feature Store -> Spark ML -> ONNX
```

## 10.2 Booking Event Processing Pipeline

```
Booking Service (MySQL)
     | (Debezium CDC)
     v
Kafka Topic: booking-events (partitioned by user_id)
     |
     |--> Consumer 1: Redis Cache Update (inventory DECR/INCR)
     |--> Consumer 2: Elasticsearch Update (hotel doc update)  
     |--> Consumer 3: Analytics Pipeline (Delta Lake append)
     |--> Consumer 4: Notification Service (email/push)
     |--> Consumer 5: Feature Pipeline (ML feature recompute)
     |--> Consumer 6: Fraud Detection (real-time scoring)

Each consumer is a separate CONSUMER GROUP
-> Independent processing, independent offset tracking
-> If one consumer is slow, others are unaffected
```

## 10.3 Clickstream Analytics (3T events/day)

```
Browser/App SDK (batch 20 events, send every 5 sec)
     |
     v
Collection Service (Nginx + Go)
  -> Validate schema
  -> Enrich with geo_ip, device_info
  -> Write to LOCAL DISK (2-step pattern)
  -> Forwarder daemon -> Kafka
     |
     v
Kafka (segmented clusters by event type)
  clicks: 500 partitions
  searches: 300 partitions
  page-views: 1000 partitions
     |
     |-> REAL-TIME: Flink -> Redis/InfluxDB -> Grafana dashboards
     |-> BATCH: Spark -> Bronze -> Silver -> Gold -> Feature Store -> BigQuery
```

---

# 11. Common Mistakes & Edge Cases <a name="11-mistakes"></a>

## 11.1 Top 15 Interview Mistakes

```python
mistakes = {
    "1: Starting with tech, not requirements": 
        "WRONG: 'I'll use Kafka'. RIGHT: 'Given 100K eps with at-least-once, Kafka fits because...'",
    
    "2: Not discussing trade-offs":
        "Every decision has trade-offs. Always say 'The downside is...'",
    
    "3: Overengineering for given scale":
        "At 1000 users/day, you don't need Kafka + multi-DC",
    
    "4: Not handling late-arriving data":
        "Use watermarks. Events beyond watermark go to 'late events' for batch reprocess",
    
    "5: Not making pipelines idempotent":
        "Use UPSERT/MERGE, not append. Pipelines WILL fail and re-run.",
    
    "6: Ignoring data quality":
        "Quality checks at each medallion layer. Failed checks block downstream.",
    
    "7: Using Python UDFs":
        "Built-in functions are 10-100x faster. Use Pandas UDFs if custom logic needed.",
    
    "8: Not mentioning data skew":
        "Top 1% of hotels = 80% of bookings. Always discuss skew handling.",
    
    "9: collect() on large datasets":
        "Keeps processing in Spark. Only collect small final results.",
    
    "10: One database for everything":
        "Polyglot persistence: right DB for right use case.",
    
    "11: Wrong partitioning key":
        "Partition by date (manageable). Z-order by entity within partition.",
    
    "12: No monitoring discussion":
        "Always mention: latency, throughput, quality metrics, alerting with runbooks.",
    
    "13: No fallback strategy":
        "If ML fails -> rule-based ranking. System stays up with degraded quality.",
    
    "14: Not considering schema evolution":
        "Avro + Schema Registry for Kafka. Delta Lake mergeSchema for storage.",
    
    "15: Not connecting to OTA domain":
        "Mention: seasonality, multi-currency, L2B ratio, cold start, supplier diversity.",
}
```

## 11.2 Edge Cases at Scale

```python
edge_cases = {
    "Timezone Hell": {
        "problem": "User in NYC, hotel in Bangkok, server in Singapore. Which timezone?",
        "solution": "ALWAYS store UTC. Convert to local only at display layer.",
    },
    "Phantom Availability": {
        "problem": "Search shows available (cached). User clicks -> just booked by someone else.",
        "solution": "Search uses cache (eventual OK). Booking uses DB with optimistic lock.",
    },
    "Duplicate Booking": {
        "problem": "User double-clicks 'Book Now'.",
        "solution": "Idempotency key on client. Server: UNIQUE constraint on request_id.",
    },
    "Hot Kafka Partition": {
        "problem": "Viral hotel gets 1000x traffic on one partition.",
        "solution": "Random partitioning for high-volume topics, or compound key with salt.",
    },
    "S3 Throttling": {
        "problem": "10K+ files in one S3 prefix -> 5,500 GET/s limit.",
        "solution": "Hash-based prefix, Delta Lake metadata listing, compact small files.",
    },
    "Feature Store Down": {
        "problem": "ML model can't get features. All search fails!",
        "solution": "L1: Local cache | L2: Default values | L3: Rule-based ranking (no ML)",
    },
}
```

---

# 12. Mock Interview Q&A <a name="12-mock-qa"></a>

## 12.1 Rapid-Fire Technical Questions

```python
rapid_fire = {
    "Parquet vs ORC?": 
        "Both columnar. Parquet: better ecosystem (Spark, Presto). Use Parquet by default.",
    
    "Delta Lake vs Iceberg vs Hudi?":
        "Delta: best Spark integration. Iceberg: best multi-engine. Hudi: best for CDC upserts.",
    
    "Star schema vs Snowflake schema?":
        "Star: denormalized, fewer joins, faster analytics. Snowflake: normalized, less storage. "
        "For OLAP: use star schema.",
    
    "Spark RDD vs DataFrame?":
        "DataFrame: Catalyst optimization, 10-100x faster. Avoid RDDs in modern Spark.",
    
    "Flink vs Spark Streaming?":
        "Flink: true per-event, lower latency. Spark SS: micro-batch, better for batch+stream unified.",
    
    "What is backfilling?":
        "Recomputing historical data. Needed for: bug fixes, new features, data migration. "
        "Requires idempotent pipelines.",
    
    "How prevent double booking?":
        "Optimistic locking: UPDATE rooms SET booked=1 WHERE hotel=X AND version=V. "
        "If affected_rows=0 -> retry or fail.",
    
    "Kafka retention vs compaction?":
        "Retention: delete after N days (for event streams). "
        "Compaction: keep latest per key (for state/snapshots).",
    
    "What is data lineage?":
        "Tracking data flow from source to destination. For: debugging, compliance (GDPR), "
        "impact analysis. Tools: Apache Atlas, DataHub.",
    
    "Small file problem?":
        "Too many small files -> task scheduling overhead >> actual work. "
        "Fix: compact, coalesce before write, Delta OPTIMIZE command.",
    
    "Exactly-once semantics?":
        "In Kafka: idempotent producer + transactions. "
        "External: idempotent consumers (UPSERT, track offsets in target).",
    
    "How debug slow Spark job?":
        "Jobs tab -> Stages tab -> Task distribution (max vs median = skew). "
        "SQL tab -> join types, predicate pushdown. Executors tab -> GC time.",
    
    "Schema evolution strategy?":
        "Kafka: Avro + Schema Registry (backward/forward compatible). "
        "Storage: Delta Lake mergeSchema. "
        "Breaking changes: dual-write migration pattern.",
}
```

---

## Final Cheat Sheet

```
┌──────────────────────────────────────────────────────────────────────┐
│                   PRE-INTERVIEW CHECKLIST                             │
│                                                                        │
│  BEFORE ANSWERING:                                                    │
│  [ ] Ask clarifying questions (scale, latency, consistency)          │
│  [ ] State assumptions explicitly                                     │
│  [ ] Draw data flow (source -> ingestion -> processing -> serving)   │
│                                                                        │
│  WHILE DESIGNING:                                                     │
│  [ ] Justify EVERY technology choice ("I chose X because...")        │
│  [ ] Mention trade-offs ("The downside is...")                       │
│  [ ] Think about failure modes ("If this fails...")                   │
│  [ ] Consider data quality ("How do we ensure correctness?")         │
│                                                                        │
│  ALWAYS MENTION FOR AGODA:                                           │
│  [ ] Seasonality (3x traffic during holidays)                        │
│  [ ] Look-to-Book ratio (1000 searches per booking)                  │
│  [ ] Cold start (new hotels with no data)                            │
│  [ ] Supplier diversity (10K+ different APIs)                        │
│  [ ] Inventory consistency (can't show booked rooms)                 │
│                                                                        │
│  KEY NUMBERS:                                                         │
│  - 1 day ~ 100K seconds                                              │
│  - 1M req/day ~ 12 QPS                                               │
│  - Agoda: 3T events/day, 2.5M properties, 50K search QPS peak      │
│  - Redis GET: 0.5ms | MySQL: 5-50ms | S3 GET: 50-200ms             │
│                                                                        │
│  AGODA'S TECH STACK:                                                 │
│  Processing: Spark (batch), Flink (streaming)                        │
│  Messaging: Kafka (3T events/day, multi-DC)                          │
│  Storage: Delta Lake, S3, ScyllaDB, Redis, Elasticsearch            │
│  ML: Feature Store (ScyllaDB-backed), ONNX, MLflow                  │
│  Orchestration: Airflow / Kubeflow                                    │
└──────────────────────────────────────────────────────────────────────┘
```

---

> **Next Step:** Study this notebook, then let's do a live mock interview where I'll play the Agoda interviewer and challenge your designs in real-time!
