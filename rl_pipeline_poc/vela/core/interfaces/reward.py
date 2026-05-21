from abc import ABC, abstractmethod
from typing import Any, Dict

from ..run_spec import RewardConfig, RunSpec


class IRewardFn(ABC):
    """Pluggable reward: template + weights from config."""

    @abstractmethod
    def compute(self, state: Dict[str, Any], action: int, next_state: Dict[str, Any], config: RewardConfig) -> float:
        """Compute reward for (state, action, next_state) using config weights."""
        pass
