# Oracle Health PMTS – Forward Deployed Engineer (AI Data Platform)
## HackerRank Screening: EOD Crash Course

> Built for: strong Python, ramping on PySpark / PyTorch / MLE / LLMs / Data Engineering.
> Strategy: maximize MCQ accuracy + survive the coding round + don't get blindsided on Oracle-specific trivia.

---

## 0. Time Allocation (8–12 hours)

| Block | Topic | Hours | Why |
|---|---|---|---|
| 1 | PySpark + Big Data (Kafka, Delta, Parquet, Hadoop) | 3.0 | Your weakest + heaviest JD emphasis |
| 2 | LLMs / RAG / Vector DB / Agents / MCP | 2.0 | Heavy JD weight, easy to ramp |
| 3 | MLOps + PyTorch essentials + Feature Eng | 1.5 | Common MCQ source |
| 4 | Python coding patterns for HackerRank | 1.5 | Coding round survival |
| 5 | System design + Networking + REST/SSE | 1.0 | MCQ + possible design Q |
| 6 | Oracle-specific (OCI, 23ai, BDS, Gen AI) | 0.5 | Trivia round – pure memorization |
| 7 | SQL refresher (windows, CTEs, joins) | 0.5 | Likely 1–2 SQL questions |
| 8 | Mock test + review | 1.0 | Calibration |

**Test format expectation (HackerRank PMTS screening):** 90–120 min, typically:
- 1–2 coding problems (Python, sometimes a Spark/SQL one)
- 20–30 MCQs spanning the full JD stack
- Possibly 1 SQL problem
- Sometimes a short design write-up

---

# PART 1 — PySpark & Big Data (3 hours)

## 1.1 Spark Architecture (memorize this diagram)

```
        ┌─────────────────────┐
        │   Driver Program    │  ← runs SparkContext / SparkSession
        │  (your main code)   │     builds DAG, schedules stages
        └──────────┬──────────┘
                   │
          ┌────────▼────────┐
          │ Cluster Manager │  ← YARN / Kubernetes / Standalone / Mesos
          └────────┬────────┘
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
   ┌────────┐ ┌────────┐  ┌────────┐
   │Executor│ │Executor│  │Executor│  ← JVMs on worker nodes
   │ (tasks)│ │ (tasks)│  │ (tasks)│     run tasks, cache data
   └────────┘ └────────┘  └────────┘
```

**Key facts (MCQ gold):**
- **Driver**: builds DAG, optimizes via Catalyst, splits into stages → tasks, sends to executors.
- **Executor**: runs tasks for a single application; multiple cores per executor = multiple tasks in parallel.
- **Stage**: set of tasks with no shuffle between them; boundary = shuffle.
- **Task**: smallest unit; one per partition per stage.
- **Job**: triggered by an **action**. One action = one job.
- **DAG**: Directed Acyclic Graph of RDD/DataFrame ops; built lazily.
- **Catalyst Optimizer**: rule-based + cost-based query optimizer for DataFrames/SQL.
- **Tungsten**: execution engine — off-heap memory, whole-stage codegen, cache-aware computation.
- **AQE (Adaptive Query Execution)**: runtime re-optimization (since Spark 3.0). Dynamically coalesces shuffle partitions, switches join strategies, handles skew.

## 1.2 RDD vs DataFrame vs Dataset

| | RDD | DataFrame | Dataset |
|---|---|---|---|
| Type safety | ✅ | ❌ (Row) | ✅ (Scala/Java only) |
| Optimized by Catalyst | ❌ | ✅ | ✅ |
| Tungsten encoding | ❌ | ✅ | ✅ |
| Python support | ✅ | ✅ | ❌ (no Dataset in PySpark) |
| Use when | low-level / unstructured | default for structured | Scala + type safety |

**Rule of thumb: in PySpark, use DataFrames. RDDs only for legacy or special low-level work.**

## 1.3 Transformations vs Actions

