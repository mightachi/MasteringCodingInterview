# Travel & Booking Systems — Domain Specialization Course

> Companion to the hands-on system design course. This document goes deep on the theoretical foundations interviewers probe (CAP, PACELC, optimization at every layer) and works out the seven system design problems travel/booking companies actually ask. The capstone — **TravelHub** — integrates all seven into one coherent platform you can demo.

**How this fits with the main course.** The main v2 course teaches you the building blocks. This document teaches you the *travel-domain composition* of those blocks and the *theoretical depth* a Staff/Principal interview demands. Do this *after* you've completed at least Parts 1–11 of v2.

**How to use it.**
- Skim Part A (theory deep dives) once before moving to Part B.
- For each system design problem in Part B, set a 45-minute timer and try it before reading the worked solution.
- Build the TravelHub capstone in Part C — every module corresponds to one of the seven problems, and they share a database, an event bus, and a deployment.

---

# Table of Contents

**Part A — Theoretical Deep Dives**
- A1. CAP Theorem (experimentally, not just mnemonically)
- A2. PACELC (the part most candidates miss)
- A3. Consistency Models — the full spectrum
- A4. The Optimization Catalog (database, query, Spark/Flink, cache, network, storage, cost)

**Part B — The Seven System Design Problems**
- B1. Hotel Search & Availability
- B2. Supplier Inventory Sync (CDC, real-time)
- B3. Dynamic Pricing Platform
- B4. Booking / Reservation Transaction System
- B5. Clickstream Analytics & A/B Testing
- B6. ML Feature Store for Recommendations
- B7. Financial Data Pipeline (FINUDP-style)

**Part C — The TravelHub Capstone**
- C1. Architecture overview
- C2. Module-by-module build plan (10–12 weeks)
- C3. Cross-cutting: schema strategy, observability, cost attribution
- C4. Demo script for interviews

---

# Part A — Theoretical Deep Dives

## A1. CAP Theorem — Beyond the Mnemonic

Most candidates can recite CAP. Few can use it. The interview signal is *applying* it to a concrete design.

### A1.1 What CAP actually says

In 2002, Brewer formalized: a distributed system can guarantee at most two of *Consistency*, *Availability*, *Partition tolerance*. Lynch & Gilbert proved it. Since *partitions happen* (networks fail), real-world systems choose between **C** and **A** *during a partition*.

- **Consistency** here means *linearizability*: every read sees the most recent write, and there is a single global order consistent with real time.
- **Availability** means every non-failing node returns a non-error response.
- **Partition tolerance** means the system continues operating despite arbitrary message loss between nodes.

**The senior framing.** "We will use Cassandra, which is AP" is not enough. The questions you must answer:
1. *How long* are we willing to be unavailable, or *how stale* are we willing to be?
2. *On which operations* does this matter? (Read-only catalog? Write-heavy booking? They have different answers.)
3. *What does the user see* during a partition? (Stale data? Error? Slow?)

### A1.2 Why partition tolerance is non-negotiable

In a single-process system you can have C and A trivially. In a single-machine system with disk, the disk *is* a separate process; subtle. In a network of two or more machines, partitions *will* occur — TCP retries, switch failures, AZ outages, GC pauses that look like partitions. So the real choice is always C vs A.

### 🛠️ Activity A1: Demonstrate CAP with Postgres + a partition (90 min)

Run two-node Postgres with streaming replication (you set this up in v2, Part 8). Start writing in a loop on the primary. Now break the network from the replica:

```bash
docker exec -it postgres-replica /bin/bash
# Inside the replica
apt-get update && apt-get install -y iptables
iptables -A INPUT -s <primary_ip> -j DROP
```

Observe:
- Writes to primary still succeed (primary picks A in this config — keeps serving).
- Reads from replica return increasingly stale data (replica is *consistent with itself* but not with primary).
- After ~1–5 minutes (depending on `wal_keep_segments`), if WAL is exhausted, the replica falls behind unrecoverably.

Now restore the network. Watch the lag drain. Did Postgres *correctly* converge? (Yes for streaming replication; not always for multi-master.)

**Done when:** You have screenshots of (a) the primary serving writes during the partition, (b) the replica returning stale reads, (c) lag draining after recovery. Write a one-paragraph narrative: *"This config picks A over C on the read replica. Real cost: stale reads up to N seconds."*

### A1.3 Choosing CP vs AP — the decision matrix

| Workload | Choice | Why |
|---|---|---|
| Bank ledger | CP | Cannot show wrong balance, ever |
| Inventory of last hotel room | CP-leaning | Cannot oversell once stock = 1 |
| Inventory when stock = 100 | AP | Show available; reconcile if you sell the 101st |
| Search results | AP | Stale by minutes is fine; results must come back |
| User's profile photo | AP | Stale read tolerable |
| Distributed lock | CP | Must guarantee one holder |
| Configuration store | CP | Wrong config = outage |
| Like counter | AP | Off by 5 likes is fine |
| Session store | AP | Re-login is acceptable; outage is not |
| DNS | AP | Stale records are tolerable; resolver must answer |
| Booking confirmation number generator | CP | Must be unique |
| Hotel availability cache | AP | The booking step is where you re-check |

### A1.4 The pattern that hides CAP from users

Most production systems are layered:

```
[ Cache (AP) ] -> [ Read replica (AP, async) ] -> [ Primary (CP, sync) ]
```

**Reads** flow through the AP layers (fast, can be stale). **Writes** go to the CP layer (slow, correct). You get the latency of AP and the correctness of CP *for the operations that need it*. This is how almost every real system works, and the senior framing: "CAP isn't picked once for the system; it's picked per-operation."

### 🤔 Reflect

- Hotel inventory has 47 rooms, you sell rooms throughout the day. Where does CAP matter? (Almost nowhere — until stock approaches zero, when you must move to CP for the booking step.)
- A flight has 1 seat left. Two users hit "Book." What happens in an AP system? (Both see "available." Both think they booked. The reconciliation step must reject one — and notify them, refund their card.)

---

## A2. PACELC — The Part Most Candidates Miss

### A2.1 What PACELC adds

CAP only covers behavior during partitions. PACELC (Abadi, 2010) adds: even *without* partitions, you choose between **L**atency and **C**onsistency.

> If Partition: trade Availability vs Consistency. Else: trade Latency vs Consistency.

A system is characterized as e.g. **PA/EL** (under partition: pick A; else: pick L) — which describes Cassandra, DynamoDB. **PC/EC** describes Spanner with strong reads, traditional RDBMS clusters. **PA/EC** is rare but possible (Cassandra with `LOCAL_QUORUM` reads and writes).

### A2.2 Why "EL" is the more common engineering trade-off

Partitions are rare. Latency budgets are *every request*. So in practice you tune the EL knob much more often than the PA knob.

**Concrete example.** DynamoDB strong reads cost ~2× of eventually consistent reads (latency, RCU). For a feed, you don't need strong reads — they're usually fine. For a payment idempotency check, you do. Per-operation choice, every time.

### A2.3 Map of common systems

| System | Class | Note |
|---|---|---|
| Spanner / CockroachDB (default) | PC/EC | TrueTime / HLC + Paxos |
| DynamoDB (default) | PA/EL | Choose strong-read per request to upgrade reads |
| Cassandra (default) | PA/EL | Tune consistency per query (`LOCAL_QUORUM`, `EACH_QUORUM`, `ALL`) |
| MongoDB (default) | PA/EC | Configurable; primary-replica with majority writes |
| Postgres (single-primary) | PC/EC for primary; PA/EL for replicas |
| Kafka | Per-topic; with `acks=all`+`min.insync.replicas`, PC/EC | The ISR mechanism is essentially this |
| Redis (single) | PC/EC trivially | One node — but no partition tolerance |
| Redis Cluster | PA/EL | Async replication; minority partitions go down |

### A2.4 Tunable consistency in practice

Cassandra exposes consistency *per query*. The same column family supports:

- `WRITE QUORUM, READ QUORUM` → consistent reads (W + R > N).
- `WRITE ANY, READ ONE` → fastest, most stale.
- `WRITE EACH_QUORUM, READ LOCAL_QUORUM` → multi-DC, locally consistent, globally eventual.

This is PACELC at the API. The senior interview move: "For the high-throughput write path I'd use `LOCAL_QUORUM` writes and `LOCAL_QUORUM` reads to get strong consistency in the local DC at acceptable latency, accepting cross-DC eventual consistency."

### 🛠️ Activity A2: Tune Cassandra consistency, measure latency (90 min)

Stand up a 3-node Cassandra cluster with Docker Compose. Insert 100K rows. Read with consistency levels `ONE`, `QUORUM`, `ALL`. Measure p50, p95, p99 latency for each.

```python
from cassandra.cluster import Cluster
from cassandra import ConsistencyLevel
from cassandra.query import SimpleStatement
import time, random, statistics

cluster = Cluster(["127.0.0.1"])
session = cluster.connect("travelhub")

for level in [ConsistencyLevel.ONE, ConsistencyLevel.QUORUM, ConsistencyLevel.ALL]:
    latencies = []
    for _ in range(1000):
        stmt = SimpleStatement(
            "SELECT * FROM hotels WHERE hotel_id=%s",
            consistency_level=level
        )
        t0 = time.perf_counter()
        session.execute(stmt, (random.randint(1, 100000),))
        latencies.append((time.perf_counter() - t0) * 1000)
    print(f"{level}: p50={statistics.median(latencies):.1f}ms, "
          f"p99={sorted(latencies)[990]:.1f}ms")
```

**Done when:** You see ONE < QUORUM < ALL on latency, and you can articulate the W+R > N rule that gives you strong consistency at QUORUM.

---

## A3. Consistency Models — The Full Spectrum

CAP gives you a binary intuition; reality is a spectrum. Senior candidates name the model precisely.

**From strongest to weakest:**

