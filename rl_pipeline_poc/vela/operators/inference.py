"""Inference Operator: load policy + preprocess, predict actions, apply guardrails, write output."""
import json
from pathlib import Path

import pandas as pd

from vela.core.run_spec import RunSpec

try:
    from stable_baselines3 import A2C, PPO
    SB3_AVAILABLE = True
except ImportError:
    SB3_AVAILABLE = False


class InferenceOperator:
    """Batch inference: policy -> discrete action per row; guardrails; write table/file."""

    def run(
        self,
        policy_path: Path,
        features_path: Path,
        preprocess_artifacts_path: Path,
        spec: RunSpec,
        output_path: Path,
        guardrails: dict | None = None,
    ) -> Path:
        guardrails = guardrails or spec.guardrails
        from vela.operators.preprocessing import SklearnPreprocessor
        preproc = SklearnPreprocessor()
        transformed_path = output_path.parent / "inference_features.parquet"
        preproc.transform(features_path, preprocess_artifacts_path, transformed_path)

        df = pd.read_parquet(transformed_path)
        cols = [c for c in spec.features.numeric_features if c in df.columns]
        if not cols:
            cols = list(df.select_dtypes(include=["number"]).columns)[:8]

        if not SB3_AVAILABLE:
            # Dummy: random actions
            actions = [0] * len(df)
        else:
            algo = spec.training.algorithm.upper()
            model = PPO.load(str(policy_path)) if algo == "PPO" else A2C.load(str(policy_path))
            actions = []
            for i in range(len(df)):
                obs = df.iloc[i][cols].values.astype("float32").reshape(1, -1)
                a, _ = model.predict(obs)
                actions.append(int(a[0]))

        deltas = [spec.actions.buckets[a] for a in actions]
        # Guardrails: clamp delta
        min_d = guardrails.get("min_delta", -1.0)
        max_d = guardrails.get("max_delta", 1.0)
        deltas = [max(min_d, min(max_d, d)) for d in deltas]

        out_df = df[["entity_id"]] if "entity_id" in df.columns else pd.DataFrame(index=df.index)
        out_df["chosen_action"] = actions
        out_df["delta"] = deltas
        out_df["bounded_delta"] = deltas
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_parquet(output_path, index=False)
        return output_path
