"""
Training entrypoint: load config, data, preprocess, train, evaluate, save.

Run from project root: python train.py

Interview point: This script is the "orchestrator" that could be wrapped by
Airflow/Kubeflow/MLflow Projects for pipeline runs. It logs dataset version
and model version for lineage.
"""

import sys
from pathlib import Path

import yaml

# Add project root so "src" imports work
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.data.load_data import load_data
from src.data.preprocess import preprocess
from src.models.train import train_model


def main() -> None:
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # 1. Data
    data_cfg = config.get("data", {})
    X, y, dataset_version = load_data(
        source=data_cfg.get("source", "sklearn_dataset"),
        version=data_cfg.get("version"),
    )

    # 2. Split (no scaling here; pipeline does it)
    X_train, y_train, X_val, y_val, X_test, y_test = preprocess(
        X, y,
        test_size=data_cfg.get("test_size", 0.2),
        val_size=data_cfg.get("val_size", 0.1),
        random_state=data_cfg.get("random_state", 42),
    )

    # 3. Train + evaluate + save
    pipeline, metrics = train_model(
        X_train, y_train, X_val, y_val, X_test, y_test,
        config=config,
        dataset_version=dataset_version,
    )

    print("Metrics:", metrics)
    print("Model saved under:", config.get("model", {}).get("output_dir", "models"))


if __name__ == "__main__":
    main()
