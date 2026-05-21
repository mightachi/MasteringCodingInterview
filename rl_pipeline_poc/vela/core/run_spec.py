"""
RunSpec: config-driven specification for a VELA pipeline run.
Drives dataset window, features, reward, action buckets, algorithm, and gates.
"""
from __future__ import annotations

import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class DataConfig:
    """Data extraction and window config."""
    source_type: str  # "bigquery" | "local"
    query_or_path: str
    run_date: str
    lookback_days: int
    filters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FeatureConfig:
    """Feature preprocessing config."""
    numeric_features: List[str]
    categorical_features: List[str] = field(default_factory=list)
    target_column: Optional[str] = None
    scale: bool = True
    missing_strategy: str = "median"  # median | mean | drop


@dataclass
class ActionConfig:
    """Discrete action space (delta buckets)."""
    type: str = "discrete"
    buckets: List[float] = field(default_factory=lambda: [-0.5, -0.25, 0.0, 0.25, 0.5])
    # bucket labels for interpretability
    labels: Optional[List[str]] = None


@dataclass
class RewardConfig:
    """Pluggable reward: template + weights (no code change)."""
    template: str  # "revenue_growth" | "revenue_stability" | "custom"
    weights: Dict[str, float] = field(default_factory=lambda: {"revenue": 0.7, "stability": 0.3})
    thresholds: Dict[str, float] = field(default_factory=dict)
    normalize: bool = True


@dataclass
class TrainingConfig:
    """Algorithm and hyperparameters."""
    algorithm: str  # "A2C" | "PPO"
    total_timesteps: int = 100_000
    learning_rate: float = 0.0003
    n_steps: int = 5
    ent_coef: float = 0.01
    vf_coef: float = 0.5
    gamma: float = 0.99
    policy_kwargs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationConfig:
    """Evaluation gates and metrics."""
    min_reward_per_episode: Optional[float] = None
    max_reward_std: Optional[float] = None
    max_sign_flip_rate: Optional[float] = None
    max_avg_delta: Optional[float] = None


@dataclass
class RunSpec:
    """Full run specification: dataset, features, reward, actions, algorithm, gates."""
    project_id: str
    segment_id: str
    pipeline_type: str  # "training" | "refinement" | "inference"
    data: DataConfig
    features: FeatureConfig
    actions: ActionConfig
    reward: RewardConfig
    training: TrainingConfig
    evaluation: EvaluationConfig = field(default_factory=lambda: EvaluationConfig())
    # Refinement-specific
    warm_start_steps: Optional[int] = None
    base_policy_alias: Optional[str] = None
    # Inference-specific
    output_table_or_path: Optional[str] = None
    guardrails: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "RunSpec":
        data = d.get("data", {})
        features = d.get("features", {})
        actions = d.get("actions", {})
        reward = d.get("reward", {})
        training = d.get("training", {})
        evaluation = d.get("evaluation", {})

        return cls(
            project_id=d["project_id"],
            segment_id=d["segment_id"],
            pipeline_type=d["pipeline_type"],
            data=DataConfig(
                source_type=data.get("source_type", "local"),
                query_or_path=data.get("query_or_path", ""),
                run_date=data.get("run_date", ""),
                lookback_days=data.get("lookback_days", 28),
                filters=data.get("filters", {}),
            ),
            features=FeatureConfig(
                numeric_features=features.get("numeric_features", []),
                categorical_features=features.get("categorical_features", []),
                target_column=features.get("target_column"),
                scale=features.get("scale", True),
                missing_strategy=features.get("missing_strategy", "median"),
            ),
            actions=ActionConfig(
                type=actions.get("type", "discrete"),
                buckets=actions.get("buckets", [-0.5, -0.25, 0.0, 0.25, 0.5]),
                labels=actions.get("labels"),
            ),
            reward=RewardConfig(
                template=reward.get("template", "revenue_growth"),
                weights=reward.get("weights", {"revenue": 0.7, "stability": 0.3}),
                thresholds=reward.get("thresholds", {}),
                normalize=reward.get("normalize", True),
            ),
            training=TrainingConfig(
                algorithm=training.get("algorithm", "A2C"),
                total_timesteps=training.get("total_timesteps", 100_000),
                learning_rate=training.get("learning_rate", 0.0003),
                n_steps=training.get("n_steps", 5),
                ent_coef=training.get("ent_coef", 0.01),
                vf_coef=training.get("vf_coef", 0.5),
                gamma=training.get("gamma", 0.99),
                policy_kwargs=training.get("policy_kwargs", {}),
            ),
            evaluation=EvaluationConfig(
                min_reward_per_episode=evaluation.get("min_reward_per_episode"),
                max_reward_std=evaluation.get("max_reward_std"),
                max_sign_flip_rate=evaluation.get("max_sign_flip_rate"),
                max_avg_delta=evaluation.get("max_avg_delta"),
            ),
            warm_start_steps=d.get("warm_start_steps"),
            base_policy_alias=d.get("base_policy_alias"),
            output_table_or_path=d.get("output_table_or_path"),
            guardrails=d.get("guardrails", {}),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "segment_id": self.segment_id,
            "pipeline_type": self.pipeline_type,
            "data": {
                "source_type": self.data.source_type,
                "query_or_path": self.data.query_or_path,
                "run_date": self.data.run_date,
                "lookback_days": self.data.lookback_days,
                "filters": self.data.filters,
            },
            "features": {
                "numeric_features": self.features.numeric_features,
                "categorical_features": self.features.categorical_features,
                "target_column": self.features.target_column,
                "scale": self.features.scale,
                "missing_strategy": self.features.missing_strategy,
            },
            "actions": {
                "type": self.actions.type,
                "buckets": self.actions.buckets,
                "labels": self.actions.labels,
            },
            "reward": {
                "template": self.reward.template,
                "weights": self.reward.weights,
                "thresholds": self.reward.thresholds,
                "normalize": self.reward.normalize,
            },
            "training": {
                "algorithm": self.training.algorithm,
                "total_timesteps": self.training.total_timesteps,
                "learning_rate": self.training.learning_rate,
                "n_steps": self.training.n_steps,
                "ent_coef": self.training.ent_coef,
                "vf_coef": self.training.vf_coef,
                "gamma": self.training.gamma,
                "policy_kwargs": self.training.policy_kwargs,
            },
            "evaluation": {
                "min_reward_per_episode": self.evaluation.min_reward_per_episode,
                "max_reward_std": self.evaluation.max_reward_std,
                "max_sign_flip_rate": self.evaluation.max_sign_flip_rate,
                "max_avg_delta": self.evaluation.max_avg_delta,
            },
            "warm_start_steps": self.warm_start_steps,
            "base_policy_alias": self.base_policy_alias,
            "output_table_or_path": self.output_table_or_path,
            "guardrails": self.guardrails,
        }


def load_run_spec(path: Path) -> RunSpec:
    """Load RunSpec from YAML file."""
    with open(path) as f:
        d = yaml.safe_load(f)
    return RunSpec.from_dict(d)
