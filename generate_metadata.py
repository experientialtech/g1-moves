#!/usr/bin/env python3
"""Generate dataset metadata for g1-moves repository.

Reads all 59 motion capture clips and produces:
  - manifest.json: per-clip metadata index
  - quality_report.json: automated validation results
  - <clip>/README.md: per-clip summary

Usage:
    python generate_metadata.py
    python generate_metadata.py --skip-quality
    python generate_metadata.py --clips "B_Fence*"
"""

import argparse
import json
import os
import pickle
import fnmatch
from datetime import datetime, timezone

import numpy as np

# ── G1 joint configuration ──────────────────────────────────────────────────

JOINT_NAMES = [
    "left_hip_pitch_joint", "left_hip_roll_joint", "left_hip_yaw_joint",
    "left_knee_joint", "left_ankle_pitch_joint", "left_ankle_roll_joint",
    "right_hip_pitch_joint", "right_hip_roll_joint", "right_hip_yaw_joint",
    "right_knee_joint", "right_ankle_pitch_joint", "right_ankle_roll_joint",
    "waist_yaw_joint", "waist_roll_joint", "waist_pitch_joint",
    "left_shoulder_pitch_joint", "left_shoulder_roll_joint",
    "left_shoulder_yaw_joint", "left_elbow_joint", "left_wrist_roll_joint",
    "left_wrist_pitch_joint", "left_wrist_yaw_joint",
    "right_shoulder_pitch_joint", "right_shoulder_roll_joint",
    "right_shoulder_yaw_joint", "right_elbow_joint", "right_wrist_roll_joint",
    "right_wrist_pitch_joint", "right_wrist_yaw_joint",
]

JOINT_LIMITS = {
    "left_hip_pitch_joint": (-2.5307, 2.8798),
    "left_hip_roll_joint": (-0.5236, 2.9671),
    "left_hip_yaw_joint": (-2.7576, 2.7576),
    "left_knee_joint": (-0.0873, 2.8798),
    "left_ankle_pitch_joint": (-0.8727, 0.5236),
    "left_ankle_roll_joint": (-0.2618, 0.2618),
    "right_hip_pitch_joint": (-2.5307, 2.8798),
    "right_hip_roll_joint": (-2.9671, 0.5236),
    "right_hip_yaw_joint": (-2.7576, 2.7576),
    "right_knee_joint": (-0.0873, 2.8798),
    "right_ankle_pitch_joint": (-0.8727, 0.5236),
    "right_ankle_roll_joint": (-0.2618, 0.2618),
    "waist_yaw_joint": (-2.6180, 2.6180),
    "waist_roll_joint": (-0.5200, 0.5200),
    "waist_pitch_joint": (-0.5200, 0.5200),
    "left_shoulder_pitch_joint": (-3.0892, 2.6704),
    "left_shoulder_roll_joint": (-1.5882, 2.2515),
    "left_shoulder_yaw_joint": (-2.6180, 2.6180),
    "left_elbow_joint": (-1.0472, 2.0944),
    "left_wrist_roll_joint": (-1.9722, 1.9722),
    "left_wrist_pitch_joint": (-1.6144, 1.6144),
    "left_wrist_yaw_joint": (-1.6144, 1.6144),
    "right_shoulder_pitch_joint": (-3.0892, 2.6704),
    "right_shoulder_roll_joint": (-2.2515, 1.5882),
    "right_shoulder_yaw_joint": (-2.6180, 2.6180),
    "right_elbow_joint": (-1.0472, 2.0944),
    "right_wrist_roll_joint": (-1.9722, 1.9722),
    "right_wrist_pitch_joint": (-1.6144, 1.6144),
    "right_wrist_yaw_joint": (-1.6144, 1.6144),
}

# Performer mapping from clip name prefix
PERFORMERS = {
    "B_": "Mitch Chaiet",
    "J_": "Jasmine Coro",
    "M_": "Mike Gassaway",
}

