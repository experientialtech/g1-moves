<p align="center">
  <img src="logo.png" alt="Experiential Technologies" width="500">
</p>

# G1 Moves

> **[Dataset](https://huggingface.co/datasets/exptech/g1-moves)** (BVH, FBX, PKL, NPZ, ONNX policies) · **[Showcase](https://huggingface.co/spaces/exptech/g1-moves)** (interactive gallery) · **Code** (this repo)

Scripts and documentation for the G1 Moves motion capture dataset — 60 clips for the Unitree G1 humanoid robot, captured with MOVIN TRACIN and retargeted to 29-DOF joint trajectories with trained RL policies.

**All data files live on [HuggingFace](https://huggingface.co/datasets/exptech/g1-moves).** This repository contains only the processing scripts, standalone inference code, and documentation.

## Credits

**Director:** [Mitch Chaiet](https://mitchchaiet.com/)
**DIT:** [Molly Maguire](https://www.linkedin.com/in/mollymaguire001/)
**Dance:** [Jasmine Coro](https://jasminecoro.com/)
**Karate:** [Mike Gassaway](https://www.backstage.com/u/mike-gassaway/)

## What's Where

| Location | Contents |
|----------|----------|
| [HuggingFace Dataset](https://huggingface.co/datasets/exptech/g1-moves) | All motion data (BVH, FBX, PKL, NPZ), trained policies (PT, ONNX), training logs, metadata |
| [HuggingFace Space](https://huggingface.co/spaces/exptech/g1-moves) | Interactive showcase with video previews of every clip at each pipeline stage |
| [GitHub](https://github.com/experientialtech/g1-moves) (this repo) | `run_policy.py`, `retarget_all.py`, `generate_metadata.py`, `CONTROLLER.md`, documentation |

## Dataset Structure

The dataset on HuggingFace is organized as follows:

```
dance/                          28 clips — dance routines
  B_DadDance/
  B_LongDance/
  B_SpiralDance/
  B_StretchDance/
  B_WiggleDance/
  J_Dance0_StepTouch/
  J_Dance1_Modern/
  J_Dance2_Salsa/
  J_Dance3_Woah/
  J_Dance4_Broadway/
  J_Dance5_Hype/
  J_Dance6_Sassy/
  J_Dance7_Party/
  J_Dance8_WestCoast/
  J_Dance9_PeaceMaker/
  J_Dance11_Gnarly/
  J_Dance12_LushLife/
  J_Dance17_Shuffle/
  J_Dance18_TikTok/
  J_Dance19_LetsGO/
  J_Dance20_DWG/
  J_Dance21_Blunt/
  J_Dance22_Thrilling/
  J_Dance23_MidnightSun/
  J_ShortDance13_SingleLadies/
  J_ShortDance14_Disco/
  J_ShortDance15_Nineties/
  J_ShortDance16_JazzWalk/
karate/                         27 clips — karate/martial arts moves
  B_AttackKarate/
  B_BowKarate/
  B_ChopsKarate/
  B_CrazyChopsKarate/
  B_ForwardKarate/
  B_LongKarate/
  B_SpinKarate/
  M_Move1/                — Guard Combo
  M_Move2/                — Low Punch
  M_Move3/                — Horse Stance
  M_Move4/                — Spin Punch
  M_Move5/                — Twist Punch
  M_Move6/                — Spin Strike
  M_Move7/                — Rapid Punch
  M_Move8/                — Drop Spin
  M_Move9/                — Level Change
  M_Move10/               — Side Kick
  M_Move11/               — Blitz
  M_Move17/               — Double Strike
  M_Move18/               — Front Kick
  M_Move19/               — Slow Kata
  M_Move20/               — Open Strike
  M_ShortMove12/          — Quick Jab
  M_ShortMove13/          — Snap Kick
  M_ShortMove14/          — Light Punch
  M_ShortMove15/          — Drop Strike
  M_ShortMove16/          — Power Burst
bonus/                           5 clips — fencing, hands-up, chops, video extraction
  B_Fence1/
  B_Fence2/
  B_HandsChop/
  B_HandsUp/
  V_Rocamena/          — extracted via video2robot
movin-studio-project/           Raw Movin Studio recordings and project file
```

Each clip lives in its own subfolder containing:

| File | Format |
|------|--------|
| `<clip>.bvh` | BVH motion capture (humanoid skeleton, Hips root) |
| `<clip>.pkl` | Retargeted G1 joint trajectories (29 DOF) |
| `<clip>_bl.fbx` | FBX for Blender |
| `<clip>_mb.fbx` | FBX for Maya |
| `<clip>_ue.fbx` | FBX for Unreal Engine |
| `<clip>_un.fbx` | FBX for Unity |

## Retarget

All 60 clips have been retargeted to the Unitree G1 (mode 15, 29 DOF) using [movin_sdk_python](https://github.com/MOVIN3D/movin_sdk_python). The pipeline:

1. **BVH → IK**: Per-frame inverse kinematics maps human skeleton to G1 joint limits (1.75m human height)
2. **Ground calibration**: MuJoCo forward kinematics finds minimum foot Z across all frames, shifts root down for ground contact
3. **PKL output**: `{fps, root_pos, root_rot, dof_pos}` — 60 FPS, quaternions in xyzw order, 29 joint angles
4. **Video render**: MuJoCo offscreen 1080x1080, libx264 CRF 18

Run `python retarget_all.py` to regenerate (skips existing outputs).

## Deploying Policies

Each trained clip has two policy variants in the [HF dataset](https://huggingface.co/datasets/exptech/g1-moves):

| Folder | Task trained with | Inputs | Use for |
|--------|-------------------|--------|---------|
| `<clip>/policy/` | `Mjlab-Tracking-Flat-Unitree-G1` | 160 | Simulation |
| `<clip>/policy_154/` | `Mjlab-Tracking-Flat-Unitree-G1-No-State-Estimation` | 154 | **Real robot** (and simulation) |

The 160-input policies also observe `motion_anchor_pos_b` (where the robot is relative to the reference in the world) and `base_lin_vel`. A real G1 has no reliable source for these without external odometry, so deploy the `policy_154` variant on hardware. All 59 `policy_154` policies (no `B_Fence1` yet) complete their motion in the standalone simulator below.

### ONNX files

| File | Inputs | Outputs | Metadata |
|------|--------|---------|----------|
| `policy/<clip>.onnx` | `obs [1,160]`, `time_step [1,1]` | `actions` + reference motion at `time_step` | yes |
| `policy_154/<clip>_policy.onnx` | `obs [1,154]`, `time_step [1,1]` | `actions` + reference motion at `time_step` | yes |
| `policy/<clip>_policy.onnx` | `obs [1,160]` | `actions` | yes (actor only, motion comes from the NPZ) |

The reference motion is bundled in the files that take `time_step`, so you don't need the NPZ. Observation normalization is baked in. Everything a deployment has to match is stored as ONNX metadata (`session.get_modelmeta().custom_metadata_map`):

| Key | Meaning |
|-----|---------|
| `joint_names` | Joint order of actions and joint observations (Unitree 29-DOF motor order) |
| `default_joint_pos` | Default pose; joint observations are relative to it and actions are offsets from it |
| `action_scale` | Per-joint scale, 0.075 to 0.548 |
| `joint_stiffness`, `joint_damping` | PD gains used in training |
| `observation_names` | Order of the observation terms |
| `anchor_body_name` | `torso_link` |
| `body_names` | Bodies in the bundled `body_pos_w` / `body_quat_w` outputs |

**Joint target**: `target = default_joint_pos + action_scale * action`, sent to a PD controller with the gains above at 50 Hz (sim at 200 Hz, decimation 4). Raw actions are *not* joint positions.

**Motion timing**: training advances the reference by one frame per 50 Hz control step (`time_step += 1`). The motion files are 60 fps, so each policy tracks its clip at 50/60 speed. Use the same stepping when deploying.

### Observation vector

Terms are concatenated in `observation_names` order. The 154-input variant drops the two terms marked *.

| Term | Size | Description |
|------|------|-------------|
| `command` | 58 | Reference joint positions (29) then velocities (29) at `time_step` |
| `motion_anchor_pos_b` * | 3 | Reference `torso_link` position in the robot's `torso_link` frame |
| `motion_anchor_ori_b` | 6 | Reference `torso_link` orientation in the robot's `torso_link` frame: first two columns of the rotation matrix, row-major `[R00, R01, R10, R11, R20, R21]` |
| `base_lin_vel` * | 3 | Pelvis IMU linear velocity, body frame |
| `base_ang_vel` | 3 | Pelvis IMU angular velocity, body frame |
| `joint_pos` | 29 | Joint positions minus `default_joint_pos` |
| `joint_vel` | 29 | Joint velocities |
| `actions` | 29 | Previous raw policy output |

### Joint Order (29 DOF, Unitree G1)

```
 0: left_hip_pitch        7: right_hip_roll       14: waist_pitch
 1: left_hip_roll         8: right_hip_yaw        15: left_shoulder_pitch
 2: left_hip_yaw          9: right_knee           16: left_shoulder_roll
 3: left_knee            10: right_ankle_pitch    17: left_shoulder_yaw
 4: left_ankle_pitch     11: right_ankle_roll     18: left_elbow
 5: left_ankle_roll      12: waist_yaw            19: left_wrist_roll
 6: right_hip_pitch      13: waist_roll           20: left_wrist_pitch
21: left_wrist_yaw       25: right_elbow
22: right_shoulder_pitch  26: right_wrist_roll
23: right_shoulder_roll   27: right_wrist_pitch
24: right_shoulder_yaw    28: right_wrist_yaw
```

### Robot model

All policies were trained on mjlab's G1 model, `mjlab/src/mjlab/asset_zoo/robots/unitree_g1/xmls/g1.xml` (the `mjlab` submodule here). mjlab adds actuators, armature, collision settings and solver options in code (`g1_constants.py`, `tracking_env_cfg.py`). `g1_mode15_square.xml` was only used during retargeting, to put the feet on the ground. It is not needed to run policies.

### Option 1: Sim2Sim with mjlab

```bash
git clone https://github.com/mujocolab/mjlab
cd mjlab
uv sync

MUJOCO_GL=egl uv run play \
  Mjlab-Tracking-Flat-Unitree-G1-No-State-Estimation \
  --checkpoint-file <clip>/policy_154/<clip>_policy.pt \
  --motion-file <clip>/training/<clip>.npz \
  --num-envs 1 \
  --viewer viser
# Open http://localhost:8080 for 3D viewer
# For policy/<clip>_policy.pt use task Mjlab-Tracking-Flat-Unitree-G1
```

### Option 2: Deploy with RoboJuDo

[RoboJuDo](https://github.com/GDDG08/RoboJuDo)'s `BeyondMimicPolicy` reads the ONNX metadata above, so the bundled ONNX files work as-is. Our fork with g1-moves configs is the `RoboJuDo` submodule (`robojudo/config/g1/g1_loco_mimic_cfg.py`, guide in `RoboJuDo/docs/g1_moves.md`).

```bash
cd RoboJuDo
pip install -e .
cp <clip>/policy_154/<clip>_policy.onnx assets/models/g1/beyondmimic/<clip>.onnx
```

```python
G1BeyondMimicPolicyCfg(policy_name="<clip>", without_state_estimator=True)   # policy_154
G1BeyondMimicPolicyCfg(policy_name="<clip>", without_state_estimator=False)  # policy (sim only)
```

`without_state_estimator` must match the file's input size; the policy refuses to load if it doesn't.

### Option 3: Standalone MuJoCo

`run_policy.py` needs only `mujoco`, `onnxruntime` and `numpy`. It reads everything from the ONNX metadata and configures mjlab's `g1.xml` the way training did.

```bash
pip install mujoco onnxruntime numpy
git submodule update --init mjlab
hf download exptech/g1-moves --repo-type dataset --include "dance/B_DadDance/*" --local-dir .

python run_policy.py dance/B_DadDance                    # 160-input policy, viewer
python run_policy.py --onnx dance/B_DadDance/policy_154/B_DadDance_policy.onnx
python run_policy.py dance/B_DadDance --headless         # print tracking metrics
```

`--headless` runs one pass and reports whether mjlab's termination conditions would have fired. `--zero-state-estimation` feeds zeros for the two state-estimation inputs, the way a robot without odometry would.

### Option 4: Raw ONNX Inference

```python
import numpy as np, onnxruntime as ort

s = ort.InferenceSession("B_DadDance_policy.onnx")          # from policy_154/
meta = s.get_modelmeta().custom_metadata_map
default = np.array(meta["default_joint_pos"].split(","), dtype=np.float32)
scale = np.array(meta["action_scale"].split(","), dtype=np.float32)

out = s.run(None, {"obs": obs_154[None], "time_step": np.array([[t]], np.float32)})
actions, ref_joint_pos, ref_joint_vel = out[0][0], out[1][0], out[2][0]
target = default + scale * actions                           # PD target, 50 Hz
```

The network is a 4-layer MLP (154 or 160 → 512 → 256 → 128 → 29) with ELU activations. It runs in under 1 ms on CPU.

## Training Quality

Aggregate metrics across all 44 trained policies (higher reward = better, lower error = better):

| Metric | Mean | Min | Max |
|--------|------|-----|-----|
| Reward | 39.7 | 33.1 | 45.6 |
| Episode length | 493 / 500 | 458 | 500 |
| Body position error | 0.045 m | 0.031 m | 0.078 m |
| Joint position error | 0.56 rad | 0.42 rad | 0.85 rad |

Per-clip training metrics are available in each clip's `policy/training_log.csv`.

## Citation

```bibtex
@misc{g1moves2026,
  title     = {G1 Moves: Motion Capture Dataset for the Unitree G1 Humanoid Robot},
  author    = {Chaiet, Mitch},
  year      = {2026},
  publisher = {Hugging Face},
  url       = {https://huggingface.co/datasets/exptech/g1-moves},
  note      = {60 motion capture clips with retargeted joint trajectories, RL training data, and trained policies}
}
```

## Equipment

### Motion Capture

59 clips were captured using the [MOVIN TRACIN](https://movin3d.com/) markerless motion capture system from [MOVIN3D](https://movin3d.com/), with 1 additional clip (V_Rocamena) extracted from monocular video via [video2robot](https://github.com/experientialtech/video2robot). MOVIN TRACIN uses on-device AI to fuse LiDAR point clouds and vision into production-ready motion data — no markers, no suit, no multi-camera rig. Captured performances were recorded and exported using [MOVIN Studio](https://www.movin3d.com/studio), which provides real-time skeleton visualization, recording management, and export to BVH and FBX formats. Retargeting from human skeleton to G1 robot joint space was performed using [movin_sdk_python](https://github.com/MOVIN3D/movin_sdk_python).

Thank you to [MOVIN3D](https://movin3d.com/) for building an incredible motion capture platform that makes professional-grade mocap accessible to robotics researchers.

### Workstation

All data was captured and policies were trained on two machines from [Dell Technologies](https://www.dell.com/):

#### [Dell Pro Max Tower T2](https://www.dell.com/en-us/shop/desktop-computers/dell-pro-max-tower-t2/spd/dell-pro-max-tower-t2-desktop/usepmtbts2_t2)

| Component | Spec |
|-----------|------|
| CPU | Intel Core Ultra 9 285K (24 cores, up to 7.2 GHz) |
| GPU | NVIDIA RTX PRO 6000 Blackwell Workstation Edition (96 GB GDDR7) |
| RAM | 128 GB DDR5 |
| Storage | 2x 4 TB WD SN8000S NVMe SSD (8 TB total) |
| OS | Ubuntu 24.04 LTS |

The RTX PRO 6000 Blackwell with 96 GB of VRAM enables running 8,192 parallel MuJoCo-Warp simulation environments on a single GPU for reinforcement learning training, while the 24-core Ultra 9 285K handles motion retargeting and data processing.

#### [Dell Pro Max with GB10](https://www.dell.com/en-us/shop/desktop-computers/dell-pro-max-desktop-with-nvidia-gb10/spd/dell-pro-max-gb10-desktop/usepmgb10bts)

| Component | Spec |
|-----------|------|
| SoC | NVIDIA GB10 Grace Blackwell Superchip |
| CPU | NVIDIA Grace (20x ARM Cortex-X925) |
| GPU | NVIDIA Blackwell GPU (1,024 CUDA cores, 120 GB unified memory) |
| RAM | 120 GB LPDDR5X unified (shared CPU/GPU, 273 GB/s) |
| Storage | 4 TB NVMe SSD |
| AI Performance | Up to 1,000 TOPS (INT4) |
| OS | Ubuntu 24.04 LTS (NVIDIA DGX OS 7.3.1) |

The Dell Pro Max with GB10 is a compact desktop AI supercomputer powered by the NVIDIA GB10 Grace Blackwell Superchip. Its unified memory architecture allows the GPU to access the full 120 GB memory pool without PCIe bottlenecks, running 4,096 parallel MuJoCo-Warp environments for secondary training workloads. Both machines train policies simultaneously from opposite ends of the clip queue.

Thank you to [Dell Technologies](https://www.dell.com/) for providing the compute power behind this project.

## Pipeline Progress

| Stage | Bonus (5) | Dance (28) | Karate (27) | Total (60) |
|-------|:---------:|:----------:|:-----------:|:----------:|
| Capture | 5 | 28 | 27 | 60 |
| PKL (retarget) | 5 | 28 | 27 | 60 |
| NPZ (training) | 5 | 28 | 27 | 60 |
| Policy (.pt) | 4 | 22 | 18 | 44 |
| ONNX (.onnx) | 4 | 22 | 18 | 44 |

