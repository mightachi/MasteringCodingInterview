"""
Training loop: build pipeline, fit, evaluate, and trigger save.

Interview point: Single entrypoint that ties data -> model -> evaluation -> artifact.
In production you would also log params/metrics to MLflow and register the model.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np

from src.evaluation.evaluate import evaluate
from src.models.ensemble import build_ensemble_pipeline
from src.package.save_model import save_pipeline


def train_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    config: Dict[str, Any],
    output_dir: Optional[Path] = None,
    dataset_version: Optional[str] = None,
) -> Tuple[Any, Dict[str, float]]:
    """
    Train ensemble pipeline, evaluate on val/test, save artifact.

    Returns:
        (fitted_pipeline, metrics_dict)
    """
    model_cfg = config.get("model", {}).get("ensemble", {})
    pipeline = build_ensemble_pipeline(
        n_estimators_rf=model_cfg.get("n_estimators_rf", 100),
        max_depth_rf=model_cfg.get("max_depth_rf", 10),
        n_estimators_gb=model_cfg.get("n_estimators_gb", 100),
        max_depth_gb=model_cfg.get("max_depth_gb", 5),
    )

    pipeline.fit(X_train, y_train)

    metrics_val = evaluate(pipeline, X_val, y_val, prefix="val")
    metrics_test = evaluate(pipeline, X_test, y_test, prefix="test")
    metrics = {**metrics_val, **metrics_test}

    if output_dir is None:
        output_dir = Path(config.get("model", {}).get("output_dir", "models"))
    output_dir = Path(output_dir)
    artifact_name = config.get("model", {}).get("artifact_name", "ensemble_pipeline")
    version = config.get("project", {}).get("version", "1.0.0")

    save_pipeline(
        pipeline=pipeline,
        output_dir=output_dir,
        artifact_name=artifact_name,
        version=version,
        dataset_version=dataset_version,
        metrics=metrics,
    )

    return pipeline, metrics