# Foot body indices in NPZ body_pos_w (30 bodies)
# These are the ankle roll links which represent the foot
FOOT_BODY_NAMES = ["left_ankle_roll_link", "right_ankle_roll_link"]
FOOT_BODY_INDICES = [3, 6]  # indices in the 30-body array


def get_performer(clip_name):
    for prefix, name in PERFORMERS.items():
        if clip_name.startswith(prefix):
            return name
    return "Unknown"


def parse_bvh(path):
    """Extract frame count, frame time, and joint count from BVH file."""
    joints = 0
    frames = 0
    frame_time = 0.0
    with open(path) as f:
        for line in f:
            stripped = line.strip()
            if "JOINT" in stripped or "ROOT" in stripped:
                joints += 1
            if stripped.startswith("Frames:"):
                frames = int(stripped.split(":")[1].strip())
            if stripped.startswith("Frame Time:"):
                frame_time = float(stripped.split(":")[1].strip())
    return {
        "joints": joints,
        "frames": frames,
        "frame_time": frame_time,
        "fps": round(1.0 / frame_time) if frame_time > 0 else 0,
        "duration_s": round(frames * frame_time, 2),
    }


def load_pkl(path):
    """Load retargeted PKL file."""
    with open(path, "rb") as f:
        return pickle.load(f)


def load_npz(path):
    """Load training NPZ file."""
    return np.load(path)


def compute_motion_stats(pkl_data):
    """Compute motion energy and difficulty metrics from PKL data."""
    dof_pos = np.array(pkl_data["dof_pos"], dtype=np.float64)
    root_pos = np.array(pkl_data["root_pos"], dtype=np.float64)
    fps = int(pkl_data["fps"])

    # Joint velocities (finite differences)
    joint_vel = np.diff(dof_pos, axis=0) * fps
    mean_joint_vel = float(np.mean(np.abs(joint_vel)))
    max_joint_vel = float(np.max(np.abs(joint_vel)))

    # Root displacement
    root_deltas = np.diff(root_pos, axis=0)
    root_displacement = float(np.sum(np.linalg.norm(root_deltas, axis=1)))

    # Root velocity
    root_vel = root_deltas * fps
    mean_root_vel = float(np.mean(np.linalg.norm(root_vel, axis=1)))

    return {
        "mean_joint_velocity": round(mean_joint_vel, 4),
        "max_joint_velocity": round(max_joint_vel, 4),
        "root_displacement_m": round(root_displacement, 4),
        "mean_root_velocity": round(mean_root_vel, 4),
    }


def compute_joint_range(pkl_data):
    """Compute per-joint min/max from PKL data."""
    dof_pos = np.array(pkl_data["dof_pos"], dtype=np.float64)
    return {
        "min": [round(float(v), 4) for v in dof_pos.min(axis=0)],
        "max": [round(float(v), 4) for v in dof_pos.max(axis=0)],
    }


def check_joint_limits(pkl_data):
    """Check for joint limit violations."""
    dof_pos = np.array(pkl_data["dof_pos"], dtype=np.float64)
    violations = 0
    max_excess = 0.0
    worst_joint = None

    for j, name in enumerate(JOINT_NAMES):
        lo, hi = JOINT_LIMITS[name]
        below = dof_pos[:, j] < lo
        above = dof_pos[:, j] > hi
        joint_violations = int(np.sum(below) + np.sum(above))
        if joint_violations > 0:
            violations += joint_violations
            excess_below = float(np.max(lo - dof_pos[below, j])) if np.any(below) else 0.0
            excess_above = float(np.max(dof_pos[above, j] - hi)) if np.any(above) else 0.0
            joint_max = max(excess_below, excess_above)
            if joint_max > max_excess:
                max_excess = joint_max
                worst_joint = name

    return {
        "violations": violations,
        "max_excess_rad": round(max_excess, 4),
        "worst_joint": worst_joint,
    }


