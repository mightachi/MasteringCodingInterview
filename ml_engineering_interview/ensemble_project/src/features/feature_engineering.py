"""
Feature pipeline: preprocessing + (optional) feature construction.

Interview point: This pipeline is fitted on training data and serialized with the model.
At serve time we load the same pipeline and call transform (or the full pipeline predict).
Ensures train/serve consistency.
"""

from typing import Optional

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def build_feature_pipeline(
    scaler: Optional[StandardScaler] = None,
    fit_scaler_on_X: Optional[object] = None,
) -> Pipeline:
    """
    Build a sklearn Pipeline for feature processing.

    - If scaler is provided (e.g. from preprocess step), we use it (no refit).
    - If fit_scaler_on_X is provided, we fit a new StandardScaler on it and use it.
    - Otherwise we add an unfitted StandardScaler (caller will fit the full pipeline on X_train).

    Returns:
        Pipeline with steps: [("scaler", StandardScaler), ...]. More steps (e.g. selector) can be added.
    """
    if scaler is not None:
        steps = [("scaler", scaler)]
    elif fit_scaler_on_X is not None:
        s = StandardScaler()
        s.fit(fit_scaler_on_X)
        steps = [("scaler", s)]
    else:
        steps = [("scaler", StandardScaler())]

    return Pipeline(steps)
