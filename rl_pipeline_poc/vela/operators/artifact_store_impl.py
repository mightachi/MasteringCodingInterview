"""Local + MLflow artifact store implementation."""
import shutil
from pathlib import Path
from typing import Optional

from vela.core.interfaces import IArtifactStore

try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False


class LocalArtifactStore(IArtifactStore):
    """File-based store for POC (no MLflow)."""

    def __init__(self, base_path: Path):
        self.base = Path(base_path)

    def _segment_dir(self, project: str, segment: str) -> Path:
        d = self.base / project / segment
        d.mkdir(parents=True, exist_ok=True)
        return d

    def save_preprocess_artifacts(self, run_id: str, project: str, segment: str, artifacts_dir: Path) -> str:
        dest = self._segment_dir(project, segment) / "preprocess" / run_id
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(artifacts_dir, dest)
        return str(dest)

    def load_preprocess_artifacts(self, uri: str) -> Path:
        return Path(uri)

    def save_policy(self, run_id: str, project: str, segment: str, policy_path: Path, metadata: dict) -> str:
        dest = self._segment_dir(project, segment) / "policies" / run_id
        dest.mkdir(parents=True, exist_ok=True)
        for f in Path(policy_path).parent.glob(Path(policy_path).name + "*"):
            shutil.copy2(f, dest / f.name)
        return str(dest)

    def load_policy(self, uri: str) -> Path:
        p = Path(uri)
        # stable_baselines3 saves as policy_checkpoint.zip or dir
        for name in ["policy_checkpoint", "policy_checkpoint.zip"]:
            if (p / name).exists():
                return p / name
            if (Path(uri).parent / name).exists():
                return Path(uri).parent / name
        return p

    def get_production_policy_uri(self, project: str, segment: str) -> Optional[str]:
        alias_file = self.base / project / segment / "prod_alias.txt"
        if alias_file.exists():
            return alias_file.read_text().strip()
        policies = self.base / project / segment / "policies"
        if policies.exists():
            subs = sorted(policies.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
            if subs:
                return str(subs[0])
        return None

    def register_production(self, project: str, segment: str, model_uri: str) -> None:
        alias_file = self.base / project / segment / "prod_alias.txt"
        alias_file.parent.mkdir(parents=True, exist_ok=True)
        alias_file.write_text(model_uri)


class MLflowArtifactStore(IArtifactStore):
    """MLflow-backed store for model registry and artifacts."""

    def __init__(self, tracking_uri: str = None, experiment_name: str = "vela"):
        if not MLFLOW_AVAILABLE:
            raise RuntimeError("mlflow not installed")
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        self.experiment_name = experiment_name

    def save_preprocess_artifacts(self, run_id: str, project: str, segment: str, artifacts_dir: Path) -> str:
        with mlflow.start_run(run_id=run_id if len(run_id) == 32 else None):
            mlflow.log_artifacts(str(artifacts_dir), "preprocess_artifacts")
            return mlflow.get_artifact_uri("preprocess_artifacts")

    def load_preprocess_artifacts(self, uri: str) -> Path:
        # MLflow artifact URI; in POC we may download to temp dir
        import tempfile
        from mlflow.tracking import MlflowClient
        client = MlflowClient()
        # uri is like file:///path or mlflow-artifacts:/...
        if uri.startswith("file:"):
            return Path(uri.replace("file://", ""))
        return Path(uri)

    def save_policy(self, run_id: str, project: str, segment: str, policy_path: Path, metadata: dict) -> str:
        with mlflow.start_run(run_id=run_id if len(run_id) == 32 else None):
            mlflow.log_artifacts(str(policy_path.parent), "policy")
            mlflow.log_params(metadata)
            return mlflow.get_artifact_uri("policy")

    def load_policy(self, uri: str) -> Path:
        if uri.startswith("file:"):
            return Path(uri.replace("file://", "")) / "policy_checkpoint"
        return Path(uri) / "policy_checkpoint"

    def get_production_policy_uri(self, project: str, segment: str) -> Optional[str]:
        from mlflow.tracking import MlflowClient
        client = MlflowClient()
        alias = f"prod_{segment}"
        try:
            mv = client.get_model_version_by_alias(project, alias)
            return mv.source
        except Exception:
            return None

    def register_production(self, project: str, segment: str, model_uri: str) -> None:
        from mlflow.tracking import MlflowClient
        client = MlflowClient()
        # Register and set alias
        mv = client.create_model_version(project, model_uri, "run_id", [])
        client.set_registered_model_alias(project, f"prod_{segment}", mv.version)