**Transformations** (lazy — build DAG, don't execute):
- **Narrow** (no shuffle, 1:1 partition mapping): `map`, `filter`, `select`, `withColumn`, `union`, `mapPartitions`
- **Wide** (shuffle): `groupBy`, `reduceByKey`, `join`, `distinct`, `orderBy`, `repartition`

**Actions** (trigger execution):
- `collect()`, `count()`, `show()`, `take(n)`, `first()`, `write.*`, `toPandas()`, `foreach()`, `reduce()`

**MCQ trap:** `cache()` and `persist()` are transformations — they don't execute until an action runs.

## 1.4 PySpark — must-know code patterns

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

spark = (SparkSession.builder
    .appName("app")
    .config("spark.sql.shuffle.partitions", "200")
    .config("spark.sql.adaptive.enabled", "true")
    .getOrCreate())

# Read
df = spark.read.parquet("s3://bucket/path/")
df = spark.read.option("header", True).option("inferSchema", True).csv("path")
df = spark.read.format("delta").load("path")

# Explicit schema (faster than inferSchema)
schema = StructType([
    StructField("id", IntegerType(), False),
    StructField("name", StringType(), True),
])

# Core ops
df.select("col1", "col2")
df.filter(F.col("age") > 30)
df.withColumn("new", F.col("a") + F.col("b"))
df.withColumnRenamed("old", "new")
df.drop("col")
df.distinct()
df.dropDuplicates(["id"])

# Aggregations
df.groupBy("dept").agg(
    F.count("*").alias("cnt"),
    F.avg("salary").alias("avg_sal"),
    F.max("salary").alias("max_sal"),
    F.collect_list("name").alias("names")
)

# Joins
df1.join(df2, "id", "inner")           # inner, left, right, outer, left_semi, left_anti
df1.join(df2, df1.id == df2.uid, "left")

# Broadcast join (small table → all executors)
from pyspark.sql.functions import broadcast
df1.join(broadcast(df2), "id")

# Window functions
w = Window.partitionBy("dept").orderBy(F.col("salary").desc())
df.withColumn("rank", F.row_number().over(w))
df.withColumn("running_total", F.sum("salary").over(w.rowsBetween(Window.unboundedPreceding, 0)))

# UDF (avoid if possible — use built-in functions instead)
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
upper_udf = udf(lambda x: x.upper(), StringType())
# Better: use pandas_udf (vectorized) for performance
from pyspark.sql.functions import pandas_udf
@pandas_udf(StringType())
def upper_p(s): return s.str.upper()

# Repartition vs coalesce
df.repartition(10)            # full shuffle, can increase or decrease
df.repartition("country")     # hash partition by column
df.coalesce(5)                # no shuffle, only DECREASE partitions

# Cache
df.cache()                    # MEMORY_AND_DISK default for DataFrame
df.persist(StorageLevel.MEMORY_ONLY)

# Write
df.write.mode("overwrite").partitionBy("year", "month").parquet("path")
df.write.format("delta").mode("append").save("path")
```

**MCQ traps:**
- `inferSchema=True` requires an extra pass over data — slower than explicit schema.
- `coalesce` can NOT increase partitions; `repartition` can.
- UDFs serialize Python ↔ JVM per row → slow. Prefer built-ins or `pandas_udf`.
- `collect()` brings ALL data to driver — OOM risk.

## 1.5 Partitioning, Shuffles, Skew

**Why shuffles are expensive:** network I/O + disk I/O + serialization across all executors.

**Causes of shuffles:** `groupBy`, `join`, `distinct`, `repartition`, `orderBy`, `window` with partitionBy.

**Default shuffle partitions:** `spark.sql.shuffle.partitions = 200` (often needs tuning).

**Data skew handling (very common MCQ):**
1. **Salting**: add random suffix to skewed keys, aggregate, then de-salt.
2. **Broadcast join** if one side is small (<10MB default, tunable via `spark.sql.autoBroadcastJoinThreshold`).
3. **AQE skew join** (Spark 3.0+): auto-splits skewed partitions.
4. **Pre-aggregation** before join to reduce key cardinality.

**Salting example:**
```python
# Skewed key 'A' shows up 1M times, others 1K
df_skewed = df.withColumn("salt", (F.rand() * 10).cast("int"))
df_skewed = df_skewed.withColumn("key_salted", F.concat(F.col("key"), F.lit("_"), F.col("salt")))
# Replicate small side
df_small_replicated = df_small.crossJoin(
    spark.range(10).withColumnRenamed("id", "salt")
).withColumn("key_salted", F.concat(F.col("key"), F.lit("_"), F.col("salt")))
joined = df_skewed.join(df_small_replicated, "key_salted")
```

## 1.6 Join Strategies (Spark picks one per join)

| Strategy | When | Cost |
|---|---|---|
| **Broadcast Hash Join** | one side < threshold (~10MB) | best |
| **Shuffle Hash Join** | one side fits in executor memory after shuffle | medium |
| **Sort-Merge Join** | both sides large, default for big joins | OK but shuffle-heavy |
| **Broadcast Nested Loop** | non-equi joins, one side tiny | last resort |
| **Cartesian** | cross join | avoid |

## 1.7 Parquet (columnar storage)

- **Columnar** → reads only needed columns (predicate/projection pushdown).
- **Compression**: snappy (default, fast), gzip (smaller, slower), zstd (best balance modern).
- **Row groups** = chunks of rows; stats per row group enable skipping.
- **Schema embedded** in file footer.
- **Splittable** → parallel reads.
- Compared to **ORC**: similar, ORC stronger in Hive ecosystem, Parquet in Spark.

## 1.8 Delta Lake (CRITICAL for this JD)

Delta = Parquet + transaction log (`_delta_log/`). Adds ACID to data lakes.

**Features (memorize):**
- **ACID transactions** via optimistic concurrency control.
- **Time travel**: `df = spark.read.format("delta").option("versionAsOf", 5).load(path)` or `timestampAsOf`.
- **Schema enforcement** (default) + **schema evolution** (`mergeSchema=true`).
- **MERGE INTO** (upsert) — huge for CDC pipelines.
- **OPTIMIZE** (compact small files) + **Z-ORDER** (multi-dim clustering for skipping).
- **VACUUM** removes old files past retention (default 7 days).
- **Change Data Feed (CDF)** — track row-level changes.

```python
from delta.tables import DeltaTable

# Upsert
delta_tbl = DeltaTable.forPath(spark, "path")
(delta_tbl.alias("t")
  .merge(updates.alias("s"), "t.id = s.id")
  .whenMatchedUpdateAll()
  .whenNotMatchedInsertAll()
  .execute())

# Time travel
spark.read.format("delta").option("versionAsOf", 3).load("path")
```

**Lakehouse concept:** Delta/Iceberg/Hudi = "lakehouse" = data lake storage + warehouse-like guarantees.

## 1.9 Kafka (high-frequency MCQ topic)

```
Producer → [Topic with Partitions] → Consumer Group(s)
```

**Core concepts:**
- **Topic**: logical stream, split into **partitions**.
- **Partition**: ordered, immutable log. Ordering guaranteed only WITHIN a partition.
- **Offset**: position in partition. Consumer commits offsets.
- **Consumer Group**: each partition consumed by exactly one consumer in the group. Parallelism = #partitions.
- **Replication factor**: copies of each partition across brokers. RF=3 typical.
- **ISR (In-Sync Replicas)**: replicas caught up to leader.
- **Retention**: time-based (default 7d) or size-based.

**Delivery semantics:**
- **At-most-once**: commit offset before processing → may lose.
- **At-least-once**: process then commit → may duplicate (default).
- **Exactly-once**: idempotent producer + transactional API (`enable.idempotence=true`, transactions).

**Key tuning knobs:**
- Producer: `acks=all` (durability), `linger.ms`, `batch.size`, `compression.type`.
- Consumer: `max.poll.records`, `fetch.min.bytes`, `auto.offset.reset` (earliest/latest).

**Schema Registry** (Confluent) — Avro/Protobuf/JSON schemas with evolution rules (BACKWARD, FORWARD, FULL).

## 1.10 Hadoop / HDFS

- **HDFS**: distributed FS, default block size **128 MB** (older: 64 MB).
- **NameNode**: metadata (single point — HA via standby NN + ZooKeeper).
- **DataNode**: stores blocks. Default replication factor **3**.
- **YARN**: resource manager (ResourceManager + NodeManager).
- **MapReduce**: legacy compute; mostly replaced by Spark.
- **Rack awareness**: replicas placed across racks for fault tolerance.

## 1.11 Flink vs Spark (JD mentions Flink)

| | Spark Streaming (Structured) | Flink |
|---|---|---|
| Model | micro-batch (true streaming since 3.0 Continuous) | true streaming (event-by-event) |
| Latency | ~100ms+ | <100ms |
| State mgmt | checkpointing | rocksDB-backed, snapshots |
| Event time / watermarks | yes | yes (more mature) |
| Exactly-once | yes | yes |

**Quick rule:** Flink for ultra-low-latency stream-first; Spark for unified batch + streaming.

## 1.12 NoSQL Quick Reference

| Type | Examples | Use case |
|---|---|---|
| Key-Value | Redis, DynamoDB | cache, session |
| Document | MongoDB, Couchbase | flexible schema, JSON |
| Wide-column | Cassandra, HBase, ScyllaDB | high write throughput, time series |
| Graph | Neo4j, JanusGraph | relationships |
| Vector | Pinecone, Weaviate, Milvus, FAISS, Oracle 23ai | semantic search / RAG |

**CAP theorem**: pick 2 of Consistency, Availability, Partition tolerance. In practice P is mandatory → CP vs AP.
- CP: HBase, MongoDB (default), Zookeeper
- AP: Cassandra, DynamoDB, Couchbase

## 1.13 Practice — write these from memory

1. Read a Parquet folder, filter rows where `country='IN'`, compute avg `revenue` per `state`, sorted desc.
2. Window: top 3 highest-paid employees per department.
3. Upsert (merge) into a Delta table by `id`.
4. Handle a skewed join where 80% of rows have `customer_id=42`.
5. Convert Kafka stream → parse JSON → aggregate 5-min tumbling window → write to Delta.

(Solutions appear at the end of this guide.)

---

# PART 2 — LLMs, RAG, Vector DBs, Agents (2 hours)

## 2.1 LLM Fundamentals

- **Transformer**: encoder-decoder architecture; decoder-only (GPT, Claude, Llama) dominates generative.
- **Tokenization**: BPE (GPT), SentencePiece, WordPiece. 1 token ≈ 4 chars / 0.75 words English.
- **Context window**: max tokens in/out combined (e.g. 128K, 200K, 1M).
- **Parameters vs context**: parameters = model size (7B, 70B); context = working memory per call.
- **Temperature**: 0 = deterministic (greedy), >0 = sampling. Top-p (nucleus) = sample from smallest set with cum prob ≥ p.
- **Inference cost**: scales with input + output tokens. Output is usually 3-5x more expensive than input.

**Training stages:**
1. **Pre-training**: next-token prediction on web-scale corpus.
2. **SFT (Supervised Fine-Tuning)**: instruction-following examples.
3. **RLHF / DPO / Constitutional AI**: align to human preferences.
4. **Fine-tuning**: domain adaptation. **LoRA / QLoRA**: parameter-efficient fine-tuning (PEFT) — train low-rank adapters instead of full weights.

**Quantization:** reduce precision to lower memory.
- FP32 → FP16 / BF16 → INT8 → INT4
- **GPTQ, AWQ, GGUF**: common quantization formats.

## 2.2 RAG (Retrieval-Augmented Generation) — high-yield

```
User Query
   ↓
[Embed query]  → vector
   ↓
[Vector DB similarity search] → top-k chunks
   ↓
[Optional: re-rank with cross-encoder]
   ↓
[Build prompt: system + context + query] → LLM
   ↓
Response (often with citations)
```

**Pipeline stages:**
1. **Ingestion**: load docs (PDF, HTML, etc.) → parse → clean.
2. **Chunking**: split text. Strategies:
   - Fixed size (e.g. 512 tokens, 50 token overlap).
   - Recursive character splitter (respects paragraphs/sentences).
   - Semantic chunking (split on embedding distance).
   - Document structure (markdown headers, sections).
3. **Embedding**: convert chunks → vectors via embedding model (OpenAI `text-embedding-3-large`, Cohere, BGE, E5, Voyage).
4. **Indexing**: store in vector DB with metadata.
5. **Retrieval**: embed query → ANN search.
6. **Re-ranking** (optional but high-impact): cross-encoder reranks top-k retrieved.
7. **Generation**: stuff into prompt with context.

**Advanced RAG patterns:**
- **Hybrid search**: combine dense (vector) + sparse (BM25/keyword). Often 20-30% better recall.
- **Query expansion / HyDE**: generate hypothetical answer first, embed THAT.
- **Multi-query**: LLM generates 3-5 query variants, retrieve all, dedup.
- **Parent-document retrieval**: embed small chunks, return larger context.
- **Self-query**: LLM extracts metadata filters from natural language query.
- **GraphRAG**: build knowledge graph from corpus, traverse it.

**Common pitfalls (MCQ traps):**
- Chunks too small → loss of context. Too large → dilution and exceeding context window.
- Embedding model mismatch between indexing and query time.
- No re-ranking → top results are merely similar, not relevant.
- Forgetting to filter on metadata (e.g. permissions, freshness).

## 2.3 Vector Databases & Similarity Search

**Distance metrics:**
- **Cosine similarity**: angle between vectors. Range [-1, 1]. Most common for text.
- **Dot product**: faster than cosine; equivalent if vectors are L2-normalized.
- **Euclidean (L2)**: straight-line distance. Sensitive to magnitude.

**ANN (Approximate Nearest Neighbor) algorithms:**
- **HNSW** (Hierarchical Navigable Small Worlds): graph-based, fast, memory-heavy. Dominant.
- **IVF** (Inverted File Index): cluster vectors, search within nearest clusters.
- **IVF-PQ** (Product Quantization): compress vectors for memory savings.
- **LSH** (Locality-Sensitive Hashing): older, less common.

| Vector DB | Notes |
|---|---|
| **FAISS** | Meta's library, in-process, no server. CPU/GPU. Great for prototypes. |
| **Pinecone** | Managed SaaS, serverless, easy. |
| **Weaviate** | Open-source, GraphQL API, built-in modules. |
| **Milvus / Zilliz** | Open-source, scalable. |
| **Qdrant** | Rust-based, fast, simple. |
| **Chroma** | Lightweight, dev-friendly. |
| **pgvector** | Postgres extension. |
| **Oracle 23ai** | Oracle DB native vector search (AI Vector Search feature). VECTOR datatype, VECTOR_DISTANCE() functions. **This is the Oracle play — likely on the test.** |

## 2.4 Oracle AI Vector Search (Oracle 23ai)

```sql
-- Oracle 23ai syntax (memorize this)
CREATE TABLE docs (
    id NUMBER,
    content CLOB,
    embedding VECTOR(1024, FLOAT32)
);

-- Insert
INSERT INTO docs VALUES (1, 'hello', VECTOR('[0.1, 0.2, ...]'));

-- Query (KNN search)
SELECT id, content
FROM docs
ORDER BY VECTOR_DISTANCE(embedding, :query_vec, COSINE)
FETCH FIRST 5 ROWS ONLY;

-- Index
CREATE VECTOR INDEX docs_idx ON docs(embedding)
  ORGANIZATION INMEMORY NEIGHBOR GRAPH
  DISTANCE COSINE
  WITH TARGET ACCURACY 95;
```

**Distance functions in 23ai:** `COSINE`, `EUCLIDEAN`, `DOT`, `MANHATTAN`, `HAMMING`.
**Index types:** **HNSW** (in-memory neighbor graph) and **IVF** (neighbor partitions, on-disk).

## 2.5 Agents & Agentic Frameworks

**Agent = LLM + tools + memory + planning loop.**

```
User goal
   ↓
[LLM plans] → which tool? what args?
   ↓
[Execute tool] → result
   ↓
[LLM observes] → done? or next step?
   ↓ (loop)
Final answer
```

**Patterns:**
- **ReAct** (Reason + Act): LLM alternates "Thought / Action / Observation" steps.
- **Plan-and-Execute**: separate planner LLM creates full plan; executor runs steps.
- **Reflexion**: agent critiques its own output and retries.
- **Multi-agent**: specialized agents collaborate (e.g. CrewAI roles).

**Frameworks:**
- **LangChain**: chains, agents, tools, memory, retrievers. Largest ecosystem.
- **LangGraph**: stateful, cyclic graphs (LangChain's modern agent framework).
- **LlamaIndex**: RAG-first, strong on data ingestion.
- **CrewAI**: role-based multi-agent collaboration.
- **Semantic Kernel**: Microsoft's, plugin-based, C#/Python.
- **AutoGen**: Microsoft, multi-agent conversation patterns.
- **Haystack**: deepset, pipelines for QA/RAG.

## 2.6 MCP (Model Context Protocol)

**Critical: this is in the JD and is Anthropic-led standard now adopted broadly (including OpenAI).**

- **What it is**: open protocol for connecting LLMs to external tools/data sources via standardized **servers**.
- **Architecture**: Host (e.g. Claude Desktop, IDE) ↔ Client ↔ MCP Server (exposes tools/resources/prompts).
- **Primitives**:
  - **Tools**: functions the LLM can call (POST-like, side effects OK).
  - **Resources**: data the LLM can read (GET-like, read-only).
  - **Prompts**: pre-baked prompt templates.
- **Transport**: stdio (local) or HTTP+SSE (remote).
- **Why it matters**: replaces ad-hoc tool integrations with one protocol. Like LSP for code editors but for AI.

## 2.7 Function Calling / Tool Use

```python
tools = [{
    "name": "get_weather",
    "description": "Get current weather",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {"type": "string"},
            "unit": {"type": "string", "enum": ["C", "F"]}
        },
        "required": ["location"]
    }
}]
# LLM returns structured tool_use; your code executes; loop back with tool_result.
```

**Key concept:** the LLM doesn't execute the tool — it returns a structured request, YOU execute, then feed result back.

## 2.8 Prompt Engineering Basics

- **System prompt**: role, rules, output format.
- **Few-shot**: 1–5 examples in prompt.
- **Chain-of-Thought (CoT)**: "Think step by step."
- **Self-consistency**: sample multiple CoT, majority vote.
- **Structured output**: JSON mode, tool-use, or grammar-constrained decoding (Outlines, Instructor).

---

# PART 3 — MLOps, PyTorch, Feature Engineering (1.5 hours)

## 3.1 MLOps Lifecycle

```
Data → Feature Eng → Train → Validate → Register → Deploy → Monitor → Retrain
        (Feature Store)    (Model Registry)   (Serving)  (Drift detection)
