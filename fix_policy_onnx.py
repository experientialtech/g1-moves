#!/usr/bin/env python3
"""Fix the actor-only policy/<clip>_policy.onnx files in the dataset.

Two problems with the original export:
1. No metadata, so nothing told a deployer the joint order, default pose,
   action scale or gains.
2. Observation normalization divided by std, but rsl_rl's normalizer (used in
   training) divides by std + 0.01. The actions differed from the trained policy.

This patches the normalizer and copies the metadata from the sibling
policy/<clip>.onnx (written by export_onnx.py), then checks that both files
produce the same actions.

Usage:
    python fix_policy_onnx.py <dataset_dir>            # all clips
    python fix_policy_onnx.py <dataset_dir> --check    # report only
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort
from onnx import numpy_helper

NORMALIZER_EPS = 0.01  # rsl_rl EmpiricalNormalization eps


def patch_normalizer(model: onnx.ModelProto) -> bool:
    """Add eps to the std constant feeding the first Div node."""
    inits = {i.name: i for i in model.graph.initializer}
    for node in model.graph.node:
        if node.op_type == "Div" and node.input[1] in inits:
            init = inits[node.input[1]]
            std = numpy_helper.to_array(init)
            init.CopyFrom(numpy_helper.from_array(std + NORMALIZER_EPS, init.name))
            return True
    return False


def same_actor(bare, full: Path) -> bool:
    if isinstance(bare, onnx.ModelProto):
        bare = bare.SerializeToString()
    else:
        bare = str(bare)
    a = ort.InferenceSession(bare, providers=["CPUExecutionProvider"])
    b = ort.InferenceSession(str(full), providers=["CPUExecutionProvider"])
    dim = a.get_inputs()[0].shape[1]
    obs = np.random.default_rng(0).normal(size=(1, dim)).astype(np.float32)
    ya = a.run(["actions"], {"obs": obs})[0]
    yb = b.run(["actions"], {"obs": obs, "time_step": np.zeros((1, 1), np.float32)})[0]
    return np.allclose(ya, yb, atol=1e-5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset_dir", type=Path)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    done = skipped = failed = 0
    for bare in sorted(args.dataset_dir.glob("*/*/policy/*_policy.onnx")):
        clip = bare.name[: -len("_policy.onnx")]
        full = bare.with_name(f"{clip}.onnx")
        model = onnx.load(str(bare))
        if not full.exists():
            print(f"FAIL {clip}: no {full.name} to copy metadata from")
            failed += 1
            continue
        has_meta = {p.key for p in model.metadata_props} >= {"joint_names", "action_scale"}
        if not same_actor(model, full):
            if not (patch_normalizer(model) and same_actor(model, full)):
                print(f"FAIL {clip}: {bare.name} and {full.name} contain different actors")
                failed += 1
                continue
        elif has_meta:
            skipped += 1
            continue
        if args.check:
            print(f"would update {bare}")
            done += 1
            continue
        meta = onnx.load(str(full), load_external_data=False).metadata_props
        del model.metadata_props[:]
        for p in meta:
            model.metadata_props.add(key=p.key, value=p.value)
        onnx.save(model, str(bare))
        print(f"updated {bare}")
        done += 1
    print(f"{done} {'to update' if args.check else 'updated'}, {skipped} already fixed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
