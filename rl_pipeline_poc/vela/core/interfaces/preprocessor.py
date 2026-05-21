from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple

from ..run_spec import RunSpec
from .artifact_store import IArtifactStore


class IPreprocessor(ABC):
    """Feature preprocessing: scale, encode, missing value; save/load artifacts."""

    @abstractmethod
    def fit_transform(
        self,
        raw_data_path: Path,
        spec: RunSpec,
        artifact_store: IArtifactStore,
        run_id: str,
        output_dir: Path,
    ) -> Tuple[Path, Path, Path]:
        """Fit preprocessors, transform, save artifacts. Returns (train_path, val_path, artifacts_dir)."""
        pass

    @abstractmethod
    def transform(
        self,
        raw_data_path: Path,
        preprocess_artifacts_path: Path,
        output_path: Path,
    ) -> Path:
        """Apply saved preprocessors; return path to transformed data."""
        pass
