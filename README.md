---
license: cc-by-4.0
task_categories:
  - robotics
  - reinforcement-learning
tags:
  - motion-capture
  - humanoid-robot
  - unitree-g1
  - bvh
  - sim-to-real
  - mujoco
  - reinforcement-learning
  - motion-imitation
size_categories:
  - n<1K
viewer: false
---

<p align="center">
  <img src="logo.png" alt="Experiential Technologies" width="500">
</p>

# G1 Moves

Motion capture clips for the Unitree G1 humanoid robot, captured with Movin Studio and exported as BVH and FBX.

**[Browse the showcase](https://huggingface.co/spaces/exptech/g1-moves)** — interactive gallery with video previews of every clip across all pipeline stages.

## Credits

**Director:** [Mitch Chaiet](https://mitchchaiet.com/)
**DIT:** [Molly Maguire](https://www.linkedin.com/in/mollymaguire001/)
**Dance:** [Jasmine Coro](https://jasminecoro.com/)
**Karate:** [Mike Gassaway](https://www.backstage.com/u/mike-gassaway/)

## Structure

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

Each trained clip includes an ONNX policy (`<clip>_policy.onnx`) and a PyTorch checkpoint (`<clip>_policy.pt`). The ONNX model has observation normalization baked in — feed it raw observations and it outputs 29 joint position targets directly.

### Policy Format

| Property | Value |
|----------|-------|
| Input | `obs` — float32 tensor, shape `[batch, 160]` |
| Output | `actions` — float32 tensor, shape `[batch, 29]` |
| Normalization | Baked into the model (obs mean/std from training) |
| Framework | ONNX opset 17, compatible with onnxruntime |
| Control freq | 50 Hz (decimation=4 at 200 Hz sim) |

### Observation Vector (160 dims)

| Index | Size | Name | Description |
|-------|------|------|-------------|
| 0-28 | 29 | `ref_joint_pos` | Reference motion joint positions at current timestep |
| 29-57 | 29 | `ref_joint_vel` | Reference motion joint velocities at current timestep |
| 58-60 | 3 | `motion_anchor_pos_b` | Motion anchor position relative to robot pelvis (body frame) |
| 61-66 | 6 | `motion_anchor_ori_b` | Motion anchor orientation relative to robot (first 2 columns of rotation matrix) |
| 67-69 | 3 | `base_ang_vel` | Robot base angular velocity (IMU) |
| 70-72 | 3 | `base_lin_vel` | Robot base linear velocity |
| 73-101 | 29 | `joint_pos_rel` | Current joint positions minus default pose |
| 102-130 | 29 | `joint_vel` | Current joint velocities |
| 131-159 | 29 | `last_action` | Previous policy output |

### Joint Order (29 DOF, Unitree G1 mode 15)

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

### Option 1: Sim2Sim with mjlab (easiest)

Visualize any policy in MuJoCo simulation:

```bash
git clone https://github.com/mujocolab/mjlab
cd mjlab
uv sync

# Play a trained policy
MUJOCO_GL=egl uv run play \
  Mjlab-Tracking-Flat-Unitree-G1 \
  --checkpoint-file <clip>/policy/<clip>_policy.pt \
  --motion-file <clip>/training/<clip>.npz \
  --num-envs 1 \
  --viewer viser
# Open http://localhost:8080 for 3D viewer
```

### Option 2: Deploy with RoboJuDo

[RoboJuDo](https://github.com/GDDG08/RoboJuDo) is a plug-and-play deployment framework for humanoid robots that supports both MuJoCo sim2sim and real robot deployment.

#### Setup

```bash
git clone https://github.com/GDDG08/RoboJuDo.git
cd RoboJuDo
pip install -e .
python submodule_install.py  # installs mujoco_viewer
```

#### Loading a Policy

Each policy needs its corresponding motion NPZ file for the reference trajectory. At each timestep, the NPZ provides the reference joint positions/velocities and body anchor positions that form the first 67 dims of the observation vector.

```python
import numpy as np
import onnxruntime as ort

# Load policy and motion
session = ort.InferenceSession("<clip>_policy.onnx")
motion = np.load("<clip>.npz")

ref_joint_pos = motion["joint_pos"]    # (T, 29) reference joint positions
ref_joint_vel = motion["joint_vel"]    # (T, 29) reference joint velocities
ref_body_pos = motion["body_pos_w"]    # (T, N, 3) reference body positions
ref_body_quat = motion["body_quat_w"]  # (T, N, 4) reference body quaternions
fps = float(motion["fps"])             # typically 60

# At each control step (50 Hz), construct the 160-dim observation:
obs = np.concatenate([
    ref_joint_pos[t],           # 29: reference joint positions
    ref_joint_vel[t],           # 29: reference joint velocities
    anchor_pos_body_frame,      # 3:  motion anchor pos in robot frame
    anchor_ori_body_frame,      # 6:  motion anchor ori (2 cols of rot matrix)
    robot_ang_vel,              # 3:  from IMU
    robot_lin_vel,              # 3:  from state estimation
    joint_pos - default_pos,    # 29: current joints minus default
    joint_vel,                  # 29: current joint velocities
    last_action,                # 29: previous policy output
])

actions = session.run(["actions"], {"obs": obs[None].astype(np.float32)})[0][0]
# actions are 29 joint position targets to send to PD controller
```

#### RoboJuDo Integration

To add G1 Moves policies as a RoboJuDo policy module, create a policy class that replays the NPZ motion and constructs the observation vector. The architecture is similar to `BeyondMimicPolicy` — an ONNX model with motion replay — but uses a simpler observation format. See the [BeyondMimic policy source](https://github.com/GDDG08/RoboJuDo/blob/main/robojudo/policy/beyondmimic_policy.py) as a reference implementation.

Key differences from BeyondMimic:
- Our ONNX takes only `obs` as input (no `time_step`)
- Observation normalization is baked into the ONNX model
- Motion data comes from the NPZ file, not embedded in the ONNX model
- Actions are direct joint position targets (no per-joint scaling needed)

### Option 3: Standalone MuJoCo Viewer

Run any policy in MuJoCo simulation without the training framework:

```bash
pip install mujoco onnxruntime numpy
python run_policy.py dance/B_DadDance --xml /path/to/g1_mode15_square.xml
```

This opens an interactive MuJoCo viewer with the robot executing the trained policy in a loop. See `run_policy.py` for the complete observation vector construction and control loop.

### Option 4: Raw ONNX Inference

For custom deployments (Jetson, microcontrollers, web):

```python
import onnxruntime as ort
session = ort.InferenceSession("B_DadDance_policy.onnx")
actions = session.run(["actions"], {"obs": obs_160.astype(np.float32)})[0]
```

The ONNX model is a 4-layer MLP (160 → 512 → 256 → 128 → 29) with ELU activations. It runs in <1ms on CPU and is compatible with ONNX Runtime on all platforms including NVIDIA Jetson (TensorRT), web (ONNX.js), and mobile.

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

