"""VELA Dashboard: build pipeline from RunSpec, visualise workflow, trigger training/inference."""
import json
from pathlib import Path

import streamlit as st

# Add project root for imports
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vela.core import load_run_spec
from vela.pipelines.training_pipeline import run_training_pipeline
from vela.pipelines.inference_pipeline import run_inference_pipeline
from vela.operators.artifact_store_impl import LocalArtifactStore


st.set_page_config(page_title="VELA RL Pipeline", layout="wide")
st.title("VELA: Custom RL Framework for Dynamic Pricing")

st.sidebar.header("Pipeline")
pipeline_type = st.sidebar.radio("Type", ["Training", "Inference"], index=0)
output_base = Path(st.sidebar.text_input("Output base dir", value="vela_output"))
spec_path = st.sidebar.text_input("RunSpec YAML path", value="config/run_spec_example.yaml")

# Workflow / DAG visualisation
st.header("Pipeline Workflow")
if pipeline_type == "Training":
    st.markdown("""
    **Training pipeline (RunSpec-driven):**
    1. **Data Extraction** → raw_dataset.parquet + dataset_metadata.json  
    2. **Feature Preprocessing** → train_features.parquet, val_features.parquet, preprocess_artifacts/  
    3. **Training (A2C/PPO)** → policy_checkpoint + train_metrics.json  
    4. **Evaluation & Gates** → eval_report.json (PASS/FAIL)  
    5. **Registry** → MLflow/local; optional promote to PROD  
    """)
else:
    st.markdown("""
    **Inference pipeline:**
    1. **Policy Fetch** → load PROD policy from artifact store  
    2. **Inference Data Build** → raw_dataset.parquet  
    3. **Preprocess Apply** → reuse saved transformers  
    4. **Policy Inference** → discrete action per entity  
    5. **Consolidator + Guardrails** → clamp delta, bounds  
    6. **Publish** → final_decisions.parquet (or BigQuery)  
    """)

# RunSpec summary
st.header("RunSpec Summary")
spec_file = Path(spec_path)
if spec_file.exists():
    try:
        spec = load_run_spec(spec_file)
        st.json(spec.to_dict())
    except Exception as e:
        st.error(str(e))
else:
    st.warning("RunSpec file not found. Use default or set path in sidebar.")

# Run pipeline
st.header("Run Pipeline")
promote = st.checkbox("Promote to PROD (training only, if gates pass)", value=False) if pipeline_type == "Training" else False
if st.button("Run"):
    if not spec_file.exists():
        st.error("RunSpec file not found.")
    else:
        try:
            spec = load_run_spec(spec_file)
            store = LocalArtifactStore(output_base / "artifacts")
            if pipeline_type == "Training":
                with st.spinner("Running training pipeline..."):
                    result = run_training_pipeline(spec, output_base, artifact_store=store, promote_to_prod=promote)
                st.success("Training completed.")
                st.json(result)
            else:
                with st.spinner("Running inference pipeline..."):
                    result = run_inference_pipeline(spec, output_base, artifact_store=store)
                st.success("Inference completed.")
                st.json(result)
        except Exception as e:
            st.exception(e)

st.sidebar.markdown("---")
st.sidebar.markdown("[VELA Confluence](https://borobudur.atlassian.net/wiki/spaces/DSMLE/pages/4682547367)")
