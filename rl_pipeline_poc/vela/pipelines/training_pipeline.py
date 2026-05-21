"""VELA Training Pipeline: extract -> preprocess -> train -> evaluate -> register."""
import uuid
from pathlib import Path

from vela.core import load_run_spec, RunSpec
from vela.core.domain.artifacts import DatasetMetadata, EvalReport, TrainMetrics
from vela.operators.data_extraction import DataExtractionOperator, LocalDataExtractor
from vela.operators.preprocessing import PreprocessingOperator, SklearnPreprocessor
from vela.operators.training import TrainingOperator
from vela.operators.evaluation import EvaluationOperator
from vela.operators.registry import RegistryOperator
from vela.operators.artifact_store_impl import LocalArtifactStore


def run_training_pipeline(
    spec: RunSpec,
    output_base: Path,
    artifact_store: LocalArtifactStore | None = None,
    promote_to_prod: bool = False,
) -> dict:
    """Run full training pipeline; return run summary (paths, metrics, eval pass/fail)."""
    if spec.pipeline_type != "training":
        spec = RunSpec.from_dict({**spec.to_dict(), "pipeline_type": "training"})

    run_id = str(uuid.uuid4()).replace("-", "")[:16]
    output_dir = Path(output_base) / run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    if artifact_store is None:
        artifact_store = LocalArtifactStore(output_base / "artifacts")

    extractor = DataExtractionOperator(LocalDataExtractor())
    preproc_op = PreprocessingOperator(SklearnPreprocessor())
    train_op = TrainingOperator()
    eval_op = EvaluationOperator()
    reg_op = RegistryOperator()

    # 1) Data Extraction
    raw_dir = output_dir / "01_raw"
    raw_path, dataset_meta = extractor.run(spec, raw_dir)

    # 2) Preprocessing
    preprocess_dir = output_dir / "02_preprocess"
    train_path, val_path, artifacts_dir = preproc_op.fit_transform(
        raw_path, spec, artifact_store, run_id, preprocess_dir
    )

    # 3) Training
    train_out_dir = output_dir / "03_train"
    policy_path, train_metrics = train_op.run(train_path, val_path, spec, train_out_dir)

    # 4) Evaluation & Gates
    eval_report = eval_op.run(policy_path, val_path, spec, train_metrics)

    # 5) Registry (and optional promote)
    model_uri = reg_op.run(
        policy_path.parent,
        spec,
        train_metrics,
        eval_report,
        artifact_store,
        run_id,
        promote_to_prod=promote_to_prod and eval_report.passed,
    )

    return {
        "run_id": run_id,
        "output_dir": str(output_dir),
        "raw_path": str(raw_path),
        "train_path": str(train_path),
        "val_path": str(val_path),
        "policy_path": str(policy_path),
        "model_uri": model_uri,
        "train_metrics": {
            "total_reward": train_metrics.total_reward,
            "reward_per_episode": train_metrics.reward_per_episode,
            "reward_std": train_metrics.reward_std,
        },
        "eval_passed": eval_report.passed,
        "eval_reasons": eval_report.reasons,
        "promoted_to_prod": promote_to_prod and eval_report.passed,
    }
