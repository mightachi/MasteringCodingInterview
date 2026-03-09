"""
Evaluation: metrics and optional threshold tuning.

Interview point: We log metrics that matter for the business (accuracy, AUC, etc.)
and optionally adjust decision threshold for precision/recall trade-off.
"""

from typing import Any, Dict

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def evaluate(
    pipeline: Any,
    X: np.ndarray,
    y_true: np.ndarray,
    prefix: str = "",
) -> Dict[str, float]:
    """
    Compute metrics for a binary classifier pipeline.

    Assumes pipeline has .predict() and .predict_proba() (for AUC).
    """
    y_pred = pipeline.predict(X)
    sep = "_" if prefix else ""

    metrics = {
        f"{prefix}{sep}accuracy": accuracy_score(y_true, y_pred),
        f"{prefix}{sep}precision": precision_score(y_true, y_pred, zero_division=0),
        f"{prefix}{sep}recall": recall_score(y_true, y_pred, zero_division=0),
        f"{prefix}{sep}f1": f1_score(y_true, y_pred, zero_division=0),
    }

    if hasattr(pipeline, "predict_proba"):
        proba = pipeline.predict_proba(X)[:, 1]
        metrics[f"{prefix}{sep}roc_auc"] = roc_auc_score(y_true, proba)

    return metrics