```

**Key components:**
- **Feature Store**: Feast, Tecton, Databricks. Online (low-latency lookup) + offline (training) consistency.
- **Model Registry**: MLflow, Vertex AI, SageMaker. Versioning + lineage + stage (Staging/Prod/Archived).
- **Experiment Tracking**: MLflow, Weights & Biases, Comet.
- **Orchestration**: Airflow, Kubeflow, Prefect, Dagster.
- **Serving**: TorchServe, Triton, BentoML, FastAPI, Ray Serve, KServe.
- **Monitoring**: drift (data + concept), latency, accuracy, fairness.

**Drift types:**
- **Data drift**: input distribution changes (KS test, PSI score).
- **Concept drift**: P(y|X) relationship changes (need labels).
- **Label drift**: P(y) changes.

**CI/CD for ML (CI/CD/CT):**
- **CI**: code + data + model tests.
- **CD**: deploy pipeline (not just model).
- **CT (Continuous Training)**: automated retraining on triggers.

**Deployment patterns:**
- **Shadow**: prod traffic to new model, don't serve responses, compare.
- **Canary**: small % of traffic to new model.
- **Blue-Green**: switch all at once with rollback.
- **A/B test**: split traffic, measure business metric.
- **Multi-arm bandit**: dynamic allocation by performance.

## 3.2 PyTorch Essentials

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset

# Tensors
x = torch.tensor([[1., 2.], [3., 4.]])
x.shape           # torch.Size([2, 2])
x.to("cuda")      # GPU
x.requires_grad_(True)

# Custom dataset
class MyDataset(Dataset):
    def __init__(self, X, y):
        self.X, self.y = X, y
    def __len__(self):
        return len(self.X)
    def __getitem__(self, i):
        return self.X[i], self.y[i]

loader = DataLoader(MyDataset(X, y), batch_size=32, shuffle=True, num_workers=4)

# Model
class MLP(nn.Module):
    def __init__(self, d_in, d_hidden, d_out):
        super().__init__()
        self.fc1 = nn.Linear(d_in, d_hidden)
        self.fc2 = nn.Linear(d_hidden, d_out)
        self.dropout = nn.Dropout(0.2)
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        return self.fc2(x)

model = MLP(784, 256, 10).to("cuda")
opt = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)
loss_fn = nn.CrossEntropyLoss()

# Training loop
for epoch in range(epochs):
    model.train()
    for xb, yb in loader:
        xb, yb = xb.to("cuda"), yb.to("cuda")
        opt.zero_grad()
        out = model(xb)
        loss = loss_fn(out, yb)
        loss.backward()
        opt.step()

    model.eval()
    with torch.no_grad():
        # validation
        pass

# Save / load
torch.save(model.state_dict(), "m.pt")
model.load_state_dict(torch.load("m.pt"))
```

**MCQ traps:**
- `model.train()` vs `model.eval()`: matters for Dropout & BatchNorm behavior.
- `torch.no_grad()` disables autograd → faster eval, no memory for grad.
- Must `opt.zero_grad()` before each `backward()` (or grads accumulate).
- `nn.CrossEntropyLoss` expects raw logits (it has softmax inside). Do NOT apply softmax first.
- DataLoader `num_workers > 0` uses multiprocessing → speeds up I/O bound loading.

**Distributed training:**
- **DataParallel (DP)**: single process, multi-GPU. Old, slow.
- **DistributedDataParallel (DDP)**: multi-process, recommended. Each GPU gets own process.
- **FSDP (Fully Sharded Data Parallel)**: shards model params/grads/optimizer state across GPUs — for huge models.
- **ZeRO** (DeepSpeed): similar to FSDP, stages 1/2/3.

## 3.3 Feature Engineering Highlights

- **Encoding**: one-hot, label, target/mean encoding (watch for leakage), embeddings, hash.
- **Scaling**: StandardScaler (Z-score), MinMaxScaler, RobustScaler (median/IQR — outlier-safe).
- **Missing values**: drop, impute (mean/median/mode), forward-fill (time series), model-based.
- **Outliers**: IQR rule (1.5×IQR), Z-score (>3), isolation forest.
- **Time series**: lag features, rolling stats, EWMA, seasonality decomposition.
- **Text**: TF-IDF, n-grams, embeddings.
- **Imbalance**: SMOTE (oversample minority), class weights, focal loss, undersampling.
- **Leakage**: target encoding without proper CV, future info in training set.

## 3.4 Model Eval Quick Reference

**Classification:**
- Accuracy = (TP+TN)/total. Bad for imbalanced data.
- Precision = TP/(TP+FP) — when FP is costly.
- Recall (Sensitivity) = TP/(TP+FN) — when FN is costly (cancer, fraud).
- F1 = 2PR/(P+R).
- ROC-AUC: across thresholds. PR-AUC: better for imbalance.

**Regression:** MAE, MSE, RMSE, MAPE, R².

**Cross-validation:** K-fold (default), Stratified K-fold (preserve class ratio), TimeSeriesSplit (no future leakage), GroupKFold.


---

# PART 4 — Python & DSA for HackerRank (1.5 hours)

## 4.1 Patterns you must be fluent with

**Two pointers** — sorted array / linked list problems.
**Sliding window** — substring/subarray with constraint.
**Hash map counting** — anagrams, frequency.
**Heap (heapq)** — top-k, scheduling, merge k sorted.
**Stack** — parentheses, monotonic stack, next-greater.
**BFS/DFS** — graph, tree level-order, shortest path on grid.
**Dynamic programming** — 1D (climbing stairs), 2D (LCS, edit distance), knapsack.
**Binary search** — sorted array, "search for answer" (boundary).
**Union-Find** — connected components.
**Trie** — prefix problems.

## 4.2 Python idioms that save time

```python
# Counter for frequency
from collections import Counter, defaultdict, deque, OrderedDict
c = Counter("mississippi")          # {'i':4,'s':4,'p':2,'m':1}
c.most_common(2)                    # [('i',4),('s',4)]

# defaultdict
d = defaultdict(list)
d["a"].append(1)                    # no KeyError

# deque – O(1) both ends
q = deque([1,2,3])
q.appendleft(0); q.popleft(); q.pop()

# heapq (MIN-heap)
import heapq
h = []
heapq.heappush(h, 3); heapq.heappush(h, 1)
heapq.heappop(h)                    # 1
# Max-heap trick: push negatives
# Top-k smallest:
heapq.nsmallest(k, iterable)
heapq.nlargest(k, iterable, key=lambda x: x.score)

# bisect – binary search
import bisect
i = bisect.bisect_left(arr, x)      # insertion point
bisect.insort(arr, x)               # insert maintaining order

# itertools
from itertools import combinations, permutations, product, accumulate, groupby, chain
list(combinations([1,2,3], 2))      # [(1,2),(1,3),(2,3)]
list(accumulate([1,2,3,4]))         # [1,3,6,10]  – prefix sum

# Comprehensions
sq = [x*x for x in range(10) if x%2==0]
mp = {k:v for k,v in pairs}
gn = (x*x for x in range(10))       # generator – lazy

# String tricks
s.split(), s.strip(), s.replace(a,b), s.startswith(p), s.find(p)
"".join(parts)                      # always faster than += in loop
ord('a')                            # 97
chr(97)                             # 'a'

# Sorting
arr.sort(key=lambda x: (-x.score, x.name))  # stable, multi-key
sorted(arr, key=..., reverse=True)

# Functools
from functools import lru_cache, reduce, cache
@cache                              # Python 3.9+ – unbounded memoize
def fib(n): return n if n<2 else fib(n-1)+fib(n-2)
```

## 4.3 Complexity cheat sheet

| Operation | List | Dict/Set | Deque | Heap |
|---|---|---|---|---|
| Access by index | O(1) | — | — | — |
| Append | O(1) amort. | — | O(1) | O(log n) |
| Pop end | O(1) | — | O(1) | O(log n) (root only) |
| Pop front | O(n) | — | O(1) | — |
| `in` | O(n) | O(1) avg | — | O(n) |
| Insert middle | O(n) | — | — | — |

**Recursion limit:** `sys.setrecursionlimit(10**6)` if needed.

## 4.4 Common HackerRank problem templates

**Sliding window — longest substring with K distinct:**
```python
def longest_k_distinct(s, k):
    from collections import defaultdict
    cnt = defaultdict(int); l = ans = 0
    for r, ch in enumerate(s):
        cnt[ch] += 1
        while len(cnt) > k:
            cnt[s[l]] -= 1
            if cnt[s[l]] == 0: del cnt[s[l]]
            l += 1
        ans = max(ans, r - l + 1)
    return ans
```

**Top-K frequent:**
```python
import heapq
from collections import Counter
def top_k(nums, k):
    c = Counter(nums)
    return heapq.nlargest(k, c.keys(), key=c.get)
```

