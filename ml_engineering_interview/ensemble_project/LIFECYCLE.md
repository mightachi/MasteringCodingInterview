# Ensemble Project – Lifecycle Component Guide

This document walks through **each component** of the ML lifecycle as implemented in this project, so you can explain and extend it in an interview.

---

## 1. Data Loading (`src/data/load_data.py`)

**Purpose:** Load raw data and optionally attach a version for lineage.

**Concepts:**

- **Reproducibility:** Every training run should record which data it used (path or version). Here we return `dataset_version` so the training script can log it (e.g. in MLflow or in `metadata.json`).
- **Abstraction:** `source` can be a built-in dataset ("sklearn_dataset") or a path to CSV. In production you might add Parquet, Delta, or a query to a data warehouse.

**Interview tip:** Explain why we version datasets (audit, rollback, debugging) and how you’d extend this to a feature store or warehouse table with a version/timestamp.

---

## 2. Preprocessing / Split (`src/data/preprocess.py`)

**Purpose:** Split data into train/val/test in a reproducible way.

**Concepts:**

- **Stratification:** `stratify=y` keeps class balance in each split.
- **Single responsibility:** We only split here. Scaling lives in the **pipeline** so that the same fitted scaler is serialized with the model and reused at serve time. That avoids train/serve skew.

**Interview tip:** Why not scale in `preprocess` and save the scaler separately? You can, but then you have two artifacts and must keep them in sync. One pipeline (scaler + model) is simpler and less error-prone.

---

## 3. Feature Pipeline (`src/features/feature_engineering.py`)

**Purpose:** Define the preprocessing steps that will be part of the saved model.

**Concepts:**

- In this project the **ensemble pipeline** already includes the scaler (see `src/models/ensemble.py`), so the feature pipeline is minimal. In a larger system you might have a dedicated `Pipeline([Imputer(), Scaler(), Selector(), ...])` that is fitted on train and saved with the model.
- **Train/serve consistency:** Whatever transform you apply in training must be applied identically at inference. Putting it in one sklearn `Pipeline` guarantees that.

**Interview tip:** Discuss how you’d add feature selection, one-hot encoding, or custom transformers, and how you’d validate schema (number and order of features) at serve time.

---

## 4. Ensemble Model (`src/models/ensemble.py`)

**Purpose:** Define the model as a single pipeline: scaler + VotingClassifier.

**Concepts:**

- **VotingClassifier (soft voting):** Each base estimator outputs class probabilities; the ensemble averages them and picks the class with highest average probability. Better than hard voting when classifiers are well-calibrated.
- **Why these estimators:** Logistic regression (linear, interpretable), Random Forest (non-linear, robust), Gradient Boosting (strong performance). All work with the same feature matrix after scaling.
- **Pipeline:** `Pipeline([("scaler", StandardScaler()), ("ensemble", VotingClassifier(...))])` is fitted once on raw `X_train`. At serve we pass raw features and get predictions.

**Interview tip:** Explain the difference between bagging (e.g. Random Forest) and boosting (e.g. Gradient Boosting), and when you’d use StackingClassifier instead of VotingClassifier (more flexibility, meta-learner, but more complexity and overfitting risk).

---

## 5. Training Orchestration (`src/models/train.py`, `train.py`)

**Purpose:** Tie together: load data → split → build pipeline → fit → evaluate → save.

**Concepts:**

- **Single entrypoint:** `train.py` reads config, calls data and preprocessing, then `train_model()`. In production this could be one step in an Airflow DAG or a Kubeflow pipeline.
- **Evaluation:** We evaluate on both validation (for early stopping / model selection) and test (for final reporting). Metrics are saved in `metadata.json` for comparison across runs.
- **Config-driven:** Hyperparameters and paths come from `config.yaml` (or env) so the same code can run in dev/staging/prod with different configs.

**Interview tip:** How would you add MLflow? In `train_model()`, use `mlflow.start_run()`, `mlflow.log_params()`, `mlflow.log_metrics()`, and `mlflow.sklearn.log_model()` (or log the artifact path). Then register the model in the MLflow Model Registry and point the inference service to the registered artifact.

---

## 6. Evaluation (`src/evaluation/evaluate.py`)

