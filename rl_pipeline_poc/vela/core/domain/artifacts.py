"""Domain artifacts produced by pipeline operators."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DatasetMetadata:
    """Metadata for raw or processed dataset."""
    path: str
    run_date: str
    lookback_days: int
    num_rows: int
    num_features: int
    segment_id: str
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrainMetrics:
    """Training run metrics (reward, etc.)."""
    total_reward: float
    reward_per_episode: float
    reward_std: Optional[float] = None
    episode_length_mean: Optional[float] = None
    n_episodes: int = 0
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvalReport:
    """Evaluation & gates output: PASS/FAIL + reasons."""
    passed: bool
    reasons: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    # stability
    sign_flip_rate: Optional[float] = None
    avg_abs_delta: Optional[float] = None
    action_distribution: Optional[Dict[str, float]] = None
