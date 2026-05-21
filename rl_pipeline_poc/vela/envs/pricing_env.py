"""Configurable discrete-action pricing env for VELA (state from dataframe rows)."""
import numpy as np
from gymnasium import Env, spaces

from vela.core.run_spec import RunSpec


class PricingEnv(Env):
    """Discrete action space: delta buckets. State = feature vector; reward from config."""

    def __init__(self, df, feature_columns: list, buckets: list, reward_weights: dict, seed: int | None = None):
        super().__init__()
        self.df = df.reset_index(drop=True)
        self.feature_columns = [c for c in feature_columns if c in df.columns]
        if not self.feature_columns:
            self.feature_columns = list(df.select_dtypes(include=[np.number]).columns)[:8]
        self.buckets = np.array(buckets, dtype=np.float32)
        self.reward_weights = reward_weights
        self.n_actions = len(self.buckets)
        self.obs_dim = len(self.feature_columns)
        self.action_space = spaces.Discrete(self.n_actions)
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(self.obs_dim,), dtype=np.float32
        )
        self._idx = 0
        self._rng = np.random.default_rng(seed)

    def _get_obs(self):
        row = self.df.iloc[self._idx]
        obs = row[self.feature_columns].values.astype(np.float32)
        return np.nan_to_num(obs, nan=0.0)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        if seed is not None:
            self._rng = np.random.default_rng(seed)
        self._idx = self._rng.integers(0, len(self.df))
        return self._get_obs(), {}

    def step(self, action: int):
        delta = self.buckets[action]
        row = self.df.iloc[self._idx]
        state = row[self.feature_columns].values.astype(np.float32)
        # Simple reward: revenue component + stability (penalize large |delta|)
        revenue_term = float(state.mean()) if len(state) > 0 else 0.0
        stability_term = -abs(delta)
        r = self.reward_weights.get("revenue", 0.7) * revenue_term + self.reward_weights.get("stability", 0.3) * stability_term
        self._idx = (self._idx + 1) % len(self.df)
        next_obs = self._get_obs()
        return next_obs, float(r), False, False, {}
