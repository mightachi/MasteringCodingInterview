# 🎤 Agoda Backend Design Round — Part 4: Mock Interview, Resume Deep-Dive & Behavioral

## 📋 Table of Contents
1. [Full Mock Interview Simulation](#1-mock-interview)
2. [Resume Deep-Dive Questions & Answers](#2-resume-deep-dive)
3. [Agoda-Specific Domain Questions](#3-agoda-domain)
4. [Behavioral & Leadership Questions](#4-behavioral)
5. [Questions to Ask the Interviewer](#5-ask-interviewer)
6. [Final Cheat Sheet — Day-of-Interview Guide](#6-cheat-sheet)

---

## 1. Full Mock Interview Simulation <a name="1-mock-interview"></a>

### 🎯 Scenario: "Design a Hotel Bidding & Ranking System"

This simulates a 50-minute backend design round with an Agoda interviewer. Follow this structure exactly.

---

### Minute 0-8: Requirements Clarification

**Interviewer:** "Design a system where hotels can bid for higher placement in search results, similar to sponsored ads, while maintaining organic ranking quality."

**Your response (ask these questions):**

```
YOU: "Before I start designing, I'd like to clarify the requirements."

FUNCTIONAL QUESTIONS:
1. "Who are the users? — Hotels (bidding) and travelers (searching), correct?"
2. "Can hotels set daily budgets and bid amounts?"
3. "Should sponsored results be clearly marked as 'Sponsored'?"
4. "How many sponsored slots per page? Mix of organic + sponsored?"
5. "Can hotels target specific keywords or destinations?"
6. "Real-time bidding or pre-set bid amounts?"

NON-FUNCTIONAL QUESTIONS:
1. "What's the expected QPS for search? ~50K QPS?"
2. "Latency requirement? Should be under 200ms end-to-end?"
3. "How many hotels are in the system? ~2.5M globally?"
4. "Do we need to support real-time budget tracking?"

After clarification, RESTATE the scope:

"So let me summarize what we're building:
- Hotels can set bid amounts and daily budgets
- Search results combine organic ML ranking with bid-boosted results  
- Max 3 sponsored slots in top 10 results, clearly labeled
- Budget depletion tracked in real-time
- 50K QPS, p95 < 200ms, 2.5M properties"
```

### Minute 8-20: High-Level Architecture

```
YOU: "Let me walk through the high-level architecture."

                    HOTEL BIDDING + RANKING SYSTEM
                    ================================

    ┌─────────────────────────────────────────────────────┐
    │                  HOTEL PARTNER PORTAL                │
    │  Set bids: destination, keyword, amount, budget     │
    └─────────────────────┬───────────────────────────────┘
                          │ Write path (low QPS)
                          ▼
    ┌─────────────────────────────────────────────────────┐
    │                 BIDDING SERVICE                       │
    │  • Store bid configs (PostgreSQL)                   │
    │  • Track budgets (Redis — real-time counter)        │
    │  • Calculate bid eligibility                         │
    └─────────────────────┬───────────────────────────────┘
                          │
                          │ Pre-compute eligible bids
                          ▼
    ┌─────────────────────────────────────────────────────┐
    │              BID INDEX (Redis / In-Memory)           │
    │  destination → [(hotel_id, bid_amount, budget_left)]│
    └─────────────────────────────────────────────────────┘
                          │
                          │ Queried during search
                          ▼
    ┌─────────────────────────────────────────────────────┐
    │    SEARCH FLOW (50K QPS — read path)                │
    │                                                      │
    │  User Query                                          │
    │    ↓                                                 │
    │  1. Elasticsearch → Top 500 candidates               │
    │    ↓                                                 │
    │  2. Redis → Filter by availability                   │
    │    ↓                                                 │
    │  3. Feature Store → Fetch features                   │
    │    ↓                                                 │
    │  4. ML Ranker → Score organic ranking                │
    │    ↓                                                 │
    │  5. Bid Merger → Combine organic + sponsored         │
    │    ↓                                                 │
    │  6. Business Rules → Enforce slot limits, diversity  │
    │    ↓                                                 │
    │  Final Results (organic + sponsored, labeled)        │
    └─────────────────────────────────────────────────────┘
```

### Minute 20-35: Deep Dive into Components

**Interviewer:** "Let's deep dive into the Bid Merger. How do you combine organic and sponsored results?"

```python
# YOUR ANSWER:

class BidMerger:
    """
    Combines organic ML ranking with sponsored bids.
    
    Algorithm:
    1. Get organic ranked list from ML model
    2. Get eligible sponsored hotels (have budget, match destination)
    3. Score sponsored hotels: combined_score = α * ml_score + β * bid_amount
    4. Insert sponsored results into organic list at designated slots
    5. Charge the bid (deduct from budget)
    
    Design Decisions:
    - We DON'T just insert highest bidder at top → bad user experience!
    - Sponsored hotels MUST also have a minimum organic relevance score
    - This prevents irrelevant hotels from buying top placement
    """
    
    MAX_SPONSORED = 3       # Max sponsored in top 10
    SPONSORED_SLOTS = [0, 3, 7]  # Positions where sponsored can appear
    MIN_RELEVANCE = 0.3     # Minimum ML relevance score for sponsored
    
    def merge(self, organic_results: list, bid_index: dict, destination: str) -> list:
        # Step 1: Get eligible bids for this destination
        eligible_bids = self._get_eligible_bids(bid_index, destination)
        
        # Step 2: Filter bids with minimum relevance
        relevant_bids = [
            bid for bid in eligible_bids 
            if bid.hotel_id in organic_results 
            and self._get_ml_score(bid.hotel_id) >= self.MIN_RELEVANCE
        ]
        
        # Step 3: Rank bids by eCPM (expected cost per mille)
        # eCPM = P(click) * bid_amount
        # WHY eCPM? Maximizes revenue while considering user experience
        ranked_bids = sorted(
            relevant_bids,
            key=lambda b: self._get_click_prob(b.hotel_id) * b.bid_amount,
            reverse=True
        )
        
        # Step 4: Insert into organic results at designated slots
        final_results = list(organic_results)
        sponsored_count = 0
        
        for bid in ranked_bids:
            if sponsored_count >= self.MAX_SPONSORED:
                break
            
            slot = self.SPONSORED_SLOTS[sponsored_count]
            hotel_result = self._create_sponsored_result(bid)
            
            # Remove from organic position and insert at sponsored slot
            final_results = [r for r in final_results if r.hotel_id != bid.hotel_id]
            final_results.insert(slot, hotel_result)
            sponsored_count += 1
            
            # Deduct budget (async — fire and forget)
            self._charge_bid(bid)
        
        return final_results
    
    def _charge_bid(self, bid):
        """Deduct bid amount from hotel's daily budget using Redis DECR."""
        # Redis: DECR budget:{hotel_id}:{date} by bid_amount
        # Atomic operation — prevents overspending
        # If budget reaches 0 → hotel removed from bid index
        pass
```

**Interviewer:** "How do you ensure the budget doesn't go negative under high concurrency?"

```python
# YOUR ANSWER:

"""
Budget Management Under High Concurrency:

APPROACH: Optimistic Locking with Redis Atomic Operations

1. Use Redis DECRBY (atomic decrement):
   - DECRBY budget:hotel123:2024-01-15 500
   - This is an ATOMIC operation — no race condition
   - If result < 0, INCRBY to restore and reject the bid

2. Pre-sharding budgets:
   - For very high-traffic hotels, split daily budget across N shards
   - budget:hotel123:2024-01-15:shard_0, shard_1, ... shard_N
   - Each search request hits a random shard
   - More shards = less contention, but approximate budget tracking

3. Budget refresh loop:
   - Background job runs every N seconds
   - Reconciles Redis budgets with PostgreSQL source of truth
   - Handles edge cases (Redis restart, network issues)

4. Overspend tolerance:
   - Allow small overspend (e.g., 5%) to avoid complex locking
   - Reconcile in daily billing pipeline
"""

# Redis Lua script for atomic budget check + deduct
BUDGET_DEDUCT_SCRIPT = """
local current = tonumber(redis.call('GET', KEYS[1]))
if current == nil then
    return -1  -- Budget not found
end
local bid_amount = tonumber(ARGV[1])
if current >= bid_amount then
    redis.call('DECRBY', KEYS[1], bid_amount)
    return current - bid_amount  -- Return remaining budget
else
    return -2  -- Insufficient budget
end
"""
```

### Minute 35-45: Monitoring, Scaling & Trade-offs

**Interviewer:** "How would you monitor this system?"

```python
# YOUR ANSWER:

monitoring_strategy = {
    "Business Metrics": {
        "Bid fill rate":     "% of sponsored slots actually filled",
        "Advertiser ROI":    "Bookings generated per $ spent on bids",
        "Revenue per search":"Total revenue (booking + sponsored) per search",
        "User experience":   "CTR on sponsored vs organic results",
    },
    "Technical Metrics": {
        "Latency":          "p50/p95/p99 for bid merge step (should be < 10ms)",
        "Budget accuracy":  "Discrepancy between Redis counter and PostgreSQL",
        "Cache hit rate":   "Bid index cache hit rate (should be > 95%)",
        "Error rate":       "Failed bid lookups, budget charge failures",
    },
    "ML Metrics": {
        "Ranking quality":  "NDCG@10 with sponsored results (shouldn't degrade > 5%)",
        "Click prediction": "AUC-ROC of click probability model for sponsored",
        "Revenue uplift":   "A/B test: with bidding vs without",
    },
    "Alerting": {
        "P0 (Page)":       "Bidding service down, budget service unreachable",
        "P1 (Alert)":      "Latency p95 > 50ms, budget discrepancy > 10%",
        "P2 (Monitor)":    "CTR on sponsored drops > 20%, bid fill rate drops",
    },
}
```

**Interviewer:** "What are the key trade-offs in your design?"

```python
# YOUR ANSWER:

trade_offs = {
    "User Experience vs Revenue": {
        "Decision": "Require minimum ML relevance score for sponsored results",
        "Rationale": "Could boost short-term revenue by showing any bidder, "
                    "but degrades user experience and long-term L2B ratio",
    },
    "Consistency vs Availability (Budget)": {
        "Decision": "Allow 5% budget overspend, reconcile daily",
        "Rationale": "Strong consistency would require distributed locking, "
                    "adding 20-50ms latency. Eventual consistency acceptable "
                    "for billing.",
    },
    "Pre-computed vs Real-time Bid Scoring": {
        "Decision": "Pre-compute bid index, refresh every 30 seconds",
        "Rationale": "Real-time auction for every search would add latency. "
                    "30-second staleness is acceptable for bid eligibility.",
    },
    "Simple Rules vs ML for Bid Ranking": {
        "Decision": "Start with eCPM formula, evolve to ML-based auction",
        "Rationale": "Simple formula is transparent, easy to debug, and "
                    "explainable to hotel partners. ML can be added as V2.",
    },
}
```

---

## 2. Resume Deep-Dive Questions & Answers <a name="2-resume-deep-dive"></a>

### 🎯 Expect 10-15 Minutes on YOUR Projects

The interviewer WILL ask deep questions about your resume. Here's how to answer:

### Question Bank & Prepared Answers

```python
# ==========================================================
# Q1: "Tell me about your Hotel Ranking ML Platform.
#      Walk me through the architecture."
# ==========================================================

answer_ranking_platform = """
STRUCTURE: Use the STAR format (Situation → Task → Action → Result)

SITUATION:
"At Tiket.com, our hotel search results were ranked using hand-crafted 
rules — price, review score, and popularity as static weights. This led 
to suboptimal booking conversion because it didn't personalize results."

TASK:
"I was tasked with building an end-to-end ML ranking platform that could 
serve personalized rankings at the scale of millions of searches per day."

ACTION:
"I architected a 5-layer system:

1. DATA LAYER:
   - BigQuery for training data (user interactions, bookings, hotel features)
   - Designed point-in-time-correct feature extraction queries to prevent 
     data leakage

2. FEATURE LAYER:
   - Built Feast feature store backed by MongoDB
   - Online store (Redis) for real-time serving — sub-100ms p95 latency
   - Offline store (GCS/BigQuery) for training
   - Applied compression → 60% storage cost reduction

3. TRAINING LAYER:
   - Kubeflow pipelines for automated training
   - MLflow for experiment tracking and model registry
   - Random Forest and Gradient Boosting models with hyperparameter optimization
   - Training pipeline ran daily, full retrain weekly

4. SERVING LAYER:
   - FastAPI microservice serving predictions
   - ONNX Runtime for inference — 3x throughput vs TensorFlow
   - Supported 4+ concurrent model versions for A/B testing
   - Shadow deployment for safe model rollout

5. MONITORING LAYER:
   - Feature drift detection with PSI (Population Stability Index)
   - Model performance SLA tracking
   - Slack/email alerting for automated retraining triggers"

RESULT:
"- Model accuracy improved from 82% to 90%
- 60% storage cost reduction on feature store
- 3x throughput improvement with ONNX Runtime
- System handles millions of search queries per day"
"""


# ==========================================================
# Q2: "How did you reduce training time from ~7 hours to 22 minutes?"
# ==========================================================

answer_training_optimization = """
"This was a combination of 4 optimization layers:

1. DATA I/O OPTIMIZATION (before computation):
   - Switched from CSV to Parquet → 10x faster reads
   - Added column pruning — only read needed columns
   - Partitioned training data by date for faster filtered reads
   - Result: Data loading from 45 min → 5 min

2. FEATURE ENGINEERING OPTIMIZATION:
   - Parallelized independent feature groups using Python multiprocessing
   - Pre-computed expensive aggregations and stored in feature store
   - Used PySpark broadcast joins for dimension tables
   - Replaced Python UDFs with native PySpark functions
   - Result: Feature engineering from 3 hours → 8 minutes

3. TRAINING OPTIMIZATION:
   - Early stopping (monitor validation metric, stop when no improvement)
   - Bayesian hyperparameter optimization (vs Grid Search)
   - Feature selection — removed 30% low-importance features (faster training)
   - Result: Training from 2 hours → 7 minutes

4. PIPELINE ARCHITECTURE:
   - Separated feature computation from training (ran independently)
   - Incremental feature updates (only process new data since last run)
   - Used Kubeflow caching — skip unchanged pipeline steps
   - Result: End-to-end from 7 hours → 22 minutes"
"""


# ==========================================================
# Q3: "Explain your A/B testing and shadow deployment approach"
# ==========================================================

answer_ab_testing = """
"We supported 4+ concurrent ranking models simultaneously:

SHADOW DEPLOYMENT:
- New model runs in parallel with production model
- Both receive the same traffic, both compute predictions
- Only production model's predictions are served to users
- Shadow model's predictions are logged for offline comparison
- If shadow model outperforms production → promote to A/B test

A/B TESTING:
- Traffic split: 90% control (current model) / 10% treatment (new model)
- Randomized by user_id (hash-based) for consistency
- Minimum 7-day duration for statistical significance
- Primary metric: Booking Conversion Rate
- Guardrail metrics: Revenue per search, user satisfaction
- Automatic rollback if guardrail metrics drop > 3%

MULTI-VERSION SERVING:
- FastAPI service loads multiple ONNX models in memory
- Request routing based on user_id hash → determines model version
- Feature flags for percentage-based traffic splitting
- Gradual rollout: 5% → 25% → 50% → 100%"
"""


# ==========================================================
# Q4: "Tell me about the Dynamic Pricing RL agent"
# ==========================================================

answer_rl_pricing = """
SITUATION:
"We needed a system to dynamically adjust B2B commission rates to optimize 
both revenue and hotel partner retention."

WHY REINFORCEMENT LEARNING:
"Traditional supervised learning wouldn't work because:
1. It's a sequential decision problem — today's price affects tomorrow's bookings
2. We need exploration — try different prices to learn optimal policy
3. Delayed rewards — partner retention is measured over months
4. Non-stationary environment — market conditions change constantly"

THE RL SETUP:
"- State: Partner performance metrics (booking rate, revenue trend, competitor 
  rates, inventory level, seasonality index) — 15 dimensions
- Action: Price adjustment percentage (-5%, -3%, -1%, 0%, +1%, +3%, +5%)
- Reward: Weighted combination of booking revenue and partner satisfaction score
- Algorithm: DQN (Deep Q-Network) with experience replay
- Training: Historical interaction logs → offline training → online fine-tuning

CHALLENGES:
1. Exploration-Exploitation: Used epsilon-greedy with annealing schedule
   - Start with ε=0.3 (explore 30% of time)
   - Decay to ε=0.05 over 3 months
   
2. Safety Constraints: Added action masking
   - Can't increase price more than 10% in a week
   - Can't go below minimum contractual rate
   
3. Delayed Rewards: Used multi-step returns (n-step Q-learning)
   - Consider reward signal over 30-day horizon
   
4. Cold Start: For new partners, use population-level policy
   - As interaction data accumulates, personalize policy"

RESULT:
"Reduced model training & evaluation runtime from ~6-8 hours to 22 minutes 
via multiprocessing and optimized data pipelines."
"""


# ==========================================================
# Q5: "How did you handle feature drift detection?"
# ==========================================================

answer_feature_drift = """
"Feature drift is when the statistical distribution of input features 
changes over time, causing model performance to degrade.

DETECTION APPROACH:
1. Population Stability Index (PSI):
   - Compare distribution of each feature: training vs last 24h
   - PSI < 0.1 → stable
   - 0.1-0.25 → moderate shift → investigate
   - PSI > 0.25 → significant drift → trigger retraining

2. Implementation:
   - Daily batch job computes PSI for each feature
   - Store reference distributions from training data
   - Compare against latest inference data
   - Results stored in monitoring database

3. Alerting:
   - Moderate drift → Slack notification to ML team
   - Significant drift → Automatic retraining pipeline trigger
   - Combine with model performance metrics (if accuracy drops below SLA)

4. Root Cause Analysis:
   - Upstream data quality issues (source schema changed)
   - Seasonal shifts (holiday traffic patterns)
   - Business changes (new hotel partnerships)
   - External events (pandemic, new competitor)

CODE EXAMPLE:
```python
import numpy as np

def compute_psi(reference: np.ndarray, current: np.ndarray, bins: int = 10) -> float:
    '''Compute Population Stability Index between two distributions.'''
    # Bin the data
    breakpoints = np.linspace(
        min(reference.min(), current.min()),
        max(reference.max(), current.max()),
        bins + 1
    )
    
    ref_counts = np.histogram(reference, breakpoints)[0] + 1  # Add 1 to avoid log(0)
    cur_counts = np.histogram(current, breakpoints)[0] + 1
    
    ref_pct = ref_counts / ref_counts.sum()
    cur_pct = cur_counts / cur_counts.sum()
    
    psi = np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct))
    return psi
```"
"""


# ==========================================================
# Q6: "Tell me about the LLM chatbot you built"
# ==========================================================

answer_llm_chatbot = """
"I designed a production-ready LLM-powered chatbot using an agentic 
architecture:

ARCHITECTURE:
1. Agent Orchestration (LangChain):
   - Query classification → determines intent (search, book, FAQ)
   - Routes to appropriate tool based on intent
   
2. Hybrid Retrieval:
   - Semantic search via Milvus vector DB (3,500+ embeddings)
   - SQL filtering via PGVector for structured queries
   - Combined results for accurate content retrieval
   - Sub-second latency on retrieval

3. Tools (10+ integrations):
   - Hotel search, image analysis (OpenAI Vision)
   - Timer management, user preference tracking
   - Rate lookup, availability check

4. Conversational Memory:
   - Maintains user context across sessions
   - Tracks preferences and constraints
   - Enables personalized responses

5. Production Hardening:
   - Docker Compose orchestrating Milvus, PostgreSQL, FastAPI
   - Guardrails for safe LLM outputs
   - Structured response validation
   - Rate limiting and error handling"
"""
```

---

## 3. Agoda-Specific Domain Questions <a name="3-agoda-domain"></a>

```python
# ==========================================================
# QUESTIONS SPECIFIC TO AGODA'S BUSINESS DOMAIN
# ==========================================================

agoda_domain_questions = {
    "Q1: What is Look-to-Book (L2B) ratio and why does it matter?": {
        "Answer": """
        L2B = Number of searches / Number of bookings
        
        For Agoda, a typical L2B might be 50:1 (50 searches per booking).
        
        WHY IT MATTERS:
        - Lower L2B = users are finding what they want faster = better ranking
        - It's the PRIMARY metric for measuring search quality
        - Even a 1% improvement at Agoda's scale = millions in revenue
        
        HOW ML HELPS:
        - Personalized ranking → users see relevant hotels earlier
        - Better ranking → fewer searches needed → lower L2B → more bookings
        """,
    },
    
    "Q2: How would you handle the cold-start problem for new hotels?": {
        "Answer": """
        COLD START: New hotel has no booking/click history → model can't rank it.
        
        SOLUTIONS:
        1. Content-based features (don't need history):
           - Star rating, location, amenities, photo quality (ML-scored)
           - Price relative to market average
        
        2. Similar hotel proxy:
           - Find similar existing hotels (same city, star, price range)
           - Use their historical performance as initial signal
        
        3. Exploration boost:
           - Temporarily boost new hotels to gather click/booking data
           - Use Thompson Sampling or UCB to balance explore-exploit
        
        4. Multi-armed bandit:
           - Allocate a small percentage of impressions to new hotels
           - Quickly learn which new hotels perform well
        
        5. Transfer learning:
           - If hotel exists on other platforms, use that data
           - Use hotel chain/brand reputation as prior
        """,
    },
    
    "Q3: How do you handle seasonality in ML models?": {
        "Answer": """
        SEASONALITY: Travel demand varies by season, holidays, events.
        
        FEATURE ENGINEERING:
        - "is_peak_season" (summer, Chinese New Year, Christmas)
        - "is_holiday" (country-specific holidays)
        - "days_to_event" (proximity to major events)
        - "demand_index" (historical demand for this destination + time)
        - "same_period_last_year_bookings" (year-over-year comparison)
        
        MODEL DESIGN:
        - Time-based features allow the model to learn seasonal patterns
        - Regular retraining to capture shifting patterns
        - Separate models or model weights for peak vs off-peak
        
        DATA HANDLING:
        - Use at least 2 years of training data to capture full cycles
        - Ensure training data includes both peak and off-peak periods
        - Weight recent data higher (exponential decay)
        """,
    },
    
    "Q4: How would you prevent double bookings at scale?": {
        "Answer": """
        PROBLEM: Two users try to book the last room simultaneously.
        
        SOLUTION: Pessimistic locking at the inventory level.
        
        1. SEARCH TIME: Show availability from Redis cache (eventually consistent)
           - It's OK if slightly stale (user sees "available" but it's being booked)
        
        2. BOOKING TIME: Use distributed lock or optimistic locking in DB
           - BEGIN TRANSACTION
           - SELECT rooms_available FROM inventory WHERE hotel_id=X AND date=Y FOR UPDATE
           - IF rooms_available > 0: UPDATE rooms_available = rooms_available - 1
           - COMMIT
           
        3. POST-BOOKING: Update Redis cache asynchronously via Kafka
           - Booking event → Kafka → Redis consumer → update cache
        
        TRADE-OFF:
        - Search: AP (eventual consistency okay, show slightly stale availability)
        - Booking: CP (strong consistency, MUST prevent double bookings)
        """,
    },
    
    "Q5: What's Agoda's Featureflow? How does it relate to your experience?": {
        "Answer": """
        Agoda's Featureflow is their internal ML pipeline platform that:
        - Streamlines feature ideation → deployment lifecycle
        - Provides admin UI for creating feature sets via SQL
        - Automates data preprocessing and labeling
        
        MY SIMILAR EXPERIENCE at Tiket.com:
        - Built a comparable system using Feast + Kubeflow
        - Feature definitions in SQL → computed by PySpark → stored in MongoDB/Redis
        - Automated pipeline: feature definition → computation → serving → monitoring
        - Centralized feature store accelerated model development across teams
        
        I'D IMPROVE UPON IT BY:
        - Adding feature importance tracking (which models use which features)
        - Auto-deprecation of unused features
        - Feature version control with rollback capability
        """,
    },
}
```

---

## 4. Behavioral & Leadership Questions <a name="4-behavioral"></a>

```python
# ==========================================================
# BEHAVIORAL QUESTIONS — STAR FORMAT
# ==========================================================

# For Senior/Staff level, Agoda looks for:
# - Technical Leadership
# - Cross-team collaboration
# - Handling ambiguity
# - Ownership and impact

behavioral_questions = {
    "Q1: Tell me about a time you disagreed with a technical decision.": {
        "STAR": """
        SITUATION: At Tiket.com, the team proposed serving our ranking model 
        directly via TensorFlow Serving. I believed ONNX Runtime would be 
        better.
        
        TASK: I needed to convince the team with evidence, not just opinion.
        
        ACTION: I built a proof-of-concept comparing TensorFlow Serving vs 
        ONNX Runtime. I tested with production traffic patterns:
        - Same model, same features, same hardware
        - Measured latency (p50, p95, p99), throughput, and memory usage
        
        RESULT: ONNX Runtime showed 3x throughput improvement with lower 
        latency. The team adopted ONNX. I presented the results in a 
        brown-bag session and ONNX became our standard for model serving.
        """,
    },
    
    "Q2: How do you handle production incidents?": {
        "STAR": """
        SITUATION: Our ranking model's accuracy dropped significantly in 
        production — booking conversion rate fell 8% overnight.
        
        TASK: Identify root cause and fix immediately.
        
        ACTION: 
        1. TRIAGE (15 min): Checked monitoring dashboards. Feature drift 
           detector showed PSI > 0.25 for 'competitor_price' feature.
        2. ROOT CAUSE (30 min): Upstream data pipeline had a schema change 
           — competitor prices were coming in a different currency format.
        3. MITIGATION (10 min): Rolled back to previous model version using 
           our blue-green deployment setup.
        4. FIX (2 hours): Updated feature pipeline to handle new format, 
           retrained model, validated with shadow deployment.
        5. PREVENTION: Added data contract validation at Silver layer 
           boundary. Added schema drift detection to alerting.
        
        RESULT: 
        - Downtime: 45 minutes (detection to rollback)
        - Root cause identified and fixed same day
        - Prevention measures reduced similar incidents by 90%
        """,
    },
    
    "Q3: How do you mentor junior engineers?": {
        "STAR": """
        SITUATION: A junior ML engineer joined my team and was struggling 
        with production ML concepts — their background was research/academic.
        
        TASK: Help them become a productive team member capable of owning 
        production ML services.
        
        ACTION:
        1. Created onboarding document covering our ML platform architecture
        2. Paired programming on feature engineering tasks (low risk, high learning)
        3. Gradually increased responsibility: bug fixes → feature additions 
           → new model pipeline
        4. Weekly 1:1s reviewing their code and discussing design patterns
        5. Encouraged them to present at team tech talks
        
        RESULT: Within 3 months, they independently built and deployed a new 
        room-grouping ML service using our standard pipeline with proper 
        testing, monitoring, and documentation.
        """,
    },
    
    "Q4: How do you prioritize when multiple stakeholders want different things?": {
        "Answer": """
        "I use a framework based on IMPACT and EFFORT:
        
        1. QUANTIFY IMPACT: 
           - How much revenue/conversion will this improve?
           - How many users/partners are affected?
           - Is there a hard deadline (regulatory, contractual)?
        
        2. ESTIMATE EFFORT:
           - Engineering hours, dependencies, risks
           - Can we deliver an MVP first?
        
        3. COMMUNICATE TRANSPARENTLY:
           - Share the prioritization matrix with all stakeholders
           - Explain trade-offs clearly
           - Propose alternatives (e.g., 'We can't do X now, but here's a 
             simpler V1 that delivers 80% of the value')
        
        4. AT TIKET.COM:
           - Product wanted new ranking features
           - Partners wanted pricing model improvements  
           - I proposed a shared feature store that benefited both — 
             centralized features accelerated development for both teams."
        """,
    },
    
    "Q5: Tell me about a project you're most proud of.": {
        "Answer": """
        "The Hotel Ranking ML Platform at Tiket.com.
        
        WHY I'M PROUD:
        1. END-TO-END OWNERSHIP: I owned the entire lifecycle — from BigQuery 
           data to production serving to monitoring.
        
        2. MEASURABLE IMPACT: 
           - 82% → 90% accuracy
           - 60% storage cost reduction
           - 3x throughput with ONNX
           - Training time 7hrs → 22min
        
        3. PLATFORM THINKING: Built it as a reusable platform, not just a 
           one-off model. Other teams now build their models on the same 
           infrastructure.
        
        4. PRODUCTION MATURITY: Full monitoring, A/B testing, shadow 
           deployment, automated retraining — this is what separates 
           an ML experiment from an ML system."
        """,
    },
}
```

---

## 5. Questions to Ask the Interviewer <a name="5-ask-interviewer"></a>

```python
# ==========================================================
# SMART QUESTIONS TO ASK — Shows Depth & Genuine Interest
# ==========================================================

questions_to_ask = {
    "About the Team": [
        "What does the ML platform stack look like at Agoda today? "
        "I read about Featureflow — is that still the primary platform?",
        
        "How does the bidding team collaborate with the ranking team? "
        "Are they separate squads or part of the same group?",
        
        "What's the biggest technical challenge the ML team is facing right now?",
    ],
    
    "About the Role": [
        "What does a typical week look like for a Staff ML Engineer on the bidding team?",
        
        "How much time is spent on new feature development vs maintaining "
        "existing systems?",
        
        "What's the current model serving infrastructure? ONNX, TensorFlow Serving, "
        "custom?",
    ],
    
    "About Culture": [
        "Agoda has 90+ nationalities — how does the team handle technical "
        "decisions with such diverse perspectives?",
        
        "What's the experimentation culture like? How do you decide to ship "
        "a new model to production?",
        
        "What does career growth look like from Staff ML Engineer? "
        "Is there a technical track (Principal, Distinguished)?",
    ],
    
    "About Impact": [
        "What's the most impactful ML improvement the team has shipped recently?",
        
        "How do you measure success for the bidding system? "
        "Revenue per search, advertiser ROI, or something else?",
    ],
}
```

---

## 6. Final Cheat Sheet — Day-of-Interview Guide <a name="6-cheat-sheet"></a>

```
╔══════════════════════════════════════════════════════════════════╗
║               🎯 INTERVIEW DAY CHEAT SHEET                      ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  THE SUKH FRAMEWORK (For ALL design questions):                  ║
║  S → SCOPE    (Ask requirements, define constraints)            ║
║  U → UNDERSTAND (Data sources, features, scale)                 ║
║  K → KNIT     (Architecture diagram, components, models)        ║
║  H → HARDEN   (Monitoring, fallbacks, scaling, trade-offs)      ║
║                                                                  ║
║  YOUR RESUME POWER NUMBERS:                                     ║
║  • 82% → 90% accuracy improvement                               ║
║  • ~7 hrs → 22 min training time                                ║
║  • 60% storage cost reduction                                    ║
║  • 3x throughput (ONNX Runtime)                                 ║
║  • 4+ concurrent models (A/B testing)                           ║
║  • 3,500+ embeddings (LLM chatbot)                              ║
║  • Sub-100ms p95 latency                                        ║
║                                                                  ║
║  DESIGN PATTERNS (Pick the right one):                          ║
║  • Strategy  → Swap ranking algorithms / A/B test               ║
║  • Factory   → Create models from config                        ║
║  • Repository → Abstract data access                            ║
║  • Observer  → Event-driven monitoring                          ║
║  • Template  → ML pipeline skeleton                             ║
║  • Builder   → Complex pipeline config                          ║
║                                                                  ║
║  AGODA DOMAIN VOCABULARY:                                        ║
║  • L2B (Look-to-Book ratio)                                     ║
║  • OTA (Online Travel Agency)                                    ║
║  • eCPM (expected Cost Per Mille)                               ║
║  • Rate Parity (same price across channels)                     ║
║  • Cold Start (new hotels without data)                         ║
║  • Seasonality (travel demand patterns)                         ║
║  • Featureflow (Agoda's ML platform)                            ║
║  • Inventory Consistency (no double bookings)                   ║
║                                                                  ║
║  TRADE-OFF PHRASES TO USE:                                       ║
║  "I chose X over Y because..."                                  ║
║  "The trade-off here is between A and B..."                     ║
║  "In production, this means..."                                 ║
║  "At scale, the bottleneck would be..."                         ║
║  "A simpler approach would be... but it fails when..."         ║
║                                                                  ║
║  AVOID:                                                          ║
║  ❌ "I'd use SageMaker/Vertex AI" (explain the underlying design)║
║  ❌ Jumping to model without discussing data & features         ║
║  ❌ Forgetting to mention monitoring & fallbacks               ║
║  ❌ Not connecting answers to YOUR experience                   ║
║  ❌ One-word technology choices without justification           ║
║                                                                  ║
║  DO:                                                             ║
║  ✅ Ask clarifying questions first (always!)                    ║
║  ✅ Draw architecture diagrams (even on whiteboard)             ║
║  ✅ Discuss trade-offs at every decision point                  ║
║  ✅ Mention monitoring, alerting, fallback strategies           ║
║  ✅ Connect every answer to your Tiket.com experience          ║
║  ✅ Use numbers from your resume to support claims             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 📚 Recommended Study Plan (1 Week Before Interview)

```
Day 1: System Design Framework
  ├── Re-read Part 1: Hotel Ranking System Design
  ├── Practice drawing architecture diagrams
  └── Time yourself: can you present in 40 min?

Day 2: Python OOP & Patterns
  ├── Re-read Part 2: All 6 design patterns
  ├── Code the Strategy + Factory + Repository patterns from memory
  └── Practice code review exercise (BEFORE/AFTER)

Day 3: PySpark & Data Pipelines
  ├── Re-read Part 3: PySpark optimization techniques
  ├── Write 5 SQL window function queries from memory
  └── Review Medallion architecture

Day 4: Resume Deep-Dive Practice
  ├── Practice explaining each project in 5 minutes
  ├── Record yourself and listen back
  └── Prepare 3 follow-up details for each project

Day 5: Mock Interview Simulation  
  ├── Full 50-minute mock (use Part 4 mock)
  ├── Practice trade-off discussions
  └── Prepare questions for interviewer

Day 6: Agoda-Specific Prep
  ├── Read Agoda Engineering Blog (medium.com/agoda-engineering)
  ├── Review domain questions (L2B, cold start, seasonality)
  └── Study Agoda's Featureflow and data pipeline architecture

Day 7: Light Review & Rest
  ├── Skim cheat sheet
  ├── Review weak areas from practice
  └── Get good sleep — you've prepared well!
```

---

**You've got this, Sukh! 🚀**

Your Tiket.com experience maps almost 1:1 to Agoda's tech stack and challenges. The key is to **communicate clearly**, **connect to your experience**, and **always discuss trade-offs**.
