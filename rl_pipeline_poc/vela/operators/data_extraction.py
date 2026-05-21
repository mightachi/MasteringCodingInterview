"""Data Extraction Operator: warehouse/local -> raw_dataset.parquet + metadata."""
import json
from pathlib import Path

import pandas as pd

from vela.core.domain.artifacts import DatasetMetadata
from vela.core.interfaces import IDataExtractor
from vela.core.run_spec import RunSpec


class LocalDataExtractor(IDataExtractor):
    """Extract from local CSV/parquet (POC). For production, swap with BigQuery extractor."""

    def extract(self, spec: RunSpec, output_dir: Path) -> tuple[Path, DatasetMetadata]:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        path = Path(spec.data.query_or_path)
        if not path.exists():
            # Generate synthetic data for demo
            df = self._synthetic_data(spec)
        else:
            if path.suffix == ".csv":
                df = pd.read_csv(path)
            else:
                df = pd.read_parquet(path)

        out_path = output_dir / "raw_dataset.parquet"
        df.to_parquet(out_path, index=False)

        meta = DatasetMetadata(
            path=str(out_path),
            run_date=spec.data.run_date,
            lookback_days=spec.data.lookback_days,
            num_rows=len(df),
            num_features=len(spec.features.numeric_features) + len(spec.features.categorical_features),
            segment_id=spec.segment_id,
        )
        meta_path = output_dir / "dataset_metadata.json"
        with open(meta_path, "w") as f:
            json.dump(
                {
                    "path": meta.path,
                    "run_date": meta.run_date,
                    "lookback_days": meta.lookback_days,
                    "num_rows": meta.num_rows,
                    "num_features": meta.num_features,
                    "segment_id": meta.segment_id,
                },
                f,
                indent=2,
            )
        return out_path, meta

    def _synthetic_data(self, spec: RunSpec) -> pd.DataFrame:
        """Generate minimal synthetic data for POC."""
        n = 5000
        import numpy as np
        np.random.seed(42)
        cols = spec.features.numeric_features or ["f1", "f2", "f3", "revenue", "prev_delta"]
        df = pd.DataFrame(
            np.random.randn(n, len(cols)).cumsum(axis=0) * 0.1 + np.random.randn(n, len(cols)) * 0.5,
            columns=cols,
        )
        df["entity_id"] = [f"e_{i}" for i in range(n)]
        if "prev_delta" not in df.columns and "prev_delta" in cols:
            df["prev_delta"] = np.random.choice(spec.actions.buckets, size=n)
        return df


class DataExtractionOperator:
    """Facade: runs the configured extractor (Strategy pattern)."""

    def __init__(self, extractor: IDataExtractor):
        self.extractor = extractor

    def run(self, spec: RunSpec, output_dir: Path) -> tuple[Path, DatasetMetadata]:
        return self.extractor.extract(spec, output_dir)