**BFS on grid (shortest path):**
```python
from collections import deque
def shortest(grid, start, end):
    R, C = len(grid), len(grid[0])
    q = deque([(start, 0)])
    seen = {start}
    while q:
        (r,c), d = q.popleft()
        if (r,c) == end: return d
        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr,nc = r+dr, c+dc
            if 0<=nr<R and 0<=nc<C and grid[nr][nc]==0 and (nr,nc) not in seen:
                seen.add((nr,nc))
                q.append(((nr,nc), d+1))
    return -1
```

**LRU cache:**
```python
from collections import OrderedDict
class LRU:
    def __init__(self, cap): self.cap, self.d = cap, OrderedDict()
    def get(self, k):
        if k not in self.d: return -1
        self.d.move_to_end(k); return self.d[k]
    def put(self, k, v):
        if k in self.d: self.d.move_to_end(k)
        self.d[k] = v
        if len(self.d) > self.cap: self.d.popitem(last=False)
```

**Union-Find:**
```python
class UF:
    def __init__(self, n):
        self.p = list(range(n)); self.r = [0]*n
    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]   # path compression
            x = self.p[x]
        return x
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb: return False
        if self.r[ra] < self.r[rb]: ra, rb = rb, ra
        self.p[rb] = ra
        if self.r[ra] == self.r[rb]: self.r[ra] += 1
        return True
```

## 4.5 HackerRank input parsing (don't lose time here)

```python
import sys
input = sys.stdin.readline           # faster for many lines

n = int(input())
arr = list(map(int, input().split()))
mat = [list(map(int, input().split())) for _ in range(n)]

# Read all at once
data = sys.stdin.read().split()
ptr = 0
def nxt():
    global ptr; ptr += 1; return data[ptr-1]
```

## 4.6 Python deep dive (likely MCQs)

- **GIL**: only one thread executes Python bytecode at a time. Threads help for I/O-bound, multiprocessing for CPU-bound.
- **`is` vs `==`**: identity vs equality. `is` for `None` checks only.
- **Mutable default args trap**: `def f(x=[])` shares list across calls → use `None` sentinel.
- **Generators**: `yield` → lazy iteration; memory efficient.
- **Decorators**: `@dec` = `f = dec(f)`. Use `functools.wraps` to preserve metadata.
- **Context managers**: `__enter__` / `__exit__` or `@contextmanager`.
- **Dataclasses**: `@dataclass` auto-generates `__init__`, `__repr__`, `__eq__`.
- **Async**: `async def` + `await` + `asyncio.run()`. Concurrency via event loop, not threads.
- **Typing**: `list[int]` (3.9+), `Optional[X]` = `X | None` (3.10+).


---

# PART 5 — System Design, REST/SSE, Networking (1 hour)

## 5.1 Distributed Systems Concepts (MCQ-heavy)

- **CAP theorem**: under partition, choose Consistency or Availability.
- **PACELC**: extension — if Partition then C/A, Else Latency/Consistency.
- **Consistency models**: strong, sequential, causal, eventual.
- **Idempotency**: same op multiple times = same effect. Critical for retries.
- **Quorum**: R + W > N for strong consistency in replicated systems.
- **Consistent hashing**: minimize key remapping when nodes added/removed. Used in Cassandra, DynamoDB.
- **Bloom filter**: probabilistic set; no false negatives, possible false positives. Used in Cassandra, HBase, Parquet.
- **HLL (HyperLogLog)**: cardinality estimation in tiny memory.
- **Vector clocks / Lamport timestamps**: ordering events in distributed systems.
- **Raft / Paxos**: consensus protocols. Raft is simpler and now more popular (etcd, Consul, CockroachDB).
- **2-phase commit (2PC)**: distributed transactions, blocking.
- **Saga pattern**: long-running distributed transactions via local txns + compensating actions.

## 5.2 REST API Design

- **HTTP verbs**: GET (safe, idempotent), POST (create, not idempotent), PUT (replace, idempotent), PATCH (partial, often idempotent), DELETE (idempotent).
- **Status codes**:
  - 2xx success (200 OK, 201 Created, 204 No Content)
  - 3xx redirect (301 permanent, 302 temp, 304 not modified)
  - 4xx client (400 bad req, 401 unauth, 403 forbidden, 404 not found, 409 conflict, 422 unprocessable, 429 too many)
  - 5xx server (500 internal, 502 bad gateway, 503 unavailable, 504 timeout)
- **Idempotency keys**: header for safe retries on POST.
- **Pagination**: offset (simple, bad for deep), cursor (scalable, recommended).
- **Versioning**: URL `/v1/`, header, or query param.
- **HATEOAS**: hypermedia links in responses (REST purist).
- **Auth**: API key, OAuth 2.0 (auth code, client credentials, PKCE), JWT, mTLS.

## 5.3 SSE vs WebSocket vs Long Polling (JD mentions SSE)

| | SSE | WebSocket | Long Polling |
|---|---|---|---|
| Direction | Server → Client | Bi-directional | Client → Server (pseudo) |
| Protocol | HTTP | ws:// upgrade | HTTP |
| Auto-reconnect | ✅ built-in | ❌ manual | ❌ |
| Binary | text only | ✅ | text |
| Through proxies | ✅ (plain HTTP) | sometimes blocked | ✅ |
| Use case | LLM streaming, notifications, live updates | chat, gaming, collab editing | legacy fallback |

**SSE in FastAPI (likely on test):**
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio, json

app = FastAPI()

async def event_gen():
    for i in range(10):
        yield f"data: {json.dumps({'i': i})}\n\n"
        await asyncio.sleep(0.5)

@app.get("/stream")
async def stream():
    return StreamingResponse(event_gen(), media_type="text/event-stream")
```

Format on the wire: each event is `data: <payload>\n\n` (blank line terminates the event).

## 5.4 Caching

- **Layers**: browser → CDN → reverse proxy (Nginx) → app → DB.
- **Strategies**: cache-aside (lazy), write-through, write-behind, refresh-ahead.
- **Eviction**: LRU, LFU, FIFO, TTL.
- **Invalidation**: TTL, event-based, write-through.
- **Redis** vs **Memcached**: Redis has data structures, persistence, pub/sub, scripting; Memcached is simpler, pure cache.

## 5.5 Networking Essentials

- **OSI 7 layers**: Physical, Data Link, Network (IP), Transport (TCP/UDP), Session, Presentation, Application (HTTP).
- **TCP vs UDP**: TCP reliable, ordered, connection-oriented; UDP unreliable, fast, no connection.
- **HTTP/1.1 → /2 → /3**: H2 multiplexing over single TCP; H3 over QUIC (UDP-based).
- **TLS**: handshake, certs, SNI, mTLS, TLS 1.3 is current.
- **DNS**: A, AAAA (IPv6), CNAME, MX, TXT, NS; TTL.
- **CIDR**: `/24` = 256 addresses; `/16` = 65k.
- **Load balancers**: L4 (TCP, fast) vs L7 (HTTP, content-aware). Algorithms: round-robin, least-conn, IP-hash, weighted.
- **CDN**: edge caching for static + dynamic. Cloudflare, Akamai, OCI CDN, CloudFront.
- **VPC subnets**: public (has IGW route), private (no direct internet, uses NAT).
- **Firewalls / Security Groups**: stateful (track conn); NACLs are stateless.

## 5.6 Containers + K8s (likely MCQs)

- **Docker**: image (layered), container (running instance), Dockerfile.
- **K8s primitives**: Pod (group of containers sharing net+storage), Deployment (rolling updates), Service (stable IP/DNS, types: ClusterIP/NodePort/LoadBalancer), Ingress, ConfigMap, Secret, StatefulSet (stable identity), DaemonSet (one per node), Job/CronJob, HPA (horizontal pod autoscaler).
- **Probes**: liveness (restart if fail), readiness (remove from LB), startup.


---

# PART 6 — Oracle-Specific (30 min) — pure memorization

> The JD heavily references Oracle products. Expect 3-5 MCQs of pure trivia. Skim this section twice.

## 6.1 Oracle Cloud Infrastructure (OCI) — core services

| Layer | OCI service | AWS equivalent (for memory) |
|---|---|---|
| Compute | OCI Compute, Container Instances | EC2 |
| Container orchestration | OKE (Oracle Kubernetes Engine) | EKS |
| Serverless | OCI Functions (Fn) | Lambda |
| Object storage | OCI Object Storage | S3 |
| Block storage | OCI Block Volumes | EBS |
| File storage | OCI File Storage | EFS |
| VCN (network) | Virtual Cloud Network | VPC |
| Load balancer | OCI Load Balancer + NLB | ELB / NLB |
| DNS | OCI DNS | Route 53 |
| IAM | Identity Domains | IAM |
| Monitoring | OCI Monitoring + Logging | CloudWatch |
| Streaming | OCI Streaming (Kafka-compatible) | Kinesis / MSK |
| Queue | OCI Queue | SQS |
| Notifications | OCI Notifications | SNS |
| Data integration | OCI Data Integration | Glue |
| Data catalog | OCI Data Catalog | Glue Catalog |

## 6.2 OCI Data & AI Stack

- **Oracle Autonomous Database** — self-driving Oracle DB (Autonomous Transaction Processing / Autonomous Data Warehouse).
- **Oracle Database 23ai** — converged DB with **AI Vector Search** (vector datatype, HNSW/IVF indexes), JSON, graph, blockchain tables, property graphs.
- **OCI Data Science** — managed Jupyter notebooks, model catalog, model deployment, AutoML, jobs.
- **OCI Generative AI Service** — managed inference for foundation models (Cohere, Meta Llama) + fine-tuning + dedicated AI clusters.
- **OCI Generative AI Agents** — managed RAG service over your data with grounded responses, includes agent orchestration.
- **OCI Data Flow** — managed Spark service (run PySpark jobs serverless).
- **OCI Big Data Service (BDS)** — managed Hadoop cluster (HDFS, Hive, Spark, HBase, Kafka). Replaces on-prem Hadoop.
- **OCI Big Data Appliance (BDA)** — engineered system (hardware + Cloudera-style stack), legacy on-prem play.
- **OCI Data Catalog** — metadata management.
- **OCI Data Integration** — visual ETL.
- **OCI GoldenGate** — CDC + replication.

## 6.3 Oracle AI Data Platform (the JD focus)

Unified platform launched 2024-2025 combining:
- Data lakehouse on OCI Object Storage + Iceberg/Delta.
- Oracle Database 23ai for transactional + vector workloads.
- OCI Data Flow / Spark for processing.
- OCI Generative AI / Agents for AI workloads.
- Apache Iceberg as the open table format choice.

## 6.4 Talking points (likely written/oral round if shortlisted)

- "Bring AI to your data, not data to AI" — Oracle's positioning. Vector search inside the DB avoids ETL to a separate vector store.
- 23ai integrates **vector + relational + JSON + graph** in one engine.
- OCI Gen AI emphasizes **enterprise data security** and **dedicated AI clusters** for predictable performance.
- For FDE role: think customer-facing — design reviews, reference architectures, troubleshooting, SDK/example code.

---

# PART 7 — SQL Quick Refresher (30 min)

## 7.1 Joins (visualize before answering)

```sql
SELECT a.id, a.name, b.amount
FROM customers a
INNER JOIN orders b ON a.id = b.cust_id     -- only matching
LEFT JOIN orders b ON a.id = b.cust_id      -- all left, NULL right if no match
RIGHT JOIN ...
FULL OUTER JOIN ...                          -- all rows from both, NULLs where unmatched
CROSS JOIN ...                               -- Cartesian
;
-- Semi join (Oracle): EXISTS / IN subquery — returns left rows that have match
-- Anti join: NOT EXISTS / NOT IN — left rows with no match
```

## 7.2 Window Functions (very common in MLE/DE tests)

```sql
SELECT
  emp_id, dept, salary,
  ROW_NUMBER()  OVER (PARTITION BY dept ORDER BY salary DESC) AS rn,
  RANK()        OVER (PARTITION BY dept ORDER BY salary DESC) AS rnk,    -- gaps on ties
  DENSE_RANK()  OVER (PARTITION BY dept ORDER BY salary DESC) AS dr,     -- no gaps
  LAG(salary, 1)  OVER (PARTITION BY dept ORDER BY hire_date) AS prev_sal,
  LEAD(salary, 1) OVER (PARTITION BY dept ORDER BY hire_date) AS next_sal,
  SUM(salary)   OVER (PARTITION BY dept ORDER BY hire_date
                      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total,
  AVG(salary)   OVER (PARTITION BY dept
                      ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg_3
FROM employees;
```

**Top-N per group:**
```sql
SELECT *
FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) rn
  FROM emp
) WHERE rn <= 3;
```

## 7.3 CTEs and Recursion

```sql
WITH dept_avg AS (
  SELECT dept, AVG(salary) avg_sal FROM emp GROUP BY dept
)
SELECT e.* FROM emp e
JOIN dept_avg d ON e.dept = d.dept
WHERE e.salary > d.avg_sal;

