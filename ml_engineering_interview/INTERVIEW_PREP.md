# ML Engineering Interview – Preparation Guide

A structured guide covering fundamentals, common challenges, inference/platform topics, and production practices for ML Engineering interviews.

---

## 1. Fundamentals and Core Concepts

### 1.1 Model Serving Lifecycle

**Concept:** A production model goes through: **Train → Validate → Package → Deploy → Serve → Monitor → Update**.

| Phase | What Happens | Key Concerns |
|-------|--------------|--------------|
| **Train** | Experimentation, hyperparameter tuning, feature engineering | Reproducibility, versioning (code, data, config) |
| **Validate** | Offline metrics, A/B test design, shadow traffic | Statistical significance, metric parity with production |
| **Package** | Serialize model (e.g. pickle, ONNX, TorchScript), build container | Format compatibility, size, load time |
| **Deploy** | Roll out to serving cluster (e.g. K8s), traffic routing | Zero-downtime, canary, rollback |
| **Serve** | Handle requests, run inference, return predictions | Latency, throughput, batching, resource use |
| **Monitor** | Logs, metrics, alerts, drift detection | P99 latency, error rate, data/schema drift |
| **Update** | New model versions, rollback, feature flags | Versioning, safe rollout, compatibility |

**Example – minimal serving contract:**

```python
# Contract: every model server must implement predict(input) -> output
from abc import ABC, abstractmethod
from typing import Any

class ModelServer(ABC):
    @abstractmethod
    def load(self, model_uri: str) -> None:
        """Load model from registry or path."""
        pass

    @abstractmethod
    def predict(self, input: Any) -> Any:
        """Single request inference."""
        pass

    @abstractmethod
    def health(self) -> bool:
        """Liveness/readiness for K8s."""
        pass
```

---

### 1.2 Latency, Throughput, and Cost

**Definitions:**

- **Latency:** Time from request received to response sent (e.g. p50, p95, p99).
- **Throughput:** Requests per second (QPS/RPS) the system can handle.
- **Cost:** Compute (CPU/GPU), memory, network, storage per request or per hour.

**Trade-offs:**

- **Batching:** Increases throughput and GPU utilization but adds latency (wait for batch).
- **Replicas:** More pods/nodes → higher throughput and cost; need load balancing.
- **Caching:** Reduces compute and latency for repeated inputs; invalidation and memory cost.

**Example – latency budget:**

```
Total SLA: 100ms p99
├── Network / API gateway:  10ms
├── Preprocessing:          15ms
├── Model inference:        60ms
├── Postprocessing:         10ms
└── Response:                5ms
```

---

### 1.3 Model Versioning and Registry

**Concept:** Every deployable artifact should be uniquely identifiable: **model version = f(code, data, config)**.

- **Why:** Reproducibility, rollback, audit, and safe canary/AB tests.
- **What to version:** Model binary, preprocessing code, feature schema, config (thresholds, feature flags).

**Example – versioning scheme:**

```python
# Semantic versioning for models: major.minor.patch
# major: breaking API/schema change
# minor: retrain same schema, improved metrics
# patch: config/code fix, same weights

def get_model_version(model_uri: str) -> str:
    # e.g. s3://bucket/models/churn-v2.3.1/
    return model_uri.rstrip("/").split("/")[-1]
```

---

### 1.4 Observability for Inference

**Three pillars:**

1. **Metrics:** Request count, latency (p50/p95/p99), error rate, queue depth, batch size.
2. **Logs:** Request IDs, model version, errors, optional sampled payloads (privacy-safe).
3. **Traces:** End-to-end request flow (gateway → preprocess → model → postprocess).

**Example – minimal metrics (Prometheus-style):**

```python
from prometheus_client import Counter, Histogram

INFERENCE_LATENCY = Histogram("inference_latency_seconds", "Inference latency", ["model_version"])
REQUEST_COUNT = Counter("inference_requests_total", "Total requests", ["model_version", "status"])

def predict_with_metrics(model_version: str, input_data: dict):
    with INFERENCE_LATENCY.labels(model_version=model_version).time():
        try:
            out = model.predict(input_data)
            REQUEST_COUNT.labels(model_version=model_version, status="success").inc()
            return out
        except Exception:
            REQUEST_COUNT.labels(model_version=model_version, status="error").inc()
            raise
```

---

### 1.5 Feature Management and Dataset Versioning

**Concept:** Training and serving must use the same feature definitions and compatible data versions.

