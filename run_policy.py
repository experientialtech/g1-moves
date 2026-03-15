#!/usr/bin/env python3
"""Run a trained G1 Moves policy in MuJoCo simulation.

Standalone script — requires only mujoco and onnxruntime (no mjlab needed).

Usage:
    pip install mujoco onnxruntime numpy
    python run_policy.py dance/B_DadDance

    # Or specify files explicitly:
    python run_policy.py \
        --onnx dance/B_DadDance/policy/B_DadDance_policy.onnx \
        --npz dance/B_DadDance/training/B_DadDance.npz \
        --xml /path/to/g1_mode15_square.xml
"""

import argparse
import time
from pathlib import Path

import mujoco
import mujoco.viewer
import numpy as np
import onnxruntime as ort


# G1 mode 15 default joint positions (29 DOF)
DEFAULT_JOINT_POS = np.zeros(29, dtype=np.float32)

# Control frequency: 50 Hz (decimation=4 at 200 Hz sim)
DECIMATION = 4
CONTROL_DT = 0.02  # 1 / 50 Hz

# PD gains per joint (29 DOF), matched to mjlab training configuration.
# Joint order: L hip p/r/y, L knee, L ankle p/r, R hip p/r/y, R knee,
#              R ankle p/r, waist y/r/p, L shoulder p/r/y, L elbow,
#              L wrist r/p/y, R shoulder p/r/y, R elbow, R wrist r/p/y
KP = np.array([
    40.2, 99.1, 40.2, 99.1, 28.6, 28.6,   # left leg (hip p/r/y, knee, ankle p/r)
    40.2, 99.1, 40.2, 99.1, 28.6, 28.6,   # right leg
    40.2, 28.6, 28.6,                       # waist (yaw, roll, pitch)
    14.3, 14.3, 14.3, 14.3, 14.3, 16.8, 16.8,  # left arm (shoulder p/r/y, elbow, wrist r/p/y)
    14.3, 14.3, 14.3, 14.3, 14.3, 16.8, 16.8,  # right arm
], dtype=np.float32)

KD = np.array([
    2.6, 6.3, 2.6, 6.3, 1.8, 1.8,         # left leg
    2.6, 6.3, 2.6, 6.3, 1.8, 1.8,         # right leg
    2.6, 1.8, 1.8,                          # waist
    0.9, 0.9, 0.9, 0.9, 0.9, 1.1, 1.1,    # left arm
    0.9, 0.9, 0.9, 0.9, 0.9, 1.1, 1.1,    # right arm
], dtype=np.float32)


def rotation_matrix_to_6d(rot_matrix: np.ndarray) -> np.ndarray:
    """Extract first two columns of a 3x3 rotation matrix (6D representation)."""
    return rot_matrix[:, :2].T.flatten()


def quat_to_rot_matrix(quat_wxyz: np.ndarray) -> np.ndarray:
    """Convert wxyz quaternion to 3x3 rotation matrix."""
    w, x, y, z = quat_wxyz
    return np.array([
        [1 - 2*(y*y + z*z), 2*(x*y - w*z), 2*(x*z + w*y)],
        [2*(x*y + w*z), 1 - 2*(x*x + z*z), 2*(y*z - w*x)],
        [2*(x*z - w*y), 2*(y*z + w*x), 1 - 2*(x*x + y*y)],
    ])


def transform_to_body_frame(pos_world, quat_world_wxyz, anchor_pos_world, anchor_quat_world_wxyz):
    """Transform anchor position and orientation into the robot's body frame."""
    # Robot rotation matrix (world -> body)
    R_robot = quat_to_rot_matrix(quat_world_wxyz)

    # Anchor position in body frame
    delta_pos = anchor_pos_world - pos_world
    anchor_pos_b = R_robot.T @ delta_pos

    # Anchor orientation in body frame (relative rotation)
    R_anchor = quat_to_rot_matrix(anchor_quat_world_wxyz)
    R_rel = R_robot.T @ R_anchor
    anchor_ori_b = rotation_matrix_to_6d(R_rel)

    return anchor_pos_b.astype(np.float32), anchor_ori_b.astype(np.float32)