-- Recursive (hierarchy)
WITH RECURSIVE org AS (
  SELECT id, mgr_id, name, 0 AS lvl FROM emp WHERE mgr_id IS NULL
  UNION ALL
  SELECT e.id, e.mgr_id, e.name, o.lvl + 1
  FROM emp e JOIN org o ON e.mgr_id = o.id
)
SELECT * FROM org;
```

## 7.4 Indexes & Plans

- **B-tree**: default, range + equality.
- **Hash**: equality only.
- **Bitmap** (Oracle): low-cardinality columns, DW workloads.
- **Function-based**: index on `UPPER(name)`.
- **Composite**: order matters (leftmost prefix rule).
- **Covering index**: query satisfied entirely from index.
- **EXPLAIN PLAN / `EXPLAIN`**: read seq vs index scan vs nested loop vs hash join.

## 7.5 Performance pitfalls

- `SELECT *` defeats projection pushdown.
- Functions on indexed columns disable index (use function-based index or rewrite).
- Implicit type conversion can disable index.
- `NOT IN` with NULLs returns no rows — use `NOT EXISTS`.
- `COUNT(*) ` vs `COUNT(col)`: `COUNT(col)` ignores NULLs.


---

# PART 8 — MCQ Cheat Sheet (rapid-fire, memorize these)

## Spark / Big Data

1. **Default shuffle partitions in Spark SQL?** → 200.
2. **Difference between `cache()` and `persist()`?** → `cache()` is shorthand for `persist(MEMORY_AND_DISK)` (DataFrame default).
3. **What triggers a Spark job?** → an **action**, not a transformation.
4. **Narrow transformation example?** → `filter`, `map`, `select` (no shuffle, 1:1 partition).
5. **Wide transformation example?** → `groupBy`, `join`, `distinct` (shuffle).
6. **Catalyst is for?** → query optimization (logical → physical plan).
7. **Tungsten is for?** → execution engine (memory mgmt, codegen).
8. **Broadcast join threshold default?** → 10MB (`spark.sql.autoBroadcastJoinThreshold`).
9. **AQE does what?** → runtime re-optimization: coalesces shuffle partitions, switches join strategy, handles skew.
10. **`repartition` vs `coalesce`?** → repartition shuffles, can up/down; coalesce no shuffle, only down.
11. **HDFS default block size?** → 128 MB.
12. **HDFS default replication?** → 3.
13. **Kafka ordering guarantee?** → Per partition only.
14. **Kafka consumer group rule?** → One partition → one consumer in a group max.
15. **`acks=all` means?** → leader waits for ISR ack, strongest durability.
16. **Parquet is?** → columnar, splittable, with row groups + footer metadata.
17. **Delta `_delta_log` contains?** → JSON commit files + checkpoints.
18. **Delta time travel option?** → `versionAsOf` or `timestampAsOf`.
19. **OPTIMIZE in Delta does?** → compacts small files into larger ones.
20. **Z-ORDER does?** → multi-dim clustering for data skipping.

## LLM / RAG / Agents

21. **Cosine similarity is sensitive to magnitude?** → No (it's angle only).
22. **Dot product == cosine if?** → vectors are L2-normalized.
23. **HNSW is a?** → graph-based ANN algorithm.
24. **IVF is a?** → partition-based ANN (clusters then searches within nearest).
25. **Top-k retrieval followed by re-ranking improves?** → relevance precision (cross-encoder reorders).
26. **LoRA stands for?** → Low-Rank Adaptation (PEFT method).
27. **Temperature = 0 means?** → greedy decoding (deterministic).
28. **Top-p (nucleus) sampling?** → sample from smallest set with cumulative prob ≥ p.
29. **RAG stands for?** → Retrieval-Augmented Generation.
30. **Hybrid search combines?** → dense (vector) + sparse (BM25 keyword).
31. **HyDE technique?** → generate hypothetical answer, embed it for retrieval.
32. **MCP transport options?** → stdio (local), HTTP+SSE (remote).
33. **MCP primitives?** → tools, resources, prompts.
34. **ReAct pattern?** → Thought → Action → Observation loop.
35. **Oracle 23ai vector index types?** → HNSW (in-memory neighbor graph), IVF (neighbor partitions).
36. **Function calling: who runs the function?** → Your code (LLM only returns the request).

## MLOps / ML

37. **Data drift vs concept drift?** → data: P(X) changes; concept: P(y|X) changes.
38. **PSI test used for?** → detecting data drift between distributions.
39. **Shadow deployment?** → traffic to new model but responses not served (compare only).
40. **Canary deployment?** → small % of real traffic to new model.
41. **Feature store solves?** → train/serve consistency + reuse.
42. **Cross-entropy loss in PyTorch expects?** → raw logits (no softmax beforehand).
43. **`model.eval()` affects which layers?** → Dropout (off), BatchNorm (uses running stats).
44. **DDP vs FSDP?** → DDP replicates model per GPU; FSDP shards params/grads/opt-state.
45. **SMOTE used for?** → oversampling minority class in imbalanced data.

## System / Networking

46. **Idempotent HTTP verbs?** → GET, PUT, DELETE, HEAD, OPTIONS (and PATCH usually).
47. **POST is idempotent?** → No (unless you add idempotency key).
48. **TLS 1.3 vs 1.2?** → faster handshake (1-RTT or 0-RTT resumption), removed insecure ciphers.
49. **HTTP/2 main feature?** → multiplexing streams over one connection.
50. **HTTP/3 runs over?** → QUIC (UDP).
51. **SSE direction?** → server → client only.
52. **WebSocket direction?** → bi-directional.
53. **CAP theorem under partition forces choice between?** → Consistency and Availability.
54. **Quorum formula?** → R + W > N for strong consistency.
55. **Bloom filter can have?** → false positives, NOT false negatives.
56. **Consistent hashing minimizes?** → key remapping when nodes change.
57. **2PC drawback?** → blocking; coordinator failure stalls.
58. **Saga pattern uses?** → local transactions + compensating actions.
59. **L4 vs L7 load balancing?** → L4 transport (TCP), L7 application (HTTP content-aware).
60. **K8s readiness probe failing causes?** → pod removed from service endpoints (but not restarted).

## Python

61. **GIL prevents?** → multiple threads executing Python bytecode in parallel.
62. **`is` vs `==`?** → identity vs value equality.
63. **Generator memory advantage?** → lazy, one item at a time.
64. **`@dataclass` provides?** → auto `__init__`, `__repr__`, `__eq__`.
65. **`async/await` runs on?** → event loop (asyncio), cooperative, single-threaded.
66. **`functools.lru_cache(maxsize=None)` ==?** → unbounded memoize == `@cache`.

## SQL

67. **`COUNT(*)` vs `COUNT(col)`?** → `COUNT(col)` skips NULLs.
68. **`RANK` vs `DENSE_RANK`?** → RANK has gaps after ties; DENSE_RANK doesn't.
69. **`NOT IN` with NULL problem?** → returns no rows; use `NOT EXISTS`.
70. **Bitmap index best for?** → low-cardinality, read-heavy (DW).


---

# PART 9 — Mock Test (timed, take this 2 hrs before the real one)

> Set a 60-min timer. Don't peek at answers below until you finish all questions.

## Section A: Coding (35 min)

**Problem 1 — Sessionize event stream (PySpark or Python).**
Given a stream of events `(user_id, timestamp)`, group consecutive events per user into "sessions" where two events belong to the same session if the gap is ≤ 30 minutes. Output one row per session: `(user_id, session_start, session_end, event_count)`. Schema is provided; solve in PySpark.

**Problem 2 — Top-K trending hashtags.**
Given a stream of tweets (list of strings, with hashtags inside), return the top-K trending hashtags by frequency. Ties broken alphabetically. Optimize for memory; assume the input is too large to load fully — use a streaming-friendly approach.

## Section B: SQL (10 min)

Given table `orders(order_id, cust_id, order_date, amount)`, write a query that, **per customer**, finds:
- their 2nd-largest order amount, and
- the date of their largest order.

## Section C: MCQs (15 min, 15 questions)

(Choose best answer.)

1. In Spark, which is NOT a wide transformation?
   a) `groupByKey`  b) `join`  c) `filter`  d) `distinct`

2. Default replication factor of HDFS?
   a) 1   b) 2   c) 3   d) 5

3. Which join strategy is preferred for a 5MB lookup table joined with a 1TB fact table?
   a) Sort-merge   b) Broadcast hash   c) Shuffle hash   d) Cartesian

4. Kafka guarantees ordering:
   a) Globally across a topic   b) Within a partition   c) Across partitions per key   d) Only in compacted topics

5. Cosine similarity equals dot product when:
   a) Vectors are integers   b) Vectors are L2-normalized   c) Vectors are sparse   d) Dimension > 100

6. RAG pipeline benefits most from re-ranking because:
   a) It reduces cost   b) Top-k from ANN is similar but not always relevant   c) It removes hallucinations   d) It expands the context window

7. Which is true about MCP?
   a) Proprietary to OpenAI   b) Replaces vector DBs   c) Open protocol with tools/resources/prompts   d) Only works with stdio transport

8. PyTorch `nn.CrossEntropyLoss` expects:
   a) Probabilities from softmax   b) Raw logits   c) Log-probabilities   d) One-hot labels

9. PSI is used to detect:
   a) Concept drift   b) Data drift   c) Label leakage   d) Overfitting

10. SSE protocol primarily supports:
    a) Bi-directional binary streaming  b) Server-to-client text events over HTTP  c) UDP messaging  d) gRPC streaming

11. Under network partition, CAP theorem forces a tradeoff between:
    a) Latency and Throughput   b) Consistency and Availability   c) Durability and Availability   d) Strong and Weak typing

12. Idempotent HTTP method that creates/replaces a resource:
    a) POST   b) PUT   c) PATCH   d) GET

13. Bloom filter property:
    a) No false positives, possible false negatives
    b) Possible false positives, no false negatives
    c) Both possible   d) Neither possible

14. Best Spark structure for type safety + Catalyst in PySpark:
    a) RDD   b) DataFrame   c) Dataset   d) Pandas DF

15. Oracle 23ai vector index types include:
    a) HNSW and IVF   b) B-tree and Hash   c) Bitmap and HNSW   d) GIN and GiST

---

## Mock Test Answers

**Coding 1 — Sessionize:**
```python
from pyspark.sql import functions as F
from pyspark.sql.window import Window

