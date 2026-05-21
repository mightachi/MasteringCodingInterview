"""Evaluation & Gates Operator: stability + reward -> PASS/FAIL."""
from pathlib import Path

import numpy as np
import pandas as pd

from vela.core.domain.artifacts import EvalReport, TrainMetrics
from vela.core.run_spec import RunSpec

try:
    from stable_baselines3 import A2C, PPO
    SB3_AVAILABLE = True
except ImportError:
    SB3_AVAILABLE = False


class EvaluationOperator:
    """Compute eval metrics and gate (config-driven thresholds)."""

    def run(
        self,
        policy_path: Path,
        features_path: Path,
        spec: RunSpec,
        train_metrics: TrainMetrics,
    ) -> EvalReport:
        reasons = []
        metrics = {
            "reward_per_episode": train_metrics.reward_per_episode,
            "reward_std": train_metrics.reward_std or 0,
        }

        if spec.evaluation.min_reward_per_episode is not None:
            if train_metrics.reward_per_episode < spec.evaluation.min_reward_per_episode:
                reasons.append(f"reward_per_episode {train_metrics.reward_per_episode} < {spec.evaluation.min_reward_per_episode}")
        if spec.evaluation.max_reward_std is not None and train_metrics.reward_std is not None:
            if train_metrics.reward_std > spec.evaluation.max_reward_std:
                reasons.append(f"reward_std {train_metrics.reward_std} > {spec.evaluation.max_reward_std}")

        # Optional: run policy on val set to get action distribution / sign flips
        sign_flip_rate = None
        avg_abs_delta = None
        action_dist = None
        if SB3_AVAILABLE and features_path.exists():
            df = pd.read_parquet(features_path)
            cols = [c for c in spec.features.numeric_features if c in df.columns]
            if not cols:
                cols = list(df.select_dtypes(include=["number"]).columns)[:8]
            algo = spec.training.algorithm.upper()
            model = PPO.load(str(policy_path)) if algo == "PPO" else A2C.load(str(policy_path))
            actions = []
            for i in range(min(500, len(df))):
                obs = df.iloc[i][cols].values.astype(np.float32).reshape(1, -1)
                a, _ = model.predict(obs)
                actions.append(int(a[0]))
            deltas = [spec.actions.buckets[a] for a in actions]
            action_dist = {}
            for a in set(actions):
                action_dist[str(spec.actions.buckets[a])] = actions.count(a) / len(actions)
            avg_abs_delta = float(np.mean(np.abs(deltas)))
            sign_changes = sum(1 for i in range(1, len(deltas)) if (deltas[i] * deltas[i - 1]) < 0)
            sign_flip_rate = sign_changes / max(1, len(deltas) - 1)
            metrics["sign_flip_rate"] = sign_flip_rate
            metrics["avg_abs_delta"] = avg_abs_delta
            if spec.evaluation.max_sign_flip_rate is not None and sign_flip_rate > spec.evaluation.max_sign_flip_rate:
                reasons.append(f"sign_flip_rate {sign_flip_rate} > {spec.evaluation.max_sign_flip_rate}")
            if spec.evaluation.max_avg_delta is not None and avg_abs_delta > spec.evaluation.max_avg_delta:
                reasons.append(f"avg_abs_delta {avg_abs_delta} > {spec.evaluation.max_avg_delta}")

        passed = len(reasons) == 0
        return EvalReport(
            passed=passed,
            reasons=reasons,
            metrics=metrics,
            sign_flip_rate=sign_flip_rate,
            avg_abs_delta=avg_abs_delta,
            action_distribution=action_dist,
        )
