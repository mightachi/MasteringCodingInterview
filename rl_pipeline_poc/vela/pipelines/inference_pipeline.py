"""VELA Inference Pipeline: fetch policy -> build features -> preprocess -> infer -> guardrails -> publish."""
from pathlib import Path

from vela.core import load_run_spec, RunSpec
from vela.operators.data_extraction import DataExtractionOperator, LocalDataExtractor
from vela.operators.preprocessing import PreprocessingOperator, SklearnPreprocessor
from vela.operators.inference import InferenceOperator
from vela.operators.artifact_store_impl import LocalArtifactStore


def run_inference_pipeline(
    spec: RunSpec,
    output_base: Path,
    artifact_store: LocalArtifactStore | None = None,
) -> dict:
    """Run batch inference; return path to final_decisions table/file."""
    if spec.pipeline_type != "inference":
        spec = RunSpec.from_dict({**spec.to_dict(), "pipeline_type": "inference"})

    output_dir = Path(output_base) / "inference_run"
    output_dir.mkdir(parents=True, exist_ok=True)

    if artifact_store is None:
        artifact_store = LocalArtifactStore(output_base / "artifacts")

    # 1) Policy Fetch
    policy_uri = artifact_store.get_production_policy_uri(spec.project_id, spec.segment_id)
    if not policy_uri:
        raise FileNotFoundError(f"No production policy for {spec.project_id}/{spec.segment_id}. Run training and promote first.")
    policy_path = artifact_store.load_policy(policy_uri)

    # 2) Inference Data Build (extract latest window)
    extractor = DataExtractionOperator(LocalDataExtractor())
    raw_dir = output_dir / "01_raw"
    raw_path, _ = extractor.run(spec, raw_dir)

    # 3) Preprocess Apply (reuse transformers)
    preprocess_dir = Path(artifact_store.base) / spec.project_id / spec.segment_id / "preprocess"
    if not preprocess_dir.exists():
        raise FileNotFoundError(f"No preprocess artifacts for {spec.project_id}/{spec.segment_id}")
    latest = sorted(preprocess_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)[0]
    preprocess_artifacts_path = latest

    preproc_op = PreprocessingOperator(SklearnPreprocessor())
    features_path = output_dir / "02_features" / "inference_features.parquet"
    features_path.parent.mkdir(parents=True, exist_ok=True)
    preproc_op.transform(raw_path, preprocess_artifacts_path, features_path)

    # 4) Policy Inference + 5) Guardrails + 6) Publish
    out_path = Path(spec.output_table_or_path or str(output_dir / "final_decisions.parquet"))
    inf_op = InferenceOperator()
    final_path = inf_op.run(
        policy_path,
        features_path,
        preprocess_artifacts_path,
        spec,
        out_path,
    )

    return {
        "output_path": str(final_path),
        "policy_uri": policy_uri,
        "num_rows": len(__import__("pandas").read_parquet(final_path)),
    }
