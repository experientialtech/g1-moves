#!/usr/bin/env python3
"""Run a trained G1 Moves policy in standalone MuJoCo, matching mjlab training.

Requires only mujoco, onnxruntime and numpy (no mjlab install needed).

Everything that must match training is read from the ONNX metadata written by
export_onnx.py (joint order, default pose, action scale, PD gains, anchor body,
observation layout). The motion reference is bundled inside the same ONNX file.

The robot model is mjlab's G1 MJCF (the exact model the policies were trained
on), shipped in the mjlab submodule:
    mjlab/src/mjlab/asset_zoo/robots/unitree_g1/xmls/g1.xml
mjlab adds actuators, armature, collision settings and solver options in code;
this script applies the same settings to the raw XML.

Usage:
    pip install mujoco onnxruntime numpy
    git submodule update --init mjlab           # for the G1 model

    # Clip data lives in the HF dataset; download one clip next to this script:
    hf download exptech/g1-moves --repo-type dataset \
        --include "dance/B_DadDance/*" --local-dir .

    python run_policy.py dance/B_DadDance                 # interactive viewer
    python run_policy.py dance/B_DadDance --headless      # one pass, print metrics
    python run_policy.py --onnx path/to/B_DadDance.onnx   # explicit file
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

import mujoco
import numpy as np
import onnxruntime as ort

REPO_DIR = Path(__file__).resolve().parent
DEFAULT_XML = REPO_DIR / "mjlab/src/mjlab/asset_zoo/robots/unitree_g1/xmls/g1.xml"

# mjlab tracking task settings (mjlab/tasks/tracking/tracking_env_cfg.py).
SIM_DT = 0.005
DECIMATION = 4
CONTROL_DT = SIM_DT * DECIMATION  # 50 Hz policy
SOLVER_ITERATIONS = 10
SOLVER_LS_ITERATIONS = 20

# mjlab G1 actuator constants (mjlab/asset_zoo/robots/unitree_g1/g1_constants.py).
# Stiffness = armature * (2*pi*10 Hz)^2, so armature is recovered from the
# stiffness stored in the ONNX metadata. Effort limits are not in the metadata.
NATURAL_FREQ = 10 * 2.0 * 3.1415926535
EFFORT_LIMITS = [
    (r".*_wrist_(pitch|yaw)_joint", 5.0),                 # 4010
    (r".*_(hip_roll|knee)_joint", 139.0),                  # 7520-22
    (r".*_(hip_pitch|hip_yaw)_joint|waist_yaw_joint", 88.0),  # 7520-14
    (r".*_ankle_(pitch|roll)_joint|waist_(pitch|roll)_joint", 50.0),  # 2x 5020
    (r".*_(shoulder_\w+|elbow|wrist_roll)_joint", 25.0),   # 5020
]

# mjlab tracking terminations, used for the headless report.
TERM_ANCHOR_Z = 0.25
TERM_ANCHOR_ORI = 0.8
TERM_EE_Z = 0.25
EE_BODIES = ("left_ankle_roll_link", "right_ankle_roll_link",
             "left_wrist_yaw_link", "right_wrist_yaw_link")

REQUIRED_META = ("joint_names", "default_joint_pos", "action_scale",
                 "joint_stiffness", "joint_damping", "observation_names",
                 "anchor_body_name", "body_names")


# --------------------------------------------------------------------------- #
# Math (quaternions are w, x, y, z, as in MuJoCo and mjlab)
# --------------------------------------------------------------------------- #

def quat_to_mat(q: np.ndarray) -> np.ndarray:
    m = np.empty(9)
    mujoco.mju_quat2Mat(m, np.asarray(q, dtype=np.float64))
    return m.reshape(3, 3)


def subtract_frame_transforms(p01, q01, p02, q02):
    """Pose of frame 2 expressed in frame 1 (mjlab.utils.lab_api.math)."""
    r01 = quat_to_mat(q01)
    pos = r01.T @ (np.asarray(p02) - np.asarray(p01))
    rot = r01.T @ quat_to_mat(q02)
    return pos, rot


# --------------------------------------------------------------------------- #
# Policy + bundled motion
# --------------------------------------------------------------------------- #

class Policy:
    def __init__(self, onnx_path: Path):
        self.session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
        meta = self.session.get_modelmeta().custom_metadata_map
        missing = [k for k in REQUIRED_META if k not in meta]
        if missing:
            sys.exit(
                f"{onnx_path.name} has no deployment metadata (missing {missing}).\n"
                "Use policy/<clip>.onnx or policy_154/<clip>_policy.onnx (written by export_onnx.py)."
            )
        floats = lambda k: np.array([float(x) for x in meta[k].split(",")], dtype=np.float64)
        strings = lambda k: meta[k].split(",")

        self.joint_names = strings("joint_names")
        self.default_joint_pos = floats("default_joint_pos")
        self.action_scale = floats("action_scale")
        self.kp = floats("joint_stiffness")
        self.kd = floats("joint_damping")
        self.obs_names = strings("observation_names")
        self.body_names = strings("body_names")
        self.anchor_body = meta["anchor_body_name"]
        self.anchor_idx = self.body_names.index(self.anchor_body)

        inputs = {i.name: i.shape for i in self.session.get_inputs()}
        if "time_step" not in inputs:
            sys.exit(f"{onnx_path.name} has no bundled motion (no 'time_step' input). Use "
                     "policy/<clip>.onnx or policy_154/<clip>_policy.onnx instead.")
        self.obs_dim = int(inputs["obs"][1])
        self.has_state_estimation = "base_lin_vel" in self.obs_names
        self._load_motion()

    def _load_motion(self):
        """Pull the reference motion out of the ONNX (one frame per control step)."""
        # Frame count isn't exposed directly; time_step is clamped to the last
        # frame, so probe until the output stops changing.
        zeros = np.zeros((1, self.obs_dim), np.float32)
        frames = []
        t = 0
        prev = None
        while True:
            out = self.session.run(None, {"obs": zeros, "time_step": np.array([[t]], np.float32)})
            cur = tuple(o[0] for o in out[1:5])
            if prev is not None and all(np.array_equal(a, b) for a, b in zip(cur, prev)):
                break
            frames.append(cur)
            prev = cur
            t += 1
            if t > 200_000:
                break
        self.ref_joint_pos = np.stack([f[0] for f in frames]).astype(np.float64)
        self.ref_joint_vel = np.stack([f[1] for f in frames]).astype(np.float64)
        self.ref_body_pos = np.stack([f[2] for f in frames]).astype(np.float64)
        self.ref_body_quat = np.stack([f[3] for f in frames]).astype(np.float64)
        self.num_frames = len(frames)

    def act(self, obs: np.ndarray, t: int) -> np.ndarray:
        out = self.session.run(["actions"], {
            "obs": obs[None].astype(np.float32),
            "time_step": np.array([[t]], np.float32),
        })
        return out[0][0].astype(np.float64)


# --------------------------------------------------------------------------- #
# Robot model, configured like mjlab's training scene
# --------------------------------------------------------------------------- #

def effort_limit(joint: str) -> float:
    for pattern, limit in EFFORT_LIMITS:
        if re.fullmatch(pattern, joint):
            return limit
    raise KeyError(f"no effort limit for {joint}")


def build_model(xml_path: Path, policy: Policy) -> mujoco.MjModel:
    spec = mujoco.MjSpec.from_file(str(xml_path))
    spec.option.timestep = SIM_DT
    spec.option.iterations = SOLVER_ITERATIONS
    spec.option.ls_iterations = SOLVER_LS_ITERATIONS

    # Collisions: only *_collision geoms collide; feet get condim 3, friction 0.6.
    foot = re.compile(r"^(left|right)_foot[1-7]_collision$")
    for g in spec.geoms:
        if g.name.endswith("_collision"):
            g.contype, g.conaffinity = 1, 1
            if foot.match(g.name):
                g.condim, g.priority = 3, 1
                g.friction[0] = 0.6
            else:
                g.condim = 1
        else:
            g.contype, g.conaffinity = 0, 0

    # Ground plane (mjlab adds a flat terrain).
    if not any(g.type == mujoco.mjtGeom.mjGEOM_PLANE for g in spec.geoms):
        spec.worldbody.add_geom(
            name="floor", type=mujoco.mjtGeom.mjGEOM_PLANE, size=[0, 0, 0.05],
            contype=1, conaffinity=1, condim=3, rgba=[0.3, 0.35, 0.4, 1],
        )
        spec.worldbody.add_light(pos=[0, 0, 4], dir=[0, 0, -1])

    # Position actuators with the training gains, armature and effort limits.
    for a in list(spec.actuators):
        spec.delete(a)
    joints = {j.name: j for j in spec.joints}
    for name, kp, kd in zip(policy.joint_names, policy.kp, policy.kd):
        j = joints[name]
        j.armature = kp / NATURAL_FREQ**2
        tau = effort_limit(name)
        j.actfrclimited = mujoco.mjtLimited.mjLIMITED_TRUE
        j.actfrcrange = [-tau, tau]
        act = spec.add_actuator(name=name, target=name,
                                trntype=mujoco.mjtTrn.mjTRN_JOINT)
        act.set_to_position(kp=kp, kv=kd)
        act.forcelimited = mujoco.mjtLimited.mjLIMITED_TRUE
        act.forcerange = [-tau, tau]
    return spec.compile()


# --------------------------------------------------------------------------- #
# Runner
# --------------------------------------------------------------------------- #

class Runner:
    def __init__(self, policy: Policy, model: mujoco.MjModel, zero_state_est: bool = False):
        self.p, self.m = policy, model
        self.zero_state_est = zero_state_est
        self.d = mujoco.MjData(model)

        jnt_ids = [mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, n) for n in policy.joint_names]
        if min(jnt_ids) < 0:
            sys.exit("Robot model is missing joints listed in the policy metadata.")
        self.qadr = np.array([model.jnt_qposadr[i] for i in jnt_ids])
        self.vadr = np.array([model.jnt_dofadr[i] for i in jnt_ids])
        self.act_ids = np.array([mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, n)
                                 for n in policy.joint_names])
        body = lambda n: mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, n)
        self.anchor_body = body(policy.anchor_body)
        self.ee_bodies = [body(n) for n in EE_BODIES]
        self.ee_ref_idx = [policy.body_names.index(n) for n in EE_BODIES]
        sensor = lambda n: model.sensor_adr[mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SENSOR, n)]
        self.lin_vel_adr = sensor("imu_lin_vel")
        self.ang_vel_adr = sensor("imu_ang_vel")
        self.reset()

    def reset(self):
        """Start at frame 0 of the motion, like mjlab play mode (sampling_mode='start')."""
        p, d = self.p, self.d
        mujoco.mj_resetData(self.m, d)
        root = p.body_names.index("pelvis")
        d.qpos[0:3] = p.ref_body_pos[0, root]
        d.qpos[3:7] = p.ref_body_quat[0, root]
        d.qpos[self.qadr] = p.ref_joint_pos[0]
        d.qvel[self.vadr] = p.ref_joint_vel[0]
        mujoco.mj_forward(self.m, d)
        self.t = 0
        self.last_action = np.zeros(len(p.joint_names))

    def observation(self) -> np.ndarray:
        p, d, t = self.p, self.d, self.t
        pos_b, rot_b = subtract_frame_transforms(
            d.xpos[self.anchor_body], d.xquat[self.anchor_body],
            p.ref_body_pos[t, p.anchor_idx], p.ref_body_quat[t, p.anchor_idx],
        )
        terms = {
            "command": np.concatenate([p.ref_joint_pos[t], p.ref_joint_vel[t]]),
            "motion_anchor_pos_b": pos_b,
            "motion_anchor_ori_b": rot_b[:, :2].reshape(-1),  # row-major, as mjlab
            "base_lin_vel": d.sensordata[self.lin_vel_adr:self.lin_vel_adr + 3],
            "base_ang_vel": d.sensordata[self.ang_vel_adr:self.ang_vel_adr + 3],
            "joint_pos": d.qpos[self.qadr] - p.default_joint_pos,
            "joint_vel": d.qvel[self.vadr],
            "actions": self.last_action,
        }
        if self.zero_state_est:
            # What a real G1 without odometry feeds these inputs.
            terms["motion_anchor_pos_b"] = np.zeros(3)
            terms["base_lin_vel"] = np.zeros(3)
        obs = np.concatenate([terms[n] for n in p.obs_names])
        assert obs.shape[0] == p.obs_dim, f"obs {obs.shape[0]} != policy input {p.obs_dim}"
        return obs

    def step(self) -> bool:
        """One 50 Hz control step. Returns True when the motion wrapped around."""
        p, d = self.p, self.d
        action = p.act(self.observation(), self.t)
        self.last_action = action
        d.ctrl[self.act_ids] = p.default_joint_pos + p.action_scale * action
        for _ in range(DECIMATION):
            mujoco.mj_step(self.m, d)
        # Training advances one motion frame per control step.
        self.t += 1
        return self.t >= p.num_frames

    def errors(self) -> dict:
        p, d, t = self.p, self.d, min(self.t, self.p.num_frames - 1)
        a = self.anchor_body
        _, rot = subtract_frame_transforms(np.zeros(3), d.xquat[a], np.zeros(3),
                                           p.ref_body_quat[t, p.anchor_idx])
        g = np.array([0, 0, -1.0])
        return {
            "anchor_z": abs(d.xpos[a, 2] - p.ref_body_pos[t, p.anchor_idx, 2]),
            "anchor_ori": np.linalg.norm(quat_to_mat(d.xquat[a]).T @ g
                                         - quat_to_mat(p.ref_body_quat[t, p.anchor_idx]).T @ g),
            "ee_z": max(abs(d.xpos[b, 2] - p.ref_body_pos[t, i, 2])
                        for b, i in zip(self.ee_bodies, self.ee_ref_idx)),
            "joint": float(np.mean(np.abs(d.qpos[self.qadr] - p.ref_joint_pos[t]))),
        }


def run_headless(runner: Runner, loops: int) -> int:
    p = runner.p
    worst = 0
    for loop in range(loops):
        runner.reset()
        joint_err, fell_at = [], None
        done = False
        while not done:
            done = runner.step()
            e = runner.errors()
            joint_err.append(e["joint"])
            if fell_at is None and (e["anchor_z"] > TERM_ANCHOR_Z or e["anchor_ori"] > TERM_ANCHOR_ORI
                                    or e["ee_z"] > TERM_EE_Z):
                fell_at = runner.t * CONTROL_DT
                break
        status = "FAILED" if fell_at is not None else "ok"
        print(f"pass {loop + 1}: {status}"
              + (f" (would terminate at {fell_at:.1f}s)" if fell_at is not None else "")
              + f", mean joint error {np.degrees(np.mean(joint_err)):.1f} deg"
              + f" over {len(joint_err) * CONTROL_DT:.1f}s")
        worst = max(worst, 1 if fell_at is not None else 0)
    return worst


def run_viewer(runner: Runner, speed: float):
    import mujoco.viewer
    with mujoco.viewer.launch_passive(runner.m, runner.d) as viewer:
        viewer.cam.trackbodyid = runner.anchor_body
        viewer.cam.type = mujoco.mjtCamera.mjCAMERA_TRACKING
        while viewer.is_running():
            start = time.time()
            if runner.step():
                runner.reset()
            viewer.sync()
            time.sleep(max(0.0, CONTROL_DT / speed - (time.time() - start)))


def resolve_onnx(args, parser) -> Path:
    if args.onnx:
        return Path(args.onnx)
    if not args.clip:
        parser.error("give a clip (e.g. dance/B_DadDance) or --onnx")
    clip_dir = Path(args.data_dir) / args.clip
    onnx = clip_dir / "policy" / f"{clip_dir.name}.onnx"
    if not onnx.exists():
        parser.error(
            f"{onnx} not found. Download the clip first:\n"
            f'  hf download exptech/g1-moves --repo-type dataset --include "{args.clip}/*" '
            f"--local-dir {args.data_dir}"
        )
    return onnx


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("clip", nargs="?", help="clip path, e.g. dance/B_DadDance")
    parser.add_argument("--onnx", help="explicit <clip>.onnx (with metadata + bundled motion)")
    parser.add_argument("--data-dir", default=str(REPO_DIR), help="folder holding the dataset clips")
    parser.add_argument("--xml", default=str(DEFAULT_XML), help="G1 MJCF (default: mjlab's g1.xml)")
    parser.add_argument("--speed", type=float, default=1.0, help="viewer playback speed")
    parser.add_argument("--headless", action="store_true", help="no viewer; print tracking metrics")
    parser.add_argument("--loops", type=int, default=1, help="headless passes over the motion")
    parser.add_argument("--zero-state-estimation", action="store_true",
                        help="feed zeros for base_lin_vel / motion_anchor_pos_b, as on a real "
                             "robot without odometry (shows why 160-input policies fail there)")
    args = parser.parse_args()

    xml = Path(args.xml)
    if not xml.exists():
        parser.error(f"{xml} not found. Run: git submodule update --init mjlab")

    policy = Policy(resolve_onnx(args, parser))
    print(f"Policy: {policy.obs_dim} inputs ({', '.join(policy.obs_names)}), "
          f"{len(policy.joint_names)} actions, anchor {policy.anchor_body}")
    print(f"Motion: {policy.num_frames} frames at 50 Hz = {policy.num_frames * CONTROL_DT:.1f}s")
    if policy.has_state_estimation:
        print("Note: this policy needs base_lin_vel and motion_anchor_pos_b (state estimation). "
              "Fine in sim; on the real robot use a No-State-Estimation policy.")

    runner = Runner(policy, build_model(xml, policy), args.zero_state_estimation)
    if args.headless:
        sys.exit(run_headless(runner, args.loops))
    run_viewer(runner, args.speed)


if __name__ == "__main__":
    main()