GAP_MIN = 30
w = Window.partitionBy("user_id").orderBy("ts")

df2 = (df
  .withColumn("prev_ts", F.lag("ts").over(w))
  .withColumn("gap_min", (F.col("ts").cast("long") - F.col("prev_ts").cast("long")) / 60)
  .withColumn("new_session", F.when(F.col("gap_min") > GAP_MIN, 1).otherwise(0))
  # When prev_ts is NULL (first event), gap is NULL → treat as new session
  .withColumn("new_session", F.coalesce(F.col("new_session"), F.lit(1)))
  .withColumn("session_id", F.sum("new_session").over(w))
)

sessions = (df2.groupBy("user_id", "session_id")
  .agg(F.min("ts").alias("session_start"),
       F.max("ts").alias("session_end"),
       F.count("*").alias("event_count")))
```

**Coding 2 — Top-K hashtags (streaming-friendly):**
```python
import re, heapq
from collections import Counter

def top_k_hashtags(tweets_iter, k):
    counter = Counter()
    pat = re.compile(r"#\w+")
    for tweet in tweets_iter:                 # iterator → streaming
        counter.update(pat.findall(tweet.lower()))
    # Heap of (-count, tag) gives count desc, tag asc on ties via negative cmp:
    return heapq.nsmallest(k, counter.items(), key=lambda x: (-x[1], x[0]))
