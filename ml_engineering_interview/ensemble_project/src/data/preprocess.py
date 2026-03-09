"""
Preprocessing: train/val/test split only.

Interview point: Scaling is done inside the model pipeline (scaler + classifier)
so one artifact ensures identical preprocessing at serve time. We only split here.
"""

from typing import Tuple

import numpy as np
from sklearn.model_selection import train_test_split


def preprocess(
    X: np.ndarray,
    y: np.ndarray,
    test_size: float = 0.2,
    val_size: float = 0.1,
    random_state: int = 42,
) -> Tuple[
    np.ndarray, np.ndarray,
    np.ndarray, np.ndarray,
    np.ndarray, np.ndarray,
]:
    """
    Split into train/val/test. No scaling here; pipeline handles that.

    Returns:
        X_train, y_train, X_val, y_val, X_test, y_test
    """
    # First split: train+val vs test
    X_tt, X_test, y_tt, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    # Second split: train vs val
    val_ratio = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_tt, y_tt, test_size=val_ratio, random_state=random_state, stratify=y_tt
    )
    return X_train, y_train, X_val, y_val, X_test, y_test
