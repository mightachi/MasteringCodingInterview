# Ensemble Learning Project – Full Lifecycle to Deployment

This project demonstrates an **end-to-end ML lifecycle** using **ensemble learning** in Python: from data and training through packaging, serving, and deployment. Each component is explained so you can walk through it in an interview.

## Lifecycle Overview

```
Data → Preprocess → Feature Engineering → Train (Ensemble) → Evaluate → Package → Serve → Deploy
```

| Stage | Component | Purpose |
|-------|-----------|---------|
| **Data** | `src/data/load_data.py` | Load and validate raw data; support versioning |
| **Preprocess** | `src/data/preprocess.py` | Cleaning, train/val/test split, optional scaling |
| **Features** | `src/features/feature_engineering.py` | Feature pipeline (same for train and serve) |
| **Train** | `src/models/ensemble.py`, `src/models/train.py` | Ensemble model definition and training loop |
| **Evaluate** | `src/evaluation/evaluate.py` | Metrics, thresholds, and model selection |
| **Package** | `src/package/save_model.py` | Save pipeline + schema + metadata for reproducibility |
| **Serve** | `api/main.py` | FastAPI server: load model, validate input, return predictions |
| **Deploy** | `Dockerfile`, `k8s/` | Container and Kubernetes deployment |

## Quick Start

```bash
# Create venv and install
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# 1. Train and save model (uses sklearn breast_cancer by default)
python train.py

# 2. Run inference server locally
uvicorn api.main:app --host 0.0.0.0 --port 8000

# 3. Call health and predict
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"features": [...]}'
```

## Project Structure

```
ensemble_project/
├── README.md                 # This file
├── requirements.txt
├── config.yaml               # Config for paths, model params, server
├── train.py                  # Entrypoint: run full training pipeline
├── api/
│   └── main.py               # FastAPI app: load model, /health, /predict
├── src/
│   ├── data/
│   │   ├── load_data.py      # Load and validate data
│   │   └── preprocess.py     # Split, optional scaling
│   ├── features/
│   │   └── feature_engineering.py   # Feature pipeline (sklearn Pipeline)
│   ├── models/
│   │   ├── ensemble.py       # Ensemble definition (VotingClassifier / Stacking)
│   │   └── train.py         # Train loop, logging, save
│   ├── evaluation/
│   │   └── evaluate.py      # Metrics, confusion matrix, threshold
│   └── package/
│       └── save_model.py    # Save pipeline + schema + version
├── Dockerfile
└── k8s/
    └── deployment.yaml      # Example K8s Deployment + Service
```

## Ensemble Design

We use a **VotingClassifier** (soft voting) over:

- **Logistic Regression** – fast, interpretable baseline
- **Random Forest** – robust to non-linearity and feature scale
- **Gradient Boosting (e.g. XGBoost or sklearn GradientBoostingClassifier)** – strong performance

Alternative: **StackingClassifier** with a meta-learner for slightly better performance at the cost of complexity.

## Configuration

- **config.yaml**: dataset path (or "sklearn_dataset"), model output path, server port, model version.
- **Environment**: `MODEL_PATH`, `MODEL_VERSION` can override config for deployment.

## Deployment

- **Docker:** `docker build -t ensemble-model:latest . && docker run -p 8000:8000 ensemble-model:latest`
- **K8s:** Apply `k8s/deployment.yaml`; adjust image, resources, and env as needed.

See [INTERVIEW_PREP.md](../INTERVIEW_PREP.md) for inference platform, observability, and safe rollout practices.
