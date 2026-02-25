"""Export a trained checkpoint to ONNX with bundled motion data."""

import sys
from dataclasses import asdict
from pathlib import Path
from typing import cast

import torch

import mjlab.tasks  # noqa: F401 (populate registry)
from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import RslRlVecEnvWrapper
from mjlab.rl.exporter_utils import attach_metadata_to_onnx, get_base_metadata
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
from mjlab.tasks.tracking.mdp.commands import MotionCommand, MotionCommandCfg
from mjlab.tasks.tracking.rl.runner import MotionTrackingOnPolicyRunner
from mjlab.utils.torch import configure_torch_backends

TASK = "Mjlab-Tracking-Flat-Unitree-G1"
CHECKPOINT = "/home/sparky/git/g1-moves/bonus/B_Fence1/policy/B_Fence1_policy.pt"
MOTION = "/home/sparky/git/g1-moves/bonus/B_Fence1/training/B_Fence1.npz"
OUTPUT_DIR = "/home/sparky/git/g1-moves/bonus/B_Fence1/policy"
OUTPUT_NAME = "B_Fence1.onnx"

configure_torch_backends()
device = "cuda:0" if torch.cuda.is_available() else "cpu"

env_cfg = load_env_cfg(TASK, play=True)
agent_cfg = load_rl_cfg(TASK)

# Point to local motion file
motion_cmd = env_cfg.commands["motion"]
assert isinstance(motion_cmd, MotionCommandCfg)
motion_cmd.motion_file = MOTION

env_cfg.scene.num_envs = 1
env = ManagerBasedRlEnv(cfg=env_cfg, device=device)
env_wrapped = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)

runner_cls = load_runner_cls(TASK) or MotionTrackingOnPolicyRunner
runner = runner_cls(env_wrapped, asdict(agent_cfg), device=device)
runner.load(CHECKPOINT, load_cfg={"actor": True}, strict=True, map_location=device)

# Export ONNX
runner.export_policy_to_onnx(OUTPUT_DIR, OUTPUT_NAME)

# Attach metadata
motion_term = cast(MotionCommand, env.command_manager.get_term("motion"))
metadata = get_base_metadata(env, "local")
metadata.update(
    {
        "anchor_body_name": motion_term.cfg.anchor_body_name,
        "body_names": list(motion_term.cfg.body_names),
    }
)
attach_metadata_to_onnx(str(Path(OUTPUT_DIR) / OUTPUT_NAME), metadata)

print(f"Exported: {Path(OUTPUT_DIR) / OUTPUT_NAME}")
env.close()
