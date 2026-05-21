#!/usr/bin/env python3
"""CLI: Run VELA training pipeline from a RunSpec YAML."""
import argparse
from pathlib import Path

from vela.core import load_run_spec
from vela.pipelines.training_pipeline import run_training_pipeline
from vela.operators.artifact_store_impl import LocalArtifactStore


def main():
    p = argparse.ArgumentParser(description="VELA Training Pipeline")
    p.add_argument("run_spec", type=Path, help="Path to RunSpec YAML")
    p.add_argument("-o", "--output", type=Path, default=Path("vela_output"), help="Output base dir")
    p.add_argument("--promote", action="store_true", help="Promote to PROD if gates pass")
    args = p.parse_args()

    spec = load_run_spec(args.run_spec)
    store = LocalArtifactStore(args.output / "artifacts")
    result = run_training_pipeline(spec, args.output, artifact_store=store, promote_to_prod=args.promote)

    print("Run ID:", result["run_id"])
    print("Output dir:", result["output_dir"])
    print("Eval passed:", result["eval_passed"])
    if result.get("eval_reasons"):
        print("Reasons:", result["eval_reasons"])
    print("Reward/episode:", result["train_metrics"]["reward_per_episode"])
    if result.get("promoted_to_prod"):
        print("Promoted to PROD.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
