from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

from ..domain.artifacts import EvalReport, TrainMetrics
from ..run_spec import RunSpec


class IEvaluator(ABC):
    """Evaluation & gates: metrics + PASS/FAIL."""

    @abstractmethod
    def evaluate(
        self,
        policy_path: Path,
        features_path: Path,
        spec: RunSpec,
        train_metrics: TrainMetrics,
    ) -> EvalReport:
        """Compute eval metrics and gate (stability, reward); return PASS/FAIL + reasons."""
        pass