# For massive scale: Count-Min Sketch + heap (approximate top-k in sublinear memory).
```

**SQL:**
```sql
WITH ranked AS (
  SELECT
    cust_id, order_date, amount,
    ROW_NUMBER() OVER (PARTITION BY cust_id ORDER BY amount DESC, order_date DESC) AS rn_desc,
    FIRST_VALUE(order_date) OVER (
      PARTITION BY cust_id ORDER BY amount DESC, order_date DESC
      ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS top_order_date
  FROM orders
)
SELECT cust_id,
       MAX(CASE WHEN rn_desc = 2 THEN amount END) AS second_largest,
       MAX(top_order_date)                         AS largest_order_date
FROM ranked
GROUP BY cust_id;
```

**MCQ answers:**
1-c, 2-c, 3-b, 4-b, 5-b, 6-b, 7-c, 8-b, 9-b, 10-b, 11-b, 12-b, 13-b, 14-b, 15-a

(Goal: ≥ 12/15 on MCQs and both coding problems compiling and passing basic cases.)

---

# PART 10 — Test-day playbook

## Before the test
- [ ] Quiet room, water, restroom done, 2.5 hrs blocked.
- [ ] Open: this guide, a Python REPL (or local IDE), HackerRank's test interface beforehand to learn navigation.
- [ ] Check: webcam works (if proctored), stable internet, browser supports HR.

## During the test — pacing
1. **First 5 min**: read EVERY question. Mark MCQs you know cold, mark coding for last.
2. **MCQs first** (if mixed): bank the easy points. If you don't know, eliminate 2 wrong answers and guess.
3. **Coding last 60-70 min**:
   - Read problem twice. Restate constraints to yourself.
   - Write the **brute force** first if stuck — partial credit beats nothing.
   - Add 2-3 print debug statements; remove before submit.
   - Always submit SOMETHING — empty solutions get 0.
4. **Last 5 min**: review marked questions, sanity-check submissions.

## Common HR gotchas
- Hidden test cases on edge cases: empty input, single element, all duplicates, negative numbers, very large input.
- Reading stdin slowly with `input()` in tight loops — use `sys.stdin`.
- Off-by-one in window/range boundaries.
- Integer vs float division (`/` vs `//`).
- Modifying a list while iterating.

## If a coding problem is Spark-flavored
HackerRank can simulate Spark with PySpark in their environment. If you get one:
- Don't write a `for` loop over rows — use DataFrame ops.
- Use `F.col`, not bare strings, for complex expressions.
- Window function = your friend for "per group" computations.

## Mindset
- Senior screening is about **breadth + judgment**, not deep algorithmic CS.
- If you blank: skip, move on, return later. Don't burn 20 min on one question.

---

# PART 11 — Final 30-min skim list (read this just before logging in)

1. **Narrow vs wide transformations** (Spark) — Section 1.3.
2. **Default shuffle partitions / broadcast threshold / repartition vs coalesce** — Section 1.4–1.5.
3. **Delta features** (ACID, time travel, MERGE, Z-ORDER) — Section 1.8.
4. **Kafka partition/consumer-group rules** — Section 1.9.
5. **HNSW + IVF + cosine/L2/dot** — Section 2.3.
6. **RAG pipeline stages + re-ranking** — Section 2.2.
7. **Oracle 23ai vector syntax** — Section 2.4.
8. **MCP primitives (tools/resources/prompts)** — Section 2.6.
9. **CAP, idempotency, quorum, Bloom filter** — Section 5.1.
10. **SSE format and FastAPI snippet** — Section 5.3.
11. **REST status codes + idempotent verbs** — Section 5.2.
12. **PyTorch training loop quirks** — Section 3.2.
13. **Drift types + deployment patterns** — Section 3.1.
14. **Window functions: RANK vs DENSE_RANK vs ROW_NUMBER** — Section 7.2.
15. **MCQ cheat sheet** — Part 8 (read all 70).

You've got this. Be honest about what you don't know, demonstrate strong fundamentals, and write clean code.

---

# PART 12 — REAL Candidate-Reported Test Patterns & Questions

> Compiled from public reports on Medium, Blind, Glassdoor, LeetCode discuss, GeeksforGeeks, Reddit, and Scribd. These are **patterns from actual Oracle HackerRank screening tests** (including PMTS-level and AI/ML team variants).

## 12.1 Format patterns across recent Oracle HR screenings

What candidates report, in rough order of frequency for 2024-2026:

| Variant | Coding | MCQs | SQL | Duration | Source signal |
|---|---|---|---|---|---|
| Standard SDE OA | 1-2 medium | 15-30 MCQ (OS/DBMS/CN/OOP) | sometimes 1 | 90-140 min | most common |
| AI/ML team OA | 1 medium | 10 MCQ (ML/LLM/Prompt/Aptitude) | — | 60-90 min | OAL/AI roles |
| Oracle Health screening (live) | 1-2 LC medium | — | — | 45 min coding + 15 min behavioral | Blind reports |
| PMTS-level screen (live) | 1-2 (1 med + 1 med-hard) | — | — | 60 min | LeetCode discuss |
| HackerRank-style format observed | 1 coding + 35 MCQ | as above | maybe | 100 min, 30-min login window | Scribd, GFG |

**Key signal for *your* role (FDE / AI Data Platform PMTS):** Given the JD blends data engineering + LLM + cloud, expect a hybrid: 1 coding problem (Python or PySpark, possibly SQL) + MCQs spanning Spark/distributed systems + LLM/RAG fundamentals + OCI services + OOP/networking.

## 12.2 Real coding problems reported by Oracle candidates

These are paraphrased so they're general patterns — practice solving them in 25 min each.

### Q1. "Interesting Substrings" (Oracle OA, 2024–25)
Given a `mapping` string of length 26 ('0'/'1' for each letter), a string `s`, and integer `k`, find the length of the largest substring of `s` such that the number of characters whose `mapping` value is `1` is **exactly** `k`.

```python
def interesting_substrings(mapping, s, k):
    # Sliding window: count "interesting" chars (mapping=='1') in window
    n = len(s)
    l = 0
    interesting = 0
    best = 0
    for r in range(n):
        if mapping[ord(s[r]) - ord('a')] == '1':
            interesting += 1
        while interesting > k:
            if mapping[ord(s[l]) - ord('a')] == '1':
                interesting -= 1
            l += 1
        if interesting == k:
            best = max(best, r - l + 1)
    return best
```

### Q2. "Top-K stocks in last T minutes" (Oracle OCI pre-screen)
Stream of `(stock_name, price, time)`. Implement a function `top_k(K, T)` returning top-K most expensive stocks seen in the last `T` minutes. **If the same stock appears multiple times, use the latest price.**

```python
from collections import OrderedDict
import heapq, time

class StockStream:
    def __init__(self):
        # name -> (price, ts), keep latest only
        self.latest = {}
        # could also use sortedcontainers for efficient time-window pruning

    def add(self, name, price, ts):
        self.latest[name] = (price, ts)

    def top_k(self, K, T, now):
        cutoff = now - T * 60
        # Only consider stocks within window
        active = [(p, n) for n, (p, ts) in self.latest.items() if ts >= cutoff]
        # nlargest is heap-based, O(N log K)
        top = heapq.nlargest(K, active)
        return [(n, p) for p, n in top]
```

Edge case: latest price could be outside window → that stock disappears. Practice with a more efficient deque-based sliding window if asked to optimize.

### Q3. "Lucky Numbers in a Matrix" (Oracle on-campus 2023, also LC #1380)
Given an `m × n` matrix of unique numbers, return all "lucky numbers" — the minimum in their row AND maximum in their column.

```python
def lucky_numbers(matrix):
    row_min = {min(row) for row in matrix}
    col_max = {max(col) for col in zip(*matrix)}
    return list(row_min & col_max)
```

### Q4. "Search Suggestions System" (Oracle 2022, also LC #1268)
Given `products` and a `searchWord`, for each prefix of `searchWord`, return up to 3 lexicographically smallest products that start with that prefix.

```python
def suggestedProducts(products, searchWord):
    products.sort()
    res = []
    for i in range(1, len(searchWord) + 1):
        prefix = searchWord[:i]
        matches = [p for p in products if p.startswith(prefix)][:3]
        res.append(matches)
    return res
# Optimization for larger inputs: binary search (bisect) or Trie.
```

### Q5. "Calendar Free Slots" (Oracle 2022)
Two people's busy schedules as lists of `[start, end]`; find common free slots ≥ `duration`.

```python
def common_free_slots(busy1, busy2, day_start, day_end, duration):
    # Merge all busy intervals
    busy = sorted(busy1 + busy2)
    merged = []
    for s, e in busy:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    # Find gaps ≥ duration between day_start and day_end
    free = []
    prev = day_start
    for s, e in merged:
        if s - prev >= duration:
            free.append((prev, s))
        prev = max(prev, e)
    if day_end - prev >= duration:
        free.append((prev, day_end))
    return free
```

### Q6. "Max Sum Path in Tree" (Oracle 2024, also LC #124 variant)
Given a tree (parent–child edges) with values per node, return the max path sum where path can start/end anywhere.

```python
def max_path_sum(adj, values, root=0):
    best = [-float('inf')]
    def dfs(u, parent):
        # Best single-arm extensions through u
        best_arm1, best_arm2 = 0, 0
        for v in adj[u]:
            if v == parent: continue
            arm = max(dfs(v, u), 0)
            if arm > best_arm1:
                best_arm2 = best_arm1
                best_arm1 = arm
            elif arm > best_arm2:
                best_arm2 = arm
        # Path passing through u
        through = values[u] + best_arm1 + best_arm2
        best[0] = max(best[0], through)
        return values[u] + best_arm1
    dfs(root, -1)
    return best[0]
```

### Q7. "Sort: primes, then evens, then odds" (Oracle 2023)
Sort ascending within each group.

```python
def sieve(n):
    is_p = [True] * (n + 1); is_p[0] = is_p[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, n+1, i): is_p[j] = False
    return is_p

def custom_sort(arr):
    if not arr: return []
    is_p = sieve(max(arr))
    primes, evens, odds = [], [], []
    for x in arr:
        if x >= 0 and is_p[x]: primes.append(x)
        elif x % 2 == 0: evens.append(x)
        else: odds.append(x)
    return sorted(primes) + sorted(evens) + sorted(odds)
```

### Q8. "Max sum non-adjacent" (Oracle OCI SDE-2, LC #198 House Robber)
```python
def rob(nums):
    prev2, prev1 = 0, 0
    for x in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + x)
    return prev1
```

### Q9. "Sort Linked List" (Oracle multiple reports — they want merge sort, O(n log n), not bubble)
```python
def sort_list(head):
    if not head or not head.next: return head
    # Split in middle (slow/fast)
    slow, fast = head, head.next
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    mid = slow.next; slow.next = None
    left = sort_list(head); right = sort_list(mid)
    # Merge
    dummy = tail = ListNode(0)
    while left and right:
        if left.val <= right.val:
            tail.next, left = left, left.next
        else:
            tail.next, right = right, right.next
        tail = tail.next
    tail.next = left or right
    return dummy.next
```

### Q10. PySpark — "Sessionize clickstream by 30-min inactivity" (commonly asked at PMTS/SMTS DE roles)
Already covered in mock test, but real candidates report this exact pattern. Two variants:
- "Find the relevant user session for each click event" (label rows with session_id)
- "Aggregate per session" (one row per session)

## 12.3 Real MCQ topics reported (Oracle screenings)

These came up repeatedly:

- **B-tree**: count of keys with given order and height
- **Topological sort**: count of valid orderings for a DAG
- **BFS/DFS**: traversal output
- **Inversions**: count in array (merge sort approach)
- **MST**: Prim's vs Kruskal's
- **Tree traversals**: preorder/inorder/postorder reconstruction
- **OOP**: virtual functions, polymorphism types, abstract class vs interface
- **DBMS**: ACID, normal forms (1NF/2NF/3NF/BCNF), indexes, transactions, isolation levels (READ UNCOMMITTED → READ COMMITTED → REPEATABLE READ → SERIALIZABLE)
- **OS**: scheduling algorithms (FCFS, SJF, Round Robin), deadlock conditions (mutual exclusion, hold-and-wait, no preemption, circular wait), paging vs segmentation
- **Networking**: OSI layers, TCP handshake (SYN, SYN-ACK, ACK), DNS, HTTP status codes, subnet masks
- **HTTP error codes**: 200, 201, 301, 304, 400, 401, 403, 404, 409, 422, 429, 500, 502, 503, 504
- **Java specifics** (if Java team): inheritance, exception hierarchy, final/finally/finalize, collections (ArrayList vs LinkedList vs HashMap)
- **String immutability**, serialization, synchronization
- **Connection pooling**

## 12.4 OCI Generative AI MCQ Bank (HIGH-YIELD — Source: Oracle Cert 1Z0-1127)

> The official OCI Gen AI Professional certification practice questions are an almost-exact preview of what the AI portion of this screening will test. Memorize these answers. (`★` = correct.)

**1. What is the role of temperature in LLM decoding?**
- ★ To adjust the sharpness of the probability distribution when selecting the next word

**2. Greedy decoding entails?**
- ★ Choosing the word with the highest probability at each step

**3. What does increasing temperature do?**
- ★ Flattens the distribution, allowing more varied word choices

**4. Fine-tuning vs PEFT — which is true?**
- ★ Fine-tuning trains entire model (expensive); PEFT updates only a small subset of params (cheap)

**5. Soft prompting is appropriate when?**
- ★ You need to add learnable parameters to an LLM without task-specific training

**6. T-Few fine-tuning characteristic?**
- ★ Selectively updates only a fraction of the model's weights (reduces compute + prevents overfitting)

**7. When is fine-tuning appropriate?**
- ★ When the LLM doesn't perform well on a task AND the data is too large for prompt engineering

**8. Cosine distance of 0 indicates?**
- ★ Vectors are similar in direction (cos similarity = 1, so distance = 1 - cos = 0)

**9. Dot product vs cosine similarity?**
- ★ Cosine = angle/direction only; dot product = direction + magnitude. They are equal when vectors are L2-normalized.

**10. Why normalize vectors in a vector DB?**
- ★ To support cosine similarity calculation by having all vectors of the same length

**11. Embeddings in LLMs represent?**
- ★ Semantic content of data in high-dimensional vectors

**12. What does semantic search differ from keyword search by?**
- ★ It involves understanding the intent and context of the search

**13. Indexing in vector DBs is for?**
- ★ Mapping vectors to a data structure for faster search / efficient retrieval

**14. Structure of vector DBs vs relational?**
- ★ Based on distances and similarities in a vector space (not tabular)

**15. Accuracy in vector DBs preserves which type of relationship important for LLMs?**
- ★ Semantic relationships — crucial for context and precise generation

**16. Purpose of RAG?**
- ★ To generate text using extra information from an external data source

**17. RAG Sequence model behavior?**
- ★ For each input query, retrieves a set of relevant documents and considers them TOGETHER to generate a cohesive response

**18. RAG-Sequence vs RAG-Token?**
- ★ Sequence uses the same retrieved doc for the entire output sequence; Token can use different snippets per generated token

**19. Groundedness vs Answer Relevance in RAG?**
- ★ Groundedness = factual correctness (no hallucination); Answer Relevance = relevance to the user's query

**20. What does "hallucination" mean for LLMs?**
- ★ The model generates factually incorrect / unrelated content as if it were true

**21. LLMs WITHOUT RAG rely on what?**
- ★ Internal knowledge learned during pretraining on a large text corpus

**22. Building a chatbot using internal store policies + conversation memory — best choice?**
- ★ Retrieval Augmented Generation (RAG) chatbot

**23. Few-shot prompting main advantage?**
- ★ Provides examples in the prompt to guide the LLM with no training cost

**24. In-context learning involves?**
- ★ Conditioning the model with task-specific instructions or demonstrations

**25. Chain-of-Thought prompting is when?**
- ★ LLM emits intermediate reasoning steps in its response

**26. k-shot prompting?**
- ★ Using exactly k examples in the prompt

**27. Prompt engineering definition?**
- ★ Iteratively refining the ask to elicit a desired response

**28. Best prompt-injection example from a list?**
- ★ Asking the LLM how to bypass its system prompt

**29. Stop sequence "." — what happens?**
- ★ Model stops after the first sentence ends, even if token limit higher

**30. Frequency penalty does?**
- ★ Penalizes tokens that have already appeared, based on how many times they were used

**31. Presence penalty does?**
- ★ Penalizes a token each time it appears after the first occurrence (regardless of count)

**32. LangChain Retrievers purpose?**
- ★ Retrieve relevant information from knowledge bases

**33. LangChain component that generates linguistic output?**
- ★ LLMs

**34. LangChain memory purpose?**
- ★ Store data and provide algorithms for summarizing past interactions

**35. When does a chain interact with memory in LangChain?**
- ★ After user input but before chain execution, AND after core logic but before output

**36. Prompt templates use what syntax?**
- ★ Python's `str.format` syntax

**37. Prompt templates and variables?**
- ★ Support any number of variables, including zero

**38. What is LECL?**
- ★ A declarative way to compose chains via LangChain Expression Language

**39. What is LangChain?**
- ★ A Python library for building applications with LLMs

**40. How are chains traditionally created in LangChain?**
- ★ Using Python classes like `LLMChain` etc.

**41. Ranker in a text-gen system?**
- ★ Evaluates and prioritizes the information retrieved by the Retriever

**42. Generator in a text-gen system?**
- ★ Generates human-like text using retrieved info + user's original query

**43. Loss metric meaning?**
- ★ Indicates how WRONG the model's predictions are (lower = better)

**44. Accuracy in fine-tuning evaluation?**
- ★ How many predictions were correct out of all predictions

**45. Dedicated AI Cluster GPU distinctive feature?**
- ★ The GPUs allocated for a customer's tasks are isolated from other customers' GPUs

**46. OCI fine-tuning training data is stored where, encrypted?**
- ★ Encrypted by default in the user's OCI Object Storage bucket

**47. Fine-tuning dedicated cluster — minimum unit hours for 10 days?**
- ★ 480 (10 days × 24 hr × 2 units)
- Hosting cluster default = 744 unit-hours

**48. OCI Gen AI default fine-tunable model types?**
- ★ Generation, Summarization, Embedding, Chat (NOT translation)

**49. Cohere Embed v3 improvement over v2?**
- ★ Better retrieval for RAG systems

**50. Diffusion models for text — why hard?**
- ★ Text is categorical (discrete tokens), unlike images which are continuous

## 12.5 Big Data / Spark / Distributed Systems MCQs (high probability)

51. **Default Spark shuffle partitions?** → 200
52. **HDFS default block size?** → 128 MB
53. **HDFS default replication factor?** → 3
54. **Kafka ordering guaranteed at what level?** → per partition
55. **Spark transformation is lazy or eager?** → lazy
56. **`cache()` triggers execution?** → no (only actions do)
57. **Catalyst optimizer?** → query optimization (rule + cost based)
58. **Tungsten?** → physical execution engine (memory, codegen)
59. **Broadcast join recommended when one side is?** → small (<~10 MB)
60. **`repartition` vs `coalesce` shuffle?** → repartition shuffles; coalesce minimizes shuffle
61. **Spark stage boundary?** → shuffle
62. **One job = one ?** → action
63. **Sort-merge join requires?** → both sides sorted on join key, shuffled
64. **Delta Lake provides?** → ACID transactions on data lakes via transaction log
65. **OPTIMIZE in Delta?** → compacts small files
66. **Z-ORDER in Delta?** → multi-dim clustering for data skipping
67. **Parquet is?** → columnar, splittable, with row groups
68. **Snappy in Parquet is?** → fast compression codec (default)
69. **`collect()` brings data where?** → to driver (OOM risk)
70. **Skew handling techniques?** → salting, broadcast, AQE skew join, pre-aggregation

## 12.6 OOP / DBMS / OS / Networking Quick MCQs (Oracle classics)

71. **4 OOP pillars?** → encapsulation, inheritance, polymorphism, abstraction
72. **Method overloading is what kind of polymorphism?** → compile-time (static)
73. **Method overriding is what kind?** → runtime (dynamic)
74. **Abstract class vs interface (Java 8+)?** → abstract class can have state + constructors; interface can have default + static methods, no state
75. **Final keyword on class?** → cannot be inherited
76. **Try-finally — does finally run when catch has return?** → yes (unless JVM exits)
77. **ACID stands for?** → Atomicity, Consistency, Isolation, Durability
78. **3NF requires?** → no transitive dependencies (every non-key attribute depends only on the primary key)
79. **BCNF stronger than?** → 3NF
80. **Isolation levels strongest to weakest?** → SERIALIZABLE > REPEATABLE READ > READ COMMITTED > READ UNCOMMITTED
81. **Phantom read prevented at which level?** → SERIALIZABLE
82. **Index on PRIMARY KEY by default?** → clustered (in most RDBMS like SQL Server; Oracle's PK gets a unique index, table organization separate)
83. **B-tree vs Hash index?** → B-tree supports range queries; hash only equality
84. **Deadlock necessary conditions?** → mutual exclusion + hold-and-wait + no preemption + circular wait
85. **TCP 3-way handshake?** → SYN → SYN-ACK → ACK
86. **TCP vs UDP?** → TCP reliable/ordered; UDP fast/unreliable
87. **HTTP 301?** → permanent redirect
88. **HTTP 401 vs 403?** → 401 = unauthenticated; 403 = authenticated but not authorized
89. **HTTP 429?** → too many requests (rate-limited)
90. **DNS A record vs CNAME?** → A maps name → IPv4; CNAME maps name → another name (alias)
91. **OSI layer of TCP?** → Layer 4 (Transport)
92. **OSI layer of HTTP?** → Layer 7 (Application)
93. **Subnet `/24` provides?** → 256 addresses (254 usable)
94. **NAT translates?** → private IPs to public IPs
95. **Load balancer L4 vs L7?** → L4 routes by transport (TCP/UDP); L7 by app content (HTTP path, headers)

## 12.7 Additional PySpark practice problems (with solutions)

### P1. Group with collect_list (asked at multiple Oracle DE screenings)
Input rows like `("a","aa",1)`, group by first two columns and aggregate third into a list.

```python
from pyspark.sql.functions import collect_list
df.groupBy("Col1", "Col2").agg(collect_list("Col3").alias("Col3")).show()
```

### P2. Explode delimited values
Input: `("Alice", "Badminton, Tennis")` → two rows per person.

```python
from pyspark.sql.functions import split, explode, trim
df.withColumn("sport", explode(split("Sport", ","))) \
  .withColumn("sport", trim("sport")) \
  .select("Name", "sport").show()
```

### P3. Highest-paid employee globally (single rank)
```python
from pyspark.sql.window import Window
from pyspark.sql.functions import rank
w = Window.orderBy(df.salary.desc())
df.withColumn("rnk", rank().over(w)).filter("rnk = 1").show()
```

### P4. Count of direct reports per manager
```python
from pyspark.sql.functions import col, count
df.filter(col("ManagerId").isNotNull()) \
  .groupBy("ManagerId") \
  .agg(count("EmpId").alias("reports")) \
  .show()
```

### P5. Start/end day of each week
Given rows with `(year, week_num, date)`, return `(year, week_num, start_day, end_day)`.

```python
from pyspark.sql.functions import to_date, col, min as smin, max as smax
df.withColumn("dates", to_date("dates")) \
  .groupBy("year", "week_num") \
  .agg(smin("dates").alias("start_day_week"),
       smax("dates").alias("end_day_week")) \
  .show()
```

### P6. Orders count by status, side-by-side
Given `(order_id, status, date)`, output `(order_id, total, shipped, delivered)`.

```python
from pyspark.sql.functions import count, when, col
df.groupBy("order_id").agg(
    count("*").alias("total"),
    count(when(col("status")=="Shipped", 1)).alias("shipped"),
    count(when(col("status")=="Delivered", 1)).alias("delivered"),
).show()
```

### P7. Transactions monthly per country (LC #1193 + PySpark variant)
```python
from pyspark.sql.functions import date_format, when, sum as ssum, count
df.withColumn("ym", date_format("trans_date", "yyyy-MM")) \
  .groupBy("ym", "country") \
  .agg(
      count("*").alias("trans_count"),
      ssum("amount").alias("trans_total"),
      count(when(df.state=="approved", 1)).alias("approved_count"),
      ssum(when(df.state=="approved", df.amount).otherwise(0)).alias("approved_total"),
  ).show()
```

### P8. Sessionize with explicit session_id (variant of mock)
```python
from pyspark.sql import functions as F
from pyspark.sql.window import Window

w = Window.partitionBy("user_id").orderBy("click_time")
df = (df
  .withColumn("prev", F.lag("click_time").over(w))
  .withColumn("gap_sec", (F.col("click_time").cast("long") - F.col("prev").cast("long")))
  .withColumn("new_sess", F.when((F.col("gap_sec") > 30*60) | F.col("gap_sec").isNull(), 1).otherwise(0))
  .withColumn("session_id", F.sum("new_sess").over(w))
)
```

## 12.8 Behavioral patterns reported (in case live behavioral follows screening)

If the screening is followed immediately by a 10-15 min behavioral chat (Oracle Health pattern), prepare crisp STAR stories for:
1. A time you had a technical disagreement and how you resolved it
2. A time you mentored / led someone
3. A challenging project and what you learned
4. A time you delivered under ambiguous requirements
5. Why Oracle / why this team
6. A time you had to explain a complex technical concept to a non-technical stakeholder (FDE-specific!)
7. A failure and what you learned

**FDE-specific tip from public reports:** interviewers grade for "diagnose the right client problem before coding" — show that thinking pattern in any open-ended answer.

## 12.9 Things to AVOID in the screening (from candidate post-mortems)

- Don't spend > 25 min on one MCQ-style problem; mark and move on.
- Don't use `printf`/`print` in production solutions — strip them before submitting.
- Don't ignore output format (one candidate reported failing because `"0.00"` came back as `".00"` due to auto-formatting; **explicitly format numeric output**, e.g., `f"{x:.2f}"` in Python).
- Don't use brute force when O(n log n) is clearly expected — but ALWAYS submit something working over nothing.
- Don't switch tabs / open external sites — HackerRank proctoring flags this.
- Don't paste large code blocks from outside; the proctor can detect that.

## 12.10 What's likely on YOUR test (based on JD + reports)

My ranked predictions for what you'll face:

1. **High likelihood**: 1 medium Python coding problem (data manipulation, possibly involving streams/intervals/groups)
2. **High likelihood**: 10–20 MCQs blending: Spark internals, OOP, DBMS/SQL, networking, REST, OCI services
3. **Moderate likelihood**: 5–10 MCQs on LLM/RAG/embeddings (use the OCI Gen AI bank above)
4. **Moderate likelihood**: 1 SQL query (window function or aggregation)
5. **Lower but possible**: 1 PySpark coding problem instead of (or alongside) Python
6. **Lower but possible**: 1 REST API problem (HackerRank's standard REST API question type)
7. **Lower**: Live behavioral chat right after (if Oracle Health–style screening)

Practice problems Q1–Q10 in section 12.2 above plus the PySpark P1–P8 cover the highest-yield coding patterns. The MCQ banks in 12.4–12.6 should give you 80%+ of the trivia coverage.

