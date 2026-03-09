"""
Packaging: save pipeline + metadata for reproducibility and safe loading.

Interview point: We save (1) the sklearn pipeline (joblib), (2) a small metadata dict
(schema version, dataset version, metrics) for lineage and validation at load time.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

import joblib


def save_pipeline(
    pipeline: Any,
    output_dir: Path,
    artifact_name: str = "ensemble_pipeline",
    version: str = "1.0.0",
    dataset_version: Optional[str] = None,
    metrics: Optional[Dict[str, float]] = None,
) -> Path:
    """
    Save pipeline as joblib and metadata as JSON.

    Directory layout: output_dir / artifact_name / version / model.joblib, metadata.json
    """
    output_dir = Path(output_dir)
    artifact_path = output_dir / artifact_name / version
    artifact_path.mkdir(parents=True, exist_ok=True)

    model_path = artifact_path / "model.joblib"
    joblib.dump(pipeline, model_path)

    metadata = {
        "version": version,
        "artifact_name": artifact_name,
        "dataset_version": dataset_version,
        "metrics": metrics or {},
    }
    meta_path = artifact_path / "metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    return artifact_path


def load_pipeline(artifact_path: Path) -> tuple[Any, Dict[str, Any]]:
    """
    Load pipeline and metadata from an artifact directory.

    artifact_path should point to the versioned folder (e.g. models/ensemble_pipeline/1.0.0).
    Returns (pipeline, metadata).
    """
    artifact_path = Path(artifact_path)
    model_path = artifact_path / "model.joblib"
    meta_path = artifact_path / "metadata.json"

    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    pipeline = joblib.load(model_path)
    metadata = {}
    if meta_path.exists():
        with open(meta_path) as f:
            metadata = json.load(f)

    return pipeline, metadata
