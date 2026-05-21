from abc import ABC, abstractmethod
from pathlib import Path
from typing import Tuple

from ..domain.artifacts import DatasetMetadata
from ..run_spec import RunSpec


class IDataExtractor(ABC):
    """Extract raw dataset from source (BigQuery, local, etc.)."""

    @abstractmethod
    def extract(self, spec: RunSpec, output_dir: Path) -> Tuple[Path, DatasetMetadata]:
        """Extract data; write raw_dataset.parquet + dataset_metadata.json; return (path, metadata)."""
        pass