- **Feature store:** Single source of truth for feature names, types, and (optionally) computed values (batch/real-time).
- **Dataset versioning:** Snapshots of training/validation data (e.g. by date, by version ID) so runs are reproducible.

**Example – dataset versioning (conceptual):**

```python
# Training script records dataset version in MLflow
import mlflow

with mlflow.start_run():
    train_data = load_dataset("s3://bucket/datasets/train/v=20240301/")
    mlflow.log_param("dataset_version", "20240301")
    mlflow.log_param("dataset_path", str(train_data.path))
    # ... train and log model
```

---

### 1.6 Lineage

**Concept:** Track where a model came from (which code, data, config) and where it is used (which endpoints, experiments).

- **Upstream:** Git commit, dataset version, feature list, environment.
- **Downstream:** Deployed endpoints, A/B tests, dashboards.

This enables debugging (“which data produced this model?”) and impact analysis (“if I change this dataset, which models are affected?”).

---

## 2. Common Challenges and Solutions

### 2.1 High Latency / Unpredictable p99

| Cause | Mitigation |
|-------|------------|
| Cold start (model load on first request) | Pre-load at startup; use readiness probe after load; keep minimum replicas warm. |
| Large model / slow inference | Optimize (quantization, pruning, smaller model); use GPU; batch inference where acceptable. |
| No batching / small batches | Implement dynamic batching with a max wait time to balance latency vs throughput. |
| Noisy neighbors / resource contention | Request limits, QoS (CPU/memory), dedicated nodes for latency-sensitive services. |
| Blocking I/O in request path | Async I/O; cache external calls; avoid heavy logging in hot path. |

**Example – simple dynamic batching:**

```python
import threading
import time
from collections import deque

class DynamicBatcher:
    def __init__(self, max_batch_size: int = 32, max_wait_sec: float = 0.05):
        self.max_batch_size = max_batch_size
        self.max_wait_sec = max_wait_sec
        self.queue = deque()
        self.lock = threading.Lock()
        self.cond = threading.Condition(self.lock)

    def submit(self, request_id: str, input_data: dict) -> Any:
        with self.cond:
            self.queue.append((request_id, input_data))
            if len(self.queue) >= self.max_batch_size:
                self.cond.notify_all()
            else:
                self.cond.wait(timeout=self.max_wait_sec)
            batch = list(self.queue)[:self.max_batch_size]
            for _ in batch:
                self.queue.popleft()
        # Run batch inference (actual impl would return result to each request)
        return self._run_batch(batch)
```

---

### 2.2 Model Drift and Data Quality

| Challenge | Solution |
|-----------|----------|
| Input distribution shift | Monitor feature distributions (e.g. PSI); alert on thresholds; retrain or recalibrate. |
| Label drift / concept drift | Track target distribution and performance over time; scheduled retrains; shadow model comparisons. |
| Missing/corrupt features | Validation layer at ingest; default/fallback values; reject or flag bad requests. |
| Schema changes | Versioned schemas; backward-compatible deployments; feature flags for new fields. |

**Example – simple PSI (Population Stability Index):**

```python
import numpy as np

def psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    """PSI > 0.2 often indicates meaningful shift."""
    breakpoints = np.percentile(expected, np.linspace(0, 100, bins + 1)[1:-1])
    def bucketize(arr):
        return np.histogram(arr, bins=np.concatenate(([-np.inf], breakpoints, [np.inf])))[0] / len(arr)
    e, a = bucketize(expected), bucketize(actual)
    e, a = np.clip(e, 1e-6, 1), np.clip(a, 1e-6, 1)
    return np.sum((a - e) * np.log(a / e))
```

---

### 2.3 Safe Rollouts and Rollbacks

| Practice | How |
|----------|-----|
| Canary | Route small % of traffic to new version; compare latency and error rate. |
| Blue-green | Two identical environments; switch traffic at once; instant rollback by switching back. |
| Feature flags | Toggle model version or behavior without redeploying. |
| Rollback | Keep previous model version available; revert route/selector in K8s or config. |

**K8s example – canary with two deployments:**

```yaml
# deployment-v1 (stable): 90% traffic
# deployment-v2 (canary): 10% traffic via separate Service or Istio/Ingress weight
apiVersion: v1
kind: Service
metadata:
  name: model-service
spec:
  selector:
    app: model-api
    version: v1   # default; canary has version: v2
  ports:
    - port: 8000
```

Use a service mesh or ingress to split traffic by weight between `v1` and `v2` services.

---

### 2.4 Cost Efficiency at Scale