1. **Linearizability** — every operation appears to take effect instantaneously at some point between its invocation and response, in real-time order. Single-object guarantee.
2. **Sequential consistency** — there is *some* total order consistent with each client's program order, but not necessarily real time.
3. **Causal consistency** — operations causally related (A happens-before B) are seen in order; concurrent operations may be seen in different orders by different observers.
4. **Read-your-writes** — a client always sees its own writes. Practical, often "good enough."
5. **Monotonic reads** — once you see a value, you never see an older one.
6. **Monotonic writes** — your writes are applied in order.
7. **Eventual consistency** — replicas converge if writes stop. Says nothing about speed or order.

**For multi-object operations:**
- **Serializability** — the result of running concurrent transactions is equivalent to *some* serial schedule.
- **Strict serializability** = serializability + linearizability. Spanner.
- **Snapshot isolation** — each transaction sees a snapshot at start; protects from most anomalies but allows write-skew.

### Practical mapping for travel domain

| Operation | Model needed |
|---|---|
| Search hotels | Eventual (5-min stale fine) |
| Read your own booking | Read-your-writes (you must see what you just booked) |
| Confirm a booking | Strict serializability (no double-sell) |
| Inventory write | Linearizable per-room |
| Reviews feed | Causal (replies after the post) |
| Click event ingestion | Eventual (lossless, but order doesn't matter much) |
| Payment idempotency check | Linearizable |

The interview move: don't say "consistent." Say "read-your-writes for the booking acknowledgment, eventual for downstream search index, linearizable for the inventory decrement."

---

## A4. The Optimization Catalog

The recruiter's specific feedback was that you sometimes pick patterns without justifying them. The fix is to know the *classes* of optimization, when each applies, and what each costs.

### A4.1 Database & query optimization

**A4.1.1 Indexes — pick the right kind**

| Type | Use when | Cost |
|---|---|---|
| B-tree | Equality + range (`WHERE x = ?` and `WHERE x BETWEEN`) | Storage; write amplification |
| Hash | Pure equality, no range | Cannot do range queries |
| Bitmap | Low-cardinality columns in OLAP | Bad for high-update workloads |
| GIN / inverted | Full-text search, JSONB containment | Slow inserts |
| GiST / R-tree / spatial | Geospatial range, nearest-neighbour | Specialized |
| BRIN | Naturally clustered data (time-series) | Only useful when physical order ≈ logical order |
| Partial | `WHERE active = true` for the 1% active rows | Tighter than full index |
| Covering / INCLUDE | Read multiple columns without table lookup | Bigger index |
| Hash on multi-column | Composite equality | Order matters: `(country, city)` serves country-only queries; not city-only |

**A4.1.2 Query plan reading — the universal skill**

```sql
EXPLAIN ANALYZE SELECT * FROM bookings 
WHERE user_id = 42 AND created_at > NOW() - INTERVAL '30 days';
```

Look for: `Seq Scan` (bad — full table read), `Index Scan` (good), `Bitmap Heap Scan` (good for medium selectivity), `Hash Join` vs `Merge Join` vs `Nested Loop` (depends on size), `cost`/`actual time` mismatches (statistics out of date — `ANALYZE` the table).

**A4.1.3 Predicate and projection pushdown**

In any columnar / federated engine (Trino, Spark, BigQuery, Snowflake), pushdown is the difference between scanning 10 GB and 10 MB:
- **Predicate pushdown**: filter at the storage layer, not after pulling all rows.
- **Projection pushdown**: read only the columns you need.

In Spark: `spark.read.parquet(...).filter("country = 'IN'").select("hotel_id")` should generate a job that reads only the `hotel_id` column from row groups whose `country` min/max include `IN`. Verify with `.explain(true)`.

**A4.1.4 Partition pruning**

Partition by columns you filter on most. Partitioning by `(year, month, day)` and filtering by `WHERE date = ...` cuts files read by ~365×. Critical for any large warehouse table. Hidden partitioning (Iceberg) does this without the user thinking about it.

### 🛠️ Activity A4.1: EXPLAIN-driven optimization (60 min)

Take a Postgres table of 10M rows with several columns. Write 5 queries (range, equality, join, aggregation, top-N). For each:
1. Run with no index — note plan and time.
2. Add an appropriate index — re-run.
3. Add a redundant index — re-run; observe write slowdown.

**Done when:** You have a one-page table of "query → original time → indexed time → which index" and you can explain why each index helps.

### A4.2 Spark / Flink optimization

The single biggest determinant of Spark performance is *shuffle*. The optimization catalog:

**A4.2.1 Avoid shuffle when possible**

- **Broadcast join** — if one side is < `spark.sql.autoBroadcastJoinThreshold` (default 10 MB; set up to ~200 MB for known cases). The small side is shipped to every executor; no shuffle on the big side.
- **Bucketing** — pre-partition tables by join key on disk. Two bucketed tables with the same key/buckets join without shuffle.
- **Co-partitioned data** — if both sides come from the same partitioning, Spark may skip the exchange.

**A4.2.2 Mitigate skew**

Skew = one task has 100× the data of others. Symptom: 99 tasks done, 1 task running for 30 minutes.

- **Salting** — append `floor(rand() * N)` to the join key on the big side; replicate the small side N times. Spreads hot keys across N partitions.
- **AQE skew handling** — Spark 3.x detects skewed partitions at runtime and splits them (`spark.sql.adaptive.skewJoin.enabled=true`).
- **Skew hint** — `df.hint("skew", "join_key")`.
- **Two-phase aggregation** — `groupBy(key, salt)` then `groupBy(key)`.

**A4.2.3 Right-size partitions**

- Target ~128–256 MB per partition for HDFS/S3; smaller for in-memory operations.
- `repartition(N)` is a full shuffle; `coalesce(N)` only reduces. Use `coalesce` before write to avoid tiny files.
- Output file size: aim for 128 MB–1 GB per Parquet file. Tiny files are S3's number-one performance killer.

**A4.2.4 Cache strategically**

- `df.cache()` materializes the DataFrame in memory after the next action.
- Cache only what's reused 2+ times; unpersist when done.
- `MEMORY_AND_DISK` is safer than `MEMORY_ONLY` for large DataFrames.

**A4.2.5 AQE and CBO**

Spark 3.x AQE (Adaptive Query Execution) does runtime adjustments: coalesce small partitions, switch sort-merge to broadcast at runtime if the result is small, split skewed joins. Enable it: `spark.sql.adaptive.enabled=true`. Combined with cost-based optimizer (CBO) using table statistics — `ANALYZE TABLE x COMPUTE STATISTICS FOR ALL COLUMNS`.

**A4.2.6 Flink-specific**

- **State backend** — RocksDB on local SSD with periodic checkpoints to S3. Tune block cache size.
- **Watermark generation** — too aggressive = late events dropped; too conservative = window completion delayed.
- **Checkpoint interval** — every 10–60 seconds typical; trade-off between recovery time and write amplification.
- **Exactly-once sinks** — require two-phase commit. Slower; only enable when needed.

### 🛠️ Activity A4.2: Find and fix a Spark skew (90 min)

Generate a skewed dataset: 90% of rows have `country = 'IN'`. Join with a countries dimension. Observe one task takes forever. Apply salting and re-run. Compare.

```python
from pyspark.sql import SparkSession, functions as F
import random

spark = SparkSession.builder.appName("skew").getOrCreate()

# Skewed fact: 90% IN, 10% spread across 10 countries
rows = [(i, "IN" if random.random() < 0.9 else f"C{random.randint(1,10)}") 
        for i in range(10_000_000)]
fact = spark.createDataFrame(rows, ["id", "country"])

countries = spark.createDataFrame([("IN", "India")] + 
    [(f"C{i}", f"Country {i}") for i in range(1, 11)], ["code", "name"])

# Naive join — watch one task drag
fact.join(countries, fact.country == countries.code).count()  

# Salted join
N = 50
salted_fact = fact.withColumn("salt", (F.rand() * N).cast("int"))
salted_dim = countries.crossJoin(
    spark.range(N).withColumnRenamed("id", "salt")
)
salted_fact.join(salted_dim, 
    (salted_fact.country == salted_dim.code) & 
    (salted_fact.salt == salted_dim.salt)
).count()
```

Compare wall-clock time and Spark UI's stage view.

### A4.3 Cache optimization patterns

**Multi-level caching.** Browser cache → CDN → reverse proxy cache → application memory cache → distributed cache (Redis) → DB query cache → DB itself. Cache where the *miss* is expensive but the *cardinality* of cacheable data is bounded.

**Write strategies revisited:**

| Strategy | When to use |
|---|---|
| Write-through (DB + cache atomically) | Strong read-your-writes need; can tolerate write latency |
| Write-around (DB only; cache lazy-loads) | Writes don't need to populate cache; reads are dominant |
| Write-behind (cache, then DB async) | Need fast writes; tolerable durability gap |
| Cache-aside (app reads cache; on miss reads DB and populates) | Default for most read-heavy systems |

**Stampede protection** — when a popular key expires, hundreds of requests miss simultaneously. Mitigate via:
- **Single-flight (request coalescing)** — first miss takes the lock; others wait for the result.
- **Probabilistic early expiration** — start refresh before TTL expires (e.g., 10% of the time when TTL < 30 s).
- **Locking with token** — only one process refills.

**Negative caching** — cache "not found" results too. Otherwise a missing key triggers DB hits forever.

**Cache warming** — pre-populate the cache after deploys or evictions. Critical for big-traffic events (sales, releases).

### A4.4 Network optimization

- **Connection pooling** — TCP setup costs ~RTT; TLS adds another. Reuse connections.
- **Persistent HTTP** (keep-alive, HTTP/2 multiplexing) — reuse one TCP/TLS for many requests.
- **Batching** — coalesce multiple small requests into one. Trades a bit of latency for huge throughput gains. Used by Bigtable, DynamoDB BatchGetItem, Kafka producer batching.
- **Pipelining** — send multiple requests without waiting for each response. Redis pipeline; HTTP/2 streams.
- **Compression** — gzip/zstd on payloads >1 KB. Be careful with TLS: BREACH attack means don't compress secrets.
- **Reduce hop count** — every microservice hop is RTT + serialization. Don't make 10 hops where 2 will do.
- **Edge / regional placement** — if 80% of users are in NA, having all services in eu-west-1 is malpractice.

### A4.5 Storage optimization

- **Columnar formats** for analytics (Parquet/ORC). Write once, read columns many times.
- **Compression** — Snappy (fast, less compression), Zstd (great trade-off), Gzip (high compression, slow), LZ4 (very fast, less compression). Default Zstd level 1–3 for Parquet in 2025.
- **Block / row group size** — Parquet row groups of 128 MB–1 GB. Smaller = better selectivity, more metadata overhead.
- **Partitioning** as covered above.
- **Z-ordering / Liquid clustering / data skipping** — physically co-locate rows with similar values along multiple columns. Delta/Iceberg/Hudi support this. Big wins for multi-column filter predicates.
- **Hot/warm/cold tiering** — recent data in standard storage, older in IA/Glacier. Lifecycle policies automate this. Object storage cost can drop 70%.

### A4.6 Cost optimization

- **Right-sizing** — measure actual usage; don't size for fictional peaks.
- **Reserved/committed/spot mix** — baseline on 1–3 yr commits (~30–60% off), bursts on on-demand, batch on spot/preemptible (60–90% off; checkpoint to recover).
- **Storage tiering** — move data older than X days to cheaper tier.
- **Egress avoidance** — design same-region; egress is the silent budget killer.
- **Dataframe materialization vs recomputation** — sometimes recomputing in Spark is cheaper than caching a huge intermediate; sometimes the opposite. Measure.
- **Partition pruning + projection pruning** — directly reduces scanned bytes, which is the BigQuery / Athena unit of cost.
- **Auto-stop dev clusters** — devs forget; automation doesn't.
- **Pre-aggregations** — for frequently asked queries on raw events, pre-aggregate hourly. Trade storage and pipeline complexity for query time and cost.

### 🛠️ Activity A4.6: Cut a sample query's cost in half (60 min)

Take any BigQuery / Athena / Snowflake query that scans > 10 GB. Apply: partition pruning, projection pruning, predicate pushdown via partition column, materialized view if frequent. Measure bytes scanned before and after. Document the optimization order.

---

# Part B — The Seven System Design Problems

For each: I write the question as an interviewer would ask it, walk through RESHADED, mark the 2–3 deep dives, and end with the trade-offs to verbalize.

**General preamble for travel/booking interviews.** The domain has these constants, and saying them up front signals seniority:
- **Read:write ratio is extreme** — typically 1000:1 for search vs. booking.
- **Inventory is contended** — the same room is sold by many channels (your site, OTAs, the hotel directly).
- **Pricing changes constantly** — supplier-driven, demand-driven, dynamic.
- **Compliance** — PCI-DSS for payments, GDPR/CCPA for personal data, data residency for some markets.
- **The booking is the money event** — everything else is cheap. The booking system gets the most engineering.
- **Two-sided marketplace** — supplier (hotel) experience matters as much as guest experience. They have different SLAs.

---

## B1. Hotel Search & Availability

> *"Design a hotel search and availability system. Users enter location + dates; we show ranked, available hotels with current prices in <500 ms p95."*

### B1.1 Clarifying questions

1. Catalog size? *Assume 5M hotels globally, 2B nights of inventory cached at any time.*
2. Search QPS? *Peak ~50K/s globally (search is cheap; lots of speculative searches before a booking).*
3. How fresh must inventory be? *Pricing — minutes; availability — minutes; once user clicks "book," we re-check live.*
4. Personalization? *Yes; rank using user features.*
5. Mobile + web + partner APIs? *All three.*
6. Geographic constraints? *Multi-region active-active.*

### B1.2 Functional requirements

- Search by location (city, lat/lng + radius, country, point of interest).
- Filter by date range, guests, rooms, price range, star rating, amenities, free cancellation.
- Sort by relevance, price, rating, distance.
- Return per-hotel: name, photos (URL), price, rating, distance, key amenities, room types available.
- Pagination, ~25 results per page, up to 1000 results per query.
- Autocomplete for location.

### B1.3 Non-functional requirements

- p95 < 500 ms; p99 < 1 s.
- 50K QPS sustained, 200K QPS peak (sales events).
- Inventory staleness < 5 minutes (with live re-check at booking).
- Multi-region; 99.95% availability.
- Cost per search target < $0.0001.

### B1.4 Estimation

- 5M hotels × ~5 KB metadata = 25 GB. Trivial; fits in any KV.
- 5M hotels × 365 nights × ~100 bytes per night-availability row = ~180 GB raw availability. Compressed Parquet ~30 GB. Fits in memory of moderate cluster.
- 50K QPS × 5 KB response = 250 MB/s outbound. Mostly served from CDN/edge cache for popular queries.

### B1.5 High-level architecture

```
                                ┌─────────────┐
                  ┌─────────────│  CDN edge   │── popular queries cached
                  │             └──────┬──────┘
              client request           │ miss
                  │                    ▼
              ┌───────────────────────────────────┐
              │   Search API (stateless)           │
              │   - parses query                    │
              │   - calls Geo Index for candidates  │
              │   - calls Availability Service      │
              │   - calls Pricing Service           │
              │   - calls Ranker                    │
              │   - assembles response              │
              └───┬────────┬───────┬───────┬───────┘
                  │        │       │       │
        ┌─────────▼┐ ┌─────▼─┐ ┌───▼───┐ ┌─▼──────────────┐
        │ Geo idx  │ │ Avail │ │ Price │ │ Ranker (model) │
        │ (Elastic │ │ Cache │ │ Cache │ │ + Feature Store│
        │  /OS)    │ │(Redis)│ │(Redis)│ │  (online lookup│
        │          │ │       │ │       │ │   keyed by user│
        │          │ │       │ │       │ │   + hotel)     │
        └──────────┘ └───┬───┘ └───┬───┘ └────────────────┘
                         │         │
                         ▼         ▼
              ┌──────────────────────┐
              │  Source of truth      │
              │  (Postgres, Iceberg)  │
              └──────────────────────┘
```

### B1.6 Data model

**Geo index (Elasticsearch/OpenSearch):**
```
{
  "hotel_id": "h_12345",
  "name": "Grand Hotel",
  "location": { "lat": 28.61, "lon": 77.21 },  // geo_point
  "city": "Delhi",
  "country": "IN",
  "star_rating": 4,
  "amenities": ["wifi", "pool", "gym"],
  "min_price_30d": 4500,
  "score_signals": { "review_score": 8.4, "popularity": 0.78 }
}
```

**Availability cache (Redis):**
- Key: `avail:{hotel_id}:{checkin_date}:{checkout_date}`
- Value: `{rooms_left: int, base_price: float, currency: str, ttl: 300s}`

**Source of truth (Postgres / Iceberg):**
- `hotels` (id, attrs)
- `room_types` (hotel_id, room_type, capacity, …)
- `availability` (hotel_id, room_type, date, rooms_total, rooms_held, rooms_sold)
- `prices` (hotel_id, room_type, date, price, valid_from, valid_to)

### B1.7 Deep dive 1 — Geospatial indexing

ES `geo_point` with bounding-box / radius queries handles most cases. For very high QPS or specific patterns, alternatives:
- **Geohash** — encode lat/lng as a hierarchical string. Adjacent geohashes can be looked up; good for "find hotels near here."
- **S2 / H3** — Google's S2 cells / Uber's H3 hexagonal grid. Better for non-uniform queries (the equator distortion of geohash is real). H3 makes "everything within 5 km" simple.

For a search of "hotels within 5 km of (28.61, 77.21) where price < $200, free WiFi, available May 10–12":
1. Use geo filter to get candidates (~10K hotels).
2. Apply attribute filters (~1K hotels).
3. Inner-join with availability cache (~500 hotels).
4. Score with ranker (~500 hotels).
5. Return top-25 with pagination.

### B1.8 Deep dive 2 — Index freshness

The geo index has min_price, popularity, available rooms (boolean). These change. Strategies:

- **Bulk re-index nightly** for slow-changing fields (description, photos, amenities).
- **Incremental updates** for fast-changing fields (price, availability flag): consume Kafka topic of changes (from B2's CDC pipeline).
- **Multi-tier**: ES for filtered candidate generation; Redis for the live numbers (price, rooms_left). Don't keep prices *in* the index — let it be a candidate generator, then enrich.

### B1.9 Deep dive 3 — Ranking

Two-stage:
1. **Candidate generation** — geo + filter, returns top ~500 by simple heuristic (popularity score).
2. **Ranking** — a learned model (gradient-boosted tree or DNN) scores each candidate using user features (from feature store — see B6), hotel features, query context (date, party size, day of week), and historical CTR/conversion.

Latency budget for ranking: ~50 ms for 500 candidates → batch features fetch + batch model inference.

### B1.10 Failure modes

- ES cluster down → fall back to a simpler, regional secondary index (read replica or backup).
- Ranker model down → return candidates sorted by simple heuristic (popularity × min_price_inverse).
- Availability cache cold → bypass cache; hit Postgres directly; warn on dashboard. Cache will warm naturally.
- Hot popular query (e.g., "Goa beach hotels") → CDN edge cache; protect ES with a single-flight wrapper.

### B1.11 Trade-offs to verbalize

- **Eventual consistency on availability** — we accept showing rooms that just sold out. Mitigation: re-check at booking.
- **Pre-computed sort scores** — we trade index size for ranking speed.
- **Two-stage retrieval** — adds complexity but lets us run an expensive ranker on only 500 candidates instead of 5M.
- **Multi-region active-active** — each region has full data; writes from suppliers go to nearest region and replicate via Kafka.

### 🛠️ Activity B1: Build a tiny hotel search (3–4 hours)

Generate 100K fake hotels (city, lat/lng, price, rating, amenities). Index in OpenSearch. Implement a `/search` endpoint that takes `lat, lng, radius_km, max_price, amenities[]`, returns top 25 sorted by a score = `0.6*rating + 0.4*price_inverse`. Add a Redis-backed cache with 5-min TTL on the query string. Load test with 1000 concurrent queries.

**Done when:** p95 < 100 ms hot, < 300 ms cold; you can articulate the trade-offs of caching the full response vs caching only candidate IDs.

---

## B2. Supplier Inventory Sync (CDC, Real-Time)

> *"Hotels publish room availability and prices to us via partner APIs and direct integrations. Build a system to keep our catalog fresh in near-real-time."*

### B2.1 Why this is hard

- Tens of thousands of suppliers; many push, many require pulling.
- Mixed protocols: REST APIs, FTP files, XML push, supplier portals, our own CDC from supplier DBs (for direct connect partners).
- Different freshness SLAs — premium partners push every change; long-tail might allow only a daily refresh.
- The same room appears at multiple suppliers; we must reconcile and avoid double-counting.
- Late events, out-of-order events, duplicates. All certain.
- Schema evolution — suppliers add fields, change formats, all the time.

### B2.2 Functional requirements

- Ingest from N supplier connectors (push and pull).
- Parse, validate, enrich, normalize to a canonical schema.
- Detect deltas — only emit *changes*, not full state, to downstream.
- Publish changes to a `hotel.inventory.changed.v1` Kafka topic for downstream consumers (search index, pricing, availability cache).
- Provide a complete history of all inventory states (audit, debugging, replay).

### B2.3 Non-functional

- p95 freshness lag: < 60 seconds for premium partners; < 15 minutes for long-tail.
- Throughput: peak ~500K updates/sec (sales events, holiday booking surges).
- Loss is unacceptable; duplicates are tolerable (idempotent consumers).
- Schema changes from suppliers must not break the pipeline.

### B2.4 Architecture

```
        Premium partner CDC (Debezium → Kafka)
        ──────────────┐
                      │
        Push API      ├──► [ Ingest Gateway ] ──► raw_events topic
        (HTTP, gRPC) ─┘     (auth, rate limit,
                             schema validation)
        Pull workers ─┘
        (poll suppliers
         on schedule)
                                │
                                ▼
                  ┌──────────────────────────┐
                  │ Stream Processor (Flink)  │
                  │  - dedup (idempotency key)│
                  │  - enrich (lookup hotel)  │
                  │  - normalize to canonical │
                  │  - reconcile (multi-      │
                  │    supplier same room)    │
                  │  - delta detection        │
                  │  - emit changes           │
                  └──────────┬───────────────┘
                             │
                ┌────────────┼─────────────┐
                ▼            ▼             ▼
       ┌────────────┐ ┌─────────────┐ ┌──────────────┐
       │ inventory   │ │ availability │ │ DLQ (errors,│
       │ canonical   │ │ canonical   │ │ schema fails)│
       │ topic       │ │ topic        │ └──────────────┘
       └─────┬───────┘ └─────┬────────┘
             │               │
             ▼               ▼
    ┌─────────────────────────────────┐
    │ Downstream consumers:            │
    │ - Search indexer                 │
    │ - Availability cache writer      │
    │ - Pricing service                │
    │ - Iceberg (raw + canonical) lake │
    └─────────────────────────────────┘
```

### B2.5 Deep dive 1 — Schema strategy

Use **Avro/Protobuf with a Schema Registry**. Versioning rules:
- Producers register schema; only backward-compatible changes accepted.
- Each event carries `schema_version`.
- Canonical schema evolves; mappers from supplier schema → canonical live with the connector.
- Unknown supplier fields land in a `metadata: map<string, string>` extension column.

Schema registry enforces compatibility — `BACKWARD` for consumer-evolved, `FORWARD` for producer-evolved, `FULL` for both. For canonical event streams, **FULL** is the right default.

### B2.6 Deep dive 2 — CDC for direct-connect partners

For partners who give us DB access (direct integrations), use Debezium reading their replication log:
- Postgres: logical replication slots.
- MySQL: binlog with row-format replication.
- Outbox pattern for partners running it on their side.

Each row change becomes a Kafka event with `before`, `after`, and `op` fields. Downstream consumers compute deltas.

### B2.7 Deep dive 3 — Reconciliation (the hardest part)

The same physical room may appear at supplier A and supplier B (and a third bedbank). We must:
1. Match rooms across suppliers (entity resolution via name + GPS + room type + capacity).
2. Pick one as the canonical "primary" for our catalog.
3. Cross-update: if A says "sold out" and B says "5 left," we must not double-list, but we want to keep B's signal.

Approaches:
- **Entity resolution** offline (daily Spark job) — produces a `hotel_alias` mapping table.
- **Online reconciliation** — at write time, look up the canonical hotel ID via the alias table.
- **Confidence scoring** — resolution is rarely 100% certain; track confidence and gate auto-merging at thresholds.

### B2.8 Deep dive 4 — Idempotency and ordering

- Each event has an `idempotency_key` = `(supplier_id, supplier_event_id, version)`.
- Consumers maintain a "seen keys" cache (Redis with TTL) to drop duplicates.
- Within a (supplier, hotel_id) the partition key forces ordering. Across suppliers we cannot order globally.
- The state-store (Flink keyed state) holds the last known state per hotel; compute delta = new vs last.

### B2.9 Failure modes

- Supplier sends malformed payload → DLQ; alert; never block the pipeline.
- Late events arrive after the watermark → reprocess via Flink's allowed lateness, or batch-correct nightly.
- Schema breaking change on producer → schema registry rejects; alert; producer rolled back.
- Kafka topic out of disk → partition expansion; alert; tier old data to S3 (Confluent Tiered Storage / Apache Tiered Storage).

### B2.10 Trade-offs

- **Streaming vs micro-batch** — true streaming for premium (Flink), micro-batch (Spark Structured Streaming, 30-second triggers) for long-tail. Pragmatic.
- **At-least-once with idempotency vs Kafka EOS** — we pick the former; simpler, sufficient with idempotent consumers.
- **Schema-on-write for canonical, schema-on-read for raw** — we land everything in the lake including bad data; only validated stuff goes to the canonical topic.

### 🛠️ Activity B2: Build a CDC mini-pipeline (4 hours)

Use Debezium + Postgres + Kafka. Run a Postgres "supplier" with an `inventory` table. Insert/update rows; observe Debezium emitting events to Kafka. Write a Flink (PyFlink works) or simple Python consumer that:
1. Maintains a state of the last known price per room.
2. Emits a `price_changed` event only when the price actually changes (not on every row touch).
3. Drops duplicates via an idempotency key.

**Done when:** You can flip a row's price in Postgres and see exactly one `price_changed` event in your downstream topic, regardless of how many duplicate Debezium events arrive.

---

## B3. Dynamic Pricing Platform

> *"Build a system that prices hotel rooms dynamically based on demand, supply, competitor prices, and ML-predicted conversion."*

### B3.1 Why this is hard

- **Many inputs** — base rate from supplier, competitor prices, ML demand model, business rules (margin floor, surge cap), customer segment, currency.
- **Real-time but stable** — can't oscillate prices every second; user trust.
- **Multi-currency** with FX rate updates.
- **Auditability** — every price shown must be reproducible for fraud / regulatory reasons.
- **Latency budget** — pricing is in the search hot path; <50 ms.

### B3.2 Functional requirements

- Compute price for `(hotel, room_type, dates, party_size, customer_segment, currency)`.
- Allow business rules engine: "for hotel X, never go below Y%; never above Z%."
- Support A/B testing of pricing models.
- Serve cached "shelf prices" for search; live recompute at booking.
- Audit trail: every quote stored with its inputs (model version, rules applied, FX rate).

### B3.3 Non-functional

- p99 < 50 ms for shelf price; <200 ms for live booking quote.
- 100K QPS at peak.
- Currency precision: 4 decimal places internally, rounded at presentation.
- Auditability: 7-year retention for compliance.

### B3.4 Architecture

```
                     ┌─ Demand model server ───┐
   ┌──────────┐      │ (gradient boost / DNN,  │
   │ Pricing  │◄────►│  served from Triton)    │
   │ Service  │      └─────────────────────────┘
   │          │
   │ - inputs │      ┌─ Competitor price feed ─┐
   │   from:  │◄────►│ (Kafka topic, scrapers, │
   │   1-4    │      │  aggregator partners)   │
   │ - rules  │      └─────────────────────────┘
   │   engine │      
   │ - ab     │      ┌─ Rules engine ───┐
   │   route  │◄────►│ (e.g. OPA, or    │
   │ - price  │      │  internal DSL)   │
   │   cache  │      └──────────────────┘
   │ - audit  │      
   │   sink   │      ┌─ FX rates ───────┐
   └────┬─────┘◄────►│ (Redis, 1-min TTL│
        │            │  from FX feed)   │
        ▼            └──────────────────┘
   ┌─────────────────┐
   │ Audit log       │
   │ (Kafka → S3 +    │
   │  Iceberg)        │
   └──────────────────┘
```

### B3.5 The pricing formula (a worked example)

```
price_USD = base_supplier_rate
          × demand_multiplier(hotel, dates, party)        # ML
          × competitive_factor(median_competitor_price)    # rule
          × segment_modifier(customer_segment, ab_arm)     # personalization
          × surge_cap                                       # safety
price_local = price_USD × FX_rate(local_currency)
price_displayed = round_to_currency_precision(price_local, currency)
```

Each multiplier is independently testable, monitorable, and rollback-able.

### B3.6 Deep dive 1 — Two-tier pricing

- **Shelf price** — cached, slightly stale (5-min TTL), used in search results. Served from Redis.
- **Booking-time price** — live computation when the user clicks "Book." Reserved for ~10–15 minutes (price hold). If the live price is materially different from the shelf, show a "price updated" notice.

This is a fundamental UX trade-off. Showing the live price for every search would 10× cost. Showing only the cached price would let users book at outdated rates.

### B3.7 Deep dive 2 — Audit trail

Every quote emits an event:
```
{
  "quote_id": "q_abc123",
  "ts": "2025-...",
  "inputs": {
    "hotel_id": "h_12345",
    "dates": ["2025-06-01", "2025-06-03"],
    "party": {"adults": 2},
    "segment": "loyalty_gold",
    "ab_arm": "model_v3"
  },
  "components": {
    "base_supplier_rate": 100.00,
    "demand_multiplier": 1.18,
    "competitive_factor": 0.97,
    "segment_modifier": 0.95,
    "surge_cap_applied": false,
    "fx_rate_USD_to_INR": 83.42
  },
  "final_displayed": {"amount": 9275, "currency": "INR"},
  "model_version": "v3.4.2",
  "rules_version": "rules-2025-04-12"
}
```

Land in Kafka → S3 → Iceberg. Query in BigQuery or Trino for "show me how the price for hotel X at date Y was computed at time T."

### B3.8 Deep dive 3 — Online experimentation

- The pricing service consults an experiment service to get the user's arm: `model_v3` or `model_v4`.
- Both models are deployed; traffic split 50/50.
- Per-arm metrics: revenue per search, conversion rate, average margin. (See B5.)
- Model upgrades are *experiments*, not deploys.

### B3.9 Deep dive 4 — Latency budget

```
Total budget: 50 ms
- Cache lookup (Redis): 1 ms
- Demand model inference (batch of 25): 15 ms
- Rules engine: 2 ms
- FX lookup (Redis): 1 ms
- Audit emit (async, non-blocking): 0 ms
Headroom: 31 ms — used for tail latency, network, GC.
```

Most cache hits are sub-5 ms. Cache misses dominate p99.

### B3.10 Failure modes

- Demand model down → fall back to demand_multiplier = 1.0 (no demand premium); alert.
- Competitor feed stale > 1 hour → use last known good; alert; rules engine should clamp.
- FX rate stale > 5 minutes → use last known good with a `stale_fx` flag; reject for high-margin segments where exact FX matters.

### 🛠️ Activity B3: Build a pricing service with audit (3 hours)

```python
from fastapi import FastAPI
import redis, time, json, uuid

app = FastAPI()
r = redis.Redis(decode_responses=True)

def get_demand(hotel_id, dates):
    # In real life, model inference; for now a synthetic signal.
    return 1.0 + 0.3 * abs(hash(f"{hotel_id}:{dates[0]}")) % 100 / 100

def get_competitor_factor(hotel_id):
    return 0.97  # placeholder

def get_fx(currency):
    return float(r.get(f"fx:{currency}") or 1.0)

@app.get("/price")
def price(hotel_id: str, checkin: str, checkout: str, currency: str = "USD"):
    quote_id = str(uuid.uuid4())
    base = 100.0  # would come from supplier API
    demand = get_demand(hotel_id, [checkin, checkout])
    comp = get_competitor_factor(hotel_id)
    fx = get_fx(currency)
    
    final = base * demand * comp * fx
    
    audit = {
        "quote_id": quote_id, "ts": time.time(),
        "hotel_id": hotel_id, "dates": [checkin, checkout],
        "components": {"base": base, "demand": demand, 
                        "competitive": comp, "fx": fx},
        "final": round(final, 2), "currency": currency,
        "model_version": "v1.0"
    }
    # Async-publish to Kafka in real life; here just print
    print(json.dumps(audit))
    
    return {"quote_id": quote_id, "amount": round(final, 2), 
            "currency": currency, "valid_for_seconds": 600}
```

Add Redis caching with `quote_id` lookup so the booking endpoint can verify the price.

**Done when:** Every quote has an audit record; you can recompute the price from the audit and get the same answer.

---

## B4. Booking / Reservation Transaction System

> *"Build the booking system. User selects a hotel + dates + room; we charge them, decrement inventory, send confirmation, notify the supplier. Must be reliable, must not double-sell, must handle concurrent bookings of the last room."*

This is the most-asked, most-watched part of the interview. **Treat it as the centerpiece.**

### B4.1 Functional requirements

- Confirm a quote → reserve inventory → charge payment → write booking → send confirmation → notify supplier.
- Handle cancellation (within policy) → refund → release inventory.
- Idempotency: client may retry; we must not double-charge or double-book.
- Multiple payment methods (card, wallet, partial points, BNPL).
- Multi-currency.

### B4.2 Non-functional

- Booking commit p99 < 3 s.
- Zero overselling.
- 99.99% availability for the booking flow (it's the money path).
- Strong consistency on inventory; eventual on confirmation email.
- PCI-DSS compliance — payment data never touches our systems unencrypted; tokenize at the gateway.

### B4.3 Estimation

- ~10K bookings/sec at global peak (compare 50K searches/sec; ratio ~5:1 search:book at conversion).
- Each booking touches: inventory, payment, ledger, supplier API, email queue. Latency adds up.
- Annual: ~300M bookings × ~5 KB metadata = ~1.5 TB/year. Trivial.

### B4.4 Architecture — Saga pattern

A booking is a *distributed transaction* across multiple systems. 2PC is unworkable (third-party APIs don't speak XA). Use the **Saga** pattern: split into local transactions, each with a compensating action.

```
        Client
          │
          │ POST /book {quote_id, idempotency_key, payment_token, ...}
          ▼
    ┌──────────────────────┐
    │ Booking API          │  ── Outbox pattern
    │ Validates idempotent │     (Postgres + Kafka)
    │ Creates "pending"    │
    │ booking row          │
    └──────┬───────────────┘
           │
           │ kafka: booking.created
           ▼
    ┌──────────────────────────────┐
    │  Booking Saga Orchestrator    │
    │  (Temporal workflow)          │
    │  Steps:                       │
    │   1. ReserveInventory         │── compensate: ReleaseInventory
    │   2. AuthorizePayment         │── compensate: VoidAuthorization
    │   3. ConfirmInventory         │── compensate: ReleaseInventory
    │   4. CapturePayment           │── compensate: RefundPayment
    │   5. WriteFinalBooking        │── compensate: MarkCancelled
    │   6. NotifySupplier (async)   │── retry-only
    │   7. SendConfirmation (async) │── retry-only
    └──────────────────────────────┘
```

**Why Temporal (or Cadence / Step Functions)?** Because:
- Workflows are durable — orchestrator state survives crashes.
- Compensations are first-class.
- Retries with backoff are built-in.
- You get observable workflow history for free — critical for support.

### B4.5 Deep dive 1 — Inventory locking (the no-oversell guarantee)

The golden rule: at the moment of "ReserveInventory," we *atomically* check-and-decrement.

**Option A — Postgres row-level lock with conditional update:**
```sql
UPDATE availability
SET rooms_held = rooms_held + 1
WHERE hotel_id = $1 AND room_type = $2 AND date = $3
  AND (rooms_total - rooms_sold - rooms_held) >= 1
RETURNING *;
```
If 0 rows returned, no inventory. Postgres's MVCC + this conditional UPDATE makes it linearizable. Index `(hotel_id, room_type, date)`.

**Option B — Redis with Lua script (atomic):**
```lua
local available = tonumber(redis.call('GET', KEYS[1]))
if available and available > 0 then
    redis.call('DECR', KEYS[1])
    return 1
else
    return 0
end
```
Faster, but Redis is not your durable inventory store — it's a cache. The Postgres update remains the truth; Redis is for fast pre-checks.

**Pattern**: Redis fast pre-check → Postgres authoritative decrement. Most users hit the Redis fast path; cache misses fall through.

### B4.6 Deep dive 2 — Idempotency

The client sends `Idempotency-Key: <UUID>` with every request. Server stores `(idempotency_key, response)` in a small KV with 24-hour TTL.

```python
def book(req):
    cached = idem_store.get(req.idempotency_key)
    if cached:
        return cached.response  # exact same response, even if stale
    
    response = do_booking(req)
    idem_store.put(req.idempotency_key, response, ttl=86400)
    return response
```

Subtleties:
- Two concurrent retries with the same key: use SETNX; the loser waits for the winner.
- Mismatched body with same key: reject 422; the client has a bug.
- This protects against *retries*; it doesn't help if the client uses different keys.

### B4.7 Deep dive 3 — Payment integration

- We **never** see raw card data. The frontend sends card data to our PSP (Stripe, Adyen) → gets back a `payment_token`.
- Our backend authorizes against the token: `auth_id = psp.authorize(token, amount, currency)`.
- On saga commit: capture (`psp.capture(auth_id)`).
- On saga compensation: void (`psp.void(auth_id)`) if not yet captured, refund (`psp.refund(auth_id)`) if captured.
- Idempotency at the PSP is also critical — they expose their own idempotency keys.

### B4.8 Deep dive 4 — Outbox pattern (don't lose events)

When the Booking API writes the "pending" booking, it also wants to emit a `booking.created` Kafka event so the saga orchestrator picks it up. **Don't dual-write** (DB then Kafka) — they can diverge.

The outbox pattern:
```sql
BEGIN;
INSERT INTO bookings (...) VALUES (...);
INSERT INTO outbox (event_type, payload) 
  VALUES ('booking.created', '{"booking_id": ...}');
COMMIT;
```

Both writes are atomic. A separate process (Debezium or a polling worker) reads the outbox and publishes to Kafka. Now the DB write and the event publication share fate.

### B4.9 Deep dive 5 — Concurrent last-room booking

Two users hit "Book" within 10 ms; only one room left.

1. Both pass quote validation (quote was valid 10 minutes ago).
2. Both pass Redis fast-check (cache says 1 left).
3. Both reach Postgres `UPDATE … WHERE rooms_available >= 1`.
4. Postgres serializes them via row lock; one succeeds (`rooms_held = 1`), one returns 0 rows.
5. The loser gets a "no longer available" response; their saga short-circuits before payment.

Test this in your local stack with two concurrent clients hitting the same hotel/date. Verify: exactly one succeeds; the other gets a 409.

### B4.10 Failure modes

- Payment authorized but inventory step fails → compensate: void payment; user sees "couldn't book; nothing charged."
- Inventory reserved but payment fails → compensate: release inventory; user sees "payment declined."
- Supplier notification fails after we charged + reserved → retry indefinitely with backoff; this *cannot* fail the user's booking. Surface to ops if it doesn't recover.
- Saga orchestrator crashes mid-flow → Temporal resumes from checkpoint; all steps idempotent so retry is safe.

### B4.11 Trade-offs

- **Saga vs 2PC** — saga because third-party PSPs and supplier APIs don't speak XA. The cost: compensation logic for every step.
- **Strong consistency on inventory** — the only operation in the system where we accept the latency cost.
- **Idempotency keys with 24h TTL** — covers retries; longer is overkill.
- **Async confirmation email** — email arriving 5 minutes late is fine; booking failing because email queue is full is not.

### 🛠️ Activity B4: Build the booking saga (6 hours)

This is the largest activity in the course. Build:
1. A FastAPI booking endpoint that creates a "pending" booking via the outbox pattern.
2. A Temporal worker (or a simulated saga in pure Python with retries and compensations) implementing the 5 steps.
3. Postgres for inventory with the conditional update.
4. A "fake" payment service (just an HTTP service that returns success/failure based on amount).
5. Kafka for the outbox.

Test:
- Happy path: book a room, verify inventory decremented, payment captured, email queued.
- Concurrent last-room: two clients race; exactly one succeeds.
- Payment failure: inventory is released after compensation.
- Crash mid-saga: kill the worker between steps 2 and 3; restart; verify it resumes correctly.

**Done when:** All four scenarios pass and you can articulate every state transition.

---

## B5. Clickstream Analytics & A/B Testing

> *"Every user action — view, click, search, add-to-favorites, book — is captured. Build the pipeline + analytics layer that powers experimentation and product analytics."*

### B5.1 Functional requirements

- Capture client-side and server-side events at scale.
- Schema-validated, deduplicated, attributed.
- Land in a queryable store with sub-minute freshness for dashboards.
- Power experiment metrics with statistical rigor (significance, guardrails).
- Support both real-time (sub-second alerts on metric anomalies) and batch (daily cohort analyses).

### B5.2 Non-functional

- Ingest: 1M events/sec at peak.
- Loss < 0.1%.
- Query freshness: real-time dashboards < 30 s lag; ad-hoc < 5 min.
- 90-day raw retention; 5-year aggregated.
- Per-event cost: < $0.0000005 ingest+storage.

### B5.3 Architecture

```
   Browser/mobile        Backend services
       │                       │
       └──────┬────────────────┘
              ▼
    ┌────────────────────┐
    │ Edge Collector      │  (rate limit, sampling,
    │ (CDN edge worker /  │   schema validation, GeoIP)
    │  HTTP ingest API)   │
    └────────┬───────────┘
             │
             ▼
    ┌────────────────────┐
    │ Kafka: events.raw   │  ── partition by user_id (consistent ordering)
    └────────┬───────────┘
             │
             ├─────────────► [ Real-time: Flink ─► StarRocks/ClickHouse/Druid ]
             │                  - Per-experiment counters
             │                  - Funnels in 30s windows
             │
             └─────────────► [ Batch: Iceberg on S3 ]
                                - Raw → Bronze
                                - Bronze → Silver (cleaned, joined to dims)
                                - Silver → Gold (aggregates, cohorts)
                                - Queried by Trino / Spark / dbt
```

### B5.4 Data model (event envelope)

```
{
  "event_id": "uuid",                    // for dedup
  "event_type": "search_performed",      // namespaced
  "ts_event": 1714999999000,              // client time
  "ts_received": 1715000000000,           // server time
  "user_id": "u_42",
  "session_id": "s_xyz",
  "device": {...},
  "geo": {...},                          // from edge GeoIP
  "experiment_arms": {"pricing": "v3", "ranker": "control"},
  "context": {...},                      // page, query, etc.
  "properties": {...}                    // event-specific
}
```

**Critical rules:**
- `event_id` set at the source for dedup.
- `ts_event` and `ts_received` are different — use event time for analytics.
- `experiment_arms` propagated *server-side* and stamped at ingestion — never trust client-supplied arm.

### B5.5 Deep dive 1 — Schema evolution at scale

Add a field to a thousand-times-a-second event. How?
- Avro/Protobuf with a registry; backward-compat checked.
- New consumers handle missing field with default.
- Old consumers ignore new field.
- For breaking changes: emit `event_type.v2`; run both for a deprecation window.

The data lake (Iceberg) supports schema evolution natively — adding a column is metadata-only.

### B5.6 Deep dive 2 — Experiment framework

A user's *experiment arm* must be:
- Deterministic from `(user_id, experiment_id)` — same user always gets same arm; replays of analysis are deterministic.
- Stamped at the *first relevant decision point* and propagated through subsequent events.
- Subject to *guardrails* — never assign more than X% to a risky variant; ramp gradually.
- Mutually exclusive with conflicting experiments.

Hash-bucketed assignment:
```python
def assign_arm(user_id, experiment_id, arms):
    h = int(hashlib.md5(f"{user_id}:{experiment_id}".encode()).hexdigest(), 16)
    bucket = h % 10000  # 0..9999
    cumulative = 0
    for arm, weight_bps in arms.items():  # weights in basis points
        cumulative += weight_bps
        if bucket < cumulative:
            return arm
```

### B5.7 Deep dive 3 — Statistical machinery

For every experiment metric, the pipeline computes:
- Mean and variance per arm.
- Sample size.
- Effect size (control vs. treatment).
- Confidence interval (95% default).
- p-value (frequentist) or posterior probability (Bayesian).

**Common pitfalls:**
- **Peeking** — looking at the experiment too early and stopping when significant. Use sequential testing or pre-registered fixed sample sizes.
- **Sample ratio mismatch (SRM)** — if your 50/50 split actually delivers 51/49, something is broken; alert.
- **Novelty effects** — first week of an experiment is biased; ignore the warmup period.
- **Multiple-comparisons** — tracking 10 metrics, one will hit p < 0.05 by chance. Bonferroni or FDR correction.

### B5.8 Deep dive 4 — Cost optimization

Click events at 1M/sec × 1 KB × 86400 seconds = ~85 TB/day. At BigQuery / Snowflake on-demand prices, naive querying is six figures/year.

- **Pre-aggregate** — hourly cubes for the top 50 dimensions.
- **Sample for ad-hoc** — 1% sample for exploratory work; full data only for committed analyses.
- **Tier storage** — raw events older than 30 days to Glacier.
- **Materialized experiment metrics** — every experiment has a daily refresh job that writes to a small `experiment_metrics` table.

### B5.9 Failure modes

- Edge collector overloaded → 429 responses; client retries with backoff. Acceptable; some dropped events.
- Kafka topic out of partitions → expand at Kafka level; consumers rebalance.
- Flink job lagging → scale slots; if persistent, drop sampling rate.
- Schema-incompatible event → DLQ; the source service is rolled back.

### B5.10 Trade-offs

- **Real-time + batch** dual lanes — Lambda architecture. Necessary for the use cases (real-time alerts vs deep cohort analysis).
- **Sampling for cost** — accept 1% sampling on raw event scans; experiment metrics use full data because precision matters.
- **Kafka partition by user_id** — gets consistent per-user ordering; risks hot partitions for power users.

### 🛠️ Activity B5: Build the experiment framework (4 hours)

1. Implement deterministic arm assignment.
2. Stamp arms onto Kafka events.
3. In Flink (or pure Python with a window over the event stream), compute conversion rate per arm in 5-min windows.
4. Add SRM detection.
5. Compute a confidence interval and a p-value at the end of each window.

**Done when:** You can simulate an A/B test where treatment converts 10% better; the pipeline correctly attributes events; the p-value drops below 0.05 after enough samples; SRM stays clean (50/50).

---

## B6. ML Feature Store for Recommendations

> *"Build a feature store that powers personalized hotel recommendations. Online lookups in <5 ms p99; offline historical for training."*

### B6.1 Functional requirements

- Online: serve features for a given `(user_id, hotel_id, context)` in single-digit ms.
- Offline: produce point-in-time-correct training data given an `(entity, event_time)` spine.
- Same feature definition compiles to both online and offline code paths (no skew).
- Feature versioning, ownership, freshness SLA, lineage.

### B6.2 Non-functional

- Online p99: 5 ms.
- Offline backfill: TBs in hours.
- Online cost per lookup: < $0.0000001.
- Multi-tenant: each ML team owns their feature group.

### B6.3 Feature catalog (representative)

**User features:**
- `user.searches_30d`, `user.bookings_lifetime`, `user.avg_price_paid`, `user.preferred_star_rating`, `user.embeddings_v3`, `user.last_destination`, `user.churn_risk_score`.

**Hotel features:**
- `hotel.bookings_30d`, `hotel.cancel_rate`, `hotel.avg_review_score`, `hotel.embeddings_v3`, `hotel.price_volatility`, `hotel.image_quality_score`.

**User × hotel features:**
- `user_hotel.has_visited`, `user_hotel.affinity_score` (collaborative filter).

**Context features:**
- `context.day_of_week`, `context.is_weekend`, `context.local_holiday`, `context.device_class`.

### B6.4 Architecture

```
        Source events (Kafka, DB)
                │
        ┌───────┴───────┐
        │               │
   ┌─────────┐    ┌──────────────┐
   │ Stream  │    │ Batch         │
   │ jobs    │    │ jobs          │
   │ (Flink) │    │ (Spark + dbt) │
   │ — fast  │    │ — full history│
   │  features│   │                │
   └────┬────┘    └────────┬──────┘
        │                  │
        ▼                  ▼
   ┌────────────┐  ┌──────────────┐
   │ ONLINE     │  │ OFFLINE       │
   │ Redis /    │  │ Iceberg /     │
   │ DynamoDB / │  │ BigQuery /    │
   │ Cassandra  │  │ Snowflake     │
   │ (KV by     │  │ (partitioned  │
   │  entity)   │  │  by event_ts) │
   └────────────┘  └──────────────┘
        ▲                  ▲
        │                  │
   inference         training data
```

### B6.5 Feature definition (single source of truth)

```python
@feature_view(
    entities=["user_id"],
    online=True,
    offline=True,
    ttl="30d",
    owner="search-relevance@",
)
def user_recent_metrics(user_id):
    sql = """
    SELECT user_id,
           COUNT(*) FILTER (WHERE event_type='search') AS searches_30d,
           COUNT(*) FILTER (WHERE event_type='booking') AS bookings_30d,
           AVG(amount) FILTER (WHERE event_type='booking') AS avg_price_paid_30d
    FROM events
    WHERE event_ts > NOW() - INTERVAL '30 days'
      AND user_id = :user_id
    GROUP BY user_id
    """
    return sql
```

The framework compiles this to both:
- **Batch**: a Spark/dbt job that writes to the offline store partitioned by `event_ts`.
- **Stream**: a Flink job that maintains rolling aggregates and writes to the online store.

### B6.6 Deep dive 1 — Point-in-time correctness

The killer bug in ML pipelines: training labels are joined to *current* feature values, not values *as of the prediction time*. Result: features include the future. Models look great in offline eval; collapse in production.

**The PIT-join pattern:** for each training example, join features as they were at `event_ts`:

```sql
SELECT
  e.user_id, e.event_ts, e.label,
  f.searches_30d, f.bookings_30d
FROM events e
LEFT JOIN LATERAL (
  SELECT * FROM user_features f
  WHERE f.user_id = e.user_id 
    AND f.feature_ts <= e.event_ts
  ORDER BY f.feature_ts DESC LIMIT 1
) f ON true;
```

**Why this is hard at scale**: you may have billions of events × millions of features. Specialized systems (Tecton, Feast, Hopsworks) materialize this efficiently via temporal joins.

### B6.7 Deep dive 2 — Online lookup latency

5 ms p99 means: one network hop to the online store, no cross-region, batched lookup of all features for one prediction.

**Design choices:**
- One key per `(entity, feature_set)` — lookup is one GET; feature_set is the model's inputs.
- Co-locate online store with the inference service (same AZ).
- Fan-out: model needs user features + hotel features (×500 candidates) + context. That's 502 lookups. Use **mget** or **batch get**; pipeline if needed; in practice 1-2 ms for the whole batch from Redis.
- Pre-fetch user features at session start (one fetch, cached for the session) to avoid repeated lookups.

### B6.8 Deep dive 3 — Materialization freshness

Streaming features (searches_30d, bookings_30d) must be incrementally maintained. Approaches:
- **Sliding window** (Flink) — keyed state holds the last 30 days; events update the count.
- **Tumbling daily** + read-time merge — daily partition + today's stream-state. Simpler, larger fanout at read.
- **Approximate** (HyperLogLog, count-min sketch) for counts that don't need to be exact — fits into Redis cheaply.

### B6.9 Failure modes

- Online store down → fall back to default values (zero-filled or a "cold-start" feature set); model degrades but doesn't fail.
- Stream feature lag spike → fall back to batch values; warn that some features are stale.
- Schema change → versioned feature names (`searches_30d_v2`); deploy producer first, consumer after.

### B6.10 Trade-offs

- **Streaming + batch dual** — necessary; some features are inherently batch (e.g., trained embeddings refresh weekly).
- **Online store choice** — Redis for sub-ms with ephemeral persistence; DynamoDB/Cassandra for huge-scale durable; pick from access pattern.
- **Build vs Buy** — Tecton/Feast/Hopsworks save 18 months of engineering; cost real money. The trade depends on team size.

### 🛠️ Activity B6: Build a tiny feature store with PIT correctness (4 hours)

1. Generate synthetic events: searches and bookings for 10K users over 90 days.
2. Materialize batch features into SQLite or DuckDB.
3. Materialize the same features into Redis via a streaming-style update loop.
4. Implement a PIT-join: given a training table `(user_id, event_ts, label)`, output the features as they were at each `event_ts`.
5. Implement online lookup: given `(user_id, list_of_features)`, return them from Redis in one batched call.

**Done when:** Your batch and online materialization produce *identical* feature values for the same point in time, and your PIT join doesn't leak future data.

---

## B7. Financial Data Pipeline (FINUDP-style)

> *"Build the financial pipeline. Every booking, refund, supplier payout, currency conversion, tax line, fee. Reconciles with PSP, supplier statements, and accounting. Audit-grade."*

This question separates Senior from Staff. Most candidates underestimate it.

### B7.1 Functional requirements

- Capture every monetary event from booking, payment, refund, chargeback, supplier payout, FX, tax, fees, promotions.
- Land in an immutable ledger.
- Daily three-way reconciliation: our ledger ↔ PSP statements ↔ supplier statements.
- Produce regulatory financial reports (revenue recognition, taxes, transfer pricing).
- Audit trail with cryptographic integrity.

### B7.2 Non-functional

- Zero data loss (financial-grade).
- Reproducibility: any historical balance must be re-derivable from the ledger.
- 7–10 year retention for compliance.
- Daily reconciliation completes < 6 hours.
- Strong consistency on the ledger; eventual on derived reports.

### B7.3 Why "FINUDP-style"

A "Financial Data Unification Platform" centralizes all monetary events from every source into one canonical ledger. The shape mirrors **double-entry bookkeeping**:

Every transaction is two or more entries that sum to zero:
```
Booking #B100: $100
  CREDIT Revenue                +$100
  DEBIT  Cash (PSP receivable)  -$100

Supplier payout for B100:
  CREDIT Cash (PSP receivable)  +$80
  DEBIT  Supplier payable       -$80
  
Margin retained:
  (already in revenue recognition: $20)
```

The ledger is **append-only**; corrections are *new entries that reverse and rebook*, never updates.

### B7.4 Architecture

```
   Booking events ──┐
   Payment events ──┤
   Refund events ───┤
   Supplier acks ───┼──► [ Event ingestion (Kafka) ]
   FX feed ─────────┤
   Tax engine ──────┤
   Promo grants ────┘
                              │
                              ▼
                  ┌────────────────────────────┐
                  │ Ledger Builder (Flink)      │
                  │  - apply business rules     │
                  │  - generate double entries  │
                  │  - validate sums to zero    │
                  │  - dedup via idempotency_key│
                  └────────┬───────────────────┘
                           │
                           ▼
                  ┌────────────────────────────┐
                  │ Append-only Ledger          │
                  │ (Postgres for OLTP queries  │
                  │  + Iceberg for warehouse)   │
                  │  Each row immutable         │
                  └────────┬───────────────────┘
                           │
              ┌────────────┼─────────────┬─────────────┐
              ▼            ▼             ▼             ▼
      ┌─────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
      │ Reconcil-    │ │ Revenue  │ │ Reports  │ │ Audit       │
      │ iation jobs  │ │ recogn.  │ │ (BigQuery │ │ (immutable, │
      │ (Spark)      │ │ jobs     │ │  /Snowflk)│ │  hash-chained)│
      └─────────────┘ └──────────┘ └──────────┘ └──────────────┘
```

### B7.5 Deep dive 1 — Idempotency at every layer

Multiple sources will deliver the same event due to retries. Each ingest event has:
```
idempotency_key = HASH(source_system, source_event_id, version)
```

The ledger builder maintains a "seen keys" table. Already-seen events are dropped silently. Critical because reprocessing a booking event twice would create double the revenue entries.

### B7.6 Deep dive 2 — Reconciliation

Three statements should agree:
1. **Our ledger** — what we *think* happened.
2. **PSP statement** — what the payment processor actually settled.
3. **Supplier statement** — what suppliers say we owe / paid.

Daily Spark job:
- Pull yesterday's PSP file, supplier files.
- Join with our ledger by `transaction_id`.
- Categorize discrepancies: missing on either side, amount mismatch, FX mismatch, tax mismatch.
- Produce an **exception report**.

Most discrepancies are timing (event lands tomorrow) or rounding (FX precision). Persistent ones go to operations for manual investigation.

### B7.7 Deep dive 3 — FX and currency precision

A booking might:
- Be made in INR.
- Be charged in INR.
- Be paid to supplier in USD.
- Be reported in EUR (HQ currency).

Every conversion must use a *captured* FX rate (the one used at the moment), not "today's rate." This rate is part of the ledger entry.

Storage:
- All amounts as integers in minor units (paise, cents) with currency code.
- FX rates as fixed-point decimals with 8+ digits.
- Rounding policy explicit and consistent (banker's rounding common).

### B7.8 Deep dive 4 — Audit & integrity

Hash-chained ledger: each entry contains `prev_hash = HASH(prev_entry)`. Any tampering breaks the chain. Periodically commit the latest hash to a write-once medium (S3 Object Lock, blockchain, or simply a notarized log).

For SOX/equivalent, also:
- Separation of duties — no single person can produce, approve, and reconcile.
- All ledger code changes go through code review with sign-off from finance.
- Backdated entries are forbidden — any "correction" is a new entry today that cancels and rebooks.

### B7.9 Deep dive 5 — Revenue recognition (RevRec)

A $100 booking today doesn't necessarily produce $100 of revenue today. ASC 606 / IFRS 15 require recognition when service is rendered. For travel:
- Booking on May 1 for stay on June 10–12.
- Cash collected May 1 → liability ("deferred revenue").
- Service rendered June 10–12 → recognize revenue then.
- If cancelled May 15 → reverse the deferred revenue, record refund.

The pipeline must produce daily revenue recognition entries. Spark job runs nightly, walks bookings, applies the recognition rules.

### B7.10 Failure modes

- Ledger event ingestion lag → reconciliation reports flagged as incomplete; do not finalize until caught up.
- PSP file missing → reconciliation skips that day's segment; alerts; auto-retries on file arrival.
- Out-of-order events (refund arrives before booking) → ledger builder buffers in keyed state; emits when both arrive (or alerts after a deadline).

### B7.11 Trade-offs

- **Stream + batch hybrid** — stream for ingestion + immediate ledger; batch for daily recon and revenue recognition. Acceptable; finance is OK with T+1.
- **Postgres + Iceberg dual write** — Postgres for sub-second OLTP queries (treasury checks, customer support); Iceberg for analytical history. CDC keeps them in sync.
- **Strong consistency on ledger** — non-negotiable.
- **Audit costs CPU and storage** — accept it; the alternative (audit failure) is an unbounded business risk.

### 🛠️ Activity B7: Build a mini double-entry ledger (5 hours)

1. Define a `ledger_entries` table with columns: `id, ts, txn_id, account, amount_minor, currency, fx_rate, prev_hash, hash`.
2. Insert booking events; produce double-entry rows (revenue + receivable).
3. Verify balance constraint: per `txn_id`, debits = credits.
4. Insert a refund; produce the reversing entries.
5. Daily job: compute account balances; verify global zero.
6. Hash-chain entries; verify integrity.

**Done when:** You can run the chain validator and it returns "valid" before tampering, "invalid at row N" after.

---

# Part C — The TravelHub Capstone

This capstone integrates all 7 systems into one platform you can demo. It's the headline project for your interview portfolio.

## C1. The product

**TravelHub** — a hotel booking platform with:

- Search across 100K simulated hotels, with availability + pricing.
- Real-time supplier inventory sync (synthetic suppliers + CDC).
- Dynamic pricing with audit trail.
- Booking flow with saga orchestration, no overselling.
- Clickstream + A/B testing platform.
- Personalized search ranking via feature store.
- Financial pipeline reconciling bookings, payments, payouts, currencies.

Build it for ~10–12 weeks part-time. By the end, you've *built every system in Part B* and they talk to each other.

## C2. Module-by-module plan

### Module 0 — Foundations (week 1)

- Set up the monorepo. One Docker Compose stack.
- Postgres, Redis, Kafka (Redpanda for local), MinIO, OpenSearch, ClickHouse, Prometheus, Grafana, Jaeger.
- Two services: `gateway` (FastAPI), `auth` (JWT). Both with OpenTelemetry instrumented.
- A canonical event schema with Avro + a local Schema Registry (Karapace works).

**Done when:** You can `docker-compose up`, `curl /healthz`, see traces in Jaeger.

### Module 1 — Hotel Search & Availability (B1, weeks 2–3)

- Generate 100K synthetic hotels with geo data, amenities, photos.
- Index in OpenSearch.
- `Search Service`: returns candidates by geo + filter; calls `Availability Cache` (Redis) and `Pricing Service` (stub for now); merges and ranks (simple heuristic).
- Add caching, load-test with `vegeta` or `hey`.

**Demo moment:** "Show me hotels in Goa for May 10–12 under ₹8000 with pool." Returns in <300 ms p95.

### Module 2 — Supplier Inventory Sync (B2, weeks 3–4)

- Three "suppliers" (each its own Postgres). Different schemas.
- Debezium connectors → Kafka.
- Flink job (PyFlink): normalize, dedup, reconcile, emit `inventory.changed` to canonical topic.
- Search indexer consumes canonical topic; updates OpenSearch.
- Availability cache writer consumes canonical topic; updates Redis.

**Demo moment:** Update a row in supplier-1's DB; <60 seconds later, the search results reflect the new price.

### Module 3 — Dynamic Pricing Platform (B3, week 5)

- `Pricing Service` with the formula in B3.5.
- Demand model stub (a small XGBoost trained on synthetic data).
- Audit topic + S3/MinIO sink.
- Iceberg table for audit; query in DuckDB or Trino.

**Demo moment:** Hit `/price` for the same hotel five times; trace the audit and see how each component (demand, competitive, FX) contributed.

### Module 4 — Booking Saga (B4, weeks 6–7)

- Booking service with outbox pattern.
- Temporal worker implementing the 5-step saga (or Python orchestrator with explicit state machine).
- Postgres inventory with the conditional UPDATE.
- Stub PSP service.
- Integration with search (re-checks at booking time).

**Demo moment:** Run two concurrent clients booking the last room; one succeeds, the other gets 409. Crash the worker mid-saga; restart; saga resumes correctly.

### Module 5 — Clickstream & A/B (B5, week 8)

- Edge collector (FastAPI) ingests events to Kafka.
- Experiment service: deterministic arm assignment.
- Pricing and Search consume the assignment service.
- Flink (or Faust) windows events; emits per-arm metrics to ClickHouse.
- Grafana dashboard with conversion rates per arm, SRM check, p-value.
- Run an experiment: pricing v1 vs v2.

**Demo moment:** Show a dashboard where a treatment arm has higher conversion, with confidence interval.

### Module 6 — Feature Store & Recommendations (B6, week 9)

- Define 5 user features and 5 hotel features.
- Batch materialization via Spark or DuckDB → SQLite/DuckDB offline store.
- Streaming materialization via Flink → Redis online store.
- Search service calls feature store in the ranking step; uses an XGBoost ranker.
- A/B test the personalized ranker against the heuristic.

**Demo moment:** Two users searching the same query see *different* hotel orderings.

### Module 7 — Financial Pipeline (B7, week 10)

- Booking events + payment events + supplier acks → Kafka.
- Flink ledger builder: double-entry rows in Postgres + Iceberg.
- Daily reconciliation: synthetic PSP file + supplier file; Spark job produces an exception report.
- Hash-chained audit ledger; integrity validator.

**Demo moment:** Walk through a booking → its 4 ledger entries → a refund → the 4 reversing entries → the daily recon report showing zero exceptions.

### Module 8 — Cross-cutting (week 11)

- SLOs for each service. Grafana dashboards.
- Distributed traces: a single booking trace touches 7 services; render the waterfall in Jaeger.
- Chaos test: kill Redis, kill a Kafka broker, partition the network. Verify graceful degradation.
- Cost dashboard: CPU/sec per booking; storage per click; data scanned per analytics query.

### Module 9 — Polish (week 12)

- README with architecture diagram and trade-off discussion for each module.
- A 30-minute demo video walking through end-to-end.
- A 1-page "interview cheat sheet" summarizing every system, every trade-off you made, and what you'd do differently with infinite time.

## C3. Cross-cutting design decisions

### C3.1 Event schema strategy

- One **Schema Registry** for canonical events.
- Naming: `<domain>.<entity>.<verb>.<version>` — `booking.reservation.created.v1`, `inventory.room.changed.v1`.
- Mandatory envelope: `event_id`, `event_ts`, `received_ts`, `source`, `correlation_id`, `causation_id`, `version`.
- Schema evolution rules — backward compat default; major version bump on breaking change.
- DLQ topic per service: `<service>.dlq.v1`.

### C3.2 Observability

Three pillars; one stack:
- Prometheus + Grafana for metrics.
- Loki for logs.
- Jaeger for traces.
- All instrumented via OpenTelemetry.

For ML-specific:
- Drift dashboards in Grafana fed from a Flink job on prediction events.

### C3.3 Cost attribution

Every Kafka message and every cloud call carries a `tenant_id` (or `team_id` for internal cost allocation). Daily Spark job aggregates cost by tag → cost dashboard.

### C3.4 Deployment

- All services as Docker containers, with `docker-compose.yml` for local and a Helm chart in a separate repo for K8s.
- Single rolling-deploy strategy; canary for booking and pricing.
- Secrets via env vars locally, Sealed Secrets in K8s.

## C4. Interview demo script

When asked about your project, hit these beats in order:

1. **One-line product** — "TravelHub: a hotel booking platform with seven integrated services. I built it to internalize the system design patterns of a real travel company."
2. **One sentence per service**, each ending with the *hardest part*. "The booking saga used Temporal, and the hardest part was ensuring no oversold rooms under concurrent last-room bookings — solved with an atomic conditional update."
3. **One decision you'd make differently** — shows reflection.
4. **Two metrics** — "p95 search 220 ms, booking p99 1.8 s under 1K concurrent users."
5. **One war story** — a bug you found and fixed. "Initially my Flink job double-counted events when the consumer restarted; the fix was idempotency keys + checkpoint barriers."

If invited to draw, draw the architecture diagram from C2's overview. If invited to dive, pick the *system relevant to the role*: data engineering interviews → B2 (CDC) or B7 (financial). Backend interviews → B4 (booking saga). ML platform interviews → B6 (feature store).

---

# Final Word

By the end of this companion course you will have:

- Internalized **CAP, PACELC, and consistency models** through experiments, not memorization.
- A **catalogue of optimization techniques** with the cost and applicability of each.
- Walked through **seven full system designs** in the travel domain, with the depth a Staff interview demands.
- Built **one integrated capstone** — TravelHub — that demonstrates all seven in a coherent, observable, production-shaped system.

The interview question will not be exactly one of these. It will be a variant. But after this work, you will be designing from *patterns you have seen with your own eyes*, not patterns you have read about in someone else's blog.

That is the difference.
