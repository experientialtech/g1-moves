"""Export a trained checkpoint to ONNX with bundled motion data.

Usage:
    uv run python export_onnx.py <category>/<clip>
    uv run python export_onnx.py bonus/B_Fence1
    uv run python export_onnx.py --all              # export all clips with policies
"""

import argparse
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import cast

import torch
from torch import nn

import mjlab.tasks  # noqa: F401 (populate registry)
from mjlab.envs import ManagerBasedRlEnv
from mjlab.rl import RslRlVecEnvWrapper
from mjlab.rl.exporter_utils import attach_metadata_to_onnx, get_base_metadata
from mjlab.tasks.registry import load_env_cfg, load_rl_cfg, load_runner_cls
from mjlab.tasks.tracking.mdp.commands import MotionCommand, MotionCommandCfg
from mjlab.tasks.tracking.rl.runner import MotionTrackingOnPolicyRunner
from mjlab.utils.torch import configure_torch_backends

TASK = "Mjlab-Tracking-Flat-Unitree-G1"
REPO_DIR = Path(__file__).resolve().parent


class _OnnxActorModel(nn.Module):
    """ONNX-exportable wrapper for the actor MLP + obs normalizer."""

    def __init__(self, actor_critic):
        super().__init__()
        self.normalizer = actor_critic.actor_obs_normalizer
        self.actor = actor_critic.actor
        # Get input size from first Linear layer
        for layer in self.actor:
            if isinstance(layer, nn.Linear):
                self.input_size = layer.in_features
                break

    def forward(self, x):
        return self.actor(self.normalizer(x))


class _OnnxMotionModel(nn.Module):
    """ONNX-exportable model wrapping the policy and motion reference data."""

    def __init__(self, actor_model, motion):
        super().__init__()
        self.policy = actor_model
        self.register_buffer("joint_pos", motion.joint_pos.to("cpu"))
        self.register_buffer("joint_vel", motion.joint_vel.to("cpu"))
        self.register_buffer("body_pos_w", motion.body_pos_w.to("cpu"))
        self.register_buffer("body_quat_w", motion.body_quat_w.to("cpu"))
        self.register_buffer("body_lin_vel_w", motion.body_lin_vel_w.to("cpu"))
        self.register_buffer("body_ang_vel_w", motion.body_ang_vel_w.to("cpu"))
        self.time_step_total: int = self.joint_pos.shape[0]

    def forward(self, x, time_step):
        time_step_clamped = torch.clamp(
            time_step.long().squeeze(-1), max=self.time_step_total - 1
        )
        return (
            self.policy(x),
            self.joint_pos[time_step_clamped],
            self.joint_vel[time_step_clamped],
            self.body_pos_w[time_step_clamped],
            self.body_quat_w[time_step_clamped],
            self.body_lin_vel_w[time_step_clamped],
            self.body_ang_vel_w[time_step_clamped],
        )


def export_clip(category: str, clip: str, device: str = "cuda:0"):
    """Export a single clip's policy to ONNX."""
    clip_dir = REPO_DIR / category / clip
    checkpoint = clip_dir / "policy" / f"{clip}_policy.pt"
    motion = clip_dir / "training" / f"{clip}.npz"
    output_dir = clip_dir / "policy"
    output_name = f"{clip}.onnx"

    if not checkpoint.exists():
        print(f"SKIP {category}/{clip} — no policy checkpoint")
        return False
    if not motion.exists():
        print(f"SKIP {category}/{clip} — no training NPZ")
        return False

    print(f"Exporting {category}/{clip}...")

    env_cfg = load_env_cfg(TASK, play=True)
    agent_cfg = load_rl_cfg(TASK)

    motion_cmd = env_cfg.commands["motion"]
    assert isinstance(motion_cmd, MotionCommandCfg)
    motion_cmd.motion_file = str(motion)

    env_cfg.scene.num_envs = 1
    env = ManagerBasedRlEnv(cfg=env_cfg, device=device)
    env_wrapped = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)

    runner_cls = load_runner_cls(TASK) or MotionTrackingOnPolicyRunner
    runner = runner_cls(env_wrapped, asdict(agent_cfg), device=device)
    runner.load(str(checkpoint), load_optimizer=False, map_location=device)

    # Build ONNX model directly (bypasses runner.export_policy_to_onnx which
    # relies on PPO.get_policy() / ActorCritic.as_onnx() that don't exist in
    # the installed rsl_rl version).
    actor_model = _OnnxActorModel(runner.alg.policy)
    motion_term = cast(MotionCommand, env.command_manager.get_term("motion"))
    model = _OnnxMotionModel(actor_model, motion_term.motion)
    model.to("cpu")
    model.eval()

    os.makedirs(str(output_dir), exist_ok=True)
    obs = torch.zeros(1, actor_model.input_size)
    time_step = torch.zeros(1, 1)
    torch.onnx.export(
        model,
        (obs, time_step),
        str(output_dir / output_name),
        export_params=True,
        opset_version=18,
        verbose=False,
        input_names=["obs", "time_step"],
        output_names=[
            "actions",
            "joint_pos",
            "joint_vel",
            "body_pos_w",
            "body_quat_w",
            "body_lin_vel_w",
            "body_ang_vel_w",
        ],
        dynamic_axes={},
        dynamo=False,
    )

    metadata = get_base_metadata(env, "local")
    metadata.update(
        {
            "anchor_body_name": motion_term.cfg.anchor_body_name,
            "body_names": list(motion_term.cfg.body_names),
        }
    )
    attach_metadata_to_onnx(str(output_dir / output_name), metadata)

    print(f"  Exported: {output_dir / output_name}")
    env.close()
    return True


def find_all_clips_with_policies():
    """Find all clips that have a trained policy checkpoint."""
    clips = []
    for category in ["bonus", "dance", "karate"]:
        cat_dir = REPO_DIR / category
        if not cat_dir.is_dir():
            continue
        for clip_dir in sorted(cat_dir.iterdir()):
            if not clip_dir.is_dir():
                continue
            clip = clip_dir.name
            pt = clip_dir / "policy" / f"{clip}_policy.pt"
            npz = clip_dir / "training" / f"{clip}.npz"
            if pt.exists() and npz.exists():
                clips.append((category, clip))
    return clips


def main():
    parser = argparse.ArgumentParser(description="Export trained policies to ONNX")
    parser.add_argument("clip", nargs="?", help="category/clip (e.g. bonus/B_Fence1)")
    parser.add_argument("--all", action="store_true", help="Export all clips with policies")
    parser.add_argument("--device", default="cuda:0", help="Device (default: cuda:0)")
    args = parser.parse_args()

    if not args.clip and not args.all:
        parser.print_help()
        sys.exit(1)

    configure_torch_backends()
    device = args.device if torch.cuda.is_available() else "cpu"

    if args.all:
        clips = find_all_clips_with_policies()
        print(f"Found {len(clips)} clips with trained policies")
        ok, skip = 0, 0
        for category, clip in clips:
            onnx = REPO_DIR / category / clip / "policy" / f"{clip}.onnx"
            if onnx.exists():
                print(f"SKIP {category}/{clip} — ONNX already exists")
                skip += 1
                continue
            if export_clip(category, clip, device):
                ok += 1
            else:
                skip += 1
        print(f"\nDone: {ok} exported, {skip} skipped")
    else:
        parts = args.clip.strip("/").split("/")
        if len(parts) != 2:
            print(f"Expected category/clip, got: {args.clip}")
            sys.exit(1)
        category, clip = parts
        if not export_clip(category, clip, device):
            sys.exit(1)


if __name__ == "__main__":
    main()