| Lever | Approach |
|-------|----------|
| Right-sizing | Profile CPU/memory per replica; set requests/limits in K8s; use HPA/VPA. |
| Scale-to-zero / scale-down | Reduce replicas when traffic is low; use KEDA or similar for queue-based scaling. |
| Spot / preemptible | For batch or delay-tolerant inference; handle preemption gracefully. |
| Caching | Cache identical or similar requests (embedding/model output cache). |
| Model optimization | Quantization, distillation, pruning to reduce compute per request. |

---

### 2.5 Reproducibility (Training)

| Problem | Solution |
|---------|----------|
| Non-determinism | Fixed seeds (numpy, torch, etc.); deterministic ops where possible. |
| Unversioned data | Dataset registry with version tags; log dataset path/version in experiment tracker. |
| Environment drift | Containerized training (Docker); log pip/conda env in MLflow or similar. |
| Code drift | Git tags per run; log commit SHA in experiments. |

---

## 3. Inference Platform Expertise

### 3.1 Scalable, Reliable, Low-Latency Serving

- **Scalable:** Horizontal scaling (more replicas); autoscaling (HPA) on CPU/memory or custom metrics (e.g. queue depth).
- **Reliable:** Health checks (liveness/readiness), retries with backoff, circuit breakers, multi-zone deployment.
- **Low-latency:** Pre-loaded models, batching, optimized runtimes (ONNX, TensorRT), minimal dependencies in hot path.

### 3.2 Model Serving Frameworks (Hands-On)

| Framework | Typical Use | Notes |
|-----------|-------------|--------|
| **TensorFlow Serving** | TF/Keras models | gRPC/REST, batching, version policy (latest, specific). |
| **TorchServe** | PyTorch | Multi-model, versioning, metrics. |
| **Triton Inference Server** | Multi-framework (TF, PyTorch, ONNX) | Dynamic batching, GPU optimization. |
| **KServe (formerly KFServing)** | K8s-native | Standard InferenceService CRD; supports many runtimes. |
| **Seldon Core** | K8s, custom containers | Flexible pipelines (pre/post), A/B tests. |
| **Custom FastAPI/Flask** | Full control | You manage loading, batching, scaling; good for interviews to show clarity. |

**Example – FastAPI model server (conceptual):**

```python
from fastapi import FastAPI
import uvicorn

app = FastAPI()
model = None

@app.on_event("startup")
def load_model():
    global model
    model = load_from_registry(os.environ["MODEL_URI"])

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}

@app.post("/predict")
def predict(request: PredictRequest):
    return model.predict(request.features)
```

### 3.3 K8s Migration and Deployment

- **Migration:** Move from VM/EC2 or single-node deployment to K8s: containerize the serving app, define Deployment, Service, Ingress, ConfigMaps/Secrets, and optionally HPA.
- **JSB (likely “Job” or “Job Submission”):** If the role refers to job scheduling (e.g. training jobs), align with K8s Jobs/CronJobs or a framework like Kubeflow Pipelines; update any existing job runner to submit to K8s API.

**Minimal Deployment + Service:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: model-server
  template:
    metadata:
      labels:
        app: model-server
    spec:
      containers:
        - name: server
          image: myregistry/model-server:latest
          ports:
            - containerPort: 8000
          env:
            - name: MODEL_URI
              valueFrom:
                configMapKeyRef:
                  name: model-config
                  key: model_uri
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "1Gi"
              cpu: "1"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: model-service
spec:
  selector:
    app: model-server
  ports:
    - port: 80
      targetPort: 8000
```

### 3.4 Performance Optimization

- **Inference:** Use ONNX/TensorRT; quantization (INT8/FP16); batch size tuning.
- **Request path:** Avoid sync I/O; cache feature lookups; compress payloads if needed.
- **Infra:** Right-size pods; use node affinity for GPU; tune concurrency (e.g. workers per pod).

### 3.5 Model Versioning and Observability (Recap)

- **Versioning:** Registry (MLflow, S3 + tags); version in image or env (e.g. `MODEL_URI`); expose version in `/health` or headers.
- **Observability:** Metrics (latency, QPS, errors), logs (request id, version), traces; alerts on SLO breaches and drift.

---

## 4. ML Platform and MLOps

### 4.1 Experiment Tracking and Registry (e.g. MLFlow)

- **Experiments:** Log params, metrics, artifacts; compare runs; register models.
- **Model registry:** Named versions (e.g. “churn-prod”); promote to Production/Staging; load by name+version or URI.

**Example – MLflow log and register:**

```python
import mlflow

mlflow.set_tracking_uri("http://mlflow:5000")
mlflow.set_experiment("churn-prediction")

