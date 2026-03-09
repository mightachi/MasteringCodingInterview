"""
Data loading with validation and optional versioning.

Interview point: Reproducibility requires knowing exactly which data was used.
We return a dataset object that carries path/version so training can log it (e.g. MLflow).
"""

from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd


def load_data(
    source: str,
    version: Optional[str] = None,
) -> Tuple[np.ndarray, np.ndarray, Optional[str]]:
    """
    Load feature matrix X and target y.

    Args:
        source: "sklearn_dataset" for in-memory demo, or path to CSV (e.g. "data/raw/train.csv").
        version: Optional dataset version for lineage (e.g. "20240301").

    Returns:
        (X, y, dataset_version). dataset_version is None for sklearn_dataset.
    """
    if source == "sklearn_dataset":
        from sklearn.datasets import load_breast_cancer

        data = load_breast_cancer()
        X, y = data.data, data.target
        # Optional: wrap in DataFrame for clarity; we use ndarray for sklearn API
        return X, y, None

    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)
    # Assume last column is target; rest are features (config could specify column names)
    target_col = df.columns[-1]
    y = df[target_col].values
    X = df.drop(columns=[target_col]).values
    dataset_version = version or path.parent.name
    return X, y, dataset_version
