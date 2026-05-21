"""Feature Preprocessing Operator: raw -> train/val features + preprocess_artifacts."""
import json
import pickle
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from vela.core.interfaces import IArtifactStore, IPreprocessor
from vela.core.run_spec import RunSpec


class SklearnPreprocessor(IPreprocessor):
    """StandardScaler + optional encoding; fit_transform saves artifacts."""

    def fit_transform(
        self,
        raw_data_path: Path,
        spec: RunSpec,
        artifact_store: IArtifactStore,
        run_id: str,
        output_dir: Path,
    ) -> tuple[Path, Path, Path]:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        artifacts_dir = output_dir / "preprocess_artifacts"
        artifacts_dir.mkdir(exist_ok=True)

        df = pd.read_parquet(raw_data_path)
        numeric = [c for c in spec.features.numeric_features if c in df.columns]
        if not numeric:
            numeric = [c for c in df.select_dtypes(include=["number"]).columns if c != "entity_id"][:5]
        X = df[numeric].fillna(df[numeric].median())
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        X_df = pd.DataFrame(X_scaled, columns=numeric, index=df.index)
        for c in df.columns:
            if c not in X_df.columns:
                X_df[c] = df[c].values

        train_df, val_df = train_test_split(X_df, test_size=0.2, random_state=42)
        train_path = output_dir / "train_features.parquet"
        val_path = output_dir / "val_features.parquet"
        train_df.to_parquet(train_path, index=False)
        val_df.to_parquet(val_path, index=False)

        with open(artifacts_dir / "scaler.pkl", "wb") as f:
            pickle.dump(scaler, f)
        with open(artifacts_dir / "feature_columns.json", "w") as f:
            json.dump(numeric, f)

        artifact_store.save_preprocess_artifacts(run_id, spec.project_id, spec.segment_id, artifacts_dir)
        return train_path, val_path, artifacts_dir

    def transform(self, raw_data_path: Path, preprocess_artifacts_path: Path, output_path: Path) -> Path:
        df = pd.read_parquet(raw_data_path)
        with open(preprocess_artifacts_path / "scaler.pkl", "rb") as f:
            scaler = pickle.load(f)
        with open(preprocess_artifacts_path / "feature_columns.json") as f:
            numeric = json.load(f)
        X = df[numeric].fillna(df[numeric].median())
        X_scaled = scaler.transform(X)
        X_df = pd.DataFrame(X_scaled, columns=numeric, index=df.index)
        for c in df.columns:
            if c not in X_df.columns:
                X_df[c] = df[c].values
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        X_df.to_parquet(output_path, index=False)
        return output_path


class PreprocessingOperator:
    def __init__(self, preprocessor: IPreprocessor):
        self.preprocessor = preprocessor

    def fit_transform(self, raw_path: Path, spec: RunSpec, store: IArtifactStore, run_id: str, output_dir: Path):
        return self.preprocessor.fit_transform(raw_path, spec, store, run_id, output_dir)

    def transform(self, raw_path: Path, artifacts_path: Path, output_path: Path):
        return self.preprocessor.transform(raw_path, artifacts_path, output_path)
