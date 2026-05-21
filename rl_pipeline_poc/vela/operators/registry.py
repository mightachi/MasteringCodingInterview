"""Registry Operator: log model + RunSpec snapshot to MLflow / local."""
import json
from pathlib import Path

from vela.core.domain.artifacts import EvalReport, TrainMetrics
from vela.core.interfaces import IArtifactStore
from vela.core.run_spec import RunSpec

try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False


class RegistryOperator:
    """Register policy + config in MLflow (or local) with tags; optionally promote to PROD."""

    def run(
        self,
        policy_path: Path,
        spec: RunSpec,
        train_metrics: TrainMetrics,
        eval_report: EvalReport,
        artifact_store: IArtifactStore,
        run_id: str,
        promote_to_prod: bool = False,
    ) -> str:
        metadata = {
            "project_id": spec.project_id,
            "segment_id": spec.segment_id,
            "algorithm": spec.training.algorithm,
            "reward_template": spec.reward.template,
            "total_reward": train_metrics.total_reward,
            "reward_per_episode": train_metrics.reward_per_episode,
            "eval_passed": eval_report.passed,
        }
        uri = artifact_store.save_policy(run_id, spec.project_id, spec.segment_id, policy_path, metadata)
        if promote_to_prod and eval_report.passed:
            artifact_store.register_production(spec.project_id, spec.segment_id, uri)
        return uri
