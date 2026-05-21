#!/usr/bin/env python3
"""CLI: Run VELA inference pipeline from a RunSpec YAML (requires prior training + promote)."""
import argparse
from pathlib import Path

from vela.core import load_run_spec
from vela.pipelines.inference_pipeline import run_inference_pipeline
from vela.operators.artifact_store_impl import LocalArtifactStore


def main():
    p = argparse.ArgumentParser(description="VELA Inference Pipeline")
    p.add_argument("run_spec", type=Path, help="Path to RunSpec YAML (pipeline_type can be inference)")
    p.add_argument("-o", "--output", type=Path, default=Path("vela_output"), help="Output base dir (same as training)")
    args = p.parse_args()

    spec = load_run_spec(args.run_spec)
    if spec.pipeline_type != "inference":
        from vela.core.run_spec import RunSpec
        spec = RunSpec.from_dict({**spec.to_dict(), "pipeline_type": "inference"})
    store = LocalArtifactStore(args.output / "artifacts")
    result = run_inference_pipeline(spec, args.output, artifact_store=store)

    print("Output path:", result["output_path"])
    print("Num rows:", result["num_rows"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
