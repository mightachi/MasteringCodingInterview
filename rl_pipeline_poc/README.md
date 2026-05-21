# VELA POC – Generic RL Pipeline for Dynamic Pricing

Proof-of-concept implementation of **[VELA: Custom Reinforcement Learning Framework for Dynamic Pricing](https://borobudur.atlassian.net/wiki/spaces/DSMLE/pages/4682547367)**. Config-driven training, refinement, and inference pipelines with discrete action space (A2C/PPO), evaluation gates, and artifact store (local/MLflow).

## Quick Start

```bash
cd rl_pipeline_poc
pip install -r requirements.txt
# Training (synthetic data if no data path in RunSpec)
python run_training.py config/run_spec_example.yaml -o vela_output --promote
# Inference (after at least one promoted policy)
python run_inference.py config/run_spec_example.yaml -o vela_output
# Dashboard
streamlit run dashboard/app.py
```

## Contents

| Document | Description |
|----------|-------------|
| [CONFLUENCE_VELA_PAGE.md](./CONFLUENCE_VELA_PAGE.md) | **POC doc for Confluence:** tech stack, workflow, HLD, LLD, sequence diagrams, architecture, **how to use** to build RL training/inference for a project. |
| [DESIGN.md](./DESIGN.md) | **HLD**: system context, pipeline types, requirements, tech stack. |
| [LLD.md](./LLD.md) | **LLD**: package layout, design patterns, SOLID, interfaces, operators. |

## Goals

1. **RunSpec-driven:** dataset, features, reward, actions, algorithm (A2C/PPO), evaluation gates—all from YAML; no code change per project.
2. **Three pipelines:** Training (full train), Policy Refinement (warm start), Inference (batch + guardrails).
3. **Dashboard** (Streamlit): visualise workflow, trigger training/inference, view RunSpec and results.
4. **Artifact-first:** versioned preprocessors, policies, PROD alias for promotion/rollback.

## Repo Layout

- **vela/** – Core (RunSpec, domain, interfaces), envs (PricingEnv), operators, pipelines.
- **config/run_spec_example.yaml** – Example RunSpec.
- **run_training.py**, **run_inference.py** – CLI entrypoints.
- **dashboard/app.py** – Streamlit UI.
