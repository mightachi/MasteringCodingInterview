# Generic RL Pipeline POC (Exploration)

|  |  |
| --- | --- |
| **Exploration Date** | 2026-03-10 |
| **Jira Link** | [*DAS-5702*](https://borobudur.atlassian.net/browse/DAS-5702) |
| **Objective** | *Design and build a POC for a generic, pipeline-based reinforcement learning platform with a dashboard to build, visualise, and run RL pipelines, orchestrated by Kubeflow on GCP—reusable across projects (e.g. Orion B2B, MUSCA).* |
| **Conclusion** | *POC design delivered: HLD and LLD with SOLID/modular design, config-driven pipeline template (training, policy refinement, batch inference), cost-effective tech stack. Dashboard to visualise pipeline DAG and trigger runs; implementation can follow the LLD for handoff.* |

---

## Overview

- **Explore a generic RL pipeline template** that can be reused across projects (Orion B2B, MUSCA, etc.), aligned with existing Confluence architecture: [Orion B2B v3.0 Reinforcement Learning Model](https://borobudur.atlassian.net/wiki/spaces/DSMLE/pages/4098886341), [Orion B2B Magnitude Model](https://borobudur.atlassian.net/wiki/spaces/DSMLE/pages/4098886402).
- **Deliver a POC** that includes:
  - **High-Level Design (HLD):** system context, pipeline types (training, policy refinement, batch inference), requirements, tech stack.
  - **Low-Level Design (LLD):** package layout, interfaces, design patterns (Strategy, Template Method, Factory, Repository, Adapter), SOLID, operators and pipeline composition.
  - **Dashboard:** build pipeline definitions from a template, visualise pipeline DAG, trigger runs, view run status (Kubeflow on GKE).
  - **Cost-effective tech stack:** FastAPI, Kubeflow Pipelines on GKE, MLflow, GCS, Cloud SQL/Firestore, React/Vue or Streamlit for the dashboard.

---

## Task Description – POC Scope

| Pillar | Description |
| --- | --- |
| **HLD & requirements** | Document system context, three pipeline types (training, policy refinement, batch inference), functional/non-functional requirements, architecture decisions, success criteria. |
| **LLD & design patterns** | Modular package layout; core interfaces (IDataExtractor, IDataProcessor, IArtifactStore, IModelTrainer, IModelPredictor); SOLID mapping; Strategy, Template Method, Factory, Repository, Adapter; operator and pipeline classes; API services (config + run orchestration). |
| **Pipeline orchestration** | Generic RL template runs on **Kubeflow Pipelines (GKE)**; reusable operators: Data Extraction → Data Processing → (HPO) → Train/Refine → Model Wrapper → Batch Prediction → Consolidation/Publish; artifacts in MLflow and GCS. |
| **Dashboard** | Web UI to create/edit pipeline definitions from template, visualise pipeline DAG, trigger runs, and show run status (and optionally link to KFP UI for logs). |
| **Tech stack** | Cost-effective: Python FastAPI, Kubeflow on GKE (with preemptible/Spot for cost), MLflow, GCS, PostgreSQL or Firestore; dashboard: React/Vue or Streamlit. |

---

## High-Level Design Summary

### System Context

- **Dashboard** → Pipeline API / Config Service → **Kubeflow Pipelines (GKE)** (training, policy refinement, batch inference).
- **Storage:** GCS (raw/processed data), MLflow (models, scalers, wrapper), BigQuery optional (features/outputs).
- **Output:** Downstream systems (e.g. Kafka, Kuber) consume predictions.

### Pipeline Types (Generic Template)

| Pipeline | Purpose | Typical schedule | Main operators |
| --- | --- | --- | --- |
| **Training** | First-time RL model training (e.g. A2C/SAC) | On-demand / weekly | Data Extract → Process → HPO → Train+Wrap → MLflow |
| **Policy Refinement** | Update policy with latest data | Weekly (e.g. Sunday) | Data Extract → Process (scaler from MLflow) → Refine → Wrap → MLflow |
| **Batch Inference** | Score entities, publish actions | Weekly/daily | Data Extract → Process → Predict → Consolidate → BigQuery/Kafka |

### Key Requirements (Summary)

- **FR-1–FR-4:** Dashboard: create/edit pipelines from template, visualise DAG, trigger runs, show run status (Kubeflow).
- **FR-5–FR-8:** Configurable data source, segments, reward weights, algorithm; training/refinement/inference pipelines as above.
- **NFR:** Cost-effective stack, modular/reusable design, SOLID, versioning via MLflow and run metadata.

### Cost-Effective Tech Stack

| Layer | Technology |
| --- | --- |
| Dashboard | React or Vue (or Streamlit for fast POC) |
| Backend API | Python (FastAPI) |
| Pipeline orchestration | Kubeflow Pipelines on GKE |
| Config & run metadata | PostgreSQL (Cloud SQL) or Firestore |
| Object storage | GCS |
| Model registry | MLflow (self-hosted on GKE or Cloud) |
| Data source | BigQuery (optional) + GCS |
| DAG visualisation | React Flow / ELK or embed KFP UI |

*Cost levers:* Autoscaling GKE, preemptible/Spot nodes for training and batch inference.

---

## Low-Level Design Summary

### Package Layout (Modular)

- **core/** – Interfaces (IDataExtractor, IDataProcessor, IArtifactStore, IModelTrainer, IModelPredictor), domain entities (PipelineDefinition, RunMetadata, RLTrainingConfig).
- **operators/** – Kubeflow step implementations (DataExtraction, DataProcessing, HPO, Training, Refinement, Prediction, Consolidation) delegating to core interfaces.
- **pipelines/** – KFP DAG definitions (TrainingPipeline, RefinementPipeline, InferencePipeline) using Template Method.
- **api/** – Routes (pipelines, runs, templates), services (PipelineConfigService, RunOrchestrationService), Kubeflow client.

### Design Patterns

| Pattern | Where | Purpose |
| --- | --- | --- |
| Strategy | Algorithm (A2C vs SAC), data source (BQ vs GCS) | Swap behaviour per project without changing pipeline code. |
| Template Method | Base pipeline (training/refinement/inference) | Define skeleton; subclasses fill steps. |
| Factory | Operator creation from config | Create the right operator from template. |
| Repository | Pipeline config, run metadata | Abstract persistence. |
| Adapter | Kubeflow component ↔ core interfaces | KFP components call core logic; testable. |
| Dependency Injection | Services and operators | Inject artifact store, data source, etc. |

### SOLID Mapping

| Principle | Application |
| --- | --- |
| **S** – Single Responsibility | Each operator does one thing; config service only pipeline definitions; run service only orchestration. |
| **O** – Open/Closed | New pipeline types/operators extend base classes or implement interfaces. |
| **L** – Liskov Substitution | Any IDataExtractor/IDataProcessor/… implementation can be swapped in. |
| **I** – Interface Segregation | Small interfaces per concern. |
| **D** – Dependency Inversion | Pipelines and services depend on abstractions; implementations injected. |

### Dashboard DAG Contract (API)

Backend exposes pipeline DAG for the dashboard, e.g.:

- **nodes:** list of { id, label, type } (e.g. extract, process, hpo, train, wrap).
- **edges:** list of { from, to } (e.g. extract → process → hpo → train → wrap).

Run status from `/runs/{run_id}`; optional link to KFP UI for logs.

---

## Document References

- **Jira:** [DAS-5702](https://borobudur.atlassian.net/browse/DAS-5702) – [MLE] Create Architecture for Musca
- **Confluence:** [Orion B2B Magnitude Model (Orion V4.0)](https://borobudur.atlassian.net/wiki/spaces/DSMLE/pages/4098886402)
- **Confluence:** [Orion B2B v3.0 Reinforcement Learning Model](https://borobudur.atlassian.net/wiki/spaces/DSMLE/pages/4098886341)
- **Confluence:** [Orion B2B AB Test V3.0 vs NML – Difference-in-Differences Analysis](https://borobudur.atlassian.net/wiki/spaces/DSMLE/pages/4565696554)
- **Reference exploration format:** [new FalkorDB](https://borobudur.atlassian.net/wiki/spaces/DSMLE/pages/4663804126)

---

## Conclusion

The POC delivers a **generic RL pipeline template** and design suitable for reuse across projects (Orion B2B, MUSCA). The **HLD** defines system context, three pipeline types, requirements, and a cost-effective tech stack (Kubeflow on GKE, MLflow, GCS, FastAPI, React/Vue or Streamlit). The **LLD** provides a modular package layout, core interfaces, SOLID-aligned design, and patterns (Strategy, Template Method, Factory, Repository, Adapter) so new projects can plug in implementations without changing pipeline composition. The **dashboard** is specified to build pipelines from a template, visualise the DAG, and trigger runs with status visibility. Full design details (including Mermaid diagrams and code-level interfaces) are in the repo: `rl_pipeline_poc/DESIGN.md` and `rl_pipeline_poc/LLD.md`. Next step: implement API + operators + dashboard following the LLD and integrate with Kubeflow.