with mlflow.start_run():
    mlflow.log_param("model_type", "RandomForest")
    mlflow.log_param("max_depth", 10)
    mlflow.log_metric("accuracy", 0.92)
    mlflow.log_metric("auc", 0.88)
    mlflow.sklearn.log_model(sk_model, "model", registered_model_name="churn-model")
```

### 4.2 Training Pipelines and Orchestration

- **Pipelines:** DAG of steps: data load → preprocess → train → evaluate → register model (and optionally deploy).
- **Orchestration:** Airflow, Kubeflow Pipelines, Vertex AI Pipelines, or custom (e.g. Step Functions + Lambda).

### 4.3 Feature Management and Dataset Versioning

- **Features:** Central catalog; versioned transforms; same code or config for train and serve.
- **Datasets:** Versioned paths (e.g. `s3://bucket/data/v=20240301/`); logged in runs for lineage.

### 4.4 Lineage and Integration with Inference

- **Lineage:** Link run → dataset version, code commit, model artifact → deployed endpoint.
- **Integration:** Pipeline publishes model URI to registry; inference platform reads registry and deploys (e.g. by tag “Production”) or is triggered by webhook/event.

---

## 5. Production-Grade Python and System Design

### 5.1 Production Python

- **Clarity:** Small functions, clear names, type hints; docstrings for public APIs.
- **Error handling:** Use exceptions; don’t swallow errors; log with context (request_id, model_version).
- **Config:** Environment variables or config files; no secrets in code; 12-factor style.
- **Testing:** Unit tests for preprocessing and business logic; integration tests for predict path; load tests for latency/throughput.
- **Dependencies:** Pin versions (requirements.txt or poetry); minimal surface; understand critical libs (e.g. how `sklearn` loads models, what `pickle` does).

### 5.2 Library Depth (Loading, Parsing, Internals)

Be prepared to explain:

- **Loading:** e.g. `joblib.load()` vs `pickle`; ONNX `onnxruntime.InferenceSession`; TF `tf.saved_model.load()`.
- **Parsing:** Request validation (Pydantic); safe parsing of JSON/config; schema evolution.
- **Internals:** e.g. sklearn pipeline steps order; what gets serialized in a pickle (module path matters); thread-safety of a global model object.

### 5.3 Scalable and Extensible System Design

- **Stateless servers:** No in-memory state that can’t be recreated; session affinity only if required.
- **Pluggable components:** Feature source, model loader, post-processor as interfaces; swap implementations without changing the serving loop.
- **Configuration-driven:** Model URI, batch size, timeouts from config; easy to change per environment or version.

---

## 6. Summary Checklist

- [ ] Explain end-to-end model lifecycle (train → deploy → monitor → update).
- [ ] Describe trade-offs: latency vs throughput, batching, scaling, cost.
- [ ] Explain versioning and registry; safe rollout and rollback.
- [ ] Name serving frameworks (Triton, TF Serving, TorchServe, KServe) and when to use each.
- [ ] Sketch K8s Deployment/Service and canary strategy.
- [ ] Define metrics and alerts for inference (latency, errors, drift).
- [ ] Explain ML platform: experiments, registry, pipelines, features, lineage.
- [ ] Write clear, testable Python (contracts, config, errors); explain key library behavior.
- [ ] Design a scalable, extensible inference system (stateless, pluggable, config-driven).

### Hands-On: Ensemble Project in This Repo

The **ensemble_project** folder implements the full lifecycle in code:

- **Data:** `src/data/load_data.py` – load with optional version for lineage.
- **Preprocess:** `src/data/preprocess.py` – stratified train/val/test split (scaling in pipeline).
- **Ensemble:** `src/models/ensemble.py` – `Pipeline(StandardScaler(), VotingClassifier(lr, rf, gb))`.
- **Train:** `train.py` + `src/models/train.py` – config-driven train → evaluate → save.
- **Package:** `src/package/save_model.py` – joblib + metadata.json (version, metrics).
- **Serve:** `api/main.py` – FastAPI, load at startup, `/health`, `/ready`, `/predict`.
- **Deploy:** `Dockerfile`, `k8s/deployment.yaml` – container and K8s Deployment/Service.

See [ensemble_project/README.md](./ensemble_project/README.md) for quick start and [ensemble_project/LIFECYCLE.md](./ensemble_project/LIFECYCLE.md) for a component-by-component walkthrough. Use it as a concrete example: data → train (ensemble) → validate → package → serve and deploy, with each step explained in code and docs.
