from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional


class IArtifactStore(ABC):
    """Persist and load preprocessors, policy checkpoints, RunSpec snapshots."""

    @abstractmethod
    def save_preprocess_artifacts(self, run_id: str, project: str, segment: str, artifacts_dir: Path) -> str:
        """Save preprocess artifacts; return URI/path."""
        pass

    @abstractmethod
    def load_preprocess_artifacts(self, uri: str) -> Path:
        """Return path to unpacked preprocess artifacts."""
        pass

    @abstractmethod
    def save_policy(self, run_id: str, project: str, segment: str, policy_path: Path, metadata: dict) -> str:
        """Save policy checkpoint; return URI."""
        pass

    @abstractmethod
    def load_policy(self, uri: str) -> Path:
        """Return path to policy checkpoint."""
        pass

    @abstractmethod
    def get_production_policy_uri(self, project: str, segment: str) -> Optional[str]:
        """Get URI for current PROD alias (for refinement/inference)."""
        pass

    @abstractmethod
    def register_production(self, project: str, segment: str, model_uri: str) -> None:
        """Promote model version to PROD alias."""
        pass
