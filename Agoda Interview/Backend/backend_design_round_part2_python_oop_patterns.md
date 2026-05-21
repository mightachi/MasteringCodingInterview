# 🐍 Agoda Backend Design Round — Part 2: Python OOP, Design Patterns & API Design

## 📋 Table of Contents
1. [Python OOP Deep Dive — Expert Level](#1-python-oop)
2. [Design Patterns for ML Systems (with Code)](#2-design-patterns)
3. [SOLID Principles in ML Engineering](#3-solid)
4. [FastAPI / API Design Best Practices](#4-api-design)
5. [Code Review — What Agoda Looks For](#5-code-review)
6. [Mock Code Review Exercise](#6-mock-review)

---

## 1. Python OOP Deep Dive — Expert Level <a name="1-python-oop"></a>

### 🎯 Why This Matters for Agoda

Agoda's JD explicitly states: *"Expert level understanding of Python with design patterns and object-oriented programming."*

In the Backend Design Round, you may be asked to:
- Design a class hierarchy for an ML pipeline
- Review and refactor existing Python code
- Implement a component using proper OOP principles

### 1.1 Core OOP Concepts — The "WHY"

```python
# ==========================================================
# ENCAPSULATION: Hide complexity, expose clean interfaces
# ==========================================================
# WHY? In ML systems, encapsulation prevents accidental 
# modification of model state and keeps feature logic contained.

class ModelServer:
    """Encapsulated model serving component."""
    
    def __init__(self, model_path: str, config: dict):
        self._model = self._load_model(model_path)  # Private: internal state
        self._config = config                         # Private: configuration
        self._request_count = 0                       # Private: metrics
    
    def predict(self, features: dict) -> float:
        """Public interface — clean and simple."""
        self._request_count += 1
        preprocessed = self._preprocess(features)
        return self._model.predict(preprocessed)
    
    def _load_model(self, path: str):
        """Private: model loading details hidden from consumers."""
        pass
    
    def _preprocess(self, features: dict) -> list:
        """Private: preprocessing logic hidden from consumers."""
        pass
    
    @property
    def request_count(self) -> int:
        """Read-only access to request count (no setter)."""
        return self._request_count


# ==========================================================
# ABSTRACTION: Define WHAT without HOW
# ==========================================================
# WHY? Different ML models (XGBoost, LightGBM, NN) have different
# interfaces, but consumers shouldn't care about implementation.

from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseModel(ABC):
    """Abstract base class defining the contract for ALL ML models."""
    
    @abstractmethod
    def load(self, model_path: str) -> None:
        """Load model from storage."""
        pass
    
    @abstractmethod
    def predict(self, features: Dict[str, Any]) -> float:
        """Run inference on input features."""
        pass
    
    @abstractmethod
    def get_feature_names(self) -> List[str]:
        """Return list of expected feature names."""
        pass
    
    def validate_features(self, features: Dict[str, Any]) -> bool:
        """Concrete method: shared validation logic."""
        expected = set(self.get_feature_names())
        provided = set(features.keys())
        missing = expected - provided
        if missing:
            raise ValueError(f"Missing features: {missing}")
        return True


# ==========================================================
# INHERITANCE vs COMPOSITION
# ==========================================================
# RULE OF THUMB: "Favor composition over inheritance"
# WHY? Inheritance creates tight coupling. Composition is more flexible.

# BAD: Deep inheritance hierarchy
class BasePredictor:
    pass
class TreePredictor(BasePredictor):       # inherits BasePredictor
    pass
class GBDTPredictor(TreePredictor):       # inherits TreePredictor
    pass
class XGBoostPredictor(GBDTPredictor):    # 3 levels deep = nightmare!
    pass

# GOOD: Composition — "has-a" relationships
class PredictionService:
    """Uses composition: 'has-a' model, 'has-a' preprocessor, 'has-a' logger."""
    
    def __init__(self, model: BaseModel, preprocessor, logger):
        self.model = model                # Injected dependency
        self.preprocessor = preprocessor  # Injected dependency
        self.logger = logger              # Injected dependency
    
    def predict(self, raw_input: dict) -> float:
        self.logger.log("Prediction request received")
        features = self.preprocessor.transform(raw_input)
        self.model.validate_features(features)
        result = self.model.predict(features)
        self.logger.log(f"Prediction: {result}")
        return result


# ==========================================================
# POLYMORPHISM: Same interface, different behavior
# ==========================================================
# WHY? In ML, you swap models (XGBoost → LightGBM → NN) 
# without changing the serving code.

class XGBoostModel(BaseModel):
    def load(self, model_path: str) -> None:
        import xgboost as xgb
        self._model = xgb.Booster()
        self._model.load_model(model_path)
    
    def predict(self, features: Dict[str, Any]) -> float:
        dmatrix = self._to_dmatrix(features)
        return float(self._model.predict(dmatrix)[0])
    
    def get_feature_names(self) -> List[str]:
        return ["price", "star_rating", "review_score", "location_score"]
    
    def _to_dmatrix(self, features):
        pass

class LightGBMModel(BaseModel):
    def load(self, model_path: str) -> None:
        import lightgbm as lgb
        self._model = lgb.Booster(model_file=model_path)
    
    def predict(self, features: Dict[str, Any]) -> float:
        return float(self._model.predict([list(features.values())])[0])
    
    def get_feature_names(self) -> List[str]:
        return ["price", "star_rating", "review_score", "location_score"]

# Polymorphism in action — same code, different models:
def serve_predictions(model: BaseModel, requests: list):
    """Works with ANY model that implements BaseModel."""
    return [model.predict(req) for req in requests]

# Swap models without changing serving code:
# serve_predictions(XGBoostModel(), requests)
# serve_predictions(LightGBMModel(), requests)
```

### 1.2 Advanced Python Concepts

```python
# ==========================================================
# DUNDER (MAGIC) METHODS — Make objects Pythonic
# ==========================================================

class FeatureVector:
    """Custom feature vector with rich Python integration."""
    
    def __init__(self, name: str, values: dict):
        self.name = name
        self.values = values
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"FeatureVector(name='{self.name}', dim={len(self.values)})"
    
    def __str__(self) -> str:
        """User-friendly string."""
        return f"Features[{self.name}]: {list(self.values.keys())}"
    
    def __len__(self) -> int:
        """len(feature_vector) returns number of features."""
        return len(self.values)
    
    def __getitem__(self, key: str) -> float:
        """feature_vector['price'] returns value."""
        return self.values[key]
    
    def __setitem__(self, key: str, value: float):
        """feature_vector['price'] = 99.0 sets value."""
        self.values[key] = value
    
    def __contains__(self, key: str) -> bool:
        """'price' in feature_vector checks existence."""
        return key in self.values
    
    def __add__(self, other: 'FeatureVector') -> 'FeatureVector':
        """Merge two feature vectors: fv1 + fv2."""
        merged = {**self.values, **other.values}
        return FeatureVector(f"{self.name}+{other.name}", merged)
    
    def __eq__(self, other: 'FeatureVector') -> bool:
        """Compare feature vectors."""
        return self.values == other.values
    
    def __hash__(self) -> int:
        """Make hashable for use in sets/dicts."""
        return hash(frozenset(self.values.items()))
    
    def __call__(self, model) -> float:
        """Make callable: fv(model) → prediction."""
        return model.predict(self.values)


# Usage:
fv_user = FeatureVector("user", {"age": 30, "loyalty_tier": 3})
fv_hotel = FeatureVector("hotel", {"price": 150, "stars": 4})

combined = fv_user + fv_hotel           # __add__
print(len(combined))                     # __len__ → 4
print("price" in combined)              # __contains__ → True
print(combined["price"])                # __getitem__ → 150


# ==========================================================
# DECORATORS — Cross-cutting concerns
# ==========================================================
import time
import functools
import logging

logger = logging.getLogger(__name__)

def retry(max_attempts: int = 3, backoff: float = 1.0):
    """Decorator: retry failed function calls with exponential backoff."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    wait = backoff * (2 ** attempt)
                    logger.warning(f"Attempt {attempt+1} failed: {e}. Retrying in {wait}s")
                    time.sleep(wait)
        return wrapper
    return decorator

def log_execution(func):
    """Decorator: log function entry, exit, and duration."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"→ {func.__name__} called")
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"← {func.__name__} completed in {duration:.3f}s")
        return result
    return wrapper

def validate_input(schema: dict):
    """Decorator: validate function inputs against schema."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Validate kwargs against schema
            for key, expected_type in schema.items():
                if key in kwargs:
                    if not isinstance(kwargs[key], expected_type):
                        raise TypeError(f"{key} must be {expected_type.__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage with ML service:
class FeatureService:
    
    @retry(max_attempts=3, backoff=0.5)
    @log_execution
    def fetch_features(self, entity_id: str) -> dict:
        """Fetch features from store with retry and logging."""
        return self._store.get_online_features(entity_id)


# ==========================================================
# CLASS METHODS vs STATIC METHODS vs INSTANCE METHODS
# ==========================================================

class MLModel:
    """Demonstrating method types."""
    
    _registry = {}  # Class-level registry
    
    def __init__(self, name: str, version: str):
        self.name = name          # Instance attribute
        self.version = version    # Instance attribute
    
    # Instance method: operates on specific model instance
    def predict(self, features: dict) -> float:
        """Instance method — needs self (the specific model instance)."""
        return self._run_inference(features)
    
    # Class method: operates on the class itself (factory pattern)
    @classmethod
    def from_registry(cls, model_name: str) -> 'MLModel':
        """Class method — factory to create model from registry."""
        config = cls._registry.get(model_name)
        if not config:
            raise ValueError(f"Model '{model_name}' not found in registry")
        return cls(name=config["name"], version=config["version"])
    
    @classmethod
    def register(cls, name: str, config: dict):
        """Class method — register a new model configuration."""
        cls._registry[name] = config
    
    # Static method: utility, doesn't need class or instance
    @staticmethod
    def validate_version(version: str) -> bool:
        """Static method — utility function, no class/instance needed."""
        parts = version.split(".")
        return len(parts) == 3 and all(p.isdigit() for p in parts)

# Usage:
MLModel.register("ranking_v1", {"name": "hotel_ranker", "version": "1.0.0"})
model = MLModel.from_registry("ranking_v1")   # classmethod as factory
model.predict({"price": 100})                  # instance method
MLModel.validate_version("1.0.0")              # static method (no instance needed)


# ==========================================================
# CONTEXT MANAGERS — Resource management
# ==========================================================

class ModelContext:
    """Context manager for model lifecycle."""
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
    
    def __enter__(self):
        """Load model when entering context."""
        print(f"Loading model from {self.model_path}")
        self.model = self._load(self.model_path)
        return self.model
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup when exiting context."""
        print("Releasing model resources")
        self.model = None
        return False  # Don't suppress exceptions
    
    def _load(self, path):
        pass

# Usage:
# with ModelContext("models/ranker_v1.onnx") as model:
#     predictions = model.predict(features)
# Model automatically cleaned up after 'with' block


# ==========================================================
# METHOD RESOLUTION ORDER (MRO) & super()
# ==========================================================

class DataSource(ABC):
    """Base class for data sources."""
    
    def connect(self):
        print("DataSource: establishing connection")

class CacheMixin:
    """Mixin: adds caching capability."""
    
    def connect(self):
        print("CacheMixin: warming up cache")
        super().connect()  # Calls next in MRO chain

class RetryMixin:
    """Mixin: adds retry capability."""
    
    def connect(self):
        print("RetryMixin: setting up retry logic")
        super().connect()  # Calls next in MRO chain

class ProductionDataSource(RetryMixin, CacheMixin, DataSource):
    """Combines retry + cache + base data source."""
    
    def connect(self):
        print("ProductionDataSource: connecting...")
        super().connect()  # Follows MRO chain

# MRO: ProductionDataSource → RetryMixin → CacheMixin → DataSource
# print(ProductionDataSource.__mro__)

# When .connect() is called:
# 1. ProductionDataSource.connect()
# 2. RetryMixin.connect()
# 3. CacheMixin.connect()
# 4. DataSource.connect()
```

---

## 2. Design Patterns for ML Systems <a name="2-design-patterns"></a>

### 🎯 Patterns You MUST Know for Agoda

```python
# ==========================================================
# PATTERN 1: STRATEGY — Swap algorithms at runtime
# ==========================================================
# USE CASE: Different ranking algorithms for different markets
# or A/B testing between models

from abc import ABC, abstractmethod
from typing import Protocol

class RankingStrategy(Protocol):
    """Protocol defining ranking strategy interface."""
    
    def rank(self, candidates: list, context: dict) -> list:
        """Rank candidates based on context."""
        ...

class MLRanking:
    """ML-based ranking using trained model."""
    
    def __init__(self, model):
        self.model = model
    
    def rank(self, candidates: list, context: dict) -> list:
        scores = self.model.predict_batch(candidates, context)
        return sorted(zip(candidates, scores), key=lambda x: -x[1])

class PopularityRanking:
    """Fallback: rank by popularity score."""
    
    def rank(self, candidates: list, context: dict) -> list:
        return sorted(candidates, key=lambda h: -h.popularity_score)

class PriceRanking:
    """Simple price-based ranking."""
    
    def rank(self, candidates: list, context: dict) -> list:
        return sorted(candidates, key=lambda h: h.price)

class HotelSearchService:
    """Service that uses Strategy pattern for flexible ranking."""
    
    def __init__(self, ranking_strategy: RankingStrategy):
        self._strategy = ranking_strategy
    
    def set_strategy(self, strategy: RankingStrategy):
        """Swap ranking strategy at runtime (A/B testing)."""
        self._strategy = strategy
    
    def search(self, query: dict) -> list:
        candidates = self._get_candidates(query)
        return self._strategy.rank(candidates, query)
    
    def _get_candidates(self, query):
        pass

# Usage:
# For ML-powered search:
# service = HotelSearchService(MLRanking(trained_model))

# For A/B test with simple ranking:
# service.set_strategy(PopularityRanking())

# Fallback when ML is down:
# service.set_strategy(PopularityRanking())


# ==========================================================
# PATTERN 2: FACTORY — Create objects without specifying exact class
# ==========================================================
# USE CASE: Loading different model types based on configuration

class ModelFactory:
    """Factory for creating ML model instances based on type."""
    
    _registry = {}
    
    @classmethod
    def register(cls, model_type: str, model_class):
        """Register a model class."""
        cls._registry[model_type] = model_class
    
    @classmethod
    def create(cls, model_type: str, config: dict) -> BaseModel:
        """Create model instance by type."""
        model_class = cls._registry.get(model_type)
        if not model_class:
            raise ValueError(f"Unknown model type: {model_type}")
        model = model_class()
        model.load(config["model_path"])
        return model

# Register models
ModelFactory.register("xgboost", XGBoostModel)
ModelFactory.register("lightgbm", LightGBMModel)

# Create model based on config (could come from MLflow registry)
config = {"model_type": "xgboost", "model_path": "models/ranker_v2.bin"}
model = ModelFactory.create(config["model_type"], config)


# ==========================================================
# PATTERN 3: REPOSITORY — Decouple data access from business logic
# ==========================================================
# USE CASE: Feature retrieval, model metadata storage
# WHY? Makes testing easy (mock the repository)

class FeatureRepository(ABC):
    """Abstract repository for feature storage."""
    
    @abstractmethod
    def get_features(self, entity_id: str, feature_names: list) -> dict:
        pass
    
    @abstractmethod
    def save_features(self, entity_id: str, features: dict) -> None:
        pass

class RedisFeatureRepository(FeatureRepository):
    """Redis-backed feature repository for online serving."""
    
    def __init__(self, redis_client):
        self._client = redis_client
    
    def get_features(self, entity_id: str, feature_names: list) -> dict:
        pipe = self._client.pipeline()
        for name in feature_names:
            pipe.hget(f"features:{entity_id}", name)
        values = pipe.execute()
        return dict(zip(feature_names, values))
    
    def save_features(self, entity_id: str, features: dict) -> None:
        self._client.hset(f"features:{entity_id}", mapping=features)

class MongoFeatureRepository(FeatureRepository):
    """MongoDB-backed feature repository for batch operations."""
    
    def __init__(self, collection):
        self._collection = collection
    
    def get_features(self, entity_id: str, feature_names: list) -> dict:
        projection = {name: 1 for name in feature_names}
        doc = self._collection.find_one({"entity_id": entity_id}, projection)
        return doc or {}
    
    def save_features(self, entity_id: str, features: dict) -> None:
        self._collection.update_one(
            {"entity_id": entity_id},
            {"$set": features},
            upsert=True
        )

# Testing is easy — create a mock repository:
class InMemoryFeatureRepository(FeatureRepository):
    """In-memory repository for unit testing."""
    
    def __init__(self):
        self._store = {}
    
    def get_features(self, entity_id, feature_names):
        return {k: self._store.get(entity_id, {}).get(k) for k in feature_names}
    
    def save_features(self, entity_id, features):
        self._store.setdefault(entity_id, {}).update(features)


# ==========================================================
# PATTERN 4: OBSERVER / PUB-SUB — Event-driven monitoring
# ==========================================================
# USE CASE: Model performance monitoring, alerting

from typing import Callable

class EventBus:
    """Simple event bus for ML pipeline events."""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, handler: Callable):
        """Register a handler for an event type."""
        self._subscribers.setdefault(event_type, []).append(handler)
    
    def publish(self, event_type: str, data: dict):
        """Publish event to all subscribers."""
        for handler in self._subscribers.get(event_type, []):
            handler(data)

class DriftDetector:
    """Subscribes to prediction events, detects feature drift."""
    
    def __init__(self, event_bus: EventBus, threshold: float = 0.2):
        self.threshold = threshold
        event_bus.subscribe("prediction_made", self.check_drift)
    
    def check_drift(self, data: dict):
        psi = self._compute_psi(data["features"])
        if psi > self.threshold:
            print(f"⚠️ Feature drift detected! PSI={psi:.3f}")

class LatencyTracker:
    """Subscribes to prediction events, tracks latency."""
    
    def __init__(self, event_bus: EventBus, sla_ms: float = 100):
        self.sla_ms = sla_ms
        event_bus.subscribe("prediction_made", self.track_latency)
    
    def track_latency(self, data: dict):
        if data["latency_ms"] > self.sla_ms:
            print(f"⚠️ SLA violation! Latency={data['latency_ms']:.1f}ms > {self.sla_ms}ms")

# Setup:
bus = EventBus()
drift_detector = DriftDetector(bus)
latency_tracker = LatencyTracker(bus)

# When a prediction is made:
# bus.publish("prediction_made", {
#     "features": {...},
#     "prediction": 0.85,
#     "latency_ms": 45.2
# })


# ==========================================================
# PATTERN 5: TEMPLATE METHOD — Define pipeline skeleton
# ==========================================================
# USE CASE: ML training pipeline with customizable steps

class MLPipeline(ABC):
    """Template Method: defines the skeleton of ML pipeline.
    Subclasses override specific steps.
    """
    
    def run(self, data_config: dict):
        """Template method — controls the algorithm."""
        data = self.load_data(data_config)
        features = self.engineer_features(data)
        X_train, X_test, y_train, y_test = self.split_data(features)
        model = self.train_model(X_train, y_train)
        metrics = self.evaluate_model(model, X_test, y_test)
        self.log_experiment(model, metrics)
        if self.should_deploy(metrics):
            self.deploy_model(model)
        return model, metrics
    
    @abstractmethod
    def load_data(self, config): pass
    
    @abstractmethod
    def engineer_features(self, data): pass
    
    def split_data(self, features):
        """Default split — can be overridden."""
        from sklearn.model_selection import train_test_split
        X = features.drop("target", axis=1)
        y = features["target"]
        return train_test_split(X, y, test_size=0.2, random_state=42)
    
    @abstractmethod
    def train_model(self, X_train, y_train): pass
    
    @abstractmethod
    def evaluate_model(self, model, X_test, y_test): pass
    
    def log_experiment(self, model, metrics):
        """Default logging — MLflow."""
        print(f"Logging metrics: {metrics}")
    
    def should_deploy(self, metrics) -> bool:
        """Default deploy check — override for custom logic."""
        return metrics.get("ndcg_10", 0) > 0.85
    
    def deploy_model(self, model):
        """Default deployment."""
        print("Deploying model to production...")


class HotelRankingPipeline(MLPipeline):
    """Concrete pipeline for hotel ranking model."""
    
    def load_data(self, config):
        # Load from BigQuery
        pass
    
    def engineer_features(self, data):
        # Feature engineering specific to hotel ranking
        pass
    
    def train_model(self, X_train, y_train):
        # Train LightGBM with LambdaRank
        pass
    
    def evaluate_model(self, model, X_test, y_test):
        # Evaluate with NDCG@10, MAP@10
        return {"ndcg_10": 0.88, "map_10": 0.75}


class PricingModelPipeline(MLPipeline):
    """Concrete pipeline for pricing model — different steps."""
    
    def load_data(self, config):
        # Load from different BigQuery tables
        pass
    
    def engineer_features(self, data):
        # Pricing-specific features (seasonality, competitors)
        pass
    
    def train_model(self, X_train, y_train):
        # Train XGBoost for click probability
        pass
    
    def evaluate_model(self, model, X_test, y_test):
        # Evaluate with AUC-ROC, calibration
        return {"auc_roc": 0.92, "calibration_error": 0.02}
    
    def should_deploy(self, metrics) -> bool:
        """Custom deploy gate for pricing model."""
        return metrics["auc_roc"] > 0.90 and metrics["calibration_error"] < 0.05


# ==========================================================
# PATTERN 6: BUILDER — Complex object construction
# ==========================================================
# USE CASE: Building complex ML pipeline configurations

class PipelineConfig:
    """Complex pipeline configuration built step-by-step."""
    
    def __init__(self):
        self.data_source = None
        self.features = []
        self.model_type = None
        self.hyperparams = {}
        self.deployment_config = {}
        self.monitoring_config = {}

class PipelineBuilder:
    """Builder for constructing complex pipeline configurations."""
    
    def __init__(self):
        self._config = PipelineConfig()
    
    def with_data_source(self, source: str, query: str) -> 'PipelineBuilder':
        self._config.data_source = {"source": source, "query": query}
        return self
    
    def with_features(self, features: list) -> 'PipelineBuilder':
        self._config.features.extend(features)
        return self
    
    def with_model(self, model_type: str, **hyperparams) -> 'PipelineBuilder':
        self._config.model_type = model_type
        self._config.hyperparams = hyperparams
        return self
    
    def with_deployment(self, strategy: str, **kwargs) -> 'PipelineBuilder':
        self._config.deployment_config = {"strategy": strategy, **kwargs}
        return self
    
    def with_monitoring(self, drift_threshold: float, sla_ms: float) -> 'PipelineBuilder':
        self._config.monitoring_config = {
            "drift_threshold": drift_threshold,
            "sla_ms": sla_ms,
        }
        return self
    
    def build(self) -> PipelineConfig:
        # Validate configuration
        if not self._config.data_source:
            raise ValueError("Data source is required")
        if not self._config.model_type:
            raise ValueError("Model type is required")
        return self._config

# Usage — fluent, readable API:
config = (
    PipelineBuilder()
    .with_data_source("bigquery", "SELECT * FROM hotel_features")
    .with_features(["price", "star_rating", "review_score", "location_score"])
    .with_model("lightgbm", n_estimators=500, learning_rate=0.01)
    .with_deployment("canary", initial_percentage=5)
    .with_monitoring(drift_threshold=0.2, sla_ms=100)
    .build()
)
```

---

## 3. SOLID Principles in ML Engineering <a name="3-solid"></a>

```python
# ==========================================================
# S — Single Responsibility Principle
# ==========================================================
# Each class should have ONE reason to change.
# BAD: One class does everything
# GOOD: Separate concerns

# BAD ❌
class MonolithicMLService:
    def load_data(self): ...
    def engineer_features(self): ...
    def train_model(self): ...
    def serve_predictions(self): ...
    def monitor_model(self): ...
    def send_alerts(self): ...

# GOOD ✅
class DataLoader:
    """Responsible ONLY for loading data."""
    def load(self, config): ...

class FeatureEngineer:
    """Responsible ONLY for feature transformation."""
    def transform(self, data): ...

class ModelTrainer:
    """Responsible ONLY for model training."""
    def train(self, features, labels): ...

class PredictionServer:
    """Responsible ONLY for serving predictions."""
    def predict(self, features): ...

class ModelMonitor:
    """Responsible ONLY for monitoring."""
    def check_drift(self, predictions): ...


# ==========================================================
# O — Open/Closed Principle
# ==========================================================
# Open for extension, closed for modification.
# Add new model types without changing existing code.

# GOOD: Add new models without modifying existing code
class ONNXModel(BaseModel):
    """New model type — extends the system without modifying existing code."""
    def load(self, model_path):
        import onnxruntime as ort
        self._session = ort.InferenceSession(model_path)
    
    def predict(self, features):
        input_name = self._session.get_inputs()[0].name
        result = self._session.run(None, {input_name: features})
        return float(result[0][0])
    
    def get_feature_names(self):
        return ["price", "stars", "reviews", "location"]
    
# Register and use — ZERO changes to existing code!
ModelFactory.register("onnx", ONNXModel)


# ==========================================================
# L — Liskov Substitution Principle
# ==========================================================
# Subtypes must be substitutable for their base types.

# GOOD: Any BaseModel subclass can replace another
def run_ab_test(model_a: BaseModel, model_b: BaseModel, test_data: list):
    """Works with ANY BaseModel implementation."""
    results_a = [model_a.predict(d) for d in test_data]
    results_b = [model_b.predict(d) for d in test_data]
    return compare_metrics(results_a, results_b)


# ==========================================================
# I — Interface Segregation Principle
# ==========================================================
# Don't force classes to implement interfaces they don't use.

# BAD: One fat interface ❌
class MLServiceInterface(ABC):
    @abstractmethod
    def train(self): ...
    @abstractmethod
    def predict(self): ...
    @abstractmethod
    def explain(self): ...      # Not all models support explanations!
    @abstractmethod
    def retrain(self): ...

# GOOD: Segregated interfaces ✅
class Trainable(ABC):
    @abstractmethod
    def train(self, data): ...

class Predictable(ABC):
    @abstractmethod
    def predict(self, features): ...

class Explainable(ABC):
    @abstractmethod
    def explain(self, prediction): ...

# Models only implement what they support:
class SimpleLinearModel(Trainable, Predictable):
    def train(self, data): ...
    def predict(self, features): ...
    # No explain() — linear model is simple enough

class XGBoostWithSHAP(Trainable, Predictable, Explainable):
    def train(self, data): ...
    def predict(self, features): ...
    def explain(self, prediction): ...  # SHAP values


# ==========================================================
# D — Dependency Inversion Principle
# ==========================================================
# High-level modules should not depend on low-level modules.
# Both should depend on abstractions.

# BAD: Direct dependency ❌
class RankingService:
    def __init__(self):
        self.model = XGBoostModel()  # Tightly coupled!
        self.store = RedisFeatureRepository()  # Tightly coupled!

# GOOD: Depend on abstractions ✅
class RankingService:
    def __init__(self, model: BaseModel, store: FeatureRepository):
        self.model = model   # Injected, depends on abstraction
        self.store = store   # Injected, depends on abstraction
    
    def rank(self, query):
        features = self.store.get_features(query.user_id, self.model.get_feature_names())
        return self.model.predict(features)

# Easy to swap implementations:
# Production:
# service = RankingService(XGBoostModel(), RedisFeatureRepository(redis_client))

# Testing:
# service = RankingService(MockModel(), InMemoryFeatureRepository())
```

---

## 4. FastAPI / API Design Best Practices <a name="4-api-design"></a>

```python
# ==========================================================
# FASTAPI SERVICE FOR ML SERVING
# ==========================================================

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel as PydanticModel, Field, validator
from typing import Optional
from enum import Enum
import time

app = FastAPI(
    title="Hotel Ranking ML Service",
    version="2.0.0",
    description="Real-time hotel ranking powered by ML"
)

# ==========================================================
# REQUEST/RESPONSE MODELS (Pydantic)
# ==========================================================

class SortOrder(str, Enum):
    RELEVANCE = "relevance"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    RATING = "rating"

class SearchRequest(PydanticModel):
    """Validated search request — Pydantic handles validation."""
    
    destination: str = Field(..., min_length=1, max_length=100,
                              description="City or region name")
    check_in: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$",
                           description="Check-in date (YYYY-MM-DD)")
    check_out: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$",
                            description="Check-out date (YYYY-MM-DD)")
    num_guests: int = Field(ge=1, le=10, default=2)
    page: int = Field(ge=1, default=1)
    page_size: int = Field(ge=1, le=50, default=20)
    sort_by: SortOrder = SortOrder.RELEVANCE
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    min_stars: Optional[int] = Field(None, ge=1, le=5)
    
    @validator("check_out")
    def check_out_after_check_in(cls, v, values):
        if "check_in" in values and v <= values["check_in"]:
            raise ValueError("check_out must be after check_in")
        return v

class HotelResult(PydanticModel):
    hotel_id: str
    name: str
    star_rating: int
    review_score: float
    price_per_night: float
    ml_score: float
    is_sponsored: bool = False

class SearchResponse(PydanticModel):
    results: list[HotelResult]
    total_count: int
    page: int
    page_size: int
    model_version: str
    latency_ms: float

class HealthResponse(PydanticModel):
    status: str
    model_loaded: bool
    model_version: str
    uptime_seconds: float


# ==========================================================
# API ENDPOINTS
# ==========================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for load balancer."""
    return HealthResponse(
        status="healthy",
        model_loaded=True,
        model_version="ranking_v2.1.0",
        uptime_seconds=time.time() - app.state.start_time
    )

@app.post("/v1/search/rank", response_model=SearchResponse)
async def rank_hotels(
    request: SearchRequest,
    background_tasks: BackgroundTasks
):
    """
    Rank hotels for a search query.
    
    Pipeline:
    1. Generate candidates from search index
    2. Filter by availability
    3. Score with ML model
    4. Apply business rules
    5. Return paginated results
    """
    start = time.time()
    
    try:
        # Step 1-5: Ranking pipeline
        results = await ranking_service.rank(request)
        
        # Pagination
        offset = (request.page - 1) * request.page_size
        page_results = results[offset:offset + request.page_size]
        
        latency = (time.time() - start) * 1000
        
        # Async logging for latency tracking
        background_tasks.add_task(
            log_prediction,
            request=request,
            results=page_results,
            latency_ms=latency
        )
        
        return SearchResponse(
            results=page_results,
            total_count=len(results),
            page=request.page,
            page_size=request.page_size,
            model_version="ranking_v2.1.0",
            latency_ms=round(latency, 2)
        )
    
    except Exception as e:
        # Fallback to rule-based ranking
        logger.error(f"ML ranking failed: {e}, falling back to rules")
        results = fallback_ranking(request)
        return SearchResponse(
            results=results,
            total_count=len(results),
            page=request.page,
            page_size=request.page_size,
            model_version="fallback_v1",
            latency_ms=round((time.time() - start) * 1000, 2)
        )


@app.post("/v1/predict/click-probability")
async def predict_click_probability(
    hotel_id: str,
    user_id: str,
    context: dict
):
    """Predict P(click) for a hotel-user pair."""
    features = await feature_store.get_features(
        entities={"hotel_id": hotel_id, "user_id": user_id},
        feature_names=click_model.get_feature_names()
    )
    probability = click_model.predict(features)
    return {"hotel_id": hotel_id, "click_probability": probability}


# ==========================================================
# MIDDLEWARE & ERROR HANDLING
# ==========================================================

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Track request timing for all endpoints."""
    
    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        # Alert on SLA violations
        if duration > 0.2:  # 200ms SLA
            logger.warning(f"SLA violation: {request.url.path} took {duration:.3f}s")
        
        return response

app.add_middleware(RequestTimingMiddleware)


# ==========================================================
# DEPENDENCY INJECTION
# ==========================================================

def get_model():
    """Dependency: provides the current ML model."""
    return app.state.model

def get_feature_store():
    """Dependency: provides feature store client."""
    return app.state.feature_store

@app.post("/v1/predict")
async def predict(
    features: dict,
    model: BaseModel = Depends(get_model),
    store: FeatureRepository = Depends(get_feature_store)
):
    """Endpoint with dependency injection — easy to test."""
    enriched = store.get_features(features["entity_id"], model.get_feature_names())
    return {"prediction": model.predict(enriched)}
```

### API Design Best Practices Checklist

```python
api_best_practices = {
    "Versioning": "Always version your API (/v1/, /v2/)",
    "Pagination": "Cursor-based for large result sets, offset-based for search",
    "Idempotency": "POST requests should be idempotent (use idempotency keys)",
    "Rate Limiting": "Protect services from abuse (429 Too Many Requests)",
    "Error Format": {
        "standard": {
            "error_code": "HOTEL_NOT_FOUND",
            "message": "Hotel with ID 'H12345' does not exist",
            "details": {},
            "request_id": "req-abc-123"
        }
    },
    "Authentication": "JWT tokens for service-to-service, API keys for external",
    "Caching": "Cache-Control headers, ETag for conditional requests",
    "Compression": "gzip/brotli for response compression",
    "Documentation": "Auto-generated OpenAPI/Swagger docs (FastAPI does this)",
}
```

---

## 5. Code Review — What Agoda Looks For <a name="5-code-review"></a>

### 🎯 Code Review Evaluation Criteria

```python
# In Agoda's backend design round, you may be asked to:
# 1. Review a code snippet and identify issues
# 2. Refactor code to follow best practices
# 3. Design a class structure for a given problem

code_review_checklist = {
    "Clean Code": {
        "Naming":         "Descriptive variable/function/class names",
        "Single Purpose": "Functions do ONE thing",
        "DRY":           "Don't Repeat Yourself — extract common logic",
        "Comments":       "WHY, not WHAT (code should be self-documenting)",
    },
    "Error Handling": {
        "Specific Exceptions": "Catch specific exceptions, not bare except",
        "Graceful Degradation":"Have fallback behavior on failure",
        "Logging":             "Log errors with context (request_id, user_id)",
        "Custom Exceptions":   "Define domain-specific exceptions",
    },
    "Design Patterns": {
        "SOLID":          "Follow SOLID principles",
        "Composition":    "Favor composition over inheritance",
        "DI":             "Use dependency injection for testability",
    },
    "Testing": {
        "Unit Tests":     "Test individual components in isolation",
        "Integration":    "Test component interactions",
        "Mocking":        "Use mocks for external dependencies",
        "Edge Cases":     "Test boundary conditions, None values, empty lists",
    },
    "Performance": {
        "Algorithmic":    "Appropriate data structures and algorithms",
        "Database":       "Efficient queries, proper indexing",
        "Caching":        "Cache expensive computations",
        "Async":          "Use async for I/O-bound operations",
    },
}
```

---

## 6. Mock Code Review Exercise <a name="6-mock-review"></a>

### 🎯 Exercise: Review and Refactor This Code

```python
# ==========================================================
# BEFORE: Code with MANY issues (identify them all!)
# ==========================================================

import requests
import json

class predictor:
    def __init__(self):
        self.m = None
        self.d = {}
    
    def load(self, p):
        try:
            f = open(p, 'rb')
            import pickle
            self.m = pickle.load(f)
        except:
            print("error")
    
    def pred(self, data):
        features = []
        features.append(data['price'])
        features.append(data['stars'])
        features.append(data['reviews'])
        features.append(data['loc'])
        
        r = self.m.predict([features])
        
        # save to db
        url = "http://db-service:8080/save"
        requests.post(url, json={'pred': r[0], 'features': str(features)})
        
        return r[0]
    
    def pred_batch(self, data_list):
        results = []
        for d in data_list:
            r = self.pred(d)
            results.append(r)
        return results


# ==========================================================
# ISSUES IDENTIFIED (Code Review)
# ==========================================================

issues = {
    "1. Naming": [
        "Class name 'predictor' should be PascalCase → 'Predictor' or 'ModelPredictor'",
        "Variable 'm' should be '_model' (descriptive + private)",
        "Variable 'd' should be '_cache' or removed",
        "Function 'pred' should be 'predict'",
        "Variable 'r' should be 'result' or 'prediction'",
        "Variable 'p' should be 'model_path'",
    ],
    "2. Error Handling": [
        "Bare except clause catches ALL exceptions (even SystemExit!)",
        "File not explicitly closed (use context manager)",
        "No error handling on requests.post (network failures!)",
        "print('error') is not proper logging",
    ],
    "3. Security": [
        "pickle.load is a SECURITY RISK (arbitrary code execution)",
        "Use ONNX, joblib, or validated model formats instead",
        "Hardcoded URL in method (should be configurable)",
    ],
    "4. Design": [
        "Direct HTTP call in predict method violates SRP",
        "No separation between prediction and persistence",
        "pred_batch is sequential — should be vectorized",
        "No input validation",
        "No type hints",
        "Tight coupling to specific DB service",
    ],
    "5. Performance": [
        "pred_batch calls pred in a loop — should batch predict",
        "HTTP call on every prediction — latency overhead",
        "No caching of repeated predictions",
    ],
    "6. Testing": [
        "Impossible to test without real model file and DB service",
        "No dependency injection",
        "No interface/abstract class",
    ],
}


# ==========================================================
# AFTER: Refactored Code (show this as YOUR solution)
# ==========================================================

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# --- Data Models ---
@dataclass
class PredictionInput:
    """Validated input for prediction."""
    price: float
    star_rating: int
    review_score: float
    location_score: float
    
    def to_feature_vector(self) -> List[float]:
        return [self.price, self.star_rating, self.review_score, self.location_score]
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PredictionInput':
        """Factory method with validation."""
        required = ["price", "star_rating", "review_score", "location_score"]
        missing = [k for k in required if k not in data]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        return cls(
            price=float(data["price"]),
            star_rating=int(data["star_rating"]),
            review_score=float(data["review_score"]),
            location_score=float(data["location_score"]),
        )

@dataclass
class PredictionResult:
    """Structured prediction output."""
    score: float
    model_version: str
    input_features: PredictionInput

# --- Interfaces (Abstractions) ---
class ModelLoader(ABC):
    @abstractmethod
    def load(self, path: str):
        pass

class PredictionStore(ABC):
    @abstractmethod
    def save(self, result: PredictionResult) -> None:
        pass

# --- Implementations ---
class ONNXModelLoader(ModelLoader):
    """Safe model loading using ONNX (not pickle!)."""
    
    def load(self, path: str):
        import onnxruntime as ort
        try:
            session = ort.InferenceSession(path)
            logger.info(f"Model loaded successfully from {path}")
            return session
        except Exception as e:
            logger.error(f"Failed to load model from {path}: {e}")
            raise

class AsyncPredictionStore(PredictionStore):
    """Non-blocking prediction storage."""
    
    def __init__(self, store_url: str):
        self._url = store_url
    
    def save(self, result: PredictionResult) -> None:
        """Fire-and-forget save (don't block prediction)."""
        try:
            import httpx
            # In production: use async/background task
            httpx.post(self._url, json={
                "score": result.score,
                "model_version": result.model_version,
            }, timeout=1.0)
        except Exception as e:
            logger.warning(f"Failed to save prediction: {e}")
            # Don't fail the prediction just because storage failed

# --- Main Service (Refactored) ---
class HotelScorer:
    """
    Clean, testable, production-ready prediction service.
    
    Follows: SRP, DIP, Open/Closed, proper error handling.
    """
    
    FEATURE_NAMES = ["price", "star_rating", "review_score", "location_score"]
    
    def __init__(
        self,
        model_loader: ModelLoader,
        prediction_store: Optional[PredictionStore] = None,
        model_version: str = "unknown"
    ):
        self._model = None
        self._loader = model_loader
        self._store = prediction_store
        self._model_version = model_version
    
    def load_model(self, path: str) -> None:
        """Load model from path."""
        self._model = self._loader.load(path)
    
    def predict(self, input_data: PredictionInput) -> PredictionResult:
        """Single prediction with validation."""
        if self._model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        features = input_data.to_feature_vector()
        score = float(self._model.predict([features])[0])
        
        result = PredictionResult(
            score=score,
            model_version=self._model_version,
            input_features=input_data,
        )
        
        # Non-blocking save (background task in production)
        if self._store:
            self._store.save(result)
        
        return result
    
    def predict_batch(self, inputs: List[PredictionInput]) -> List[PredictionResult]:
        """Vectorized batch prediction — NOT a loop!"""
        if not inputs:
            return []
        
        # Batch all features into single array for vectorized prediction
        feature_matrix = [inp.to_feature_vector() for inp in inputs]
        scores = self._model.predict(feature_matrix)
        
        return [
            PredictionResult(
                score=float(scores[i]),
                model_version=self._model_version,
                input_features=inputs[i],
            )
            for i in range(len(inputs))
        ]


# ==========================================================
# TESTING EXAMPLE (shows testability of refactored code)
# ==========================================================

class MockModelLoader(ModelLoader):
    """Mock loader for testing — no real model needed!"""
    
    def load(self, path: str):
        class MockModel:
            def predict(self, features):
                return [0.85] * len(features)
        return MockModel()

class MockPredictionStore(PredictionStore):
    """Mock store for testing — no real DB needed!"""
    
    def __init__(self):
        self.saved = []
    
    def save(self, result):
        self.saved.append(result)

def test_hotel_scorer():
    """Unit test demonstrating testability."""
    # Arrange
    scorer = HotelScorer(
        model_loader=MockModelLoader(),
        prediction_store=MockPredictionStore(),
        model_version="test_v1"
    )
    scorer.load_model("fake_path")
    
    input_data = PredictionInput(
        price=150.0, star_rating=4, review_score=8.5, location_score=9.0
    )
    
    # Act
    result = scorer.predict(input_data)
    
    # Assert
    assert result.score == 0.85
    assert result.model_version == "test_v1"
    assert scorer._store.saved[0] == result
    print("✅ All tests passed!")

# test_hotel_scorer()
```

---

## 📝 Key Takeaways for the Backend Design Round

### What to Demonstrate:

```
┌────────────────────────────────────────────────────────────┐
│  ✅ Expert Python OOP                                       │
│     • Abstraction, encapsulation, polymorphism              │
│     • Dunder methods, decorators, context managers          │
│     • @classmethod (factory), @staticmethod (utility)       │
│                                                              │
│  ✅ Design Patterns (KNOW THESE 6)                          │
│     1. Strategy — swap ranking algorithms / A/B testing     │
│     2. Factory — create models from config/registry          │
│     3. Repository — decouple data access from logic         │
│     4. Observer — event-driven monitoring/alerting           │
│     5. Template Method — standard ML pipeline skeleton       │
│     6. Builder — complex pipeline configuration              │
│                                                              │
│  ✅ SOLID Principles                                         │
│     • Single Responsibility → separate concerns              │
│     • Open/Closed → extend without modifying                 │
│     • Liskov → subtypes are substitutable                    │
│     • Interface Segregation → small, focused interfaces      │
│     • Dependency Inversion → depend on abstractions          │
│                                                              │
│  ✅ API Design                                               │
│     • RESTful resource-based URIs                            │
│     • Pydantic validation, proper HTTP status codes          │
│     • Versioning, pagination, error handling                 │
│     • Middleware for logging/timing/auth                     │
│     • Dependency injection for testability                   │
│                                                              │
│  ✅ Code Review Skills                                       │
│     • Identify naming, error handling, design issues         │
│     • Refactor to clean, testable, production-ready code     │
│     • Show BEFORE → AFTER with clear improvements           │
│                                                              │
│  📌 ALWAYS connect to YOUR resume:                          │
│     "At Tiket.com, I applied Python OOP and design           │
│     patterns (Factory, Strategy, Repository) across all      │
│     ML services for maintainability and testability."        │
└────────────────────────────────────────────────────────────┘
```

---

> **Next:** Part 3 covers **PySpark Deep Dive, Data Pipeline Design, SQL, and Distributed Systems** — the Big Data aspects of the Backend Design Round.
