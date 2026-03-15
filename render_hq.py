#!/usr/bin/env python3
"""Render a high-quality front-facing video of a G1 Moves policy using mjlab.

Uses mjlab's actual environment (correct actuators, PD gains, model) to render
the policy rollout. No ghost overlay.

Usage:
    cd ~/Repositories/mjlab-gui
    MUJOCO_GL=egl uv run python ~/Repositories/g1-moves/render_hq.py dance/B_SpiralDance
    MUJOCO_GL=egl uv run python ~/Repositories/g1-moves/render_hq.py dance/B_SpiralDance --width 1920 --height 1080
"""

import argparse
import sys
from dataclasses import asdict
from pathlib import Path

import torch

from mjlab.scripts.play import PlayConfig, run_play

# Monkey-patch to disable ghost and set video resolution before env creation
_original_run_play = run_play


def patched_run_play(task_id, cfg):
    from mjlab.tasks.registry import load_env_cfg, load_rl_cfg
    from mjlab.tasks.tracking.mdp import MotionCommandCfg

    env_cfg = load_env_cfg(task_id, play=True)

    # Disable ghost visualization
    if "motion" in env_cfg.commands:
        motion_cmd = env_cfg.commands["motion"]
        if isinstance(motion_cmd, MotionCommandCfg):
            motion_cmd.viz.mode = "none"

    _original_run_play(task_id, cfg)


def main():
    import mjlab.tasks  # noqa: F401 (populate registry)

    parser = argparse.ArgumentParser(description="Render HQ policy video (no ghost)")
    parser.add_argument("clip", help="Clip path, e.g. 'dance/B_SpiralDance'")
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--video-length", type=int, default=None,
                        help="Number of steps to record (default: auto from motion)")
    args = parser.parse_args()

    g1_moves = Path(__file__).resolve().parent
    clip_dir = g1_moves / args.clip
    clip_name = clip_dir.name

    npz_path = clip_dir / "training" / f"{clip_name}.npz"
    if not npz_path.exists():
        print(f"NPZ not found: {npz_path}")
        sys.exit(1)

    # Find checkpoint
    import numpy as np
    motion = np.load(str(npz_path))
    num_frames = motion["joint_pos"].shape[0]
    fps = float(motion["fps"])
    duration_s = num_frames / fps
    video_length = args.video_length or int(duration_s * 50) + 50  # 50 Hz + buffer

    # Find training run checkpoint
    logs_dir = Path.home() / "Repositories/mjlab-gui/logs/rsl_rl/g1_tracking"
    matching_runs = sorted(logs_dir.glob(f"*_{clip_name}"))
    if not matching_runs:
        # Fall back to archived policy
        pt_path = clip_dir / "policy" / f"{clip_name}_policy.pt"
        if not pt_path.exists():
            print(f"No checkpoint found for {clip_name}")
            sys.exit(1)
        checkpoint = str(pt_path)
    else:
        run_dir = matching_runs[-1]  # latest run
        checkpoints = sorted(run_dir.glob("model_*.pt"))
        if not checkpoints:
            print(f"No checkpoints in {run_dir}")
            sys.exit(1)
        checkpoint = str(checkpoints[-1])

    print(f"Clip: {clip_name}")
    print(f"Motion: {num_frames} frames, {fps} FPS, {duration_s:.1f}s")
    print(f"Checkpoint: {checkpoint}")
    print(f"Output: {args.width}x{args.height}, {video_length} steps")

    play_cfg = PlayConfig(
        checkpoint_file=checkpoint,
        motion_file=str(npz_path),
        num_envs=1,
        video=True,
        video_length=video_length,
        video_height=args.height,
        video_width=args.width,
        no_terminations=True,
    )

    # Patch env_cfg before play runs to disable ghost
    from mjlab.tasks.registry import load_env_cfg
    from mjlab.tasks.tracking.mdp import MotionCommandCfg

    _orig_load = load_env_cfg

    def patched_load(task_id, **kwargs):
        cfg = _orig_load(task_id, **kwargs)
        if "motion" in cfg.commands:
            motion_cmd = cfg.commands["motion"]
            if isinstance(motion_cmd, MotionCommandCfg):
                motion_cmd.viz.mode = "none"
        return cfg

    import mjlab.tasks.registry
    mjlab.tasks.registry.load_env_cfg = patched_load

    run_play("Mjlab-Tracking-Flat-Unitree-G1", play_cfg)

    # Find and copy the output video
    run_dir = Path(checkpoint).parent
    video_dir = run_dir / "videos" / "play"
    videos = sorted(video_dir.glob("*.mp4")) if video_dir.exists() else []
    if videos:
        output = Path.home() / "Desktop" / f"{clip_name}_hq.mp4"
        import shutil
        shutil.copy2(videos[-1], output)
        size_mb = output.stat().st_size / 1024 / 1024
        print(f"\nSaved: {output} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
