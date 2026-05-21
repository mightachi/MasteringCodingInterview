"""Training Operator: A2C/PPO discrete action, config-driven."""
import json
from pathlib import Path

import pandas as pd

from vela.core.domain.artifacts import TrainMetrics
from vela.core.run_spec import RunSpec
from vela.envs import PricingEnv

try:
    from stable_baselines3 import A2C, PPO
    from stable_baselines3.common.vec_env import DummyVecEnv
    SB3_AVAILABLE = True
except ImportError:
    SB3_AVAILABLE = False


class TrainingOperator:
    """Train policy (A2C/PPO) from config; output policy_checkpoint + train_metrics.json."""

    def run(
        self,
        train_features_path: Path,
        val_features_path: Path,
        spec: RunSpec,
        output_dir: Path,
    ) -> tuple[Path, TrainMetrics]:
        if not SB3_AVAILABLE:
            raise RuntimeError("stable-baselines3 not installed. pip install stable-baselines3")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        train_df = pd.read_parquet(train_features_path)
        feature_cols = [c for c in spec.features.numeric_features if c in train_df.columns]
        if not feature_cols:
            feature_cols = list(train_df.select_dtypes(include=["number"]).columns)[:8]

        def make_env():
            return PricingEnv(
                train_df,
                feature_cols,
                spec.actions.buckets,
                spec.reward.weights,
            )

        env = DummyVecEnv([make_env])
        algo = spec.training.algorithm.upper()
        if algo == "A2C":
            model = A2C(
                "MlpPolicy",
                env,
                learning_rate=spec.training.learning_rate,
                n_steps=spec.training.n_steps,
                ent_coef=spec.training.ent_coef,
                vf_coef=spec.training.vf_coef,
                gamma=spec.training.gamma,
                policy_kwargs=spec.training.policy_kwargs or {},
            )
        elif algo == "PPO":
            model = PPO(
                "MlpPolicy",
                env,
                learning_rate=spec.training.learning_rate,
                n_steps=spec.training.n_steps,
                ent_coef=spec.training.ent_coef,
                gamma=spec.training.gamma,
                policy_kwargs=spec.training.policy_kwargs or {},
            )
        else:
            raise ValueError(f"Unsupported algorithm: {algo}")

        model.learn(total_timesteps=min(spec.training.total_timesteps, 50_000))
        policy_path = output_dir / "policy_checkpoint"
        model.save(str(policy_path))

        # Simple metrics from last rollout
        obs = env.reset()
        rewards = []
        for _ in range(100):
            action, _ = model.predict(obs)
            obs, r, _, _ = env.step(action)
            rewards.append(float(r))
        import numpy as np
        train_metrics = TrainMetrics(
            total_reward=sum(rewards),
            reward_per_episode=float(np.mean(rewards)),
            reward_std=float(np.std(rewards)) if rewards else None,
            n_episodes=len(rewards),
        )
        metrics_path = output_dir / "train_metrics.json"
        with open(metrics_path, "w") as f:
            json.dump(
                {
                    "total_reward": train_metrics.total_reward,
                    "reward_per_episode": train_metrics.reward_per_episode,
                    "reward_std": train_metrics.reward_std,
                    "n_episodes": train_metrics.n_episodes,
                },
                f,
                indent=2,
            )
        return policy_path, train_metrics