def run_policy(onnx_path: str, npz_path: str, xml_path: str, speed: float = 1.0):
    """Run ONNX policy with MuJoCo viewer."""
    # Load motion reference
    motion = np.load(npz_path)
    ref_joint_pos = motion["joint_pos"]      # (T, 29)
    ref_joint_vel = motion["joint_vel"]      # (T, 29)
    ref_body_pos = motion["body_pos_w"]      # (T, N, 3)
    ref_body_quat = motion["body_quat_w"]    # (T, N, 4) — wxyz in NPZ
    fps = float(motion["fps"])
    num_frames = ref_joint_pos.shape[0]
    duration = num_frames / fps

    print(f"Motion: {num_frames} frames, {fps} FPS, {duration:.1f}s")

    # Load ONNX policy
    session = ort.InferenceSession(onnx_path)
    print(f"Policy: {onnx_path}")

    # Load MuJoCo model
    model = mujoco.MjModel.from_xml_path(xml_path)
    data = mujoco.MjData(model)
    model.opt.timestep = CONTROL_DT / DECIMATION  # 200 Hz sim

    # State
    last_action = np.zeros(29, dtype=np.float32)
    motion_time = 0.0

    def get_motion_frame(t: float) -> int:
        """Get the motion frame index for a given time."""
        frame = int(t * fps) % num_frames
        return frame

    def controller(model, data):
        nonlocal last_action, motion_time

        frame = get_motion_frame(motion_time)

        # Reference motion at current timestep
        ref_jp = ref_joint_pos[frame].astype(np.float32)
        ref_jv = ref_joint_vel[frame].astype(np.float32)

        # Robot state from simulation
        robot_pos = data.qpos[:3].copy()
        robot_quat_wxyz = data.qpos[3:7].copy()  # MuJoCo uses wxyz
        joint_pos = data.qpos[7:36].astype(np.float32)
        joint_vel = data.qvel[6:35].astype(np.float32)

        # Angular and linear velocity (body frame)
        base_ang_vel = data.sensordata[:3].astype(np.float32) if data.sensordata.size >= 3 else np.zeros(3, dtype=np.float32)
        base_lin_vel = data.sensordata[3:6].astype(np.float32) if data.sensordata.size >= 6 else np.zeros(3, dtype=np.float32)

        # Motion anchor: pelvis body (index 0) from reference
        anchor_pos_w = ref_body_pos[frame, 0].astype(np.float64)
        anchor_quat_w = ref_body_quat[frame, 0].astype(np.float64)  # wxyz

        # Transform to body frame
        anchor_pos_b, anchor_ori_b = transform_to_body_frame(
            robot_pos, robot_quat_wxyz, anchor_pos_w, anchor_quat_w
        )

        # Build 160-dim observation
        obs = np.concatenate([
            ref_jp,                              # 29: reference joint positions
            ref_jv,                              # 29: reference joint velocities
            anchor_pos_b,                        #  3: motion anchor pos (body frame)
            anchor_ori_b,                        #  6: motion anchor ori (body frame)
            base_ang_vel,                        #  3: base angular velocity
            base_lin_vel,                        #  3: base linear velocity
            joint_pos - DEFAULT_JOINT_POS,       # 29: joint positions minus default
            joint_vel,                           # 29: joint velocities
            last_action,                         # 29: previous action
        ]).astype(np.float32)

        # Run policy
        actions = session.run(["actions"], {"obs": obs[None]})[0][0]
        last_action = actions.copy()

        # PD control: convert position targets to torques
        target_pos = actions + DEFAULT_JOINT_POS
        torques = KP * (target_pos - joint_pos) - KD * joint_vel
        data.ctrl[:29] = torques

        motion_time += CONTROL_DT * speed

    # Initialize robot pose from first frame of motion
    data.qpos[:3] = ref_body_pos[0, 0]
    data.qpos[3:7] = ref_body_quat[0, 0]
    data.qpos[7:36] = ref_joint_pos[0]
    mujoco.mj_forward(model, data)

    print(f"Starting viewer (speed={speed}x, duration={duration:.1f}s, loops forever)")
    print("Close the viewer window to exit.")

    with mujoco.viewer.launch_passive(model, data) as viewer:
        while viewer.is_running():
            step_start = time.time()

            # Run controller at 50 Hz, sim at 200 Hz
            controller(model, data)
            for _ in range(DECIMATION):
                mujoco.mj_step(model, data)

            viewer.sync()

            # Real-time pacing
            elapsed = time.time() - step_start
            sleep_time = CONTROL_DT - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)


def main():
    parser = argparse.ArgumentParser(description="Run a G1 Moves policy in MuJoCo")
    parser.add_argument("clip", nargs="?", help="Clip path, e.g. 'dance/B_DadDance'")
    parser.add_argument("--onnx", help="Path to ONNX policy file")
    parser.add_argument("--npz", help="Path to NPZ motion file")
    parser.add_argument("--xml", default=None, help="Path to G1 MuJoCo XML model")
    parser.add_argument("--speed", type=float, default=1.0, help="Playback speed multiplier")
    args = parser.parse_args()

    # Resolve paths
    base = Path(__file__).parent

    if args.clip:
        clip_dir = base / args.clip
        clip_name = clip_dir.name
        onnx_path = str(clip_dir / "policy" / f"{clip_name}_policy.onnx")
        npz_path = str(clip_dir / "training" / f"{clip_name}.npz")
    elif args.onnx and args.npz:
        onnx_path = args.onnx
        npz_path = args.npz
    else:
        parser.error("Provide either a clip path or both --onnx and --npz")

    # Find XML model
    if args.xml:
        xml_path = args.xml
    else:
        # Try common locations
        candidates = [
            Path.home() / "Repositories/mjlab-gui/external/RoboJuDo/assets/robots/g1/g1_29dof_rev_1_0.xml",
            Path.home() / "Repositories/g1-urdf/g1_mode15_square.xml",
            base / "g1_mode15_square.xml",
        ]
        xml_path = None
        for c in candidates:
            if c.exists():
                xml_path = str(c)
                break
        if xml_path is None:
            parser.error(
                "Could not find G1 MuJoCo XML. Provide --xml or place "
                "g1_mode15_square.xml in the repo root."
            )

    # Validate files exist
    for label, path in [("ONNX", onnx_path), ("NPZ", npz_path), ("XML", xml_path)]:
        if not Path(path).exists():
            parser.error(f"{label} file not found: {path}")

    run_policy(onnx_path, npz_path, xml_path, speed=args.speed)


if __name__ == "__main__":
    main()