def check_ground_penetration(npz_data):
    """Check for foot ground penetration in training data."""
    body_pos = npz_data["body_pos_w"]  # (frames, 30, 3)
    min_foot_z = float("inf")
    penetration_frames = 0

    for idx in FOOT_BODY_INDICES:
        foot_z = body_pos[:, idx, 2]
        below = foot_z < -0.01  # 1cm tolerance
        penetration_frames += int(np.sum(below))
        min_foot_z = min(min_foot_z, float(np.min(foot_z)))

    return {
        "penetration_frames": penetration_frames,
        "min_foot_z_m": round(min_foot_z, 4),
    }


def check_nan(pkl_data, npz_data):
    """Check for NaN values in data arrays."""
    issues = []
    for key in ["root_pos", "root_rot", "dof_pos"]:
        arr = np.array(pkl_data[key])
        if np.any(np.isnan(arr)):
            issues.append(f"pkl.{key}")
    for key in npz_data.files:
        arr = npz_data[key]
        if np.any(np.isnan(arr)):
            issues.append(f"npz.{key}")
    return {"has_nan": len(issues) > 0, "fields": issues}


def get_file_sizes(clip_dir, clip_name):
    """Get sizes of key data files."""
    files = {
        "bvh": f"capture/{clip_name}.bvh",
        "pkl": f"retarget/{clip_name}.pkl",
        "csv": f"retarget/{clip_name}.csv",
        "npz": f"training/{clip_name}.npz",
    }
    sizes = {}
    for key, rel_path in files.items():
        full = os.path.join(clip_dir, rel_path)
        if os.path.exists(full):
            sizes[key] = os.path.getsize(full)
    return sizes


def get_pipeline_stages(clip_dir, clip_name):
    """Determine which pipeline stages are complete."""
    stages = []
    if os.path.exists(os.path.join(clip_dir, "capture", f"{clip_name}.bvh")):
        stages.append("capture")
    if os.path.exists(os.path.join(clip_dir, "retarget", f"{clip_name}.pkl")):
        stages.append("retarget")
    if os.path.exists(os.path.join(clip_dir, "training", f"{clip_name}.npz")):
        stages.append("training")
    if os.path.exists(os.path.join(clip_dir, "policy", f"{clip_name}_policy.pt")):
        stages.append("policy")
    return stages


def generate_clip_readme(clip_dir, clip_name, clip_data):
    """Generate a README.md for a clip folder."""
    stages = clip_data["pipeline_stages"]
    stats = clip_data["motion_stats"]
    has_policy = "policy" in stages

    lines = [
        f"# {clip_name}",
        "",
        f"**Category:** {clip_data['category'].title()} | "
        f"**Performer:** {clip_data['performer']} | "
        f"**Duration:** {clip_data['duration_s']}s | "
        f"**Frames:** {clip_data['frames']}",
        "",
        "## Files",
        "",
        "| Stage | Files |",
        "|-------|-------|",
        f"| `capture/` | BVH, MP4, GIF, 4x FBX |",
        f"| `retarget/` | PKL, CSV, MP4, GIF |",
        f"| `training/` | NPZ, MP4, GIF |",
    ]
    if has_policy:
        lines.append(f"| `policy/` | PT, MP4, GIF, agent.yaml, env.yaml, training_log.csv |")

    lines.extend([
        "",
        "## Motion Stats",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Joint velocity (mean) | {stats['mean_joint_velocity']:.2f} rad/s |",
        f"| Joint velocity (max) | {stats['max_joint_velocity']:.2f} rad/s |",
        f"| Root displacement | {stats['root_displacement_m']:.2f} m |",
        f"| Root velocity (mean) | {stats['mean_root_velocity']:.2f} m/s |",
        "",
        "## Formats",
        "",
        "- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS",
        f"- **PKL**: Retargeted G1 trajectories — `root_pos` ({clip_data['frames']}, 3), "
        f"`root_rot` ({clip_data['frames']}, 4), `dof_pos` ({clip_data['frames']}, 29)",
        f"- **NPZ**: Training data — `joint_pos/vel` ({clip_data['training_frames']}, 29), "
        f"`body_pos/quat/vel` ({clip_data['training_frames']}, 30, 3/4)",
        "- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)",
        "",
    ])

    readme_path = os.path.join(clip_dir, "README.md")
    with open(readme_path, "w") as f:
        f.write("\n".join(lines))
    return readme_path


