# 🏗️ Agoda Backend Design Round — Part 1: System Design & ML System Design

## 📋 Table of Contents
1. [Round Overview & What to Expect](#1-round-overview)
2. [The Framework — How to Answer Any Design Question](#2-the-framework)
3. [Question 1: Design a Hotel Search Ranking System](#3-hotel-ranking)
4. [Question 2: Design a Dynamic Pricing / Bidding System](#4-dynamic-pricing)
5. [Question 3: Design a Feature Store for ML Serving](#5-feature-store)
6. [Question 4: Design a Real-Time Recommendation System](#6-recommendation)
7. [Question 5: Design a Fraud Detection System for Bookings](#7-fraud-detection)

---

## 1. Round Overview & What to Expect <a name="1-round-overview"></a>

### 🎯 What is the Backend Design Round at Agoda?

Agoda's 2nd round is a **System Design / Backend Architecture** round that blends:
- **Traditional System Design** (HLD — High Level Design)
- **ML System Design** (because of the ML Engineering role)
- **Code Review / API Design** elements
- **Deep-dive into YOUR resume projects**

### 🔑 What Interviewers Evaluate

| Dimension | What They Look For |
|---|---|
| **Problem Scoping** | Do you ask clarifying questions? Define scope? |
| **Trade-off Reasoning** | Can you articulate WHY you chose X over Y? |
| **Scalability Thinking** | Can you scale from 1K to 1M QPS? |
| **Production Awareness** | Monitoring, fallbacks, failure handling |
| **Domain Knowledge** | Travel tech: seasonality, cold-start, inventory |
| **Communication** | Clear, structured, collaborative discussion |

### ⏱️ Time Allocation (45-60 min)

```
┌──────────────────────────────────────────────────────┐
│  0-8 min  │ Clarify Requirements & Scope             │
│  8-16 min │ High-Level Architecture                   │
│ 16-26 min │ Data & Feature Engineering Deep Dive      │
│ 26-36 min │ Model & Training Pipeline                 │
│ 36-46 min │ Deployment, Serving & Monitoring           │
│ 46-50 min │ Trade-offs Summary & Q&A                  │
└──────────────────────────────────────────────────────┘
```

---

## 2. The Framework — How to Answer ANY Design Question <a name="2-the-framework"></a>

### 🧠 The SUKH Framework (Scope → Understand → Knit → Harden)

Use this mnemonic for EVERY design question:

```
S — SCOPE       → Define functional & non-functional requirements
U — UNDERSTAND   → Identify data sources, volume, velocity, variety
K — KNIT         → Connect components into end-to-end architecture
H — HARDEN       → Add monitoring, fallbacks, scaling, trade-offs
```

### Step-by-Step Breakdown

#### S — SCOPE (Requirements Clarification)

**Always ask these questions FIRST:**

```python
# Functional Requirements Checklist
functional_requirements = {
    "What":       "What does the system DO? (rank hotels, price rooms, detect fraud)",
    "Who":        "Who are the users? (end consumers, hotel partners, internal teams)",
    "Input":      "What does the system receive? (search query, user profile, booking event)",
    "Output":     "What does the system return? (ranked list, price, fraud score)",
    "Latency":    "What's the acceptable response time? (p95 < 100ms, < 500ms)",
    "Scale":      "How many requests per second? (10K QPS? 1M QPS?)",
    "Freshness":  "How fresh must the data be? (real-time, hourly, daily)",
}

# Non-Functional Requirements Checklist
non_functional_requirements = {
    "Availability":   "99.9% or 99.99% uptime?",
    "Consistency":    "Strong consistency (bookings) vs eventual (reviews)?",
    "Scalability":    "Horizontal scaling? Auto-scaling?",
    "Fault Tolerance":"What happens when a component fails?",
    "Cost":           "Any budget constraints?",
    "Security":       "Authentication, authorization, data privacy?",
}
```

**💡 PRO TIP:** At Agoda, always mention:
- **Look-to-Book Ratio** (L2B) — searches per booking, key metric
- **Seasonality** — travel demand varies by season, holidays, events
- **Cold Start** — new hotels with no historical data
- **Inventory Consistency** — can't show rooms that are already booked

#### U — UNDERSTAND (Data & Features)

```python
# Data Sources for Agoda-like System
data_sources = {
    "User Data": {
        "clickstream":    "real-time user interactions (clicks, views, scrolls)",
        "search_history": "past search queries and filters",
        "booking_history":"past bookings, cancellations, preferences",
        "user_profile":   "demographics, loyalty tier, preferred language",
    },
    "Hotel/Supply Data": {
        "inventory":      "rooms available, room types, capacity",
        "metadata":       "name, location, amenities, photos, ratings",
        "pricing":        "base price, discounts, commission rates",
        "reviews":        "guest reviews, ratings distributions",
    },
    "Contextual Data": {
        "time_features":  "day of week, time of day, season, holidays",
        "market_signals": "competitor prices, demand trends",
        "geo_features":   "user location, destination popularity",
    }
}
```

#### K — KNIT (Architecture)

```
┌────────────────────────────────────────────────────────────────┐
│                    HIGH-LEVEL ARCHITECTURE                      │
│                                                                  │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐        │
│  │ API GW / │───▶│  Prediction  │───▶│  Feature Store   │        │
│  │ Load Bal │    │   Service    │    │  (Online/Offline)│        │
│  └──────────┘    └──────┬───────┘    └────────┬─────────┘        │
│                         │                      │                  │
│                 ┌───────▼──────┐    ┌──────────▼─────────┐       │
│                 │   Model      │    │  Data Pipeline      │       │
│                 │  Repository  │    │ (Batch + Streaming) │       │
│                 │  (MLflow)    │    │ (Spark + Kafka)     │       │
│                 └──────────────┘    └────────────────────┘        │
│                                                                   │
│  ┌─────────────────────────────────────────────────────┐         │
│  │              Monitoring & Alerting                    │         │
│  │  (Feature Drift, Model Performance, SLA Tracking)    │         │
│  └─────────────────────────────────────────────────────┘         │
└────────────────────────────────────────────────────────────────┘
```

#### H — HARDEN (Production-Readiness)

```python
# Production Hardening Checklist
hardening_checklist = {
    "Monitoring": [
        "Feature drift detection (PSI, KL divergence)",
        "Model performance metrics (accuracy, latency p50/p95/p99)",
        "Business metrics (CTR, conversion rate, revenue)",
        "Infrastructure metrics (CPU, memory, disk, network)",
    ],
    "Fallbacks": [
        "If ML service fails → serve cached/heuristic-based results",
        "If feature store is down → use default feature values",
        "Circuit breaker pattern for downstream dependencies",
    ],
    "Scaling": [
        "Horizontal pod autoscaler (HPA) for serving",
        "Spark auto-scaling for training pipelines",
        "Read replicas for feature store",
    ],
    "Testing": [
        "A/B testing framework for model comparison",
        "Shadow deployment for safe rollout",
        "Canary releases with automatic rollback",
    ],
}
```

---

## 3. Question 1: Design a Hotel Search Ranking System <a name="3-hotel-ranking"></a>

### 🎯 Problem Statement
> "Design a system that ranks hotels for Agoda's search results page. When a user searches for 'Bangkok, 2 adults, July 15-18', the system should return a ranked list of hotels optimized for booking probability."

### Step 1: SCOPE — Requirements

```python
# Functional Requirements
functional = {
    "Search Input":  "location, dates, guests, filters (price, stars, amenities)",
    "Output":        "Ranked list of N hotels (typically top 20-50 per page)",
    "Personalized":  "Yes — user history, preferences affect ranking",
    "Sponsored":     "Hotels can bid for higher placement (bidding integration)",
    "Real-time":     "Must reflect current availability & pricing",
}

# Non-Functional Requirements
non_functional = {
    "Latency":       "p95 < 200ms for the ranking step",
    "Throughput":    "~50K search queries/sec during peak",
    "Availability":  "99.99% — downtime = direct revenue loss",
    "Data Freshness":"Inventory: real-time | Reviews: eventually consistent",
}

# Key Metrics
metrics = {
    "Offline":  ["NDCG@K", "MAP@K", "AUC-ROC"],
    "Online":   ["Click-Through Rate (CTR)", "Look-to-Book (L2B)", 
                 "Revenue per Search", "Booking Conversion Rate"],
}
```

### Step 2: UNDERSTAND — Data & Features

```python
# Feature Categories for Hotel Ranking
features = {
    "Query Features": {
        "destination":      "city/region encoding",
        "check_in_date":    "day of week, months to departure",
        "stay_duration":    "number of nights",
        "num_guests":       "adults + children",
        "filters_applied":  "price range, star rating, amenities",
    },
    "User Features": {
        "booking_history":  "past destinations, hotel stars, avg spend",
        "click_history":    "recent hotel clicks in this session",
        "user_segment":     "business/leisure, loyalty tier",
        "device_type":      "mobile vs desktop (correlates with behavior)",
        "preferred_lang":   "language/country of origin",
    },
    "Hotel Features": {
        "static": {
            "star_rating":     "1-5 stars",
            "amenities":       "pool, wifi, breakfast (one-hot or embedding)",
            "location_score":  "distance to city center, attractions",
            "review_score":    "average rating from verified guests",
            "photo_quality":   "ML-scored photo attractiveness",
        },
        "dynamic": {
            "current_price":   "price for this specific search",
            "availability":    "rooms remaining (scarcity signal)",
            "competitor_price":"price on competing OTAs",
            "recent_bookings": "popularity trend (last 24h, 7d)",
        },
    },
    "Context Features": {
        "is_weekend":       "boolean",
        "is_holiday":       "boolean",
        "season":           "peak/off-peak",
        "time_of_day":      "hour bucket",
    },
    "Cross Features": {
        "price_per_night_vs_user_avg": "relative price signal",
        "star_rating_match":           "does hotel match user preference?",
        "destination_familiarity":     "has user visited this city before?",
    },
}
```

### Step 3: KNIT — Architecture

```
                    Hotel Search Ranking — Architecture
                    ====================================

User Query (Bangkok, July 15-18, 2 adults)
     │
     ▼
┌──────────────┐
│   API Gateway │──── Rate limiting, auth, request validation
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│                  SEARCH TIER (Read-Heavy)                  │
│                                                            │
│  ┌──────────────┐     ┌────────────────────┐              │
│  │ Elasticsearch │────▶│  Candidate         │              │
│  │ (Hotel Index) │     │  Generator         │              │
│  │               │     │  (Top 500 matches) │              │
│  └──────────────┘     └────────┬───────────┘              │
│                                 │                          │
└─────────────────────────────────┼──────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────┐
│                 AVAILABILITY TIER (Real-Time)              │
│                                                            │
│  ┌────────────┐    ┌──────────────────────────┐           │
│  │   Redis     │───▶│  Availability Filter     │           │
│  │ (Inventory) │    │  (Remove sold-out hotels)│           │
│  └────────────┘    └──────────┬───────────────┘           │
│                                │                           │
└────────────────────────────────┼───────────────────────────┘
                                 │ (e.g., 300 available)
                                 ▼
┌──────────────────────────────────────────────────────────┐
│                    RANKING TIER (ML)                       │
│                                                            │
│  ┌──────────────────┐    ┌──────────────┐                 │
│  │  Feature Store    │───▶│   ML Ranker   │                │
│  │  (Feast + Redis)  │    │  (GBDT/LTR)  │                │
│  │                   │    │              │                  │
│  │ - User features   │    │  Score each   │                │
│  │ - Hotel features   │    │  candidate   │                │
│  │ - Context features │    └──────┬───────┘                │
│  └──────────────────┘            │                         │
│                                   │                        │
│  ┌──────────────────┐    ┌───────▼────────┐               │
│  │  Bidding Service  │───▶│   Re-Ranker /  │               │
│  │(sponsored scores) │    │   Business     │               │
│  └──────────────────┘    │   Rules Layer  │                │
│                           └───────┬────────┘               │
│                                   │                        │
└───────────────────────────────────┼────────────────────────┘
                                    │
                                    ▼
                          Final Ranked Results
                          (Top 20 per page)
```

### Step 4: Model Selection & Training

```python
# ==========================================================
# MODEL: Learning-to-Rank with Gradient Boosted Trees
# ==========================================================
# WHY GBDT (XGBoost/LightGBM) for Hotel Ranking?
# 1. Handles mixed feature types (categorical + numerical) natively
# 2. Feature importance for explainability
# 3. Fast inference (~1-5ms per batch of 500 hotels)
# 4. Works well with tabular data (hotel features ARE tabular)
# 5. Simpler to debug in production vs deep learning

# Model Architecture: Two-Stage Ranking
# Stage 1: Candidate Generation (Elasticsearch) → Top 500
# Stage 2: ML Re-Ranking (GBDT LTR) → Top 20 per page

from dataclasses import dataclass
from typing import List, Dict
import numpy as np

@dataclass
class RankingRequest:
    """Represents a user's search request for ranking."""
    user_id: str
    destination: str
    check_in: str
    check_out: str
    num_guests: int
    filters: Dict[str, any]

@dataclass
class HotelCandidate:
    """A candidate hotel to be ranked."""
    hotel_id: str
    features: Dict[str, float]
    ml_score: float = 0.0
    bid_boost: float = 0.0
    final_score: float = 0.0

class HotelRankingService:
    """
    Production hotel ranking service.
    
    Architecture:
    1. Receive search query
    2. Generate candidates from Elasticsearch
    3. Filter by availability (Redis)
    4. Fetch features from Feature Store
    5. Score with ML model
    6. Apply business rules & bidding boosts
    7. Return ranked list
    """
    
    def __init__(self, model, feature_store, availability_store, bidding_service):
        self.model = model                     # ONNX Runtime model
        self.feature_store = feature_store       # Feast online store
        self.availability_store = availability_store  # Redis
        self.bidding_service = bidding_service   # Bidding microservice
    
    def rank(self, request: RankingRequest) -> List[HotelCandidate]:
        # Step 1: Candidate Generation (Elasticsearch)
        candidates = self._generate_candidates(request)  # Top 500
        
        # Step 2: Availability Filter (Redis)
        available = self._filter_available(candidates, request)  # ~300
        
        # Step 3: Feature Enrichment (Feature Store)
        enriched = self._enrich_features(available, request)
        
        # Step 4: ML Scoring (ONNX Runtime)
        scored = self._score_candidates(enriched)
        
        # Step 5: Business Rules + Bidding
        reranked = self._apply_business_rules(scored, request)
        
        return reranked[:20]  # Top 20 per page
    
    def _generate_candidates(self, request):
        """Elasticsearch query with filters → top 500 candidates."""
        # Uses inverted index for fast text/geo search
        # Applies hard filters: location, dates, guest capacity
        pass
    
    def _filter_available(self, candidates, request):
        """Redis lookup: check room availability for dates."""
        # Key: hotel_id:room_type:date → available_count
        # Uses MGET for batch lookup (single round trip)
        # WHY Redis? Sub-ms latency, inventory changes frequently
        pass
    
    def _enrich_features(self, candidates, request):
        """Fetch features from Feast online store (Redis-backed)."""
        # Batch fetch: user features + hotel features + context
        # WHY Feast? Prevents training-serving skew
        pass
    
    def _score_candidates(self, candidates):
        """ONNX Runtime batch inference."""
        # Batch all 300 candidates into single inference call
        # WHY ONNX? 3x faster than native TensorFlow/PyTorch
        pass
    
    def _apply_business_rules(self, candidates, request):
        """Apply bidding boosts and business constraints."""
        # Formula: final_score = α * ml_score + β * bid_boost
        # Constraints: max 3 sponsored results in top 10
        # Diversity: ensure variety in star ratings, price ranges
        pass
```

### Step 5: HARDEN — Production Concerns

```python
# Training Pipeline (Kubeflow)
training_pipeline = {
    "Data Source":      "BigQuery (user interactions, bookings)",
    "Label":           "Booking probability (binary: booked or not)",
    "Training Data":   "Point-in-time feature snapshots (prevent leakage!)",
    "Framework":       "LightGBM with LambdaRank loss (LTR objective)",
    "Tracking":        "MLflow (params, metrics, artifacts)",
    "Registry":        "MLflow Model Registry (staging → production)",
    "Schedule":        "Daily retraining, weekly full retrain",
    "Evaluation":      "Offline: NDCG@10, MAP@10 | Online: A/B test",
}

# Serving Architecture
serving = {
    "Framework":       "FastAPI microservice",
    "Model Format":    "ONNX (optimized inference)",
    "Scaling":         "Kubernetes HPA (CPU-based auto-scaling)",
    "Deployment":      "Canary release (5% → 25% → 50% → 100%)",
    "Fallback":        "If ML fails → fallback to rule-based ranking (price * review_score)",
    "Caching":         "Cache popular destination rankings (TTL: 5 min)",
}

# Monitoring
monitoring = {
    "Feature Drift":   "Population Stability Index (PSI) per feature, daily",
    "Model Perf":      "Live NDCG@10, CTR, L2B ratio — tracked in Grafana",
    "Latency":         "p50, p95, p99 per endpoint — alerting on p99 > 200ms",
    "Business SLA":    "Revenue per search must not drop > 5% after model deploy",
    "Alerting":        "Slack + email on metric degradation → auto-trigger retrain",
}
```

### 💬 How Sukh Should Answer This (Connected to Resume)

> "At Tiket.com, I built exactly this kind of system. Our **Hotel Ranking ML Platform** processed millions of search queries daily. I architected the end-to-end pipeline: data ingestion from BigQuery → feature engineering → Kubeflow training pipelines → MLflow tracking → FastAPI serving with ONNX Runtime.
>
> We used **Random Forest and Gradient Boosting** models with hyperparameter optimization, improving accuracy from 82% to 90%. The feature store was **Feast backed by MongoDB** with compression, achieving 60% storage cost reduction while maintaining sub-100ms p95 latency.
>
> For deployment, we supported **4+ concurrent ranking models** via A/B testing and shadow deployment. The ONNX Runtime integration gave us **3x throughput improvement** over native TensorFlow serving."

---

## 4. Question 2: Design a Dynamic Pricing / Bidding System <a name="4-dynamic-pricing"></a>

### 🎯 Problem Statement
> "Design a dynamic pricing system for a travel platform. The system should optimize prices for both B2B (hotel partners) and B2C (end consumers) to maximize revenue while remaining competitive."

### Step 1: SCOPE

```python
functional = {
    "B2B Track": "Adjust commission/prices to hotel partners based on performance",
    "B2C Track": "Set optimal display prices for end consumers",
    "Real-time": "Prices must reflect current demand, competition, inventory",
    "Constraints":"Prices must respect business rules (min/max, parity agreements)",
}

non_functional = {
    "Latency":     "Batch inference OK (hourly/daily price updates)",
    "Scale":       "2.5M+ properties globally, each with multiple room types",
    "Accuracy":    "Revenue optimization within 2% of theoretical optimal",
    "Compliance":  "Respect rate parity agreements with hotel partners",
}

metrics = {
    "B2B": ["Revenue per partner", "Partner retention", "Win rate vs competitors"],
    "B2C": ["Click probability", "Conversion rate", "Revenue per user", "Margin"],
}
```

### Step 2: Architecture

```
                Dynamic Pricing System — Architecture
                ======================================

┌───────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌─────────────┐  ┌────────────┐  │
│  │ BigQuery  │  │ Booking  │  │ Competitor  │  │ Market     │  │
│  │ (History) │  │ Events   │  │ Prices      │  │ Signals    │  │
│  └─────┬────┘  └─────┬────┘  └──────┬──────┘  └─────┬──────┘  │
│        │              │              │                │          │
│        └──────────────┴──────────────┴────────────────┘          │
│                              │                                    │
│                    ┌─────────▼──────────┐                        │
│                    │  Feature Pipeline   │                        │
│                    │  (PySpark on EMR)   │                        │
│                    └─────────┬──────────┘                        │
│                              │                                    │
└──────────────────────────────┼────────────────────────────────────┘
                               │
           ┌───────────────────┼────────────────────┐
           │                   │                     │
           ▼                   ▼                     ▼
┌────────────────┐  ┌────────────────┐    ┌────────────────────┐
│   B2B TRACK    │  │   B2C TRACK    │    │   B2C TRACK        │
│                │  │ Click Prob.    │    │ Demand Forecast    │
│  RL Agent      │  │ XGBoost Model  │    │ LightGBM Model     │
│  (Price Adj.)  │  │                │    │                    │
└───────┬────────┘  └───────┬────────┘    └────────┬───────────┘
        │                   │                       │
        └───────────────────┼───────────────────────┘
                            │
                   ┌────────▼──────────┐
                   │  Pricing Engine   │
                   │  (Business Rules) │
                   │  - Min/max bounds │
                   │  - Parity checks  │
                   │  - Budget caps    │
                   └────────┬──────────┘
                            │
                   ┌────────▼──────────┐
                   │  Kafka Publisher  │
                   │  (Price Updates)  │
                   └────────┬──────────┘
                            │
              ┌─────────────┼──────────────┐
              ▼             ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ Pricing  │  │ Ranking  │  │ Partner  │
        │ Display  │  │ Service  │  │ Portal   │
        │ Service  │  │          │  │          │
        └──────────┘  └──────────┘  └──────────┘
```

### Step 3: Model Details

```python
# ==========================================================
# B2B Track: Reinforcement Learning Agent
# ==========================================================
# WHY RL for B2B pricing?
# - Sequential decision: each price adjustment affects future partner behavior
# - Delayed rewards: partner retention is long-term
# - Exploration-exploitation: need to try different prices while maximizing revenue
# - Environment changes: market conditions and competitor pricing shift

class B2BPricingAgent:
    """
    Reinforcement Learning agent for B2B price adjustment.
    
    State:  [partner_performance, historical_bookings, competitor_rates, 
             season, inventory_level, commission_rate]
    Action: Price adjustment delta (+/- percentage)
    Reward: Revenue signal from bookings + partner retention metric
    """
    
    def __init__(self):
        self.state_dim = 15
        self.action_space = [-5, -3, -1, 0, +1, +3, +5]  # % adjustments
    
    def get_state(self, partner_id: str) -> np.ndarray:
        """Construct state vector from feature store."""
        return np.array([
            self._get_partner_booking_rate(partner_id),
            self._get_partner_revenue_trend(partner_id),
            self._get_competitor_avg_price(partner_id),
            self._get_inventory_level(partner_id),
            self._get_seasonal_demand_index(),
            # ... more features
        ])
    
    def predict_action(self, state: np.ndarray) -> float:
        """Select optimal price adjustment using learned policy."""
        # Epsilon-greedy for exploration during learning
        # Greedy (argmax Q-value) during production
        pass


# ==========================================================
# B2C Track: Click Probability (XGBoost)
# ==========================================================
# WHY XGBoost for click probability?
# - Tabular features → GBDT excels
# - Fast inference needed for many listings
# - Handles missing features gracefully
# - Feature importance for explainability

class ClickProbabilityModel:
    """
    XGBoost model predicting P(click | listing, user, context).
    Used for demand-aware price positioning.
    """
    
    features = {
        "listing_features": [
            "price_relative_to_market",  # current price / avg market price
            "star_rating",
            "review_score",
            "photo_quality_score",
            "distance_to_center",
        ],
        "user_features": [
            "user_price_sensitivity",     # derived from booking history
            "preferred_star_rating",
            "booking_frequency",
        ],
        "context_features": [
            "days_to_checkin",
            "is_weekend",
            "demand_index",               # high/medium/low demand period
        ],
    }
    
    def predict_click_prob(self, features_df):
        """Batch predict click probability for all listings."""
        # Returns P(click) for each listing
        # Used by pricing engine: higher click prob → can increase price slightly
        pass


# ==========================================================
# B2C Track: Demand Forecasting (LightGBM)
# ==========================================================
# WHY LightGBM for demand forecasting?
# - Faster training than XGBoost (Histogram-based)
# - Handles large datasets efficiently
# - Good with time-series derived features

class DemandForecastModel:
    """
    LightGBM model predicting demand for a destination/date combination.
    Incorporates seasonality, market trends, and historical patterns.
    """
    
    features = {
        "temporal": [
            "day_of_week", "month", "is_holiday", "days_to_event",
            "demand_lag_7d", "demand_lag_30d", "demand_rolling_avg_7d",
        ],
        "market": [
            "competitor_avg_price", "flight_search_volume",
            "destination_popularity_trend",
        ],
        "historical": [
            "bookings_same_period_last_year",
            "cancellation_rate_trend",
        ],
    }
```

### Step 4: Training Pipeline Optimization

```python
# ==========================================================
# KEY RESUME POINT: Reduced training time from ~7 hrs → 22 min
# ==========================================================
# Here's HOW you achieved this — be ready to explain!

optimization_techniques = {
    "1. Multiprocessing": {
        "what": "Parallelized feature computation across CPU cores",
        "how":  "Python multiprocessing.Pool for independent feature groups",
        "gain": "~4x speedup on feature engineering step",
    },
    "2. PySpark Optimization": {
        "what": "Optimized Spark job configurations",
        "how":  """
            - Increased parallelism (repartition to match executor count)
            - Used broadcast joins for small dimension tables
            - Cached intermediate DataFrames used multiple times
            - Switched from JSON to Parquet format (10x read speed)
            - Columnar pruning (select only needed columns early)
        """,
        "gain": "~5x speedup on data processing",
    },
    "3. Training Optimization": {
        "what": "Optimized model training itself",
        "how":  """
            - Early stopping (prevent unnecessary iterations)
            - Feature selection (removed low-importance features)
            - Optimized hyperparameter search (Bayesian over Grid)
            - Used GPU-accelerated XGBoost where applicable
        """,
        "gain": "~3x speedup on training step",
    },
    "4. Pipeline Design": {
        "what": "Restructured the end-to-end pipeline",
        "how":  """
            - Separated feature computation from training
            - Pre-computed expensive features (stored in feature store)
            - Incremental training (only process new data)
        """,
        "gain": "~2x speedup by avoiding redundant computation",
    },
}
# Combined effect: 6-8 hours → 22 minutes
```

### 💬 How Sukh Should Answer This (Connected to Resume)

> "At Tiket.com, I designed and deployed the **Orion Dynamic Pricing Platform** covering both B2B and B2C tracks.
>
> For **B2B**, I built a Reinforcement Learning agent that learned optimal pricing policies from historical booking and revenue signals. For **B2C**, I built an XGBoost model for click probability forecasting and a LightGBM model for demand forecasting incorporating seasonality and market trends.
>
> The entire pipeline was orchestrated with **Kubeflow** and tracked with **MLflow**. Kafka published inference results downstream to pricing and recommendation consumers. I reduced the training & evaluation runtime from **~6-8 hours to 22 minutes** through multiprocessing and optimized data pipelines."

---

## 5. Question 3: Design a Feature Store for ML Serving <a name="5-feature-store"></a>

### 🎯 Problem Statement
> "Design a feature store architecture that serves both offline training and online low-latency inference for multiple ML models across teams."

### Architecture

```
              Feature Store Architecture
              ==========================

┌─────────────────────────────────────────────────────────────┐
│                    DATA SOURCES                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ BigQuery  │  │ Kafka    │  │ App DBs  │  │ Logs     │    │
│  │ (Batch)   │  │ (Stream) │  │ (MongoDB)│  │ (ELK)    │    │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘    │
│        │              │              │              │          │
└────────┼──────────────┼──────────────┼──────────────┼──────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│              FEATURE COMPUTATION LAYER                        │
│                                                               │
│  ┌─────────────────┐     ┌─────────────────────┐            │
│  │  Batch Pipeline  │     │  Streaming Pipeline  │            │
│  │  (PySpark/SQL)   │     │  (Kafka + Flink)     │            │
│  │                  │     │                      │            │
│  │ • Daily/hourly   │     │ • Real-time features │            │
│  │ • Aggregations   │     │ • Session features   │            │
│  │ • Historical     │     │ • Live click counts  │            │
│  └────────┬────────┘     └──────────┬───────────┘            │
│           │                         │                         │
└───────────┼─────────────────────────┼─────────────────────────┘
            │                         │
            ▼                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FEATURE STORE (Feast)                       │
│                                                               │
│  ┌──────────────────┐      ┌──────────────────────┐          │
│  │   Offline Store   │      │    Online Store       │          │
│  │   (S3 / BigQuery) │      │    (Redis / MongoDB)  │          │
│  │                   │      │                       │          │
│  │ • Training data   │      │ • Latest feature vals │          │
│  │ • Point-in-time   │      │ • Sub-100ms lookups  │          │
│  │   correct joins   │      │ • Compressed storage  │          │
│  │ • Historical      │      │ • (60% cost reduction)│          │
│  └────────┬──────────┘      └──────────┬───────────┘          │
│           │                             │                      │
│  ┌────────▼──────────┐      ┌──────────▼───────────┐          │
│  │ Feature Registry  │      │  Feature Serving API  │          │
│  │ (Schema, Metadata)│      │  (FastAPI + gRPC)     │          │
│  └───────────────────┘      └──────────────────────┘          │
│                                                               │
└───────────────────────────────────────────────────────────────┘
            │                             │
            ▼                             ▼
     ┌──────────────┐            ┌──────────────┐
     │ ML Training  │            │ ML Serving   │
     │ Pipelines    │            │ (Real-time   │
     │ (Kubeflow)   │            │  inference)  │
     └──────────────┘            └──────────────┘
```

### Key Design Decisions

```python
# ==========================================================
# Training-Serving Skew Prevention
# ==========================================================
# THE #1 PROBLEM in production ML systems!
# 
# What is it?
# - Features computed differently during training vs serving
# - Example: "avg_price_7d" computed with pandas in training
#   but differently formatted SQL query in serving → different values!
#
# Solution: Single Feature Definition → Used by Both Pipelines

# Feast Feature Definition Example
from feast import Entity, Feature, FeatureView, FileSource, ValueType
from datetime import timedelta

# Entity
hotel = Entity(name="hotel_id", value_type=ValueType.STRING)
user = Entity(name="user_id", value_type=ValueType.STRING)

# Feature View (single source of truth)
hotel_features = FeatureView(
    name="hotel_features",
    entities=["hotel_id"],
    ttl=timedelta(hours=24),
    features=[
        Feature(name="avg_review_score", dtype=ValueType.FLOAT),
        Feature(name="bookings_last_7d", dtype=ValueType.INT64),
        Feature(name="avg_price_3d", dtype=ValueType.FLOAT),
        Feature(name="cancellation_rate", dtype=ValueType.FLOAT),
    ],
    online=True,   # Available for real-time serving
    batch_source=FileSource(
        path="s3://features/hotel_features/",
        timestamp_field="event_timestamp",
    ),
)

# Training: Point-in-Time Join (prevents data leakage)
# training_df = store.get_historical_features(
#     entity_df=booking_events,  # with timestamps
#     features=["hotel_features:avg_review_score", ...]
# )

# Serving: Online Lookup (sub-100ms)
# online_features = store.get_online_features(
#     features=["hotel_features:avg_review_score", ...],
#     entity_rows=[{"hotel_id": "H12345"}]
# )

# ==========================================================
# Storage Optimization (60% cost reduction)
# ==========================================================
storage_optimization = {
    "Compression": {
        "what": "Applied MongoDB compression on feature values",
        "how":  "Snappy compression for fast read/write, ZSTD for archival",
        "gain": "60% storage cost reduction",
    },
    "TTL Policy": {
        "what": "Auto-expire stale features",
        "how":  "MongoDB TTL indexes on timestamp fields",
        "gain": "Prevents unbounded storage growth",
    },
    "Feature Selection": {
        "what": "Only store features that are actually used",
        "how":  "Track feature usage across models, deprecate unused features",
        "gain": "Reduced feature table size by 30%",
    },
    "Partitioning": {
        "what": "Partition by entity_id for fast point lookups",
        "how":  "MongoDB sharding on entity_id",
        "gain": "Sub-100ms p95 latency for online lookups",
    },
}
```

---

## 6. Question 4: Design a Real-Time Recommendation System <a name="6-recommendation"></a>

### 🎯 Problem Statement
> "Design a personalized hotel recommendation system that operates in real-time, showing 'Hotels you might like' based on a user's current session behavior."

### Architecture

```python
# Two-Stage Recommendation Architecture
# ======================================
# Stage 1: Candidate Generation (fast, broad recall)
# Stage 2: Ranking/Scoring (precise, personalized)

class RecommendationSystem:
    """
    Real-time personalized hotel recommendations.
    
    Flow:
    1. User views a hotel page → trigger recommendation request
    2. Candidate Generation: Retrieve 200 similar/popular hotels
    3. Ranking: Score candidates with personalized ML model
    4. Post-processing: Apply diversity rules, remove already-viewed
    5. Return top 10 recommendations
    """
    
    # Stage 1: Candidate Generation Strategies
    candidate_strategies = {
        "Collaborative Filtering": {
            "method": "Users who booked Hotel A also booked Hotel B",
            "tech":   "Pre-computed item-item similarity matrix (ALS/SVD)",
            "storage":"Redis sorted sets: hotel_id → [similar_hotel_ids + scores]",
            "latency":"~5ms (pre-computed lookup)",
        },
        "Content-Based": {
            "method": "Hotels with similar attributes (location, star, amenities)",
            "tech":   "Elasticsearch more_like_this query",
            "latency":"~20ms",
        },
        "Session-Based": {
            "method": "Based on hotels viewed in current session",
            "tech":   "Real-time session tracker (Redis) → find similar hotels",
            "latency":"~10ms",
        },
        "Popularity": {
            "method": "Trending hotels in same destination",
            "tech":   "Pre-computed per-destination popularity scores",
            "latency":"~3ms",
        },
    }
    
    # Cold Start Handling
    cold_start = {
        "New User":  "Use popularity + content-based (no click history)",
        "New Hotel": "Use content-based similarity + promote for data collection",
        "Strategy":  "Explore-exploit: show diverse options initially, personalize later",
    }
    
    # Stage 2: Ranking Model
    ranking_model = {
        "Input":   "User features + Hotel features + Context features",
        "Output":  "P(click) or P(book) for each candidate",
        "Model":   "LightGBM (fast, tabular data, real-time serving)",
        "Training":"Click/booking logs with point-in-time features",
    }
    
    # Diversity Rules (Post-Processing)
    diversity_rules = [
        "Max 3 hotels from same chain/brand",
        "Ensure mix of price ranges (budget + mid + luxury)",
        "Ensure geographic diversity (not all in same neighborhood)",
        "No duplicate hotels already shown in search results",
    ]
```

---

## 7. Question 5: Design a Fraud Detection System <a name="7-fraud-detection"></a>

### 🎯 Problem Statement
> "Design a system to detect fraudulent bookings and fake reviews on a travel platform."

### Architecture

```python
# ==========================================================
# Fraud Detection — Two-Layer Architecture
# ==========================================================

class FraudDetectionSystem:
    """
    Two-layer fraud detection:
    Layer 1: Real-time rules engine (instant blocking)
    Layer 2: ML model scoring (probabilistic fraud detection)
    """
    
    # Layer 1: Rule-Based (Real-Time, Deterministic)
    rules_engine = {
        "Velocity Rules": [
            "Same credit card > 5 bookings in 1 hour → flag",
            "Same IP > 10 bookings in 1 hour → flag",
            "Same user > 3 countries in 24 hours → flag",
        ],
        "Pattern Rules": [
            "Check-in date within 2 hours of booking → high risk",
            "Booking value > 10x user's average spend → flag",
            "New account + high-value booking → flag",
        ],
        "Blocklist Rules": [
            "Known fraudulent email domains → block",
            "Known VPN/proxy IPs → increase risk score",
            "Previously banned credit card BINs → block",
        ],
    }
    
    # Layer 2: ML Model (Near Real-Time, Probabilistic)
    ml_model = {
        "Model":     "XGBoost binary classifier: P(fraud | booking)",
        "Features":  {
            "user_behavior":   ["time_on_site", "pages_viewed", "search_pattern"],
            "booking_features":["booking_value", "lead_time", "room_type"],
            "device_features": ["device_fingerprint", "browser_type", "screen_res"],
            "payment_features":["card_country_mismatch", "payment_method", "bin_risk"],
            "historical":      ["past_chargebacks", "past_fraud_flags", "account_age"],
        },
        "Threshold": "P(fraud) > 0.8 → auto-block, 0.5-0.8 → manual review",
        "Latency":   "Must score within 50ms to not delay booking flow",
    }
    
    # Fake Review Detection
    fake_review = {
        "NLP Features": [
            "Review sentiment vs rating mismatch",
            "Review text similarity to other reviews (copy-paste detection)",
            "Unusual review length or generic language patterns",
        ],
        "Behavioral Features": [
            "User reviewed 20+ hotels in 1 day → suspicious",
            "All reviews are 5-star or 1-star → suspicious",
            "Review without actual booking → verify",
        ],
        "Model": "Fine-tuned BERT or simpler TF-IDF + Logistic Regression",
    }
```

---

## 📝 Quick Reference: How to Structure ANY Design Answer

```
┌─────────────────────────────────────────────────────────┐
│          THE SUKH FRAMEWORK CHEAT SHEET                   │
│                                                           │
│  S → SCOPE (5-8 min)                                     │
│      • Functional requirements (what does it DO?)        │
│      • Non-functional (latency, scale, availability)     │
│      • Success metrics (offline + online)                │
│                                                           │
│  U → UNDERSTAND (8-10 min)                               │
│      • Data sources & volume                             │
│      • Feature categories (user, item, context, cross)   │
│      • Feature freshness (real-time vs batch)            │
│                                                           │
│  K → KNIT (15-20 min)                                    │
│      • High-level architecture diagram                   │
│      • Component deep dives (Feature Store, Model, API)  │
│      • Model selection with justification                │
│      • Training pipeline design                          │
│                                                           │
│  H → HARDEN (8-10 min)                                   │
│      • Deployment strategy (canary, A/B, shadow)         │
│      • Monitoring (feature drift, model perf, SLAs)      │
│      • Fallback strategies                               │
│      • Scaling plan                                      │
│                                                           │
│  ALWAYS: Connect to YOUR resume experience!              │
└─────────────────────────────────────────────────────────┘
```

---

> **Next:** Part 2 covers **Python OOP, Design Patterns, PySpark Deep Dives, and API Design** — the coding-heavy aspects of the Backend Design Round.