**Purpose:** Compute metrics (accuracy, precision, recall, F1, ROC-AUC) for a given split.

**Concepts:**

- **Binary classification:** Metrics assume binary labels. For multi-class you’d use macro/micro averages or a confusion matrix.
- **predict_proba:** We use it for ROC-AUC. The pipeline exposes `predict_proba` because VotingClassifier (soft) and the base estimators support it.
- **Threshold:** Default decision threshold is 0.5. In production you might tune threshold for precision/recall trade-off and save it in config or metadata.

**Interview tip:** How would you detect model drift? Compare recent request feature distributions to training distribution (e.g. PSI), or compare predictions vs actuals over time (if you have delayed labels).

---

## 7. Packaging (`src/package/save_model.py`)

**Purpose:** Save the pipeline and metadata so deployment can load one artifact and know its lineage.

**Concepts:**

- **joblib:** Standard way to serialize sklearn models (and pipelines). It pickles the object graph. Ensure the same Python/sklearn versions at train and serve to avoid deserialization issues.
- **Metadata:** We save version, dataset_version, and metrics. At deploy time you can validate that the loaded model version matches what you expect and surface it in `/ready` or logs.
- **Directory layout:** `models/ensemble_pipeline/1.0.0/model.joblib` and `metadata.json` keeps multiple versions side by side for rollback.

**Interview tip:** When would you use ONNX or TorchScript instead of joblib? When you need framework-agnostic serving (ONNX) or production runtimes (e.g. Triton with ONNX), or when the model is PyTorch and you want optimized inference. For sklearn, joblib is usually sufficient.

---

## 8. Inference API (`api/main.py`)

**Purpose:** Load the model once at startup and serve HTTP `/health`, `/ready`, and `/predict`.

**Concepts:**

- **Startup load:** Model is loaded in `on_event("startup")`. Readiness probe should succeed only after load completes so K8s doesn’t send traffic until the model is ready.
- **Stateless:** No per-request state; the same global model is used for all requests. Scale by adding replicas.
- **Input validation:** Pydantic validates `PredictRequest` (list of feature lists). You could add schema checks (e.g. exact number of features) to catch client bugs or upstream changes.
- **Model version in response:** Returning `model_version` helps debugging and audit.

**Interview tip:** How would you add metrics? Use `prometheus_client`: a Histogram for latency, Counter for request count by status/model_version. Expose `/metrics` for Prometheus scraping. Optionally add request_id to logs for tracing.

---

## 9. Deployment (Dockerfile, k8s/)

**Purpose:** Containerize the app and run it on Kubernetes.

**Concepts:**

- **Dockerfile:** Install deps, copy code, run `train.py` at build time so the image contains a trained model (optional; alternatively mount a volume or pull from a registry at startup).
- **K8s Deployment:** Replicas, resource requests/limits, liveness and readiness probes. Use readiness so traffic only goes to pods that have finished loading the model.
- **Service:** ClusterIP (or LoadBalancer/Ingress for external access) to route to the deployment.

**Interview tip:** For canary rollouts, run two Deployments (e.g. `version: v1` and `version: v2`) and use an Ingress or service mesh to split traffic (e.g. 90% v1, 10% v2). Compare latency and error rate before shifting more traffic to v2.

---

## 10. End-to-End Flow (Summary)

| Step | Component | Input | Output |
|------|------------|--------|--------|
| 1 | load_data | source, version | X, y, dataset_version |
| 2 | preprocess | X, y, config | X_train, y_train, X_val, y_val, X_test, y_test |
| 3 | build_ensemble_pipeline | config | Pipeline(scaler, VotingClassifier) |
| 4 | pipeline.fit(X_train, y_train) | train data | fitted pipeline |
| 5 | evaluate | pipeline, X_val, X_test, y | metrics |
| 6 | save_pipeline | pipeline, metadata | model.joblib, metadata.json |
| 7 | load_pipeline (in API) | artifact path | pipeline, metadata |
| 8 | POST /predict | features | predictions, probabilities, model_version |

Using this flow, you can describe the full lifecycle from data to deployment and tie it to the interview prep topics: versioning, observability, safe rollouts, and production Python.
