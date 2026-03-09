"""
Ensemble model: scaler + VotingClassifier (or StackingClassifier).

Interview point: We use soft voting over LogisticRegression, RandomForest, and
GradientBoostingClassifier. All in one sklearn Pipeline so serialization is a single
artifact and serve logic is just pipeline.predict(X).
"""

from sklearn.ensemble import (
    GradientBoostingClassifier,
    RandomForestClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def build_ensemble_pipeline(
    random_state: int = 42,
    n_estimators_rf: int = 100,
    max_depth_rf: int = 10,
    n_estimators_gb: int = 100,
    max_depth_gb: int = 5,
) -> Pipeline:
    """
    Build full pipeline: StandardScaler + VotingClassifier (soft voting).

    - LogisticRegression: fast baseline, benefits from scaling.
    - RandomForest: robust, no scaling needed but harmless.
    - GradientBoosting: strong performance; scaling often helps.

    Returns:
        Pipeline with steps [("scaler", StandardScaler), ("ensemble", VotingClassifier)].
    """
    estimators = [
        ("lr", LogisticRegression(max_iter=1000, random_state=random_state)),
        (
            "rf",
            RandomForestClassifier(
                n_estimators=n_estimators_rf,
                max_depth=max_depth_rf,
                random_state=random_state,
            ),
        ),
        (
            "gb",
            GradientBoostingClassifier(
                n_estimators=n_estimators_gb,
                max_depth=max_depth_gb,
                random_state=random_state,
            ),
        ),
    ]
    voting = VotingClassifier(estimators=estimators, voting="soft")
    return Pipeline([
        ("scaler", StandardScaler()),
        ("ensemble", voting),
    ])
