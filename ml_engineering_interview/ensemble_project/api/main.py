"""
Inference API: load model once at startup, serve /health and /predict.

Interview point: Stateless server; model loaded in startup event; input validated
with Pydantic; same feature order as training (schema consistency). In production
add auth, rate limiting, and Prometheus metrics.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Project root for resolving MODEL_PATH and importing src
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.package.save_model import load_pipeline

app = FastAPI(title="Ensemble Model API", version="1.0.0")

# Global model and metadata (loaded at startup)
_model = None
_metadata = {}
_model_version = "unknown"


class PredictRequest(BaseModel):
    """Expect a list of feature vectors (each row = one sample)."""

    features: List[List[float]] = Field(..., min_length=1, description="List of feature vectors")

    class Config:
        # breast_cancer has 30 features per sample
        json_schema_extra = {
            "example": {
                "features": [[0.0] * 30]
            }
        }


class PredictResponse(BaseModel):
    predictions: List[int]
    probabilities: Optional[List[float]] = None
    model_version: str


def _get_model_path() -> Path:
    """Resolve model path from env or default."""
    path = os.environ.get("MODEL_PATH")
    if path:
        return Path(path)
    # Default: latest version under models/ensemble_pipeline
    base = ROOT / "models" / "ensemble_pipeline"
    if not base.exists():
        raise FileNotFoundError(f"Model directory not found: {base}. Run train.py first.")
    versions = sorted([d.name for d in base.iterdir() if d.is_dir()], reverse=True)
    if not versions:
        raise FileNotFoundError(f"No version found under {base}")
    return base / versions[0]


@app.on_event("startup")
def load_model() -> None:
    global _model, _metadata, _model_version
    try:
        artifact_path = _get_model_path()
        _model, _metadata = load_pipeline(artifact_path)
        _model_version = _metadata.get("version", artifact_path.name)
    except Exception as e:
        raise RuntimeError(f"Failed to load model: {e}") from e


@app.get("/health")
def health() -> dict:
    """Liveness: is the process up?"""
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict:
    """Readiness: is the model loaded and ready to serve?"""
    if _model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ready", "model_version": _model_version}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    """Run inference. features: list of rows (each row = one sample)."""
    if _model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    import numpy as np

    X = np.array(request.features)
    predictions = _model.predict(X).tolist()

    probabilities = None
    if hasattr(_model, "predict_proba"):
        proba = _model.predict_proba(X)[:, 1]
        probabilities = proba.tolist()

    return PredictResponse(
        predictions=predictions,
        probabilities=probabilities,
        model_version=_model_version,
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