def discover_clips(base_dir, pattern=None):
    """Find all clip directories."""
    clips = []
    for category in ["dance", "karate", "bonus"]:
        cat_dir = os.path.join(base_dir, category)
        if not os.path.isdir(cat_dir):
            continue
        for clip_name in sorted(os.listdir(cat_dir)):
            clip_dir = os.path.join(cat_dir, clip_name)
            if not os.path.isdir(clip_dir):
                continue
            bvh = os.path.join(clip_dir, "capture", f"{clip_name}.bvh")
            if not os.path.exists(bvh):
                continue
            if pattern and not fnmatch.fnmatch(clip_name, pattern):
                continue
            clips.append((category, clip_name, clip_dir))
    return clips


def main():
    parser = argparse.ArgumentParser(description="Generate g1-moves dataset metadata")
    parser.add_argument("--skip-quality", action="store_true", help="Skip quality checks")
    parser.add_argument("--clips", type=str, default=None, help="Only process matching clips")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    clips = discover_clips(".", args.clips)
    print(f"Found {len(clips)} clips")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    manifest = {
        "version": "1.0",
        "generated": now,
        "robot": "unitree_g1",
        "robot_mode": 15,
        "dof": 29,
        "capture_system": "MOVIN TRACIN",
        "retarget_sdk": "movin_sdk_python",
        "clips": {},
    }

    quality = {
        "generated": now,
        "checks": {
            "joint_limit_violations": {"description": "Frames where retargeted angles exceed G1 limits", "clips": {}},
            "ground_penetration": {"description": "Frames where foot Z < -1cm", "clips": {}},
            "frame_consistency": {"description": "PKL frames == BVH frames, NPZ frames == BVH - 1", "clips": {}},
            "nan_check": {"description": "NaN values in PKL or NPZ arrays", "clips": {}},
            "file_completeness": {"description": "All expected files present", "clips": {}},
        },
        "summary": {"passed": [], "warnings": [], "errors": []},
    }

    total_frames = 0
    total_duration = 0.0

    for category, clip_name, clip_dir in clips:
        print(f"  Processing {clip_name}...", end=" ", flush=True)

        # Parse BVH
        bvh_path = os.path.join(clip_dir, "capture", f"{clip_name}.bvh")
        bvh = parse_bvh(bvh_path)

        # Load PKL
        pkl_path = os.path.join(clip_dir, "retarget", f"{clip_name}.pkl")
        pkl_data = load_pkl(pkl_path)

        # Load NPZ
        npz_path = os.path.join(clip_dir, "training", f"{clip_name}.npz")
        npz_data = load_npz(npz_path)

        # Compute stats
        motion_stats = compute_motion_stats(pkl_data)
        joint_range = compute_joint_range(pkl_data)
        stages = get_pipeline_stages(clip_dir, clip_name)
        file_sizes = get_file_sizes(clip_dir, clip_name)

        clip_entry = {
            "category": category,
            "performer": get_performer(clip_name),
            "frames": bvh["frames"],
            "fps": bvh["fps"],
            "duration_s": bvh["duration_s"],
            "bvh_joints": bvh["joints"],
            "retarget_dof": 29,
            "training_frames": int(npz_data["joint_pos"].shape[0]),
            "file_sizes": file_sizes,
            "joint_range": joint_range,
            "motion_stats": motion_stats,
            "has_policy": "policy" in stages,
            "pipeline_stages": stages,
        }
        manifest["clips"][clip_name] = clip_entry

        total_frames += bvh["frames"]
        total_duration += bvh["duration_s"]

        # Quality checks
        if not args.skip_quality:
            # Joint limits
            jl = check_joint_limits(pkl_data)
            quality["checks"]["joint_limit_violations"]["clips"][clip_name] = jl

            # Ground penetration
            gp = check_ground_penetration(npz_data)
            quality["checks"]["ground_penetration"]["clips"][clip_name] = gp

            # Frame consistency
            pkl_frames = np.array(pkl_data["dof_pos"]).shape[0]
            npz_frames = npz_data["joint_pos"].shape[0]
            fc = {
                "bvh_frames": bvh["frames"],
                "pkl_frames": pkl_frames,
                "npz_frames": npz_frames,
                "pkl_match": pkl_frames == bvh["frames"],
                "npz_match": npz_frames in (bvh["frames"], bvh["frames"] - 1),
            }
            quality["checks"]["frame_consistency"]["clips"][clip_name] = fc

            # NaN check
            nan = check_nan(pkl_data, npz_data)
            quality["checks"]["nan_check"]["clips"][clip_name] = nan

            # File completeness
            expected_capture = [f"{clip_name}.bvh", f"{clip_name}.gif", f"{clip_name}.mp4",
                                f"{clip_name}_bl.fbx", f"{clip_name}_mb.fbx",
                                f"{clip_name}_ue.fbx", f"{clip_name}_un.fbx"]
            expected_retarget = [f"{clip_name}.pkl", f"{clip_name}.csv",
                                 f"{clip_name}_retarget.gif", f"{clip_name}_retarget.mp4"]
            expected_training = [f"{clip_name}.npz",
                                 f"{clip_name}_training.gif", f"{clip_name}_training.mp4"]
            missing = []
            for f in expected_capture:
                if not os.path.exists(os.path.join(clip_dir, "capture", f)):
                    missing.append(f"capture/{f}")
            for f in expected_retarget:
                if not os.path.exists(os.path.join(clip_dir, "retarget", f)):
                    missing.append(f"retarget/{f}")
            for f in expected_training:
                if not os.path.exists(os.path.join(clip_dir, "training", f)):
                    missing.append(f"training/{f}")
            quality["checks"]["file_completeness"]["clips"][clip_name] = {
                "complete": len(missing) == 0,
                "missing": missing,
            }

            # Classify clip
            has_issues = (jl["violations"] > 0 or gp["penetration_frames"] > 0 or
                          not fc["pkl_match"] or not fc["npz_match"] or
                          nan["has_nan"] or len(missing) > 0)
            has_errors = nan["has_nan"] or not fc["pkl_match"] or not fc["npz_match"]

            if has_errors:
                quality["summary"]["errors"].append(clip_name)
            elif has_issues:
                quality["summary"]["warnings"].append(clip_name)
            else:
                quality["summary"]["passed"].append(clip_name)

        # Generate per-clip README
        generate_clip_readme(clip_dir, clip_name, clip_entry)

        print("done")

    # Add totals to manifest
    manifest["total_clips"] = len(clips)
    manifest["total_duration_s"] = round(total_duration, 1)
    manifest["total_frames"] = total_frames
    manifest["categories"] = {}
    for cat in ["dance", "karate", "bonus"]:
        cat_clips = [c for c in clips if c[0] == cat]
        manifest["categories"][cat] = {
            "clips": len(cat_clips),
            "duration_s": round(sum(manifest["clips"][c[1]]["duration_s"] for c in cat_clips), 1),
        }

    # Write manifest
    with open("manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nWrote manifest.json ({len(clips)} clips)")

    # Write quality report
    if not args.skip_quality:
        with open("quality_report.json", "w") as f:
            json.dump(quality, f, indent=2)
        p = len(quality["summary"]["passed"])
        w = len(quality["summary"]["warnings"])
        e = len(quality["summary"]["errors"])
        print(f"Wrote quality_report.json ({p} passed, {w} warnings, {e} errors)")

    print(f"Generated {len(clips)} clip READMEs")
    print(f"\nDataset: {len(clips)} clips, {total_frames} frames, {total_duration:.0f}s ({total_duration/60:.1f} min)")


if __name__ == "__main__":
    main()
