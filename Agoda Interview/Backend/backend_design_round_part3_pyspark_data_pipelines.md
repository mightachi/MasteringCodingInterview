# 🔥 Agoda Backend Design Round — Part 3: PySpark, Data Pipelines & Distributed Systems

## 📋 Table of Contents
1. [PySpark Deep Dive — From Basics to Optimization](#1-pyspark)
2. [Data Pipeline Architecture](#2-data-pipeline)
3. [SQL for ML Engineers](#3-sql)
4. [Kafka, Streaming & Event-Driven Architecture](#4-kafka)
5. [Distributed Systems Concepts](#5-distributed-systems)
6. [Hadoop Ecosystem](#6-hadoop)

---

## 1. PySpark Deep Dive <a name="1-pyspark"></a>

### 🎯 Why PySpark Matters for Agoda

From the JD: *"Good experience in PySpark"* and *"Build, administer and scale ML processing pipelines"*

Agoda processes **1.8 trillion messages daily**. PySpark is their workhorse for:
- Feature engineering at scale
- Training data preparation
- Batch inference pipelines
- ETL and data quality checks

### 1.1 Spark Architecture — Understand the Internals

```python
# ==========================================================
# SPARK ARCHITECTURE — What Happens When You Run a Spark Job
# ==========================================================

"""
SPARK EXECUTION FLOW:
====================

1. DRIVER PROGRAM
   ├── Creates SparkContext / SparkSession
   ├── Defines transformations and actions
   └── Sends DAG to Cluster Manager

2. CLUSTER MANAGER (YARN / Kubernetes)
   ├── Allocates resources (executors)
   └── Monitors executor health

3. EXECUTORS (Worker Nodes)
   ├── Execute tasks in parallel
   ├── Store data in memory (cached RDDs)
   └── Report results back to Driver

KEY CONCEPTS:
=============
• DAG (Directed Acyclic Graph): Spark builds a plan of operations
• Stage: Group of tasks that can run in parallel (separated by shuffles)
• Task: Smallest unit of work, runs on ONE partition
• Shuffle: Expensive data exchange between executors (disk I/O + network)
• Partition: Chunk of data processed by one task

MEMORY MODEL:
=============
Executor Memory = Execution Memory + Storage Memory + User Memory + Reserved
├── Execution Memory:  Shuffles, joins, sorts, aggregations
├── Storage Memory:    Cached DataFrames/RDDs
├── User Memory:       User-defined data structures, UDFs
└── Reserved Memory:   Spark internal (300MB fixed)

Unified Memory Management (since Spark 1.6):
├── Execution and Storage share a pool
├── Execution can borrow from Storage (and evict cached data)
└── Storage can borrow from Execution (when Execution is not using it)
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType


# ==========================================================
# CREATING SPARK SESSION (for interviews, show you know config)
# ==========================================================

spark = SparkSession.builder \
    .appName("HotelFeatureEngineering") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.default.parallelism", "100") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.sql.parquet.compression.codec", "snappy") \
    .getOrCreate()

# WHY these configs?
spark_config_explanation = {
    "shuffle.partitions": "Default 200. Increase for large data, decrease for small.",
    "adaptive.enabled": "AQE: Spark auto-optimizes shuffle partitions at runtime",
    "adaptive.coalescePartitions": "Merges small partitions post-shuffle → fewer tasks",
    "KryoSerializer": "10x faster serialization than Java default",
    "parquet + snappy": "Columnar format + fast compression → optimal I/O",
}
```

### 1.2 Feature Engineering with PySpark

```python
# ==========================================================
# REAL EXAMPLE: Hotel Feature Engineering Pipeline
# ==========================================================

def engineer_hotel_features(bookings_df, clicks_df, reviews_df):
    """
    Feature engineering pipeline for hotel ranking model.
    
    Input DataFrames:
    - bookings_df: booking history (hotel_id, user_id, booking_date, price, ...)
    - clicks_df: click events (hotel_id, user_id, timestamp, position, ...)
    - reviews_df: review data (hotel_id, rating, review_text, review_date, ...)
    
    Output: Feature DataFrame (hotel_id → feature vector)
    """
    
    # ==========================================
    # AGGREGATION FEATURES (hotel-level)
    # ==========================================
    
    hotel_booking_features = bookings_df \
        .groupBy("hotel_id") \
        .agg(
            F.count("*").alias("total_bookings"),
            F.countDistinct("user_id").alias("unique_bookers"),
            F.avg("price").alias("avg_booking_price"),
            F.stddev("price").alias("price_stddev"),
            F.avg("stay_duration").alias("avg_stay_duration"),
            F.sum(F.when(F.col("is_cancelled") == True, 1).otherwise(0))
                .alias("cancellation_count"),
        )
    
    # ==========================================
    # WINDOW FEATURES (time-based trends)
    # ==========================================
    
    # Bookings in last 7 days, 30 days, 90 days
    # WHY? Captures recent popularity trends
    
    now = F.current_timestamp()
    
    hotel_trend_features = bookings_df \
        .groupBy("hotel_id") \
        .agg(
            F.sum(F.when(
                F.datediff(now, F.col("booking_date")) <= 7, 1
            ).otherwise(0)).alias("bookings_last_7d"),
            
            F.sum(F.when(
                F.datediff(now, F.col("booking_date")) <= 30, 1
            ).otherwise(0)).alias("bookings_last_30d"),
            
            F.sum(F.when(
                F.datediff(now, F.col("booking_date")) <= 90, 1
            ).otherwise(0)).alias("bookings_last_90d"),
        )
    
    # Booking velocity: is popularity increasing or decreasing?
    # bookings_last_7d / bookings_last_30d → > 0.25 means trending up
    
    # ==========================================
    # CLICK-THROUGH RATE (CTR) FEATURES
    # ==========================================
    
    ctr_features = clicks_df \
        .groupBy("hotel_id") \
        .agg(
            F.count("*").alias("total_impressions"),
            F.sum(F.when(F.col("is_clicked") == True, 1).otherwise(0))
                .alias("total_clicks"),
        ) \
        .withColumn("ctr", F.col("total_clicks") / F.col("total_impressions"))
    
    # ==========================================
    # REVIEW FEATURES
    # ==========================================
    
    review_features = reviews_df \
        .groupBy("hotel_id") \
        .agg(
            F.count("*").alias("review_count"),
            F.avg("rating").alias("avg_rating"),
            F.percentile_approx("rating", 0.5).alias("median_rating"),
            F.stddev("rating").alias("rating_variance"),
            # Recent reviews matter more
            F.avg(
                F.when(F.datediff(now, F.col("review_date")) <= 90, F.col("rating"))
            ).alias("recent_avg_rating"),
        )
    
    # ==========================================
    # JOIN ALL FEATURES
    # ==========================================
    
    # WHY left join? Hotels without bookings/clicks should still appear
    # with NULL features (handled by model or filled with defaults)
    
    final_features = hotel_booking_features \
        .join(hotel_trend_features, "hotel_id", "left") \
        .join(ctr_features, "hotel_id", "left") \
        .join(review_features, "hotel_id", "left") \
        .fillna(0)  # Fill nulls with 0 for numeric features
    
    return final_features


# ==========================================================
# USER FEATURE ENGINEERING
# ==========================================================

def engineer_user_features(bookings_df, clicks_df):
    """User-level feature engineering."""
    
    # User booking preferences
    user_features = bookings_df \
        .groupBy("user_id") \
        .agg(
            F.count("*").alias("lifetime_bookings"),
            F.avg("price").alias("avg_spend"),
            F.avg("star_rating").alias("preferred_stars"),
            F.avg("stay_duration").alias("avg_stay"),
            F.countDistinct("destination").alias("destinations_visited"),
            
            # Recency: days since last booking
            F.datediff(F.current_timestamp(), F.max("booking_date"))
                .alias("days_since_last_booking"),
            
            # Price sensitivity
            F.stddev("price").alias("price_sensitivity"),
        )
    
    # Session-level features (real-time, from clicks)
    window_spec = Window \
        .partitionBy("user_id", "session_id") \
        .orderBy("timestamp")
    
    session_features = clicks_df \
        .withColumn("click_order", F.row_number().over(window_spec)) \
        .withColumn("time_on_page", 
            F.lead("timestamp").over(window_spec) - F.col("timestamp")) \
        .groupBy("user_id", "session_id") \
        .agg(
            F.count("*").alias("clicks_in_session"),
            F.avg("time_on_page").alias("avg_time_on_page"),
            F.countDistinct("hotel_id").alias("hotels_viewed"),
        )
    
    return user_features, session_features
```

### 1.3 PySpark Optimization — Interview Must-Knows

```python
# ==========================================================
# OPTIMIZATION TECHNIQUES — What Agoda WILL Ask About
# ==========================================================

# ─────────────────────────────────────────────
# 1. BROADCAST JOINS (Small table × Large table)
# ─────────────────────────────────────────────

# PROBLEM: Joining a 100M row bookings table with a 10K row hotels table
# DEFAULT: Shuffle join (expensive — moves 100M rows across network!)
# SOLUTION: Broadcast the small table to all executors

# BAD: Shuffle join on large × small ❌
result = large_df.join(small_df, "hotel_id")

# GOOD: Broadcast join ✅
from pyspark.sql.functions import broadcast
result = large_df.join(broadcast(small_df), "hotel_id")

# WHEN: Small table < 10MB (auto-broadcast threshold)
# spark.sql.autoBroadcastJoinThreshold = 10MB (default)

# ─────────────────────────────────────────────
# 2. PARTITIONING STRATEGIES
# ─────────────────────────────────────────────

# repartition vs coalesce:
# repartition(N): Full shuffle → N partitions (use to INCREASE partitions)
# coalesce(N):    No shuffle → merge to N partitions (use to DECREASE partitions)

# BAD: repartition to decrease (triggers unnecessary shuffle) ❌
df = df.repartition(10)  # From 1000 → 10 partitions WITH shuffle

# GOOD: coalesce to decrease (no shuffle) ✅
df = df.coalesce(10)     # From 1000 → 10 partitions WITHOUT shuffle

# GOOD: repartition to increase parallelism
df = df.repartition(200)  # Increase for better parallelism

# BEST: Partition by key for downstream operations
df = df.repartition("hotel_id")  # All rows for same hotel → same partition
# Now groupBy("hotel_id") requires NO shuffle!


# ─────────────────────────────────────────────
# 3. HANDLING DATA SKEW
# ─────────────────────────────────────────────

# PROBLEM: 80% of bookings are for top 1% of hotels
# RESULT: Executor 1 processes 80M rows, others process 1M → stragglers!

# SOLUTION 1: Salting (add random suffix to skewed key)
import random

def salt_key(df, key_col, num_salts=10):
    """Add salt to distribute skewed keys across partitions."""
    return df.withColumn(
        f"{key_col}_salted",
        F.concat(F.col(key_col), F.lit("_"), F.lit(random.randint(0, num_salts)))
    )

# SOLUTION 2: Adaptive Query Execution (AQE) — Spark 3.0+
# spark.sql.adaptive.enabled = true
# spark.sql.adaptive.skewJoin.enabled = true
# Spark auto-detects skew and splits large partitions


# ─────────────────────────────────────────────
# 4. CACHING & PERSISTENCE
# ─────────────────────────────────────────────

# RULE: Cache DataFrames that are used MORE THAN ONCE
# DON'T cache data used only once!

# Cache in memory (default: MEMORY_AND_DISK)
features_df = engineer_hotel_features(bookings, clicks, reviews)
features_df.cache()  # Lazily cached on first action

# Or persist with specific level
from pyspark import StorageLevel
features_df.persist(StorageLevel.MEMORY_AND_DISK_SER)  # Serialized = less memory

# ALWAYS unpersist when done
features_df.unpersist()

# ─────────────────────────────────────────────
# 5. PREDICATE PUSHDOWN & COLUMN PRUNING
# ─────────────────────────────────────────────

# GOOD: Filter early, select only needed columns ✅
df = spark.read.parquet("s3://data/bookings/") \
    .select("hotel_id", "user_id", "price", "booking_date") \
    .filter(F.col("booking_date") >= "2024-01-01")

# BAD: Read everything then filter ❌
df = spark.read.parquet("s3://data/bookings/")
# ... many transformations ...
df = df.select("hotel_id", "price")  # Too late! Already read all columns

# Parquet + filter pushdown: Spark reads ONLY relevant row groups
# This can reduce I/O by 90%+


# ─────────────────────────────────────────────
# 6. UDF vs BUILT-IN FUNCTIONS
# ─────────────────────────────────────────────

# BAD: Python UDF (slow — serialization overhead) ❌
from pyspark.sql.functions import udf

@udf(FloatType())
def calc_score(price, rating):
    return price * 0.3 + rating * 0.7

df = df.withColumn("score", calc_score("price", "rating"))

# GOOD: Built-in functions (optimized by Catalyst) ✅
df = df.withColumn("score", F.col("price") * 0.3 + F.col("rating") * 0.7)

# If you MUST use UDF, use Pandas UDF (vectorized) ✅
from pyspark.sql.functions import pandas_udf
import pandas as pd

@pandas_udf(FloatType())
def calc_score_vectorized(price: pd.Series, rating: pd.Series) -> pd.Series:
    return price * 0.3 + rating * 0.7

df = df.withColumn("score", calc_score_vectorized("price", "rating"))
# Pandas UDF: 10-100x faster than regular Python UDF


# ─────────────────────────────────────────────
# 7. EXPLAIN PLAN — Debug Performance
# ─────────────────────────────────────────────

# Use .explain() to understand query plan
result_df.explain(mode="extended")

# Look for:
# ✅ BroadcastHashJoin (good for small tables)
# ❌ SortMergeJoin (expensive shuffle — consider broadcast)
# ✅ FileScan with PushedFilters (predicate pushdown working)
# ❌ Exchange (shuffle — consider repartitioning)
```

### 1.4 PySpark Interview Questions & Answers

```python
# ==========================================================
# TOP PYSPARK INTERVIEW QUESTIONS FOR AGODA
# ==========================================================

pyspark_qa = {
    "Q1: Transformation vs Action?": {
        "Transformations": "Lazy operations that build the DAG (map, filter, select, groupBy, join)",
        "Actions": "Trigger execution and return results (collect, count, show, write, take)",
        "Key": "Spark does NOTHING until an action is called! This is LAZY EVALUATION.",
        "Benefit": "Allows Catalyst optimizer to merge and optimize the entire plan",
    },
    
    "Q2: Narrow vs Wide Transformations?": {
        "Narrow": "Each input partition contributes to ONE output partition (map, filter, union)",
        "Wide": "Input partitions contribute to MULTIPLE output partitions (groupBy, join, sort)",
        "Key": "Wide transformations trigger SHUFFLES (expensive!)",
        "Interview Tip": "Minimize wide transformations. Use broadcast joins when possible.",
    },
    
    "Q3: How to handle Out of Memory errors?": {
        "Driver OOM": [
            "Reduce data collected to driver (avoid .collect() on large data)",
            "Increase spark.driver.memory",
            "Use .take(N) instead of .collect()",
        ],
        "Executor OOM": [
            "Increase spark.executor.memory",
            "Reduce partition size (repartition to more partitions)",
            "Use MEMORY_AND_DISK persistence instead of MEMORY_ONLY",
            "Check for data skew (one partition much larger than others)",
            "Reduce spark.memory.fraction if too much storage memory",
        ],
    },
    
    "Q4: Spark SQL vs DataFrame API?": {
        "Both": "Generate the same execution plan (Catalyst optimizer)",
        "SQL": "Better for complex analytics, familiar to data analysts",
        "DataFrame": "Better for programmatic pipelines, type-safe, better IDE support",
        "Best Practice": "Use DataFrame API in ML pipelines, SQL for ad-hoc analysis",
    },
    
    "Q5: What is Catalyst Optimizer?": {
        "What": "Spark's query optimizer that transforms logical plan to physical plan",
        "Steps": [
            "1. Parsing → Unresolved Logical Plan",
            "2. Analysis → Resolved Logical Plan (type checking)",
            "3. Optimization → Optimized Logical Plan (predicate pushdown, constant folding)",
            "4. Physical Planning → Physical Plan (choose join strategies, etc.)",
            "5. Code Generation → JVM bytecode (Tungsten)",
        ],
        "Interview Tip": "Mention Catalyst when explaining why built-in functions are faster than UDFs",
    },
    
    "Q6: What is Tungsten?": {
        "What": "Spark's execution engine for CPU and memory optimization",
        "Features": [
            "Off-heap memory management (avoid GC overhead)",
            "Cache-aware computation (data locality)",
            "Whole-stage code generation (single JVM function per stage)",
        ],
    },
}
```

---

## 2. Data Pipeline Architecture <a name="2-data-pipeline"></a>

### 2.1 Medallion Architecture (Bronze-Silver-Gold)

```python
# ==========================================================
# MEDALLION ARCHITECTURE — Agoda's Pipeline Structure
# ==========================================================

"""
MEDALLION ARCHITECTURE:
======================

┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│    BRONZE     │───▶│    SILVER     │───▶│     GOLD      │
│  (Raw Data)   │    │ (Cleaned)    │    │ (Business)    │
│               │    │              │    │               │
│ • Raw events  │    │ • Deduped    │    │ • Aggregated  │
│ • All columns │    │ • Validated  │    │ • Feature     │
│ • Append-only │    │ • Typed      │    │   tables      │
│ • As-is from  │    │ • Joined     │    │ • ML-ready    │
│   source      │    │ • Enriched   │    │ • Dashboard   │
│               │    │              │    │   metrics     │
└──────────────┘    └──────────────┘    └──────────────┘

WHY?
• Clear data quality boundaries
• Easy debugging (trace data lineage)
• Supports multiple consumers (ML, BI, ops)
• Idempotent reprocessing (re-run Silver from Bronze)
"""

class MedallionPipeline:
    """Example Medallion pipeline for hotel booking data."""
    
    def bronze_layer(self, raw_path: str):
        """
        Bronze: Ingest raw data as-is.
        
        Rules:
        - No transformations
        - Add ingestion metadata (timestamp, source, batch_id)
        - Schema evolution allowed (new columns OK)
        """
        raw_df = spark.read.json(raw_path)
        
        bronze_df = raw_df \
            .withColumn("ingestion_timestamp", F.current_timestamp()) \
            .withColumn("source_file", F.input_file_name()) \
            .withColumn("batch_id", F.lit("batch_2024_01_15"))
        
        bronze_df.write \
            .mode("append") \
            .partitionBy("ingestion_date") \
            .parquet("s3://data-lake/bronze/bookings/")
        
        return bronze_df
    
    def silver_layer(self, bronze_df):
        """
        Silver: Clean, validate, and deduplicate.
        
        Rules:
        - Remove duplicates
        - Apply schema enforcement
        - Handle null values
        - Data quality checks
        """
        silver_df = bronze_df \
            .dropDuplicates(["booking_id"]) \
            .filter(F.col("hotel_id").isNotNull()) \
            .filter(F.col("booking_date").isNotNull()) \
            .withColumn("price", F.col("price").cast(FloatType())) \
            .withColumn("booking_date", F.to_date("booking_date", "yyyy-MM-dd")) \
            .filter(F.col("price") > 0) \
            .filter(F.col("price") < 100000)  # Outlier removal
        
        # Data quality assertion
        total_bronze = bronze_df.count()
        total_silver = silver_df.count()
        drop_rate = 1 - (total_silver / total_bronze)
        
        if drop_rate > 0.1:  # More than 10% dropped → alert!
            raise DataQualityException(
                f"Drop rate {drop_rate:.2%} exceeds threshold 10%"
            )
        
        silver_df.write \
            .mode("overwrite") \
            .partitionBy("booking_date") \
            .parquet("s3://data-lake/silver/bookings/")
        
        return silver_df
    
    def gold_layer(self, silver_bookings, silver_clicks, silver_reviews):
        """
        Gold: Business-ready aggregations and ML features.
        
        Rules:
        - Aggregated to entity level (hotel, user)
        - Joined across data sources
        - Feature tables for ML models
        - KPI tables for dashboards
        """
        # ML Feature Table
        hotel_features = engineer_hotel_features(
            silver_bookings, silver_clicks, silver_reviews
        )
        
        hotel_features.write \
            .mode("overwrite") \
            .parquet("s3://data-lake/gold/hotel_features/")
        
        # KPI Table for dashboard
        daily_kpis = silver_bookings \
            .groupBy("booking_date", "destination") \
            .agg(
                F.count("*").alias("total_bookings"),
                F.sum("revenue").alias("total_revenue"),
                F.avg("price").alias("avg_booking_price"),
                F.countDistinct("user_id").alias("unique_users"),
            )
        
        daily_kpis.write \
            .mode("overwrite") \
            .partitionBy("booking_date") \
            .parquet("s3://data-lake/gold/daily_kpis/")
        
        return hotel_features, daily_kpis
```

### 2.2 Lambda vs Kappa Architecture

```python
# ==========================================================
# LAMBDA vs KAPPA — Which to Use When?
# ==========================================================

architectures = {
    "Lambda Architecture": {
        "Structure": """
            ┌──────────────┐
            │  Data Source  │
            └──────┬───────┘
                   │
           ┌───────┴────────┐
           ▼                ▼
     ┌──────────┐    ┌──────────┐
     │  Batch   │    │  Speed   │
     │  Layer   │    │  Layer   │
     │ (Spark)  │    │ (Flink)  │
     └────┬─────┘    └────┬─────┘
          │               │
          └───────┬───────┘
                  ▼
           ┌──────────┐
           │ Serving  │
           │  Layer   │
           └──────────┘
        """,
        "Pros": "Accurate batch + low-latency speed layer",
        "Cons": "Two codebases to maintain (batch + streaming)",
        "Use When": "Need both historical accuracy AND real-time updates",
    },
    
    "Kappa Architecture": {
        "Structure": """
            ┌──────────────┐
            │  Data Source  │
            └──────┬───────┘
                   │
                   ▼
           ┌──────────────┐
           │  Streaming   │
           │    Layer     │
           │ (Kafka +    │
           │  Flink)     │
           └──────┬───────┘
                  │
                  ▼
           ┌──────────┐
           │ Serving  │
           │  Layer   │
           └──────────┘
        """,
        "Pros": "Single codebase, simpler to maintain",
        "Cons": "Reprocessing historical data is hard/expensive",
        "Use When": "Real-time is primary requirement, batch is secondary",
    },
    
    "Agoda's Approach": {
        "What": "Hybrid — batch for features, streaming for freshness",
        "Batch": "PySpark for daily feature aggregations (Bronze → Silver → Gold)",
        "Streaming": "Kafka for real-time events (clicks, bookings, inventory updates)",
        "Serving": "Feature Store serves both batch and streaming features",
    },
}
```

---

## 3. SQL for ML Engineers <a name="3-sql"></a>

### 3.1 SQL Questions Commonly Asked at Agoda

```sql
-- ==========================================================
-- Q1: Find the top 5 hotels by booking revenue in each city
-- (Tests: Window Functions, Ranking)
-- ==========================================================

WITH hotel_revenue AS (
    SELECT 
        city,
        hotel_id,
        hotel_name,
        SUM(booking_value) AS total_revenue,
        COUNT(*) AS total_bookings,
        RANK() OVER (
            PARTITION BY city 
            ORDER BY SUM(booking_value) DESC
        ) AS revenue_rank
    FROM bookings b
    JOIN hotels h ON b.hotel_id = h.id
    WHERE booking_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
    GROUP BY city, hotel_id, hotel_name
)
SELECT city, hotel_id, hotel_name, total_revenue, total_bookings
FROM hotel_revenue
WHERE revenue_rank <= 5
ORDER BY city, revenue_rank;


-- ==========================================================
-- Q2: Calculate 7-day rolling average booking price per hotel
-- (Tests: Window Functions, Moving Averages)
-- ==========================================================

SELECT 
    hotel_id,
    booking_date,
    price,
    AVG(price) OVER (
        PARTITION BY hotel_id 
        ORDER BY booking_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_avg_price_7d,
    
    COUNT(*) OVER (
        PARTITION BY hotel_id 
        ORDER BY booking_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS bookings_in_window
FROM bookings
ORDER BY hotel_id, booking_date;


-- ==========================================================
-- Q3: Find users who booked in January but NOT in February
-- (Tests: Set Operations, NOT EXISTS / LEFT JOIN)
-- ==========================================================

-- Method 1: NOT EXISTS (usually fastest)
SELECT DISTINCT user_id
FROM bookings b1
WHERE EXTRACT(MONTH FROM booking_date) = 1
  AND EXTRACT(YEAR FROM booking_date) = 2024
  AND NOT EXISTS (
      SELECT 1 FROM bookings b2
      WHERE b2.user_id = b1.user_id
        AND EXTRACT(MONTH FROM b2.booking_date) = 2
        AND EXTRACT(YEAR FROM b2.booking_date) = 2024
  );

-- Method 2: LEFT JOIN with NULL check
SELECT DISTINCT jan.user_id
FROM bookings jan
LEFT JOIN bookings feb 
    ON jan.user_id = feb.user_id
    AND EXTRACT(MONTH FROM feb.booking_date) = 2
    AND EXTRACT(YEAR FROM feb.booking_date) = 2024
WHERE EXTRACT(MONTH FROM jan.booking_date) = 1
  AND EXTRACT(YEAR FROM jan.booking_date) = 2024
  AND feb.user_id IS NULL;


-- ==========================================================
-- Q4: Detect consecutive bookings (same user, within 24 hours)
-- (Tests: Self-join, LAG/LEAD window functions)
-- ==========================================================

WITH booking_gaps AS (
    SELECT 
        user_id,
        booking_id,
        booking_timestamp,
        LAG(booking_timestamp) OVER (
            PARTITION BY user_id 
            ORDER BY booking_timestamp
        ) AS prev_booking_timestamp,
        
        TIMESTAMPDIFF(
            HOUR,
            LAG(booking_timestamp) OVER (
                PARTITION BY user_id 
                ORDER BY booking_timestamp
            ),
            booking_timestamp
        ) AS hours_since_last_booking
    FROM bookings
)
SELECT *
FROM booking_gaps
WHERE hours_since_last_booking IS NOT NULL
  AND hours_since_last_booking <= 24;


-- ==========================================================
-- Q5: Feature Engineering in SQL (for ML model training)
-- (Tests: Complex aggregation, pivoting, feature creation)
-- ==========================================================

SELECT 
    h.hotel_id,
    
    -- Booking features
    COUNT(b.booking_id) AS total_bookings_30d,
    COUNT(DISTINCT b.user_id) AS unique_users_30d,
    AVG(b.price) AS avg_price_30d,
    STDDEV(b.price) AS price_stddev_30d,
    
    -- Conversion metrics
    COALESCE(
        SUM(CASE WHEN b.booking_id IS NOT NULL THEN 1 ELSE 0 END) * 1.0 
        / NULLIF(SUM(c.impressions), 0), 
        0
    ) AS conversion_rate,
    
    -- Cancellation rate
    SUM(CASE WHEN b.is_cancelled THEN 1 ELSE 0 END) * 1.0 
    / NULLIF(COUNT(b.booking_id), 0) AS cancellation_rate,
    
    -- Review features
    AVG(r.rating) AS avg_rating,
    COUNT(r.review_id) AS review_count,
    
    -- Seasonality features
    SUM(CASE WHEN EXTRACT(DOW FROM b.check_in_date) IN (0, 6) THEN 1 ELSE 0 END) * 1.0
    / NULLIF(COUNT(b.booking_id), 0) AS weekend_booking_ratio,
    
    -- Price positioning
    h.base_price / NULLIF(city_avg.avg_city_price, 0) AS price_vs_market
    
FROM hotels h
LEFT JOIN bookings b ON h.hotel_id = b.hotel_id 
    AND b.booking_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
LEFT JOIN click_stats c ON h.hotel_id = c.hotel_id
LEFT JOIN reviews r ON h.hotel_id = r.hotel_id
LEFT JOIN (
    SELECT city, AVG(base_price) AS avg_city_price
    FROM hotels
    GROUP BY city
) city_avg ON h.city = city_avg.city
GROUP BY h.hotel_id, h.base_price, city_avg.avg_city_price;
```

---

## 4. Kafka, Streaming & Event-Driven Architecture <a name="4-kafka"></a>

```python
# ==========================================================
# KAFKA — Core Concepts for Interview
# ==========================================================

kafka_concepts = {
    "Topic": "A named feed of messages (e.g., 'booking-events', 'click-events')",
    "Partition": "Topic split into partitions for parallelism. Messages ordered WITHIN partition.",
    "Producer": "Publishes messages to topics",
    "Consumer": "Reads messages from topics",
    "Consumer Group": "Set of consumers that share work. Each partition → one consumer in group.",
    "Offset": "Position of message in partition. Consumer tracks its offset.",
    "Broker": "A Kafka server. Cluster = multiple brokers.",
    "Replication Factor": "How many copies of each partition (e.g., 3 for production)",
}

# Kafka at Agoda — How YOU Used It (from resume):
kafka_usage = {
    "What": "Integrated Kafka to publish inference results downstream",
    "Producers": [
        "Pricing model → publishes price updates to 'hotel-prices' topic",
        "Ranking model → publishes ranking scores to 'ranking-scores' topic",
    ],
    "Consumers": [
        "Pricing display service → reads from 'hotel-prices'",
        "Recommendation engine → reads from 'ranking-scores'",
        "Analytics pipeline → reads from all topics for dashboarding",
    ],
    "Guarantees": {
        "At-least-once": "Default — may have duplicates, consumers handle idempotency",
        "Exactly-once":  "Use Kafka transactions + idempotent producers (higher latency)",
    },
}

# ==========================================================
# KAFKA CONSUMER EXAMPLE (Python)
# ==========================================================

from kafka import KafkaConsumer, KafkaProducer
import json

class PriceUpdateProducer:
    """Publishes price updates to Kafka after batch inference."""
    
    def __init__(self, bootstrap_servers: list, topic: str):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8'),
            acks='all',           # Wait for ALL replicas to acknowledge
            retries=3,            # Retry on transient failures
            enable_idempotence=True,  # Exactly-once semantics
        )
        self.topic = topic
    
    def publish_prices(self, price_updates: list):
        """Publish batch of price updates."""
        for update in price_updates:
            self.producer.send(
                self.topic,
                key=update['hotel_id'],        # Partition by hotel_id
                value={
                    'hotel_id': update['hotel_id'],
                    'new_price': update['new_price'],
                    'model_version': update['model_version'],
                    'timestamp': update['timestamp'],
                }
            )
        self.producer.flush()  # Ensure all messages sent

class PriceUpdateConsumer:
    """Consumes price updates and applies to display service."""
    
    def __init__(self, bootstrap_servers, topic, group_id):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',  # Start from beginning if no offset
            enable_auto_commit=False,       # Manual commit for reliability
        )
    
    def process(self):
        for message in self.consumer:
            try:
                price_update = message.value
                self._apply_price_update(price_update)
                self.consumer.commit()  # Commit AFTER successful processing
            except Exception as e:
                logger.error(f"Failed to process: {e}")
                # Don't commit — message will be reprocessed
    
    def _apply_price_update(self, update):
        """Apply price update to cache/database."""
        pass
```

---

## 5. Distributed Systems Concepts <a name="5-distributed-systems"></a>

```python
# ==========================================================
# CORE DISTRIBUTED SYSTEMS CONCEPTS FOR AGODA INTERVIEW
# ==========================================================

distributed_systems = {
    "CAP Theorem": {
        "C": "Consistency — every read returns the most recent write",
        "A": "Availability — every request receives a response",
        "P": "Partition Tolerance — system operates despite network failures",
        "Key": "In network partition, choose C or A (can't have both)",
        "Agoda": {
            "Bookings/Inventory": "CP — MUST be consistent (no double bookings!)",
            "Search/Reviews":     "AP — eventual consistency OK (stale reviews acceptable)",
            "Feature Store":      "AP — serving slightly stale features is acceptable",
        },
    },
    
    "Consistency Models": {
        "Strong":     "Reads always return latest write (expensive). Use for: inventory.",
        "Eventual":   "Reads may return stale data but converge eventually. Use for: reviews.",
        "Read-your-writes": "User sees their own writes immediately. Use for: user profiles.",
    },
    
    "Database Selection": {
        "PostgreSQL": "ACID transactions, joins, booking records, user accounts",
        "MongoDB":    "Flexible schema, document store, feature store, hotel metadata",
        "Redis":      "Low-latency cache, session store, inventory counts, feature serving",
        "Elasticsearch": "Full-text search, hotel search index, log aggregation",
        "BigQuery":   "Analytics, ML training data, large-scale aggregations",
        "Kafka":      "Event streaming, real-time data pipeline, async communication",
    },
    
    "Caching Strategies": {
        "Cache-Aside": {
            "How": "App checks cache first → miss → load from DB → store in cache",
            "Pros": "Simple, cache only what's needed",
            "Cons": "Cache can be stale, cold start",
            "Use": "Feature store online layer, hotel metadata",
        },
        "Write-Through": {
            "How": "Write to cache AND DB simultaneously",
            "Pros": "Cache always consistent",
            "Cons": "Write latency (double write)",
            "Use": "Inventory updates (booking confirmation)",
        },
        "Write-Behind": {
            "How": "Write to cache first, async write to DB",
            "Pros": "Fast writes",
            "Cons": "Data loss risk if cache fails before DB write",
            "Use": "Click tracking, analytics events",
        },
    },
    
    "Scaling Patterns": {
        "Horizontal Scaling": "Add more instances (microservices, Kubernetes)",
        "Vertical Scaling":   "Bigger machines (limited, expensive)",
        "Database Sharding":  "Split data by key (hotel_id, region) across DB instances",
        "Read Replicas":      "Multiple read-only DB copies for read-heavy workloads",
        "CQRS":              "Separate read and write models (search vs booking)",
    },
    
    "Fault Tolerance": {
        "Circuit Breaker": {
            "What": "Stop calling a failing service, return fallback",
            "States": "Closed (normal) → Open (failing) → Half-Open (testing)",
            "Use": "If ML service is down → fallback to rule-based ranking",
        },
        "Retry with Backoff": {
            "What": "Retry failed calls with exponential wait",
            "Use": "Feature store lookups, Kafka message publishing",
        },
        "Bulkhead": {
            "What": "Isolate failures — don't let one service crash everything",
            "Use": "Separate thread pools for ranking, pricing, recommendations",
        },
        "Timeout": {
            "What": "Don't wait forever for slow services",
            "Use": "100ms timeout for ML inference, fallback to cached result",
        },
    },
}
```

---

## 6. Hadoop Ecosystem <a name="6-hadoop"></a>

```python
# ==========================================================
# HADOOP ECOSYSTEM — Quick Reference
# ==========================================================

hadoop_ecosystem = {
    "HDFS": {
        "What": "Distributed file system for storing large datasets",
        "Architecture": "NameNode (metadata) + DataNodes (data blocks)",
        "Block Size": "128MB or 256MB default",
        "Replication": "3 copies of each block (configurable)",
        "Use at Agoda": "Underlying storage for Spark jobs, raw data",
    },
    
    "YARN": {
        "What": "Resource manager for Hadoop cluster",
        "Components": "ResourceManager (global) + NodeManagers (per node) + ApplicationMasters",
        "Use": "Manages Spark executor allocation, job scheduling",
    },
    
    "HIVE": {
        "What": "SQL interface on top of Hadoop data (converts SQL → MapReduce/Spark)",
        "Metastore": "Central metadata repository (table schemas, locations)",
        "Use at Agoda": "Ad-hoc analytics, KPI reporting on large datasets",
        "Your Experience": "From Infosys — used HIVE on Hadoop for large-scale analysis",
    },
    
    "S3 (AWS equivalent)": {
        "What": "Object storage replacing HDFS in cloud environments",
        "Advantages": "Cheaper, elastic, no cluster management",
        "With Spark": "spark.read.parquet('s3://bucket/path/')",
    },
}

# ==========================================================
# HOW TO TALK ABOUT HADOOP IN INTERVIEW
# ==========================================================

hadoop_talking_points = """
"While I've worked with the Hadoop ecosystem throughout my career —
starting at Infosys using HIVE on Hadoop for large-scale data analysis,
and at Pitney Bowes with S3-based data workflows — I've seen the 
evolution toward cloud-native alternatives.

At Tiket.com, we use a hybrid approach:
- BigQuery for analytical workloads (replaces Hive)
- S3/GCS for data lake storage (replaces HDFS)
- PySpark on Kubeflow/EMR for processing (still leverages Spark)
- Kafka for streaming (instead of MapReduce)

The principles remain the same: distributed storage, parallel processing,
and fault tolerance — but the tooling has modernized."
"""
```

---

## 📝 Quick Reference Card for Data Engineering Interview

```
┌────────────────────────────────────────────────────────────┐
│  PySpark Optimization Hierarchy (Most Impact → Least)     │
│                                                            │
│  1. 🏠 Data Format:  Parquet > ORC > JSON > CSV            │
│  2. 🔍 Predicate Pushdown: Filter EARLY, select columns    │
│  3. 📡 Broadcast Joins: Small table × Large table           │
│  4. 🔄 Avoid Shuffles: Minimize groupBy/joins               │
│  5. 📦 Partition Wisely: By query key, right granularity   │
│  6. 💾 Cache/Persist: Only if reused, unpersist when done  │
│  7. 🐍 Avoid Python UDFs: Use built-in or Pandas UDFs     │
│  8. ⚙️ AQE: Enable adaptive query execution (Spark 3.0+) │
│                                                            │
│  Data Pipeline Design Checklist:                           │
│  ✅ Medallion Architecture (Bronze → Silver → Gold)        │
│  ✅ Idempotent processing (safe to re-run)                 │
│  ✅ Data quality checks at each layer                      │
│  ✅ Schema evolution handling                               │
│  ✅ Monitoring & alerting on pipeline failures             │
│  ✅ Point-in-time correctness for ML features              │
│                                                            │
│  Distributed Systems ("Why X?" answers):                   │
│  • "I chose Redis because sub-ms latency for feature       │
│     serving is critical for p95 < 100ms SLA"              │
│  • "I chose Kafka because we need reliable async           │
│     delivery of price updates to multiple consumers"      │
│  • "I chose MongoDB for the feature store because          │
│     flexible schema and document model fits features"     │
│  • "I chose Elasticsearch for hotel search because         │
│     inverted index is optimal for text + geo queries"     │
└────────────────────────────────────────────────────────────┘
```

---

> **Next:** Part 4 covers **Mock Interview Simulation, Resume Deep-Dive Questions, and Behavioral Questions** — the final preparation layer.
